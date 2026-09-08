# Quality Rules Engine

**IBM Products**: IBM watsonx.data Intelligence, IBM Cloud IAM, IBM Cloud Object Storage
**Language**: Python 3.12
**Framework**: FastAPI

## Overview

FastAPI service wrapping the **IBM watsonx.data Intelligence (DAI) REST API** — create and manage data quality rules (completeness, uniqueness, validity, consistency, accuracy), execute them asynchronously against any data asset in your watsonx.data Intelligence project, and retrieve aggregate quality scores and per-rule results.

## Prerequisites

- IBM Cloud API key
- IBM watsonx.data Intelligence instance and project ID
- (Optional) IBM Cloud Object Storage for report archiving

## Quick Start

```bash
cp .env.example .env
# Edit .env — set IBM_API_KEY and WXDI_PROJECT_ID
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

## Environment Variables

| Variable | Description |
|---|---|
| `IBM_API_KEY` | IBM Cloud API key (IAM authentication) |
| `WXDI_BASE_URL` | watsonx.data Intelligence base URL |
| `WXDI_PROJECT_ID` | watsonx.data Intelligence project ID |
| `COS_API_KEY` | IBM COS API key (optional, for report archiving) |
| `COS_INSTANCE_CRN` | IBM COS service CRN (optional) |
| `COS_ENDPOINT` | IBM COS endpoint URL (optional) |
| `REST_API_KEY` | API key for this service |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/rules` | Create a DQ rule |
| `GET` | `/rules` | List all DQ rules in the project |
| `POST` | `/rules/{rule_id}/execute` | Execute a rule asynchronously |
| `GET` | `/rules/score` | Aggregate quality score (passed / total) |
| `GET` | `/results` | List all execution results |
| `GET` | `/results/{id}` | Single result detail |
| `POST` | `/profile` | Submit column profiling job |
| `GET` | `/profile/{job_id}` | Poll profiling job status |

## Usage Examples

**Create a completeness rule**:
```bash
curl -X POST http://localhost:8080/rules \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_email_not_null",
    "type": "completeness",
    "asset_ref": {"asset_id": "your-asset-id"},
    "columns": ["email"],
    "threshold": 0.99
  }'
```

**Execute and check score**:
```bash
# Execute the rule
curl -X POST http://localhost:8080/rules/rule-123/execute \
  -H "REST_API_KEY: your_key"

# Get aggregate score
curl http://localhost:8080/rules/score \
  -H "REST_API_KEY: your_key"
```

## Supported Rule Types

| Type | Description | Example |
|---|---|---|
| `completeness` | Checks null/missing value rate | Email must not be null (threshold ≥ 99%) |
| `uniqueness` | Detects duplicate records | Primary key must be unique |
| `validity` | Validates format/regex/enum | Date must match ISO 8601 format |
| `consistency` | Cross-column referential checks | Country + zip code must match |
| `accuracy` | Comparison to reference dataset | Customer name matches master file |

## Docker Deployment

```bash
docker build -t quality-rules-engine .
docker run -p 8080:8080 --env-file .env quality-rules-engine
```

## Project Structure

```
quality-rules-engine/
├── main.py                              # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   ├── rules/routes.py              # Rule CRUD + execute endpoints
    │   ├── results/routes.py            # Result retrieval endpoints
    │   └── profile/routes.py           # Profiling job endpoints
    └── src/
        ├── model/
        │   ├── RulesModel.py            # Rule request/response models
        │   └── ResultsModel.py          # Results response models
        ├── services/
        │   ├── RulesService.py          # DAI rules API calls
        │   └── ProfilingService.py      # DAI profiling API calls
        └── utils/wxdi_client.py         # IAM auth + DAI HTTP client
```

## IBM Cloud References

- [IBM watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [watsonx.data Intelligence API Reference](https://cloud.ibm.com/apidocs/watsonx-data-intelligence)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
