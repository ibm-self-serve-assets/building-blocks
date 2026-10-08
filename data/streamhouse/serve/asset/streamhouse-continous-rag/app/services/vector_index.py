from __future__ import annotations

import re
import threading
from dataclasses import dataclass

from app.models import KnowledgeChunk, RagEvidence
from app.services.embedding import cosine_similarity

_STOP_WORDS = frozenset(
    {
        "a", "an", "the", "is", "it", "in", "on", "of", "to", "and", "or",
        "for", "be", "was", "are", "with", "at", "by", "from", "that", "this",
        "what", "when", "how", "do", "does", "did", "has", "have", "had",
        "not", "no", "if", "as", "so", "but", "we", "i", "my", "you",
    }
)

_KEYWORD_BOOST = 0.06  # cosine score added per matched keyword token


def _keywords(text: str) -> set[str]:
    """Return lower-case non-stop-word tokens from *text*."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if t not in _STOP_WORDS and len(t) > 1}


@dataclass
class IndexedChunk:
    value: KnowledgeChunk


class VectorIndex:
    """Small demo read index reconstructed from the durable embedding topic.

    The index tracks the latest observed document version by ``updated_at``. Older
    chunks remain in Kafka for replay/audit but are excluded from retrieval after a
    newer version of the same document arrives. This prevents stale text from an
    earlier document version from being returned by RAG.

    Retrieval combines cosine similarity with a lightweight keyword re-rank boost:
    each query token that appears in the chunk text adds ``_KEYWORD_BOOST`` to the
    score, improving recall for hash-embedding demos where semantic distance is
    less discriminative than real embedding models.
    """

    def __init__(self) -> None:
        self._items: dict[str, IndexedChunk] = {}
        self._latest_document_version: dict[str, str] = {}
        self._lock = threading.RLock()

    def upsert(self, chunk: KnowledgeChunk) -> None:
        with self._lock:
            self._items[chunk.chunk_id] = IndexedChunk(value=chunk)
            current = self._latest_document_version.get(chunk.document_id)
            if current is None or chunk.updated_at > current:
                self._latest_document_version[chunk.document_id] = chunk.updated_at

    def count(self) -> int:
        """Return the count of retrievable chunks from latest document versions."""
        with self._lock:
            return sum(
                1
                for indexed in self._items.values()
                if self._is_latest(indexed.value)
            )

    def _is_latest(self, chunk: KnowledgeChunk) -> bool:
        return self._latest_document_version.get(chunk.document_id) == chunk.updated_at

    def search(self, query_embedding: list[float], top_k: int, query_text: str = "") -> list[RagEvidence]:
        """Return the top-k most relevant chunks.

        Scores each chunk as: cosine_similarity + (_KEYWORD_BOOST × matched_keywords).
        The keyword boost compensates for the limited discrimination of the demo
        hash-embedding model — it is additive and bounded so cosine still dominates.
        """
        query_kw = _keywords(query_text) if query_text else set()
        scored: list[tuple[float, KnowledgeChunk]] = []
        with self._lock:
            for indexed in self._items.values():
                chunk = indexed.value
                if not self._is_latest(chunk):
                    continue
                score = cosine_similarity(query_embedding, chunk.embedding)
                if query_kw:
                    chunk_kw = _keywords(chunk.text + " " + chunk.title)
                    overlap = len(query_kw & chunk_kw)
                    score = min(1.0, score + overlap * _KEYWORD_BOOST)
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RagEvidence(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                title=chunk.title,
                text=chunk.text,
                source=chunk.source,
                asset_id=chunk.asset_id,
                score=round(score, 4),
                updated_at=chunk.updated_at,
            )
            for score, chunk in scored[:top_k]
        ]
