"""Pipeline and run API routes."""
from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from app.src.model.PipelineModel import PipelineRunsQuery, RunDetailResponse
import app.src.services.PipelineService as pipeline_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])

_API_KEY_HEADER = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _check_key(key: str = Security(_API_KEY_HEADER)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.get(
    "",
    summary="List all Databand pipelines",
    description="Returns all pipelines visible to the configured Databand instance.",
)
async def list_pipelines(
    page: int = 1,
    page_size: int = 50,
    _: str = Security(_check_key),
) -> dict:
    try:
        return pipeline_svc.list_pipelines(page=page, page_size=page_size)
    except Exception as exc:
        logger.exception("list_pipelines failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "/runs",
    summary="List pipeline runs",
    description=(
        "Returns run history for a named pipeline with optional date range filtering. "
        "Uses IBM Databand GET /api/v1/runs."
    ),
)
async def list_pipeline_runs(
    query: PipelineRunsQuery,
    _: str = Security(_check_key),
) -> dict:
    try:
        return pipeline_svc.get_pipeline_runs(
            pipeline_name=query.pipeline_name,
            from_date=query.from_date,
            to_date=query.to_date,
            page_size=query.page_size,
        )
    except Exception as exc:
        logger.exception("list_pipeline_runs failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/runs/{run_uid}",
    summary="Get run detail",
    description="Returns full run detail including metrics and per-task breakdowns.",
    response_model=RunDetailResponse,
)
async def get_run_detail(
    run_uid: str,
    _: str = Security(_check_key),
) -> RunDetailResponse:
    try:
        data = pipeline_svc.get_run_detail(run_uid)
        return RunDetailResponse(**data)
    except Exception as exc:
        logger.exception("get_run_detail failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
