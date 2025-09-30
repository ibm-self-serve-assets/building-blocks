import os
import json
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.IngestDataModel import IngestDataInput, IngestDataResponse
from app.src.services.COSService import COSService
import app.src.services.IngestService as ingest_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Load environment variables
load_dotenv()

# Initialize router
ingest_api_route = APIRouter(
    prefix="",
    tags=["Ingest files from COS into Milvus."]
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
        detail="Invalid REST_API_KEY."
    )


# Routes
@ingest_api_route.post("/ingest-files", 
    description="Ingest files from COS into Milvus.",
    summary="Ingest files from COS into Milvus.",
    response_model=IngestDataResponse
)
async def get_ui_data(
    ingest_data_input: IngestDataInput,
    api_key: str = Security(get_api_key)
) -> IngestDataResponse:
    
    bucket_name = ingest_data_input.bucket_name
    collection_name = ingest_data_input.collection_name
    chunk_type = ingest_data_input.chunk_type

    cos_service = COSService(bucket_name)
    info = {}

    try:
        # Time the COS operation
        tic = time.perf_counter()

        # Get files list from COS
        files_list = cos_service.get_all_objects_from_cos(download_files=True)
        
        # Initialize environment
        config = ingest_service.init_environment(collection_name, chunk_type)
        
        # Pass the files list directly to the ingest_files function
        num_docs = ingest_service.ingest_files(config, files_list, # window_size = 'L', search = 'hybrid'
                                               )
        
        # Track the time for performance analysis
        info["ingestion-time"] = time.perf_counter() - tic

        # Log performance info
        logging.info(json.dumps(info, indent=4))

        # Get list of filenames for the response message
        filenames = [file['filename'] for file in files_list]

        return IngestDataResponse(
            status="success",
            message=f"Successfully ingested {num_docs} docs from {len(filenames)} file(s)"
        )

    except Exception as e:
        logging.error(f"Failed to ingest files: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest files: {str(e)}"
        )