#!/usr/bin/env python3
"""
schema_retriever_pgvector.py

FastAPI service that searches schema embeddings stored in Postgres pgvector.
- Matches embedding provider options from the ingest program:
  - EMBED_PROVIDER = auto | watsonx | st
  - EMBED_MODEL (watsonx)
  - EMBED_ST_MODEL (sentence-transformers)
  - ST_DEVICE (cpu|cuda)
- Works with a partitioned table by schema_name
- Threaded connection pooling (psycopg2.pool.ThreadedConnectionPool) for high concurrency
- Uses shared embedders module with thread-safe IAM caching and exponential back-off
- Returns distance and a derived confidence score for each result
- Returns HTTP 503 on health check failure
"""

from __future__ import annotations

import os
import sys
import re
import time
import uuid
import json
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, Union

# --- Load .env early so os.getenv() sees values ---
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

# ---------- Logging ----------
import logging

RUN_ID = os.getenv("RUN_ID") or str(uuid.uuid4())
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def kv(**kwargs) -> dict:
    return kwargs

class SimpleFormatter(logging.Formatter):
    def format(self, record):
        base = (
            f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} "
            f"[{record.levelname}] "
            f"{record.filename}:{record.lineno} {record.funcName}() "
            f"run={RUN_ID} — {record.getMessage()}"
        )
        std = set(vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys())
        parts = []
        for attr, val in vars(record).items():
            if attr in std or attr in ("message",):
                continue
            parts.append(f"{attr}={repr(val)}")
        if parts:
            base += " | " + ", ".join(parts)
        if record.exc_info:
            return base + "\n" + self.formatException(record.exc_info)
        return base

def _setup_logger():
    logger = logging.getLogger("schema_api")
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(SimpleFormatter())
    logger.handlers = [handler]
    logger.propagate = False
    return logger

log = _setup_logger()

def _excepthook(exctype, value, tb):
    try:
        log.exception("Uncaught exception (global)", extra=kv(exctype=str(exctype.__name__)))
    finally:
        sys.__excepthook__(exctype, value, tb)
sys.excepthook = _excepthook

# ---------- Third-party imports ----------
import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extras import RealDictCursor
from psycopg2 import sql

try:
    from pgvector.psycopg2 import register_vector
    HAS_PGVECTOR = True
except Exception:
    HAS_PGVECTOR = False

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator
from sqlalchemy.exc import SAWarning
import warnings

# Optionally silence SAWarning about 'vector' type (cosmetic)
warnings.filterwarnings("ignore", message="Did not recognize type 'vector' of column 'embedding'", category=SAWarning)

# Shared embedding provider
from embedders import EmbeddingProvider, build_embedder

# ---------- Env & Config ----------
def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")

def initialize_and_validate_env():
    required = ["PG_HOST", "PG_PORT", "PG_DATABASE", "PG_USER", "PG_PASSWORD", "PG_SSLMODE"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        log.error("Missing required environment variables", extra=kv(missing=missing))
        raise SystemExit(2)

    if os.getenv("PG_SSLMODE", "require").lower() in ("verify-ca", "verify-full"):
        if not os.getenv("PG_SSLROOTCERT"):
            log.error("PG_SSLROOTCERT required when PG_SSLMODE is verify-ca or verify-full")
            raise SystemExit(2)

    provider = os.getenv("EMBED_PROVIDER", "auto").lower()
    if provider not in ("auto", "watsonx", "st"):
        log.error("Invalid EMBED_PROVIDER. Use one of: auto | watsonx | st", extra=kv(value=provider))
        raise SystemExit(2)

    wx_key = os.getenv("WATSONX_API_KEY")
    wx_url = os.getenv("WATSONX_URL")
    wx_proj = os.getenv("WATSONX_PROJECT_ID")
    has_wx = bool(wx_key and wx_url and wx_proj)

    if provider == "watsonx" or (provider == "auto" and has_wx):
        if not os.getenv("EMBED_MODEL"):
            log.error("EMBED_MODEL required for watsonx provider")
            raise SystemExit(2)
        log.info("Embedding provider: watsonx", extra=kv(mode=provider, model=os.getenv("EMBED_MODEL")))
    else:
        if not os.getenv("EMBED_ST_MODEL"):
            log.error("EMBED_ST_MODEL required for sentence-transformers provider")
            raise SystemExit(2)
        log.info("Embedding provider: sentence-transformers", extra=kv(mode=provider, model=os.getenv("EMBED_ST_MODEL"), device=os.getenv("ST_DEVICE", "cpu")))

    log.info("Embeddings table target", extra=kv(
        schema=os.getenv("PG_SCHEMA", "public"),
        table=os.getenv("PG_TABLE_PREFIX", "") + "schema_embeddings"
    ))

def load_config() -> Dict[str, Any]:
    cfg: Dict[str, Any] = {}
    # DB
    cfg["PG_HOST"] = os.getenv('PG_HOST')
    cfg["PG_PORT"] = os.getenv('PG_PORT', '5432')
    cfg["PG_DATABASE"] = os.getenv('PG_DATABASE')
    cfg["PG_USER"] = os.getenv('PG_USER')
    cfg["PG_PASSWORD"] = os.getenv('PG_PASSWORD')
    cfg["PG_SSLMODE"] = os.getenv('PG_SSLMODE', 'require')
    cfg["PG_SSLROOTCERT"] = os.getenv('PG_SSLROOTCERT')
    # Table
    cfg["PG_SCHEMA"] = os.getenv('PG_SCHEMA', 'public')
    cfg["PG_TABLE_PREFIX"] = os.getenv('PG_TABLE_PREFIX', '')
    cfg["TABLE_NAME"] = cfg["PG_TABLE_PREFIX"] + "schema_embeddings"
    # Query behavior & Pool
    cfg["TOP_K"] = int(os.getenv('TOP_K', '5'))
    cfg["POOL_MIN"] = int(os.getenv('POOL_MIN', '1'))
    cfg["POOL_MAX"] = int(os.getenv('POOL_MAX', '10'))
    # Embedding settings
    cfg["EMBED_PROVIDER"] = os.getenv("EMBED_PROVIDER", "auto").lower()
    cfg["EMBED_MODEL"] = os.getenv("EMBED_MODEL", "ibm-granite/granite-embedding-125m-english")
    cfg["EMBED_ST_MODEL"] = os.getenv("EMBED_ST_MODEL", "BAAI/bge-base-en-v1.5")
    cfg["ST_DEVICE"] = os.getenv("ST_DEVICE", "cpu")
    # watsonx creds
    cfg["WATSONX_API_KEY"] = os.getenv('WATSONX_API_KEY')
    cfg["WATSONX_URL"] = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    cfg["WATSONX_PROJECT_ID"] = os.getenv('WATSONX_PROJECT_ID')
    # Re-ranking
    cfg["RERANK_ENABLED"] = os.getenv("RERANK_ENABLED", "false")
    cfg["RERANK_PROVIDER"] = os.getenv("RERANK_PROVIDER", "cross-encoder")
    cfg["RERANK_MODEL"] = os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    cfg["RERANK_TOP_N"] = os.getenv("RERANK_TOP_N", "15")
    cfg["RERANK_DEVICE"] = os.getenv("RERANK_DEVICE", "cpu")
    return cfg

CFG: Optional[Dict[str, Any]] = None
EMBEDDER: Optional[EmbeddingProvider] = None
POOL: Optional[pg_pool.ThreadedConnectionPool] = None
RERANKER: Any = None

# ---------- DB Pool ----------
def _build_dsn(cfg: Dict[str, Any]) -> str:
    parts = [
        f"host={cfg['PG_HOST']}",
        f"port={cfg['PG_PORT']}",
        f"dbname={cfg['PG_DATABASE']}",
        f"user={cfg['PG_USER']}",
        f"password={cfg['PG_PASSWORD']}",
        f"sslmode={cfg['PG_SSLMODE']}",
        "application_name=text2sql_schema_retriever_pgvector",
    ]
    if cfg.get("PG_SSLROOTCERT"):
        parts.append(f"sslrootcert='{cfg['PG_SSLROOTCERT']}'")
    return " ".join(parts)

def init_pool(cfg: Dict[str, Any]) -> pg_pool.ThreadedConnectionPool:
    dsn = _build_dsn(cfg)
    pool = pg_pool.ThreadedConnectionPool(
        minconn=cfg["POOL_MIN"],
        maxconn=cfg["POOL_MAX"],
        dsn=dsn,
    )
    return pool

def get_connection():
    global POOL, CFG
    if POOL is None:
        if CFG is None:
            CFG = load_config()
        POOL = init_pool(CFG)
    conn = POOL.getconn()
    if HAS_PGVECTOR:
        try:
            register_vector(conn)
        except Exception:
            pass
    return conn

def release_connection(conn):
    global POOL
    if POOL is not None and conn is not None:
        try:
            POOL.putconn(conn)
        except Exception:
            pass

def connect():
    """Legacy compatibility helper."""
    return get_connection()

def get_embedder(cfg: Dict[str, Any]) -> EmbeddingProvider:
    return build_embedder(cfg)

# ---------- Request / Response models ----------
class Req(BaseModel):
    user_query: str
    # Accept a single schema name (str) OR a list of schema names for filtering.
    # e.g. schema_filter="public"  OR  schema_filter=["public","reporting"]
    schema_filter: Optional[Union[str, List[str]]] = None
    top_k: Optional[int] = None

    @field_validator("user_query")
    @classmethod
    def _nonempty_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_query must not be empty")
        return v.strip()

    @field_validator("schema_filter", mode="before")
    @classmethod
    def _normalise_schema_filter(cls, v):
        """Always coerce to a list of stripped strings, or None."""
        if v is None:
            return None
        if isinstance(v, str):
            v = [v]
        return [s.strip() for s in v if s and s.strip()]

def _sketches_for_table(table_full: str, columns: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    cols = [c.get("name") for c in columns if isinstance(c, dict) and "name" in c]
    date_cols = [c for c in cols if c and re.search(r"(date|time|timestamp)$", c, re.I)]
    sketches = [{"id": "count_rows", "sql": f"SELECT COUNT(*) AS cnt FROM {table_full};"}]
    if cols:
        first = cols[0]
        sketches.append({"id": "distinct_top", "sql": f'SELECT "{first}", COUNT(*) AS n FROM {table_full} GROUP BY 1 ORDER BY n DESC LIMIT 50;'})
    if date_cols:
        dc = date_cols[0]
        sketches.append({"id": "monthly_counts", "sql": f"SELECT date_trunc('month', {dc}) AS m, COUNT(*) AS n FROM {table_full} GROUP BY 1 ORDER BY 1;"})
    return sketches

# ---------- FastAPI lifespan ----------
@asynccontextmanager
async def _lifespan(app: FastAPI):
    global CFG, EMBEDDER, POOL, RERANKER
    try:
        initialize_and_validate_env()
        CFG = load_config()
        EMBEDDER = get_embedder(CFG)
        POOL = init_pool(CFG)
        try:
            from reranker import build_reranker
            RERANKER = build_reranker(CFG)
        except Exception:
            RERANKER = None
        log.info(
            "API startup complete",
            extra=kv(
                top_k=CFG["TOP_K"],
                table=CFG["TABLE_NAME"],
                schema=CFG["PG_SCHEMA"],
                pool_min=CFG["POOL_MIN"],
                pool_max=CFG["POOL_MAX"],
            ),
        )
    except SystemExit:
        raise
    except Exception:
        log.exception("Startup failed")
        raise
    yield
    if POOL is not None:
        try:
            POOL.closeall()
        except Exception:
            pass

app = FastAPI(title='Schema Retriever (pgvector, partitioned)', lifespan=_lifespan)

@app.get("/health")
def health(response: Response):
    """
    Liveness + Postgres ping.
    Returns HTTP 503 when Postgres is unreachable so Code Engine marks the instance unhealthy.
    """
    if CFG is None:
        response.status_code = 503
        return {"ok": False, "error": "Config not initialized"}
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        return {"ok": True, "db": "up", "provider": CFG["EMBED_PROVIDER"]}
    except Exception as e:
        log.exception("Health check failed")
        response.status_code = 503
        return {"ok": False, "error": str(e)}
    finally:
        if conn is not None:
            release_connection(conn)

@app.post('/retrieve-schema')
def retrieve_schema(req: Req):
    if CFG is None or EMBEDDER is None:
        log.error("Service not initialized (CFG/EMBEDDER is None)")
        raise HTTPException(503, "Service not initialized. Check startup logs.")

    t_request = time.time()
    if not req.user_query:
        raise HTTPException(400, "user_query is required")

    try:
        q_emb = EMBEDDER.embed([req.user_query])[0]
    except Exception as e:
        log.exception("Embedding failed")
        raise HTTPException(500, f"Embedding failed: {e}")

    # Client top_k always wins; fall back to server default only when not supplied.
    top_k = req.top_k if (req.top_k is not None and req.top_k > 0) else CFG["TOP_K"]
    rerank_enabled = str(CFG.get("RERANK_ENABLED", "false")).lower() in ("1", "true", "yes")
    fetch_k = max(top_k, int(CFG.get("RERANK_TOP_N", "15"))) if rerank_enabled else top_k

    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Use cosine distance (<=>). Embeddings are unit-normalised so cosine
        # distance = 1 - cosine_similarity, giving scores in [0, 1] with good
        # separation. L2 (<->) produced a narrow 0.67–0.98 band over 15 tables.
        select_base = sql.SQL("""
            SELECT
                schema_name,
                table_name,
                columns_json,
                pk_json,
                fk_json,
                sample_rows_json,
                text_agg,
                (embedding <=> %s::vector) AS distance
            FROM {}.{}
        """).format(sql.Identifier(CFG["PG_SCHEMA"]), sql.Identifier(CFG["TABLE_NAME"]))

        if req.schema_filter:
            query = select_base + sql.SQL(" WHERE schema_name = ANY(%s) ORDER BY distance LIMIT %s")
            cur.execute(query.as_string(cur), (q_emb, list(req.schema_filter), fetch_k))
        else:
            query = select_base + sql.SQL(" ORDER BY distance LIMIT %s")
            cur.execute(query.as_string(cur), (q_emb, fetch_k))

        rows = cur.fetchall()
    except Exception as e:
        log.exception("Query failed", extra=kv(top_k=top_k, has_filter=bool(req.schema_filter)))
        raise HTTPException(500, "Database query failed")
    finally:
        if conn is not None:
            release_connection(conn)

    results = []
    for r in rows:
        schema_name = r['schema_name']
        table_name = r['table_name']
        table_full = f'{schema_name}."{table_name}"'
        try:
            columns = json.loads(r['columns_json']) if isinstance(r['columns_json'], str) else r['columns_json']
            pk = json.loads(r['pk_json']) if isinstance(r['pk_json'], str) else r['pk_json']
            fk = json.loads(r['fk_json']) if isinstance(r['fk_json'], str) else r['fk_json']
            sample_rows = json.loads(r['sample_rows_json']) if isinstance(r['sample_rows_json'], str) else r['sample_rows_json']
        except Exception:
            columns = r['columns_json']
            pk = r['pk_json']
            fk = r['fk_json']
            sample_rows = r['sample_rows_json']

        # cosine distance ∈ [0, 2]; for unit-norm vectors it is ∈ [0, 1].
        # score = cosine similarity = 1 - cosine_distance (clamped to [0, 1]).
        distance = float(r.get('distance', 0.0))
        score = round(max(0.0, min(1.0, 1.0 - distance)), 6)
        confidence = round(1.0 / (1.0 + distance), 6)

        # Strip is_pii from column objects — internal ingestion detail, not for callers.
        clean_columns = []
        if isinstance(columns, list):
            for col in columns:
                if isinstance(col, dict):
                    clean_columns.append({k: v for k, v in col.items() if k != "is_pii"})
                else:
                    clean_columns.append(col)
        else:
            clean_columns = columns

        results.append({
            'table_id': f'{schema_name}.{table_name}',
            'schema_name': schema_name,
            'table_name': table_name,
            'columns': clean_columns,
            'pk': pk,
            'fk': fk,
            'sample_rows': sample_rows,
            'text_agg': r['text_agg'],
            'score': score,
            'distance': round(distance, 6),
            'confidence': confidence,
            'sketches': _sketches_for_table(table_full, clean_columns if isinstance(clean_columns, list) else [])
        })

    if rerank_enabled and RERANKER and results:
        try:
            results = RERANKER.rerank(req.user_query, results, top_k)
        except Exception as e:
            log.exception(f"Reranking failed: {e}")
            results = results[:top_k]
    else:
        results = results[:top_k]

    took_ms = round((time.time() - t_request) * 1000, 1)
    log.info("retrieve-schema served", extra=kv(results=len(results), took_ms=took_ms, filtered=bool(req.schema_filter)))
    return {'query': req.user_query, 'results': results, 'took_ms': took_ms}

# ---------- Optional direct run ----------
if __name__ == "__main__":
    try:
        initialize_and_validate_env()
        CFG = load_config()
        EMBEDDER = get_embedder(CFG)
        POOL = init_pool(CFG)
        import uvicorn
        uvicorn.run("schema_retriever_pgvector:app", host="0.0.0.0", port=int(os.getenv("PORT", "8080")), reload=_bool_env("RELOAD", False))
    except SystemExit:
        raise
    except Exception:
        log.exception("Startup failed")
