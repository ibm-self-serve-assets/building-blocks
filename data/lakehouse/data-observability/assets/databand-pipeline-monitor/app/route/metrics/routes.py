"""Data quality metrics API routes."""
from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from app.src.model.MetricsModel import MetricsQuery, MetricsSummary
import app.src.services.MetricsService as metrics_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics", tags=["Data Quality Metrics"])

_API_KEY_HEADER = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _check_key(key: str = Security(_API_KEY_HEADER)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.post(
    "/quality-summary",
    summary="Get run quality summary",
    description=(
        "Returns aggregated quality metrics for a pipeline run: "
        "null rate, schema drift, quality score, record counts, "
        "and optional per-task breakdowns. Powered by IBM Databand."
    ),
    response_model=MetricsSummary,
)
async def get_quality_summary(
    query: MetricsQuery,
    _: str = Security(_check_key),
) -> MetricsSummary:
    try:
        data = metrics_svc.get_run_quality_summary(
            run_uid=query.run_uid,
            include_tasks=query.include_tasks,
        )
        return MetricsSummary(**data)
    except Exception as exc:
        logger.exception("get_quality_summary failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
