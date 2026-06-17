"""Pipeline and run service — business logic layer wrapping DatabandClient."""
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


def list_pipelines(page: int = 1, page_size: int = 50) -> dict[str, Any]:
    """Return all pipelines visible to the configured Databand instance."""
    logger.info("Fetching pipeline list (page=%s, page_size=%s)", page, page_size)
    return _get_client().list_pipelines(page=page, page_size=page_size)


def get_pipeline_runs(
    pipeline_name: str,
    from_date: str | None = None,
    to_date: str | None = None,
    page_size: int = 20,
) -> dict[str, Any]:
    """Return run history for *pipeline_name*."""
    logger.info(
        "Fetching runs for pipeline '%s' (from=%s, to=%s)", pipeline_name, from_date, to_date
    )
    return _get_client().list_pipeline_runs(
        pipeline_name=pipeline_name,
        from_date=from_date,
        to_date=to_date,
        page_size=page_size,
    )


def get_run_detail(run_uid: str) -> dict[str, Any]:
    """Fetch run metadata, metrics, and task runs for *run_uid*."""
    logger.info("Fetching run detail for uid=%s", run_uid)
    client = _get_client()
    run = client.get_run(run_uid)
    metrics = client.get_run_metrics(run_uid)
    tasks = client.get_run_tasks(run_uid)
    return {
        "run_uid": run_uid,
        "pipeline_name": run.get("pipeline_name", ""),
        "state": run.get("state", ""),
        "start_time": run.get("start_time"),
        "end_time": run.get("end_time"),
        "metrics": metrics,
        "task_runs": tasks.get("task_runs", []),
    }
