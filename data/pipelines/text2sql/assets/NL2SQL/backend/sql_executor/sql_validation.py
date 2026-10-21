"""
sql_validation.py

Pure SQL safety validation logic — no FastAPI/psycopg2 dependency.
Imported by tool_sql_executor.py and directly by tests.

Requires only: sqlglot
"""

from __future__ import annotations

import re
from typing import Optional, Set

import sqlglot
import sqlglot.expressions as exp
from sqlglot.errors import ParseError as SQLGlotParseError


# ===========================================================================
# Fast pre-filters (regex)
# ===========================================================================

_ALLOWED_STARTS = re.compile(r"^\s*(select|explain|with)\b", re.IGNORECASE)

_BLOCKED_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|truncate|alter|create|replace|"
    r"grant|revoke|copy|call|do|execute|pg_read_file|pg_ls_dir)\b",
    re.IGNORECASE,
)


# ===========================================================================
# Error type
# ===========================================================================

class SQLValidationError(ValueError):
    """Raised when a query fails any safety check."""


# ===========================================================================
# AST parsing
# ===========================================================================

def _parse_sql(sql: str) -> sqlglot.Expression:
    """
    Parse SQL with sqlglot (PostgreSQL dialect).

    Raises SQLValidationError on parse failure or if the parsed statement is
    not a single SELECT / EXPLAIN.
    """
    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except SQLGlotParseError as exc:
        raise SQLValidationError(f"SQL parse error: {exc}") from exc

    if not statements:
        raise SQLValidationError("Empty SQL statement.")
    if len(statements) > 1:
        raise SQLValidationError(
            f"Only a single SQL statement is permitted; got {len(statements)}."
        )

    stmt = statements[0]
    if stmt is None:
        raise SQLValidationError("Could not parse SQL statement.")

    if not isinstance(stmt, (exp.Select, exp.With, exp.Command)):
        raise SQLValidationError(
            f"Only SELECT/EXPLAIN/WITH queries are permitted; "
            f"got {type(stmt).__name__}."
        )

    if isinstance(stmt, exp.With):
        inner = stmt.args.get("this")
        if not isinstance(inner, exp.Select):
            raise SQLValidationError(
                "WITH expression must terminate in a SELECT statement."
            )

    return stmt


# ===========================================================================
# Public API
# ===========================================================================

def validate_read_only(sql: str) -> sqlglot.Expression:
    """
    Full SQL safety validation pipeline.

    1. Regex fast pre-filter.
    2. sqlglot AST parse — rejects multi-statement, DDL, DML.
    3. Blocked-keyword secondary net.

    Returns the parsed AST expression so callers can reuse it.
    Raises SQLValidationError on any violation.
    """
    stripped = sql.strip()

    if not _ALLOWED_STARTS.match(stripped):
        raise SQLValidationError(
            "Only SELECT, EXPLAIN, and WITH … SELECT queries are permitted."
        )

    if _BLOCKED_KEYWORDS.search(stripped):
        raise SQLValidationError(
            "Query contains a prohibited keyword (INSERT/UPDATE/DELETE/DROP/…)."
        )

    return _parse_sql(stripped)


def enforce_limit(stmt: sqlglot.Expression, max_rows: int) -> str:
    """
    Inject or cap the LIMIT clause in the parsed AST.

    - SELECT without LIMIT  → add LIMIT max_rows
    - SELECT LIMIT n > max  → reduce to LIMIT max_rows
    - EXPLAIN               → unchanged
    Returns the rewritten SQL string.
    """
    select_node: Optional[exp.Select] = None
    if isinstance(stmt, exp.Select):
        select_node = stmt
    elif isinstance(stmt, exp.With):
        inner = stmt.args.get("this")
        if isinstance(inner, exp.Select):
            select_node = inner

    if select_node is None:
        return stmt.sql(dialect="postgres")

    current_limit = select_node.args.get("limit")
    if current_limit is None:
        select_node = select_node.limit(max_rows)
    else:
        limit_expr = current_limit.args.get("expression")
        if isinstance(limit_expr, exp.Literal):
            try:
                current_val = int(limit_expr.this)
                if current_val > max_rows:
                    select_node = select_node.limit(max_rows)
            except (ValueError, TypeError):
                pass

    if isinstance(stmt, exp.With):
        stmt.set("this", select_node)
        return stmt.sql(dialect="postgres")
    return select_node.sql(dialect="postgres")


def validate_schema_objects(
    stmt: sqlglot.Expression,
    allowed_tables: Optional[Set[str]],
) -> None:
    """
    If allowed_tables is non-empty, verify every table in the AST exists in it.
    Raises SQLValidationError listing the offending names on failure.
    """
    if not allowed_tables:
        return
    referenced = _extract_tables(stmt)
    unknown = referenced - {t.lower() for t in allowed_tables}
    if unknown:
        raise SQLValidationError(
            f"Query references unknown table(s): {', '.join(sorted(unknown))}. "
            "Verify the table names and schema metadata."
        )


def _extract_tables(stmt: sqlglot.Expression) -> Set[str]:
    """Return the set of table names referenced in the statement (lower-cased)."""
    return {
        tbl.name.lower()
        for tbl in stmt.find_all(exp.Table)
        if tbl.name
    }


def _extract_columns(stmt: sqlglot.Expression) -> Set[str]:
    """Return the set of bare column names referenced (lower-cased)."""
    return {
        col.name.lower()
        for col in stmt.find_all(exp.Column)
        if col.name
    }
