import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from app.route.query import routes as query_api
from app.route.qna import routes as qna_ai_service_api
from app.route.ingest import routes as ingest_api
from app.src.utils import config
from app.src.utils import rag_helper_functions


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

# Get parameters from config
parameter_sets = config.PARAMETERS
parameter_sets_list = list(parameter_sets.keys())
parameters=rag_helper_functions.get_parameter_sets(parameter_sets_list)


# Environment variable fallback
SERVER_URL =  parameters["server_url"].strip() if parameters["server_url"] else "http://localhost:4050"
ALLOWED_ORIGINS = parameters.get("allowed_origins", "*").split(",")

# FastAPI application instance
app = FastAPI(
    title="RAG Accelerator 2.0 API Service",
    description="RAG Accelerator 2.0 API Service for ingesting data and querying vector databases and watsonx.ai LLM",
    version="1.0.1-fastapi",
    servers=[{"url": SERVER_URL}],
)

app.include_router(ingest_api.ingest_api_route)
app.include_router(query_api.query_api_route)
app.include_router(qna_ai_service_api.qna_ai_service_route)

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Update environment variable for flexibility
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Start logging
logger.info("Starting API service...")

# Application entry point
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=4050, log_level="info")