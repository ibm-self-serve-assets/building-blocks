"""Pydantic models for results and profiling endpoints."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class QualityScoreResponse(BaseModel):
    project_id: str
    quality_score: float | None
    total_rules: int
    passed_rules: int = 0
    failed_rules: int = 0


class ProfilingJobRequest(BaseModel):
    asset_id: str
    columns: list[str] | None = None


class ProfilingJobResponse(BaseModel):
    job_id: str
    status: str
    asset_id: str | None = None
    stats: dict[str, Any] = {}
