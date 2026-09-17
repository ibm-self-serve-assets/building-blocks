"""
ingest.py — unified ingestion entry point

Reads VECTOR_BACKEND from the environment and delegates to the matching
backend implementation.

  VECTOR_BACKEND=opensearch   (default)
      → runs ingest_opensearch.py pipeline
      → stores embeddings in an OpenSearch k-NN index

  VECTOR_BACKEND=pgvector
      → runs ingest_pgvector.py pipeline
      → stores embeddings in a PostgreSQL pgvector table

Both backends share the same source connectors (PostgreSQL, Db2) and the same
embedding providers (sentence-transformers, watsonx).  All other env vars
(PG_HOST, EMBED_PROVIDER, etc.) remain unchanged — only VECTOR_BACKEND
switches which storage backend is used.

Usage
-----
  # OpenSearch backend (default)
  VECTOR_BACKEND=opensearch python ingest.py

  # pgvector backend
  VECTOR_BACKEND=pgvector python ingest.py

  # Or just rely on the value in .env
  python ingest.py
"""

from __future__ import annotations

import os
import sys

# ── Load .env early so os.getenv() sees the value ──
# Resolution order: module-local .env → NL2SQL root .env → cwd fallback
try:
    from dotenv import load_dotenv
    _load_dotenv_path = next(
        (p for p in (
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"),
        ) if os.path.exists(p)),
        ".env",
    )
    load_dotenv(dotenv_path=_load_dotenv_path, override=True)
except Exception:
    pass

_VALID_BACKENDS = ("opensearch", "pgvector")

def _get_backend() -> str:
    backend = os.getenv("VECTOR_BACKEND", "opensearch").strip().lower()
    if backend not in _VALID_BACKENDS:
        print(
            f"[ingest] ERROR: VECTOR_BACKEND='{backend}' is not valid. "
            f"Choose one of: {', '.join(_VALID_BACKENDS)}",
            file=sys.stderr,
        )
        sys.exit(2)
    return backend


if __name__ == "__main__":
    backend = _get_backend()
    print(f"[ingest] VECTOR_BACKEND={backend} — starting ingestion pipeline")

    if backend == "opensearch":
        import ingest_opensearch as _os
        cfg = _os.load_config()
        _os.validate_config(cfg)
        _os.ingest(cfg, batch_size=int(cfg.get("BATCH_SIZE", "64")))

    elif backend == "pgvector":
        import ingest_pgvector as _pg
        _pg.initialize_and_validate_env()
        cfg = _pg.load_config()
        _pg.ingest_all(cfg, batch_size=128)
