from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from enum import Enum


class IngestDataInput(BaseModel):
    bucket_name: str = Field(
        ..., 
        description="COS bucket to ingest files from.",
    )
    index_name: str = Field(
        ...,
        description="Elastic search index name or milvus collection name",
    )
    connection_name: str = Field(
        ...,
        description="connection name for (milvuswxd/milvus/elasticsearch)",
    )
    directory: str = Field(
        ...,
        description="temporary directory name to store files",
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "bucket_name": "example-bucket-name",
                "index_name": "example_index_name",
                "connection_name":"example_connection",
                "directory":"example_directory_name"
            }
        }

class IngestDataResponse(BaseModel):
    status: str
    message: str

class ErrorResponse(BaseModel):
    status: str
    message: str