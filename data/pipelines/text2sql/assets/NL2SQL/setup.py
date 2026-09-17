"""
setup.py — unified one-time setup entry point

Reads VECTOR_BACKEND from the environment and runs the matching
backend initialisation — creating all necessary database objects
so the ingestion pipeline can run.

  VECTOR_BACKEND=opensearch   (default)
      → reads .env (root) or setup/opensearch/.env
      → creates the schema_embeddings k-NN index in OpenSearch
      → idempotent: safe to re-run; skips if index already exists

  VECTOR_BACKEND=pgvector
      → reads .env (root) or setup/pgvector/.env
      → creates the schema_embeddings partitioned table + ivfflat
        indexes in PostgreSQL
      → idempotent: safe to re-run; skips objects that already exist

Run this once before the first ingestion run, and again whenever you
drop and recreate the index / table.

Usage
-----
  # From the NL2SQL/ root — backend is read from the root .env
  VECTOR_BACKEND=opensearch python setup.py
  VECTOR_BACKEND=pgvector   python setup.py

  # Or just: python setup.py  (reads VECTOR_BACKEND from .env)
"""

from __future__ import annotations

import os
import sys

_VALID_BACKENDS = ("opensearch", "pgvector")


def _read_backend() -> str:
    """
    Read VECTOR_BACKEND from the environment.
    If not set, try the root NL2SQL/.env first, then the backend-specific .env
    files, so the caller doesn't have to export the variable explicitly.
    """
    # 1. Already in the environment
    val = os.environ.get("VECTOR_BACKEND", "").strip().lower()
    if val:
        pass
    else:
        # 2. Root .env → setup/opensearch/.env → setup/pgvector/.env
        for candidate in (
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup", "opensearch", ".env"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup", "pgvector", ".env"),
        ):
            if os.path.exists(candidate):
                with open(candidate) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("VECTOR_BACKEND="):
                            val = line.split("=", 1)[1].strip().lower()
                            break
                if val:
                    break
        # 3. Default
        if not val:
            val = "opensearch"

    if val not in _VALID_BACKENDS:
        print(
            f"[setup] ERROR: VECTOR_BACKEND='{val}' is not valid. "
            f"Choose one of: {', '.join(_VALID_BACKENDS)}",
            file=sys.stderr,
        )
        sys.exit(2)
    return val


def _setup_opensearch() -> None:
    """Create the OpenSearch k-NN index if it does not already exist."""
    # Resolution order: root NL2SQL/.env → setup/opensearch/.env
    try:
        from dotenv import load_dotenv
        _root_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        _sub_env  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup", "opensearch", ".env")
        for _env_path in (_root_env, _sub_env):
            if os.path.exists(_env_path):
                load_dotenv(dotenv_path=_env_path, override=True)
    except Exception:
        pass

    # Add setup/opensearch to path so opensearch_index_mapping can be imported
    _setup_os_dir = os.path.join(os.path.dirname(__file__), "setup", "opensearch")
    sys.path.insert(0, _setup_os_dir)

    try:
        from opensearchpy import OpenSearch
    except ImportError:
        print(
            "[setup] ERROR: opensearch-py is not installed.\n"
            "  pip install opensearch-py",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        from opensearch_index_mapping import MAPPING
    except ImportError:
        print(
            "[setup] ERROR: cannot import opensearch_index_mapping from setup_opensearch/.\n"
            "  Make sure setup_opensearch/opensearch_index_mapping.py exists.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Override VECTOR_DIM in the mapping if explicitly set
    vector_dim = int(os.getenv("VECTOR_DIM", "768"))
    MAPPING["mappings"]["properties"]["embedding"]["dimension"] = vector_dim

    use_ssl    = os.getenv("OS_USE_SSL", "false").lower() in ("1", "true", "yes")
    verify     = os.getenv("OS_VERIFY_CERTS", "false").lower() in ("1", "true", "yes")
    http_auth  = None
    if os.getenv("OS_USER") and os.getenv("OS_PASSWORD"):
        http_auth = (os.getenv("OS_USER"), os.getenv("OS_PASSWORD"))

    client = OpenSearch(
        hosts=[{
            "host": os.getenv("OS_HOST", "localhost"),
            "port": int(os.getenv("OS_PORT", "9200")),
        }],
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=verify,
        ssl_assert_hostname=verify,
        ssl_show_warn=False,
        timeout=30,
    )

    index = os.getenv("OS_INDEX", "schema_embeddings")

    try:
        info = client.info()
        print(
            f"[setup] Connected to OpenSearch "
            f"{info.get('version', {}).get('number', '?')} "
            f"at {os.getenv('OS_HOST', 'localhost')}:{os.getenv('OS_PORT', '9200')}"
        )
    except Exception as exc:
        print(f"[setup] ERROR: Cannot connect to OpenSearch — {exc}", file=sys.stderr)
        sys.exit(1)

    if client.indices.exists(index=index):
        mapping     = client.indices.get_mapping(index=index)
        actual_dim  = (
            mapping.get(index, {})
            .get("mappings", {})
            .get("properties", {})
            .get("embedding", {})
            .get("dimension")
        )
        print(
            f"[setup] Index '{index}' already exists "
            f"(embedding dimension={actual_dim}). Skipping creation."
        )
    else:
        client.indices.create(index=index, body=MAPPING)
        print(
            f"[setup] Index '{index}' created "
            f"(embedding dimension={vector_dim}, shards=1, replicas=1)."
        )


def _setup_pgvector() -> None:
    """Create the pgvector partitioned table and ivfflat indexes."""
    # Resolution order: root NL2SQL/.env → setup/pgvector/.env
    try:
        from dotenv import load_dotenv
        _root_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        _sub_env  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup", "pgvector", ".env")
        for _env_path in (_root_env, _sub_env):
            if os.path.exists(_env_path):
                load_dotenv(dotenv_path=_env_path, override=True)
    except Exception:
        pass

    # Add setup/pgvector to path and delegate to bootstrap_embeddings_schema
    _setup_pg_dir = os.path.join(os.path.dirname(__file__), "setup", "pgvector")
    sys.path.insert(0, _setup_pg_dir)

    try:
        import bootstrap_embeddings_schema as _bootstrap
    except ImportError as exc:
        print(
            f"[setup] ERROR: cannot import bootstrap_embeddings_schema — {exc}\n"
            "  Make sure setup/pgvector/bootstrap_embeddings_schema.py exists.",
            file=sys.stderr,
        )
        sys.exit(2)

    print("[setup] Running pgvector bootstrap …")
    _bootstrap.main()


if __name__ == "__main__":
    backend = _read_backend()
    print(f"[setup] VECTOR_BACKEND={backend}")

    if backend == "opensearch":
        _setup_opensearch()
    elif backend == "pgvector":
        _setup_pgvector()

    print("[setup] Done.")
