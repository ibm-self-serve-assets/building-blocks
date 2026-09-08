"""DQ results API routes."""
from __future__ import annotations
import logging, os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.utils.wxdi_client import WXDIClient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/results", tags=["Rule Results"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.get("", summary="List DQ rule execution results")
async def list_results(rule_id: str | None = None, _: str = Security(_auth)) -> dict:
    try:
        return WXDIClient().list_results(rule_id=rule_id)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/{result_id}", summary="Get a single rule execution result")
async def get_result(result_id: str, _: str = Security(_auth)) -> dict:
    try:
        return WXDIClient().get_result(result_id)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
