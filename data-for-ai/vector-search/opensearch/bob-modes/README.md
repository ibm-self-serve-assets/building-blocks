# Bob Mode for OpenSearch Vector Search

Custom IBM Bob mode configuration for OpenSearch vector database development.

---

## Overview

This Bob mode provides specialized assistance for:

- **OpenSearch Integration**: Working with OpenSearch vector capabilities
- **Vector Embeddings**: Generating embeddings with watsonx.ai
- **Hybrid Search**: Combining vector and keyword search
- **Data Ingestion**: Loading documents into OpenSearch indexes
- **Index Management**: Creating and configuring OpenSearch indexes
- **Performance Optimization**: Tuning OpenSearch for production

---

## What's Included

- **[`base-modes/opensearch.yaml`](base-modes/opensearch.yaml)**: Bob mode configuration for OpenSearch development

---

## Mode Capabilities

- OpenSearch index design and mapping configuration
- Vector embedding generation with watsonx.ai
- Document chunking and preprocessing strategies
- Batch ingestion from IBM Cloud Object Storage
- k-NN vector search implementation
- Keyword search with BM25 scoring
- Hybrid search combining vector and keyword
- Index settings and shard configuration
- Connection management and authentication
- Performance tuning and optimization
- Error handling and retry logic
- Integration with FastAPI applications

---

## When to Use This Mode

- Setting up OpenSearch vector search
- Implementing hybrid search (vector + keyword)
- Designing index mappings and settings
- Optimizing ingestion pipelines
- Troubleshooting OpenSearch connectivity
- Configuring k-NN algorithms
- Building RAG applications with OpenSearch
- Migrating to OpenSearch from Elasticsearch

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/opensearch.yaml`](base-modes/opensearch.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with OpenSearch vector database tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/opensearch.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/opensearch.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.