"""
IBM Databand client — wraps the Databand REST API v1.
Authentication: IBM IAM API key → Bearer token injected into every request.
Databand API reference: https://databand.ai/docs/api
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class IAMTokenManager:
    """Fetches and caches an IBM Cloud IAM bearer token."""

    _IAM_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._token: str | None = None
        self._expiry: float = 0.0

    def get_token(self) -> str:
        if not self._token or time.time() >= self._expiry:
            self._refresh()
        return self._token  # type: ignore[return-value]

    def _refresh(self) -> None:
        resp = requests.post(
            self._IAM_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self._api_key,
            },
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        self._token = body["access_token"]
        self._expiry = time.time() + int(body.get("expires_in", 3600)) - 300
        logger.debug("IAM token refreshed, expires in ~%s s", body.get("expires_in"))


class DatabandClient:
    """
    Thin wrapper around the IBM Databand REST API v1.

    Databand is IBM's data observability platform (acquired 2021).
    Every method maps 1-to-1 to a documented Databand API endpoint.

    Ref: https://databand.ai/docs/api
    """

    def __init__(
        self,
        databand_url: str | None = None,
        access_token: str | None = None,
        ibm_api_key: str | None = None,
    ) -> None:
        self._base = (databand_url or os.environ["DATABAND_URL"]).rstrip("/")
        # Prefer a static personal-access-token; fall back to IAM-derived token.
        self._static_token: str | None = access_token or os.getenv("DATABAND_ACCESS_TOKEN")
        self._iam: IAMTokenManager | None = None
        if not self._static_token:
            key = ibm_api_key or os.environ["IBM_API_KEY"]
            self._iam = IAMTokenManager(key)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_header(self) -> dict[str, str]:
        token = self._static_token if self._static_token else self._iam.get_token()  # type: ignore[union-attr]
        return {"Authorization": f"Bearer {token}"}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{self._base}/api/v1{path}"
        resp = requests.get(url, headers=self._auth_header(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _post(self, path: str, payload: dict) -> Any:
        url = f"{self._base}/api/v1{path}"
        resp = requests.post(url, headers=self._auth_header(), json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _patch(self, path: str, payload: dict) -> Any:
        url = f"{self._base}/api/v1{path}"
        resp = requests.patch(url, headers=self._auth_header(), json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Pipeline / Run endpoints
    # ------------------------------------------------------------------

    def list_pipelines(self, page: int = 1, page_size: int = 50) -> dict:
        """GET /pipelines — list all registered pipelines."""
        return self._get("/pipelines", params={"page": page, "page_size": page_size})

    def get_pipeline(self, pipeline_name: str) -> dict:
        """GET /pipelines/{name}"""
        return self._get(f"/pipelines/{pipeline_name}")

    def list_pipeline_runs(
        self,
        pipeline_name: str,
        from_date: str | None = None,
        to_date: str | None = None,
        page_size: int = 20,
    ) -> dict:
        """GET /runs — filtered by pipeline name and optional date range."""
        params: dict[str, Any] = {"pipeline_name": pipeline_name, "page_size": page_size}
        if from_date:
            params["from_date"] = from_date
        if to_date:
            params["to_date"] = to_date
        return self._get("/runs", params=params)

    def get_run(self, run_uid: str) -> dict:
        """GET /runs/{run_uid}"""
        return self._get(f"/runs/{run_uid}")

    def get_run_metrics(self, run_uid: str) -> dict:
        """GET /runs/{run_uid}/metrics — data quality metrics for a specific run."""
        return self._get(f"/runs/{run_uid}/metrics")

    def get_run_tasks(self, run_uid: str) -> dict:
        """GET /runs/{run_uid}/task_runs — individual task-level metrics."""
        return self._get(f"/runs/{run_uid}/task_runs")

    # ------------------------------------------------------------------
    # Alert / policy endpoints
    # ------------------------------------------------------------------

    def list_alert_policies(self) -> dict:
        """GET /alert_defs — all configured alert policies."""
        return self._get("/alert_defs")

    def create_alert_policy(self, policy: dict) -> dict:
        """POST /alert_defs — create a new alert policy."""
        return self._post("/alert_defs", policy)

    def update_alert_policy(self, policy_uid: str, updates: dict) -> dict:
        """PATCH /alert_defs/{uid}"""
        return self._patch(f"/alert_defs/{policy_uid}", updates)

    # ------------------------------------------------------------------
    # Dataset / data quality endpoints
    # ------------------------------------------------------------------

    def list_datasets(self, pipeline_name: str | None = None) -> dict:
        """GET /datasets — datasets monitored by Databand."""
        params: dict = {}
        if pipeline_name:
            params["pipeline_name"] = pipeline_name
        return self._get("/datasets", params=params)

    def get_dataset_stats(self, dataset_uid: str) -> dict:
        """GET /datasets/{uid}/stats — column-level stats and quality score."""
        return self._get(f"/datasets/{dataset_uid}/stats")
