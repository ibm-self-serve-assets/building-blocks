# Data for AI — Building Blocks

## Overview

IBM's Data-for-AI building blocks organized by core capability, providing comprehensive solutions for AI data management, integration, intelligence, and retrieval. Every building block ships with **runnable assets** (FastAPI services, Python scripts), **Bob Modes** (AI assistant configurations), and **Bob Skills** (expert knowledge zips).

> **AI-tool agnostic**: All runnable assets work independently of any AI assistant. Bob modes and skills are optimised for IBM Bob but the patterns apply equally when using Claude, GitHub Copilot, or any other coding assistant.

---

## When to Use This Repository

Use these building blocks when you need to **accelerate delivery** of an IBM data or AI application. Pick the capability that matches your goal:

| I want to… | Go here |
|---|---|
| Build a RAG pipeline — ingest documents, embed, search, answer questions | [`retrieval/RAG/`](retrieval/RAG/) |
| Add hybrid vector + keyword search (OpenSearch) to my app | [`retrieval/vector-search/`](retrieval/vector-search/README.md) |
| Store and query documents with NoSQL (Cassandra-compatible) | [`retrieval/no-sql-database/`](retrieval/no-sql-database/) |
| Query across COS, Db2, S3 without copying data | [`retrieval/zero-copy/`](retrieval/zero-copy/) |
| Build AI-generated DataStage / ingestion pipelines | [`integration/data-pipeline-ai-generated/`](integration/data-pipeline-ai-generated/) |
| Set up real-time Kafka event streaming with Confluent | [`integration/data-streaming/`](integration/data-streaming/) |
| Monitor data pipeline health and lineage with IBM Databand | [`integration/data-observability/`](integration/data-observability/) |
| Validate data quality before it reaches an AI model | [`intelligence/data-quality/`](intelligence/data-quality/) |
| Track data lineage from source to model consumption | [`intelligence/data-lineage/`](intelligence/data-lineage/) |
| Convert natural language questions to SQL | [`intelligence/text2sql/`](intelligence/text2sql/) |

---

## Getting Started

### Step 1 — Pick a building block

Navigate to the folder that matches your use case from the table above. Read the `README.md` in that folder to understand exactly what it does, what IBM services it requires, and which assets are included.

### Step 2 — Check prerequisites

Each building block lists its required IBM services at the top of its README (e.g. IBM watsonx.ai, watsonx.data, IBM COS). Ensure you have:
- An **IBM Cloud account** with access to the listed services
- An **IBM Cloud API key** — create one at [IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+** installed locally (for FastAPI / script assets)

### Step 3 — Run the asset

Every building block with a runnable asset follows the same pattern:

```bash
# 1. Navigate to the asset directory
cd <building-block>/assets/<asset-name>

# 2. Copy the environment template and fill in your credentials
cp .env.example .env
# Edit .env with your IBM_API_KEY and service-specific values

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the service
python main.py        # or: uvicorn app.server:app --host 0.0.0.0 --port 8080
# API docs → http://localhost:8080/docs
```

### Step 4 — IBM Bob, Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant, purpose-built for IBM Cloud and watsonx development. Every building block ships **Bob Modes** and **Bob Skills** that give Bob deep expertise in that specific capability — so instead of asking generic questions, Bob already knows the APIs, schemas, patterns, and IBM Cloud specifics for what you're building.

- **Bob Mode** — a pre-built expert persona scoped to a single capability (e.g. RAG Builder, OpenSearch Hybrid Search, Text2SQL). Switch modes to get focused, context-aware assistance.
- **Bob Skill** — a reusable knowledge pack Bob loads into its context. Skills teach Bob the exact API calls, environment variable patterns, and IBM service integration details for this building block.

**Install a Bob Mode** — give Bob a specialist persona for this building block:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the new mode will appear in the mode selector. Switch to it before starting development.

**Install a Bob Skill** — teach Bob the details of this building block:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill. Bob will now use it as active context for every prompt in this workspace.

---

## Building Blocks

---

### Integration

Data pipeline management — from AI-generated ingestion to real-time streaming to end-to-end observability.

#### [Data Ingestion — AI Generated](integration/data-pipeline-ai-generated/README.md)

> AI-generated DataStage and Docling pipelines for structured and unstructured data

**IBM Products**: IBM DataStage · IBM UDI · IBM Docling · IBM COS
**Bob Mode**: `data-ingestion.zip` · **Bob Skills**: `data-ingestion-structured.zip`, `data-ingestion-unstructured.zip`

Describe your source and target in plain English — IBM Bob generates the complete ingestion pipeline. Covers relational databases via DataStage CDC connectors (Db2, PostgreSQL, MySQL, Oracle) and unstructured documents (PDFs, DOCX, HTML, images) via IBM Docling and UDI.

| Asset | Description |
|---|---|
| [`assets/udi-ingestion-opensearch/`](integration/data-pipeline-ai-generated/assets/udi-ingestion-opensearch/README.md) | IBM UDI + OpenSearch ingestion pipeline |
| `bob-skills/data-ingestion-structured.zip` | Bob generates DataStage CDC pipeline (structured sources) |
| `bob-skills/data-ingestion-unstructured.zip` | Bob generates Docling + UDI pipeline (documents) |

---

#### [Data Streaming](integration/data-streaming/README.md)

> Real-time event ingestion and stream processing with Confluent on IBM Cloud

**IBM Products**: Confluent (on IBM Cloud)
**Bob Skills**: `data-streaming-confluent.zip`

Continuous data flow with enterprise-grade schema governance, Flink SQL stream processing, and infrastructure-as-code provisioning via Terraform. Covers Kafka topics, Schema Registry (Avro / JSON / Protobuf), Confluent Connectors, and Python producer/consumer patterns.

| Asset | Description |
|---|---|
| `bob-skills/confluent-iac-terraform.zip` | Terraform IaC for Confluent environment provisioning |

---

#### [Data Observability](integration/data-observability/README.md)

> Pipeline health monitoring, lineage tracking, and alert management with IBM Databand

**IBM Products**: IBM Databand
**Bob Mode**: `data-observability-builder.zip` · **Bob Skills**: `databand-pipeline-setup.zip`

Monitor pipeline run health, surface data quality anomalies, enforce SLA thresholds, and maintain a complete OpenLineage lineage graph for all IBM Cloud data assets. Apply pre-built alert policies or emit OpenLineage events from any Python ETL, DataStage, or Spark job.

| Asset | Description |
|---|---|
| `assets/databand-pipeline-monitor/` | REST API client for pipeline run health + COS archiving |
| `assets/openlineage-emitter/` | Emit OpenLineage events from Python / DataStage / Spark |
| `assets/databand-alert-templates/` | Pre-built alert policies: null-rate, schema-drift, SLA-breach |

---

### Intelligence

Automated data quality, lineage governance, and natural language SQL for AI-ready data.

#### [Data Quality](intelligence/data-quality/README.md)

> Automated validation rules and quality scoring before data reaches AI models

**IBM Products**: IBM watsonx.data Intelligence
**Bob Mode**: `data-quality-builder.zip` · **Bob Skills**: `data-quality-rules.zip`

Define completeness, uniqueness, validity, consistency, and accuracy rules against any data asset in your watsonx.data Intelligence project. Execute rules asynchronously, surface quality scores, and profile column statistics to catch data issues before they reach AI models.

| Asset | Description |
|---|---|
| `assets/quality-rules-engine/` | FastAPI service — create rules, execute, score, profile |

---

#### [Data Lineage](intelligence/data-lineage/README.md)

> End-to-end lineage graph from source to AI model consumption

**IBM Products**: IBM watsonx.data Intelligence (Manta) · IBM Databand
**Bob Mode**: `data-lineage-builder.zip` · **Bob Skills**: `openlineage-instrumentation.zip`

Emit OpenLineage events from any Python ETL, IBM DataStage, or Apache Spark pipeline and query the resulting lineage graph for governance, impact analysis, and compliance reporting. Column-level impact analysis shows all downstream assets affected by a schema change.

| Asset | Description |
|---|---|
| `assets/openlineage-collector/` | FastAPI service — collect + forward OpenLineage events |
| `assets/lineage-impact-analyzer/` | CLI tool — query lineage graph, archive reports to IBM COS |

---

#### [Text2SQL](intelligence/text2sql/README.md)

> Natural language to SQL using IBM watsonx.data Intelligence

**IBM Products**: IBM watsonx.data Intelligence
**Bob Mode**: `text-to-sql.zip` · **Bob Skills**: `text2sql-metadata-enrichment.zip`, `text2sql-query-optimizer.zip`

Convert natural language questions to validated, executable SQL without writing a single line of SQL manually. Enrich table and column metadata (descriptions, synonyms, query examples) via the DAI REST API to maximize query accuracy.

| Asset | Description |
|---|---|
| `assets/applications/text_to_sql_app/` | FastAPI service — `/query` endpoint, Code Engine / OpenShift deploy |
| `assets/metadata_enrichment_text2sql/` | Metadata enrichment scripts for improved query accuracy |

---

### Retrieval

Efficient AI data access — RAG pipelines, hybrid search, NoSQL storage, and federated zero-copy analytics.

#### [RAG — Retrieval-Augmented Generation](retrieval/RAG/README.md)

> Complete end-to-end RAG pipeline with MCP server integration

**IBM Products**: IBM watsonx.ai · IBM watsonx.data (OpenSearch) · IBM COS
**Bob Modes**: `rag-builder.zip`, `rag-ingestion.zip`, `rag-retrieval.zip` · **Bob Skills**: `rag-pipeline-builder.zip`, `rag-mcp-server-builder.zip`

Ingest documents from IBM COS, generate dense embeddings with IBM watsonx.ai, store in OpenSearch, and serve hybrid search (vector + BM25) and Q&A via REST API or MCP server. Three focused Bob modes cover the full RAG lifecycle — pipeline design, ingestion, and retrieval tuning.

| Asset | Description |
|---|---|
| `assets/rag-accelerator/` | Full-featured RAG service — `/ingest`, `/query`, `/qna` REST endpoints |
| `assets/rag-ingestion-sse-mcp-server/` | MCP server — Bob or Claude triggers document ingestion as a tool |
| `assets/rag-retrieval-sse-mcp-server/` | MCP server — Bob or Claude queries the knowledge base as a tool |
| `assets/rag-retrieval-fastapi-server/` | Lightweight REST retrieval API — pair with your own ingestion pipeline |

---

#### [Hybrid Search — OpenSearch](retrieval/vector-search/opensearch/README.md)

> Vector + BM25 keyword hybrid search on IBM watsonx.data OpenSearch

**IBM Products**: IBM watsonx.data (OpenSearch) · IBM watsonx.ai · IBM COS
**Bob Mode**: `opensearch-builder.zip` · **Bob Skills**: `opensearch-vector-search.zip`

Build semantic vector search and hybrid search applications using IBM watsonx.data OpenSearch with IBM watsonx.ai embeddings. Hybrid search (k-NN + BM25) outperforms vector-only retrieval for real-world corpora. Covers k-NN index design, HNSW parameter tuning, and score normalization.

| Asset | Description |
|---|---|
| `assets/opensearch-data-ingestion/` | FastAPI service — ingest from IBM COS, generate embeddings, index to OpenSearch |

---

#### [NoSQL — Astra DB / watsonx.data DataStax](retrieval/no-sql-database/astradb/README.md)

> Large-scale NoSQL document storage with Cassandra compatibility

**IBM Products**: IBM HCD (Astra DB) · IBM watsonx.data DataStax
**Bob Mode**: `nosql-astradb-builder.zip` · **Bob Skills**: `astradb-nosql-design.zip`

Store and query large volumes of JSON documents without a fixed schema. Supports MongoDB-style filter expressions (`$eq`, `$in`, `$and`, `$or`) at scale via the `astrapy` Data API. Available as SaaS on IBM Cloud HCD (Astra DB) or on-premises via IBM watsonx.data DataStax.

| Asset | Description |
|---|---|
| `assets/astradb-nosql-crud/` | FastAPI service — full CRUD, filter queries, batch insert, vector search |

---

#### [Zero-Copy Lakehouse](retrieval/zero-copy/zero-copy-lakehouse/README.md)

> Federated analytics across COS, Db2, and S3 without data duplication

**IBM Products**: IBM watsonx.data (Iceberg / Delta Lake · Presto · Spark)
**Bob Mode**: `lakehouse-setup.zip` · **Bob Skills**: `watsonxdata-lakehouse.zip`, `iceberg-table-management.zip`

Register storage buckets and databases once, then query across all sources with standard SQL — no ETL, no data copying. Supports Apache Iceberg and Delta Lake open table formats with time-travel queries and schema evolution.

| Asset | Description |
|---|---|
| `assets/setup-lakehouse/` | Python automation script — provision buckets, register catalogs, create Iceberg schemas |
