# OpenSearch Data Ingestion Service

**IBM Products**: IBM watsonx.data (OpenSearch), IBM watsonx.ai, IBM Cloud Object Storage
**Language**: Python 3.12
**Framework**: FastAPI

## Overview

FastAPI service that downloads documents from **IBM Cloud Object Storage**, generates dense vector embeddings using **IBM watsonx.ai**, creates k-NN indexes in **IBM watsonx.data OpenSearch**, and bulk-inserts document vectors. Supports both pure vector (k-NN) search and hybrid search combining k-NN with BM25 keyword scoring.

## Prerequisites

- IBM Cloud API key
- IBM watsonx.ai project ID
- IBM watsonx.data OpenSearch cluster (host, port, credentials)
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
| `WATSONX_PROJECT_ID` | IBM watsonx.ai project ID |
| `WATSONX_URL` | watsonx.ai endpoint URL |
| `OPENSEARCH_HOST` | OpenSearch hostname |
| `OPENSEARCH_PORT` | OpenSearch port (default `9200`) |
| `OPENSEARCH_USER` | OpenSearch username |
| `OPENSEARCH_PASSWORD` | OpenSearch password |
| `COS_API_KEY` | IBM COS API key |
| `COS_INSTANCE_CRN` | IBM COS service CRN |
| `COS_ENDPOINT` | IBM COS endpoint URL |
| `REST_API_KEY` | API key for this service |

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/ingest` | Download docs from COS, embed, bulk-index into OpenSearch |

## Usage Example

**Ingest documents from IBM COS**:
```bash
curl -X POST http://localhost:8080/ingest \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-docs-bucket",
    "directory": "documents/",
    "index_name": "product_knowledge_base",
    "embedding_model_id": "ibm/slate-125m-english-rtrvr"
  }'
```

**Response**:
```json
{
  "status": "success",
  "documents_processed": 28,
  "chunks_indexed": 214,
  "index": "product_knowledge_base"
}
```

## k-NN Index Configuration

The service creates indexes with HNSW configuration for high-recall vector search:

```json
{
  "settings": {"index": {"knn": true}},
  "mappings": {
    "properties": {
      "vector": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "l2",
          "engine": "nmslib",
          "parameters": {"ef_construction": 128, "m": 24}
        }
      },
      "text": {"type": "text"},
      "source": {"type": "keyword"}
    }
  }
}
```

## Supported Embedding Models

| Model ID | Dimension | Use Case |
|---|---|---|
| `ibm/slate-125m-english-rtrvr` | 768 | Recommended for English RAG |
| `ibm/slate-30m-english-rtrvr` | 384 | Lightweight English RAG |
| `intfloat/multilingual-e5-large` | 1024 | Multilingual RAG |

## Docker Deployment

```bash
docker build -t opensearch-data-ingestion .
docker run -p 8080:8080 --env-file .env opensearch-data-ingestion
```

## Project Structure

```
opensearch-data-ingestion/
├── main.py                               # FastAPI app entrypoint
├── Dockerfile
├── requirements.txt
├── .env.example
└── app/
    ├── route/
    │   └── ingest/routes.py             # Ingestion endpoint
    └── src/
        ├── model/IngestModel.py          # Pydantic request/response models
        ├── services/IngestService.py     # COS + embed + OpenSearch bulk insert
        └── utils/                        # Config, IAM auth, COS ops
```

## IBM Cloud References

- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [OpenSearch k-NN Plugin](https://opensearch.org/docs/latest/search-plugins/knn/)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
