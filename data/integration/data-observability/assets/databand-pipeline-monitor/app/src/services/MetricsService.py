"""Metrics service — surface data quality scores and column-level statistics."""
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


def get_run_quality_summary(run_uid: str, include_tasks: bool = True) -> dict[str, Any]:
    """
    Aggregate quality metrics for a single pipeline run.

    Returns a dict with null_rate, schema_drift flag, quality_score,
    total/failed record counts, and optionally per-task breakdowns.
    """
    logger.info("Fetching quality metrics for run uid=%s", run_uid)
    client = _get_client()

    run = client.get_run(run_uid)
    raw_metrics = client.get_run_metrics(run_uid)

    # Extract top-level quality indicators surfaced by Databand
    metrics_data = raw_metrics.get("metrics", {})
    quality_score = metrics_data.get("quality_score")
    null_rate = metrics_data.get("null_rate")
    total_records = metrics_data.get("total_records")
    failed_records = metrics_data.get("failed_records")
    schema_drift = bool(metrics_data.get("schema_drift_detected", False))

    summary: dict[str, Any] = {
        "run_uid": run_uid,
        "pipeline_name": run.get("pipeline_name", ""),
        "total_records": total_records,
        "failed_records": failed_records,
        "null_rate": null_rate,
        "schema_drift_detected": schema_drift,
        "quality_score": quality_score,
        "raw": raw_metrics,
    }

    if include_tasks:
        tasks = client.get_run_tasks(run_uid)
        summary["task_metrics"] = tasks.get("task_runs", [])

    return summary
