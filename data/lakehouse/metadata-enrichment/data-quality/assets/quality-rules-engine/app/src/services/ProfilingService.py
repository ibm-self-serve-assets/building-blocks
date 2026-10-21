"""Profiling service."""
from __future__ import annotations
from app.src.utils.wxdi_client import WXDIClient

_client: WXDIClient | None = None


def _get() -> WXDIClient:
    global _client
    if _client is None:
        _client = WXDIClient()
    return _client


def submit_profile_job(asset_id: str, columns: list[str] | None = None) -> dict:
    return _get().submit_profile_job(asset_id, columns)

def get_profile_status(job_id: str) -> dict:
    return _get().get_profile_job(job_id)
