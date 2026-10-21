"""OpenLineage event ingestion routes."""
from __future__ import annotations
import logging, os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.LineageModel import OpenLineageEventRequest
from app.src.utils.lineage_client import LineageClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["OpenLineage Events"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)
_client: LineageClient | None = None


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


def _get() -> LineageClient:
    global _client
    if _client is None:
        _client = LineageClient()
    return _client


@router.post(
    "/lineage",
    summary="Ingest an OpenLineage event",
    description=(
        "Accepts an OpenLineage RunEvent and forwards it to IBM Databand's "
        "Marquez-compatible /api/v1/lineage endpoint. "
        "Supports START, COMPLETE, FAIL events with dataset inputs/outputs."
    ),
)
async def ingest_event(event: OpenLineageEventRequest, _: str = Security(_auth)) -> dict:
    try:
        return _get().forward_event(event.model_dump())
    except Exception as exc:
        logger.exception("ingest_event failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
