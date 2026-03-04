# Bob Mode for DataStax Astra DB Vector Search

Custom IBM Bob mode configuration for DataStax Astra DB vector database development.

---

## Overview

This Bob mode provides specialized assistance for:

- **Astra DB Integration**: Working with DataStax Astra DB vector capabilities
- **Vector Embeddings**: Generating embeddings with watsonx.ai
- **Serverless Vector Search**: Leveraging Astra DB's managed infrastructure
- **Data Ingestion**: Loading documents into Astra DB collections
- **Collection Management**: Creating and configuring Astra DB collections
- **Performance Optimization**: Tuning queries for production workloads

---

## What's Included

- **[`base-mode/astradb.yaml`](base-mode/astradb.yaml)**: Bob mode configuration for Astra DB development

---

## Mode Capabilities

- Astra DB collection design and schema definition
- Vector embedding generation with watsonx.ai
- Document chunking and preprocessing strategies
- Batch ingestion from IBM Cloud Object Storage
- Vector similarity search implementation
- CQL query optimization
- Connection management with application tokens
- Performance tuning and optimization
- Error handling and retry logic
- Integration with FastAPI applications
- Serverless scaling configuration

---

## When to Use This Mode

- Setting up DataStax Astra DB vector search
- Implementing serverless vector databases
- Designing collection schemas
- Optimizing ingestion pipelines
- Troubleshooting Astra DB connectivity
- Configuring vector search indexes
- Building RAG applications with Astra DB
- Migrating to Astra DB from other vector databases

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-mode/astradb.yaml`](base-mode/astradb.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with DataStax Astra DB vector database tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-mode/astradb.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-mode/astradb.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.