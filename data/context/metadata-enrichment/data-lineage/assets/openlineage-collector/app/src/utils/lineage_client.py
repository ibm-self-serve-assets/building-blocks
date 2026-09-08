"""
IBM Lineage client — wraps both:
  1. IBM Databand /api/v1/lineage  (OpenLineage event ingest)
  2. watsonx.data Intelligence REST API /data_lineage/*  (Manta lineage graph queries)
"""
from __future__ import annotations
import logging, os, time
from typing import Any
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class IAMTokenManager:
    _IAM_URL = "https://iam.cloud.ibm.com/identity/token"

    def __init__(self, api_key: str) -> None:
        self._api_key, self._token, self._expiry = api_key, None, 0.0

    def get_token(self) -> str:
        if not self._token or time.time() >= self._expiry:
            self._refresh()
        return self._token  # type: ignore[return-value]

    def _refresh(self) -> None:
        resp = requests.post(self._IAM_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self._api_key},
            timeout=30)
        resp.raise_for_status()
        body = resp.json()
        self._token = body["access_token"]
        self._expiry = time.time() + int(body.get("expires_in", 3600)) - 300


class LineageClient:
    """
    Unified client for IBM lineage stack.

    - forward_event() → IBM Databand Marquez-compatible endpoint
    - get_lineage_graph() → watsonx.data Intelligence Manta REST API
    """

    def __init__(self) -> None:
        api_key = os.environ["IBM_API_KEY"]
        self._iam = IAMTokenManager(api_key)
        # Databand static token preferred
        self._databand_token: str | None = os.getenv("DATABAND_ACCESS_TOKEN")
        self._databand_base = os.environ["DATABAND_URL"].rstrip("/")
        region = os.getenv("WXDI_REGION", "us-south")
        self._wxdi_base = os.getenv("WXDI_BASE_URL", f"https://api.{region}.dai.cloud.ibm.com").rstrip("/")
        self._project_id = os.environ["WXDI_PROJECT_ID"]

    def _databand_headers(self) -> dict:
        token = self._databand_token or self._iam.get_token()
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _wxdi_headers(self) -> dict:
        return {"Authorization": f"Bearer {self._iam.get_token()}", "Content-Type": "application/json"}

    # ------------------------------------------------------------------
    # Databand – ingest OpenLineage events
    # ------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def forward_event(self, ol_event: dict) -> dict:
        """POST to Databand /api/v1/lineage — Marquez-compatible OpenLineage endpoint."""
        url = f"{self._databand_base}/api/v1/lineage"
        resp = requests.post(url, headers=self._databand_headers(), json=ol_event, timeout=30)
        resp.raise_for_status()
        logger.info("OpenLineage event forwarded to Databand: eventType=%s", ol_event.get("eventType"))
        return {"status": "forwarded", "eventType": ol_event.get("eventType"), "url": url}

    # ------------------------------------------------------------------
    # watsonx.data Intelligence – Manta lineage queries
    # ------------------------------------------------------------------

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_lineage_graph(self, asset_id: str, direction: str = "both", depth: int = 3) -> dict:
        """
        GET /data_lineage/graphs — retrieve the Manta lineage graph for an asset.

        direction: upstream | downstream | both
        depth:     number of hops to traverse
        """
        url = f"{self._wxdi_base}/data_lineage/graphs"
        params = {"project_id": self._project_id, "asset_id": asset_id,
                  "direction": direction, "depth": depth}
        resp = requests.get(url, headers=self._wxdi_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def list_lineage_assets(self) -> dict:
        """GET /data_lineage/assets — all assets tracked in the lineage catalog."""
        url = f"{self._wxdi_base}/data_lineage/assets"
        resp = requests.get(url, headers=self._wxdi_headers(),
                            params={"project_id": self._project_id}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_impact_analysis(self, asset_id: str) -> dict:
        """
        GET /data_lineage/impact_analysis — all downstream assets affected by changes
        to *asset_id*.  Useful for impact analysis before schema changes.
        """
        url = f"{self._wxdi_base}/data_lineage/impact_analysis"
        params = {"project_id": self._project_id, "asset_id": asset_id}
        resp = requests.get(url, headers=self._wxdi_headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
