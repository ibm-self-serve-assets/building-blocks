"""DQ Rules service."""
from __future__ import annotations
import logging
from typing import Any
from app.src.utils.wxdi_client import WXDIClient

logger = logging.getLogger(__name__)
_client: WXDIClient | None = None


def _get() -> WXDIClient:
    global _client
    if _client is None:
        _client = WXDIClient()
    return _client


def create_rule(rule_payload: dict[str, Any]) -> dict:
    return _get().create_rule(rule_payload)

def list_rules() -> dict:
    return _get().list_rules()

def execute_rule(rule_id: str) -> dict:
    return _get().execute_rule(rule_id)

def get_quality_score() -> dict:
    return _get().get_quality_score()
