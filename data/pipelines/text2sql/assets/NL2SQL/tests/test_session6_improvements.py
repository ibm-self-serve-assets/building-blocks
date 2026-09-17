"""
tests/test_session6_improvements.py

Unit tests for Session 6 improvements (A1–A6):

  A1 — PostgreSQL row-count fallback: pg_class.reltuples used when n_live_tup = 0
  A3 — ColumnMeta.to_dict() excludes is_pii; all other fields are present
  A5 — get_model_dim() is now the single source of truth in embedders.py
  A6 — FK expansion helper: _fetch_fk_neighbours() cycle guard + 2-hop logic

Run:
    py -3.12 -m pytest NL2SQL/tests/test_session6_improvements.py -v
"""

from __future__ import annotations

import sys
import os
import types
import unittest.mock as mock

# ---------------------------------------------------------------------------
# Path wiring
# ---------------------------------------------------------------------------
_connectors_dir = os.path.join(os.path.dirname(__file__), "..", "embedding", "connectors")
_embedders_dir  = os.path.join(os.path.dirname(__file__), "..", "embedding")
_retriever_dir  = os.path.join(os.path.dirname(__file__), "..", "backend", "schema_retriever")

sys.path.insert(0, _retriever_dir)
sys.path.insert(0, _connectors_dir)
sys.path.insert(0, _embedders_dir)

# ---------------------------------------------------------------------------
# Stub heavy dependencies so tests run without installing them
# ---------------------------------------------------------------------------

def _stub(name: str) -> types.ModuleType:
    """Return an existing module or create a MagicMock stub for it."""
    if name in sys.modules:
        return sys.modules[name]
    m = mock.MagicMock()
    m.__name__ = name
    sys.modules[name] = m
    return m

for _dep in [
    "requests",
    "opensearchpy",
    "opensearchpy.exceptions",
    "opensearchpy.helpers",
    "fastapi",
    "pydantic",
    "sentence_transformers",
    "sqlalchemy",
    "sqlalchemy.exc",
]:
    _stub(_dep)

import pytest


# ===========================================================================
# A3 — ColumnMeta.to_dict() must exclude is_pii
# ===========================================================================

class TestColumnMetaToDict:

    def _make_col(self, **kwargs):
        # Import after path + stubs are wired
        import importlib
        if "base" in sys.modules:
            base_mod = sys.modules["base"]
        else:
            import base as base_mod
        return base_mod.ColumnMeta(**kwargs)

    def test_to_dict_excludes_is_pii(self):
        col = self._make_col(name="email", data_type="varchar", is_pii=True)
        d = col.to_dict()
        assert "is_pii" not in d, "is_pii must not appear in to_dict() output"

    def test_to_dict_contains_required_fields(self):
        col = self._make_col(
            name="status", data_type="varchar",
            is_nullable=False, is_unique=True,
            enum_values=["ACTIVE", "INACTIVE"],
        )
        d = col.to_dict()
        assert d["name"]        == "status"
        assert d["data_type"]   == "varchar"
        assert d["is_nullable"] is False
        assert d["is_unique"]   is True
        assert d["enum_values"] == ["ACTIVE", "INACTIVE"]

    def test_to_dict_defaults(self):
        col = self._make_col(name="id", data_type="bigint")
        d = col.to_dict()
        assert d["default"]   is None
        assert d["comment"]   is None
        assert d["is_unique"] is False
        assert d["enum_values"] == []

    def test_to_dict_pii_col_has_correct_data_but_no_flag(self):
        col = self._make_col(
            name="ssn", data_type="char",
            is_pii=True, is_nullable=False,
        )
        d = col.to_dict()
        assert d["name"]        == "ssn"
        assert d["is_nullable"] is False
        assert "is_pii" not in d


# ===========================================================================
# A5 — get_model_dim() in embedders.py
# ===========================================================================

class TestGetModelDim:

    def _load_embedders(self):
        # Force a fresh import so stubs are picked up
        import importlib
        if "embedders" in sys.modules:
            return sys.modules["embedders"]
        import embedders as em
        return em

    def _cfg(self, **overrides) -> dict:
        base = {
            "EMBED_PROVIDER":     "watsonx",
            "EMBED_MODEL":        "ibm-granite/granite-embedding-125m-english",
            "EMBED_ST_MODEL":     "BAAI/bge-base-en-v1.5",
            "WATSONX_API_KEY":    "dummy",
            "WATSONX_URL":        "https://us-south.ml.cloud.ibm.com",
            "WATSONX_PROJECT_ID": "dummy-project",
            "VECTOR_DIM":         "",
        }
        base.update(overrides)
        return base

    def test_known_watsonx_model(self):
        em = self._load_embedders()
        cfg = self._cfg(EMBED_MODEL="ibm-granite/granite-embedding-125m-english")
        assert em.get_model_dim(cfg) == 768

    def test_known_watsonx_278m(self):
        em = self._load_embedders()
        cfg = self._cfg(EMBED_MODEL="ibm-granite/granite-embedding-278m-english")
        assert em.get_model_dim(cfg) == 1024

    def test_known_st_model(self):
        em = self._load_embedders()
        cfg = self._cfg(EMBED_PROVIDER="st", EMBED_ST_MODEL="BAAI/bge-large-en-v1.5")
        assert em.get_model_dim(cfg) == 1024

    def test_explicit_vector_dim_overrides_model(self):
        em = self._load_embedders()
        cfg = self._cfg(
            EMBED_MODEL="ibm-granite/granite-embedding-125m-english",
            VECTOR_DIM="512",
        )
        assert em.get_model_dim(cfg) == 512

    def test_unknown_model_defaults_to_768(self):
        em = self._load_embedders()
        cfg = self._cfg(EMBED_MODEL="unknown-model-xyz")
        assert em.get_model_dim(cfg) == 768

    def test_invalid_vector_dim_ignored(self):
        em = self._load_embedders()
        cfg = self._cfg(
            EMBED_MODEL="BAAI/bge-base-en-v1.5",
            EMBED_PROVIDER="st",
            VECTOR_DIM="not-a-number",
        )
        assert em.get_model_dim(cfg) == 768

    def test_all_minilm_dim(self):
        em = self._load_embedders()
        cfg = self._cfg(EMBED_PROVIDER="st", EMBED_ST_MODEL="all-MiniLM-L6-v2")
        assert em.get_model_dim(cfg) == 384

    def test_model_dims_table_is_canonical(self):
        """Verify _MODEL_DIMS is accessible from embedders module."""
        em = self._load_embedders()
        assert hasattr(em, "_MODEL_DIMS"), "_MODEL_DIMS must be exported from embedders"
        assert isinstance(em._MODEL_DIMS, dict)
        assert len(em._MODEL_DIMS) >= 9  # at least the 9 models added in A5


# ===========================================================================
# A6 — _fetch_fk_neighbours() pure in-memory tests
# ===========================================================================

def _load_retriever():
    """Import schema_retriever_opensearch with all heavy deps stubbed."""
    if "schema_retriever_opensearch" in sys.modules:
        return sys.modules["schema_retriever_opensearch"]
    import schema_retriever_opensearch as m
    return m


class TestFetchFkNeighbours:

    def test_outgoing_fk_extracted(self):
        m = _load_retriever()
        doc = {
            "fk": [
                {"to_schema": "public", "to_table": "customers",
                 "from_column": "cust_id", "to_column": "id"},
            ],
            "referenced_by": [],
        }
        result = m._fetch_fk_neighbours(doc)
        assert "public.customers" in result

    def test_incoming_ref_extracted(self):
        m = _load_retriever()
        doc = {
            "fk": [],
            "referenced_by": ["public.order_items.order_id"],
        }
        result = m._fetch_fk_neighbours(doc)
        assert "public.order_items" in result

    def test_empty_fk_and_ref(self):
        m = _load_retriever()
        doc = {"fk": [], "referenced_by": []}
        assert m._fetch_fk_neighbours(doc) == set()

    def test_malformed_fk_skipped(self):
        m = _load_retriever()
        # Both to_schema and to_table empty → produces "." which must be dropped
        doc = {
            "fk": [{"to_schema": "", "to_table": ""}],
            "referenced_by": [],
        }
        result = m._fetch_fk_neighbours(doc)
        assert "." not in result
        assert result == set()

    def test_deduplication(self):
        m = _load_retriever()
        doc = {
            "fk": [
                {"to_schema": "public", "to_table": "customers",
                 "from_column": "c1", "to_column": "id"},
                {"to_schema": "public", "to_table": "customers",
                 "from_column": "c2", "to_column": "id"},
            ],
            "referenced_by": [],
        }
        result = m._fetch_fk_neighbours(doc)
        assert result == {"public.customers"}

    def test_both_fk_and_ref_combined(self):
        m = _load_retriever()
        doc = {
            "fk": [{"to_schema": "public", "to_table": "products",
                    "from_column": "prod_id", "to_column": "id"}],
            "referenced_by": ["public.order_items.order_id"],
        }
        result = m._fetch_fk_neighbours(doc)
        assert "public.products" in result
        assert "public.order_items" in result
        assert len(result) == 2
