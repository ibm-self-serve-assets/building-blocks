"""Pydantic models for data quality metrics endpoints."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class MetricsQuery(BaseModel):
    run_uid: str = Field(..., description="Databand run UID to fetch metrics for")
    include_tasks: bool = Field(True, description="Whether to include per-task metrics")


class MetricsSummary(BaseModel):
    run_uid: str
    pipeline_name: str
    total_records: int | None
    failed_records: int | None
    null_rate: float | None
    schema_drift_detected: bool
    quality_score: float | None
    raw: dict[str, Any] = {}
