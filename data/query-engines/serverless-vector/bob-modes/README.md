# Bob Mode for DataStax Astra DB Vector Search

Custom IBM Bob mode configuration for **DataStax Astra DB** vector search development — part of the IBM Cloud HCD portfolio.

---

## Overview

This Bob mode provides specialized assistance for:

- **Astra DB Data API**: Creating collections, inserting vectors, ANN search using `astrapy`
- **IBM watsonx.ai Embeddings**: Generating dense vectors with `ibm/slate-125m-english-rtrvr`
- **IBM COS Document Source**: Downloading and chunking documents with `ibm-cos-sdk`
- **Collection Schema Design**: Choosing dimensions, metric, and indexing options
- **ANN Search Queries**: Building `find()` queries with `$vector` sort

---

## What's Included

- **[`base-modes/astradb-vector-builder.zip`](base-modes/astradb-vector-builder.zip)**: Bob mode for Astra DB vector development

---

## Mode Capabilities

- DataStax Astra DB Data API collection creation and management
- IBM watsonx.ai embedding generation integration
- IBM COS document ingestion with `ibm-cos-sdk`
- `astrapy` SDK CRUD operations and ANN vector search
- `$vector` field conventions and document ID strategies
- Batch insert optimisation (≤20 documents per request)
- Cosine, dot-product, and Euclidean distance metric selection
- IBM HCD token management and endpoint configuration

---

## When to Use This Mode

- Building vector search applications on IBM HCD (Astra DB)
- Designing vector collection schemas with cosine or dot-product similarity
- Ingesting documents from IBM COS into Astra DB vector collections
- Implementing ANN search queries with `astrapy` `find()` patterns
- Troubleshooting Astra DB token or API endpoint configuration
- Integrating IBM watsonx.ai embeddings with Astra DB serverless storage
- Building serverless, globally distributed RAG systems

---

## Installing Bob Modes

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/astradb-vector-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/astradb-vector-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
