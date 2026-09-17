"""
connectors/db2.py

IBM Db2 connector — extracts schema metadata (tables, columns, PKs, FKs,
sample rows, enum values) directly from the Db2 system catalog views.

Two driver backends are supported, tried in order:

  1. ibm_db / ibm_db_dbi  (preferred — native IBM driver)
       pip install ibm-db
       Works with Db2 on-prem, Db2 on Cloud, and Db2 Warehouse.

  2. jaydebeapi + JDBC     (fallback — useful in environments where the
       native driver cannot be installed, e.g. ARM containers)
       pip install jaydebeapi
       Requires the Db2 JDBC JAR (db2jcc4.jar) on the classpath.

Required env vars (or pass cfg dict directly):
  DB2_HOST        – hostname / IP
  DB2_PORT        – default 50000 (plain) or 50001 (SSL)
  DB2_DATABASE    – database name (catalog name)
  DB2_USER
  DB2_PASSWORD
  DB2_SCHEMA      – comma-separated list of schemas to walk (optional;
                    default: all non-system schemas owned by DB2_USER)
  DB2_SSL         – "true" / "false"  (default: false)
  DB2_SSLCERT     – path to server certificate (.arm / .pem) when SSL=true
  DB2_DRIVER      – "ibm_db" | "jdbc" | "auto"  (default: auto)
  DB2_JDBC_JAR    – path to db2jcc4.jar (required when DRIVER=jdbc)
  DB_ALIAS        – human label stored in OpenSearch (default: DB2_DATABASE)
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseConnector, ColumnMeta, ForeignKey, SchemaDoc

log = logging.getLogger("ingest.db2")

# --------------------------------------------------------------------------
# System schemas that are never business data in Db2
# --------------------------------------------------------------------------
_DB2_SYSTEM_SCHEMAS = frozenset({
    "SYSIBM", "SYSCAT", "SYSSTAT", "SYSPROC", "SYSIBMADM",
    "SYSTOOLS", "NULLID", "SQLJ", "DB2GSE", "SYSFUN",
    "SYSIBMTS",
})


# ==========================================================================
# Driver wrappers
# ==========================================================================

class _IbmDbBackend:
    """Thin wrapper around ibm_db_dbi to provide a DB-API 2 interface."""

    def __init__(self, conn_str: str) -> None:
        import ibm_db_dbi as dbi  # type: ignore
        self._conn = dbi.connect(conn_str, "", "")
        log.debug("ibm_db_dbi connected")

    def execute(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        cur = self._conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall() if cur.description else []
        cur.close()
        return rows

    def columns(self, sql: str, params: Tuple = ()) -> Tuple[List[str], List[Tuple]]:
        cur = self._conn.cursor()
        cur.execute(sql, params)
        cols = [d[0].lower() for d in (cur.description or [])]
        rows = cur.fetchall() if cur.description else []
        cur.close()
        return cols, rows

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass


class _JdbcBackend:
    """Thin wrapper around jaydebeapi."""

    def __init__(self, host: str, port: str, db: str,
                 user: str, pw: str, jar: str, ssl: bool, cert: str) -> None:
        import jaydebeapi  # type: ignore
        url = f"jdbc:db2://{host}:{port}/{db}"
        props: Dict[str, str] = {"user": user, "password": pw}
        if ssl:
            props["sslConnection"] = "true"
            if cert:
                props["sslCertLocation"] = cert
        self._conn = jaydebeapi.connect(
            "com.ibm.db2.jcc.DB2Driver",
            url,
            props,
            jar,
        )
        log.debug("jaydebeapi (JDBC) connected")

    def columns(self, sql: str, params: Tuple = ()) -> Tuple[List[str], List[Tuple]]:
        cur = self._conn.cursor()
        cur.execute(sql, params)
        cols = [d[0].lower() for d in (cur.description or [])]
        rows = cur.fetchall() if cur.description else []
        cur.close()
        return cols, rows

    def execute(self, sql: str, params: Tuple = ()) -> List[Tuple]:
        _, rows = self.columns(sql, params)
        return rows

    def close(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass


# ==========================================================================
# Db2 catalog SQL
# ==========================================================================

# All user tables in a schema (excludes views, system objects, nicknames)
_SQL_TABLES = """
SELECT TABNAME, REMARKS
FROM   SYSCAT.TABLES
WHERE  TABSCHEMA = ?
  AND  TYPE = 'T'
ORDER BY TABNAME
"""

# All columns for a table
_SQL_COLUMNS = """
SELECT
    COLNAME,
    TYPENAME,
    NULLS,
    DEFAULT,
    REMARKS,
    COLNO
FROM SYSCAT.COLUMNS
WHERE TABSCHEMA = ?
  AND TABNAME   = ?
ORDER BY COLNO
"""

# Primary key columns
_SQL_PK = """
SELECT k.COLNAME
FROM   SYSCAT.KEYCOLUSE k
JOIN   SYSCAT.TABCONST  tc
       ON  tc.TABSCHEMA = k.TABSCHEMA
       AND tc.TABNAME   = k.TABNAME
       AND tc.CONSTNAME = k.CONSTNAME
WHERE  k.TABSCHEMA = ?
  AND  k.TABNAME   = ?
  AND  tc.TYPE     = 'P'
ORDER BY k.COLSEQ
"""

# Foreign keys
_SQL_FK = """
SELECT
    r.FK_COLNAMES   AS from_cols,
    r.REFTABSCHEMA  AS to_schema,
    r.REFTABNAME    AS to_table,
    r.PK_COLNAMES   AS to_cols
FROM SYSCAT.REFERENCES r
WHERE r.TABSCHEMA = ?
  AND r.TABNAME   = ?
"""

# Sample rows (Db2 uses FETCH FIRST n ROWS ONLY)
_SQL_SAMPLE = 'SELECT * FROM "{schema}"."{table}" FETCH FIRST {n} ROWS ONLY'

# Distinct values for a single low-cardinality column
_SQL_ENUM_VALUES = (
    'SELECT DISTINCT "{col}" FROM "{schema}"."{table}" '
    'WHERE "{col}" IS NOT NULL '
    'FETCH FIRST {n} ROWS ONLY'
)

# All non-system schemas visible to the current user
_SQL_SCHEMAS = """
SELECT DISTINCT TABSCHEMA
FROM   SYSCAT.TABLES
WHERE  TYPE = 'T'
ORDER BY TABSCHEMA
"""


# ==========================================================================
# Connector
# ==========================================================================

class Db2Connector(BaseConnector):
    """
    Connects to IBM Db2 and returns a list of SchemaDoc objects.

    Parameters
    ----------
    cfg : dict
        Keys: DB2_HOST, DB2_PORT, DB2_DATABASE, DB2_USER, DB2_PASSWORD,
              DB2_SSL, DB2_SSLCERT, DB2_DRIVER, DB2_JDBC_JAR, DB_ALIAS.
    """

    def __init__(self, cfg: Dict[str, str]) -> None:
        self._cfg = cfg
        self._alias = cfg.get("DB_ALIAS") or cfg.get("DB2_DATABASE", "db2")
        self._backend = self._connect(cfg)

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def collect(
        self,
        schemas_include: Optional[List[str]] = None,
        sample_row_limit: int = 3,
        pii_patterns: Optional[List[str]] = None,
        enum_row_limit: int = 20,
        mask_values: bool = True,
    ) -> List[SchemaDoc]:
        pii_patterns = pii_patterns or []
        t0 = time.time()

        # Resolve schemas to walk
        if schemas_include:
            schemas = [s.upper() for s in schemas_include]
        else:
            schemas = self._list_schemas()

        docs: List[SchemaDoc] = []
        for schema in schemas:
            if schema in _DB2_SYSTEM_SCHEMAS:
                log.debug("Skipping system schema", extra={"schema": schema})
                continue

            tables = self._list_tables(schema)
            log.info(
                "Reflecting Db2 schema",
                extra={"schema": schema, "tables": len(tables)},
            )
            for table_name, table_comment in tables:
                doc = self._reflect_table(
                    schema, table_name, table_comment,
                    sample_row_limit, pii_patterns, enum_row_limit,
                    mask_values=mask_values,
                )
                docs.append(doc)

        elapsed = round((time.time() - t0) * 1000, 1)
        log.info(
            "Db2 collection complete",
            extra={"docs": len(docs), "elapsed_ms": elapsed},
        )
        return docs

    def close(self) -> None:
        try:
            self._backend.close()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Private — catalog queries
    # ------------------------------------------------------------------

    def _list_schemas(self) -> List[str]:
        rows = self._backend.execute(_SQL_SCHEMAS)
        result = [r[0].strip() for r in rows if r[0].strip() not in _DB2_SYSTEM_SCHEMAS]
        log.debug("Db2 schemas discovered", extra={"count": len(result)})
        return result

    def _list_tables(self, schema: str) -> List[Tuple[str, Optional[str]]]:
        rows = self._backend.execute(_SQL_TABLES, (schema,))
        # rows: (TABNAME, REMARKS)
        return [(r[0].strip(), (r[1] or "").strip() or None) for r in rows]

    def _reflect_table(
        self,
        schema: str,
        table: str,
        table_comment: Optional[str],
        sample_row_limit: int,
        pii_patterns: List[str],
        enum_row_limit: int = 20,
        mask_values: bool = True,
    ) -> SchemaDoc:
        columns   = self._get_columns(schema, table, pii_patterns)
        pks       = self._get_pks(schema, table)
        fks       = self._get_fks(schema, table)
        samples   = self._get_samples(schema, table, sample_row_limit, pii_patterns, mask_values) \
                    if sample_row_limit > 0 else []

        # Populate enum_values for low-cardinality non-PII columns
        if enum_row_limit > 0:
            self._populate_enum_values(schema, table, columns, enum_row_limit, pii_patterns)

        return SchemaDoc(
            source_type="db2",
            db_alias=self._alias,
            schema_name=schema,
            table_name=table,
            columns=columns,
            primary_keys=pks,
            foreign_keys=fks,
            sample_rows=samples,
            table_comment=table_comment,
        )

    def _get_columns(
        self, schema: str, table: str, pii_patterns: List[str],
    ) -> List[ColumnMeta]:
        col_headers, rows = self._backend.columns(_SQL_COLUMNS, (schema, table))
        idx = {h: i for i, h in enumerate(col_headers)}

        result: List[ColumnMeta] = []
        for row in rows:
            name     = (row[idx["colname"]] or "").strip()
            dtype    = (row[idx["typename"]] or "").strip()
            nullable = (row[idx["nulls"]] or "Y") == "Y"
            default  = (row[idx["default"]] or "").strip() or None
            comment  = (row[idx["remarks"]] or "").strip() or None
            result.append(ColumnMeta(
                name=name,
                data_type=dtype,
                is_nullable=nullable,
                default=default,
                comment=comment,
                is_pii=self._is_pii(name, pii_patterns),
            ))
        return result

    def _get_pks(self, schema: str, table: str) -> List[str]:
        rows = self._backend.execute(_SQL_PK, (schema, table))
        return [(r[0] or "").strip() for r in rows]

    def _get_fks(self, schema: str, table: str) -> List[ForeignKey]:
        """
        Db2 stores FK/PK column lists as space-padded strings in
        SYSCAT.REFERENCES.  We zip them pairwise.
        """
        col_headers, rows = self._backend.columns(_SQL_FK, (schema, table))
        idx = {h: i for i, h in enumerate(col_headers)}
        result: List[ForeignKey] = []
        for row in rows:
            from_raw = (row[idx["from_cols"]] or "").split()
            to_raw   = (row[idx["to_cols"]]   or "").split()
            to_schema = (row[idx["to_schema"]] or schema).strip()
            to_table  = (row[idx["to_table"]]  or "").strip()
            for fc, tc in zip(from_raw, to_raw):
                result.append(ForeignKey(
                    from_column=fc.strip(),
                    to_schema=to_schema,
                    to_table=to_table,
                    to_column=tc.strip(),
                ))
        return result

    def _get_samples(
        self,
        schema: str, table: str,
        limit: int, pii_patterns: List[str],
        mask_values: bool = True,
    ) -> List[dict]:
        sql = _SQL_SAMPLE.format(schema=schema, table=table, n=limit)
        try:
            col_headers, rows = self._backend.columns(sql)
            dicts = [dict(zip(col_headers, r)) for r in rows]
            return [self._mask_row(d, pii_patterns, mask_values) for d in dicts]
        except Exception:
            log.warning(
                "Db2 sample fetch failed — skipping",
                extra={"schema": schema, "table": table},
                exc_info=True,
            )
            return []

    def _populate_enum_values(
        self,
        schema: str,
        table: str,
        columns: List,
        enum_row_limit: int,
        pii_patterns: List[str],
    ) -> None:
        """
        Collect distinct values for low-cardinality columns using SYSCAT.COLUMNS
        statistics to identify candidates (HIGH2KEY - LOW2KEY heuristic), then
        query actual distinct values.

        Only non-PII columns where SYSCAT reports COLCARD <= enum_row_limit are
        queried.  COLCARD = -1 means stats are stale / unavailable; those columns
        are skipped to avoid expensive full-scans.
        """
        # Fetch COLCARD (estimated cardinality) for all columns in one catalog query
        cardinality_sql = """
        SELECT COLNAME, COLCARD
        FROM   SYSCAT.COLUMNS
        WHERE  TABSCHEMA = ?
          AND  TABNAME   = ?
          AND  COLCARD   > 0
          AND  COLCARD  <= ?
        """
        try:
            rows = self._backend.execute(cardinality_sql, (schema, table, enum_row_limit))
        except Exception:
            log.debug(
                "Could not read SYSCAT.COLUMNS cardinality — skipping enum collection",
                extra={"schema": schema, "table": table},
                exc_info=True,
            )
            return

        # A4 — warn when COLCARD returned no usable rows for this table.
        # This typically means RUNSTATS has not been run or stats are stale
        # (COLCARD = -1 for all columns).  The WHERE COLCARD > 0 filter above
        # excludes those columns, so rows will be empty.
        if not rows:
            log.warning(
                "Db2 SYSCAT.COLUMNS has no positive COLCARD entries for this table — "
                "enum collection skipped.  Run RUNSTATS to populate statistics.",
                extra={"schema": schema, "table": table},
            )
            return

        # Build a map: col_name_upper → ColumnMeta
        col_map = {c.name.upper(): c for c in columns}

        for row in rows:
            col_name = (row[0] or "").strip()
            col_upper = col_name.upper()

            # Skip PII columns
            if self._is_pii(col_name, pii_patterns):
                continue

            col_meta = col_map.get(col_upper)
            if col_meta is None:
                continue

            sql = _SQL_ENUM_VALUES.format(
                schema=schema, table=table, col=col_name, n=enum_row_limit
            )
            try:
                value_rows = self._backend.execute(sql)
                col_meta.enum_values = [
                    str(r[0]) for r in value_rows if r[0] is not None
                ]
                log.debug(
                    "Db2 enum values collected",
                    extra={"schema": schema, "table": table,
                           "col": col_name, "count": len(col_meta.enum_values)},
                )
            except Exception:
                log.debug(
                    "Db2 enum value fetch failed — skipping column",
                    extra={"schema": schema, "table": table, "col": col_name},
                    exc_info=True,
                )

    # ------------------------------------------------------------------
    # Private — driver selection
    # ------------------------------------------------------------------

    @staticmethod
    def _connect(cfg: Dict[str, str]):
        driver = cfg.get("DB2_DRIVER", "auto").lower()
        host   = cfg["DB2_HOST"]
        port   = cfg.get("DB2_PORT", "50000")
        db     = cfg["DB2_DATABASE"]
        user   = cfg["DB2_USER"]
        pw     = cfg["DB2_PASSWORD"]
        ssl    = cfg.get("DB2_SSL", "false").lower() in ("1", "true", "yes")
        cert   = cfg.get("DB2_SSLCERT", "")
        jar    = cfg.get("DB2_JDBC_JAR", "")

        if driver in ("auto", "ibm_db"):
            try:
                return _IbmDbBackend(
                    Db2Connector._build_ibm_db_str(host, port, db, user, pw, ssl, cert)
                )
            except ImportError:
                if driver == "ibm_db":
                    raise RuntimeError(
                        "ibm-db not installed. Run: pip install ibm-db"
                    )
                log.info("ibm_db not available, falling back to JDBC")

        # JDBC fallback
        if not jar:
            raise RuntimeError(
                "DB2_JDBC_JAR must point to db2jcc4.jar when using JDBC driver. "
                "Download from: https://www.ibm.com/support/pages/db2-jdbc-driver-versions-and-downloads"
            )
        if not os.path.isfile(jar):
            raise FileNotFoundError(f"Db2 JDBC JAR not found: {jar}")

        try:
            return _JdbcBackend(host, port, db, user, pw, jar, ssl, cert)
        except ImportError:
            raise RuntimeError(
                "jaydebeapi not installed. Run: pip install jaydebeapi"
            )

    @staticmethod
    def _build_ibm_db_str(
        host: str, port: str, db: str,
        user: str, pw: str, ssl: bool, cert: str,
    ) -> str:
        parts = [
            f"DATABASE={db}",
            f"HOSTNAME={host}",
            f"PORT={port}",
            f"PROTOCOL=TCPIP",
            f"UID={user}",
            f"PWD={pw}",
        ]
        if ssl:
            parts.append("Security=SSL")
            if cert:
                parts.append(f"SSLServerCertificate={cert}")
        return ";".join(parts) + ";"


# ==========================================================================
# Factory helper — build from environment variables
# ==========================================================================

def db2_connector_from_env() -> Db2Connector:
    """
    Convenience factory that reads all DB2_* variables from the environment.
    """
    required = ["DB2_HOST", "DB2_DATABASE", "DB2_USER", "DB2_PASSWORD"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required Db2 env vars: {missing}")

    cfg = {
        "DB2_HOST":      os.environ["DB2_HOST"],
        "DB2_PORT":      os.getenv("DB2_PORT", "50000"),
        "DB2_DATABASE":  os.environ["DB2_DATABASE"],
        "DB2_USER":      os.environ["DB2_USER"],
        "DB2_PASSWORD":  os.environ["DB2_PASSWORD"],
        "DB2_SSL":       os.getenv("DB2_SSL", "false"),
        "DB2_SSLCERT":   os.getenv("DB2_SSLCERT", ""),
        "DB2_DRIVER":    os.getenv("DB2_DRIVER", "auto"),
        "DB2_JDBC_JAR":  os.getenv("DB2_JDBC_JAR", ""),
        "DB_ALIAS":      os.getenv("DB_ALIAS", os.environ["DB2_DATABASE"]),
    }
    return Db2Connector(cfg)
