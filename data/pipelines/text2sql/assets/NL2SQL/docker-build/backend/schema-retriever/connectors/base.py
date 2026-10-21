"""
connectors/base.py

Abstract base class that every database connector must implement.
Each connector's job is to produce a list of SchemaDoc objects — one per table —
by reading the live database catalog (not a static DDL file).

Enrichment additions over the original
---------------------------------------
• column_count, row_count_approx  — size signals for ranking
• indexes                         — index names + covered columns (improves WHERE/JOIN hints)
• unique_columns                  — columns with UNIQUE constraint (useful for JOIN keys)
• enum_values                     — distinct values for low-cardinality columns (<= 20 values)
• referenced_by                   — reverse FK: which tables point TO this table
• natural_language_hint           — optional free-text business description (from DB comment
                                    or manually supplied); added verbatim to to_text()
• to_text() now generates a richer embedding text with all the above fields included
• _mask_row() now applies regex-pattern masking for common sensitive value shapes
  (email addresses, phone numbers, IP addresses, credit card numbers) regardless
  of whether the column name matches a PII pattern.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ColumnMeta:
    name:        str
    data_type:   str
    is_nullable: bool = True
    default:     Optional[str] = None
    comment:     Optional[str] = None
    is_pii:      bool = False
    # enrichment
    is_unique:   bool = False               # column has UNIQUE constraint
    enum_values: List[str] = field(default_factory=list)  # top distinct values

    def to_dict(self) -> dict:
        """
        Serialise this column for storage in OpenSearch / API responses.

        A3 — the ``is_pii`` classification flag is intentionally excluded:
        it is an internal ingestion concern and should not be visible in
        stored index documents or API responses (avoids leaking which columns
        were flagged, which could itself be considered sensitive metadata).
        """
        return {
            "name":        self.name,
            "data_type":   self.data_type,
            "is_nullable": self.is_nullable,
            "default":     self.default,
            "comment":     self.comment,
            "is_unique":   self.is_unique,
            "enum_values": self.enum_values,
        }


@dataclass
class ForeignKey:
    from_column: str
    to_schema:   str
    to_table:    str
    to_column:   str


@dataclass
class IndexInfo:
    """One index on a table (may cover multiple columns)."""
    name:       str
    columns:    List[str]
    is_unique:  bool = False
    is_primary: bool = False


@dataclass
class SchemaDoc:
    """
    One document per database table, ready to embed and index.

    Enrichment fields are optional — connectors fill what their catalog
    supports.  Missing fields degrade gracefully (omitted from to_text).
    """
    # ---- core (always populated) ----
    source_type:   str          # "postgresql" | "db2"
    db_alias:      str          # human label, e.g. "claims_db"
    schema_name:   str
    table_name:    str
    columns:       List[ColumnMeta]    = field(default_factory=list)
    primary_keys:  List[str]           = field(default_factory=list)
    foreign_keys:  List[ForeignKey]    = field(default_factory=list)
    sample_rows:   List[dict]          = field(default_factory=list)
    table_comment: Optional[str]       = None

    # ---- enrichment ----
    indexes:              List[IndexInfo] = field(default_factory=list)
    referenced_by:        List[str]       = field(default_factory=list)  # "schema.table.col"
    row_count_approx:     Optional[int]   = None   # from pg_stat / SYSCAT stats
    natural_language_hint: Optional[str]  = None   # free-text override for embedding

    # ---- derived ----
    @property
    def table_id(self) -> str:
        return f"{self.db_alias}.{self.schema_name}.{self.table_name}"

    @property
    def column_count(self) -> int:
        return len(self.columns)

    def to_text(self, max_chars: int = 6000) -> str:
        """
        Build the human-readable text blob that will be embedded.

        Design principles
        -----------------
        1. Every fact that could help an LLM write correct SQL is included.
        2. Plain English labels are used so the embedding model can match
           natural-language queries (e.g. "customer orders" → order_items table).
        3. The most discriminative facts (table name, comment, column names)
           appear early so they dominate the embedding even if the text is
           truncated to max_chars.
        4. PII columns are flagged so the LLM can avoid selecting them
           unless explicitly asked.
        5. Enum values for low-cardinality columns let the LLM write
           correct WHERE clauses (e.g. status = 'ACTIVE').
        6. Reverse FKs tell the LLM which tables JOIN to this one,
           enabling correct JOIN chain suggestions.
        """
        lines: List[str] = []

        # --- header ---
        lines.append(f"Table: {self.schema_name}.{self.table_name}")
        lines.append(f"Database: {self.db_alias} ({self.source_type})")

        if self.natural_language_hint:
            lines.append(f"Purpose: {self.natural_language_hint}")
        elif self.table_comment:
            lines.append(f"Description: {self.table_comment}")

        if self.row_count_approx is not None:
            lines.append(f"Approximate row count: {self.row_count_approx:,}")

        lines.append(f"Column count: {self.column_count}")

        # --- primary key ---
        pk_str = ", ".join(self.primary_keys) if self.primary_keys else "none"
        lines.append(f"Primary key: {pk_str}")

        # --- columns ---
        lines.append("Columns:")
        for c in self.columns:
            nullable_tag = "" if c.is_nullable else " NOT NULL"
            pii_tag      = " [PII - do not expose]" if c.is_pii else ""
            unique_tag   = " [UNIQUE]" if c.is_unique else ""
            pk_tag       = " [PK]" if c.name in self.primary_keys else ""
            comment_str  = f" -- {c.comment}" if c.comment else ""
            enum_str     = ""
            if c.enum_values:
                vals = ", ".join(repr(v) for v in c.enum_values[:20])
                enum_str = f" [values: {vals}]"
            lines.append(
                f"  {c.name} {c.data_type}{nullable_tag}"
                f"{pk_tag}{unique_tag}{pii_tag}{enum_str}{comment_str}"
            )

        # --- foreign keys (outgoing) ---
        if self.foreign_keys:
            lines.append("Foreign keys (this table → other tables):")
            for fk in self.foreign_keys:
                lines.append(
                    f"  {fk.from_column} → {fk.to_schema}.{fk.to_table}.{fk.to_column}"
                )

        # --- reverse foreign keys (incoming) ---
        if self.referenced_by:
            lines.append("Referenced by (other tables → this table):")
            for ref in self.referenced_by:
                lines.append(f"  ← {ref}")

        # --- indexes ---
        non_pk_indexes = [
            idx for idx in self.indexes
            if not idx.is_primary and idx.columns
        ]
        if non_pk_indexes:
            lines.append("Indexes:")
            for idx in non_pk_indexes:
                uniq_tag = " UNIQUE" if idx.is_unique else ""
                cols     = ", ".join(idx.columns)
                lines.append(f"  {idx.name}{uniq_tag} on ({cols})")

        # --- sample rows ---
        if self.sample_rows:
            lines.append("Sample rows:")
            for row in self.sample_rows[:3]:
                parts = ", ".join(f"{k}: {repr(v)}" for k, v in row.items())
                lines.append(f"  {{{parts}}}")

        text = "\n".join(lines)
        return text[:max_chars] if len(text) > max_chars else text


# ---------------------------------------------------------------------------
# Abstract connector
# ---------------------------------------------------------------------------

class BaseConnector(ABC):
    """
    Subclass this for each source database type.
    The only public method is `collect()`.
    """

    @abstractmethod
    def collect(
        self,
        schemas_include:  Optional[List[str]] = None,
        sample_row_limit: int = 3,
        pii_patterns:     Optional[List[str]] = None,
        enum_row_limit:   int = 20,
        mask_values:      bool = True,
    ) -> List[SchemaDoc]:
        """
        Introspect the database and return one SchemaDoc per table.

        Parameters
        ----------
        schemas_include   : if given, only these schema names are walked
        sample_row_limit  : max rows to fetch per table (0 = skip)
        pii_patterns      : column name substrings that flag PII; pass an
                            empty list to disable column-name masking
        enum_row_limit    : max distinct values to collect for low-cardinality
                            columns (0 = skip enum collection)
        mask_values       : when True (default), the regex value-pattern pass
                            runs on sample rows regardless of column name —
                            masking emails, phones, IPs and card numbers.
                            Set False to disable all value-level masking.
        """

    # ------ helpers available to all subclasses ------

    @staticmethod
    def _is_pii(col_name: str, patterns: List[str]) -> bool:
        lower = (col_name or "").lower()
        return any(p in lower for p in patterns)

    # Regex patterns that detect sensitive *values* regardless of column name.
    # These complement the column-name-based PII flag for sample row masking.
    _VALUE_PATTERNS: List[tuple] = [
        # Email address (match before phone to avoid @-domain being phone-scanned)
        (re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"), "<email>"),
        # IPv4 address — must come before phone pattern (dots-and-digits overlap)
        (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<ip>"),
        # Credit / debit card: 13–19 consecutive digits (may be space/dash separated)
        (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "<card>"),
        # Phone number: loose match covers +1-800-555-0100, (800) 555-0100, etc.
        # Applied last so more-specific patterns (IP, card) take precedence.
        (re.compile(r"(\+?\d[\d\s\-().]{7,}\d)"), "<phone>"),
    ]

    @classmethod
    def _mask_row(
        cls,
        row: dict,
        patterns: List[str],
        mask_values: bool = True,
    ) -> dict:
        """
        Mask PII in a sample row.

        Pass 1 — Column-name masking (controlled by ``patterns``):
            Any column whose name contains a pattern substring (e.g. 'email',
            'phone') has its value replaced with ``[MASKED]``.
            Disabled by passing an empty ``patterns`` list.

        Pass 2 — Regex value masking (controlled by ``mask_values``):
            Values that *look like* sensitive data are substituted regardless
            of column name: email addresses → ``<email>``, phone numbers →
            ``<phone>``, IPv4 addresses → ``<ip>``, card numbers → ``<card>``.
            Disabled by setting ``mask_values=False``.
        """
        masked: dict = {}
        for k, v in row.items():
            # Pass 1 — column name match
            if patterns and any(p in k.lower() for p in patterns) and v is not None:
                masked[k] = "[MASKED]"
                continue
            # Pass 2 — regex value scan (only when enabled and value is a non-empty string)
            if mask_values and isinstance(v, str) and v:
                replacement = v
                for pattern, label in cls._VALUE_PATTERNS:
                    if pattern.search(replacement):
                        replacement = pattern.sub(label, replacement)
                masked[k] = replacement
            else:
                masked[k] = v
        return masked
