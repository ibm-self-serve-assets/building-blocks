import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.QueryDataModel import QueryDataInput, QueryDataResponse
import app.src.services.QueryService as query_service

# Load environment variables
load_dotenv()


# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("query_route")

# Initialize router
query_api_route = APIRouter(
    prefix="",
    tags=["Query a Milvus and Elastic Search Vector DB"]
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

# config = query_service.init_environment()

# Routes
@query_api_route.post("/query", 
    description="Query Milvus and Elastic Search Vector DB",
    summary="Query Milvus and Elastic Search Vector DB",
    response_model=QueryDataResponse
)
async def get_ui_data(
    query_data_input: QueryDataInput,
    api_key: str = Security(get_api_key)
) -> QueryDataResponse:
    
    config = {}
    
    config['query'] = query_data_input.query
    config['num_results'] = query_data_input.num_results
    config['num_rerank_results'] = query_data_input.num_rerank_results
    config['connection_name'] = query_data_input.connection_name
    config['index_name'] = query_data_input.index_name

    logger.debug("Received query request with config: %s", config)

    info = {}

    try:
        # Time the COS operation
        tic = time.perf_counter()

        search_result, top_result = query_service.generate_answer(config)

        data = {
            "answer": top_result,
            "context": search_result
        }

        info["query-time"] = time.perf_counter() - tic
        logger.info("Query performance info: %s", json.dumps(info))

        return QueryDataResponse(
            data=data,
            status="success",
            message=f"Successfully queried Vector DB"
        )

    except Exception as e:
        logger.exception("Failed to query Milvus: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query Vector DB"
        )