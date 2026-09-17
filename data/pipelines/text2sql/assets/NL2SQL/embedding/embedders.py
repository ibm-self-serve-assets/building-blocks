"""
embedders.py

Shared embedding providers for the Text2SQL schema retriever system.

Both ingest_opensearch.py and schema_retriever_opensearch.py import from here
so that the WatsonxEmbedding and LocalSTEmbedding implementations stay in sync.

Providers
---------
  WatsonxEmbedding   — IBM watsonx.ai; IAM token cached ~50 min; exponential
                       back-off with jitter on 429/503 transient errors.
  LocalSTEmbedding   — sentence-transformers (local CPU/GPU); no network calls.

Usage
-----
  from embedders import EmbeddingProvider, WatsonxEmbedding, LocalSTEmbedding, build_embedder
  embedder = build_embedder(cfg)          # cfg is a dict of env-var-style keys
  vectors  = embedder.embed(["some text"])
"""

from __future__ import annotations

import logging
import random
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import requests

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# sentence-transformers is optional (not needed in environments that use watsonx)
# ---------------------------------------------------------------------------
_LOCAL_EMBED_AVAILABLE = False
try:
    from sentence_transformers import SentenceTransformer  # noqa: F401
    _LOCAL_EMBED_AVAILABLE = True
except Exception:
    pass


# ===========================================================================
# Base class
# ===========================================================================

class EmbeddingProvider(ABC):
    """Abstract base for all embedding backends."""

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts and return unit-length float vectors."""


# ===========================================================================
# Watsonx provider
# ===========================================================================

class WatsonxEmbedding(EmbeddingProvider):
    """
    IBM watsonx.ai text embeddings.

    IAM token is cached for ~50 minutes to avoid per-batch round-trips.
    Transient HTTP 429 / 502 / 503 / 504 errors are retried with exponential
    back-off and random jitter.

    Thread-safe: a lock guards IAM token refresh so concurrent executor
    threads don't issue duplicate refresh requests.
    """

    _TOKEN_TTL  = 3000   # seconds (~50 min; actual token lifetime ~60 min)
    _RETRY_ON   = {429, 503, 502, 504}
    _MAX_RETRY  = 5
    _BASE_DELAY = 1.0    # seconds

    def __init__(self, api_key: str, url: str, project_id: str, model_id: str) -> None:
        if not all([api_key, url, project_id, model_id]):
            raise RuntimeError("WatsonxEmbedding: missing credentials or model_id")
        self._api_key    = api_key
        self._url        = url.rstrip("/")
        self._project_id = project_id
        self._model_id   = model_id
        self._token:     Optional[str] = None
        self._token_ts:  float = 0.0
        self._token_lock = threading.Lock()

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        endpoint = f"{self._url}/ml/v1/text/embeddings?version=2024-05-31"
        headers  = {
            "Authorization": f"Bearer {self._iam_token()}",
            "Content-Type":  "application/json",
        }
        payload = {
            "input":      texts,
            "inputs":     texts,
            "model_id":   self._model_id,
            "project_id": self._project_id,
        }
        t0   = time.time()
        resp = self._post_with_retry(endpoint, headers, payload)
        elapsed = round((time.time() - t0) * 1000, 1)

        if resp.status_code != 200:
            log.error(
                "watsonx embeddings error",
                extra={"status": resp.status_code, "body": resp.text[:500]},
            )
            raise RuntimeError(
                f"watsonx embeddings error {resp.status_code}: {resp.text[:300]}"
            )

        data    = resp.json()
        if "results" in data:
            vectors = [item.get("embedding") for item in data["results"]]
        else:
            vectors = [item.get("embedding") for item in data.get("data", [])]
        if not vectors or any(v is None for v in vectors):
            raise RuntimeError(
                f"watsonx embeddings: unexpected response shape: {list(data.keys())}"
            )

        log.debug(
            "watsonx embed ok",
            extra={"batch": len(texts), "dim": len(vectors[0]), "ms": elapsed},
        )
        return vectors

    def _post_with_retry(
        self,
        url:     str,
        headers: Dict[str, str],
        payload: Dict[str, Any],
    ) -> requests.Response:
        """POST with exponential back-off for transient server errors."""
        for attempt in range(self._MAX_RETRY):
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code not in self._RETRY_ON:
                return resp
            # Refresh token in case it expired mid-retry
            headers["Authorization"] = f"Bearer {self._iam_token()}"
            wait = self._BASE_DELAY * (2 ** attempt) + random.uniform(0, 0.5)
            log.warning(
                "watsonx transient error — retrying",
                extra={"attempt": attempt + 1, "status": resp.status_code,
                       "wait_s": round(wait, 2)},
            )
            time.sleep(wait)
        # Final attempt (non-200 handled by caller)
        return requests.post(url, headers=headers, json=payload, timeout=60)

    def _iam_token(self) -> str:
        # Fast path — no lock needed when token is still fresh
        if self._token and (time.time() - self._token_ts) < self._TOKEN_TTL:
            return self._token
        with self._token_lock:
            # Re-check inside the lock — another thread may have refreshed while we waited
            if self._token and (time.time() - self._token_ts) < self._TOKEN_TTL:
                return self._token
            t0   = time.time()
            resp = requests.post(
                "https://iam.cloud.ibm.com/identity/token",
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                      "apikey": self._api_key},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            resp.raise_for_status()
            self._token    = resp.json()["access_token"]
            self._token_ts = time.time()
            log.debug("IAM token refreshed", extra={"ms": round((time.time() - t0) * 1000, 1)})
            return self._token


# ===========================================================================
# Local sentence-transformers provider
# ===========================================================================

class LocalSTEmbedding(EmbeddingProvider):
    """sentence-transformers embedding provider (runs locally, no API calls)."""

    def __init__(self, model_name: str, device: str = "cpu") -> None:
        if not _LOCAL_EMBED_AVAILABLE:
            raise RuntimeError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name, device=device)
        log.info("Local ST model loaded", extra={"model": model_name, "device": device})

    def embed(self, texts: List[str]) -> List[List[float]]:  # type: ignore[override]
        if not texts:
            return []
        t0   = time.time()
        vecs = self._model.encode(texts, normalize_embeddings=True).tolist()
        log.debug(
            "local embed ok",
            extra={"batch": len(texts), "dim": len(vecs[0]) if vecs else 0,
                   "ms": round((time.time() - t0) * 1000, 1)},
        )
        return vecs


# ===========================================================================
# Model dimension table (A5 — single source of truth, was duplicated in ingest)
# ===========================================================================

# Maps model ID → embedding vector dimension.
# Used by ingest pipelines to set the correct OpenSearch k-NN field dimension
# without issuing a probe-embed call.
_MODEL_DIMS: Dict[str, int] = {
    "ibm-granite/granite-embedding-125m-english": 768,
    "ibm-granite/granite-embedding-278m-english": 1024,
    "ibm-granite/granite-embedding-30m-english":  384,
    "ibm/slate-30m-english-rtrvr-v2":            384,
    "BAAI/bge-base-en-v1.5":                      768,
    "BAAI/bge-large-en-v1.5":                    1024,
    "BAAI/bge-m3":                               1024,
    "all-MiniLM-L6-v2":                           384,
    "all-mpnet-base-v2":                          768,
    "text-embedding-ada-002":                    1536,
}


def get_model_dim(cfg: Dict[str, str]) -> int:
    """
    Return the embedding vector dimension for the configured model.

    Resolution order:
    1. Explicit ``VECTOR_DIM`` env var  — allows override for unknown models.
    2. ``_MODEL_DIMS`` lookup           — covers all known models.
    3. Default 768                      — safe fallback; a warning is logged.

    A5 — this function was previously duplicated as ``_resolve_dim()`` inside
    ``ingest_opensearch.py``; callers should now import from here instead.
    """
    if cfg.get("VECTOR_DIM"):
        try:
            return int(cfg["VECTOR_DIM"])
        except ValueError:
            log.warning(
                "Invalid VECTOR_DIM env var — ignoring, using model default",
                extra={"val": cfg.get("VECTOR_DIM")},
            )

    provider = cfg.get("EMBED_PROVIDER", "auto").lower()
    has_wx   = bool(
        cfg.get("WATSONX_API_KEY")
        and cfg.get("WATSONX_URL")
        and cfg.get("WATSONX_PROJECT_ID")
    )
    if provider == "watsonx" or (provider == "auto" and has_wx):
        model = cfg.get("EMBED_MODEL", "")
    else:
        model = cfg.get("EMBED_ST_MODEL", "")

    dim = _MODEL_DIMS.get(model)
    if dim is None:
        log.warning(
            "Unknown model — defaulting to dim=768. "
            "Set VECTOR_DIM env var to override.",
            extra={"model": model},
        )
        dim = 768
    return dim


# ===========================================================================
# Factory
# ===========================================================================

def build_embedder(cfg: Dict[str, str]) -> EmbeddingProvider:
    """
    Return the appropriate EmbeddingProvider from configuration.

    Provider selection order:
      1. If EMBED_PROVIDER=watsonx  → WatsonxEmbedding
      2. If EMBED_PROVIDER=st       → LocalSTEmbedding
      3. If EMBED_PROVIDER=auto (default):
           → WatsonxEmbedding  when WATSONX_API_KEY + WATSONX_URL + WATSONX_PROJECT_ID are set
           → LocalSTEmbedding  otherwise
    """
    provider = cfg.get("EMBED_PROVIDER", "auto").lower()
    has_wx   = bool(
        cfg.get("WATSONX_API_KEY")
        and cfg.get("WATSONX_URL")
        and cfg.get("WATSONX_PROJECT_ID")
    )

    if provider == "watsonx" or (provider == "auto" and has_wx):
        log.info("Embedding provider: watsonx", extra={"model": cfg.get("EMBED_MODEL")})
        return WatsonxEmbedding(
            cfg["WATSONX_API_KEY"],
            cfg["WATSONX_URL"],
            cfg["WATSONX_PROJECT_ID"],
            cfg["EMBED_MODEL"],
        )

    log.info(
        "Embedding provider: sentence-transformers",
        extra={"model": cfg.get("EMBED_ST_MODEL"), "device": cfg.get("ST_DEVICE", "cpu")},
    )
    return LocalSTEmbedding(
        cfg["EMBED_ST_MODEL"],
        device=cfg.get("ST_DEVICE", "cpu"),
    )
