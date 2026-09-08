# Serverless Vector — Astra DB on IBM watsonx.data

**Core Capability**: Query Engines
**IBM Products**: IBM watsonx.data, Astra DB Serverless (DataStax)
**Product Components**: Astra DB Serverless (vector + NoSQL document); Astra DB Data API; astrapy SDK; IBM watsonx.ai embeddings; IBM COS

## Overview

Use **Astra DB Serverless through IBM watsonx.data** for elastic vector storage and NoSQL document storage on the same platform. This building block covers both the **vector similarity search** pattern (for RAG and semantic search) and the **NoSQL document CRUD** pattern (for schema-flexible JSON document workloads) — both are native capabilities of Astra DB running inside IBM HCD.

Astra DB Serverless can be provisioned directly from the **IBM watsonx.data infrastructure experience** — add an Astra DB service and provision a **Serverless (vector)** or **Serverless (tables)** database. This makes Astra DB available as a managed service inside the watsonx.data environment without requiring separate cluster provisioning.

The building block also includes a runnable FastAPI ingestion service that downloads documents from **IBM COS**, generates **IBM watsonx.ai** embeddings, stores them in Astra DB vector collections, and performs ANN similarity search.

> **Architecture note**: The Astra DB Vector ingestion asset may reflect an earlier integration pattern. Current watsonx.data documentation supports provisioning Astra DB Serverless **directly from the watsonx.data infrastructure experience**. See [IBM watsonx.data documentation](https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service) for the current product integration.

---

## When to Use

| Scenario | Asset |
|---|---|
| Need elastic vector storage for RAG, agents, recommendation or semantic search | [`assets/astradb-vector-ingestion/`](assets/astradb-vector-ingestion/) |
| Ingest documents from IBM COS and search them semantically | [`assets/astradb-vector-ingestion/`](assets/astradb-vector-ingestion/) |
| Need large-scale NoSQL document storage with MongoDB-style filter queries | [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/) |
| Already have a Cassandra workload and need an IBM-managed serverless option | [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/) |
| Want globally distributed, serverless vector or document storage inside watsonx.data | Provision from the watsonx.data infrastructure experience |

> **RAG vs Serverless Vector**: For enterprise RAG where OpenRAG capabilities are the primary requirement, use the **[RAG](../../pipelines/rag/)** building block. For vector storage as an application service — especially where teams need direct embedding/query API access — Serverless Vector is often the simpler abstraction.

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

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Serverless Vector building block ships **two Bob Modes** and **two Bob Skills** — one set for vector/RAG patterns and one set for NoSQL document CRUD patterns.

**Install Bob Modes**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/astradb-vector-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
Copy-Item bob-modes/base-modes/nosql-astradb-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/astradb-vector-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
cp bob-modes/base-modes/nosql-astradb-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Astra DB Vector Builder** and **NoSQL Astra DB Builder** appear in the mode selector.

**Install Bob Skills**:
```bash
unzip bob-skills/astradb-vector-setup.zip
unzip bob-skills/astradb-nosql-design.zip
```
Open IBM Bob → Skills panel → enable the skill(s) relevant to your use case.

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

### 2. Astra DB NoSQL CRUD Service
**Location**: [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/)
**IBM Products**: IBM HCD (Astra DB / watsonx.data DataStax)
**Description**: FastAPI service providing full CRUD operations on Astra DB NoSQL document collections using the `astrapy` Data API with MongoDB-style filter expressions (`$eq`, `$in`, `$and`, `$or`). Use this asset for schema-flexible JSON document storage at Cassandra scale.

**Quick Start**:
```bash
cd assets/astradb-nosql-crud
cp .env.example .env
# Edit .env:
#   ASTRA_DB_API_ENDPOINT         — from Astra DB console → Connect
#   ASTRA_DB_APPLICATION_TOKEN    — AstraCS:... token from Astra DB console
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**Insert documents**:
```bash
curl -X POST http://localhost:8080/collections/insert \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "customers",
    "documents": [
      {"_id": "1", "name": "IBM Corp", "region": "us-south"},
      {"_id": "2", "name": "Acme Inc", "region": "eu-de"}
    ]
  }'
```

**Query with filters**:
```bash
curl -X POST http://localhost:8080/collections/find \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"region": {"$eq": "us-south"}}, "limit": 10}'
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/collections/insert` | Insert one or many documents |
| `POST` | `/collections/find` | Query with MongoDB-style filters (`$eq`, `$in`, `$and`, `$or`) |
| `POST` | `/collections/update` | Update with `$set`, `$unset`, `$inc` |
| `POST` | `/collections/delete` | Delete matching documents |

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: Two AI modes for Astra DB — vector and NoSQL patterns
  - **Astra DB Vector Builder** — [`bob-modes/base-modes/astradb-vector-builder.zip`](./bob-modes/base-modes/astradb-vector-builder.zip): Vector collection design, ANN search, IBM watsonx.ai embedding integration, IBM COS ingestion
  - **NoSQL Astra DB Builder** — [`bob-modes/base-modes/nosql-astradb-builder.zip`](./bob-modes/base-modes/nosql-astradb-builder.zip): NoSQL document modeling, MongoDB-style CRUD, bulk operations, Cassandra compatibility
  - **Install**: copy the zip(s) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `astradb-vector-setup` | [`bob-skills/astradb-vector-setup.zip`](./bob-skills/astradb-vector-setup.zip) | Astra DB vector collection creation, IBM watsonx.ai embedding integration, ANN search queries, IBM COS ingestion patterns |
| `astradb-nosql-design` | [`bob-skills/astradb-nosql-design.zip`](./bob-skills/astradb-nosql-design.zip) | Astra DB document modeling, MongoDB-style CRUD, bulk operations, collection schema design, data migration patterns |

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

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM watsonx.data — Adding Astra DB](https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service)** | Provision and manage Astra DB Serverless from within the watsonx.data infrastructure experience |
| **[Astra DB Serverless](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html)** | Serverless vector and NoSQL document database for embeddings, similarity search, RAG, and document storage |
| **[IBM HCD (Hyper Converged Database)](https://cloud.ibm.com/catalog/services/hyper-converged-database)** | IBM Cloud managed service providing Astra DB (SaaS) and DataStax (software) |
| **[IBM watsonx.ai](https://www.ibm.com/products/watsonx-ai)** | Embedding model generation (`ibm/slate-125m-english-rtrvr`) for vector ingestion |
| **[IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)** | Document source for vector ingestion pipeline |

## IBM Cloud References

- [IBM watsonx.data — Adding Astra DB Service](https://www.ibm.com/docs/en/watsonxdata/saas?topic=watsonxdata-adding-astra-db-service)
- [IBM HCD / DataStax Astra DB](https://cloud.ibm.com/catalog/services/hyper-converged-database)
- [Astra DB Serverless Documentation](https://docs.datastax.com/en/astra-db-serverless/)
- [DataStax Astra DB Data API](https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html)
- [astrapy SDK Documentation](https://github.com/datastax/astrapy)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
