# UDI Bob Skills

Bob skills for **Unstructured Data Integration (UDI)** pipelines using **IBM UDI**, **IBM Docling**, and **IBM Cloud Object Storage** on IBM Cloud.

> **Scope note**: This building block covers unstructured document ingestion. For structured relational database batch patterns, see the [`../etl/`](../etl/) building block and its associated Bob skills.

## Overview

These skills empower IBM Bob to configure UDI flows, parse complex documents with Docling, chunk and embed content, and index prepared document chunks into OpenSearch for downstream AI and RAG use.

## Available Skills for This Building Block

| Skill | Zip | Use When |
|---|---|---|
| `data-ingestion-unstructured` | [`data-ingestion-unstructured.zip`](data-ingestion-unstructured.zip) | Ingesting unstructured documents (PDF, DOCX, images) from IBM COS using IBM UDI and Docling |
| `udi-opensearch` | [`udi-opensearch.zip`](udi-opensearch.zip) | UDI + OpenSearch pipeline setup: connection registration, flow creation, ingestion execution |

> **Also present — not for UDI**: The `data-ingestion-structured.zip` skill (IBM DataStage batch ingestion, CDC patterns) is in this directory for convenience. It covers structured relational data ingestion, not unstructured document integration. Use it alongside the [ETL / ELT](../etl/README.md) building block.

---

### `data-ingestion-unstructured`

A skill for building unstructured document ingestion pipelines:

- IBM UDI (Unstructured Data Integration) flow configuration
- IBM Docling document parsing for PDF, DOCX, images (OCR)
- Chunking strategies: fixed-size, semantic, sentence-based
- IBM watsonx.ai embedding generation for vectorised chunks
- IBM COS document source with `ibm-cos-sdk` IAM OAuth download
- Metadata extraction: title, source path, page number, chunk_seq
- Target support: OpenSearch (vectors)

### `udi-opensearch`

A skill specifically for the UDI + OpenSearch pipeline:

- Watson Data API connection registration (COS HMAC, OpenSearch)
- IBM UDI flow creation via the Watson Data API
- UDI job execution and status polling
- OpenSearch index configuration for UDI-ingested documents
- Troubleshooting UDI flow failures and WML instance status errors

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip data-ingestion-unstructured.zip
unzip udi-opensearch.zip
```

This will create:
```
.bob/skills/data-ingestion-unstructured/SKILL.md
.bob/skills/udi-opensearch/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What UDI skills do you have active?"*

---

## Usage Examples

### data-ingestion-unstructured
- *"Configure an IBM UDI flow to ingest PDFs from IBM COS into OpenSearch"*
- *"Generate a Docling document parsing script for scanned PDFs with OCR"*
- *"Write a chunking pipeline that splits DOCX files into 512-token chunks with 128-token overlap"*

### udi-opensearch
- *"Register my COS bucket and OpenSearch instance as connections in my watsonx.ai project"*
- *"Create and run a UDI flow that ingests documents from my COS folder into OpenSearch"*
- *"Troubleshoot a UDI flow that fails with invalid_instance_status_error"*

---

## What Bob Can Help You Build

1. **UDI Flow Configs**: Connection registration, flow creation, embedding and OpenSearch sink setup
2. **Document Parsers**: Docling and multi-format parsing pipelines
3. **Chunking Pipelines**: Adaptive text splitting with metadata extraction
4. **OpenSearch Ingestion**: UDI-to-OpenSearch index patterns with vector support

---

## Prerequisites

Before using these skills, ensure you have:

- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- IBM watsonx.ai project (houses UDI flows and connections)
- Watson Machine Learning instance (active, linked to your watsonx.ai project — required for OCR extraction)
- IBM Cloud Object Storage bucket with source documents
- OpenSearch instance (IBM watsonx.data managed, or self-managed)

## Skill Capabilities Summary

| Capability | data-ingestion-unstructured | udi-opensearch |
|---|---|---|
| IBM UDI Flow Configuration | ✅ | ✅ |
| Watson Data API (connection registration) | — | ✅ |
| IBM Docling OCR | ✅ | — |
| Chunking & Embedding | ✅ | ✅ |
| OpenSearch Target | ✅ | ✅ |
| Troubleshooting / Status Polling | — | ✅ |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/data-ingestion-unstructured/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

## Related

- [`../bob-modes/`](../bob-modes/) — Data Ingestion Builder Bob Mode
- [`../README.md`](../README.md) — UDI building block overview
- [`../assets/`](../assets/) — Deployable UDI OpenSearch ingestion assets
- [`../../etl/`](../../etl/README.md) — ETL / ELT building block (structured ingestion)
