"""
IBM watsonx.data Intelligence – OpenLineage Collector
======================================================
FastAPI service that:
  1. Accepts OpenLineage run events via POST /events/lineage
  2. Forwards them to IBM Databand's Marquez-compatible /api/v1/lineage endpoint
  3. Queries the Manta lineage graph via watsonx.data Intelligence REST API

IBM Cloud Products:
  - watsonx.data Intelligence (Manta data lineage)  → REST API /data_lineage/*
  - IBM Databand                                     → /api/v1/lineage (OpenLineage ingest)
  - IBM Cloud IAM                                    → Bearer token auth
  - IBM Cloud Object Storage                         → Lineage report archiving
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.events import routes as events_api
from app.route.lineage import routes as lineage_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="IBM watsonx.data Intelligence – Data Lineage Collector",
    description=(
        "Collect OpenLineage events and forward to IBM Databand. "
        "Query Manta data lineage graphs via watsonx.data Intelligence REST API."
    ),
    version="1.0.0",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(events_api.router)
app.include_router(lineage_api.router)

logger.info("Lineage Collector starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
