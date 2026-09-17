#!/usr/bin/env python3
"""
schema_retriever_opensearch.py

FastAPI service for Text2SQL schema retrieval backed by OpenSearch k-NN search.

Key improvements over the pgvector version
-------------------------------------------
• Backend is OpenSearch — no Postgres dependency for retrieval
• Hybrid search: k-NN vector similarity + BM25 keyword boost (optional)
• RRF endpoint: Reciprocal Rank Fusion — merge k-NN and BM25 result lists
• IAM token cached with TTL; connection pooled at module level
• `conn` unbound-variable bug fixed (connection initialised to None)
• `embedding` column no longer fetched back from the store (saves ~6 KB/result)
• Modern FastAPI lifespan context manager (replaces deprecated on_event)
• `schema_filter` AND `db_alias_filter` supported for multi-source setups
• Confidence score normalised against actual score range, not raw distance
• `sketches` use fully-quoted identifiers
• FK relationship expansion: retrieved tables are automatically expanded to
  include 1-hop FK-related tables (improves JOIN generation)
• HTTP 503 returned from /health when OpenSearch is unreachable

Endpoints
---------
  GET  /health                  – liveness + OpenSearch ping
  POST /retrieve-schema         – pure k-NN schema retrieval
  POST /retrieve-schema/hybrid  – k-NN + BM25 script_score
  POST /retrieve-schema/rrf     – Reciprocal Rank Fusion (k-NN + BM25 merged)

Environment variables
---------------------
  OS_HOST, OS_PORT, OS_USER, OS_PASSWORD
  OS_USE_SSL (default: true), OS_VERIFY_CERTS (default: true)
  OS_INDEX   (default: schema_embeddings)
  TOP_K      (default: 5)
  FK_EXPAND  (default: true) — set false to disable FK relationship expansion

  EMBED_PROVIDER  = auto | watsonx | st
  EMBED_MODEL, EMBED_ST_MODEL, ST_DEVICE
  WATSONX_API_KEY, WATSONX_URL, WATSONX_PROJECT_ID
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Set

# ---- .env early load ----
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

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, field_validator
from opensearchpy import OpenSearch

from embedders import EmbeddingProvider, build_embedder  # shared with ingest_opensearch
from reranker import BaseReranker, build_reranker


# ==========================================================================
# Logging
# ==========================================================================

RUN_ID    = os.getenv("RUN_ID") or str(uuid.uuid4())
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


class _Fmt(logging.Formatter):
    _std: Optional[set] = None

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


def _make_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    level  = getattr(logging, LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    h = logging.StreamHandler(sys.stdout)
    h.setLevel(level)
    h.setFormatter(_Fmt())
    logger.handlers = [h]
    logger.propagate = False
    return logger


log = _make_logger("schema_api")


def _excepthook(exctype: type, value: BaseException, tb: Any) -> None:
    try:
        log.exception("Uncaught exception (global)", extra={"exctype": exctype.__name__})
    finally:
        sys.__excepthook__(exctype, value, tb)


sys.excepthook = _excepthook


# ==========================================================================
# OpenSearch client builder
# ==========================================================================

def _build_os_client(cfg: Dict[str, str]) -> OpenSearch:
    use_ssl   = cfg.get("OS_USE_SSL", "true").lower() in ("1", "true", "yes")
    verify    = cfg.get("OS_VERIFY_CERTS", "true").lower() in ("1", "true", "yes")
    http_auth = (cfg["OS_USER"], cfg["OS_PASSWORD"]) if cfg.get("OS_USER") else None
    return OpenSearch(
        hosts=[{"host": cfg["OS_HOST"], "port": int(cfg.get("OS_PORT", "443"))}],
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=verify,
        ssl_assert_hostname=verify,
        ssl_show_warn=False,
        timeout=30,
    )


# ==========================================================================
# Config & validation
# ==========================================================================

def _load_cfg() -> Dict[str, str]:
    return {
        "OS_HOST":            os.getenv("OS_HOST", "localhost"),
        "OS_PORT":            os.getenv("OS_PORT", "443"),
        "OS_USER":            os.getenv("OS_USER", ""),
        "OS_PASSWORD":        os.getenv("OS_PASSWORD", ""),
        "OS_USE_SSL":         os.getenv("OS_USE_SSL", "true"),
        "OS_VERIFY_CERTS":    os.getenv("OS_VERIFY_CERTS", "true"),
        "OS_INDEX":           os.getenv("OS_INDEX", "schema_embeddings"),
        "TOP_K":              os.getenv("TOP_K", "5"),
        # A2 — separate min_score thresholds for pure k-NN and hybrid/RRF
        # Hybrid script_score can return values > 1.0, so its threshold is
        # higher than the k-NN cosine threshold (which is capped at 1.0).
        "MIN_SCORE":          os.getenv("MIN_SCORE", "0.40"),
        "MIN_SCORE_HYBRID":   os.getenv("MIN_SCORE_HYBRID", "0.55"),
        "FK_EXPAND":          os.getenv("FK_EXPAND", "true"),   # FK expansion
        "FK_EXPAND_HOPS":     os.getenv("FK_EXPAND_HOPS", "2"),  # A6 — 2-hop default
        "RERANK_ENABLED":     os.getenv("RERANK_ENABLED", "false"),
        "RERANK_PROVIDER":    os.getenv("RERANK_PROVIDER", "cross-encoder"),
        "RERANK_MODEL":       os.getenv("RERANK_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
        "RERANK_TOP_N":       os.getenv("RERANK_TOP_N", "15"),
        "RERANK_DEVICE":      os.getenv("RERANK_DEVICE", "cpu"),
        "EMBED_PROVIDER":     os.getenv("EMBED_PROVIDER", "auto").lower(),
        "EMBED_MODEL":        os.getenv("EMBED_MODEL", "ibm-granite/granite-embedding-125m-english"),
        "EMBED_ST_MODEL":     os.getenv("EMBED_ST_MODEL", "BAAI/bge-base-en-v1.5"),
        "ST_DEVICE":          os.getenv("ST_DEVICE", "cpu"),
        "WATSONX_API_KEY":    os.getenv("WATSONX_API_KEY", ""),
        "WATSONX_URL":        os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        "WATSONX_PROJECT_ID": os.getenv("WATSONX_PROJECT_ID", ""),
    }


def _validate_cfg(cfg: Dict[str, str]) -> None:
    missing = []
    if not cfg.get("OS_HOST"):
        missing.append("OS_HOST")
    provider = cfg["EMBED_PROVIDER"]
    has_wx   = bool(cfg.get("WATSONX_API_KEY") and cfg.get("WATSONX_URL") and cfg.get("WATSONX_PROJECT_ID"))
    if provider == "watsonx":
        for k in ["WATSONX_API_KEY", "WATSONX_URL", "WATSONX_PROJECT_ID", "EMBED_MODEL"]:
            if not cfg.get(k):
                missing.append(k)
    elif provider == "auto" and not has_wx:
        if not cfg.get("EMBED_ST_MODEL"):
            missing.append("EMBED_ST_MODEL")
    if missing:
        log.error("Missing required env vars", extra={"missing": missing})
        raise SystemExit(2)


# ==========================================================================
# Sketch generator  (fixes unquoted schema in original)
# ==========================================================================

def _sketches(
    schema:      str,
    table:       str,
    columns:     List[Dict[str, Any]],
    source_type: str = "postgresql",
) -> List[Dict[str, str]]:
    """
    Generate pre-built SQL snippets for the given table.
    SQL dialect is adjusted for the source database type:
      - postgresql: uses date_trunc(), LIMIT, double-quoted identifiers
      - db2: uses FETCH FIRST n ROWS ONLY, date_trunc not available
      - default: safe cross-dialect subset
    """
    table_full = f'"{schema}"."{table}"'
    col_names  = [c.get("name", "") for c in columns if isinstance(c, dict) and c.get("name")]
    date_cols  = [c for c in col_names if re.search(r"(date|time|timestamp)$", c, re.I)]

    is_pg  = source_type == "postgresql"
    is_db2 = source_type == "db2"

    # Row count — universal
    sketches = [{"id": "count_rows", "sql": f"SELECT COUNT(*) AS cnt FROM {table_full};"}]

    # Top distinct values for first column
    if col_names:
        fc = f'"{col_names[0]}"'
        if is_db2:
            sketches.append({
                "id":  "distinct_top",
                "sql": (
                    f"SELECT {fc}, COUNT(*) AS n FROM {table_full} "
                    f"GROUP BY {fc} ORDER BY n DESC FETCH FIRST 50 ROWS ONLY;"
                ),
            })
        else:
            sketches.append({
                "id":  "distinct_top",
                "sql": (
                    f"SELECT {fc}, COUNT(*) AS n FROM {table_full} "
                    f"GROUP BY 1 ORDER BY n DESC LIMIT 50;"
                ),
            })

    # Monthly time-series — PostgreSQL only (date_trunc is not standard SQL)
    if date_cols and is_pg:
        dc = f'"{date_cols[0]}"'
        sketches.append({
            "id":  "monthly_counts",
            "sql": (
                f"SELECT date_trunc('month', {dc}) AS m, COUNT(*) AS n "
                f"FROM {table_full} GROUP BY 1 ORDER BY 1;"
            ),
        })

    return sketches


# ==========================================================================
# Request / Response models
# ==========================================================================

class RetrieveRequest(BaseModel):
    user_query:      str
    schema_filter:   Optional[List[str]] = None   # filter by schema_name
    db_alias_filter: Optional[List[str]] = None   # filter by db_alias (multi-source)
    top_k:  Optional[int] = None
    hybrid: bool = False                          # enable BM25 + k-NN hybrid mode

    @field_validator("user_query")
    @classmethod
    def _nonempty_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("user_query must not be empty")
        return v.strip()


class HybridRetrieveRequest(RetrieveRequest):
    keyword_weight: float = 0.3   # weight for BM25 score component
    knn_weight:     float = 0.7


# ==========================================================================
# FastAPI app — modern lifespan pattern
# ==========================================================================

CFG:       Optional[Dict[str, str]]    = None
EMBEDDER:  Optional[EmbeddingProvider] = None
OS_CLIENT: Optional[OpenSearch]        = None
RERANKER:  Optional[BaseReranker]      = None


@asynccontextmanager
async def _lifespan(app: FastAPI):
    global CFG, EMBEDDER, OS_CLIENT, RERANKER
    try:
        CFG       = _load_cfg()
        _validate_cfg(CFG)
        EMBEDDER  = build_embedder(CFG)
        OS_CLIENT = _build_os_client(CFG)
        RERANKER  = build_reranker(CFG)
        # quick connectivity check
        info = OS_CLIENT.info()
        log.info(
            "API startup complete",
            extra={
                "os_version":  info.get("version", {}).get("number"),
                "index":       CFG["OS_INDEX"],
                "embed":       CFG["EMBED_PROVIDER"],
                "top_k":       CFG["TOP_K"],
            },
        )
    except SystemExit:
        raise
    except Exception:
        log.exception("Startup failed")
        raise
    yield
    # shutdown — nothing to tear down for stateless embedder/OS client


app = FastAPI(
    title="Schema Retriever (OpenSearch k-NN, multi-source)",
    version="2.0.0",
    lifespan=_lifespan,
)


# ==========================================================================
# Endpoints
# ==========================================================================

@app.get("/health")
def health(response: Response):
    """
    Liveness + OpenSearch ping.
    Returns HTTP 503 when OpenSearch is unreachable so that Code Engine /
    Kubernetes readiness probes correctly mark the instance unhealthy.
    """
    if OS_CLIENT is None or CFG is None:
        response.status_code = 503
        return {"ok": False, "error": "Service not initialised"}
    try:
        info = OS_CLIENT.info()
        idx_exists = OS_CLIENT.indices.exists(index=CFG["OS_INDEX"])
        return {
            "ok":           True,
            "opensearch":   info.get("version", {}).get("number", "unknown"),
            "index_exists": idx_exists,
            "embed":        CFG["EMBED_PROVIDER"],
        }
    except Exception as exc:
        log.exception("Health check failed")
        response.status_code = 503
        return {"ok": False, "error": str(exc)}


@app.post("/retrieve-schema")
async def retrieve_schema(req: RetrieveRequest):
    """
    Pure k-NN (vector) retrieval.
    Optionally narrow to specific schema_name or db_alias values.
    """
    return await _do_retrieve(req, hybrid=req.hybrid)


@app.post("/retrieve-schema/hybrid")
async def retrieve_schema_hybrid(req: HybridRetrieveRequest):
    """
    Hybrid k-NN + BM25 retrieval.
    Useful when the user query contains exact table/column name keywords.
    """
    return await _do_retrieve(req, hybrid=True)


@app.post("/retrieve-schema/rrf")
async def retrieve_schema_rrf(req: HybridRetrieveRequest):
    """
    Reciprocal Rank Fusion retrieval.

    Runs k-NN and BM25 independently, then merges the two ranked lists using
    RRF scoring:  score_rrf(d) = Σ  1 / (k + rank_i(d))  where k=60.

    Benefits over script_score hybrid:
    • No score-scale mismatch between cosine and BM25 values.
    • A document that ranks highly in *either* list gets a strong combined score.
    • Weights (knn_weight / keyword_weight) act as multipliers on each list's
      RRF contribution.
    """
    return await _do_retrieve_rrf(req)


# ==========================================================================
# Core retrieval logic  (Fix 1 — async wrapper; sync work runs in executor)
# ==========================================================================

async def _do_retrieve(req: RetrieveRequest, *, hybrid: bool = False) -> dict:
    """
    Async endpoint handler.  Embedding and OpenSearch calls are synchronous
    (blocking I/O), so we push them onto the default thread-pool executor to
    avoid blocking the uvicorn event loop under concurrent load.
    """
    if CFG is None or EMBEDDER is None or OS_CLIENT is None:
        raise HTTPException(503, "Service not initialised — check startup logs")

    t0    = time.time()
    top_k = req.top_k if (req.top_k and req.top_k > 0) else int(CFG["TOP_K"])
    loop  = asyncio.get_running_loop()

    # Determine candidate pool size if reranking is enabled
    rerank_enabled = CFG.get("RERANK_ENABLED", "false").lower() in ("1", "true", "yes")
    fetch_k = max(top_k, int(CFG.get("RERANK_TOP_N", "15"))) if rerank_enabled else top_k

    # 1. Embed the query — run blocking call off the event loop
    try:
        q_vec = await loop.run_in_executor(
            None, lambda: EMBEDDER.embed([req.user_query])[0]
        )
    except Exception as exc:
        log.exception("Embedding query failed")
        raise HTTPException(500, f"Embedding failed: {exc}")

    # 2. Build filters (pure in-memory, no I/O)
    filters = _build_filters(req)

    # 3. Execute OpenSearch query — also blocking I/O, run in executor
    try:
        if hybrid and isinstance(req, HybridRetrieveRequest):
            hits = await loop.run_in_executor(
                None,
                lambda: _hybrid_search(req.user_query, q_vec, filters, fetch_k,
                                       req.knn_weight, req.keyword_weight),
            )
        else:
            hits = await loop.run_in_executor(
                None,
                lambda: _knn_search(q_vec, filters, fetch_k),
            )
    except Exception as exc:
        log.exception("OpenSearch query failed")
        raise HTTPException(500, f"Search failed: {exc}")

    # 4. Format results
    results = _format_hits(hits)

    # 4b. Re-ranking step if enabled
    if rerank_enabled and RERANKER and results:
        results = await loop.run_in_executor(
            None, lambda: RERANKER.rerank(req.user_query, results, top_k)
        )
    else:
        results = results[:top_k]

    # 5. FK relationship expansion (1-hop)
    fk_expand = CFG.get("FK_EXPAND", "true").lower() in ("1", "true", "yes")
    if fk_expand and results:
        results = await loop.run_in_executor(
            None, lambda: _expand_fk_relationships(results, filters),
        )

    took_ms = round((time.time() - t0) * 1000, 1)
    log.info(
        "retrieve-schema served",
        extra={
            "results":  len(results),
            "took_ms":  took_ms,
            "hybrid":   hybrid,
            "filtered": bool(req.schema_filter or req.db_alias_filter),
        },
    )
    return {
        "query":    req.user_query,
        "results":  results,
        "took_ms":  took_ms,
    }


async def _do_retrieve_rrf(req: HybridRetrieveRequest) -> dict:
    """
    Reciprocal Rank Fusion endpoint logic.
    Runs k-NN and BM25 independently then merges with RRF scoring.
    """
    if CFG is None or EMBEDDER is None or OS_CLIENT is None:
        raise HTTPException(503, "Service not initialised — check startup logs")

    t0    = time.time()
    top_k = req.top_k if (req.top_k and req.top_k > 0) else int(CFG["TOP_K"])
    loop  = asyncio.get_running_loop()

    rerank_enabled = CFG.get("RERANK_ENABLED", "false").lower() in ("1", "true", "yes")
    fetch_k = max(top_k, int(CFG.get("RERANK_TOP_N", "15"))) if rerank_enabled else top_k

    try:
        q_vec = await loop.run_in_executor(
            None, lambda: EMBEDDER.embed([req.user_query])[0]
        )
    except Exception as exc:
        log.exception("Embedding query failed")
        raise HTTPException(500, f"Embedding failed: {exc}")

    filters = _build_filters(req)

    # Run both searches in parallel using thread executor
    try:
        knn_hits, bm25_hits = await asyncio.gather(
            loop.run_in_executor(None, lambda: _knn_search(q_vec, filters, fetch_k * 2)),
            loop.run_in_executor(None, lambda: _bm25_search(req.user_query, filters, fetch_k * 2)),
        )
    except Exception as exc:
        log.exception("RRF search failed")
        raise HTTPException(500, f"Search failed: {exc}")

    hits = _rrf_merge(knn_hits, bm25_hits, fetch_k, req.knn_weight, req.keyword_weight)
    results = _format_hits(hits)

    # Re-ranking step if enabled
    if rerank_enabled and RERANKER and results:
        results = await loop.run_in_executor(
            None, lambda: RERANKER.rerank(req.user_query, results, top_k)
        )
    else:
        results = results[:top_k]

    fk_expand = CFG.get("FK_EXPAND", "true").lower() in ("1", "true", "yes")
    if fk_expand and results:
        results = await loop.run_in_executor(
            None, lambda: _expand_fk_relationships(results, filters),
        )

    took_ms = round((time.time() - t0) * 1000, 1)
    log.info(
        "retrieve-schema/rrf served",
        extra={"results": len(results), "took_ms": took_ms},
    )
    return {
        "query":    req.user_query,
        "results":  results,
        "took_ms":  took_ms,
    }


# ==========================================================================
# OpenSearch query builders
# ==========================================================================

def _format_hits(hits: List[dict]) -> List[dict]:
    """Convert raw OpenSearch hits into the API response shape."""
    results = []
    for hit in hits:
        src   = hit["_source"]
        score = float(hit.get("_score", 0.0))

        schema_name = src.get("schema_name", "")
        table_name  = src.get("table_name", "")
        columns_raw = src.get("columns_json", [])
        columns     = columns_raw if isinstance(columns_raw, list) else []

        results.append({
            "table_id":        src.get("table_id", f"{schema_name}.{table_name}"),
            "source_type":     src.get("source_type", ""),
            "db_alias":        src.get("db_alias", ""),
            "schema_name":     schema_name,
            "table_name":      table_name,
            "table_comment":   src.get("table_comment", ""),
            "columns":         columns,
            "pk":              src.get("pk_json", []),
            "fk":              src.get("fk_json", []),
            "sample_rows":     src.get("sample_rows_json", []),
            "text_agg":        src.get("text_agg", ""),
            # cosinesimil already returns 0–1; no L1 normalisation needed
            "score":           round(score, 6),
            "confidence":      round(score, 6),
            # enrichment fields
            "indexes":         src.get("indexes_json", []),
            "referenced_by":   src.get("referenced_by_json", []),
            "row_count_approx": src.get("row_count_approx"),
            "column_names":    src.get("column_names", ""),
            "enum_values":     src.get("enum_values_json", {}),
            "sketches":        _sketches(schema_name, table_name, columns,
                                         source_type=src.get("source_type", "postgresql")),
            "fk_expanded":     False,  # set to True for tables added via FK expansion
        })
    return results


def _fetch_fk_neighbours(result_doc: dict) -> Set[str]:
    """Return the set of 'schema.table' FK neighbours for one result dict."""
    neighbours: Set[str] = set()
    for fk in (result_doc.get("fk") or []):
        if isinstance(fk, dict):
            fq = f'{fk.get("to_schema","")}.{fk.get("to_table","")}'
            if fq != ".":
                neighbours.add(fq)
    for ref in (result_doc.get("referenced_by") or []):
        if isinstance(ref, str) and ref.count(".") >= 2:
            parts = ref.split(".")
            neighbours.add(f"{parts[0]}.{parts[1]}")
    return neighbours


def _fetch_one_fk_table(
    fq_name: str,
    db_aliases: List[str],
    filters: List[dict],
) -> Optional[dict]:
    """
    Fetch a single table from the OpenSearch index by 'schema.table' key.
    Returns a formatted result dict (fk_expanded=True) or None if not found.
    """
    assert OS_CLIENT and CFG
    parts = fq_name.split(".", 1)
    tbl         = parts[-1] if len(parts) == 2 else fq_name
    schema_part = parts[0]  if len(parts) == 2 else None

    must_clauses: List[dict] = [{"term": {"table_name": tbl}}]
    if schema_part:
        must_clauses.append({"term": {"schema_name": schema_part}})
    if db_aliases:
        must_clauses.append({"terms": {"db_alias": db_aliases}})
    if filters:
        must_clauses.extend(filters)

    try:
        resp = OS_CLIENT.search(
            index=CFG["OS_INDEX"],
            body={
                "size": 1,
                "_source": {"excludes": ["embedding"]},
                "query": {"bool": {"must": must_clauses}},
            },
        )
    except Exception:
        log.debug("FK expansion fetch failed", extra={"table": fq_name}, exc_info=True)
        return None

    hits = resp.get("hits", {}).get("hits", [])
    if not hits:
        return None

    src         = hits[0]["_source"]
    schema_name = src.get("schema_name", "")
    table_name  = src.get("table_name", "")
    columns_raw = src.get("columns_json", [])
    columns     = columns_raw if isinstance(columns_raw, list) else []

    return {
        "table_id":         src.get("table_id", ""),
        "source_type":      src.get("source_type", ""),
        "db_alias":         src.get("db_alias", ""),
        "schema_name":      schema_name,
        "table_name":       table_name,
        "table_comment":    src.get("table_comment", ""),
        "columns":          columns,
        "pk":               src.get("pk_json", []),
        "fk":               src.get("fk_json", []),
        "sample_rows":      src.get("sample_rows_json", []),
        "text_agg":         src.get("text_agg", ""),
        "score":            0.0,
        "confidence":       0.0,
        "indexes":          src.get("indexes_json", []),
        "referenced_by":    src.get("referenced_by_json", []),
        "row_count_approx": src.get("row_count_approx"),
        "column_names":     src.get("column_names", ""),
        "enum_values":      src.get("enum_values_json", {}),
        "sketches":         _sketches(schema_name, table_name, columns,
                                      source_type=src.get("source_type", "postgresql")),
        "fk_expanded":      True,
    }


def _expand_fk_relationships(
    results: List[dict],
    filters: List[dict],
) -> List[dict]:
    """
    Multi-hop FK relationship expansion (A6 — up to FK_EXPAND_HOPS hops).

    Starting from the directly-retrieved tables, iteratively walks outgoing FKs
    (fk field) and incoming references (referenced_by field) up to
    ``FK_EXPAND_HOPS`` levels deep (default: 2).  A ``seen`` set guards against
    cycles so bridge tables that reference each other do not cause infinite loops.

    Hop 1 example:
        Retrieve: orders → expand to: customers, order_items

    Hop 2 example:
        orders → order_items → products   (product is 2 hops from orders)

    ``fk_expanded: true`` is set on every table added by this expansion.
    """
    assert OS_CLIENT and CFG

    max_hops = int(CFG.get("FK_EXPAND_HOPS", "2"))
    db_aliases = list({r["db_alias"] for r in results if r.get("db_alias")})

    # seen tracks table_id values already in the result set to prevent duplicates
    seen: Set[str] = {r["table_id"] for r in results}

    # frontier holds the result dicts whose FK neighbours we still need to visit
    frontier: List[dict] = list(results)
    expanded: List[dict] = list(results)

    for _hop in range(max_hops):
        next_frontier: List[dict] = []

        for doc in frontier:
            for fq_name in _fetch_fk_neighbours(doc):
                # Skip if already in the result set (cycle guard)
                already_present = any(
                    r["table_id"].endswith(f".{fq_name}") or r["table_id"] == fq_name
                    for r in expanded
                )
                if already_present:
                    continue

                fetched = _fetch_one_fk_table(fq_name, db_aliases, filters)
                if fetched is None:
                    continue

                tid = fetched["table_id"]
                if tid in seen:
                    continue

                seen.add(tid)
                expanded.append(fetched)
                next_frontier.append(fetched)

        if not next_frontier:
            break  # no new tables found — stop early
        frontier = next_frontier

    if len(expanded) > len(results):
        log.info(
            "FK expansion complete",
            extra={
                "original": len(results),
                "added":    len(expanded) - len(results),
                "hops":     max_hops,
            },
        )

    return expanded


def _rrf_merge(
    knn_hits: List[dict],
    bm25_hits: List[dict],
    top_k: int,
    knn_weight: float = 1.0,
    kw_weight: float = 1.0,
    rrf_k: int = 60,
) -> List[dict]:
    """
    Merge two ranked hit lists using Reciprocal Rank Fusion.

    score(d) = knn_weight * (1 / (rrf_k + rank_knn(d)))
             + kw_weight  * (1 / (rrf_k + rank_bm25(d)))

    Documents not appearing in a list are excluded from that list's term.
    Returns the top_k merged hits as fake OpenSearch hit dicts (score = rrf_score).
    """
    scores: Dict[str, float] = {}
    source_map: Dict[str, dict] = {}

    for rank, hit in enumerate(knn_hits, start=1):
        doc_id = hit.get("_id", "")
        scores[doc_id] = scores.get(doc_id, 0.0) + knn_weight / (rrf_k + rank)
        source_map[doc_id] = hit

    for rank, hit in enumerate(bm25_hits, start=1):
        doc_id = hit.get("_id", "")
        scores[doc_id] = scores.get(doc_id, 0.0) + kw_weight / (rrf_k + rank)
        if doc_id not in source_map:
            source_map[doc_id] = hit

    sorted_ids = sorted(scores, key=lambda d: scores[d], reverse=True)[:top_k]
    merged = []
    for doc_id in sorted_ids:
        hit = dict(source_map[doc_id])
        hit["_score"] = round(scores[doc_id], 8)
        merged.append(hit)
    return merged


def _build_filters(req: RetrieveRequest) -> List[dict]:
    """Build a list of OpenSearch filter clauses from optional request params."""
    filters: List[dict] = []
    if req.schema_filter:
        filters.append({"terms": {"schema_name": req.schema_filter}})
    if req.db_alias_filter:
        filters.append({"terms": {"db_alias": req.db_alias_filter}})
    return filters


def _knn_search(
    q_vec: List[float],
    filters: List[dict],
    top_k: int,
) -> List[dict]:
    """Pure k-NN query using OpenSearch knn_vector field."""
    assert OS_CLIENT and CFG
    knn_clause: Dict[str, Any] = {
        "vector":  q_vec,
        "k":       top_k,
    }
    if filters:
        knn_clause["filter"] = {"bool": {"must": filters}}

    body: Dict[str, Any] = {
        "size": top_k,
        "_source": {
            "excludes": ["embedding"]   # never send the vector back to the caller
        },
        "query": {
            "knn": {"embedding": knn_clause}
        },
    }
    # A2 — use MIN_SCORE (k-NN cosine threshold, default 0.40)
    min_score = float(CFG.get("MIN_SCORE", "0.40"))
    if min_score > 0:
        body["min_score"] = min_score

    resp = OS_CLIENT.search(index=CFG["OS_INDEX"], body=body)
    return resp["hits"]["hits"]


def _hybrid_search(
    query_text: str,
    q_vec: List[float],
    filters: List[dict],
    top_k: int,
    knn_weight: float,
    kw_weight: float,
) -> List[dict]:
    """
    Fix 6 — Hybrid search using script_score for a true weighted combination.

    OpenSearch's function_score wraps each sub-query independently, so both
    scores are normalised to [0, 1] before weighting.  script_score lets us
    compute the linear combination directly:

        final_score = knn_weight * knn_score + kw_weight * bm25_score

    We use a two-pass approach:
      1. BM25 multi_match is the outer query (drives candidate selection).
      2. script_score injects the k-NN cosine value via the knn() function
         and combines it with the BM25 score from _score.

    Filters are applied as a bool/filter wrapper so they don't affect scoring.
    """
    assert OS_CLIENT and CFG

    # BM25 inner query (field boosts kept from original)
    bm25_query: Dict[str, Any] = {
        "multi_match": {
            "query":  query_text,
            "fields": ["text_agg^2", "table_name^3", "table_comment", "column_names"],
            "type":   "best_fields",
        }
    }

    # Wrap with filter if needed
    if filters:
        inner_query: Dict[str, Any] = {
            "bool": {
                "must":   [bm25_query],
                "filter": filters,
            }
        }
    else:
        inner_query = bm25_query

    body: Dict[str, Any] = {
        "size": top_k,
        "_source": {"excludes": ["embedding"]},
        "query": {
            "script_score": {
                "query": inner_query,
                # knn() returns the raw cosine score (0–1 with cosinesimil space);
                # _score is the BM25 score (unbounded).  We normalise BM25 via
                # saturation: bm25_norm = _score / (1 + _score) → capped at 1.
                "script": {
                    "source": (
                        f"double knn = knn(params.field, params.query_value, params.k);"
                        f"double bm25_norm = _score / (1.0 + _score);"
                        f"return {knn_weight} * knn + {kw_weight} * bm25_norm;"
                    ),
                    "params": {
                        "field":       "embedding",
                        "query_value": q_vec,
                        "k":           top_k * 2,
                    },
                },
            }
        },
    }

    # A2 — hybrid/script_score scores can exceed 1.0, so use a higher threshold
    min_score = float(CFG.get("MIN_SCORE_HYBRID", "0.55"))
    if min_score > 0:
        body["min_score"] = min_score

    resp = OS_CLIENT.search(index=CFG["OS_INDEX"], body=body)
    return resp["hits"]["hits"]


def _bm25_search(
    query_text: str,
    filters: List[dict],
    top_k: int,
) -> List[dict]:
    """
    Pure BM25 (keyword) search — used as one leg of RRF.
    No vector query; results scored purely on lexical match.
    """
    assert OS_CLIENT and CFG
    bm25_query: Dict[str, Any] = {
        "multi_match": {
            "query":  query_text,
            "fields": ["text_agg^2", "table_name^3", "table_comment", "column_names"],
            "type":   "best_fields",
        }
    }
    if filters:
        inner_query: Dict[str, Any] = {
            "bool": {"must": [bm25_query], "filter": filters}
        }
    else:
        inner_query = bm25_query

    resp = OS_CLIENT.search(
        index=CFG["OS_INDEX"],
        body={
            "size": top_k,
            "_source": {"excludes": ["embedding"]},
            "query": inner_query,
        },
    )
    return resp["hits"]["hits"]


# ==========================================================================
# Optional direct run
# ==========================================================================

if __name__ == "__main__":
    import uvicorn

    try:
        uvicorn.run(
            "schema_retriever_opensearch:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8080")),
            reload=os.getenv("RELOAD", "false").lower() in ("1", "true", "yes"),
        )
    except ImportError:
        log.error("uvicorn not installed. pip install 'uvicorn[standard]'")
        sys.exit(2)
