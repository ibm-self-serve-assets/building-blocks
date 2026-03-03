from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class QueryDataInput(BaseModel):
    query: str = Field(
        ..., 
        description="RAG query",
    )
    collection_name: str = Field(
        ..., 
        description="Milvus collection to ingest files into.",
    )
    num_results: int = Field(
        30, 
        description="Number of results (chunks) to return for dense and sparse embeddings.",
    )
    num_rerank_results: int = Field(
        10, 
        description="Number of reranked results (chunks) to return for dense and sparse embeddings.",
    )
    
 
    class Config:
        json_schema_extra = {
            "example": {
                "query": "sample query",
                "collection_name": "example_collection_name"
            }
        }

class QueryDataResponse(BaseModel):
    data: dict
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    message: str