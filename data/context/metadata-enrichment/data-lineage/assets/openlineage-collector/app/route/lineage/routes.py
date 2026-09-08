"""Manta lineage graph query routes."""
from __future__ import annotations
import logging, os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.LineageModel import LineageGraphQuery, ImpactAnalysisQuery
from app.src.utils.lineage_client import LineageClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lineage", tags=["Manta Lineage Graph"])
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


@router.get("/assets", summary="List all lineage-tracked assets")
async def list_assets(_: str = Security(_auth)) -> dict:
    try:
        return _get().list_lineage_assets()
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/graph",
    summary="Get Manta lineage graph for an asset",
    description=(
        "Returns the Manta data lineage graph (upstream, downstream, or both) "
        "for a watsonx.data Intelligence asset up to the specified depth."
    ),
)
async def get_graph(query: LineageGraphQuery, _: str = Security(_auth)) -> dict:
    try:
        return _get().get_lineage_graph(query.asset_id, query.direction, query.depth)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/impact",
    summary="Downstream impact analysis",
    description="Returns all downstream assets that would be affected by changes to the queried asset.",
)
async def get_impact(query: ImpactAnalysisQuery, _: str = Security(_auth)) -> dict:
    try:
        return _get().get_impact_analysis(query.asset_id)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
