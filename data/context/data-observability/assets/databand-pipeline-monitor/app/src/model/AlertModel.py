"""Pydantic models for alert policy endpoints."""
from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class AlertPolicyCreate(BaseModel):
    name: str = Field(..., description="Alert policy name")
    pipeline_name: str = Field(..., description="Pipeline this policy applies to")
    severity: Literal["low", "medium", "high", "critical"] = "high"
    # Supported operators: gt, lt, eq, gte, lte
    metric: str = Field(..., description="Metric to evaluate, e.g. 'null_rate', 'row_count'")
    operator: Literal["gt", "lt", "eq", "gte", "lte"] = "gt"
    threshold: float = Field(..., description="Threshold value that triggers the alert")
    notification_channel: str | None = Field(
        None, description="Slack or email channel identifier"
    )


class AlertPolicyResponse(BaseModel):
    uid: str
    name: str
    state: str
    created_at: str
    details: dict[str, Any] = {}
