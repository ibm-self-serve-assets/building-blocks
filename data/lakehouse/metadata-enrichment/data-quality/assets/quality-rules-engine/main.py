"""
IBM watsonx.data Intelligence Data Quality Service
FastAPI entry point.
"""
import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.rules import routes as rules_api
from app.route.results import routes as results_api
from app.route.profile import routes as profile_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="watsonx.data Intelligence – Data Quality Service",
    description=(
        "Programmatic access to IBM watsonx.data Intelligence Data Quality rules, "
        "execution, result tracking, and data profiling via the DAI REST API."
    ),
    version="1.0.0",
    servers=[{"url": SERVER_URL}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rules_api.router)
app.include_router(results_api.router)
app.include_router(profile_api.router)

logger.info("watsonx.data Intelligence DQ Service starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
