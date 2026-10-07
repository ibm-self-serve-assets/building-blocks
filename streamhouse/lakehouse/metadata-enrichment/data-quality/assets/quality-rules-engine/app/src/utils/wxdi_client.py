"""
IBM watsonx.data Intelligence (DAI) API client.
Product: watsonx.data Intelligence on IBM Cloud
API ref: https://cloud.ibm.com/apidocs/watsonx-data-intelligence
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
        self._api_key = api_key
        self._token: str | None = None
        self._expiry: float = 0.0

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


class WXDIClient:
    """watsonx.data Intelligence REST API client — DQ rules, profiling."""

    def __init__(self, api_key: str | None = None, project_id: str | None = None, base_url: str | None = None) -> None:
        self._iam = IAMTokenManager(api_key or os.environ["IBM_API_KEY"])
        self._project_id = project_id or os.environ["WXDI_PROJECT_ID"]
        region = os.getenv("WXDI_REGION", "us-south")
        self._base = (base_url or os.getenv("WXDI_BASE_URL", f"https://api.{region}.dai.cloud.ibm.com")).rstrip("/")

    def _h(self) -> dict:
        return {"Authorization": f"Bearer {self._iam.get_token()}", "Content-Type": "application/json", "Accept": "application/json"}

    def _p(self, extra: dict | None = None) -> dict:
        p = {"project_id": self._project_id}
        if extra:
            p.update(extra)
        return p

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _get(self, path: str, params: dict | None = None) -> Any:
        r = requests.get(f"{self._base}{path}", headers=self._h(), params=self._p(params), timeout=30)
        r.raise_for_status(); return r.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _post(self, path: str, body: dict, params: dict | None = None) -> Any:
        r = requests.post(f"{self._base}{path}", headers=self._h(), params=self._p(params), json=body, timeout=60)
        r.raise_for_status(); return r.json()

    def create_rule(self, rule: dict) -> dict:
        return self._post("/data_quality/rules", rule)

    def list_rules(self) -> dict:
        return self._get("/data_quality/rules")

    def execute_rule(self, rule_id: str) -> dict:
        return self._post(f"/data_quality/rules/{rule_id}/execute", {})

    def list_results(self, rule_id: str | None = None) -> dict:
        return self._get("/data_quality/results", {"rule_id": rule_id} if rule_id else None)

    def get_result(self, result_id: str) -> dict:
        return self._get(f"/data_quality/results/{result_id}")

    def get_quality_score(self) -> dict:
        items = self.list_results().get("results", [])
        if not items:
            return {"project_id": self._project_id, "quality_score": None, "total_rules": 0, "passed_rules": 0, "failed_rules": 0}
        passed = sum(1 for r in items if r.get("status") == "passed")
        total = len(items)
        return {"project_id": self._project_id, "quality_score": round(passed / total, 4) if total else None,
                "total_rules": total, "passed_rules": passed, "failed_rules": total - passed}

    def submit_profile_job(self, asset_id: str, columns: list[str] | None = None) -> dict:
        body: dict[str, Any] = {"asset_ref": {"asset_id": asset_id}}
        if columns:
            body["columns"] = columns
        return self._post("/data_quality/profile_jobs", body)

    def get_profile_job(self, job_id: str) -> dict:
        return self._get(f"/data_quality/profile_jobs/{job_id}")
