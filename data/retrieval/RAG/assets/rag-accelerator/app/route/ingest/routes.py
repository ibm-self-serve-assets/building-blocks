import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.IngestDataModel import IngestDataInput, IngestDataResponse
import app.src.services.IngestService as ingest_service

# Load environment variables
load_dotenv()

# Logging configuration controlled via .env
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger("ingest_route")

# Initialize router
ingest_api_route = APIRouter(
    prefix="",
    tags=["Ingest data into Elastic Search and Milvus Vector DB"]
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
@ingest_api_route.post("/ingest-files", 
    description="Ingest data into Elastic Search and Milvus Vector DB",
    summary="Ingest data into Elastic Search and Milvus Vector DB",
    response_model=IngestDataResponse
)
async def get_ui_data(
    ingest_data_input: IngestDataInput,
    api_key: str = Security(get_api_key)
) -> IngestDataResponse:
    
    config = {}
       
    config['index_name'] = ingest_data_input.index_name
    config['bucket_name'] = ingest_data_input.bucket_name
    config['connection_name'] = ingest_data_input.connection_name
    config['directory'] = ingest_data_input.directory

    logger.debug("Received ingest request with config: %s", config)

    info = {}

    try:
        
        tic = time.perf_counter()

        doc_length = ingest_service.ingest_files(config)

        info["ingest-time"] = time.perf_counter() - tic
        logger.info("Ingestion performance info: %s", json.dumps(info))

        return IngestDataResponse(
            status="success",
            message=f"Data Ingestion successful for {doc_length} document chunks into vector database!"
        )

    except Exception as e:
        logger.exception("Failed to ingest data: %s", e)
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest data"
        )
        
