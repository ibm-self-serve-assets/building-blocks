"""Alert policy service — create and list Databand alert definitions."""
from __future__ import annotations

import logging
from typing import Any

from app.src.utils.databand_client import DatabandClient

logger = logging.getLogger(__name__)

_client: DatabandClient | None = None


def _get_client() -> DatabandClient:
    global _client
    if _client is None:
        _client = DatabandClient()
    return _client


def list_alerts() -> dict[str, Any]:
    """Return all alert definitions registered in Databand."""
    logger.info("Listing all Databand alert policies")
    return _get_client().list_alert_policies()


def create_alert(policy: dict[str, Any]) -> dict[str, Any]:
    """
    Create a Databand alert definition.

    Example policy for a null-rate threshold:
    {
        "name": "high-null-rate",
        "pipeline_name": "customer_pipeline",
        "severity": "high",
        "alert_on_change": False,
        "alert_configurations": [
            {
                "type": "column_anomaly",
                "metric": "null_rate",
                "operator": "gt",
                "value": 0.05,
                "column": "*"
            }
        ]
    }
    """
    logger.info("Creating Databand alert policy: %s", policy.get("name"))
    return _get_client().create_alert_policy(policy)
