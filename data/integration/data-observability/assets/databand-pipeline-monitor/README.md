# IBM Databand Pipeline Monitor

FastAPI service for monitoring IBM data pipelines using the **IBM Databand** REST API v1.  
IBM Databand is IBM's data observability platform, natively integrated into the IBM Cloud ecosystem.

## IBM Cloud Products Used

| Product | Role |
|---|---|
| **IBM Databand** | Pipeline observability, run tracking, quality metrics, alert policies |
| **IBM Cloud IAM** | Authentication — IBM API key → Bearer token |
| **IBM Cloud Object Storage (COS)** | Archive pipeline run reports as JSON |

## What's Included

```
databand-pipeline-monitor/
├── main.py                          # FastAPI entry point
├── Dockerfile                       # Python 3.12-slim container
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   ├── pipelines/routes.py      # GET /pipelines, POST /pipelines/runs, GET /pipelines/runs/{uid}
    │   ├── alerts/routes.py         # GET /alerts, POST /alerts
    │   └── metrics/routes.py        # POST /metrics/quality-summary
    └── src/
        ├── model/
        │   ├── PipelineModel.py
        │   ├── AlertModel.py
        │   └── MetricsModel.py
        ├── services/
        │   ├── PipelineService.py   # Run history, run detail
        │   ├── AlertService.py      # Alert CRUD
        │   └── MetricsService.py    # Quality metrics aggregation
        └── utils/
            ├── config.py
            ├── databand_client.py   # Databand REST API v1 wrapper + IAM auth
            └── cos_archiver.py      # IBM COS report archiving
```

## Prerequisites

1. An **IBM Cloud** account — [cloud.ibm.com](https://cloud.ibm.com)
2. An **IBM Databand** instance provisioned from the [IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/databand)
3. A **Databand personal access token** — Databand UI → Account → Access Tokens
4. An **IBM Cloud API key** — [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
5. Optionally an **IBM Cloud Object Storage** instance for log archiving

## Quick Start

```bash
# 1. Clone and navigate
cd data/integration/data-observability/assets/databand-pipeline-monitor

# 2. Configure environment
cp .env.example .env
# Edit .env with your Databand URL, access token, and IBM API key

# 3. Install dependencies (Python 3.12+)
pip install -r requirements.txt

# 4. Run the service
python main.py
# → API docs at http://localhost:8080/docs
```

## Docker

```bash
docker build -t databand-monitor .
docker run -p 8080:8080 --env-file .env databand-monitor
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/pipelines` | List all Databand pipelines |
| POST | `/pipelines/runs` | List runs for a pipeline with date filtering |
| GET | `/pipelines/runs/{run_uid}` | Full run detail with metrics and task breakdowns |
| GET | `/alerts` | List all alert policies |
| POST | `/alerts` | Create a new alert policy |
| POST | `/metrics/quality-summary` | Aggregated quality summary for a run |

All endpoints require `REST_API_KEY` header.

## Authentication Flow

```
Your App → POST IBM IAM /identity/token (API key) → Bearer Token
Bearer Token → Databand REST API /api/v1/* → Pipeline Data
```

## Environment Variables

| Variable | Description |
|---|---|
| `DATABAND_URL` | Your Databand instance URL (e.g. `https://your-company.databand.ai`) |
| `DATABAND_ACCESS_TOKEN` | Databand personal access token |
| `IBM_API_KEY` | IBM Cloud API key (used when no static token) |
| `COS_ENDPOINT` | IBM COS endpoint for log archiving |
| `COS_API_KEY` | IBM COS HMAC API key |
| `COS_INSTANCE_CRN` | IBM COS service instance CRN |
| `COS_BUCKET` | Bucket name for archived reports |
| `REST_API_KEY` | API key to secure this service's own endpoints |

## IBM Cloud References

- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [IBM Databand API Reference](https://databand.ai/docs/api)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
