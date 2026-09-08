# Astra DB Vector Ingestion Service

**IBM Products**: IBM watsonx.data — Astra DB service, IBM watsonx.ai, IBM Cloud Object Storage
**Language**: Python 3.12
**Framework**: FastAPI

## Overview

FastAPI service that downloads documents from **IBM Cloud Object Storage**, generates dense vector embeddings using **IBM watsonx.ai**, and inserts chunked document vectors into **DataStax Astra DB** vector collections using the `astrapy` Data API. Supports cosine similarity ANN search via the `$vector` sort operator.

## Prerequisites

- IBM Cloud API key
- IBM watsonx.ai project ID
- Astra DB service/database provisioned through IBM watsonx.data with vector-enabled collection
- IBM Cloud Object Storage bucket with source documents

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
| `IBM_CLOUD_REGION` | IBM Cloud region (e.g. `us-south`) |
| `WATSONX_PROJECT_ID` | IBM watsonx.ai project ID |
| `WATSONX_URL` | watsonx.ai endpoint URL |
| `ASTRA_DB_API_ENDPOINT` | Astra DB API endpoint URL |
| `ASTRA_DB_APPLICATION_TOKEN` | Astra DB application token |
| `COS_API_KEY` | IBM COS API key |
| `COS_INSTANCE_CRN` | IBM COS service instance CRN |
| `COS_ENDPOINT` | IBM COS endpoint URL |
| `REST_API_KEY` | API key for this service |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/ingest` | Download docs from COS, embed, insert into Astra DB |

## Usage Example

**Ingest documents from IBM COS**:
```bash
curl -X POST http://localhost:8080/ingest \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-docs-bucket",
    "directory": "documents/",
    "collection_name": "ibm_docs_vectors",
    "embedding_model_id": "ibm/granite-embedding-278m-multilingual"
  }'
```

**Response**:
```json
{
  "status": "success",
  "documents_processed": 42,
  "chunks_inserted": 387,
  "collection": "ibm_docs_vectors"
}
```

## Supported Embedding Models

| Model ID | Dimension | Use Case |
|---|---|---|
| `ibm/granite-embedding-278m-multilingual` | 768 | Current IBM example; verify support/lifecycle before deployment |

## Docker Deployment

```bash
docker build -t astradb-vector-ingestion .
docker run -p 8080:8080 --env-file .env astradb-vector-ingestion
```

## Project Structure

```
astradb-vector-ingestion/
├── main.py                           # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   └── ingest/routes.py          # Ingestion endpoint
    └── src/
        ├── model/IngestModel.py      # Pydantic request/response models
        ├── services/IngestService.py # COS download + embed + Astra DB insert
        └── utils/cos_ops.py          # IBM COS operations
```

## IBM Cloud References

- [IBM watsonx.data — Astra DB service](https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service)
- [IBM watsonx.ai Embedding Models](https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [astrapy SDK Documentation](https://github.com/datastax/astrapy)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
