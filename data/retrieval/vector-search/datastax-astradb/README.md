# DataStax Astra DB Vector Search

**Core Capability**: Retrieval
**IBM Products**: IBM HCD (DataStax Astra DB), IBM watsonx.ai, IBM Cloud Object Storage
**Product Components**: Astra DB Data API; astrapy SDK; IBM watsonx.ai embeddings; IBM COS

## Overview

Build vector search applications using **DataStax Astra DB** — part of the IBM Cloud HCD (Hyper-Converged Database) portfolio — with **IBM watsonx.ai** embeddings. Ingest documents from **IBM COS**, generate dense embeddings, store in Astra DB vector collections, and perform ANN search with cosine similarity.

---

## When to Use

| Scenario | Notes |
|---|---|
| Need vector search on IBM HCD (Astra DB) rather than OpenSearch | Use this block — Astra DB uses `$vector` field + ANN cosine search |
| Ingest documents from IBM COS and search them semantically | Start with `astradb-vector-ingestion` FastAPI asset |
| Want globally distributed, serverless vector storage | Astra DB is serverless — scales automatically |
| Need both NoSQL document storage and vector search in one service | Combine this with [`../../no-sql-database/astradb/`](../../no-sql-database/astradb/) |

> **OpenSearch vs Astra DB for RAG**: Use **OpenSearch** (via [`../opensearch/`](../opensearch/)) if you need hybrid search (vector + BM25 keyword). Use **Astra DB** if you specifically need IBM HCD serverless Cassandra-backed vector storage.

---

## Getting Started

### Prerequisites

- **Astra DB instance** on IBM Cloud HCD — note your API endpoint and Application Token
- **IBM watsonx.ai** project — note Project ID and instance URL
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM Cloud Object Storage** bucket containing documents to ingest
- **Python 3.10+**

### Quick Start

```bash
cd assets/astradb-vector-ingestion
cp .env.example .env
# Edit .env:
#   IBM_API_KEY                   — your IBM Cloud API key
#   WATSONX_PROJECT_ID            — your watsonx.ai project ID
#   ASTRA_DB_API_ENDPOINT         — from Astra DB console → Connect
#   ASTRA_DB_APPLICATION_TOKEN    — AstraCS:... token
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
    "collection_name": "ibm_docs_vectors",
    "embedding_model_id": "ibm/slate-125m-english-rtrvr"
  }'
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Astra DB Vector building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of Astra DB vector collection design, `astrapy` ANN search patterns, IBM watsonx.ai embedding integration, and IBM COS ingestion.

**Install the Bob Mode** — give Bob an Astra DB Vector specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/astradb-vector-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/astradb-vector-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Astra DB Vector Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the Astra DB vector patterns:
```bash
unzip bob-skills/astradb-vector-setup.zip
```
Open IBM Bob → Skills panel → enable `astradb-vector-setup`.

---

## Building Blocks

### 1. Astra DB Vector Ingestion Service
**Location**: `assets/astradb-vector-ingestion/`
**IBM Products**: IBM HCD (Astra DB), watsonx.ai, IBM COS, IBM Cloud IAM
**Description**: FastAPI service that downloads documents from IBM COS, generates IBM watsonx.ai embeddings, and inserts them into Astra DB vector collections using the astrapy Data API.

**Quick Start**:
```bash
cd assets/astradb-vector-ingestion
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, ASTRA_DB_API_ENDPOINT, ASTRA_DB_APPLICATION_TOKEN
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
    "collection_name": "ibm_docs_vectors",
    "embedding_model_id": "ibm/slate-125m-english-rtrvr"
  }'
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for Astra DB vector collection design and ingestion
  - **Install**: copy [`bob-modes/base-modes/astradb-vector-builder.zip`](./bob-modes/base-modes/astradb-vector-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `astradb-vector-setup` | [`bob-skills/astradb-vector-setup.zip`](./bob-skills/astradb-vector-setup.zip) | Astra DB vector collection creation, IBM watsonx.ai embedding integration, ANN search queries, IBM COS ingestion patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Architecture

```
IBM Cloud Object Storage
        │
        │  ibm-cos-sdk download
        ▼
Astra DB Ingestion Service (FastAPI)
        │
        ├─ unstructured parse + chunk
        │
        ├─ IBM watsonx.ai embed_documents()
        │   (ibm/slate-125m-english-rtrvr)
        │
        └─ astrapy collection.insert_many()
                │ { "_id": ..., "$vector": [...], "text": ... }
                ▼
DataStax Astra DB (IBM HCD)
  Vector Collection (cosine similarity)
        │
        ▼
ANN Search: collection.find(sort={"$vector": query_vec})
```

## IBM Cloud References

- [IBM HCD / DataStax Astra DB](https://cloud.ibm.com/catalog/services/hyper-converged-database)
- [DataStax Astra DB Data API](https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html)
- [astrapy SDK Documentation](https://github.com/datastax/astrapy)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
