"""Pydantic models for vector ingestion endpoints."""
from __future__ import annotations
from pydantic import BaseModel, Field


class VectorIngestRequest(BaseModel):
    bucket_name: str = Field(..., description="IBM COS bucket containing source documents")
    directory: str = Field(..., description="COS key prefix to ingest from")
    collection_name: str = Field(..., description="Astra DB vector collection name")
    embedding_model_id: str = Field("ibm/slate-125m-english-rtrvr", description="IBM watsonx.ai embedding model")


class VectorIngestResponse(BaseModel):
    status: str
    message: str
    collection_name: str
    documents_inserted: int = 0
