# OpenLineage Collector

**IBM Products**: IBM watsonx.data Intelligence (Manta), IBM Databand, IBM Cloud IAM
**Language**: Python 3.12
**Framework**: FastAPI

## Overview

FastAPI service that accepts **OpenLineage events** from any Python ETL, IBM DataStage, or Apache Spark pipeline and forwards them to **IBM Databand's** Marquez-compatible `/api/v1/lineage` endpoint. Also exposes Manta lineage graph queries via the **watsonx.data Intelligence** REST API for upstream/downstream traversal and impact analysis.

## Prerequisites

- IBM Cloud API key
- IBM watsonx.data Intelligence instance and project ID
- IBM Databand instance URL and access token

## Quick Start

```bash
cp .env.example .env
# Edit .env — set all required credentials
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
| `DATABAND_URL` | IBM Databand instance URL |
| `DATABAND_ACCESS_TOKEN` | IBM Databand access token |
| `REST_API_KEY` | API key for this service |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/events/lineage` | Ingest OpenLineage event → forwards to IBM Databand |
| `GET` | `/lineage/assets` | List all Manta-tracked assets |
| `POST` | `/lineage/graph` | Get upstream/downstream lineage graph for an asset |
| `POST` | `/lineage/impact` | Downstream impact analysis — all affected assets |

## Usage Examples

**Emit an OpenLineage COMPLETE event**:
```bash
curl -X POST http://localhost:8080/events/lineage \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "COMPLETE",
    "eventTime": "2024-06-15T10:30:00Z",
    "run": {"runId": "550e8400-e29b-41d4-a716-446655440000"},
    "job": {"namespace": "customer_etl", "name": "transform_orders"},
    "inputs": [{"namespace": "cos://raw-bucket", "name": "orders.csv"}],
    "outputs": [{"namespace": "iceberg://cos_catalog", "name": "sales.orders_curated"}]
  }'
```

**Get downstream impact of an asset change**:
```bash
curl -X POST http://localhost:8080/lineage/impact \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"asset_id": "your-source-asset-id", "max_depth": 5}'
```

**Query upstream lineage graph**:
```bash
curl -X POST http://localhost:8080/lineage/graph \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"asset_id": "your-asset-id", "direction": "upstream"}'
```

## Docker Deployment

```bash
docker build -t openlineage-collector .
docker run -p 8080:8080 --env-file .env openlineage-collector
```

## Project Structure

```
openlineage-collector/
├── main.py                               # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   ├── events/routes.py              # OpenLineage event ingestion
    │   └── lineage/routes.py            # Manta graph + impact queries
    └── src/
        ├── model/LineageModel.py         # Pydantic request/response models
        ├── services/                     # Databand + Manta service calls
        └── utils/lineage_client.py       # IAM auth + HTTP client
```

## IBM Cloud References

- [IBM watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [OpenLineage Specification](https://openlineage.io/spec)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
