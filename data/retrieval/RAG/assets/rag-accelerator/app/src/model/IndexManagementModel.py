from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ListIndexInput(BaseModel):
    connection_name: str = Field(
        default="opensearch_connect",
        description="connection name — use 'opensearch_connect'",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_name": "opensearch_connect"
            }
        }


class ListIndexResponse(BaseModel):
    data: List[str]
    status: str
    message: str


class DeleteIndexInput(BaseModel):
    connection_name: str = Field(
        default="opensearch_connect",
        description="connection name — use 'opensearch_connect'",
    )
    index_name: str = Field(
        ...,
        description="Index name to delete",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "connection_name": "opensearch_connect",
                "index_name": "example_index_name"
            }
        }


class DeleteIndexResponse(BaseModel):
    status: str
    message: str


class ErrorResponse(BaseModel):
    status: str
    message: str


