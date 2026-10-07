import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.route.pipelines import routes as pipeline_api
from app.route.alerts import routes as alert_api
from app.route.metrics import routes as metrics_api

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("main")

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8080")

app = FastAPI(
    title="IBM Databand Pipeline Monitor",
    description=(
        "FastAPI service for monitoring IBM data pipelines via the Databand REST API. "
        "Register pipelines, query run health, retrieve quality metrics, and manage alert policies."
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

app.include_router(pipeline_api.router)
app.include_router(alert_api.router)
app.include_router(metrics_api.router)

logger.info("IBM Databand Pipeline Monitor starting on %s", SERVER_URL)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, log_level="info")
