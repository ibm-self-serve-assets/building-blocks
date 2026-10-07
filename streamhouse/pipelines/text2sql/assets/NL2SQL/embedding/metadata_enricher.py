"""
metadata_enricher.py

Provides metadata enrichment loading and application for SchemaDoc objects (and raw schema dicts).
Enables enhancing table descriptions, column comments, business aliases, enum values,
and natural language purpose hints from external files (JSON, YAML, Markdown).

Format specifications:
-----------------------
1. JSON / YAML format:
{
  "tables": [
    {
      "table": "claim",                  # or "claims_db.public.claim" or "public.claim"
      "schema": "public",                # optional if qualified in table
      "db_alias": "claims_db",           # optional
      "description": "Primary insurance claims table containing claim lifecycle status and payout values.",
      "purpose": "Use this table for claim amount totals, claim status tracking, and claim dates.",
      "columns": [
        {
          "name": "clm_amt",
          "comment": "Total claimed monetary loss in USD before deductible calculation.",
          "enum_values": ["PENDING", "APPROVED", "REJECTED"]  # optional
        }
      ]
    }
  ]
}

2. Markdown format:
# Schema Metadata

## Table: public.claim
**Description**: Primary insurance claims table containing claim lifecycle status and payout values.
**Purpose**: Use this table for claim amount totals, claim status tracking, and claim dates.

### Columns
| Column | Description | Values |
| --- | --- | --- |
| clm_amt | Total claimed monetary loss in USD before deductible calculation. | |
| clm_stat | Claim settlement state | 'OPEN', 'SETTLED', 'CLOSED' |
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

log = logging.getLogger("enricher")


@dataclass
class ColumnEnrichment:
    name: str
    comment: Optional[str] = None
    enum_values: List[str] = field(default_factory=list)


@dataclass
class TableEnrichment:
    table_name: str
    schema_name: Optional[str] = None
    db_alias: Optional[str] = None
    table_comment: Optional[str] = None
    natural_language_hint: Optional[str] = None
    columns: Dict[str, ColumnEnrichment] = field(default_factory=dict)


class MetadataEnricher:
    """
    Loads external metadata descriptions from JSON, YAML, or Markdown files
    and enriches SchemaDoc or raw dictionary schema definitions.
    """

    def __init__(self, file_path: Optional[str] = None, enabled: bool = True) -> None:
        self.enabled = enabled
        self.file_path = file_path
        self.enrichments: Dict[str, TableEnrichment] = {}
        if self.enabled and self.file_path:
            self.load(self.file_path)

    @classmethod
    def from_env(cls, env: Optional[Dict[str, str]] = None) -> "MetadataEnricher":
        """Factory method that initializes MetadataEnricher from environment variables."""
        cfg = env if env is not None else os.environ
        enabled = str(cfg.get("METADATA_ENRICHMENT_ENABLED", "true")).lower() in ("1", "true", "yes")
        file_path = cfg.get("METADATA_ENRICHMENT_FILE") or cfg.get("SCHEMA_METADATA_FILE")
        if not file_path:
            # Check default locations
            default_locations = [
                "metadata/schema_metadata.yaml",
                "metadata/schema_metadata.yml",
                "metadata/schema_metadata.json",
                "metadata/schema_metadata.md",
                "schema_metadata.yaml",
                "schema_metadata.yml",
                "schema_metadata.json",
                "schema_metadata.md",
            ]
            for loc in default_locations:
                # check relative to current dir or NL2SQL root
                if os.path.exists(loc):
                    file_path = loc
                    break
        return cls(file_path=file_path, enabled=enabled)

    def load(self, file_path: str) -> None:
        """Loads metadata enrichment definitions from a file."""
        if not os.path.exists(file_path):
            log.warning(f"Metadata enrichment file not found: {file_path}")
            return

        try:
            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if ext in (".yaml", ".yml"):
                self._parse_yaml(content)
            elif ext == ".json":
                self._parse_json(content)
            elif ext in (".md", ".markdown", ".txt"):
                self._parse_markdown(content)
            else:
                # Try json first, then yaml, then markdown
                try:
                    self._parse_json(content)
                except Exception:
                    try:
                        self._parse_yaml(content)
                    except Exception:
                        self._parse_markdown(content)

            log.info(f"Loaded metadata enrichments for {len(self.enrichments)} table definitions from {file_path}")
        except Exception as exc:
            log.exception(f"Failed to load metadata enrichment from {file_path}: {exc}")

    def _register_enrichment(self, item: TableEnrichment) -> None:
        """Register table enrichment under multiple lookup keys for flexible matching."""
        tbl = (item.table_name or "").lower().strip()
        sch = (item.schema_name or "").lower().strip()
        alias = (item.db_alias or "").lower().strip()

        # Primary key: table_name alone
        if tbl:
            self.enrichments[tbl] = item
        # Schema qualified key: schema.table
        if sch and tbl:
            self.enrichments[f"{sch}.{tbl}"] = item
        # Fully qualified key: alias.schema.table
        if alias and sch and tbl:
            self.enrichments[f"{alias}.{sch}.{tbl}"] = item

    def _parse_json(self, content: str) -> None:
        data = json.loads(content)
        self._load_from_dict(data)

    def _parse_yaml(self, content: str) -> None:
        try:
            import yaml
            data = yaml.safe_load(content)
            self._load_from_dict(data)
        except ImportError:
            # Fallback simple parser if PyYAML is not installed
            log.warning("PyYAML not installed, attempting JSON parse for YAML content")
            self._parse_json(content)

    def _load_from_dict(self, data: Any) -> None:
        if not isinstance(data, dict):
            return

        tables = data.get("tables", [])
        if isinstance(tables, dict):
            # Dict mapping table_name -> table_data
            for t_name, t_meta in tables.items():
                if isinstance(t_meta, dict):
                    t_meta["table"] = t_name
                    self._process_table_dict(t_meta)
        elif isinstance(tables, list):
            for t_meta in tables:
                if isinstance(t_meta, dict):
                    self._process_table_dict(t_meta)

    def _process_table_dict(self, t_meta: dict) -> None:
        table_raw = t_meta.get("table") or t_meta.get("table_name") or ""
        parts = table_raw.split(".")
        db_alias = t_meta.get("db_alias")
        schema_name = t_meta.get("schema") or t_meta.get("schema_name")
        table_name = table_raw

        if len(parts) == 3:
            db_alias, schema_name, table_name = parts
        elif len(parts) == 2:
            schema_name, table_name = parts

        cols_dict: Dict[str, ColumnEnrichment] = {}
        cols_raw = t_meta.get("columns", [])
        if isinstance(cols_raw, list):
            for c in cols_raw:
                if isinstance(c, dict) and "name" in c:
                    c_name = c["name"]
                    c_comment = c.get("comment") or c.get("description")
                    c_enums = c.get("enum_values") or c.get("values") or []
                    if isinstance(c_enums, str):
                        c_enums = [x.strip().strip("'\"") for x in c_enums.split(",") if x.strip()]
                    cols_dict[c_name.lower()] = ColumnEnrichment(
                        name=c_name,
                        comment=c_comment,
                        enum_values=c_enums,
                    )
        elif isinstance(cols_raw, dict):
            for c_name, c_desc in cols_raw.items():
                if isinstance(c_desc, dict):
                    cols_dict[c_name.lower()] = ColumnEnrichment(
                        name=c_name,
                        comment=c_desc.get("comment") or c_desc.get("description"),
                        enum_values=c_desc.get("enum_values", []),
                    )
                else:
                    cols_dict[c_name.lower()] = ColumnEnrichment(
                        name=c_name,
                        comment=str(c_desc) if c_desc else None,
                    )

        enrichment = TableEnrichment(
            table_name=table_name,
            schema_name=schema_name,
            db_alias=db_alias,
            table_comment=t_meta.get("description") or t_meta.get("table_comment"),
            natural_language_hint=t_meta.get("purpose") or t_meta.get("natural_language_hint"),
            columns=cols_dict,
        )
        self._register_enrichment(enrichment)

    def _parse_markdown(self, content: str) -> None:
        """
        Parses Markdown formatted schema metadata.
        Looks for `## Table: [schema.]table` or `## [schema.]table` sections.
        """
        lines = content.splitlines()
        current_table: Optional[TableEnrichment] = None
        in_columns_table = False
        col_headers: List[str] = []

        for line in lines:
            line_str = line.strip()

            # Heading 2 or 3 defining table
            table_match = re.match(r"^#{2,3}\s+(?:Table:\s*)?([a-zA-Z0-9_.]+)", line_str, re.IGNORECASE)
            if table_match and not line_str.lower().startswith("### column"):
                if current_table:
                    self._register_enrichment(current_table)
                t_raw = table_match.group(1).strip()
                parts = t_raw.split(".")
                schema_name = None
                table_name = t_raw
                if len(parts) == 2:
                    schema_name, table_name = parts
                elif len(parts) == 3:
                    _, schema_name, table_name = parts

                current_table = TableEnrichment(
                    table_name=table_name,
                    schema_name=schema_name,
                )
                in_columns_table = False
                continue

            if not current_table:
                continue

            # Description
            desc_match = re.match(r"^\*{0,2}Description\*{0,2}:\s*(.+)$", line_str, re.IGNORECASE)
            if desc_match:
                current_table.table_comment = desc_match.group(1).strip()
                continue

            # Purpose / Natural language hint
            purpose_match = re.match(r"^\*{0,2}Purpose\*{0,2}:\s*(.+)$", line_str, re.IGNORECASE)
            if purpose_match:
                current_table.natural_language_hint = purpose_match.group(1).strip()
                continue

            # Columns section start
            if re.match(r"^#{3,4}\s+Columns", line_str, re.IGNORECASE):
                in_columns_table = True
                col_headers = []
                continue

            # Markdown column table row
            if in_columns_table and line_str.startswith("|"):
                cells = [c.strip() for c in line_str.split("|")[1:-1]]
                if not cells or all(c.startswith("-") for c in cells):
                    continue
                if not col_headers:
                    col_headers = [c.lower() for c in cells]
                    continue
                # Map row
                row_map = {col_headers[i]: cells[i] for i in range(min(len(col_headers), len(cells)))}
                col_name = row_map.get("column") or row_map.get("name") or row_map.get("col") or (cells[0] if cells else "")
                if col_name:
                    col_desc = row_map.get("description") or row_map.get("comment") or (cells[1] if len(cells) > 1 else None)
                    col_vals_raw = row_map.get("values") or row_map.get("enum_values") or (cells[2] if len(cells) > 2 else "")
                    enum_vals = []
                    if col_vals_raw:
                        enum_vals = [v.strip().strip("'\"") for v in col_vals_raw.split(",") if v.strip()]

                    current_table.columns[col_name.lower()] = ColumnEnrichment(
                        name=col_name,
                        comment=col_desc if col_desc else None,
                        enum_values=enum_vals,
                    )

        if current_table:
            self._register_enrichment(current_table)

    def find_enrichment(
        self,
        table_name: str,
        schema_name: Optional[str] = None,
        db_alias: Optional[str] = None,
    ) -> Optional[TableEnrichment]:
        """Finds matching TableEnrichment by trying most-specific to least-specific key."""
        tbl = (table_name or "").lower().strip()
        sch = (schema_name or "").lower().strip()
        alias = (db_alias or "").lower().strip()

        if alias and sch and tbl:
            k = f"{alias}.{sch}.{tbl}"
            if k in self.enrichments:
                return self.enrichments[k]

        if sch and tbl:
            k = f"{sch}.{tbl}"
            if k in self.enrichments:
                return self.enrichments[k]

        if tbl in self.enrichments:
            return self.enrichments[tbl]

        return None

    def enrich_schema_doc(self, doc: Any) -> None:
        """
        Applies metadata enrichment in-place to a SchemaDoc instance.
        """
        if not self.enabled:
            return

        match = self.find_enrichment(
            table_name=doc.table_name,
            schema_name=doc.schema_name,
            db_alias=getattr(doc, "db_alias", None),
        )
        if not match:
            return

        if match.natural_language_hint:
            doc.natural_language_hint = match.natural_language_hint
        if match.table_comment:
            doc.table_comment = match.table_comment

        # Enrich columns
        if hasattr(doc, "columns") and isinstance(doc.columns, list):
            for col in doc.columns:
                c_name = getattr(col, "name", "").lower()
                if c_name in match.columns:
                    col_meta = match.columns[c_name]
                    if col_meta.comment:
                        col.comment = col_meta.comment
                    if col_meta.enum_values and hasattr(col, "enum_values"):
                        col.enum_values = col_meta.enum_values

    def enrich_schema_dict(
        self,
        schema_name: str,
        table_name: str,
        columns: List[Dict[str, Any]],
        table_comment: Optional[str] = None,
        natural_language_hint: Optional[str] = None,
    ) -> tuple[Optional[str], Optional[str], List[Dict[str, Any]]]:
        """
        Applies metadata enrichment to raw dictionary structures (used e.g. in pgvector ingestion).
        Returns (updated_table_comment, updated_natural_language_hint, updated_columns).
        """
        if not self.enabled:
            return table_comment, natural_language_hint, columns

        match = self.find_enrichment(table_name=table_name, schema_name=schema_name)
        if not match:
            return table_comment, natural_language_hint, columns

        if match.natural_language_hint:
            natural_language_hint = match.natural_language_hint
        if match.table_comment:
            table_comment = match.table_comment

        enriched_cols = []
        for col in columns:
            col_copy = dict(col)
            c_name = col_copy.get("name", "").lower()
            if c_name in match.columns:
                col_meta = match.columns[c_name]
                if col_meta.comment:
                    col_copy["description"] = col_meta.comment
                    col_copy["comment"] = col_meta.comment
                if col_meta.enum_values:
                    col_copy["enum_values"] = col_meta.enum_values
            enriched_cols.append(col_copy)

        return table_comment, natural_language_hint, enriched_cols
