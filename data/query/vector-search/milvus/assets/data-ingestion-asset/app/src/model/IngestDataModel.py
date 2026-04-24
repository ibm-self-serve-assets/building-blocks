from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum

class IngestDataInput(BaseModel):
    bucket_name: str = Field(
        ..., 
        description="COS bucket to ingest files from.",
    )
    collection_name: str = Field(
        ..., 
        description="Milvus collection to ingest files into.",
    )
    chunk_type: str = Field(
        ..., 
        description="Use Markdown splitter or Docling Hybrid Chunker",
    )
    
 
    class Config:
        json_schema_extra = {
            "example": {
                "bucket_name": "example-bucket-name",
                "collection_name": "example_collection_name",
                "chunk_type": "MARKDOWN"
            }
        }

class IngestDataResponse(BaseModel):
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    message: str