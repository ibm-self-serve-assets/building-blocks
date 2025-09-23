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
from app.src.services.COSService import COSService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables
load_dotenv()

# Initialize router
query_api_route = APIRouter(
    prefix="",
    tags=["Query a Milvus collection."]
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



config = query_service.init_environment()


# Routes
@query_api_route.post("/query", 
    description="Query a Milvus collection.",
    summary="Query a Milvus collection.",
    response_model=QueryDataResponse
)
async def get_ui_data(
    query_data_input: QueryDataInput,
    api_key: str = Security(get_api_key)
) -> QueryDataResponse:
    
    config['query'] = query_data_input.query
    config['num_results'] = query_data_input.num_results
    config['num_rerank_results']= query_data_input.num_rerank_results
    config['collection_name'] = query_data_input.collection_name

    info = {}

    try:
        # Time the COS operation
        tic = time.perf_counter()

        context, answer = query_service.generate_answer(config)

        data = {"answer": answer, "context": context}

        info["query-time"] = time.perf_counter() - tic

        # Log performance info
        logging.info(json.dumps(info, indent=4))

        return QueryDataResponse(
            data=data,
            status="success",
            message=f"Successfully queried Milvus."
        )

    except Exception as e:
        logging.error(f"Failed to query Milvus: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query Milvus."
        )


