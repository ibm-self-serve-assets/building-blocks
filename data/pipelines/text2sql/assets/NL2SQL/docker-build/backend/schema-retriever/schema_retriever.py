"""
schema_retriever.py — unified schema retriever entry point

Reads VECTOR_BACKEND from the environment and starts the matching
FastAPI service.

  VECTOR_BACKEND=opensearch   (default)
      → schema_retriever_opensearch.py
      → k-NN search against an OpenSearch index
      → endpoints: /retrieve-schema, /retrieve-schema/hybrid, /retrieve-schema/rrf

  VECTOR_BACKEND=pgvector
      → schema_retriever_pgvector.py
      → cosine similarity search against a PostgreSQL pgvector table
      → endpoint: /retrieve-schema

Both services expose GET /health and POST /retrieve-schema with the same
request/response shape so that callers (watsonx Orchestrate, etc.) do not
need to change when switching backends.

Usage
-----
  # OpenSearch backend (default)
  VECTOR_BACKEND=opensearch uvicorn schema_retriever:app --host 0.0.0.0 --port 8080

  # pgvector backend
  VECTOR_BACKEND=pgvector uvicorn schema_retriever:app --host 0.0.0.0 --port 8080

  # Or run directly (reads VECTOR_BACKEND from .env)
  python schema_retriever.py
"""

from __future__ import annotations

import os
import sys

# ── Load .env early so os.getenv() sees the value before the backend is imported ──
# Resolution order: module-local .env → NL2SQL root .env → cwd fallback
try:
    from dotenv import load_dotenv
    _load_dotenv_path = next(
        (p for p in (
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
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
            f"[schema_retriever] ERROR: VECTOR_BACKEND='{backend}' is not valid. "
            f"Choose one of: {', '.join(_VALID_BACKENDS)}",
            file=sys.stderr,
        )
        sys.exit(2)
    return backend


_BACKEND = _get_backend()

# ── Import the app object from the chosen backend module ──
# uvicorn targets `schema_retriever:app` — this re-export makes that work
# regardless of which backend is selected.

if _BACKEND == "opensearch":
    from schema_retriever_opensearch import app  # noqa: F401  (re-exported as `app`)
elif _BACKEND == "pgvector":
    from schema_retriever_pgvector import app    # noqa: F401  (re-exported as `app`)


# ── Direct run ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"[schema_retriever] VECTOR_BACKEND={_BACKEND} — starting service")

    if _BACKEND == "pgvector":
        # pgvector retriever requires explicit startup initialisation before uvicorn
        import schema_retriever_pgvector as _pg
        _pg.initialize_and_validate_env()
        _pg.CFG = _pg.load_config()
        _pg.EMBEDDER = _pg.get_embedder(_pg.CFG)

    try:
        import uvicorn
        uvicorn.run(
            "schema_retriever:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            reload=os.getenv("RELOAD", "false").lower() in ("1", "true", "yes"),
        )
    except ImportError:
        print(
            "[schema_retriever] uvicorn not installed. "
            "pip install 'uvicorn[standard]'",
            file=sys.stderr,
        )
        sys.exit(2)
