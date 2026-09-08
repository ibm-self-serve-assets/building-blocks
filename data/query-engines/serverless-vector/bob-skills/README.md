# DataStax Astra DB Vector Search Bob Skills

Bob skills for **DataStax Astra DB** (IBM Cloud HCD portfolio) vector search development using **IBM watsonx.ai** embeddings.

## Overview

The `astradb-vector-setup` skill empowers IBM Bob to design and build vector search applications on **DataStax Astra DB** — covering collection creation with cosine metric, IBM watsonx.ai embedding integration, document ingestion from IBM COS, and ANN search queries using the `astrapy` Data API.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `astradb-vector-setup` | [`astradb-vector-setup.zip`](astradb-vector-setup.zip) | Building vector search collections on DataStax Astra DB (IBM HCD) with IBM watsonx.ai embeddings |

---

### `astradb-vector-setup`

A comprehensive skill for building DataStax Astra DB vector search applications using IBM Cloud services:

- `astrapy>=1.5.2` Data API client for vector collection creation and ANN search
- IBM watsonx.ai embedding generation (`ibm/slate-125m-english-rtrvr`, dim=768)
- IBM COS document source with `ibm-cos-sdk` IAM OAuth download
- Vector collection creation with cosine metric and configurable dimension
- Bulk insert with `$vector` field convention and SHA-256 `_id` hashing
- ANN search using `collection.find(sort={"$vector": query_vector})`
- `unstructured` library document parsing with `RecursiveCharacterTextSplitter`
- Astra DB token format: `AstraCS:...` and API endpoint configuration

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip astradb-vector-setup.zip
```

This will create:
```
.bob/skills/astradb-vector-setup/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `astradb-vector-setup`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What Astra DB vector skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Create an Astra DB vector collection with 768 dimensions and cosine metric"*
- *"Generate a bulk insert script that embeds PDF documents from IBM COS into Astra DB"*
- *"Write an ANN search function using collection.find() with a watsonx.ai query vector"*
- *"Show me the astrapy Data API setup for IBM HCD Astra DB"*
- *"What's the correct $vector field format for Astra DB document insertion?"*

---

## What Bob Can Help You Build

1. **Vector Collections**: `db.create_collection()` with dimension, cosine metric
2. **IBM watsonx.ai Embeddings**: `ibm_watsonx_ai.foundation_models.Embeddings` API
3. **Document Insert**: `$vector` field convention, `insert_many()` batch patterns
4. **ANN Search**: `collection.find(sort={"$vector": query_vec}, limit=N)` patterns
5. **IBM COS Integration**: `ibm-cos-sdk` IAM OAuth document download
6. **FastAPI Search Services**: `/search` and `/ingest` endpoints

---

## Prerequisites

Before using this skill, ensure you have:

- DataStax Astra DB instance (IBM Cloud HCD portfolio)
- Astra DB Application Token (`AstraCS:...`)
- Astra DB API endpoint URL (`https://<DB_ID>-<REGION>.apps.astra.datastax.com`)
- IBM watsonx.ai project with embedding model access
- IBM Cloud Object Storage bucket with source documents

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **Collection Creation** | `create_collection()` with dimension, VectorMetric.COSINE |
| **IBM watsonx.ai Embeddings** | `Embeddings` API (dim=768) for insert and query |
| **Document Insert** | `$vector` field, SHA-256 `_id`, `insert_many()` batching |
| **ANN Search** | `collection.find(sort={"$vector": ...})` with $similarity |
| **IBM COS Source** | IAM OAuth document download with `ibm-cos-sdk` |
| **Embedding Model Reference** | 768 (slate-125m), 384 (slate-30m), 1024 (multilingual-e5-large) |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/astradb-vector-setup/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates wrong astrapy syntax:**
1. Specify `astrapy>=1.5.2` in your request
2. Mention "Data API" explicitly — not the deprecated AstraDB client

## Related

- [`../bob-modes/`](../bob-modes/) — Astra DB Vector Builder Bob Mode
- [`../README.md`](../README.md) — DataStax Astra DB Vector Search building block overview
- [`../../no-sql-database/astradb/bob-skills/`](../../no-sql-database/astradb/bob-skills/) — NoSQL Astra DB skills (non-vector)
