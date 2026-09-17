"""
ingest_opensearch.py

Multi-source schema ingestion pipeline for Text2SQL.

Workflow
--------
1. Connect to one or more source databases (PostgreSQL, Db2, …) IN PARALLEL.
2. Walk every schema/table → build a fully-enriched SchemaDoc per table.
3. Embed the text blob (watsonx Granite or sentence-transformers) with
   automatic exponential back-off on transient 429/503 errors.
4. Pre-flight dimension check against existing index — prevents silent crashes.
5. Upsert each document into an OpenSearch cosinesimil k-NN index.

Enrichment in index documents
------------------------------
Each document now stores all enrichment fields added to SchemaDoc:
  indexes_json        — non-PK indexes with columns and UNIQUE flag
  referenced_by_json  — reverse FK list ("other_table.col → this table")
  row_count_approx    — approximate row count from pg_stat / SYSCAT
  column_names        — flat list of column names (text field for BM25)
  unique_columns      — flat list of columns with UNIQUE constraint
  enum_values_json    — per-column distinct value lists

Optimizations over the previous version
-----------------------------------------
• Fix 2  — exponential back-off with jitter on watsonx 429/503
• Fix 3  — static _MODEL_DIMS lookup; no probe-embed round-trip
• Fix 4  — texts computed once, passed into bulk_upsert (no double render)
• Fix 8  — parallel source collection via ThreadPoolExecutor
• Fix 9  — pre-flight index dimension check before any embedding
• Enrichment — richer OpenSearch documents (indexes, reverse FKs, row counts, enums)

Run examples
------------
  # PostgreSQL only, sentence-transformers
  EMBED_PROVIDER=st SOURCE_TYPES=postgresql python ingest_opensearch.py

  # PostgreSQL + Db2, watsonx embeddings
  SOURCE_TYPES=postgresql,db2 \\
  EMBED_PROVIDER=watsonx \\
  WATSONX_API_KEY=... WATSONX_URL=... WATSONX_PROJECT_ID=... \\
  python ingest_opensearch.py
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

# ---- .env early load ----
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

# ---- logging ----
RUN_ID    = os.getenv("RUN_ID") or str(uuid.uuid4())
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class _Fmt(logging.Formatter):
    _std = None

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        if self._std is None:
            type(self)._std = set(
                vars(logging.LogRecord("", 0, "", 0, "", (), None)).keys()
            )
        base = (
            f"{self.formatTime(record, '%Y-%m-%d %H:%M:%S')} "
            f"[{record.levelname}] "
            f"{record.filename}:{record.lineno} {record.funcName}() "
            f"run={RUN_ID} — {record.getMessage()}"
        )
        extras = [
            f"{k}={repr(v)}"
            for k, v in vars(record).items()
            if k not in self._std and k != "message"
        ]
        if extras:
            base += " | " + ", ".join(extras)
        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)
        return base


def _setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    level  = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_Fmt())
    logger.handlers  = [handler]
    logger.propagate = False
    return logger


log = _setup_logger("ingest")


def _excepthook(exctype: type, value: BaseException, tb: Any) -> None:
    try:
        log.exception(
            "Uncaught exception (global)",
            extra={"exctype": exctype.__name__},
        )
    finally:
        sys.__excepthook__(exctype, value, tb)


sys.excepthook = _excepthook

# ---- third-party ----
from opensearchpy import OpenSearch, helpers as os_helpers
from opensearchpy.exceptions import RequestError

from connectors.base import SchemaDoc
from connectors.postgresql import PostgreSQLConnector
from connectors.db2 import Db2Connector, db2_connector_from_env
# A5 — get_model_dim is now the canonical implementation in embedders.py
from embedders import EmbeddingProvider, build_embedder, get_model_dim
from metadata_enricher import MetadataEnricher


# ==========================================================================
# Dimension resolver — thin wrapper kept for backward compatibility
# ==========================================================================

def _resolve_dim(cfg: Dict[str, str]) -> int:
    """
    Return embedding dimension honoring explicit VECTOR_DIM or static table fallback.

    A5 — delegates to ``get_model_dim()`` in embedders.py, which is the
    single authoritative source of the model→dimension mapping.
    """
    return get_model_dim(cfg)


# ==========================================================================
# JSON helper
# ==========================================================================

def _default(o: Any) -> Any:
    if isinstance(o, (datetime, date)):
        return o.isoformat()
    if isinstance(o, Decimal):
        return float(o)
    if isinstance(o, uuid.UUID):
        return str(o)
    if isinstance(o, (set, tuple)):
        return list(o)
    if isinstance(o, bytes):
        return o.decode("utf-8", "ignore")
    return str(o)


def safe_json(obj: Any) -> str:
    return json.dumps(obj, default=_default, ensure_ascii=False)


# ==========================================================================
# OpenSearch helpers
# ==========================================================================

def build_os_client(cfg: Dict[str, str]) -> OpenSearch:
    use_ssl   = cfg.get("OS_USE_SSL", "true").lower() in ("1", "true", "yes")
    verify    = cfg.get("OS_VERIFY_CERTS", "true").lower() in ("1", "true", "yes")
    http_auth = None
    if cfg.get("OS_USER") and cfg.get("OS_PASSWORD"):
        http_auth = (cfg["OS_USER"], cfg["OS_PASSWORD"])

    client = OpenSearch(
        hosts=[{"host": cfg["OS_HOST"], "port": int(cfg.get("OS_PORT", "443"))}],
        http_auth    = http_auth,
        use_ssl      = use_ssl,
        verify_certs = verify,
        ssl_assert_hostname = verify,
        ssl_show_warn = False,
        timeout       = 30,
    )
    log.debug(
        "OpenSearch client ready",
        extra={"host": cfg["OS_HOST"], "port": cfg.get("OS_PORT", "443"), "ssl": use_ssl},
    )
    return client


def _check_index_dim(client: OpenSearch, index: str, expected_dim: int) -> None:
    """
    Fix 9 — Pre-flight check: if the index already exists, verify its
    knn_vector dimension matches the model we're about to use.
    A mismatch would silently crash inside bulk_upsert; catch it early.
    """
    if not client.indices.exists(index=index):
        return  # will be created fresh — nothing to check

    try:
        mapping  = client.indices.get_mapping(index=index)
        actual   = (
            mapping.get(index, {})
            .get("mappings", {})
            .get("properties", {})
            .get("embedding", {})
            .get("dimension")
        )
        if actual is not None and int(actual) != expected_dim:
            raise SystemExit(
                f"\n[DIMENSION MISMATCH]\n"
                f"  Index '{index}' was created with dimension {actual}.\n"
                f"  Current model produces dimension {expected_dim}.\n"
                f"  Action required: drop the index and re-run ingest, "
                f"or set EMBED_MODEL/EMBED_ST_MODEL to match the existing index.\n"
                f"  To drop:  DELETE /{index}  (OpenSearch REST API)\n"
            )
        log.info(
            "Pre-flight dim check passed",
            extra={"index": index, "dim": expected_dim},
        )
    except SystemExit:
        raise
    except Exception:
        log.debug("Could not verify existing index dimension", exc_info=True)


def ensure_index(client: OpenSearch, index: str, vector_dim: int) -> None:
    """
    Create the k-NN index if it doesn't already exist.
    Uses cosinesimil (matches normalize_embeddings=True in LocalSTEmbedding).
    Also creates enrichment fields for indexes, reverse FKs, row counts, etc.
    """
    if client.indices.exists(index=index):
        log.info("OpenSearch index already exists", extra={"index": index})
        return

    mapping = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 512,
                "number_of_shards":   int(os.getenv("OS_SHARDS", "1")),
                "number_of_replicas": int(os.getenv("OS_REPLICAS", "1")),
            }
        },
        "mappings": {
            "properties": {
                # ---- identity ----
                "table_id":          {"type": "keyword"},
                "source_type":       {"type": "keyword"},
                "db_alias":          {"type": "keyword"},
                "schema_name":       {"type": "keyword"},
                "table_name": {
                    "type":   "keyword",
                    "fields": {"text": {"type": "text", "analyzer": "english"}},
                },
                # ---- schema metadata ----
                "table_comment":     {"type": "text", "analyzer": "english"},
                "columns_json":      {"type": "object", "enabled": False},
                "pk_json":           {"type": "keyword"},
                "fk_json":           {"type": "object", "enabled": False},
                "sample_rows_json":  {"type": "object", "enabled": False},
                # ---- enrichment fields ----
                "indexes_json":      {"type": "object", "enabled": False},
                "referenced_by_json":{"type": "object", "enabled": False},
                "row_count_approx":  {"type": "long"},
                "column_count":      {"type": "integer"},
                # searchable flat lists for BM25 boost
                "column_names": {
                    "type":     "text",
                    "analyzer": "english",
                    "fields":   {"keyword": {"type": "keyword", "ignore_above": 256}},
                },
                "unique_columns":    {"type": "keyword"},
                "enum_values_json":  {"type": "object", "enabled": False},
                # ---- embedding text (BM25 search target) ----
                "text_agg": {
                    "type":     "text",
                    "analyzer": "english",
                    "fields":   {"keyword": {"type": "keyword", "ignore_above": 512}},
                },
                # ---- vector ----
                "embedding": {
                    "type":      "knn_vector",
                    "dimension": vector_dim,
                    "method": {
                        "name":       "hnsw",
                        "engine":     "nmslib",
                        "space_type": "cosinesimil",
                        "parameters": {"ef_construction": 512, "m": 16},
                    },
                },
            }
        },
    }
    try:
        client.indices.create(index=index, body=mapping)
        log.info(
            "Created OpenSearch index",
            extra={"index": index, "vector_dim": vector_dim},
        )
    except RequestError as exc:
        if "resource_already_exists_exception" in str(exc).lower():
            log.info("Index already exists (race condition, safe to ignore)",
                     extra={"index": index})
        else:
            raise


def delete_stale_documents(
    client: OpenSearch,
    index: str,
    current_table_ids: List[str],
) -> int:
    """
    Delete any documents in *index* whose table_id is NOT in current_table_ids.

    This prevents phantom tables (dropped or renamed in the source DB) from
    remaining in the index and causing the LLM to generate SQL against objects
    that no longer exist.

    Uses a scroll-based scan to enumerate all existing IDs, then issues a
    bulk delete for any not seen in the current ingestion run.

    Returns the number of documents deleted.
    """
    current_ids: set = set(current_table_ids)
    stale_ids: List[str] = []

    # Scroll through all documents in the index, fetching only _id + table_id
    try:
        resp = client.search(
            index=index,
            body={
                "size": 1000,
                "_source": ["table_id"],
                "query": {"match_all": {}},
            },
            scroll="2m",
        )
    except Exception:
        log.warning("Could not enumerate index for stale-doc cleanup", exc_info=True)
        return 0

    scroll_id = resp.get("_scroll_id")
    try:
        while True:
            hits = resp.get("hits", {}).get("hits", [])
            if not hits:
                break
            for hit in hits:
                doc_id  = hit.get("_id", "")
                tbl_id  = (hit.get("_source") or {}).get("table_id", doc_id)
                if tbl_id not in current_ids:
                    stale_ids.append(doc_id)
            if not scroll_id:
                break
            resp = client.scroll(scroll_id=scroll_id, scroll="2m")
            scroll_id = resp.get("_scroll_id")
    except Exception:
        log.warning("Scroll iteration failed during stale-doc cleanup", exc_info=True)
    finally:
        if scroll_id:
            try:
                client.clear_scroll(scroll_id=scroll_id)
            except Exception:
                pass

    if not stale_ids:
        log.info("Stale-doc check: no stale documents found")
        return 0

    # Bulk delete stale documents
    delete_actions = [
        {"_op_type": "delete", "_index": index, "_id": doc_id}
        for doc_id in stale_ids
    ]
    ok, errors = os_helpers.bulk(client, delete_actions, raise_on_error=False)
    if errors:
        log.error(
            "Stale-doc bulk delete had errors",
            extra={"deleted_ok": ok, "errors": len(errors)},
        )
    else:
        log.info(
            "Stale documents removed",
            extra={"count": len(stale_ids)},
        )
    return len(stale_ids)


def bulk_upsert(
    client:  OpenSearch,
    index:   str,
    docs:    List[SchemaDoc],
    vectors: List[List[float]],
    texts:   List[str],          # Fix 4 — pre-computed texts passed in; no second render
) -> None:
    """Bulk-upsert documents into OpenSearch using helpers.bulk."""
    actions = []
    for doc, vec, text_agg in zip(docs, vectors, texts):
        # ---- flat column name list for BM25 ----
        col_names    = [c.name for c in doc.columns]
        unique_cols  = [c.name for c in doc.columns if c.is_unique]
        enum_map     = {c.name: c.enum_values for c in doc.columns if c.enum_values}

        actions.append({
            "_op_type": "index",
            "_index":   index,
            "_id":      doc.table_id,
            "_source": {
                # identity
                "table_id":    doc.table_id,
                "source_type": doc.source_type,
                "db_alias":    doc.db_alias,
                "schema_name": doc.schema_name,
                "table_name":  doc.table_name,
                # schema metadata
                "table_comment":    doc.table_comment or "",
                # A3 — use to_dict() so is_pii is never stored in the index
                "columns_json":     [c.to_dict() for c in doc.columns],
                "pk_json":          doc.primary_keys,
                "fk_json":          [vars(fk) for fk in doc.foreign_keys],
                "sample_rows_json": doc.sample_rows,
                # enrichment
                "indexes_json":       [vars(idx) for idx in doc.indexes],
                "referenced_by_json": doc.referenced_by,
                "row_count_approx":   doc.row_count_approx,
                "column_count":       doc.column_count,
                "column_names":       " ".join(col_names),  # space-sep for text analysis
                "unique_columns":     unique_cols,
                "enum_values_json":   enum_map,
                # embedding text (Fix 4 — reuse pre-computed text)
                "text_agg":   text_agg,
                "embedding":  vec,
            },
        })

    t0 = time.time()
    ok, errors = os_helpers.bulk(client, actions, raise_on_error=False)
    elapsed = round((time.time() - t0) * 1000, 1)

    if errors:
        log.error(
            "Bulk upsert had errors",
            extra={"ok": ok, "errors": len(errors), "first_error": str(errors[0])[:300]},
        )
    else:
        log.info(
            "Bulk upsert complete",
            extra={"indexed": ok, "elapsed_ms": elapsed},
        )


# ==========================================================================
# Config & env validation
# ==========================================================================

def load_config() -> Dict[str, str]:
    cfg: Dict[str, str] = {}

    # OpenSearch
    cfg["OS_HOST"]         = os.getenv("OS_HOST", "localhost")
    cfg["OS_PORT"]         = os.getenv("OS_PORT", "443")
    cfg["OS_USER"]         = os.getenv("OS_USER", "")
    cfg["OS_PASSWORD"]     = os.getenv("OS_PASSWORD", "")
    cfg["OS_USE_SSL"]      = os.getenv("OS_USE_SSL", "true")
    cfg["OS_VERIFY_CERTS"] = os.getenv("OS_VERIFY_CERTS", "true")
    cfg["OS_INDEX"]        = os.getenv("OS_INDEX", "schema_embeddings")

    # Embedding
    cfg["EMBED_PROVIDER"]     = os.getenv("EMBED_PROVIDER", "auto").lower()
    cfg["EMBED_MODEL"]        = os.getenv("EMBED_MODEL", "ibm-granite/granite-embedding-125m-english")
    cfg["EMBED_ST_MODEL"]     = os.getenv("EMBED_ST_MODEL", "BAAI/bge-base-en-v1.5")
    cfg["ST_DEVICE"]          = os.getenv("ST_DEVICE", "cpu")
    cfg["WATSONX_API_KEY"]    = os.getenv("WATSONX_API_KEY", "")
    cfg["WATSONX_URL"]        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
    cfg["WATSONX_PROJECT_ID"] = os.getenv("WATSONX_PROJECT_ID", "")

    # Ingestion behaviour
    cfg["SOURCE_TYPES"]       = os.getenv("SOURCE_TYPES", "postgresql")
    cfg["SCHEMAS_INCLUDE"]    = os.getenv("SCHEMAS_INCLUDE", "")
    cfg["SAMPLE_ROW_LIMIT"]   = os.getenv("SAMPLE_ROW_LIMIT", "3")
    cfg["ENUM_ROW_LIMIT"]     = os.getenv("ENUM_ROW_LIMIT", "20")
    cfg["PII_PATTERNS"]       = os.getenv("PII_PATTERNS", "ssn,email,phone,card")
    cfg["BATCH_SIZE"]         = os.getenv("BATCH_SIZE", "64")
    cfg["VECTOR_DIM"]         = os.getenv("VECTOR_DIM", "")  # override if model not in _MODEL_DIMS
    # Metadata enrichment
    cfg["METADATA_ENRICHMENT_ENABLED"] = os.getenv("METADATA_ENRICHMENT_ENABLED", "true")
    cfg["METADATA_ENRICHMENT_FILE"]    = os.getenv("METADATA_ENRICHMENT_FILE", os.getenv("SCHEMA_METADATA_FILE", ""))
    # Masking flags
    cfg["PII_MASK_COLUMNS"]   = os.getenv("PII_MASK_COLUMNS", "true")   # column-name pass
    cfg["PII_MASK_VALUES"]    = os.getenv("PII_MASK_VALUES",  "true")   # regex value pass

    # PostgreSQL source (optional)
    for key in ["PG_HOST", "PG_PORT", "PG_DATABASE", "PG_USER", "PG_PASSWORD",
                "PG_SSLMODE", "PG_SSLROOTCERT", "PG_SCHEMA"]:
        cfg[key] = os.getenv(key, "")

    # Db2 source (optional)
    for key in ["DB2_HOST", "DB2_PORT", "DB2_DATABASE", "DB2_USER", "DB2_PASSWORD",
                "DB2_SSL", "DB2_SSLCERT", "DB2_DRIVER", "DB2_JDBC_JAR"]:
        cfg[key] = os.getenv(key, "")

    return cfg


def validate_config(cfg: Dict[str, str]) -> None:
    missing = []
    if not cfg.get("OS_HOST"):
        missing.append("OS_HOST")

    provider = cfg["EMBED_PROVIDER"]
    has_wx   = bool(cfg.get("WATSONX_API_KEY") and cfg.get("WATSONX_URL") and cfg.get("WATSONX_PROJECT_ID"))

    if provider == "watsonx":
        for k in ["WATSONX_API_KEY", "WATSONX_URL", "WATSONX_PROJECT_ID", "EMBED_MODEL"]:
            if not cfg.get(k):
                missing.append(k)
    elif provider == "st":
        if not cfg.get("EMBED_ST_MODEL"):
            missing.append("EMBED_ST_MODEL")
    else:  # auto
        if not has_wx and not cfg.get("EMBED_ST_MODEL"):
            missing.append("EMBED_ST_MODEL (or WATSONX_* vars for watsonx auto)")

    sources = [s.strip() for s in cfg.get("SOURCE_TYPES", "").split(",") if s.strip()]
    if not sources:
        missing.append("SOURCE_TYPES (at least one of: postgresql, db2)")

    if "postgresql" in sources:
        for k in ["PG_HOST", "PG_DATABASE", "PG_USER", "PG_PASSWORD"]:
            if not cfg.get(k):
                missing.append(f"{k} (required for postgresql source)")

    if "db2" in sources:
        for k in ["DB2_HOST", "DB2_DATABASE", "DB2_USER", "DB2_PASSWORD"]:
            if not cfg.get(k):
                missing.append(f"{k} (required for db2 source)")

    if missing:
        log.error("Missing required config / env vars", extra={"missing": missing})
        sys.exit(2)


# ==========================================================================
# Source connector factory
# ==========================================================================

def build_connectors(cfg: Dict[str, str]) -> List[Any]:
    sources = [s.strip() for s in cfg["SOURCE_TYPES"].split(",") if s.strip()]
    result  = []
    for src in sources:
        if src == "postgresql":
            pg_cfg = {
                "PG_HOST":        cfg["PG_HOST"],
                "PG_PORT":        cfg.get("PG_PORT") or "5432",
                "PG_DATABASE":    cfg["PG_DATABASE"],
                "PG_USER":        cfg["PG_USER"],
                "PG_PASSWORD":    cfg["PG_PASSWORD"],
                "PG_SSLMODE":     cfg.get("PG_SSLMODE") or "require",
                "PG_SSLROOTCERT": cfg.get("PG_SSLROOTCERT") or "",
                "DB_ALIAS":       os.getenv("PG_ALIAS") or os.getenv("DB_ALIAS") or cfg.get("PG_DATABASE"),
            }
            result.append(PostgreSQLConnector(pg_cfg))
            log.info("Source registered: postgresql", extra={"host": cfg["PG_HOST"]})

        elif src == "db2":
            db2_cfg = {
                "DB2_HOST":     cfg["DB2_HOST"],
                "DB2_PORT":     cfg.get("DB2_PORT") or "50000",
                "DB2_DATABASE": cfg["DB2_DATABASE"],
                "DB2_USER":     cfg["DB2_USER"],
                "DB2_PASSWORD": cfg["DB2_PASSWORD"],
                "DB2_SSL":      cfg.get("DB2_SSL") or "false",
                "DB2_SSLCERT":  cfg.get("DB2_SSLCERT") or "",
                "DB2_DRIVER":   cfg.get("DB2_DRIVER") or "auto",
                "DB2_JDBC_JAR": cfg.get("DB2_JDBC_JAR") or "",
                "DB_ALIAS":     os.getenv("DB2_ALIAS") or os.getenv("DB_ALIAS") or cfg.get("DB2_DATABASE"),
            }
            result.append(Db2Connector(db2_cfg))
            log.info("Source registered: db2", extra={"host": cfg["DB2_HOST"]})

        else:
            log.warning("Unknown source type — skipping", extra={"source": src})

    return result


# ==========================================================================
# Main ingestion loop
# ==========================================================================

def _collect_source(
    connector: Any,
    inc:         Optional[List[str]],
    limit:       int,
    pii:         List[str],
    enum_limit:  int,
    mask_values: bool,
) -> List[SchemaDoc]:
    """Worker function — runs in its own thread for parallel collection."""
    return connector.collect(
        schemas_include  = inc,
        sample_row_limit = limit,
        pii_patterns     = pii,
        enum_row_limit   = enum_limit,
        mask_values      = mask_values,
    )


def ingest(cfg: Dict[str, str], batch_size: int = 64) -> None:
    start      = time.time()
    # Column-name masking: disabled by setting PII_MASK_COLUMNS=false
    # (pass empty list to collector so column-name check is skipped)
    mask_cols  = cfg.get("PII_MASK_COLUMNS", "true").lower() in ("1", "true", "yes")
    pii        = [p.strip() for p in cfg["PII_PATTERNS"].split(",") if p.strip()] if mask_cols else []
    # Regex value masking: disabled by setting PII_MASK_VALUES=false
    mask_values = cfg.get("PII_MASK_VALUES", "true").lower() in ("1", "true", "yes")
    limit      = int(cfg["SAMPLE_ROW_LIMIT"])
    enum_limit = int(cfg["ENUM_ROW_LIMIT"])
    inc        = [s.strip() for s in cfg["SCHEMAS_INCLUDE"].split(",") if s.strip()] or None

    log.info(
        "Ingestion started",
        extra={"sources": cfg["SOURCE_TYPES"], "batch_size": batch_size,
               "schemas_filter": inc, "enum_limit": enum_limit,
               "mask_columns": mask_cols, "mask_values": mask_values},
    )

    # 1. Collect schema docs from all sources IN PARALLEL (Fix 8)
    connectors = build_connectors(cfg)
    if not connectors:
        log.error("No valid connectors built from SOURCE_TYPES", extra={"sources": cfg["SOURCE_TYPES"]})
        sys.exit(2)
    all_docs: List[SchemaDoc] = []

    with ThreadPoolExecutor(max_workers=len(connectors)) as pool:
        futures = {
            pool.submit(_collect_source, c, inc, limit, pii, enum_limit, mask_values): c
            for c in connectors
        }
        for fut in as_completed(futures):
            connector = futures[fut]
            try:
                docs = fut.result()
                all_docs.extend(docs)
                log.info(
                    "Collected from source",
                    extra={"source": type(connector).__name__, "docs": len(docs)},
                )
            except Exception:
                log.exception(
                    "Source collection failed",
                    extra={"source": type(connector).__name__},
                )

    if not all_docs:
        log.warning("No tables discovered across all sources. Nothing to ingest.")
        return

    # 1b. Apply external metadata enrichment if enabled
    enricher = MetadataEnricher.from_env(cfg)
    if enricher.enabled and enricher.enrichments:
        enriched_count = 0
        for doc in all_docs:
            before_comment = doc.table_comment
            before_hint = doc.natural_language_hint
            enricher.enrich_schema_doc(doc)
            if doc.table_comment != before_comment or doc.natural_language_hint != before_hint:
                enriched_count += 1
        log.info(
            "Applied external metadata enrichment",
            extra={"enriched_tables": enriched_count, "total_tables": len(all_docs)},
        )

    # 2. Resolve embedding dimension from static table (Fix 3 — no probe call)
    vec_dim = _resolve_dim(cfg)
    log.info("Embedding dimension resolved", extra={"dim": vec_dim})

    # 3. Build OpenSearch client + pre-flight dimension check (Fix 9)
    os_client = build_os_client(cfg)
    _check_index_dim(os_client, cfg["OS_INDEX"], vec_dim)
    ensure_index(os_client, cfg["OS_INDEX"], vec_dim)

    # 4. Build embedder
    embedder = build_embedder(cfg)

    # 5. Batch embed + upsert
    total = 0
    for i in range(0, len(all_docs), batch_size):
        chunk = all_docs[i: i + batch_size]

        # Fix 4 — compute texts once; pass to both embed() and bulk_upsert()
        texts   = [d.to_text() for d in chunk]
        vectors = embedder.embed(texts)

        bulk_upsert(os_client, cfg["OS_INDEX"], chunk, vectors, texts)
        total += len(chunk)
        log.info(
            "Batch complete",
            extra={"batch_start": i, "batch_size": len(chunk), "total_so_far": total},
        )

    # 6. Remove documents for tables that no longer exist in any source
    current_ids = [doc.table_id for doc in all_docs]
    delete_stale_documents(os_client, cfg["OS_INDEX"], current_ids)

    elapsed = round(time.time() - start, 2)
    log.info(
        "Ingestion done",
        extra={"total_tables": len(all_docs), "total_indexed": total, "elapsed_s": elapsed},
    )


# ==========================================================================
# Entry point
# ==========================================================================

if __name__ == "__main__":
    cfg = load_config()
    validate_config(cfg)
    ingest(cfg, batch_size=int(cfg.get("BATCH_SIZE", "64")))
