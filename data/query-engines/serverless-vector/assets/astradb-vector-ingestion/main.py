"""
DataStax Astra DB – Vector Ingestion Service
IBM Cloud portfolio: HCD (Hyper-Converged Database) / AstraDB
FastAPI entry point.
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.ingest import routes as ingest_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="DataStax Astra DB – Vector Ingestion Service",
    description=(
        "Ingest documents from IBM COS into DataStax Astra DB vector collections "
        "using IBM watsonx.ai embeddings (ibm/slate-125m-english-rtrvr). "
        "Part of the IBM Cloud HCD (Hyper-Converged Database) portfolio."
    ),
    version="1.0.0",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(ingest_api.router)

logger.info("Astra DB Vector Ingestion Service starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
