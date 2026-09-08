# Data — Intelligent Data Platform Building Blocks

## Overview

IBM's **Data Building Blocks** provide a practical, composable foundation for making enterprise data **connected, contextual, trusted, and ready for analytics and AI**. The building blocks are organized around three use-case groups from the IBM Data sales play: **Context**, **Pipelines**, and **Query Engines**.

Every building block ships with **runnable assets** (FastAPI services, Python scripts), **Bob Modes** (AI assistant configurations), and **Bob Skills** (expert knowledge zips).

> **AI-tool agnostic**: All runnable assets work independently of any AI assistant. Bob modes and skills are optimised for IBM Bob but the patterns apply equally when using Claude, GitHub Copilot, or any other coding assistant.

---

## Building Block Map

| Use Case | Building Block | Path | Primary Products |
|---|---|---|---|
| **Context** | [Context Hub](context/context-hub/) | `context/context-hub/` | IBM Confluent + IBM watsonx.data + IBM watsonx.data intelligence |
| **Context** | [Real-Time Streaming](context/real-time-streaming/) | `context/real-time-streaming/` | IBM Confluent (Kafka + Flink + connectors + governance) |
| **Context** | [Metadata Enrichment & Data Quality](context/metadata-enrichment/) | `context/metadata-enrichment/` | IBM watsonx.data intelligence |
| **Context** | [Data Observability](context/data-observability/) | `context/data-observability/` | IBM watsonx.data integration + IBM Data Observability by Databand |
| **Pipelines** | [RAG](pipelines/rag/) | `pipelines/rag/` | IBM watsonx.data OpenRAG + OpenSearch |
| **Pipelines** | [UDI (Unstructured Data Integration)](pipelines/udi/) | `pipelines/udi/` | IBM watsonx.data integration + Docling for IBM watsonx |
| **Pipelines** | [Text2SQL](pipelines/text2sql/) | `pipelines/text2sql/` | IBM watsonx.data intelligence |
| **Pipelines** | [ETL / ELT](pipelines/etl/) | `pipelines/etl/` | IBM DataStage + IBM watsonx.data integration |
| **Pipelines** | [Data Sync](pipelines/data-sync/) | `pipelines/data-sync/` | IBM Aspera Sync |
| **Query Engines** | [Zero-Copy Lakehouse](query-engines/zero-copy-lakehouse/) | `query-engines/zero-copy-lakehouse/` | IBM watsonx.data (Presto + Spark + Iceberg) |
| **Query Engines** | [Serverless Vector](query-engines/serverless-vector/) | `query-engines/serverless-vector/` | IBM watsonx.data + Astra DB Serverless |

---

## Quick Selection Guide

| I want to… | Go here |
|---|---|
| Build a RAG pipeline — ingest documents, embed, search, answer questions | [`pipelines/rag/`](pipelines/rag/) |
| Ingest and prepare complex PDFs, tables or presentations for AI | [`pipelines/udi/`](pipelines/udi/) |
| Let business users query governed data in plain English (Text2SQL) | [`pipelines/text2sql/`](pipelines/text2sql/) |
| Build repeatable batch ETL/ELT using IBM DataStage | [`pipelines/etl/`](pipelines/etl/) |
| Synchronize large file repositories across WAN or cloud sites | [`pipelines/data-sync/`](pipelines/data-sync/) |
| Set up real-time Kafka event streaming with IBM Confluent | [`context/real-time-streaming/`](context/real-time-streaming/) |
| Combine streaming, lakehouse and metadata for a governed context layer | [`context/context-hub/`](context/context-hub/) |
| Add business terms, quality rules and descriptions to data assets | [`context/metadata-enrichment/`](context/metadata-enrichment/) |
| Monitor data pipeline health, detect failures and track SLAs | [`context/data-observability/`](context/data-observability/) |
| Query across COS, Db2, S3 without copying data | [`query-engines/zero-copy-lakehouse/`](query-engines/zero-copy-lakehouse/) |
| Store embeddings and run vector similarity search elastically | [`query-engines/serverless-vector/`](query-engines/serverless-vector/) |

---

## Getting Started

### Step 1 — Pick a building block

Navigate to the folder that matches your use case from the table above. Read the `README.md` in that folder to understand exactly what it does, what IBM services it requires, and which assets are included.

### Step 2 — Check prerequisites

Each building block lists its required IBM services at the top of its README. Ensure you have:
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

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant, purpose-built for IBM Cloud and watsonx development. Every building block ships **Bob Modes** and **Bob Skills** that give Bob deep expertise in that specific capability.

- **Bob Mode** — a pre-built expert persona scoped to a single capability. Switch modes to get focused, context-aware assistance.
- **Bob Skill** — a reusable knowledge pack Bob loads into its context. Skills teach Bob the exact API calls, environment variable patterns, and IBM service integration details for this building block.

**Install a Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the new mode will appear in the mode selector.

**Install a Bob Skill**:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## 1. Context

> Give applications, analytics, and AI systems the business and operational context they need at the moment they need it.

[Explore Context →](context/README.md)

### [Context Hub](context/context-hub/README.md)

> Combine real-time events, enterprise data, and governed metadata into a reusable context layer for AI and analytics

**IBM Products**: IBM Confluent · IBM watsonx.data · IBM watsonx.data intelligence
**Bob Mode**: `context-hub-builder.zip` · **Bob Skills**: `confluent-watsonxdata-context.zip`

Architectural pattern combining IBM Confluent streaming with IBM watsonx.data open lakehouse and IBM watsonx.data intelligence metadata enrichment. Uses the Confluent Apache Iceberg Sink Connector to materialize Kafka topic data as Iceberg tables, then enriches with governed business context.

---

### [Real-Time Streaming](context/real-time-streaming/README.md)

> Real-time event ingestion and stream processing with IBM Confluent on IBM Cloud

**IBM Products**: Confluent (on IBM Cloud)
**Bob Skills**: `data-streaming-confluent.zip`, `confluent-iac-terraform.zip`

Continuous data flow with enterprise-grade schema governance, Flink SQL stream processing, and infrastructure-as-code provisioning via Terraform. Covers Kafka topics, Schema Registry, Confluent Connectors, and Python producer/consumer patterns.

| Asset | Description |
|---|---|
| [`assets/supply-chain-risk-control-tower/`](context/real-time-streaming/assets/supply-chain-risk-control-tower/) | Supply chain risk control tower — Kafka, Flink SQL, schema governance, Terraform IaC |

---

### [Metadata Enrichment & Data Quality](context/metadata-enrichment/README.md)

> Automated data quality, lineage governance, and metadata enrichment for AI-ready data

**IBM Products**: IBM watsonx.data Intelligence · IBM Databand

[Explore Metadata Enrichment →](context/metadata-enrichment/README.md)

#### [Data Quality](context/metadata-enrichment/data-quality/README.md)

**IBM Products**: IBM watsonx.data Intelligence
**Bob Mode**: `data-quality-builder.zip` · **Bob Skills**: `data-quality-rules.zip`

Define completeness, uniqueness, validity, consistency, and accuracy rules against data assets in IBM watsonx.data Intelligence. Execute rules asynchronously, surface quality scores, and profile column statistics.

| Asset | Description |
|---|---|
| `assets/quality-rules-engine/` | FastAPI service — create rules, execute, score, profile |

#### [Data Lineage](context/metadata-enrichment/data-lineage/README.md)

**IBM Products**: IBM watsonx.data Intelligence (Manta) · IBM Databand
**Bob Mode**: `data-lineage-builder.zip` · **Bob Skills**: `openlineage-instrumentation.zip`

Emit OpenLineage events from any Python ETL, IBM DataStage, or Apache Spark pipeline and query the resulting lineage graph for governance, impact analysis, and compliance reporting.

| Asset | Description |
|---|---|
| `assets/openlineage-collector/` | FastAPI service — collect and forward OpenLineage events |
| `assets/lineage-impact-analyzer/` | CLI tool — query lineage graph, archive reports to IBM COS |

---

### [Data Observability](context/data-observability/README.md)

> Pipeline health monitoring, alert management, and data quality visibility with IBM Databand

**IBM Products**: IBM Databand
**Bob Mode**: `data-observability-builder.zip` · **Bob Skills**: `databand-pipeline-setup.zip`

Monitor pipeline run health, surface data quality anomalies, enforce SLA thresholds, and maintain a complete OpenLineage lineage graph for all IBM Cloud data assets.

| Asset | Description |
|---|---|
| `assets/databand-pipeline-monitor/` | REST API client for pipeline run health + COS archiving |
| `assets/openlineage-emitter/` | Emit OpenLineage events from Python / DataStage / Spark |
| `assets/databand-alert-templates/` | Pre-built alert policies: null-rate, schema-drift, SLA-breach |

---

## 2. Pipelines

> Prepare and move structured and unstructured data into forms that applications, search systems, analytics and AI can consume.

[Explore Pipelines →](pipelines/README.md)

### [RAG — Retrieval-Augmented Generation](pipelines/rag/README.md)

> Complete end-to-end RAG pipeline with MCP server integration

**IBM Products**: IBM watsonx.ai · IBM watsonx.data (OpenSearch) · IBM COS
**Bob Modes**: `rag-builder.zip`, `rag-ingestion.zip`, `rag-retrieval.zip` · **Bob Skills**: `rag-pipeline-builder.zip`, `rag-mcp-server-builder.zip`

Ingest documents from IBM COS, generate dense embeddings with IBM watsonx.ai, store in OpenSearch, and serve hybrid search (vector + BM25) and Q&A via REST API or MCP server.

| Asset | Description |
|---|---|
| `assets/rag-accelerator/` | Full-featured RAG service — `/ingest`, `/query`, `/qna` REST endpoints |
| `assets/rag-ingestion-sse-mcp-server/` | MCP server — triggers document ingestion as a tool |
| `assets/rag-retrieval-sse-mcp-server/` | MCP server — queries the knowledge base as a tool |
| `assets/rag-retrieval-fastapi-server/` | Lightweight REST retrieval API |

---

### [UDI — Unstructured Data Integration](pipelines/udi/README.md)

> AI-generated DataStage and Docling pipelines for structured and unstructured data

**IBM Products**: IBM DataStage · IBM UDI · IBM Docling · IBM COS
**Bob Mode**: `data-ingestion.zip` · **Bob Skills**: `data-ingestion-structured.zip`, `data-ingestion-unstructured.zip`

Describe your source and target in plain English — IBM Bob generates the complete ingestion pipeline. Covers relational databases via DataStage CDC connectors and unstructured documents (PDFs, DOCX, HTML, images) via IBM Docling and UDI.

| Asset | Description |
|---|---|
| [`assets/udi-ingestion-opensearch/`](pipelines/udi/assets/udi-ingestion-opensearch/) | IBM UDI + OpenSearch ingestion pipeline |

---

### [Text2SQL](pipelines/text2sql/README.md)

> Natural language to SQL using IBM watsonx.data Intelligence

**IBM Products**: IBM watsonx.data Intelligence
**Bob Mode**: `text-to-sql.zip` · **Bob Skills**: `text2sql-metadata-enrichment.zip`, `text2sql-query-optimizer.zip`

Convert natural language questions to validated, executable SQL. Enrich table and column metadata to maximize query accuracy, then submit plain-English queries and receive SQL results.

| Asset | Description |
|---|---|
| `assets/applications/text_to_sql_app/` | FastAPI service — `/query` endpoint, Code Engine / OpenShift deploy |
| `assets/metadata_enrichment_text2sql/` | Metadata enrichment scripts for improved query accuracy |

---

### [ETL / ELT with DataStage](pipelines/etl/README.md)

> Governed batch data integration flows using IBM DataStage

**IBM Products**: IBM DataStage · IBM watsonx.data integration · IBM watsonx.data
**Bob Mode**: `datastage-etl-builder.zip` · **Bob Skills**: `datastage-flow-design.zip`, `datastage-watsonxdata-integration.zip`

Build visual ETL/ELT flows with enterprise connectors, transformation stages, and operational scheduling. Supports ETL (transform-before-load) and ELT (load-then-transform at lakehouse compute) patterns.

---

### [Data Sync with IBM Aspera](pipelines/data-sync/README.md)

> High-speed WAN file and repository synchronization

**IBM Products**: IBM Aspera Sync
**Bob Mode**: `aspera-sync-builder.zip` · **Bob Skills**: `aspera-sync-configuration.zip`

Synchronize large file sets and repositories securely across WAN and hybrid environments using IBM Aspera's FASP transport protocol — maintaining near-wire-speed regardless of distance or latency.

---

## 3. Query Engines

> Execute analytics and retrieval workloads on the engine best suited to the data and latency profile.

[Explore Query Engines →](query-engines/README.md)

### [Zero-Copy Lakehouse](query-engines/zero-copy-lakehouse/README.md)

> Federated analytics across COS, Db2, and S3 without data duplication

**IBM Products**: IBM watsonx.data (Iceberg · Presto · Spark)
**Bob Mode**: `lakehouse-setup.zip` · **Bob Skills**: `watsonxdata-lakehouse.zip`, `iceberg-table-management.zip`

Register storage buckets and databases once, then query across all sources with standard SQL — no ETL, no data copying. Supports Apache Iceberg and Delta Lake open table formats with time-travel queries and schema evolution.

| Asset | Description |
|---|---|
| `assets/setup-lakehouse/` | Python automation script — provision buckets, register catalogs, create Iceberg schemas |

---

### [Serverless Vector](query-engines/serverless-vector/README.md)

> Elastic vector storage for semantic search, RAG and agent memory

**IBM Products**: IBM watsonx.data + Astra DB Serverless
**Bob Mode**: `astradb-vector-builder.zip` · **Bob Skills**: `astradb-vector-setup.zip`

Provision Astra DB Serverless directly from the IBM watsonx.data infrastructure experience. Store embeddings and run vector similarity search without managing clusters. Includes a runnable FastAPI ingestion service.

| Asset | Description |
|---|---|
| `assets/astradb-vector-ingestion/` | FastAPI service — ingest from IBM COS, generate watsonx.ai embeddings, store in Astra DB |

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM watsonx.data](https://www.ibm.com/products/watsonx-data)** | Open hybrid data platform — lakehouse, Presto, Spark, Iceberg, OpenRAG |
| **[IBM Confluent](https://www.ibm.com/products/confluent)** | Managed Kafka + Flink + connectors + Stream Governance for real-time data |
| **[IBM watsonx.data integration](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integration)** | DataStage ETL, UDI, data replication and observability |
| **[IBM watsonx.data intelligence](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-enriching-your-assets)** | Metadata enrichment, business glossary, Text2SQL |
| **[IBM Aspera Sync](https://www.ibm.com/products/aspera/sync)** | High-speed WAN file and repository synchronization |
| **[Docling for IBM watsonx](https://www.ibm.com/products/docling)** | Advanced document conversion for complex PDFs and unstructured content |
| **[Astra DB Serverless](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html)** | Serverless vector and NoSQL document database for embeddings, semantic search and document storage |
| **[IBM HCD (Hyper Converged Database)](https://cloud.ibm.com/catalog/services/hyper-converged-database)** | IBM Cloud managed service for Astra DB (SaaS) and DataStax (software) |
