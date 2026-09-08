"""Alert policy API routes."""
from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_500_INTERNAL_SERVER_ERROR

from app.src.model.AlertModel import AlertPolicyCreate, AlertPolicyResponse
import app.src.services.AlertService as alert_svc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/alerts", tags=["Alert Policies"])

_API_KEY_HEADER = APIKeyHeader(name="REST_API_KEY", auto_error=False)


def _check_key(key: str = Security(_API_KEY_HEADER)) -> str:
    if key != os.environ.get("REST_API_KEY"):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key")
    return key


@router.get(
    "",
    summary="List Databand alert policies",
    description="Returns all alert definitions registered in the Databand instance.",
)
async def list_alerts(_: str = Security(_check_key)) -> dict:
    try:
        return alert_svc.list_alerts()
    except Exception as exc:
        logger.exception("list_alerts failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.post(
    "",
    summary="Create Databand alert policy",
    description=(
        "Creates a new alert definition in Databand. "
        "Supports null_rate, row_count, schema_drift, and custom metric thresholds."
    ),
)
async def create_alert(
    policy: AlertPolicyCreate,
    _: str = Security(_check_key),
) -> dict:
    try:
        databand_payload = {
            "name": policy.name,
            "pipeline_name": policy.pipeline_name,
            "severity": policy.severity,
            "alert_on_change": False,
            "alert_configurations": [
                {
                    "type": "column_anomaly",
                    "metric": policy.metric,
                    "operator": policy.operator,
                    "value": policy.threshold,
                    "column": "*",
                }
            ],
        }
        if policy.notification_channel:
            databand_payload["notification_channel"] = policy.notification_channel
        return alert_svc.create_alert(databand_payload)
    except Exception as exc:
        logger.exception("create_alert failed: %s", exc)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
