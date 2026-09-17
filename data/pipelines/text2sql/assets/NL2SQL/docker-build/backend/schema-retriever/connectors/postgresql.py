"""
connectors/postgresql.py

PostgreSQL connector — uses SQLAlchemy reflection and direct catalog queries
to produce fully-enriched SchemaDoc objects for Text2SQL ingestion.

Enrichment over the original
-----------------------------
• Indexes         — all non-system indexes (name, columns, UNIQUE flag)
• Unique columns  — columns with UNIQUE constraint flagged on ColumnMeta
• Row count       — pg_stat_user_tables.n_live_tup (fast; no COUNT(*))
• Enum values     — top-N distinct values for columns with ≤ enum_row_limit
                    distinct values (skips PII, binary, and large-text columns)
• Reverse FKs     — which other tables reference THIS table (useful for JOIN hints)
• natural_language_hint — set from table comment if present

Required env vars (or pass cfg dict directly):
  PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD
  PG_SSLMODE       (default: require)
  PG_SSLROOTCERT   (required when sslmode=verify-ca/verify-full)

Optional:
  DB_ALIAS         (default: PG_DATABASE value)
"""

from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Set

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SAWarning
import warnings

warnings.filterwarnings(
    "ignore",
    message="Did not recognize type 'vector' of column 'embedding'",
    category=SAWarning,
)

from .base import BaseConnector, ColumnMeta, ForeignKey, IndexInfo, SchemaDoc

log = logging.getLogger("ingest.pg")

# System schemas that are never business data
_PG_SYSTEM_SCHEMAS = frozenset({"pg_catalog", "information_schema", "pg_toast"})

# Column data-type prefixes where enum collection is pointless or dangerous
_SKIP_ENUM_TYPES = ("bytea", "json", "xml", "text", "varchar", "character varying",
                    "uuid", "inet", "cidr", "macaddr", "tsvector", "bit")

# Max characters in an enum value we store (avoid bloating the embedding text)
_ENUM_VAL_MAXLEN = 60


class PostgreSQLConnector(BaseConnector):
    """
    Connects to a PostgreSQL database and reflects its schema catalog.

    Parameters
    ----------
    cfg : dict
        Must contain PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD,
        PG_SSLMODE, and optionally PG_SSLROOTCERT and DB_ALIAS.
    """

    def __init__(self, cfg: Dict[str, str]) -> None:
        self._cfg    = cfg
        self._alias  = cfg.get("DB_ALIAS") or cfg.get("PG_DATABASE", "postgres")
        url          = self._build_url(cfg)
        self._engine = create_engine(url, pool_pre_ping=True, future=True)
        log.debug(
            "PostgreSQLConnector ready",
            extra={"host": cfg.get("PG_HOST"), "db": cfg.get("PG_DATABASE")},
        )

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def collect(
        self,
        schemas_include:  Optional[List[str]] = None,
        sample_row_limit: int = 3,
        pii_patterns:     Optional[List[str]] = None,
        enum_row_limit:   int = 20,
        mask_values:      bool = True,
    ) -> List[SchemaDoc]:
        pii_patterns = pii_patterns or []
        inspector    = inspect(self._engine)
        t0           = time.time()

        # ---- build reverse-FK map once across the whole DB ----
        reverse_fk_map = self._build_reverse_fk_map(inspector, schemas_include)

        # ---- build row-count map from pg_stat (single query) ----
        row_count_map = self._fetch_row_counts()

        docs: List[SchemaDoc] = []
        all_schemas = inspector.get_schema_names()

        for schema in all_schemas:
            if schema in _PG_SYSTEM_SCHEMAS or schema.startswith("pg_temp"):
                continue
            if schemas_include and schema not in schemas_include:
                continue

            tables = inspector.get_table_names(schema=schema)
            filtered_tables = []
            target_table_name = self._cfg.get("TABLE_NAME") or "schema_embeddings"
            target_schema_name = self._cfg.get("PG_SCHEMA", "public")
            for table in tables:
                if schema == target_schema_name and (table == target_table_name or table.startswith(target_table_name + "_p_")):
                    log.debug("Skipping introspection of the schema embeddings table or partition", extra={"schema": schema, "table": table})
                    continue
                filtered_tables.append(table)

            log.info("Reflecting schema", extra={"schema": schema, "tables": len(filtered_tables)})

            for table in filtered_tables:
                doc = self._reflect_table(
                    inspector, schema, table,
                    sample_row_limit, pii_patterns, enum_row_limit,
                    reverse_fk_map=reverse_fk_map.get(f"{schema}.{table}", []),
                    row_count=row_count_map.get(f"{schema}.{table}"),
                    mask_values=mask_values,
                )
                docs.append(doc)

        elapsed = round((time.time() - t0) * 1000, 1)
        log.info(
            "PostgreSQL collection complete",
            extra={"docs": len(docs), "elapsed_ms": elapsed},
        )
        return docs

    # ------------------------------------------------------------------
    # Private — per-table reflection
    # ------------------------------------------------------------------

    def _reflect_table(
        self,
        inspector,
        schema:           str,
        table:            str,
        sample_row_limit: int,
        pii_patterns:     List[str],
        enum_row_limit:   int,
        reverse_fk_map:   List[str],
        row_count:        Optional[int],
        mask_values:      bool = True,
    ) -> SchemaDoc:

        # ---- primary keys ----
        pk_constraint = inspector.get_pk_constraint(table, schema=schema)
        primary_keys: List[str] = pk_constraint.get("constrained_columns", []) or []

        # ---- unique constraints — collect all uniquely-constrained columns ----
        unique_cols: Set[str] = set()
        try:
            for uc in inspector.get_unique_constraints(table, schema=schema):
                for col in (uc.get("column_names") or []):
                    unique_cols.add(col)
        except Exception:
            pass  # driver may not support this; degrade gracefully

        # ---- columns ----
        columns: List[ColumnMeta] = []
        for col in inspector.get_columns(table, schema=schema):
            col_name = col["name"]
            columns.append(
                ColumnMeta(
                    name        = col_name,
                    data_type   = str(col.get("type", "UNKNOWN")),
                    is_nullable = bool(col.get("nullable", True)),
                    default     = str(col["default"]) if col.get("default") is not None else None,
                    comment     = col.get("comment"),
                    is_pii      = self._is_pii(col_name, pii_patterns),
                    is_unique   = col_name in unique_cols,
                )
            )

        # ---- enum values (low-cardinality, non-PII columns) ----
        if enum_row_limit > 0:
            self._fill_enum_values(schema, table, columns, pii_patterns, enum_row_limit)

        # ---- foreign keys (outgoing) ----
        foreign_keys: List[ForeignKey] = []
        for fk_info in inspector.get_foreign_keys(table, schema=schema):
            from_cols = fk_info.get("constrained_columns") or []
            to_cols   = fk_info.get("referred_columns")    or []
            to_schema = fk_info.get("referred_schema")     or schema
            to_table  = fk_info.get("referred_table")      or ""
            for fc, tc in zip(from_cols, to_cols):
                foreign_keys.append(ForeignKey(
                    from_column = fc,
                    to_schema   = to_schema,
                    to_table    = to_table,
                    to_column   = tc,
                ))

        # ---- table comment ----
        try:
            table_comment = inspector.get_table_comment(table, schema=schema).get("text")
        except Exception:
            table_comment = None

        # ---- indexes ----
        indexes: List[IndexInfo] = []
        try:
            # Add PK as a synthetic IndexInfo
            if primary_keys:
                indexes.append(IndexInfo(
                    name       = f"pk_{table}",
                    columns    = primary_keys,
                    is_unique  = True,
                    is_primary = True,
                ))
            for idx in inspector.get_indexes(table, schema=schema):
                indexes.append(IndexInfo(
                    name      = idx.get("name", ""),
                    columns   = list(idx.get("column_names") or []),
                    is_unique = bool(idx.get("unique", False)),
                ))
        except Exception:
            pass

        # ---- sample rows ----
        sample_rows: List[dict] = []
        if sample_row_limit > 0:
            sample_rows = self._fetch_samples(schema, table, sample_row_limit, pii_patterns, mask_values)

        return SchemaDoc(
            source_type       = "postgresql",
            db_alias          = self._alias,
            schema_name       = schema,
            table_name        = table,
            columns           = columns,
            primary_keys      = primary_keys,
            foreign_keys      = foreign_keys,
            sample_rows       = sample_rows,
            table_comment     = table_comment,
            indexes           = indexes,
            referenced_by     = reverse_fk_map,
            row_count_approx  = row_count,
        )

    # ------------------------------------------------------------------
    # Private — enrichment helpers
    # ------------------------------------------------------------------

    def _fill_enum_values(
        self,
        schema:       str,
        table:        str,
        columns:      List[ColumnMeta],
        pii_patterns: List[str],
        limit:        int,
    ) -> None:
        """
        For each non-PII, non-large-text column: count distinct values.
        If count <= limit, fetch those values and attach to column.enum_values.
        Uses a single multi-column SQL query per table to minimise round-trips.
        """
        candidates = [
            c for c in columns
            if not c.is_pii
            and not any(c.data_type.lower().startswith(t) for t in _SKIP_ENUM_TYPES)
        ]
        if not candidates:
            return

        count_parts = ", ".join(
            f'COUNT(DISTINCT "{c.name}") AS cnt_{i}'
            for i, c in enumerate(candidates)
        )
        count_sql = text(
            f'SELECT {count_parts} FROM "{schema}"."{table}"'
        )
        try:
            with self._engine.connect() as conn:
                row = conn.execute(count_sql).fetchone()
                if row is None:
                    return
                for i, col in enumerate(candidates):
                    cnt = row[i]
                    if cnt is None or int(cnt) > limit:
                        continue
                    # fetch actual distinct values for this column
                    vals_sql = text(
                        f'SELECT DISTINCT "{col.name}" FROM "{schema}"."{table}"'
                        f' WHERE "{col.name}" IS NOT NULL'
                        f' ORDER BY 1 LIMIT :lim'
                    )
                    vals = conn.execute(vals_sql, {"lim": limit}).fetchall()
                    col.enum_values = [
                        str(v[0])[:_ENUM_VAL_MAXLEN]
                        for v in vals
                        if v[0] is not None
                    ]
        except Exception:
            log.debug(
                "Enum value collection failed — skipping",
                extra={"schema": schema, "table": table},
                exc_info=True,
            )

    def _build_reverse_fk_map(
        self,
        inspector,
        schemas_include: Optional[List[str]],
    ) -> Dict[str, List[str]]:
        """
        Build a mapping: target_table_fqn → list of "src_schema.src_table.src_col"
        for every FK in the database (or the included schemas).
        """
        result: Dict[str, List[str]] = {}
        try:
            for schema in inspector.get_schema_names():
                if schema in _PG_SYSTEM_SCHEMAS or schema.startswith("pg_temp"):
                    continue
                if schemas_include and schema not in schemas_include:
                    continue
                target_table_name = self._cfg.get("TABLE_NAME") or "schema_embeddings"
                target_schema_name = self._cfg.get("PG_SCHEMA", "public")
                for table in inspector.get_table_names(schema=schema):
                    if schema == target_schema_name and (table == target_table_name or table.startswith(target_table_name + "_p_")):
                        continue
                    for fk_info in inspector.get_foreign_keys(table, schema=schema):
                        from_cols = fk_info.get("constrained_columns") or []
                        to_cols   = fk_info.get("referred_columns")    or []
                        to_schema = fk_info.get("referred_schema")     or schema
                        to_table  = fk_info.get("referred_table")      or ""
                        target_key = f"{to_schema}.{to_table}"
                        for fc, tc in zip(from_cols, to_cols):
                            ref_str = f"{schema}.{table}.{fc}"
                            result.setdefault(target_key, []).append(ref_str)
        except Exception:
            log.debug("Reverse FK map build failed", exc_info=True)
        return result

    def _fetch_row_counts(self) -> Dict[str, int]:
        """
        Fetch approximate row counts.

        Primary source: ``pg_stat_user_tables.n_live_tup`` — near-instant,
        updated by autovacuum.  Returns 0 on fresh databases before ANALYZE
        has run (A1 — HANDOVER outstanding item).

        Fallback: ``pg_class.reltuples`` — written by the planner during
        CREATE TABLE and refreshed more frequently than n_live_tup on tables
        that have never been VACUUMed.  A value of -1 means "no stats yet";
        those are left at 0.
        """
        sql = text(
            "SELECT s.schemaname, s.relname, s.n_live_tup, c.reltuples "
            "FROM pg_stat_user_tables s "
            "JOIN pg_class c "
            "  ON c.relname   = s.relname "
            "JOIN pg_namespace n "
            "  ON n.oid       = c.relnamespace "
            " AND n.nspname   = s.schemaname"
        )
        result: Dict[str, int] = {}
        try:
            with self._engine.connect() as conn:
                for row in conn.execute(sql):
                    schema, table, n_live, reltuples = row[0], row[1], row[2], row[3]
                    key = f"{schema}.{table}"
                    live = int(n_live) if n_live is not None else 0
                    if live > 0:
                        result[key] = live
                    else:
                        # fallback: reltuples < 0 means no stats at all
                        rel = int(reltuples) if reltuples is not None else -1
                        result[key] = max(rel, 0)
        except Exception:
            log.debug("Row count fetch failed", exc_info=True)
        return result

    def _fetch_samples(
        self,
        schema:       str,
        table:        str,
        limit:        int,
        pii_patterns: List[str],
        mask_values:  bool = True,
    ) -> List[dict]:
        q = text(f'SELECT * FROM "{schema}"."{table}" LIMIT :lim')
        try:
            with self._engine.connect() as conn:
                rows = [dict(r._mapping) for r in conn.execute(q, {"lim": limit})]
            return [self._mask_row(r, pii_patterns, mask_values) for r in rows]
        except Exception:
            log.warning(
                "Sample row fetch failed — skipping",
                extra={"schema": schema, "table": table},
                exc_info=True,
            )
            return []

    # ------------------------------------------------------------------
    # URL builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_url(cfg: Dict[str, str]) -> str:
        host = cfg["PG_HOST"]
        port = cfg.get("PG_PORT", "5432")
        db   = cfg["PG_DATABASE"]
        user = cfg["PG_USER"]
        pw   = cfg["PG_PASSWORD"]
        ssl  = cfg.get("PG_SSLMODE", "require")
        cert = cfg.get("PG_SSLROOTCERT", "")

        url = f"postgresql+psycopg2://{user}:{pw}@{host}:{port}/{db}?sslmode={ssl}"
        if cert:
            url += f"&sslrootcert={cert}"
        return url
