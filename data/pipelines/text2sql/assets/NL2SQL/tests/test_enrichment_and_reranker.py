"""
test_enrichment_and_reranker.py

Unit tests for:
1. MetadataEnricher (Markdown, JSON, YAML loading and enrichment application)
2. SchemaDoc enrichment integration
3. Re-Ranker component (NoOpReranker, CrossEncoder fallback & scoring, factory)
"""

import json
import os
import sys
import tempfile
import pytest

# Ensure paths are accessible
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "embedding"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend", "schema_retriever"))

from metadata_enricher import MetadataEnricher, TableEnrichment, ColumnEnrichment
from connectors.base import SchemaDoc, ColumnMeta
from reranker import BaseReranker, NoOpReranker, CrossEncoderReranker, FlashRankReranker, build_reranker, _sigmoid


# ===========================================================================
# Metadata Enricher Tests
# ===========================================================================

def test_metadata_enricher_json_parsing():
    json_data = {
        "tables": [
            {
                "table": "claims_db.public.claim",
                "description": "Primary insurance claims table",
                "purpose": "Query claim totals and status",
                "columns": [
                    {
                        "name": "clm_amt",
                        "comment": "Total claimed monetary loss",
                        "enum_values": ["100", "200"]
                    }
                ]
            }
        ]
    }
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(json_data, f)
        temp_path = f.name

    try:
        enricher = MetadataEnricher(file_path=temp_path, enabled=True)
        assert len(enricher.enrichments) > 0

        # Check lookup
        match = enricher.find_enrichment("claim", "public", "claims_db")
        assert match is not None
        assert match.table_comment == "Primary insurance claims table"
        assert match.natural_language_hint == "Query claim totals and status"
        assert "clm_amt" in match.columns
        assert match.columns["clm_amt"].comment == "Total claimed monetary loss"
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_metadata_enricher_markdown_parsing():
    md_content = """# Schema Metadata
## Table: public.claim
**Description**: Primary insurance claims table containing claim lifecycle status.
**Purpose**: Use this table for claim amount totals.

### Columns
| Column | Description | Values |
| --- | --- | --- |
| clm_amt | Total claimed monetary loss | |
| clm_stat | Adjudication status | 'OPEN', 'SETTLED' |
"""
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(md_content)
        temp_path = f.name

    try:
        enricher = MetadataEnricher(file_path=temp_path, enabled=True)
        assert len(enricher.enrichments) > 0

        match = enricher.find_enrichment("claim", "public")
        assert match is not None
        assert "Primary insurance claims table" in match.table_comment
        assert "Use this table for claim amount totals" in match.natural_language_hint
        assert "clm_stat" in match.columns
        assert match.columns["clm_stat"].enum_values == ["OPEN", "SETTLED"]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_enrich_schema_doc():
    doc = SchemaDoc(
        source_type="postgresql",
        db_alias="claims_db",
        schema_name="public",
        table_name="claim",
        columns=[
            ColumnMeta(name="clm_amt", data_type="numeric"),
            ColumnMeta(name="clm_stat", data_type="varchar"),
        ]
    )

    enricher = MetadataEnricher(enabled=False)
    enricher.enrichments["public.claim"] = TableEnrichment(
        table_name="claim",
        schema_name="public",
        table_comment="Enriched table comment",
        natural_language_hint="Enriched purpose hint",
        columns={
            "clm_amt": ColumnEnrichment(name="clm_amt", comment="Enriched amount comment"),
            "clm_stat": ColumnEnrichment(name="clm_stat", enum_values=["A", "B"]),
        }
    )
    enricher.enabled = True
    enricher.enrich_schema_doc(doc)

    assert doc.table_comment == "Enriched table comment"
    assert doc.natural_language_hint == "Enriched purpose hint"
    assert doc.columns[0].comment == "Enriched amount comment"
    assert doc.columns[1].enum_values == ["A", "B"]

    text = doc.to_text()
    assert "Purpose: Enriched purpose hint" in text
    assert "Enriched amount comment" in text
    assert "[values: 'A', 'B']" in text


def test_enrich_schema_dict():
    enricher = MetadataEnricher(enabled=False)
    enricher.enrichments["claim"] = TableEnrichment(
        table_name="claim",
        table_comment="Dict enriched comment",
        natural_language_hint="Dict enriched hint",
        columns={
            "col_a": ColumnEnrichment(name="col_a", comment="Enriched col_a"),
        }
    )
    enricher.enabled = True

    columns = [{"name": "col_a", "type": "int"}, {"name": "col_b", "type": "varchar"}]
    comment, hint, enriched_cols = enricher.enrich_schema_dict(
        schema_name="public",
        table_name="claim",
        columns=columns,
    )
    assert comment == "Dict enriched comment"
    assert hint == "Dict enriched hint"
    assert enriched_cols[0]["description"] == "Enriched col_a"


# ===========================================================================
# Re-ranker Tests
# ===========================================================================

def test_sigmoid():
    assert _sigmoid(0.0) == 0.5
    assert _sigmoid(100.0) == 1.0
    assert _sigmoid(-100.0) == 0.0


def test_noop_reranker():
    reranker = NoOpReranker()
    docs = [{"table_name": "t1", "score": 0.8}, {"table_name": "t2", "score": 0.5}]
    res = reranker.rerank("query", docs, top_k=1)
    assert len(res) == 1
    assert res[0]["table_name"] == "t1"


def test_build_reranker_factory():
    # Disabled by default
    r1 = build_reranker({"RERANK_ENABLED": "false"})
    assert isinstance(r1, NoOpReranker)

    # Cross encoder selection
    r2 = build_reranker({"RERANK_ENABLED": "true", "RERANK_PROVIDER": "cross-encoder"})
    assert isinstance(r2, CrossEncoderReranker)

    # FlashRank selection
    r3 = build_reranker({"RERANK_ENABLED": "true", "RERANK_PROVIDER": "flashrank"})
    assert isinstance(r3, FlashRankReranker)
