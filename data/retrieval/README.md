# Retrieval Capabilities

This directory contains building blocks for data retrieval — enabling efficient data access through hybrid search, RAG pipelines, NoSQL storage, and federated analytics.

> **AI-tool agnostic**: All assets work with IBM Bob, Claude, GitHub Copilot, or any other AI coding assistant.

---

## When to Use

| Scenario | Building Block |
|---|---|
| Build a complete RAG Q&A system with document ingestion and hybrid search | [`RAG/`](RAG/) |
| Add hybrid vector + BM25 keyword search standalone (without full RAG) | [`vector-search/`](vector-search/) |
| Store and query large document sets with NoSQL / Cassandra-style storage | [`no-sql-database/`](no-sql-database/) |
| Run SQL across IBM COS, Db2, and S3 in a single query — no data copying | [`zero-copy/`](zero-copy/) |
| Need AI assistant (Bob, Claude) to trigger search or ingestion via tools | [`RAG/`](RAG/) — MCP servers |

> **RAG vs Hybrid Search**: Use **RAG** if you also need LLM-generated answers on top of search results, or MCP server tooling for AI assistants. Use **Hybrid Search** standalone if you only need a search API without Q&A generation.

---

## Getting Started

### Prerequisites

All retrieval building blocks require:
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**
- Access to the IBM service listed in the building block's README header

### Common Setup Pattern

```bash
# 1. Navigate to the asset
cd <building-block>/assets/<asset-name>

# 2. Configure credentials
cp .env.example .env
# Edit .env: IBM_API_KEY, WATSONX_PROJECT_ID, and service-specific vars

# 3. Install and run
pip install -r requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080   # or: python main.py
# Swagger docs → http://localhost:8080/docs
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs) so Bob already knows the APIs, schemas, and IBM Cloud patterns for the capability you're working on.

**Install a Bob Mode** — give Bob a specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the mode appears in the mode selector. Switch to it before starting development.

**Install a Bob Skill** — teach Bob the details of this building block:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill. Bob will use it as active context for every prompt in this workspace.

---

## Building Blocks

### 1. RAG (Retrieval-Augmented Generation)
**Location**: [`RAG/`](RAG/)
**IBM Products**: IBM watsonx.ai, IBM watsonx.data (OpenSearch), IBM Cloud Object Storage
**Product Components**: RAG Accelerator; OpenSearch; IBM watsonx.ai embeddings; MCP Servers (SSE)

Complete RAG pipeline with document ingestion, embedding generation, vector storage, and hybrid search. Includes MCP servers for AI assistant integration with OpenSearch as the recommended backend.

**Key Features**:
- Complete RAG pipeline — ingest from IBM COS → embed → store → search
- IBM watsonx.ai embedding generation (`ibm/slate-125m-english-rtrvr`)
- OpenSearch hybrid search backend (vector + BM25 keyword — best results)
- Hybrid search (semantic + BM25 keyword) for superior retrieval accuracy
- RAG ingestion and retrieval MCP servers (SSE transport)
- FastAPI REST API with Docker deployment
- IBM Bob, Claude, and other AI assistant integration via MCP

**Bob Assets**:
- `bob-modes/base-modes/rag-builder.zip` — End-to-end RAG pipeline builder mode
- `bob-modes/base-modes/rag-ingestion.zip` — RAG ingestion specialist mode
- `bob-modes/base-modes/rag-retrieval.zip` — RAG retrieval + generation specialist mode
- `bob-skills/rag-pipeline-builder.zip` — RAG pipeline design skill
- `bob-skills/rag-mcp-server-builder.zip` — MCP server development skill

[View Details →](RAG/)

---

### 2. Hybrid Search
**Location**: [`vector-search/`](vector-search/)
**IBM Products**: IBM watsonx.data (OpenSearch), IBM watsonx.ai
**Product Components**: OpenSearch k-NN; IBM watsonx.ai embeddings; IBM COS; IBM Docling

> **Recommended approach**: Use **hybrid search** (vector + BM25 text search) on **IBM watsonx.data OpenSearch** for best retrieval results. Pure vector-only search produces inferior results compared to hybrid search.

Build hybrid search solutions combining semantic vector search and BM25 keyword search with IBM watsonx.ai embeddings.

**Key Features**:
- Hybrid search (vector + BM25) on IBM watsonx.data managed OpenSearch
- IBM watsonx.ai embedding integration
- IBM COS document source with Docling parsing
- HNSW k-NN index design and parameter tuning
- Score normalisation and result ranking

**Bob Assets**:
- `opensearch/bob-modes/base-modes/opensearch-builder.zip` — OpenSearch hybrid search mode
- `opensearch/bob-skills/opensearch-vector-search.zip` — OpenSearch k-NN + hybrid search skill

[View Details →](vector-search/)

---

### 3. No-SQL Database
**Location**: [`no-sql-database/`](no-sql-database/)
**IBM Products**: IBM HCD (Astra DB / watsonx.data DataStax)
**Product Components**: Astra DB Data API; astrapy SDK; Apache Cassandra-compatible storage

> **Product note**: **Astra DB** is the SaaS offering; **DataStax** in **IBM watsonx.data** is the software option for on-premises or private cloud deployments.

Provides large-scale NoSQL storage with Cassandra compatibility using DataStax Astra DB — part of the IBM Cloud HCD (Hyper-Converged Database) portfolio. Supports document-based CRUD via the Data API and optional vector capabilities.

**Key Features**:
- Full CRUD via Astra DB Data API using `astrapy` SDK
- MongoDB-style filter expressions (`$eq`, `$gt`, `$in`, `$and`, `$or`)
- Bulk insert and delete (`insert_many`, `delete_many`)
- Serverless Cassandra-compatible storage (Astra DB SaaS)
- Software deployment via IBM watsonx.data DataStax
- FastAPI REST service with Docker deployment

**Bob Assets**:
- `astradb/bob-modes/base-modes/nosql-astradb-builder.zip` — NoSQL Astra DB mode
- `astradb/bob-skills/astradb-nosql-design.zip` — Document modeling + CRUD skill

[View Details →](no-sql-database/)

---

### 4. Zero Copy
**Location**: [`zero-copy/`](zero-copy/)
**IBM Products**: IBM watsonx.data
**Product Components**: Apache Iceberg; Delta Lake; Presto SQL engine; Apache Spark; IBM COS; IBM Db2; watsonx.data REST API v2

Federated analytics without copying data. Query across IBM COS, AWS S3, IBM Db2, PostgreSQL, and MySQL from a single **Presto** engine using open lakehouse formats — **Apache Iceberg** and **Delta Lake** — all via **IBM watsonx.data** — without data duplication.

**Key Features**:
- One-click watsonx.data setup via Python automation script
- IBM COS / AWS S3 / Azure ADLS bucket registration
- Db2, PostgreSQL, MySQL external database connection
- Apache Iceberg and Delta Lake table support with partition strategies and time-travel
- Presto federated SQL across all registered sources
- Iceberg compaction, snapshot management, and schema evolution

**Bob Assets**:
- `zero-copy-lakehouse/bob-modes/base-modes/lakehouse-setup.zip` — Lakehouse setup mode
- `zero-copy-lakehouse/bob-skills/watsonxdata-lakehouse.zip` — watsonx.data setup skill
- `zero-copy-lakehouse/bob-skills/iceberg-table-management.zip` — Iceberg / Delta Lake lifecycle skill

[View Details →](zero-copy/)

---

## Quick Start

1. Choose the retrieval capability that matches your AI application needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **RAG Question Answering**: Build complete RAG systems with document processing and hybrid search
- **AI Assistant Integration**: Connect RAG capabilities to AI assistants via MCP servers (IBM Bob, Claude, and others)
- **Hybrid Search**: Combine semantic vector search with BM25 keyword search for best retrieval accuracy
- **Scalable NoSQL Storage**: Document storage with Cassandra compatibility via IBM HCD (Astra DB / watsonx.data DataStax)
- **Federated Analytics**: Query data across IBM COS, Db2, and S3 without copying
- **Iceberg / Delta Lake Lakehouse**: Open table formats with time-travel and schema evolution
