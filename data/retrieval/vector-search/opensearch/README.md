# OpenSearch Hybrid Search

**Core Capability**: Retrieval
**IBM Products**: IBM watsonx.data (OpenSearch), IBM watsonx.ai, IBM Cloud Object Storage
**Product Components**: IBM watsonx.data OpenSearch; ibm/slate-125m-english-rtrvr embedding model; IBM COS

## Overview

Build semantic vector search and **hybrid search** applications using **IBM watsonx.data OpenSearch** with **IBM watsonx.ai** embeddings. Ingest documents from **IBM Cloud Object Storage**, generate dense embeddings, store in k-NN vector indexes, and perform hybrid (vector + BM25) search for best retrieval accuracy.

---

## When to Use

| Scenario | Notes |
|---|---|
| Need a standalone ingestion + search service for documents stored in IBM COS | Start with `opensearch-data-ingestion` FastAPI asset |
| Want the best retrieval accuracy for a RAG pipeline | Use **hybrid search** (k-NN + BM25) — outperforms vector-only |
| Need to integrate with an existing RAG accelerator | Index documents here, point `rag-retrieval-fastapi-server` at the same index |
| Need to tune HNSW index parameters (`ef_construction`, `m`) | IBM Bob `opensearch-vector-search` skill covers this |

> **Hybrid Search vs Vector-only**: Always use hybrid search (k-NN + BM25) in production — it consistently outperforms pure vector search by catching both semantic and exact keyword matches.

---

## Getting Started

### Prerequisites

- **IBM watsonx.data OpenSearch** instance — note host, port, username, and password
- **IBM watsonx.ai** project — note Project ID and instance URL
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM Cloud Object Storage** bucket containing documents to ingest
- **Python 3.10+**

### Quick Start

```bash
cd assets/opensearch-data-ingestion
cp .env.example .env
# Edit .env:
#   IBM_API_KEY              — your IBM Cloud API key
#   WATSONX_PROJECT_ID       — your watsonx.ai project ID
#   OPENSEARCH_HOST          — OpenSearch host (from watsonx.data console)
#   OPENSEARCH_USERNAME      — OpenSearch username
#   OPENSEARCH_PASSWORD      — OpenSearch password
#   COS_ENDPOINT             — IBM COS endpoint
#   COS_BUCKET_NAME          — source bucket name
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Ingest documents from COS:
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

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The OpenSearch building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of IBM watsonx.data OpenSearch k-NN index design, HNSW parameter tuning, hybrid search score fusion, and IBM watsonx.ai embedding integration.

**Install the Bob Mode** — give Bob an OpenSearch hybrid search specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/opensearch-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/opensearch-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **OpenSearch Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the OpenSearch hybrid search patterns:
```bash
unzip bob-skills/opensearch-vector-search.zip
```
Open IBM Bob → Skills panel → enable `opensearch-vector-search`. Bob will use it as active context for every prompt in this workspace.

---

## Building Blocks

### 1. OpenSearch Data Ingestion Service
**Location**: `assets/opensearch-data-ingestion/`
**IBM Products**: watsonx.data OpenSearch, watsonx.ai, IBM COS, IBM Cloud IAM
**Description**: FastAPI service that downloads documents from IBM COS, generates IBM watsonx.ai embeddings, creates k-NN indexes in watsonx.data OpenSearch, and bulk-inserts document vectors.

**Quick Start**:
```bash
cd assets/opensearch-data-ingestion
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, OPENSEARCH_HOST, OPENSEARCH_PASSWORD, COS credentials
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**Ingest documents**:
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

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for OpenSearch k-NN index design, hybrid search, and watsonx.ai embedding integration
  - **Install**: copy [`bob-modes/base-modes/opensearch-builder.zip`](./bob-modes/base-modes/opensearch-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `opensearch-vector-search` | [`bob-skills/opensearch-vector-search.zip`](./bob-skills/opensearch-vector-search.zip) | IBM watsonx.data OpenSearch k-NN index design, HNSW parameter tuning, hybrid search (vector + BM25), watsonx.ai embedding integration |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Embedding Models

| Model ID | Dimension | Language | Use Case |
|---|---|---|---|
| `ibm/slate-125m-english-rtrvr` | 768 | English | Recommended for English RAG |
| `ibm/slate-30m-english-rtrvr` | 384 | English | Lightweight English RAG |
| `intfloat/multilingual-e5-large` | 1024 | Multi | Multilingual RAG |

## k-NN Index Configuration

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
      }
    }
  }
}
```

## Architecture

```
IBM Cloud Object Storage
        │
        │  ibm-cos-sdk download
        ▼
OpenSearch Ingestion Service (FastAPI)
        │
        ├─ unstructured parse + chunk
        │
        ├─ IBM watsonx.ai embed_documents()
        │   (ibm/slate-125m-english-rtrvr)
        │
        └─ opensearch-py bulk() insert
                │
                ▼
IBM watsonx.data OpenSearch
  (k-NN HNSW index)
        │
        ▼
Hybrid Search (k-NN + BM25)
```

## IBM Cloud References

- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [OpenSearch k-NN Plugin](https://opensearch.org/docs/latest/search-plugins/knn/)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
