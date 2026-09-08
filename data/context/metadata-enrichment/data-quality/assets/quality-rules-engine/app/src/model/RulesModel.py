"""Pydantic models for DQ rules endpoints."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field


class AssetRef(BaseModel):
    asset_id: str = Field(..., description="watsonx.data Intelligence data asset ID")


class DQRuleCreate(BaseModel):
    name: str
    type: Literal["completeness", "uniqueness", "validity", "consistency", "accuracy"]
    description: str | None = None
    asset_ref: AssetRef
    columns: list[str]
    threshold: float = Field(0.99, ge=0.0, le=1.0)
    regex_pattern: str | None = None
    allowed_values: list[Any] | None = None


class RuleExecuteResponse(BaseModel):
    rule_id: str
    execution_id: str
    status: str
    message: str | None = None
