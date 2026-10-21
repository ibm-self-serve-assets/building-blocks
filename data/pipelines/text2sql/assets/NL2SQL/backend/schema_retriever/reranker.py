"""
reranker.py

Modular re-ranking component for Schema Retriever.
Supports:
1. 'none' / disabled: No-op passthrough
2. 'cross-encoder': HuggingFace / sentence-transformers CrossEncoder (e.g., cross-encoder/ms-marco-MiniLM-L-6-v2, BAAI/bge-reranker-base)
3. 'flashrank': Ultra-lightweight CPU reranker via flashrank
4. 'watsonx': Watsonx/IBM foundation model ranking via API (optional)

Provides score normalisation and robust fallback if dependencies are missing.
"""

from __future__ import annotations

import logging
import math
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple

log = logging.getLogger("reranker")


def _sigmoid(x: float) -> float:
    """Safely compute sigmoid to map cross-encoder logits into [0, 1] probability range."""
    if x < -50:
        return 0.0
    if x > 50:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class BaseReranker(ABC):
    """Abstract interface for schema retrieval re-rankers."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Re-ranks the candidate documents for a given query.
        Returns the top_k re-ordered documents with updated 'score' / 'confidence'.
        """


class NoOpReranker(BaseReranker):
    """No-op re-ranker that preserves the initial candidate order."""

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        return documents[:top_k]


class CrossEncoderReranker(BaseReranker):
    """
    Cross-Encoder re-ranker using sentence_transformers.CrossEncoder.
    Provides deep query-document interaction scoring.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: str = "cpu") -> None:
        self.model_name = model_name
        self.device = device
        self._model = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from sentence_transformers import CrossEncoder
            log.info(f"Loading CrossEncoder model '{self.model_name}' on device '{self.device}'...")
            self._model = CrossEncoder(self.model_name, device=self.device)
            log.info("CrossEncoder model loaded successfully.")
        except Exception as exc:
            log.warning(
                f"Failed to load sentence_transformers CrossEncoder ({exc}). "
                f"Falling back to unranked candidates."
            )
            self._model = None

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        if not documents or not self._model:
            return documents[:top_k]

        # Prepare pairs of (query, document_text)
        pairs: List[Tuple[str, str]] = []
        for doc in documents:
            text = doc.get("text_agg") or ""
            if not text:
                # Build fallback text from table metadata
                t_name = doc.get("table_name", "")
                s_name = doc.get("schema_name", "")
                c_names = doc.get("column_names", "")
                comment = doc.get("table_comment", "")
                text = f"Table: {s_name}.{t_name}\nDescription: {comment}\nColumns: {c_names}"
            pairs.append((query, text[:4000]))

        try:
            raw_scores = self._model.predict(pairs)
            scored_docs = []
            for i, doc in enumerate(documents):
                raw_score = float(raw_scores[i])
                norm_score = _sigmoid(raw_score)
                doc_copy = dict(doc)
                doc_copy["score"] = round(norm_score, 6)
                doc_copy["confidence"] = round(norm_score, 6)
                doc_copy["raw_rerank_score"] = round(raw_score, 6)
                doc_copy["reranked"] = True
                scored_docs.append((norm_score, doc_copy))

            # Sort descending by score
            scored_docs.sort(key=lambda x: x[0], reverse=True)
            return [item[1] for item in scored_docs[:top_k]]

        except Exception as exc:
            log.exception(f"CrossEncoder prediction failed: {exc}")
            return documents[:top_k]


class FlashRankReranker(BaseReranker):
    """
    FlashRank re-ranker — ultralightweight, zero-PyTorch dependency reranker.
    """

    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2") -> None:
        self.model_name = model_name
        self._ranker = None
        self._load_model()

    def _load_model(self) -> None:
        try:
            from flashrank import Ranker
            log.info(f"Loading FlashRank model '{self.model_name}'...")
            self._ranker = Ranker(model_name=self.model_name)
            log.info("FlashRank model loaded successfully.")
        except Exception as exc:
            log.warning(f"FlashRank is not available ({exc}). Falling back to unranked candidates.")
            self._ranker = None

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        if not documents or not self._ranker:
            return documents[:top_k]

        try:
            from flashrank import RerankRequest
            passages = []
            for idx, doc in enumerate(documents):
                text = doc.get("text_agg") or f"{doc.get('table_name')} {doc.get('column_names', '')}"
                passages.append({"id": idx, "text": text[:4000]})

            rerank_req = RerankRequest(query=query, passages=passages)
            ranked_results = self._ranker.rerank(rerank_req)

            ordered_docs: List[Dict[str, Any]] = []
            for r in ranked_results:
                idx = int(r["id"])
                doc_copy = dict(documents[idx])
                score = float(r.get("score", 0.0))
                doc_copy["score"] = round(score, 6)
                doc_copy["confidence"] = round(score, 6)
                doc_copy["reranked"] = True
                ordered_docs.append(doc_copy)

            return ordered_docs[:top_k]
        except Exception as exc:
            log.exception(f"FlashRank rerank failed: {exc}")
            return documents[:top_k]


def build_reranker(cfg: Optional[Dict[str, Any]] = None) -> BaseReranker:
    """
    Factory function to construct the appropriate Re-ranker based on configuration.
    """
    if cfg is None:
        cfg = dict(os.environ)

    enabled_str = str(cfg.get("RERANK_ENABLED", "false")).lower()
    enabled = enabled_str in ("1", "true", "yes")
    if not enabled:
        return NoOpReranker()

    provider = str(cfg.get("RERANK_PROVIDER", "cross-encoder")).lower().strip()

    if provider in ("cross-encoder", "cross_encoder", "st"):
        model_name = cfg.get("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
        device = cfg.get("RERANK_DEVICE", "cpu")
        return CrossEncoderReranker(model_name=model_name, device=device)

    elif provider == "flashrank":
        model_name = cfg.get("RERANK_MODEL", "ms-marco-TinyBERT-L-2-v2")
        return FlashRankReranker(model_name=model_name)

    elif provider in ("none", "false", "disabled"):
        return NoOpReranker()

    log.warning(f"Unknown RERANK_PROVIDER '{provider}', default to NoOpReranker")
    return NoOpReranker()
