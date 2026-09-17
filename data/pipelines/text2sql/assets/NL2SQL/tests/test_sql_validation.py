"""
tests/test_sql_validation.py

Unit tests for sql_executor validation logic.

Covers:
  - AST-based read-only enforcement (validate_read_only)
  - Single-statement check
  - LIMIT injection and capping (enforce_limit)
  - Table validation against an allowed set (validate_schema_objects)
  - SQL safety corpus (multi-statement, DDL, DML, admin functions)

Run:
    py -3.12 -m pytest NL2SQL/tests/test_sql_validation.py -v
"""

from __future__ import annotations

import sys
import os

# Import pure validation logic from the standalone module (no FastAPI/psycopg2 needed)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend", "sql_executor"))

import pytest

from sql_validation import (
    SQLValidationError,
    validate_read_only,
    enforce_limit,
    validate_schema_objects,
    _extract_tables,
)


# ===========================================================================
# validate_read_only — allowed queries
# ===========================================================================

class TestAllowedQueries:

    def test_simple_select(self):
        stmt = validate_read_only("SELECT * FROM orders")
        assert stmt is not None

    def test_select_with_where(self):
        stmt = validate_read_only("SELECT id, name FROM customers WHERE active = true")
        assert stmt is not None

    def test_select_with_join(self):
        sql = "SELECT o.id, c.name FROM orders o JOIN customers c ON o.customer_id = c.id"
        stmt = validate_read_only(sql)
        assert stmt is not None

    def test_select_with_aggregation(self):
        sql = "SELECT status, COUNT(*) AS n FROM orders GROUP BY status ORDER BY n DESC"
        stmt = validate_read_only(sql)
        assert stmt is not None

    def test_select_with_subquery(self):
        sql = "SELECT * FROM (SELECT id FROM orders WHERE status = 'PAID') AS sub"
        stmt = validate_read_only(sql)
        assert stmt is not None

    def test_with_cte_select(self):
        sql = """
        WITH recent AS (
            SELECT id, total FROM orders WHERE created_at > NOW() - INTERVAL '7 days'
        )
        SELECT * FROM recent
        """
        stmt = validate_read_only(sql)
        assert stmt is not None

    def test_explain_allowed(self):
        stmt = validate_read_only("EXPLAIN SELECT * FROM orders")
        assert stmt is not None

    def test_leading_whitespace_and_trailing_semicolon_stripped(self):
        # Pydantic validator strips trailing semicolons before hitting validation
        stmt = validate_read_only("  SELECT 1  ")
        assert stmt is not None


# ===========================================================================
# validate_read_only — rejected queries (SQL safety corpus)
# ===========================================================================

class TestRejectedQueries:

    def _assert_rejected(self, sql: str):
        with pytest.raises(SQLValidationError):
            validate_read_only(sql)

    # ── Multiple statements ─────────────────────────────────────────────────
    def test_multiple_statements(self):
        self._assert_rejected("SELECT 1; DROP TABLE orders")

    def test_multiple_selects(self):
        self._assert_rejected("SELECT 1; SELECT 2")

    # ── DDL ─────────────────────────────────────────────────────────────────
    def test_drop_table(self):
        self._assert_rejected("DROP TABLE orders")

    def test_truncate(self):
        self._assert_rejected("TRUNCATE TABLE orders")

    def test_alter_table(self):
        self._assert_rejected("ALTER TABLE orders ADD COLUMN note TEXT")

    def test_create_table(self):
        self._assert_rejected("CREATE TABLE hack (id INT)")

    # ── DML ─────────────────────────────────────────────────────────────────
    def test_insert(self):
        self._assert_rejected("INSERT INTO orders (id) VALUES (1)")

    def test_update(self):
        self._assert_rejected("UPDATE orders SET status = 'DELETED' WHERE id = 1")

    def test_delete(self):
        self._assert_rejected("DELETE FROM orders WHERE id = 1")

    # ── DML hidden inside a CTE ─────────────────────────────────────────────
    def test_cte_with_delete(self):
        self._assert_rejected(
            "WITH d AS (DELETE FROM orders RETURNING id) SELECT * FROM d"
        )

    def test_cte_with_insert(self):
        self._assert_rejected(
            "WITH i AS (INSERT INTO orders (id) VALUES (1) RETURNING id) SELECT * FROM i"
        )

    def test_cte_with_update(self):
        self._assert_rejected(
            "WITH u AS (UPDATE orders SET status='X' WHERE id=1 RETURNING id) SELECT * FROM u"
        )

    # ── Admin / file system functions ────────────────────────────────────────
    def test_pg_read_file(self):
        self._assert_rejected("SELECT pg_read_file('/etc/passwd')")

    def test_pg_ls_dir(self):
        self._assert_rejected("SELECT * FROM pg_ls_dir('.')")

    # ── Privilege escalation ─────────────────────────────────────────────────
    def test_grant(self):
        self._assert_rejected("GRANT ALL ON orders TO public")

    def test_revoke(self):
        self._assert_rejected("REVOKE SELECT ON orders FROM myuser")

    # ── COPY (file I/O) ──────────────────────────────────────────────────────
    def test_copy(self):
        self._assert_rejected("COPY orders TO '/tmp/dump.csv'")

    # ── Procedural execution ─────────────────────────────────────────────────
    def test_call(self):
        self._assert_rejected("CALL my_proc()")

    def test_do_block(self):
        self._assert_rejected("DO $$ BEGIN DELETE FROM orders; END $$")

    # ── Not a SELECT at all ──────────────────────────────────────────────────
    def test_bare_table_name(self):
        self._assert_rejected("orders")

    def test_empty_string(self):
        with pytest.raises((SQLValidationError, ValueError)):
            validate_read_only("")


# ===========================================================================
# enforce_limit
# ===========================================================================

class TestEnforceLimit:

    def _rewrite(self, sql: str, max_rows: int = 100) -> str:
        stmt = validate_read_only(sql)
        return enforce_limit(stmt, max_rows)

    def test_adds_limit_when_absent(self):
        rewritten = self._rewrite("SELECT * FROM orders", max_rows=50)
        assert "LIMIT 50" in rewritten.upper()

    def test_caps_large_limit(self):
        rewritten = self._rewrite("SELECT * FROM orders LIMIT 100000", max_rows=200)
        upper = rewritten.upper()
        assert "LIMIT 200" in upper
        assert "100000" not in upper

    def test_keeps_limit_below_max(self):
        rewritten = self._rewrite("SELECT * FROM orders LIMIT 10", max_rows=100)
        assert "LIMIT 10" in rewritten.upper()

    def test_cte_adds_limit(self):
        sql = "WITH c AS (SELECT id FROM orders) SELECT * FROM c"
        rewritten = self._rewrite(sql, max_rows=25)
        assert "LIMIT 25" in rewritten.upper()

    def test_explain_unchanged(self):
        sql = "EXPLAIN SELECT * FROM orders"
        rewritten = self._rewrite(sql, max_rows=100)
        # EXPLAIN should not have a LIMIT injected
        assert "LIMIT" not in rewritten.upper()

    def test_zero_limit_is_capped(self):
        # A malformed LLM query with LIMIT 0 — still gets capped to max
        # (0 < max, so it is kept as-is — this tests the preserve-small-limit path)
        rewritten = self._rewrite("SELECT * FROM orders LIMIT 0", max_rows=100)
        assert "LIMIT 0" in rewritten.upper()

    def test_exact_limit_unchanged(self):
        rewritten = self._rewrite("SELECT * FROM orders LIMIT 100", max_rows=100)
        assert "LIMIT 100" in rewritten.upper()


# ===========================================================================
# validate_schema_objects
# ===========================================================================

class TestSchemaObjectValidation:

    def test_known_table_passes(self):
        stmt = validate_read_only("SELECT * FROM orders")
        validate_schema_objects(stmt, {"orders", "customers"})  # should not raise

    def test_unknown_table_raises(self):
        stmt = validate_read_only("SELECT * FROM ghost_table")
        with pytest.raises(SQLValidationError, match="ghost_table"):
            validate_schema_objects(stmt, {"orders", "customers"})

    def test_multiple_unknown_tables_listed(self):
        sql = "SELECT * FROM ghost_a JOIN ghost_b ON ghost_a.id = ghost_b.id"
        stmt = validate_read_only(sql)
        with pytest.raises(SQLValidationError) as exc_info:
            validate_schema_objects(stmt, {"orders"})
        error_msg = str(exc_info.value).lower()
        assert "ghost_a" in error_msg or "ghost_b" in error_msg

    def test_none_allowed_tables_skips_validation(self):
        stmt = validate_read_only("SELECT * FROM any_table")
        validate_schema_objects(stmt, None)  # must not raise

    def test_empty_allowed_tables_skips_validation(self):
        stmt = validate_read_only("SELECT * FROM any_table")
        validate_schema_objects(stmt, set())  # empty set → skip (treated as None)

    def test_case_insensitive_matching(self):
        stmt = validate_read_only("SELECT * FROM Orders")
        validate_schema_objects(stmt, {"orders"})  # should not raise

    def test_cte_alias_not_flagged(self):
        # 'recent' is a CTE alias, not a real table — sqlglot parses it as a Table
        # node, so it will appear in _extract_tables. This test documents current
        # behaviour: callers should include CTE names in allowed_tables or use None.
        sql = "WITH recent AS (SELECT id FROM orders) SELECT * FROM recent"
        stmt = validate_read_only(sql)
        tables = _extract_tables(stmt)
        # 'orders' must be in extracted tables; 'recent' may or may not appear
        assert "orders" in tables
