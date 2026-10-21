#!/usr/bin/env python3
"""
ingest_pgvector.py

- Introspects PostgreSQL schemas/tables
- Generates embeddings (watsonx Granite OR sentence-transformers MiniLM-L6)
- Stores them into a pgvector table partitioned by schema_name
- Creates per-schema partition + ivfflat index
- Strong logging & global excepthook
- Runtime provider selection (watsonx | st | auto)
- initialize_and_validate_env() ensures required env vars exist, else exits

Run examples:
  LOG_LEVEL=DEBUG EMBED_PROVIDER=st EMBED_ST_MODEL=all-MiniLM-L6-v2 python ingest_pgvector.py
  EMBED_PROVIDER=watsonx WATSONX_API_KEY=... WATSONX_URL=... WATSONX_PROJECT_ID=... python ingest_pgvector.py
"""

import os, json, sys, re, time, uuid
from typing import List
from datetime import date, datetime
from decimal import Decimal

# --- Load .env early so os.getenv() sees values ---
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
    pass  # it's fine if python-dotenv isn't installed

import psycopg2
from psycopg2.extras import execute_values
from psycopg2 import sql  # <-- for safe DDL

from metadata_enricher import MetadataEnricher

try:
    from pgvector.psycopg2 import register_vector
    HAS_PGVECTOR = True
except Exception:
    HAS_PGVECTOR = False

# sentence-transformers available?
try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBED_AVAILABLE = True
except Exception:
    LOCAL_EMBED_AVAILABLE = False

import requests
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SAWarning
import warnings
# Optional: silence SAWarning about unknown 'vector' type (cosmetic)
warnings.filterwarnings("ignore", message="Did not recognize type 'vector' of column 'embedding'", category=SAWarning)

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
    logger = logging.getLogger("ingest")
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

# ---------- JSON helpers (robust dumps) ----------

def _json_default(o):
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        try:
            return float(o)
        except Exception:
            return str(o)
    if isinstance(o, uuid.UUID):
        return str(o)
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, bytes):
        try:
            return o.decode("utf-8", "ignore")
        except Exception:
            return str(o)
    return str(o)

def safe_json_dumps(obj) -> str:
    return json.dumps(obj, default=_json_default, ensure_ascii=False)

# ---------- Configuration helpers ----------

def _bool_env(name: str, default: bool=False)->bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1","true","yes","y","on")

def initialize_and_validate_env():
    """
    Validate env based on provider choice.
    Exit(2) with clear message if required keys are missing.
    """
    required = []
    # Core DB
    core_db = ["PG_HOST","PG_PORT","PG_DATABASE","PG_USER","PG_PASSWORD","PG_SSLMODE"]
    required += core_db

    # Provider choice
    embed_provider = os.getenv("EMBED_PROVIDER","auto").lower()
    if embed_provider not in ("auto","watsonx","st"):
        log.error("Invalid EMBED_PROVIDER. Use one of: auto | watsonx | st", extra=kv(value=embed_provider))
        sys.exit(2)

    # When watsonx is forced OR auto with creds present, require the 3 creds
    wx_key = os.getenv("WATSONX_API_KEY")
    wx_url = os.getenv("WATSONX_URL")
    wx_proj = os.getenv("WATSONX_PROJECT_ID")
    has_wx = bool(wx_key and wx_url and wx_proj)

    if embed_provider == "watsonx" or (embed_provider == "auto" and has_wx):
        required += ["WATSONX_API_KEY","WATSONX_URL","WATSONX_PROJECT_ID"]
        required += ["EMBED_MODEL"]
    else:
        required += ["EMBED_ST_MODEL"]
        if not LOCAL_EMBED_AVAILABLE:
            log.error("sentence-transformers not installed but EMBED_PROVIDER indicates ST/auto without watsonx creds.")
            sys.exit(2)

    if os.getenv("PG_SSLMODE","require").lower() in ("verify-ca","verify-full"):
        if not os.getenv("PG_SSLROOTCERT"):
            log.error("PG_SSLROOTCERT required when PG_SSLMODE is verify-ca or verify-full")
            sys.exit(2)

    missing = [k for k in required if not os.getenv(k)]
    if missing:
        log.error("Missing required environment variables", extra=kv(missing=missing))
        sys.exit(2)

    if embed_provider == "auto" and has_wx:
        log.info("Provider decision: watsonx (auto)", extra=kv(provider="watsonx"))
    elif embed_provider == "auto":
        log.info("Provider decision: sentence-transformers (auto fallback)", extra=kv(provider="st"))
    else:
        log.info(f"Provider decision: {embed_provider}", extra=kv(provider=embed_provider))

# ---------- Read config (after validation) ----------

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
    cfg["VECTOR_DIM"] = int(os.getenv('VECTOR_DIM')) if os.getenv('VECTOR_DIM') else None
    cfg["SAMPLE_ROW_LIMIT"] = int(os.getenv('SAMPLE_ROW_LIMIT','3'))
    cfg["PII_PATTERNS"] = [p.strip() for p in os.getenv('PII_COLUMN_PATTERNS','ssn,email,phone,card').split(',') if p.strip()]
    cfg["EMBED_PROVIDER"] = os.getenv("EMBED_PROVIDER","auto").lower()
    cfg["EMBED_MODEL"] = os.getenv("EMBED_MODEL","ibm-granite/granite-embedding-30m-english")
    cfg["EMBED_ST_MODEL"] = os.getenv("EMBED_ST_MODEL","all-MiniLM-L6-v2")
    cfg["ST_DEVICE"] = os.getenv("ST_DEVICE","cpu")
    cfg["SCHEMAS_INCLUDE"] = [s.strip() for s in os.getenv("SCHEMAS_INCLUDE","").split(",") if s.strip()] or None
    cfg["LISTS"] = int(os.getenv("LISTS","100"))  # for ivfflat
    cfg["METADATA_ENRICHMENT_ENABLED"] = os.getenv("METADATA_ENRICHMENT_ENABLED", "true")
    cfg["METADATA_ENRICHMENT_FILE"] = os.getenv("METADATA_ENRICHMENT_FILE", os.getenv("SCHEMA_METADATA_FILE", ""))
    return cfg

# ---------- Providers ----------

class EmbeddingProvider:
    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

class WatsonxEmbedding(EmbeddingProvider):
    def __init__(self, api_key: str, url: str, project_id: str, model_id: str):
        self.api_key = api_key; self.url = url.rstrip('/'); self.project_id = project_id; self.model_id = model_id
        if not (self.api_key and self.url and self.project_id and self.model_id):
            raise RuntimeError("WatsonxEmbedding: missing credentials or model id")

    def embed(self, texts: List[str]) -> List[List[float]]:
        endpoint = f"{self.url}/ml/v1/text/embeddings?version=2023-05-29"
        headers = {"Authorization": f"Bearer {self._get_iam_token()}", "Content-Type": "application/json"}
        payload = {"input": texts, "inputs": texts, "model_id": self.model_id, "project_id": self.project_id}
        t0 = time.time()
        r = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        dt = round((time.time() - t0) * 1000, 1)
        if r.status_code != 200:
            body = r.text[:800]
            log.error("watsonx embeddings error", extra=kv(status=r.status_code, elapsed_ms=dt, endpoint=endpoint, batch_size=len(texts), resp_body=body))
            raise RuntimeError(f"watsonx embeddings error: {r.status_code} {body}")
        data = r.json()
        if "results" in data:
            vectors = [item.get("embedding") for item in data["results"]]
        else:
            vectors = [item.get("embedding") for item in data.get("data", [])]
        if not vectors or any(v is None for v in vectors):
            log.error("watsonx embeddings: unexpected response", extra=kv(elapsed_ms=dt, endpoint=endpoint, response_keys=list(data.keys()), raw_sample=safe_json_dumps(data)[:800]))
            raise RuntimeError(f"watsonx embeddings: unexpected response {data}")
        log.debug("watsonx embeddings ok", extra=kv(elapsed_ms=dt, endpoint=endpoint, batch_size=len(texts), dim=len(vectors[0])))
        return vectors

    def _get_iam_token(self)->str:
        t0 = time.time()
        resp = requests.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={"grant_type":"urn:ibm:params:oauth:grant-type:apikey","apikey": self.api_key},
            headers={"Content-Type":"application/x-www-form-urlencoded"},
            timeout=30
        )
        resp.raise_for_status()
        dt = round((time.time() - t0) * 1000, 1)
        log.debug("iam token acquired", extra=kv(elapsed_ms=dt))
        return resp.json()["access_token"]

class LocalSTEmbedding(EmbeddingProvider):
    def __init__(self, model_name: str, device: str = "cpu"):
        if not LOCAL_EMBED_AVAILABLE:
            raise RuntimeError("sentence-transformers not installed. pip install sentence-transformers")
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name, device=device)

    def embed(self, texts: List[str]) -> List[List[float]]:
        t0 = time.time()
        vecs = self.model.encode(texts, normalize_embeddings=False).tolist()
        dt = round((time.time() - t0) * 1000, 1)
        log.debug("local embeddings ok", extra=kv(elapsed_ms=dt, batch_size=len(texts), dim=len(vecs[0])))
        return vecs

def get_embedder(cfg)->EmbeddingProvider:
    provider = cfg["EMBED_PROVIDER"]
    has_wx = bool(os.getenv("WATSONX_API_KEY") and os.getenv("WATSONX_URL") and os.getenv("WATSONX_PROJECT_ID"))
    try:
        if provider == "watsonx":
            log.info("Embedding provider: watsonx (forced)", extra=kv(model=cfg["EMBED_MODEL"]))
            return WatsonxEmbedding(os.getenv("WATSONX_API_KEY"), os.getenv("WATSONX_URL"),
                                    os.getenv("WATSONX_PROJECT_ID"), cfg["EMBED_MODEL"])
        if provider == "st":
            log.info("Embedding provider: sentence-transformers (forced)", extra=kv(model=cfg["EMBED_ST_MODEL"], device=cfg["ST_DEVICE"]))
            return LocalSTEmbedding(cfg["EMBED_ST_MODEL"], device=cfg["ST_DEVICE"])
        # auto
        if has_wx:
            log.info("Embedding provider: watsonx (auto)", extra=kv(model=cfg["EMBED_MODEL"]))
            return WatsonxEmbedding(os.getenv("WATSONX_API_KEY"), os.getenv("WATSONX_URL"),
                                    os.getenv("WATSONX_PROJECT_ID"), cfg["EMBED_MODEL"])
        log.info("Embedding provider: sentence-transformers (auto fallback)", extra=kv(model=cfg["EMBED_ST_MODEL"], device=cfg["ST_DEVICE"]))
        return LocalSTEmbedding(cfg["EMBED_ST_MODEL"], device=cfg["ST_DEVICE"])
    except Exception:
        log.exception("Failed to init embedder")
        raise

# ---------- DB helpers ----------

def _make_sqlalchemy_url(cfg)->str:
    params = f"?sslmode={cfg['PG_SSLMODE']}"
    if cfg["PG_SSLROOTCERT"]:
        params += f"&sslrootcert={cfg['PG_SSLROOTCERT']}"
    return f"postgresql+psycopg2://{cfg['PG_USER']}:{cfg['PG_PASSWORD']}@{cfg['PG_HOST']}:{cfg['PG_PORT']}/{cfg['PG_DATABASE']}{params}"

def connect_psycopg(cfg):
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
    log.debug("Connecting to Postgres", extra=kv(dsn_redacted=f"host={cfg['PG_HOST']} port={cfg['PG_PORT']} dbname={cfg['PG_DATABASE']} user={cfg['PG_USER']} sslmode={cfg['PG_SSLMODE']}"))
    conn = psycopg2.connect(dsn)
    if HAS_PGVECTOR:
        register_vector(conn)
    return conn

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

def get_existing_vector_dim(conn, cfg):
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

def ensure_parent_table(conn, cfg, vector_dim:int):
    log.info("Ensuring parent table", extra=kv(schema=cfg["PG_SCHEMA"], table=cfg["TABLE_NAME"], vector_dim=vector_dim))
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
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
            sql.SQL(str(vector_dim)),
            sql.Identifier('schema_embeddings_pk')  # fixed name
        ))
        cur.execute(sql.SQL('CREATE INDEX IF NOT EXISTS {} ON {}.{} (table_name);').format(
            sql.Identifier(f'{cfg["TABLE_NAME"]}_tblname_idx'),
            sql.Identifier(cfg["PG_SCHEMA"]),
            sql.Identifier(cfg["TABLE_NAME"])
        ))
    conn.commit()

def ensure_parent_vector_dim(conn, cfg, desired_dim:int):
    existing_dim = get_existing_vector_dim(conn, cfg)
    if existing_dim is None:
        log.info("Altering vector dimension on empty table", extra=kv(desired_dim=desired_dim))
        with conn.cursor() as cur:
            cur.execute(sql.SQL('ALTER TABLE {}.{} ALTER COLUMN embedding TYPE vector({});').format(
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(cfg["TABLE_NAME"]),
                sql.SQL(str(desired_dim))
            ))
        conn.commit()
        return desired_dim
    if existing_dim != desired_dim:
        log.error("Vector dimension mismatch", extra=kv(existing_dim=existing_dim, desired_dim=desired_dim))
        raise RuntimeError(
            f"Vector dimension mismatch: existing={existing_dim}, new={desired_dim}. "
            "Table has data, cannot auto-migrate. Recreate table or re-embed."
        )
    return existing_dim

def _sanitize_identifier(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]+', '_', s)

def _partition_exists(conn, cfg, part_name: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = %s AND c.relname = %s
        """, (cfg["PG_SCHEMA"], part_name))
        return cur.fetchone() is not None

def ensure_partition_for_schema(conn, cfg, schema_name:str):
    """
    Safe, idempotent creation of:
      - partition table for the given schema_name
      - IVFFLAT index on (embedding) with configurable lists
    Uses psycopg2.sql to avoid DO-block placeholder issues.
    """
    part_name = f'{cfg["TABLE_NAME"]}_p_{_sanitize_identifier(schema_name)}'
    idx_name = f'{part_name}_emb_ivfflat_idx'
    t0 = time.time()
    with conn.cursor() as cur:
        # Create partition if missing
        if not _partition_exists(conn, cfg, part_name):
            cur.execute(sql.SQL(
                "CREATE TABLE {}.{} PARTITION OF {}.{} FOR VALUES IN ({});"
            ).format(
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(part_name),
                sql.Identifier(cfg["PG_SCHEMA"]),
                sql.Identifier(cfg["TABLE_NAME"]),
                sql.Literal(schema_name)
            ))
            log.info("Created partition", extra=kv(schema_name=schema_name, partition=part_name))

        # Create IVFFLAT index (idempotent)
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
    log.debug("Ensured partition/index", extra=kv(schema_name=schema_name, partition=part_name, idx=idx_name, lists=cfg["LISTS"], elapsed_ms=dt))

# ---------- Ingestion logic ----------

def mask_value(v):
    return "[MASKED]" if v is not None else None

def fetch_sample_rows_sqlalchemy(engine, schema, table, limit:int):
    q = f'SELECT * FROM "{schema}"."{table}" LIMIT {limit}'
    try:
        with engine.connect() as conn:
            res = conn.execute(text(q))
            rows = [dict(r._mapping) for r in res.fetchall()]
            if rows:
                log.debug("Fetched sample rows", extra=kv(schema=schema, table=table, rows=len(rows)))
            return rows
    except Exception:
        log.exception("Sample rows fetch failed", extra=kv(schema=schema, table=table))
        return []

def build_text(schema, table, columns, sample_rows, comment=None):
    cols = ', '.join([f"{c['name']}({c.get('type')})" for c in columns])
    sample_text = ' | '.join([safe_json_dumps(r) for r in sample_rows])
    parts = [f"Table: {table}", f"Schema: {schema}", f"Columns: {cols}"]
    if comment:
        parts.append(f"Comment: {comment}")
    if sample_text:
        parts.append(f"Samples: {sample_text}")
    combined = '\n'.join(parts)
    max_len = 4000
    model_name = os.getenv("EMBED_MODEL", "").lower()
    if "slate" in model_name:
        max_len = 1000
    if len(combined) > max_len:
        combined = combined[:max_len]
    return combined

def collect_schema_docs(engine, cfg, schemas_include):
    inspector = inspect(engine)
    t0 = time.time()
    docs = []
    schemas = inspector.get_schema_names()
    total_tables = 0
    enricher = MetadataEnricher.from_env(cfg)
    for schema in schemas:
        if schema in ('pg_catalog', 'information_schema'):
            continue
        if schemas_include and schema not in schemas_include:
            continue
        tables = inspector.get_table_names(schema=schema)
        for table in tables:
            # Skip the schema_embeddings parent table and its partitions
            target_table_name = cfg.get("TABLE_NAME", "schema_embeddings")
            target_schema_name = cfg.get("PG_SCHEMA", "public")
            if schema == target_schema_name and (table == target_table_name or table.startswith(target_table_name + "_p_")):
                log.debug("Skipping introspection of the schema embeddings table or partition", extra=kv(schema=schema, table=table))
                continue
            total_tables += 1
            cols_meta = []
            for col in inspector.get_columns(table, schema=schema):
                col_name = col['name']
                col_type = str(col.get('type'))
                col_desc = col.get('comment')
                pii = any(pat in (col_name or '').lower() for pat in cfg["PII_PATTERNS"])
                cols_meta.append({'name': col_name, 'type': col_type, 'description': col_desc, 'is_pii': pii})
            pk = inspector.get_pk_constraint(table, schema=schema).get('constrained_columns', []) or []
            fk = []
            for fk_info in inspector.get_foreign_keys(table, schema=schema):
                fk.append({
                    'from_column': (fk_info.get('constrained_columns') or [None])[0],
                    'to_table': fk_info.get('referred_table'),
                    'to_column': (fk_info.get('referred_columns') or [None])[0]
                })
            sample_rows = fetch_sample_rows_sqlalchemy(engine, schema, table, cfg["SAMPLE_ROW_LIMIT"])
            for r in sample_rows:
                for c in list(r.keys()):
                    if any(pat in c.lower() for pat in cfg["PII_PATTERNS"]):
                        r[c] = mask_value(r[c])

            # Apply external metadata enrichment
            table_comment, nat_hint, cols_meta = enricher.enrich_schema_dict(
                schema_name=schema,
                table_name=table,
                columns=cols_meta,
                table_comment=None,
                natural_language_hint=None,
            )
            comment_to_use = nat_hint or table_comment
            text_blob = build_text(schema, table, cols_meta, sample_rows, comment=comment_to_use)
            docs.append((schema, table, safe_json_dumps(cols_meta), safe_json_dumps(pk), safe_json_dumps(fk), safe_json_dumps(sample_rows), text_blob))
    dt = round((time.time() - t0) * 1000, 1)
    log.info("Collected schema docs", extra=kv(schemas=len([s for s in schemas if s not in ('pg_catalog','information_schema')]), tables=total_tables, docs=len(docs), elapsed_ms=dt))
    return docs

def bulk_insert(conn, cfg, rows_with_vectors):
    t0 = time.time()
    sql_stmt = f"""
    INSERT INTO {cfg["PG_SCHEMA"]}."{cfg["TABLE_NAME"]}"
        (schema_name, table_name, columns_json, pk_json, fk_json, sample_rows_json, text_agg, embedding)
    VALUES %s
    ON CONFLICT (schema_name, table_name) DO UPDATE SET
      columns_json = EXCLUDED.columns_json,
      pk_json = EXCLUDED.pk_json,
      fk_json = EXCLUDED.fk_json,
      sample_rows_json = EXCLUDED.sample_rows_json,
      text_agg = EXCLUDED.text_agg,
      embedding = EXCLUDED.embedding
    """
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql_stmt, rows_with_vectors, template=None)
            conn.commit()
        dt = round((time.time() - t0) * 1000, 1)
        log.info("Upserted batch", extra=kv(rows=len(rows_with_vectors), elapsed_ms=dt))
    except Exception:
        log.exception("Bulk insert failed", extra=kv(rows=len(rows_with_vectors)))
        raise

def ingest_all(cfg, batch_size:int=128):
    start = time.time()
    log.info("Ingestion started", extra=kv(batch_size=batch_size, schemas_filter=cfg['SCHEMAS_INCLUDE']))
    engine = create_engine(_make_sqlalchemy_url(cfg), pool_pre_ping=True)

    docs = collect_schema_docs(engine, cfg, cfg["SCHEMAS_INCLUDE"])
    if not docs:
        log.warning("No tables discovered to ingest.")
        return

    embedder = get_embedder(cfg)

    conn = connect_psycopg(cfg)
    try:
        first_text = docs[0][-1]
        first_vec = embedder.embed([first_text])[0]
        vec_dim = len(first_vec)
        desired_dim = cfg["VECTOR_DIM"] or vec_dim
        log.info("Embedding dimension decided", extra=kv(vec_dim=vec_dim, desired_dim=desired_dim, default_dim_env=cfg["VECTOR_DIM"]))

        if not table_exists(conn, cfg):
            ensure_parent_table(conn, cfg, desired_dim)
        else:
            ensure_parent_vector_dim(conn, cfg, desired_dim)

        rows_with_vectors = []
        total_upserted = 0
        for i in range(0, len(docs), batch_size):
            chunk = docs[i:i+batch_size]
            texts = [d[-1] for d in chunk]
            t0 = time.time()
            try:
                vectors = embedder.embed(texts)
            except Exception:
                log.exception("Embedding batch failed", extra=kv(batch_start=i, batch_size=len(texts)))
                raise
            embed_ms = round((time.time() - t0) * 1000, 1)

            schemas_in_chunk = sorted(set(d[0] for d in chunk))
            for sch in schemas_in_chunk:
                try:
                    ensure_partition_for_schema(conn, cfg, sch)
                except Exception:
                    log.exception("Ensure partition/index failed", extra=kv(schema_name=sch))
                    raise

            for (schema, table, cols_json, pk_json, fk_json, sample_rows_json, text_agg), vec in zip(chunk, vectors):
                rows_with_vectors.append((schema, table, cols_json, pk_json, fk_json, sample_rows_json, text_agg, vec))

            try:
                bulk_insert(conn, cfg, rows_with_vectors)
                total_upserted += len(rows_with_vectors)
                rows_with_vectors = []
            except Exception:
                raise

            log.info("Batch complete", extra=kv(batch_start=i, batch_size=len(chunk), schemas_in_batch=schemas_in_chunk, embed_elapsed_ms=embed_ms, total_upserted_so_far=total_upserted))

        log.info("Ingestion done", extra=kv(total_tables=len(docs), total_upserted=total_upserted, elapsed_s=round(time.time()-start, 2)))

    except Exception:
        log.exception("Ingestion failed")
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass

# ---------- Main ----------

if __name__ == '__main__':
    try:
        initialize_and_validate_env()
        cfg = load_config()
        ingest_all(cfg, batch_size=128)
    except SystemExit as se:
        if int(getattr(se, "code", 1)) != 0:
            log.error("Startup/validation failed; exiting", extra=kv(exit_code=int(getattr(se,"code",1))))
        raise
    except Exception:
        log.exception("Process terminated with error (fatal)")
        sys.exit(1)
