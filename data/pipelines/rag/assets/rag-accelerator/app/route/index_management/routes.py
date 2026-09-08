import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.IndexManagementModel import (
    ListIndexInput, 
    ListIndexResponse,
    DeleteIndexInput,
    DeleteIndexResponse
)
import app.src.services.IndexManagementService as index_management_service

# Load environment variables
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("index_management_route")

# Initialize router
index_management_api_route = APIRouter(
    prefix="",
    tags=["Index Management for Milvus and OpenSearch Vector DB"]
)

# API Key header
API_KEY_NAME = "REST_API_KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


# Utility functions
def validate_api_key(api_key: str) -> bool:
    """Validate API key from headers."""
    return api_key == os.environ.get("REST_API_KEY")


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """Retrieve and validate the API key."""
    if validate_api_key(api_key_header):
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Invalid API credentials."
    )


# Routes
@index_management_api_route.post("/list-index", 
    description="List all indices/collections in Milvus or OpenSearch Vector DB",
    summary="List all indices/collections in Vector DB",
    response_model=ListIndexResponse
)
async def list_indices(
    list_index_input: ListIndexInput,
    api_key: str = Security(get_api_key)
) -> ListIndexResponse:
    
    config = {}
    config['connection_name'] = list_index_input.connection_name

    logger.debug("Received list-index request with config: %s", config)

    info = {}

    try:
        # Time the operation
        tic = time.perf_counter()

        indices = index_management_service.list_indices(config)

        info["list-index-time"] = time.perf_counter() - tic
        logger.info("List index performance info: %s", json.dumps(info))

        return ListIndexResponse(
            data=indices,
            status="success",
            message=f"Successfully retrieved {len(indices)} indices/collections"
        )

    except Exception as e:
        logger.exception("Failed to list indices: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list indices: {str(e)}"
        )


@index_management_api_route.delete("/delete-index", 
    description="Delete an index/collection from Milvus or OpenSearch Vector DB",
    summary="Delete an index/collection from Vector DB",
    response_model=DeleteIndexResponse
)
async def delete_index(
    delete_index_input: DeleteIndexInput,
    api_key: str = Security(get_api_key)
) -> DeleteIndexResponse:
    
    config = {}
    config['connection_name'] = delete_index_input.connection_name
    config['index_name'] = delete_index_input.index_name

    logger.debug("Received delete-index request with config: %s", config)

    info = {}

    try:
        # Time the operation
        tic = time.perf_counter()

        index_management_service.delete_index(config)

        info["delete-index-time"] = time.perf_counter() - tic
        logger.info("Delete index performance info: %s", json.dumps(info))

        return DeleteIndexResponse(
            status="success",
            message=f"Successfully deleted index/collection: {config['index_name']}"
        )

    except ValueError as e:
        logger.warning("Index not found: %s", e)
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Failed to delete index: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete index: {str(e)}"
        )


