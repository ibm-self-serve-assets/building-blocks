"""
IBM watsonx.data OpenSearch – Data Ingestion Service
FastAPI entry point.

IBM Cloud products:
  - IBM watsonx.data (OpenSearch backend)
  - IBM watsonx.ai (embedding generation)
  - IBM Cloud Object Storage (document source)
  - IBM Cloud IAM (authentication)
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.ingest import routes as ingest_api
from app.route.root import routes as root_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="IBM watsonx.data OpenSearch – Data Ingestion Service",
    description=(
        "Ingest documents from IBM COS into IBM watsonx.data OpenSearch with "
        "IBM watsonx.ai embeddings (ibm/slate-125m-english-rtrvr). "
        "Supports k-NN vector indexing and hybrid (BM25 + vector) search."
    ),
    version="1.0.0",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(root_api.router)
app.include_router(ingest_api.router)

logger.info("OpenSearch Ingestion Service starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
