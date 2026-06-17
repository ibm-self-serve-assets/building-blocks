"""
DataStax Astra DB – NoSQL CRUD Service
IBM Cloud portfolio: HCD (Hyper-Converged Database) / AstraDB
FastAPI entry point.
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.collections import routes as collections_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="DataStax Astra DB – NoSQL CRUD Service",
    description=(
        "Full CRUD operations on DataStax Astra DB NoSQL collections "
        "using the astrapy Data API. Part of IBM Cloud HCD portfolio."
    ),
    version="1.0.0",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(collections_api.router)

logger.info("Astra DB NoSQL CRUD Service starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
