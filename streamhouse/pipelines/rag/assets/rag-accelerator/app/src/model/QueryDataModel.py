from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class QueryDataInput(BaseModel):
    query: str = Field(
        ..., 
        description="RAG query",
    )
    connection_name: str = Field(
        ..., 
        description="Milvus/Elastic Search connection name",
    )
    index_name: str = Field(
        ..., 
        description="Milvus collection/Elastic Search Index to ingest files into.",
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
                "connection_name": "example_connection_name",
                "index_name":"example_index_name"
            }
        }

class QueryDataResponse(BaseModel):
    data: dict
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    message: str