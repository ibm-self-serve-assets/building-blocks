"""Pydantic models for NoSQL CRUD endpoints."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class DocumentInsert(BaseModel):
    collection_name: str = Field(..., description="Astra DB collection name")
    documents: list[dict[str, Any]] = Field(..., description="List of documents to insert")


class DocumentQuery(BaseModel):
    collection_name: str
    filter: dict[str, Any] = Field({}, description="MongoDB-style filter expression")
    limit: int = Field(20, ge=1, le=200)
    projection: dict[str, Any] = Field({}, description="Fields to include/exclude")


class DocumentUpdate(BaseModel):
    collection_name: str
    filter: dict[str, Any] = Field(..., description="Filter to identify documents to update")
    update: dict[str, Any] = Field(..., description="Update operation: {$set: {field: value}}")
    upsert: bool = False


class DocumentDelete(BaseModel):
    collection_name: str
    filter: dict[str, Any] = Field(..., description="Filter to identify documents to delete")


class CRUDResponse(BaseModel):
    status: str
    collection_name: str
    affected_count: int = 0
    message: str = ""
