# Data Pipeline AI-Generated Bob Skills

Bob skills for AI-generated **structured** and **unstructured** data ingestion pipelines using **IBM DataStage**, **IBM UDI (Unstructured Data Integration)**, and **IBM Docling** on IBM Cloud.

## Overview

These skills empower IBM Bob to generate production-ready data ingestion pipelines — ingesting structured relational data (Db2, PostgreSQL, MySQL, Oracle) and unstructured documents (PDF, DOCX, images) into **IBM watsonx.data** Iceberg tables and OpenSearch vector stores.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `data-ingestion-structured` | [`data-ingestion-structured.zip`](data-ingestion-structured.zip) | Ingesting structured relational data into IBM watsonx.data using IBM DataStage, CDC, and batch patterns |
| `data-ingestion-unstructured` | [`data-ingestion-unstructured.zip`](data-ingestion-unstructured.zip) | Ingesting unstructured documents (PDF, DOCX, images) from IBM COS using IBM UDI and Docling |

---

### `data-ingestion-structured`

A comprehensive skill for building structured data ingestion pipelines:

- IBM Cloud IAM authentication with automatic token refresh
- IBM DataStage batch and incremental load job configuration
- IBM Data Replication CDC (Change Data Capture) for Db2, PostgreSQL, Oracle, MySQL
- RDBMS-to-Iceberg type mapping and schema evolution handling
- IBM COS staging area patterns for bulk Parquet loads
- Presto `INSERT INTO ... SELECT` from COS staging to Iceberg
- Error handling, retry logic, and dead-letter queue patterns
- IBM watsonx.data REST API v2 integration

### `data-ingestion-unstructured`

A comprehensive skill for building unstructured document ingestion pipelines:

- IBM UDI (Unstructured Data Integration) DataStage connector configuration
- IBM Docling document parsing for PDF, DOCX, images (OCR)
- `unstructured.io` multi-format parsing (HTML, PPTX, email, Excel) as fallback
- Chunking strategies: fixed-size, semantic, sentence-based
- IBM watsonx.ai embedding generation for vectorised chunks
- IBM COS document source with `ibm-cos-sdk` IAM OAuth download
- Metadata extraction: title, source path, page number, chunk_seq
- Target support: IBM watsonx.data Iceberg (metadata) + OpenSearch (vectors)

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip data-ingestion-structured.zip
unzip data-ingestion-unstructured.zip
```

This will create:
```
.bob/skills/data-ingestion-structured/SKILL.md
.bob/skills/data-ingestion-unstructured/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What data ingestion skills do you have active?"*

---

## Usage Examples

### data-ingestion-structured
- *"Generate an IBM DataStage batch ingestion job from PostgreSQL into an IBM watsonx.data Iceberg table"*
- *"Set up CDC for IBM Db2 using IBM Data Replication with Kafka as the target"*
- *"Create a Python script for incremental load from MySQL to Iceberg using watermarks"*

### data-ingestion-unstructured
- *"Configure an IBM UDI DataStage flow to ingest PDFs from IBM COS into OpenSearch"*
- *"Generate a Docling document parsing script for scanned PDFs with OCR"*
- *"Write a chunking pipeline that splits DOCX files into 512-token chunks with 128-token overlap"*

---

## What Bob Can Help You Build

1. **DataStage Job Configs**: Batch, incremental, and CDC job configurations
2. **CDC Subscriptions**: IBM Data Replication log-mining setup for Db2, PostgreSQL, Oracle
3. **Type Mapping**: RDBMS → Iceberg type conversion tables
4. **Document Parsers**: Docling and `unstructured.io` parsing pipelines
5. **Chunking Pipelines**: Adaptive text splitting with metadata extraction
6. **COS-to-Iceberg Flows**: Staging → Presto INSERT INTO patterns

---

## Prerequisites

Before using these skills, ensure you have:

- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- IBM watsonx.data instance (Iceberg catalog + Presto engine)
- IBM DataStage service (for structured ingestion)
- IBM Cloud Object Storage bucket (for unstructured document source)
- IBM watsonx.ai project (for embedding generation in unstructured flows)

## Skill Capabilities Summary

| Capability | data-ingestion-structured | data-ingestion-unstructured |
|---|---|---|
| IAM Authentication | ✅ | ✅ |
| IBM DataStage Jobs | ✅ | ✅ |
| CDC (Db2, PG, Oracle) | ✅ | — |
| RDBMS Type Mapping | ✅ | — |
| PDF/DOCX Parsing | — | ✅ |
| IBM Docling OCR | — | ✅ |
| Chunking & Embedding | — | ✅ |
| OpenSearch Target | — | ✅ |
| Iceberg Target | ✅ | ✅ |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/data-ingestion-structured/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

## Related

- [`../bob-modes/`](../bob-modes/) — Data Ingestion Builder Bob Mode
- [`../README.md`](../README.md) — AI-Generated Data Pipeline building block overview
- [`../assets/`](../assets/) — Deployable UDI OpenSearch ingestion assets
