"""Pydantic models for ingestion endpoints."""
from __future__ import annotations
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    bucket_name: str = Field(..., description="IBM COS bucket containing source documents")
    directory: str = Field(..., description="COS key prefix (folder path) to ingest")
    index_name: str = Field(..., description="OpenSearch index name to ingest into")
    embedding_model_id: str = Field(
        "ibm/slate-125m-english-rtrvr",
        description="IBM watsonx.ai embedding model ID"
    )


class IngestResponse(BaseModel):
    status: str
    message: str
    index_name: str
    documents_indexed: int = 0
