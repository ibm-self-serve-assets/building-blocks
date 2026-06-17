# RAG (Retrieval-Augmented Generation)

**Core Capability**: Retrieval
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM Cloud Object Storage
**Product Components**: RAG Accelerator; IBM watsonx.ai Embeddings; MCP Servers (SSE transport); FastAPI; OpenSearch; IBM COS

## Overview

Complete end-to-end RAG pipeline — ingest documents from **IBM Cloud Object Storage**, generate dense embeddings with **IBM watsonx.ai**, store in **IBM watsonx.data OpenSearch**, and serve **hybrid search** (vector + BM25 keyword) and Q&A queries via REST API or MCP server. Includes focused Bob modes for ingestion and retrieval specialists, plus MCP server assets for AI assistant integration.

> **AI-tool agnostic**: MCP servers work with **IBM Bob**, **Claude**, and other MCP-compatible AI assistants.

---

## When to Use

| Scenario | Asset |
|---|---|
| Need a full-featured RAG service with `/ingest`, `/query`, and `/qna` REST endpoints | [`assets/rag-accelerator/`](assets/rag-accelerator/) |
| Need an AI assistant (Bob, Claude) to trigger ingestion via MCP tools | [`assets/rag-ingestion-sse-mcp-server/`](assets/rag-ingestion-sse-mcp-server/) |
| Need an AI assistant (Bob, Claude) to query the knowledge base via MCP tools | [`assets/rag-retrieval-sse-mcp-server/`](assets/rag-retrieval-sse-mcp-server/) |
| Need a lightweight REST retrieval API to pair with your own ingestion pipeline | [`assets/rag-retrieval-fastapi-server/`](assets/rag-retrieval-fastapi-server/) |
| Need Bob modes and skills specifically for RAG pipeline development | [`bob-modes/`](bob-modes/) / [`bob-skills/`](bob-skills/) |

> **Which asset to start with?** Start with the **RAG Accelerator** if you want a single service that handles both ingestion and Q&A. Use the **MCP servers** when you want Bob or Claude to be able to call ingestion/retrieval as AI tools.

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**
- **IBM watsonx.ai** project — note your Project ID and instance URL
- **IBM watsonx.data OpenSearch** instance — note host, port, username, and password
- **IBM Cloud Object Storage** bucket — note endpoint, instance CRN, and bucket name

### Quickest Path — RAG Accelerator (all-in-one)

```bash
cd assets/rag-accelerator
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, WATSONX_URL,
#            OPENSEARCH_HOST, OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD,
#            COS_ENDPOINT, COS_INSTANCE_CRN, COS_BUCKET_NAME
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Then ingest your first documents:
```bash
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{"bucket_name": "my-docs", "directory": "documents/", "index_name": "my_index"}'
```

Then ask a question:
```bash
curl -X POST http://localhost:8080/qna \
  -H "Content-Type: application/json" \
  -d '{"query": "What is IBM watsonx.data?", "k": 5}'
```

### MCP Server Path — AI assistant integration

```bash
# Ingestion MCP server
cd assets/rag-ingestion-sse-mcp-server
cp .env.example .env
# Edit .env: IBM_API_KEY, VECTOR_DB_TYPE=opensearch, OPENSEARCH_*, COS_* vars
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint → http://localhost:8080/mcp
# Connect Bob or Claude to this URL as an MCP server
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The RAG building block ships **three focused Bob Modes** — each scoped to a different stage of the RAG lifecycle — plus **two Bob Skills** that teach Bob the exact watsonx.ai embedding calls, OpenSearch indexing patterns, and MCP server tool design used in these assets.

**Install a Bob Mode** — give Bob a RAG specialist persona:
```powershell
# Windows — copy the mode(s) you want
Copy-Item bob-modes/base-modes/rag-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
Copy-Item bob-modes/base-modes/rag-ingestion.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
Copy-Item bob-modes/base-modes/rag-retrieval.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/rag-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
cp bob-modes/base-modes/rag-ingestion.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
cp bob-modes/base-modes/rag-retrieval.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the modes appear in the mode selector:
- **RAG Builder** — use when designing the full pipeline end-to-end
- **RAG Ingestion Builder** — use when building or debugging document ingestion
- **RAG Retrieval Builder** — use when tuning search quality or building the Q&A layer

**Install Bob Skills** — teach Bob the RAG asset details:
```bash
unzip bob-skills/rag-pipeline-builder.zip
unzip bob-skills/rag-mcp-server-builder.zip
```
Open IBM Bob → Skills panel → enable both skills. Bob will use them as active context for every prompt in this workspace.

---

## Building Blocks

### 1. RAG Accelerator
**Location**: `assets/rag-accelerator/`
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM COS, IBM Cloud IAM
**Description**: Full-featured FastAPI RAG service — ingest documents from IBM COS, generate IBM watsonx.ai embeddings, index vectors in OpenSearch, and expose `/ingest`, `/query`, and `/qna` endpoints. Supports HNSW dense-only and hybrid (dense + sparse) search modes.

**Quick Start**:
```bash
cd assets/rag-accelerator
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, OPENSEARCH_* credentials, COS_ENDPOINT
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/ingest` | Ingest documents from IBM COS into OpenSearch |
| `POST` | `/query` | Hybrid search — returns top-K chunks (vector + BM25) |
| `POST` | `/qna` | RAG Q&A — retrieves context, generates answer with watsonx.ai |
| `GET`  | `/index_management/indices` | List all indexes |
| `POST` | `/index_management/create` | Create a new index |
| `DELETE` | `/index_management/delete` | Drop an index |

**Example — Ingest documents**:
```bash
curl -X POST http://localhost:8080/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "bucket_name": "my-docs-bucket",
    "directory": "documents/",
    "index_name": "ibm_knowledge_base",
    "embedding_model_id": "ibm/slate-125m-english-rtrvr"
  }'
```

**Example — Ask a question**:
```bash
curl -X POST http://localhost:8080/qna \
  -H "Content-Type: application/json" \
  -d '{"query": "What is IBM watsonx.data?", "k": 5}'
```

---

### 2. RAG Ingestion MCP Server
**Location**: `assets/rag-ingestion-sse-mcp-server/`
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM COS, IBM Cloud IAM
**Description**: MCP server (SSE transport, FastMCP) that exposes ingestion tools — `ingest_from_cos`, `list_indexed_documents`, `delete_document` — so AI assistants (IBM Bob, Claude) can trigger RAG ingestion without a REST client.

**Quick Start**:
```bash
cd assets/rag-ingestion-sse-mcp-server
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, VECTOR_DB_TYPE, OPENSEARCH_* credentials
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint → http://localhost:8080/mcp
```

---

### 3. RAG Retrieval MCP Server
**Location**: `assets/rag-retrieval-sse-mcp-server/`
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM Cloud IAM
**Description**: MCP server (SSE transport) that exposes retrieval tools — `search_documents`, `keyword_search`, `ask_question` — enabling AI assistants to query the OpenSearch index directly and perform RAG Q&A over ingested knowledge.

**Quick Start**:
```bash
cd assets/rag-retrieval-sse-mcp-server
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, VECTOR_DB_TYPE, OPENSEARCH_* credentials
pip install -r app/requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080
# MCP endpoint → http://localhost:8080/mcp
```

---

### 4. RAG Retrieval FastAPI Server
**Location**: `assets/rag-retrieval-fastapi-server/`
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM Cloud IAM
**Description**: Lightweight FastAPI server focused exclusively on retrieval — hybrid search (vector + BM25 keyword) against an already-ingested OpenSearch index. Designed to pair with the RAG Accelerator or the MCP ingestion server.

**Quick Start**:
```bash
cd assets/rag-retrieval-fastapi-server
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, VECTOR_DB_TYPE, OPENSEARCH_* credentials
pip install -r requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080
# Swagger UI → http://localhost:8080/docs
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/retrieve` | Hybrid search — returns top-K chunks (vector + BM25) |
| `POST` | `/keyword_search` | BM25 keyword-only search |
| `GET`  | `/health` | Server health and configuration status |

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: Three focused AI modes for RAG development
  - **RAG Builder** — [`bob-modes/base-modes/rag-builder.zip`](./bob-modes/base-modes/rag-builder.zip): End-to-end RAG expert — pipeline architecture, hybrid search design, chunking strategy, embedding model choice, MCP server design
  - **RAG Ingestion Builder** — [`bob-modes/base-modes/rag-ingestion.zip`](./bob-modes/base-modes/rag-ingestion.zip): Focused ingestion specialist — IBM COS document loading, chunking, watsonx.ai embedding, OpenSearch indexing, MCP ingestion tool design
  - **RAG Retrieval Builder** — [`bob-modes/base-modes/rag-retrieval.zip`](./bob-modes/base-modes/rag-retrieval.zip): Focused retrieval specialist — hybrid search queries, reranking, watsonx.ai generation, RAG evaluation (RAGAS), streaming SSE responses
  - **Install**: copy the zip to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `rag-pipeline-builder` | [`bob-skills/rag-pipeline-builder.zip`](./bob-skills/rag-pipeline-builder.zip) | Complete RAG pipeline design, IBM watsonx.ai embedding integration, OpenSearch HNSW + hybrid search design, chunking strategy selection, FastAPI service patterns |
| `rag-mcp-server-builder` | [`bob-skills/rag-mcp-server-builder.zip`](./bob-skills/rag-mcp-server-builder.zip) | MCP server development (SSE transport, FastMCP), RAG ingestion + retrieval tool design, IBM Bob / Claude integration, deployment to IBM Code Engine |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Embedding Models

| Model ID | Dimension | Language | Use Case |
|---|---|---|---|
| `ibm/slate-125m-english-rtrvr` | 768 | English | Recommended for English RAG |
| `ibm/slate-30m-english-rtrvr` | 384 | English | Lightweight English RAG |
| `intfloat/multilingual-e5-large` | 1024 | Multi | Multilingual RAG |

## Search Mode Comparison

| Feature | Hybrid Search (recommended) | Vector-only |
|---|---|---|
| Index type | HNSW (cosine) + BM25 | HNSW (cosine) |
| Retrieval quality | ✅ Best — catches semantic + exact matches | ⚠️ Misses keyword-specific queries |
| IBM deployment | IBM watsonx.data managed OpenSearch | IBM watsonx.data managed OpenSearch |
| Auth pattern | username + password over SSL | username + password over SSL |

## Architecture

```
IBM Cloud Object Storage
        │
        │  ibm-cos-sdk / MCP ingest_from_cos
        ▼
RAG Ingestion (FastAPI / MCP Server)
        │
        ├─ LangChain document loaders + text splitters
        │   (PDF, DOCX, PPTX, HTML, MD, TXT)
        │
        ├─ IBM watsonx.ai embed_documents()
        │   (ibm/slate-125m-english-rtrvr → 768-dim)
        │
        └─ OpenSearch bulk index
                │
                └─ k-NN HNSW index (cosine, lucene engine)
                        │
                        ▼
        RAG Retrieval (FastAPI / MCP Server)
                │
                ├─ Hybrid search (vector + BM25) — best results
                ├─ BM25 keyword search
                │
                └─ IBM watsonx.ai text generation
                    (ibm/granite-13b-instruct-v2)
                        │
                        ▼
                Generated Answer + Source Citations
```

## IBM Cloud References

- [IBM watsonx.ai Documentation](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-overview.html)
- [IBM watsonx.ai Embedding Models](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/fm-models-embed.html)
- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/docs)
