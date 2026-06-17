# Hybrid Search

**Core Capability**: Retrieval
**IBM Products**: IBM watsonx.data (OpenSearch), IBM watsonx.ai, IBM Cloud Object Storage
**Product Components**: OpenSearch k-NN + BM25; IBM watsonx.ai embeddings; IBM COS; IBM Docling

## Overview

Build high-performance **hybrid search** solutions — combining **semantic vector search** with **BM25 keyword search** for best retrieval results — using **IBM watsonx.data OpenSearch** and **IBM watsonx.ai** embeddings. Ingest documents from **IBM Cloud Object Storage**, parse them with IBM Docling, generate dense embeddings, and run hybrid search queries that outperform pure vector-only search.

> **Recommendation**: Use **hybrid search** (vector + BM25) rather than pure vector-only search. Combining dense semantic search with BM25 keyword matching consistently produces superior retrieval accuracy for RAG applications.

---

## When to Use

| Scenario | Building Block |
|---|---|
| Build a standalone search service (without LLM-generated answers) | [`opensearch/`](opensearch/) |
| Combine semantic embedding search with BM25 keyword search for best recall | [`opensearch/`](opensearch/) — hybrid mode |
| Power the retrieval layer for a RAG pipeline using OpenSearch as the backend | [`opensearch/`](opensearch/) |
| Need Astra DB vector collections with IBM watsonx.ai embeddings | [`datastax-astradb/`](datastax-astradb/) |

> **Hybrid Search vs Vector-only**: Hybrid search (k-NN + BM25) outperforms vector-only search for most RAG applications — it catches both semantic paraphrase matches and exact keyword matches.

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**
- **IBM watsonx.data OpenSearch** instance — note host, port, username, and password
- **IBM watsonx.ai** project — note Project ID and instance URL
- **IBM Cloud Object Storage** bucket (for ingestion)

### Quick Start — OpenSearch (recommended)

```bash
cd opensearch/assets/opensearch-data-ingestion
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, OPENSEARCH_HOST,
#            OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD, COS credentials
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Ingest documents:
```bash
curl -X POST http://localhost:8080/ingest \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"bucket_name": "my-docs", "index_name": "search_index", "embedding_model_id": "ibm/slate-125m-english-rtrvr"}'
```

Search:
```bash
curl -X POST http://localhost:8080/search \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is IBM watsonx?", "k": 5, "search_type": "hybrid"}'
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Hybrid Search building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of IBM watsonx.data OpenSearch k-NN index design, HNSW parameter tuning, hybrid search score fusion, and IBM watsonx.ai embedding integration.

**Install the Bob Mode** — give Bob an OpenSearch hybrid search specialist persona:
```powershell
# Windows
Copy-Item opensearch/bob-modes/base-modes/opensearch-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp opensearch/bob-modes/base-modes/opensearch-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **OpenSearch Builder** mode will appear in the mode selector.

**Install the Bob Skill** — teach Bob the OpenSearch hybrid search patterns:
```bash
unzip opensearch/bob-skills/opensearch-vector-search.zip
```
Open IBM Bob → Skills panel → enable `opensearch-vector-search`. Bob will use it as active context for every prompt in this workspace.

---

## Building Blocks

### 1. OpenSearch (Recommended)
**Location**: [`opensearch/`](opensearch/)
**IBM Products**: IBM watsonx.data (OpenSearch), IBM watsonx.ai, IBM COS
**Description**: Hybrid search engine on IBM watsonx.data managed OpenSearch — combines k-NN vector search with BM25 keyword search. Uses HNSW indexes via the k-NN plugin. This is the **recommended backend** for all new hybrid search and RAG projects.

**Quick Start**:
```bash
cd opensearch/assets/opensearch-data-ingestion
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, OPENSEARCH_HOST, OPENSEARCH_PASSWORD, COS credentials
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**Bob Assets**:
- `bob-modes/base-modes/opensearch-builder.zip` — OpenSearch hybrid search development mode
- `bob-skills/opensearch-vector-search.zip` — OpenSearch k-NN + hybrid search skill

[View Details →](opensearch/)

---

## Embedding Models

| Model ID | Dimension | Language | Use Case |
|---|---|---|---|
| `ibm/slate-125m-english-rtrvr` | 768 | English | Recommended for English RAG |
| `ibm/slate-30m-english-rtrvr` | 384 | English | Lightweight English RAG |
| `intfloat/multilingual-e5-large` | 1024 | Multi | Multilingual RAG |

## Search Strategy Comparison

| Approach | How It Works | Results |
|---|---|---|
| **Hybrid Search** (recommended) | Dense vector + BM25 keyword with score fusion | ✅ Best accuracy — catches both semantic and exact matches |
| Vector-only search | Dense vector similarity (cosine / ANN) | ⚠️ Misses keyword-specific queries |
| Keyword-only (BM25) | Term frequency / inverse document frequency | ⚠️ Misses paraphrase and semantic matches |

## k-NN Index Configuration (OpenSearch)

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
Ingestion Service (FastAPI)
        │
        ├─ IBM Docling parse + chunk
        │
        ├─ IBM watsonx.ai embed_documents()
        │   (ibm/slate-125m-english-rtrvr → 768-dim)
        │
        └─ opensearch-py bulk() insert
                │
                ▼
IBM watsonx.data OpenSearch
  (k-NN HNSW index)
        │
        ▼
Hybrid Search (k-NN + BM25)
Best retrieval accuracy for RAG
```

## IBM Cloud References

- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [OpenSearch k-NN Plugin](https://opensearch.org/docs/latest/search-plugins/knn/)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
