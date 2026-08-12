---
name: data-quality-rules
description: Expert guidance for implementing IBM watsonx.data Intelligence data quality rules on IBM Cloud — covers IAM authentication, DQ rule creation (completeness, uniqueness, validity, consistency, accuracy), rule execution via the DAI REST API, quality score interpretation, data profiling job submission, and IBM COS report archiving. Generates production-ready Python 3.12 code following IBM building-blocks conventions.
---

# IBM watsonx.data Intelligence Data Quality Builder

## Purpose

This skill defines the complete workflow for implementing **IBM watsonx.data Intelligence** data quality capabilities and generating **production-ready code** that includes:

- IBM IAM API key → Bearer token authentication with auto-refresh
- watsonx.data Intelligence (DAI) REST API integration for DQ rule CRUD
- Asynchronous rule execution and result polling
- Column-level data profiling job submission and status polling
- Quality score aggregation across project rules
- IBM COS report archiving using `ibm-cos-sdk`
- FastAPI service patterns matching IBM building-blocks conventions

## IBM Cloud Product Coverage

| IBM Cloud Product | DAI Feature Used |
|---|---|
| watsonx.data Intelligence | REST API: /data_quality/rules, /data_quality/results, /data_quality/profile_jobs |
| IBM Cloud IAM | POST /identity/token (apikey grant) |
| IBM Cloud Object Storage | ibm-cos-sdk put_object for report archiving |

## Objective

Transform natural language data quality requirements into **deployable services** that:

- Authenticate to IBM Cloud via standard IAM API key pattern
- Create, execute, and monitor DQ rules against watsonx.data Intelligence assets
- Surface quality scores and profiling statistics via REST API
- Follow Python 3.12 best practices with Pydantic v2 models

## Rules

- Always use `IAMTokenManager` with 5-minute expiry buffer
- Wrap all DAI API calls with `@retry(stop=stop_after_attempt(3), ...)` from `tenacity`
- Use `WXDI_PROJECT_ID` from environment — never hardcode project IDs
- DAI base URL: `https://api.{WXDI_REGION}.dai.cloud.ibm.com` — currently **us-south** is the supported region for DQ rules
- All request/response bodies modelled with Pydantic v2 `BaseModel`
- Use `python-dotenv` — provide `.env.example` with all IBM Cloud variable names

---

## Scope

- watsonx.data Intelligence data quality rule authoring and execution
- Completeness, uniqueness, validity, consistency, accuracy rule types
- Column-level profiling: null rate, distinct count, min, max, distribution histograms
- Quality score computation and trend analysis
- IBM COS archiving of quality reports

---

## Procedure

### Phase 1: IBM Cloud Authentication

```python
class IAMTokenManager:
    _IAM_URL = "https://iam.cloud.ibm.com/identity/token"

    def get_token(self) -> str:
        if not self._token or time.time() >= self._expiry:
            self._refresh()
        return self._token

    def _refresh(self) -> None:
        resp = requests.post(self._IAM_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self._api_key},
            timeout=30)
        resp.raise_for_status()
        body = resp.json()
        self._token = body["access_token"]
        self._expiry = time.time() + int(body.get("expires_in", 3600)) - 300
```

### Phase 2: DQ Rule Types Reference

| Rule Type | Use Case | Key Fields |
|---|---|---|
| `completeness` | Null / missing value check | `columns`, `threshold` (min non-null %) |
| `uniqueness` | Duplicate detection | `columns`, `threshold` (max duplicate %) |
| `validity` | Format / regex / enum check | `columns`, `regex_pattern` or `allowed_values` |
| `consistency` | Cross-column referential integrity | `columns`, `threshold` |
| `accuracy` | Comparison vs reference dataset | `columns`, `threshold` |

### Phase 3: watsonx.data Intelligence API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/data_quality/rules` | POST | Create a DQ rule |
| `/data_quality/rules` | GET | List all rules in project |
| `/data_quality/rules/{id}/execute` | POST | Async execution of a rule |
| `/data_quality/results` | GET | List execution results (`?rule_id=`) |
| `/data_quality/results/{id}` | GET | Single result detail |
| `/data_quality/profile_jobs` | POST | Submit column profiling job |
| `/data_quality/profile_jobs/{id}` | GET | Poll profiling job state |

All endpoints require `?project_id={WXDI_PROJECT_ID}` query parameter.

### Phase 4: Rule Payload Structure

```python
rule_payload = {
    "name": "customer_email_not_null",
    "type": "completeness",               # completeness | uniqueness | validity | consistency | accuracy
    "description": "Email must not be null",
    "asset_ref": {"asset_id": "<data-asset-id>"},
    "columns": ["email"],
    "threshold": 0.99                     # 1.0 = 100% must pass
}
```

### Phase 5: Quality Score Computation

```python
results = client.list_results()["results"]
passed = sum(1 for r in results if r.get("status") == "passed")
quality_score = passed / len(results) if results else None
```

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| DAI (us-south) | `https://api.us-south.dai.cloud.ibm.com` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
