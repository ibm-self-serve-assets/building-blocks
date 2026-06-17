"""Data profiling API routes."""
from __future__ import annotations
import logging, os
from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR
from app.src.model.ResultsModel import ProfilingJobRequest, ProfilingJobResponse
import app.src.services.ProfilingService as profile_svc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/profile", tags=["Data Profiling"])
_KEY = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _auth(key: str = Security(_KEY)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post("", summary="Submit a data profiling job")
async def submit_profile(req: ProfilingJobRequest, _: str = Security(_auth)) -> dict:
    try:
        return profile_svc.submit_profile_job(req.asset_id, req.columns)
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/{job_id}", summary="Poll profiling job status", response_model=ProfilingJobResponse)
async def get_profile(job_id: str, _: str = Security(_auth)) -> ProfilingJobResponse:
    try:
        data = profile_svc.get_profile_status(job_id)
        return ProfilingJobResponse(job_id=job_id, status=data.get("status", "unknown"),
                                    asset_id=data.get("asset_id"), stats=data.get("stats", {}))
    except Exception as exc:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
