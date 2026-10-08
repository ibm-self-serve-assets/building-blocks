from __future__ import annotations

import hashlib
import math
import re


TOKEN_RE = re.compile(r"[A-Za-z0-9_\-\.]+")


class HashEmbeddingModel:
    """Dependency-free deterministic embedding for the zero-extra-service demo profile.

    This is intentionally a demo fallback. For production quality semantic retrieval,
    use the Confluent Cloud Flink AI_EMBEDDING profile documented under infra/flink/.
    """

    name = "factorypulse-hash-demo-v1"

    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        tokens = [t.lower() for t in TOKEN_RE.findall(text)]
        if not tokens:
            return vector

        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % self.dim
            sign = -1.0 if (value >> 1) & 1 else 1.0
            vector[index] += sign

        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))
