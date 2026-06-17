# Bob Mode for OpenSearch Vector Search

Custom IBM Bob mode configuration for **IBM watsonx.data OpenSearch** vector search development.

---

## Overview

This Bob mode provides specialized assistance for:

- **IBM watsonx.data OpenSearch Setup**: Provisioning k-NN indexes on watsonx.data managed OpenSearch
- **IBM watsonx.ai Embedding Integration**: Using `ibm/slate-125m-english-rtrvr` for semantic embeddings
- **Document Ingestion from IBM COS**: Downloading, chunking, embedding, and indexing with `unstructured`
- **Hybrid Search**: Combining k-NN vector search with BM25 keyword search
- **Index Optimisation**: HNSW parameter tuning, shard configuration, score normalisation

---

## What's Included

- **[`base-modes/opensearch-builder.zip`](base-modes/opensearch-builder.zip)**: Bob mode for OpenSearch vector search development

---

## Mode Capabilities

- IBM Cloud IAM authentication (API key → Bearer token)
- IBM watsonx.data OpenSearch k-NN index design and management
- IBM watsonx.ai embedding generation (ibm/slate-125m-english-rtrvr)
- Document ingestion pipeline from IBM COS
- k-NN vector search query construction
- BM25 full-text search queries
- Hybrid search with score normalisation
- HNSW index parameter tuning
- Bulk indexing with opensearch-py `bulk` helper
- FastAPI service development for OpenSearch operations

---

## When to Use This Mode

- Building semantic search over IBM COS documents with watsonx.data OpenSearch
- Designing k-NN indexes for RAG applications
- Implementing hybrid search combining semantic and keyword matching
- Optimising OpenSearch index performance (ef_construction, m parameters)
- Troubleshooting watsonx.data OpenSearch connectivity
- Integrating IBM watsonx.ai embeddings with OpenSearch

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/opensearch-builder.zip`](base-modes/opensearch-builder.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with IBM watsonx.data OpenSearch.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/opensearch-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/opensearch-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
