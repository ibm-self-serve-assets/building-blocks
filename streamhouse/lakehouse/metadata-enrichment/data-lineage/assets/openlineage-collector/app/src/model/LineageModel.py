"""Pydantic models for OpenLineage event and lineage graph endpoints."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class OpenLineageEventRequest(BaseModel):
    """Minimal OpenLineage RunEvent envelope — full spec: https://openlineage.io/spec"""
    eventType: str = Field(..., description="START | COMPLETE | FAIL | ABORT | OTHER")
    eventTime: str = Field(..., description="ISO-8601 timestamp")
    run: dict[str, Any] = Field(..., description="Run object with runId")
    job: dict[str, Any] = Field(..., description="Job object with namespace and name")
    inputs: list[dict[str, Any]] = []
    outputs: list[dict[str, Any]] = []
    producer: str = "openlineage-collector"


class LineageGraphQuery(BaseModel):
    asset_id: str = Field(..., description="watsonx.data Intelligence asset ID")
    direction: str = Field("both", description="upstream | downstream | both")
    depth: int = Field(3, ge=1, le=10, description="Number of lineage hops to traverse")


class ImpactAnalysisQuery(BaseModel):
    asset_id: str = Field(..., description="Asset ID to analyse downstream impact for")
