# NL2SQL — Text2SQL Schema Retriever & SQL Executor

A production-ready Text2SQL schema ingestion, semantic retrieval, and safe SQL execution system built for enterprise databases (PostgreSQL and IBM Db2). Backed by **OpenSearch k-NN** (production) and **pgvector** (alternative), with embeddings generated via **IBM watsonx.ai Granite** or local **sentence-transformers**.

---

## Directory Structure

```text
NL2SQL/
├── .env.example                  ← single consolidated env file for ALL modules
├── setup.py                      ← unified one-time setup entry point
├── test_schema_retriever.py      ← integration smoke test for the retriever API
│
├── setup/                        ── One-time backend initialisation ──────────
│   ├── opensearch/               # Creates the OpenSearch k-NN index
│   │   ├── opensearch_index_mapping.py
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   └── pgvector/                 # Bootstraps the PostgreSQL pgvector schema
│       ├── bootstrap_embeddings_schema.py
│       ├── sql/
│       │   ├── pgvector_schema.sql
│       │   └── embedding_schema.sql
│       ├── requirements.txt
│       ├── .env.example
│       └── README.md
│
├── embedding/                    ── Schema introspection & ingestion pipeline ─
│   ├── ingest.py                 # Unified entry point (auto-selects backend)
│   ├── ingest_opensearch.py      # OpenSearch ingestion pipeline (multi-source)
│   ├── ingest_pgvector.py        # pgvector ingestion pipeline
│   ├── metadata_enricher.py      # Schema metadata enricher (Markdown, YAML, JSON)
│   ├── embedders.py              # watsonx Granite & sentence-transformers providers
│   ├── connectors/               # Live database introspection connectors
│   │   ├── __init__.py
│   │   ├── base.py               # BaseConnector and SchemaDoc data models
│   │   ├── postgresql.py         # PostgreSQL catalog introspector
│   │   └── db2.py                # IBM Db2 catalog introspector
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── metadata/                     ── Optional external schema metadata ─────────
│   └── schema_metadata.md        # Markdown schema descriptions & column hints
│
├── backend/                      ── Deployed microservices (Code Engine) ──────
│   ├── schema_retriever/         # Schema Retrieval API (queried by LLM agents)
│   │   ├── schema_retriever.py              # Unified entry point
│   │   ├── schema_retriever_opensearch.py   # FastAPI OpenSearch retriever
│   │   ├── schema_retriever_pgvector.py     # FastAPI pgvector retriever
│   │   ├── reranker.py                      # Cross-Encoder & FlashRank re-ranking
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   └── sql_executor/             # Hardened Read-Only SQL Execution API
│       ├── tool_sql_executor.py  # FastAPI read-only SQL runner
│       ├── sql_validation.py     # AST-based SQL safety checks
│       ├── requirements.txt
│       ├── .env.example
│       └── README.md
│
├── docker-build/                 ── Containerisation & Code Engine deployment ─
│   ├── deploy.sh                 # One-shot build, ICR push, and CE deploy script
│   ├── README.md
│   └── backend/
│       ├── schema-retriever/     # Dockerfile, .dockerignore, build.sh, ce-app.yaml
│       └── sql-executor/         # Dockerfile, .dockerignore, build.sh, ce-app.yaml, openspec.json
│
└── tests/                        # Unit tests
    ├── test_enrichment_and_reranker.py
    ├── test_pii_masking.py
    ├── test_session6_improvements.py
    ├── test_sql_validation.py
    └── requirements.txt
```

---

## Configuration — single `.env` file

Copy the root `.env.example` **once** and fill in your values:

```bash
cp .env.example .env
# Edit .env with your credentials
```

Every module (`setup.py`, `embedding/ingest.py`, `backend/schema_retriever/`, `backend/sql_executor/`) automatically finds this file at the `NL2SQL/` root. A module-local `.env` (placed inside a sub-folder) still takes precedence if you need per-module overrides.

---

## Quickstart

### 1. Install dependencies

Each module has its own `requirements.txt`. Install only what you need:

```bash
# Setup (OpenSearch)
pip install -r setup/opensearch/requirements.txt

# Embedding
pip install -r embedding/requirements.txt

# Backend services
pip install -r backend/schema_retriever/requirements.txt
pip install -r backend/sql_executor/requirements.txt
```

### 2. Create the vector index / table (one-time)

```bash
# OpenSearch backend (default)
VECTOR_BACKEND=opensearch python setup.py

# pgvector backend
VECTOR_BACKEND=pgvector python setup.py
```

### 3. Ingest schemas

```bash
python embedding/ingest.py
```

### 4. Start the Schema Retriever API

```bash
uvicorn backend.schema_retriever.schema_retriever:app --host 0.0.0.0 --port 8080
# or, running directly from the module directory:
cd backend/schema_retriever && uvicorn schema_retriever:app --host 0.0.0.0 --port 8080
```

### 5. Start the SQL Executor API

```bash
cd backend/sql_executor && uvicorn tool_sql_executor:app --host 0.0.0.0 --port 8000
```

---

## API Summary

### Schema Retriever (`:8080`)
- `POST /retrieve-schema` — semantic k-NN search over schema embeddings (with optional 2nd-stage Cross-Encoder re-ranking and FK relationship expansion)
- `POST /retrieve-schema/hybrid` — hybrid k-NN + BM25 keyword search (script_score)
- `POST /retrieve-schema/rrf` — Reciprocal Rank Fusion of vector and BM25 rankings
- `GET  /health` — liveness and backend connectivity check

### Schema Metadata Enrichment (Ingestion)
Enrich technical database catalog metadata using external definitions:
- Formats: Markdown (`.md`), YAML (`.yaml`), JSON (`.json`)
- Supported properties: business purpose descriptions (`natural_language_hint`), table comments, column definitions, and discrete domain values (`enum_values`).
- Controlled via `METADATA_ENRICHMENT_ENABLED` and `METADATA_ENRICHMENT_FILE`.

### 2nd-Stage Re-Ranking (Retrieval)
- Supported re-rankers: `cross-encoder` (sentence-transformers), `flashrank` (CPU-optimized), or `none`.
- Controlled via `RERANK_ENABLED`, `RERANK_PROVIDER`, `RERANK_MODEL`, `RERANK_TOP_N`, and `RERANK_DEVICE`.

### SQL Executor (`:8000`)
- `POST /run-sql` — executes read-only SQL (`SELECT`, `EXPLAIN`, `WITH … SELECT`) with timeout, AST-based validation, AST limit capping, and optional EXPLAIN cost gating
- `GET  /health` — connection pool and target database health check (returns 503 when database is unreachable)

### Connection Pooling & High Concurrency
- **SQL Executor**: Backed by `psycopg2.pool.ThreadedConnectionPool` configured with `POOL_MIN` and `POOL_MAX` (default 10) matching container concurrency.
- **pgvector Retriever**: Backed by `psycopg2.pool.ThreadedConnectionPool` with modern FastAPI `lifespan` management and clean pool closure on teardown.
- **OpenSearch Retriever**: Utilizes persistent HTTP keep-alive connection pooling with asynchronous non-blocking executor dispatch.

---

## Deployment to IBM Cloud Code Engine

```bash
cd docker-build
export ICR_NAMESPACE=your-namespace
export CE_PROJECT=your-code-engine-project
chmod +x deploy.sh backend/schema-retriever/build.sh backend/sql-executor/build.sh
./deploy.sh
```

See [`docker-build/README.md`](docker-build/README.md) for full deployment instructions.
