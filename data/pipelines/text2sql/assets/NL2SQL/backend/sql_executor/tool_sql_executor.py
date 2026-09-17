"""
tool_sql_executor.py  (hardened v3)

Text2SQL backend SQL execution service.

Improvements in v3
------------------
1. AST-based SQL validation     — sqlglot parses the query into an AST; only a
                                   single SELECT/EXPLAIN/WITH…SELECT is accepted.
                                   Regex is kept as a fast pre-filter only.
2. Table/column validation      — referenced tables and columns are extracted from
                                   the AST and validated against a supplied schema
                                   snapshot (optional; skipped when not provided).
3. LIMIT enforcement via parser — sqlglot rewrites the query to inject/cap the
                                   LIMIT clause at the AST level, not via string concat.
4. EXPLAIN cost check           — optional: EXPLAIN the query and reject it when
                                   the planner cost or row estimate exceeds a
                                   configurable threshold (EXPLAIN_MAX_COST,
                                   EXPLAIN_MAX_ROWS env vars).
5. HTTP 503 on health failure   — /health returns 503 when the database is
                                   unreachable so Code Engine marks the instance
                                   unhealthy.
6. Executor abstraction         — SQLExecutorBase + PostgreSQLExecutor split
                                   prepares the way for a Db2 executor without
                                   touching the API layer.

Environment variables
---------------------
  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS
  DB_SSLMODE            (default: require)
  DB_SSLROOTCERT        (path to CA cert when sslmode=verify-ca/verify-full)
  MAX_ROWS              (default: 100)
  STATEMENT_TIMEOUT_MS  (default: 30000)
  POOL_MIN, POOL_MAX    (default: 1, 5)

  # EXPLAIN cost gating (both disabled by default — set to enable)
  EXPLAIN_MAX_COST      (float; reject when planner total-cost > this value)
  EXPLAIN_MAX_ROWS      (int;   reject when planner row-estimate > this value)

  # Concurrency alignment
  # Set POOL_MAX >= (Code Engine concurrency per instance).
  # Recommended starting point: POOL_MAX=10 when CE concurrency=10.
  PORT=8000
  LOG_LEVEL=INFO
"""

from __future__ import annotations

import json
import logging
import os
import sys
from abc import ABC, abstractmethod
from typing import Any, List, Optional, Set, Tuple

import psycopg2
from psycopg2 import pool as pg_pool

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from sql_validation import (
    SQLValidationError,
    validate_read_only,
    enforce_limit,
    validate_schema_objects,
    _extract_tables,
)

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

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    stream=sys.stdout,
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d — %(message)s",
)
log = logging.getLogger("sql_executor")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DB_HOST    = os.getenv("DB_HOST", "")
DB_PORT    = os.getenv("DB_PORT", "5432")
DB_NAME    = os.getenv("DB_NAME", "")
DB_USER    = os.getenv("DB_USER", "")
DB_PASS    = os.getenv("DB_PASS", "")
DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
DB_SSLCERT = os.getenv("DB_SSLROOTCERT", "")

MAX_ROWS        = int(os.getenv("MAX_ROWS", "100"))
STMT_TIMEOUT_MS = int(os.getenv("STATEMENT_TIMEOUT_MS", "30000"))
POOL_MIN        = int(os.getenv("POOL_MIN", "1"))
POOL_MAX        = int(os.getenv("POOL_MAX", "5"))

_EXPLAIN_MAX_COST = os.getenv("EXPLAIN_MAX_COST", "")
_EXPLAIN_MAX_ROWS = os.getenv("EXPLAIN_MAX_ROWS", "")
EXPLAIN_MAX_COST: Optional[float] = float(_EXPLAIN_MAX_COST) if _EXPLAIN_MAX_COST else None
EXPLAIN_MAX_ROWS: Optional[int]   = int(_EXPLAIN_MAX_ROWS)   if _EXPLAIN_MAX_ROWS else None
EXPLAIN_ENABLED = EXPLAIN_MAX_COST is not None or EXPLAIN_MAX_ROWS is not None


# ===========================================================================
# Executor abstraction  (P1-13)
# ===========================================================================

class SQLExecutorBase(ABC):
    """Abstract SQL executor.  Each database engine subclasses this."""

    @abstractmethod
    def execute(
        self, sql: str, max_rows: int, timeout_ms: int
    ) -> Tuple[str, Any]:
        """
        Execute *sql* and return ``(rewritten_sql, rows)``.

        ``rows`` is either a list of dicts (SELECT results) or a status string.
        Raises HTTPException on error.
        """

    @abstractmethod
    def health(self) -> dict:
        """Return a health-check dict.  Must not raise."""

    @property
    @abstractmethod
    def dialect(self) -> str:
        """sqlglot dialect name (e.g. 'postgres', 'bigquery')."""


class PostgreSQLExecutor(SQLExecutorBase):
    """PostgreSQL executor backed by psycopg2 ThreadedConnectionPool."""

    dialect = "postgres"

    def __init__(self) -> None:
        if not all([DB_HOST, DB_NAME, DB_USER, DB_PASS]):
            raise RuntimeError(
                "Missing required env vars: DB_HOST, DB_NAME, DB_USER, DB_PASS"
            )
        self._pool = pg_pool.ThreadedConnectionPool(POOL_MIN, POOL_MAX, self._dsn())
        log.info(
            "PostgreSQL connection pool ready",
            extra={"host": DB_HOST, "db": DB_NAME, "min": POOL_MIN, "max": POOL_MAX},
        )

    @staticmethod
    def _dsn() -> str:
        parts = [
            f"host={DB_HOST}",
            f"port={DB_PORT}",
            f"dbname={DB_NAME}",
            f"user={DB_USER}",
            f"password={DB_PASS}",
            f"sslmode={DB_SSLMODE}",
            "application_name=text2sql_executor",
        ]
        if DB_SSLCERT:
            parts.append(f"sslrootcert='{DB_SSLCERT}'")
        return " ".join(parts)

    def health(self) -> dict:
        conn = None
        try:
            conn = self._pool.getconn()
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            return {"ok": True, "db": DB_NAME, "host": DB_HOST}
        except Exception:
            log.exception("Health check failed")
            return {"ok": False, "error": "Database unreachable"}
        finally:
            if conn is not None:
                try:
                    self._pool.putconn(conn)
                except Exception:
                    pass

    def execute(self, sql: str, max_rows: int, timeout_ms: int) -> Tuple[str, Any]:
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SET LOCAL statement_timeout = {timeout_ms}")
            with conn.cursor() as cur:
                cur.execute(sql)
                if cur.description:
                    columns: List[str] = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    result: Any = [dict(zip(columns, row)) for row in rows]
                else:
                    result = {"status": "Query executed (no rows returned)"}
            conn.rollback()
            return sql, result
        except psycopg2.errors.QueryCanceled:
            conn.rollback()
            raise HTTPException(
                status_code=408,
                detail=f"Query exceeded {timeout_ms} ms timeout",
            )
        except psycopg2.Error as exc:
            conn.rollback()
            pgcode = getattr(exc, "pgcode", "UNKNOWN")
            log.warning(
                "Query failed",
                extra={"pgcode": pgcode, "query_prefix": sql[:120]},
                exc_info=True,
            )
            raise HTTPException(
                status_code=400,
                detail=f"SQL error (pgcode={pgcode}). Check your query syntax.",
            )
        except Exception:
            conn.rollback()
            log.exception("Unexpected error executing query")
            raise HTTPException(status_code=500, detail="Internal error")
        finally:
            self._pool.putconn(conn)

    def explain_cost(self, sql: str, timeout_ms: int) -> Tuple[Optional[float], Optional[int]]:
        """
        Run EXPLAIN (FORMAT JSON) and return (total_cost, row_estimate).
        Returns (None, None) if EXPLAIN fails (non-fatal).
        """
        conn = self._pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute(f"SET LOCAL statement_timeout = {timeout_ms}")
                cur.execute(f"EXPLAIN (FORMAT JSON) {sql}")
                row = cur.fetchone()
            conn.rollback()
            if not row:
                return None, None
            plan = row[0]
            if isinstance(plan, str):
                plan = json.loads(plan)
            root = plan[0]["Plan"]
            return float(root.get("Total Cost", 0)), int(root.get("Plan Rows", 0))
        except Exception:
            log.debug("EXPLAIN cost check failed (non-fatal)", exc_info=True)
            try:
                conn.rollback()
            except Exception:
                pass
            return None, None
        finally:
            try:
                self._pool.putconn(conn)
            except Exception:
                pass


# ===========================================================================
# Module-level singleton executor
# ===========================================================================

_EXECUTOR: Optional[PostgreSQLExecutor] = None


def _get_executor() -> PostgreSQLExecutor:
    global _EXECUTOR
    if _EXECUTOR is None:
        _EXECUTOR = PostgreSQLExecutor()
    return _EXECUTOR


# ===========================================================================
# Request model
# ===========================================================================

class SQLQueryRequest(BaseModel):
    sql: str
    # Optional: set of table names to validate against (supplied by the LLM
    # after retrieving schema context). If omitted, table validation is skipped.
    allowed_tables: Optional[List[str]] = None

    @field_validator("sql")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("sql must not be empty")
        return v.strip().rstrip(";")


# ===========================================================================
# FastAPI app
# ===========================================================================

app = FastAPI(
    title="Text2SQL SQL Executor",
    description="Read-only SQL execution endpoint for Text2SQL pipelines.",
    version="3.0.0",
)


@app.exception_handler(Exception)
async def _global_handler(request: Request, exc: Exception) -> JSONResponse:
    log.exception("Unhandled error", extra={"path": str(request.url)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health(response: Response) -> dict:
    """
    Liveness + DB connectivity check.
    Returns HTTP 503 when the database is unreachable so that Code Engine /
    Kubernetes readiness probes correctly mark the instance unhealthy.
    """
    try:
        executor = _get_executor()
    except RuntimeError as exc:
        response.status_code = 503
        return {"ok": False, "error": str(exc)}

    result = executor.health()
    if not result.get("ok"):
        response.status_code = 503
    return result


@app.post("/run-sql")
def run_sql(payload: SQLQueryRequest) -> dict:
    """
    Execute a read-only SQL query.

    Validation pipeline
    -------------------
    1. Regex fast pre-filter
    2. sqlglot AST parse — single statement, SELECT/EXPLAIN/WITH only
    3. Blocked-keyword secondary net
    4. Table/column validation against allowed_tables (if supplied)
    5. LIMIT injection / cap via AST rewrite
    6. Optional EXPLAIN cost check (if EXPLAIN_MAX_COST or EXPLAIN_MAX_ROWS set)
    7. Execute with per-statement timeout
    """
    query = payload.sql
    allowed: Optional[Set[str]] = set(payload.allowed_tables) if payload.allowed_tables else None

    # ── 1–3. AST-based read-only validation ──
    try:
        stmt = validate_read_only(query)
    except SQLValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── 4. Table validation (optional) ──
    try:
        validate_schema_objects(stmt, allowed)
    except SQLValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # ── 5. Enforce LIMIT via AST rewrite ──
    query = enforce_limit(stmt, MAX_ROWS)

    executor = _get_executor()

    # ── 6. Optional EXPLAIN cost gate ──
    if EXPLAIN_ENABLED and isinstance(executor, PostgreSQLExecutor):
        total_cost, plan_rows = executor.explain_cost(query, STMT_TIMEOUT_MS)
        if total_cost is not None and EXPLAIN_MAX_COST is not None:
            if total_cost > EXPLAIN_MAX_COST:
                log.warning(
                    "Query rejected by cost gate",
                    extra={"total_cost": total_cost, "limit": EXPLAIN_MAX_COST},
                )
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Query estimated cost ({total_cost:.0f}) exceeds the "
                        f"maximum allowed ({EXPLAIN_MAX_COST:.0f}). "
                        "Refine the query (add filters, avoid large scans)."
                    ),
                )
        if plan_rows is not None and EXPLAIN_MAX_ROWS is not None:
            if plan_rows > EXPLAIN_MAX_ROWS:
                log.warning(
                    "Query rejected by row-estimate gate",
                    extra={"plan_rows": plan_rows, "limit": EXPLAIN_MAX_ROWS},
                )
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Query estimated row scan ({plan_rows:,}) exceeds the "
                        f"maximum allowed ({EXPLAIN_MAX_ROWS:,}). "
                        "Add filters to reduce the scanned row count."
                    ),
                )

    # ── 7. Execute ──
    _, result = executor.execute(query, MAX_ROWS, STMT_TIMEOUT_MS)
    return {"sql": query, "result": result}
