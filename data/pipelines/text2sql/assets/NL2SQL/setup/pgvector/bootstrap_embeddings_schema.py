#!/usr/bin/env python3
"""
bootstrap_embeddings_schema.py

Automates creation of the pgvector parent table (partitioned by schema_name) and
per‑schema partitions + ivfflat indexes.

Environment (IBM Cloud Postgres):
  PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
  PG_SSLMODE=require (recommended)
  PG_SSLROOTCERT=/path/to/cert.pem (optional)

Embedding table config:
  PG_SCHEMA=public                 # where to create the embeddings table
  PG_TABLE_PREFIX=                 # optional prefix, e.g., "ai_"
  VECTOR_DIM=384                   # required if parent doesn't exist; otherwise ignored
  LISTS=100                        # ivfflat lists parameter
  SCHEMAS_INCLUDE=hr,sales,...     # optional CSV list; if unset, all non-system schemas are used

Usage:
  python bootstrap_embeddings_schema.py
"""

import os, sys, re, time, uuid
from typing import List, Optional

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
    pass  # ok if python-dotenv isn't installed

import psycopg2
from psycopg2 import sql

# pgvector available?
try:
    from pgvector.psycopg2 import register_vector
    HAS_PGVECTOR = True
except Exception:
    HAS_PGVECTOR = False

# ---------- Simple Logging ----------
import logging

RUN_ID = os.getenv("RUN_ID") or str(uuid.uuid4())
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

def kv(**kwargs) -> dict:
    """Helper to pass context: log.info('msg', extra=kv(a=1,b=2))."""
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
    logger = logging.getLogger("bootstrap")
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

# ---------- Env & Config ----------

def _bool_env(name: str, default: bool=False)->bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","y","on")

def initialize_and_validate_env():
    required = ["PG_HOST","PG_PORT","PG_DATABASE","PG_USER","PG_PASSWORD","PG_SSLMODE"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        log.error("Missing required environment variables", extra=kv(missing=missing))
        sys.exit(2)

    if os.getenv("PG_SSLMODE","require").lower() in ("verify-ca","verify-full"):
        if not os.getenv("PG_SSLROOTCERT"):
            log.error("PG_SSLROOTCERT required when PG_SSLMODE is verify-ca or verify-full")
            sys.exit(2)

    # info log of target
    log.info("Target database", extra=kv(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT","5432"),
        db=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        schema=os.getenv("PG_SCHEMA","public"),
        table_prefix=os.getenv("PG_TABLE_PREFIX",""),
        lists=int(os.getenv("LISTS","100"))
    ))

def load_config():
    cfg = {}
    cfg["PG_HOST"] = os.getenv('PG_HOST')
    cfg["PG_PORT"] = os.getenv('PG_PORT','5432')
    cfg["PG_DATABASE"] = os.getenv('PG_DATABASE')
    cfg["PG_USER"] = os.getenv('PG_USER')
    cfg["PG_PASSWORD"] = os.getenv('PG_PASSWORD')
    cfg["PG_SSLMODE"] = os.getenv('PG_SSLMODE','require')
    cfg["PG_SSLROOTCERT"] = os.getenv('PG_SSLROOTCERT')

    cfg["PG_SCHEMA"] = os.getenv('PG_SCHEMA','public')
    cfg["PG_TABLE_PREFIX"] = os.getenv('PG_TABLE_PREFIX','')
    cfg["TABLE_NAME"] = cfg["PG_TABLE_PREFIX"] + "schema_embeddings"

    cfg["VECTOR_DIM_RAW"] = os.getenv('VECTOR_DIM')  # may be None
    cfg["LISTS"] = int(os.getenv('LISTS','100'))
    cfg["SCHEMAS_INCLUDE"] = [s.strip() for s in os.getenv('SCHEMAS_INCLUDE','').split(',') if s.strip()] or None
    return cfg

# ---------- DB helpers ----------

def connect(cfg):
    dsn_parts = [
        f"host={cfg['PG_HOST']}",
        f"port={cfg['PG_PORT']}",
        f"dbname={cfg['PG_DATABASE']}",
        f"user={cfg['PG_USER']}",
        f"password={cfg['PG_PASSWORD']}",
        f"sslmode={cfg['PG_SSLMODE']}"
    ]
    if cfg["PG_SSLROOTCERT"]:
        dsn_parts.append(f"sslrootcert={cfg['PG_SSLROOTCERT']}")
    dsn = " ".join(dsn_parts)
    log.debug("Connecting to Postgres", extra=kv(
        dsn_redacted=f"host={cfg['PG_HOST']} port={cfg['PG_PORT']} dbname={cfg['PG_DATABASE']} user={cfg['PG_USER']} sslmode={cfg['PG_SSLMODE']}"
    ))
    conn = psycopg2.connect(dsn)
    if HAS_PGVECTOR:
        try:
            register_vector(conn)
        except psycopg2.ProgrammingError as e:
            if 'vector type not found' in str(e):
                log.warning("pgvector extension not yet active in database; registration deferred.")
            else:
                raise
    return conn

def _sanitize_identifier(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]+', '_', s)

def table_exists(conn, cfg) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema=%s AND table_name=%s
        """, (cfg["PG_SCHEMA"], cfg["TABLE_NAME"]))
        exists = cur.fetchone() is not None
        log.debug("Table exists check", extra=kv(schema=cfg["PG_SCHEMA"], table=cfg["TABLE_NAME"], exists=exists))
        return exists

def get_existing_dim(conn, cfg) -> Optional[int]:
    with conn.cursor() as cur:
        try:
            cur.execute(sql.SQL('SELECT vector_dims(embedding) FROM {}.{} LIMIT 1').format(
                sql.Identifier(cfg["PG_SCHEMA"]), sql.Identifier(cfg["TABLE_NAME"])
            ))
            row = cur.fetchone()
            dim = row[0] if row else None
            log.debug("Existing vector dim", extra=kv(dim=dim))
            return dim
        except Exception:
            log.debug("vector_dims not available (table empty or not created)")
            return None

def parent_has_rows(conn, cfg) -> bool:
    with conn.cursor() as cur:
        cur.execute(sql.SQL('SELECT EXISTS (SELECT 1 FROM {}.{} LIMIT 1)').format(
            sql.Identifier(cfg["PG_SCHEMA"]), sql.Identifier(cfg["TABLE_NAME"])
        ))
        has = cur.fetchone()[0]
        log.debug("Parent has rows", extra=kv(has_rows=has))
        return has

def ensure_parent(conn, cfg, vector_dim:int):
    log.info("Ensuring parent table", extra=kv(schema=cfg["PG_SCHEMA"], table=cfg["TABLE_NAME"], vector_dim=vector_dim))
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        if HAS_PGVECTOR:
            try:
                register_vector(conn)
            except Exception:
                pass
        cur.execute(sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                schema_name TEXT NOT NULL,
                table_name  TEXT NOT NULL,
                table_id    TEXT GENERATED ALWAYS AS (schema_name || '.' || table_name) STORED,
                columns_json JSONB NOT NULL,
                pk_json       JSONB NOT NULL,
                fk_json       JSONB NOT NULL,
                sample_rows_json JSONB NOT NULL,
                text_agg      TEXT NOT NULL,
                embedding     VECTOR({}) NOT NULL,
                CONSTRAINT {} PRIMARY KEY (schema_name, table_name)
            ) PARTITION BY LIST (schema_name);
        """).format(
            sql.Identifier(cfg["PG_SCHEMA"]),
            sql.Identifier(cfg["TABLE_NAME"]),
            sql.SQL(str(vector_dim)),  # as literal
            sql.Identifier(f'{cfg["TABLE_NAME"]}_pk')
        ))
        cur.execute(sql.SQL('CREATE INDEX IF NOT EXISTS {} ON {}.{} (table_name);').format(
            sql.Identifier(f'{cfg["TABLE_NAME"]}_tblname_idx'),
            sql.Identifier(cfg["PG_SCHEMA"]),
            sql.Identifier(cfg["TABLE_NAME"])
        ))
    conn.commit()

def ensure_dim(conn, cfg, desired:int):
    if not table_exists(conn, cfg):
        ensure_parent(conn, cfg, desired)
        return desired
    existing = get_existing_dim(conn, cfg)
    if existing is None:
        log.info("Altering vector dimension on empty table", extra=kv(desired_dim=desired))
        with conn.cursor() as cur:
            cur.execute(sql.SQL('ALTER TABLE {}.{} ALTER COLUMN embedding TYPE vector({});').format(
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(cfg["TABLE_NAME"]),
                sql.SQL(str(desired))
            ))
        conn.commit()
        return desired
    if existing != desired:
        log.error("Vector dimension mismatch", extra=kv(existing_dim=existing, desired_dim=desired))
        raise RuntimeError(
            f"Vector dimension mismatch: existing={existing}, desired={desired}. "
            "Table has data, cannot auto-migrate. Recreate table or re-embed."
        )
    return existing

def list_user_schemas(conn) -> List[str]:
    with conn.cursor() as cur:
        cur.execute("""
        SELECT nspname
        FROM pg_namespace
        WHERE nspname NOT IN ('pg_catalog','information_schema','pg_toast')
          AND nspname NOT LIKE 'pg_temp%%'
          AND nspname NOT LIKE 'pg_toast_temp%%'
        ORDER BY 1
        """)
        result = [r[0] for r in cur.fetchall()]
        log.debug("User schemas discovered", extra=kv(count=len(result)))
        return result

def partition_exists(conn, cfg, part_name:str) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relname = %s
        """, (cfg["PG_SCHEMA"], part_name))
        exists = cur.fetchone() is not None
        log.debug("Partition exists check", extra=kv(schema=cfg["PG_SCHEMA"], partition=part_name, exists=exists))
        return exists

def ensure_partition(conn, cfg, schema_name:str):
    part_name = f'{cfg["TABLE_NAME"]}_p_{_sanitize_identifier(schema_name)}'
    idx_name = f'{part_name}_emb_ivfflat_idx'
    t0 = time.time()
    with conn.cursor() as cur:
        # Create partition table if missing
        if not partition_exists(conn, cfg, part_name):
            cur.execute(sql.SQL(
                "CREATE TABLE {}.{} PARTITION OF {}.{} FOR VALUES IN ({});"
            ).format(
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(part_name),
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(cfg["TABLE_NAME"]),
                sql.Literal(schema_name)  # literal value for partition key
            ))
            log.info("Created partition", extra=kv(schema_name=schema_name, partition=part_name))

        # Create IVFFLAT index on the partition if missing
        cur.execute(sql.SQL(
            "CREATE INDEX IF NOT EXISTS {} ON {}.{} USING ivfflat (embedding vector_l2_ops) WITH (lists = {});"
        ).format(
            sql.Identifier(idx_name),
            sql.Identifier(cfg["PG_SCHEMA"]),
            sql.Identifier(part_name),
            sql.SQL(str(cfg["LISTS"]))
        ))
    conn.commit()
    dt = round((time.time() - t0) * 1000, 1)
    log.info("Ensured partition/index", extra=kv(schema_name=schema_name, partition=part_name, idx=idx_name, lists=cfg["LISTS"], elapsed_ms=dt))

# ---------- Main ----------

def main():
    try:
        initialize_and_validate_env()
        cfg = load_config()

        # Pre-flight: parent exists?
        conn_probe = connect(cfg)
        parent_exists = table_exists(conn_probe, cfg)
        conn_probe.close()

        if not parent_exists and not cfg["VECTOR_DIM_RAW"]:
            log.error("VECTOR_DIM is required for first-time bootstrap (parent table doesn't exist).")
            sys.exit(2)

        conn = connect(cfg)
        try:
            desired_dim = int(cfg["VECTOR_DIM_RAW"]) if cfg["VECTOR_DIM_RAW"] else (get_existing_dim(conn, cfg) or 384)
            dim_final = ensure_dim(conn, cfg, desired_dim)
            log.info("Parent table ready", extra=kv(vector_dim=dim_final, table=cfg["TABLE_NAME"], schema=cfg["PG_SCHEMA"]))

            # Determine schemas to prepare
            schemas = cfg["SCHEMAS_INCLUDE"] or list_user_schemas(conn)
            if not schemas:
                log.warning("No user schemas discovered; nothing to partition/index.")
                return

            for sch in schemas:
                try:
                    ensure_partition(conn, cfg, sch)
                except Exception:
                    log.exception("Ensure partition/index failed", extra=kv(schema_name=sch))
                    raise

            log.info("Bootstrap complete", extra=kv(schemas=len(schemas), lists=cfg["LISTS"]))
        finally:
            try:
                conn.close()
            except Exception:
                pass

    except SystemExit:
        raise
    except Exception:
        log.exception("Bootstrap failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
