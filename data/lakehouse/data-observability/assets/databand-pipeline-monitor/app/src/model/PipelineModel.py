"""Pydantic models for pipeline and run endpoints."""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class PipelineRunsQuery(BaseModel):
    pipeline_name: str = Field(..., description="Databand pipeline name to query")
    from_date: str | None = Field(None, description="ISO-8601 start date, e.g. 2024-01-01")
    to_date: str | None = Field(None, description="ISO-8601 end date, e.g. 2024-01-31")
    page_size: int = Field(20, ge=1, le=200)


class RunDetailResponse(BaseModel):
    run_uid: str
    pipeline_name: str
    state: str
    start_time: str | None
    end_time: str | None
    metrics: dict[str, Any] = {}
    task_runs: list[dict[str, Any]] = []
