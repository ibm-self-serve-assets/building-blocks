"""
tests/test_pii_masking.py

Unit tests for sample-row PII masking in connectors/base.py.

Covers:
  - Column-name masking (Pass 1) — enabled / disabled via PII_MASK_COLUMNS flag
  - Regex value masking  (Pass 2) — enabled / disabled via PII_MASK_VALUES flag
  - Both passes disabled
  - Edge cases: None values, non-string values, partial replacements

Run:
    py -3.12 -m pytest NL2SQL/tests/test_pii_masking.py -v
"""

from __future__ import annotations

import sys
import os

# Add connectors/ dir directly so base.py can be imported without the package __init__
_connectors_dir = os.path.join(os.path.dirname(__file__), "..", "embedding", "connectors")  # embedding/ stays at root
sys.path.insert(0, _connectors_dir)

import pytest
import base as _base_module  # imports connectors/base.py directly; no SQLAlchemy needed
BaseConnector = _base_module.BaseConnector


# Convenience alias so tests don't need to reference the class name
mask = BaseConnector._mask_row


# ===========================================================================
# Pass 1 — Column-name masking
# ===========================================================================

class TestColumnNameMasking:

    def test_column_name_match_is_masked(self):
        row = {"email_address": "alice@example.com", "name": "Alice"}
        result = mask(row, patterns=["email"], mask_values=False)
        assert result["email_address"] == "[MASKED]"
        assert result["name"] == "Alice"

    def test_multiple_patterns_match(self):
        row = {"ssn": "123-45-6789", "phone_number": "555-0100", "name": "Bob"}
        result = mask(row, patterns=["ssn", "phone"], mask_values=False)
        assert result["ssn"] == "[MASKED]"
        assert result["phone_number"] == "[MASKED]"
        assert result["name"] == "Bob"

    def test_none_value_with_matching_column_is_masked(self):
        row = {"email": None}
        # Pass 1 only triggers when v is not None; None stays None
        result = mask(row, patterns=["email"], mask_values=False)
        assert result["email"] is None

    def test_empty_patterns_skips_column_masking(self):
        # PII_MASK_COLUMNS=false → pass empty patterns list
        row = {"email": "alice@example.com", "card": "4111111111111111"}
        result = mask(row, patterns=[], mask_values=False)
        # No masking applied (mask_values also off)
        assert result["email"] == "alice@example.com"
        assert result["card"] == "4111111111111111"

    def test_non_string_value_with_matching_column_is_masked(self):
        row = {"phone": 5550100}
        result = mask(row, patterns=["phone"], mask_values=False)
        assert result["phone"] == "[MASKED]"

    def test_column_name_case_insensitive(self):
        row = {"CUSTOMER_EMAIL": "bob@corp.com"}
        result = mask(row, patterns=["email"], mask_values=False)
        assert result["CUSTOMER_EMAIL"] == "[MASKED]"


# ===========================================================================
# Pass 2 — Regex value masking
# ===========================================================================

class TestRegexValueMasking:

    def test_email_in_value_is_replaced(self):
        row = {"contact": "reach me at alice@example.com for details"}
        result = mask(row, patterns=[], mask_values=True)
        assert "<email>" in result["contact"]
        assert "alice@example.com" not in result["contact"]

    def test_ipv4_in_value_is_replaced(self):
        row = {"last_login_ip": "192.168.1.1"}
        result = mask(row, patterns=[], mask_values=True)
        assert "<ip>" in result["last_login_ip"]
        assert "192.168.1.1" not in result["last_login_ip"]

    def test_integer_value_not_affected(self):
        row = {"order_count": 42}
        result = mask(row, patterns=[], mask_values=True)
        assert result["order_count"] == 42

    def test_none_value_not_affected(self):
        row = {"notes": None}
        result = mask(row, patterns=[], mask_values=True)
        assert result["notes"] is None

    def test_clean_string_unchanged(self):
        row = {"status": "ACTIVE"}
        result = mask(row, patterns=[], mask_values=True)
        assert result["status"] == "ACTIVE"

    def test_mask_values_false_skips_regex_pass(self):
        row = {"notes": "contact alice@example.com"}
        result = mask(row, patterns=[], mask_values=False)
        assert result["notes"] == "contact alice@example.com"


# ===========================================================================
# Both passes combined
# ===========================================================================

class TestBothPasses:

    def test_column_name_wins_before_regex(self):
        # email column — caught by Pass 1 before Pass 2 even runs
        row = {"email": "alice@example.com"}
        result = mask(row, patterns=["email"], mask_values=True)
        assert result["email"] == "[MASKED]"  # full mask, not <email> substitution

    def test_non_pii_column_still_gets_regex_scan(self):
        # column name 'notes' not in patterns, but value contains an email
        row = {"notes": "send to bob@corp.com"}
        result = mask(row, patterns=["email"], mask_values=True)
        assert "<email>" in result["notes"]

    def test_both_disabled(self):
        row = {"email": "alice@example.com", "notes": "call 555-123-4567"}
        result = mask(row, patterns=[], mask_values=False)
        assert result["email"] == "alice@example.com"
        assert result["notes"] == "call 555-123-4567"

    def test_multiple_sensitive_values_in_one_field(self):
        row = {"raw": "email: alice@example.com and ip: 10.0.0.1"}
        result = mask(row, patterns=[], mask_values=True)
        assert "alice@example.com" not in result["raw"]
        assert "10.0.0.1" not in result["raw"]
        assert "<email>" in result["raw"]
        assert "<ip>" in result["raw"]
