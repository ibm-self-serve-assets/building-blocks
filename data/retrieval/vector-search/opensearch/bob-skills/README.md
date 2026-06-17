# OpenSearch Bob Skills

Bob skills for **IBM watsonx.data OpenSearch** hybrid search and vector search development using **IBM watsonx.ai** embeddings.

## Overview

The `opensearch-vector-search` skill empowers IBM Bob to design and build production-ready hybrid search applications on IBM watsonx.data OpenSearch — covering k-NN index design, IBM watsonx.ai embedding integration, document ingestion from IBM COS, and hybrid search query patterns.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `opensearch-vector-search` | [`opensearch-vector-search.zip`](opensearch-vector-search.zip) | Building hybrid search (vector + BM25) on IBM watsonx.data OpenSearch with IBM watsonx.ai embeddings |

---

### `opensearch-vector-search`

A comprehensive skill for building IBM watsonx.data OpenSearch hybrid search applications:

- k-NN index design with HNSW (nmslib engine) for IBM watsonx.data managed OpenSearch
- IBM watsonx.ai embedding model integration (`ibm/slate-125m-english-rtrvr`, dim=768)
- IBM COS document source with `ibm-cos-sdk` IAM OAuth download
- `unstructured` library document parsing (PDF, DOCX, HTML)
- `opensearch-py` bulk indexing with `opensearch-py.helpers.bulk`
- Hybrid search: k-NN vector + BM25 keyword query construction
- Score normalisation and result ranking
- SSL/TLS configuration for IBM watsonx.data managed OpenSearch
- `langchain_text_splitters.RecursiveCharacterTextSplitter` chunking

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip opensearch-vector-search.zip
```

This will create:
```
.bob/skills/opensearch-vector-search/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `opensearch-vector-search`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What OpenSearch skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Create a k-NN index mapping for IBM watsonx.data OpenSearch with HNSW and 768 dimensions"*
- *"Generate a hybrid search query combining k-NN vector search and BM25 keyword search"*
- *"Write a bulk indexing script that embeds documents from IBM COS using IBM watsonx.ai"*
- *"Show me SSL/TLS configuration for IBM watsonx.data managed OpenSearch"*
- *"Implement score normalisation for hybrid search results"*

---

## What Bob Can Help You Build

1. **k-NN Index Creation**: HNSW index mappings with correct IBM watsonx.data settings
2. **Hybrid Search Queries**: `bool.should` combining `knn` and `match` clauses
3. **Embedding Pipelines**: IBM watsonx.ai `ibm/slate-125m-english-rtrvr` integration
4. **Bulk Indexing Scripts**: Efficient `opensearch-py.helpers.bulk` insert patterns
5. **IBM COS Integration**: `ibm-cos-sdk` IAM OAuth document download
6. **FastAPI Search Services**: `/search` endpoints with hybrid results

---

## Prerequisites

Before using this skill, ensure you have:

- IBM watsonx.data instance with OpenSearch provisioned
- IBM watsonx.ai project with embedding model access (`ibm/slate-125m-english-rtrvr`)
- IBM Cloud Object Storage bucket with source documents
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **k-NN Index Design** | HNSW mapping with correct engine settings for watsonx.data |
| **IBM watsonx.ai Embeddings** | `Embeddings` API for dim=768 dense vectors |
| **Hybrid Search** | Vector + BM25 `bool.should` query patterns |
| **Bulk Indexing** | Efficient batch insert via `opensearch-py.helpers.bulk` |
| **IBM COS Source** | IAM OAuth document download with `ibm-cos-sdk` |
| **Score Normalisation** | Min-max and RRF score fusion patterns |
| **SSL/TLS Config** | Managed OpenSearch TLS connection setup |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/opensearch-vector-search/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates wrong OpenSearch query syntax:**
1. Mention "IBM watsonx.data OpenSearch" explicitly
2. Specify the index dimension: *"768-dimensional k-NN index"*

## Related

- [`../bob-modes/`](../bob-modes/) — OpenSearch Builder Bob Mode
- [`../README.md`](../README.md) — OpenSearch Vector Search building block overview
- [`../assets/`](../assets/) — Deployable OpenSearch ingestion and search assets
