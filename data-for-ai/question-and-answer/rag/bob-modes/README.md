# Bob Mode for RAG (Retrieval-Augmented Generation)

Custom IBM Bob mode configuration for RAG pipeline development and optimization.

---

## Overview

This Bob mode provides specialized assistance for:

- **RAG Pipeline Development**: Building end-to-end RAG systems
- **Vector Database Integration**: Working with Milvus, OpenSearch, and other vector stores
- **Embedding Strategies**: Implementing and optimizing embedding models
- **Retrieval Optimization**: Tuning semantic search and retrieval quality
- **Document Processing**: Chunking strategies and document ingestion
- **LLM Integration**: Connecting RAG pipelines with watsonx.ai and other LLMs

---

## What's Included

- **[`base-modes/rag-builder.yaml`](base-modes/rag-builder.yaml)**: Bob mode configuration for RAG development

---

## Mode Capabilities

- RAG architecture design and implementation
- Vector database configuration (Milvus, OpenSearch)
- Embedding model selection and optimization
- Document chunking and preprocessing strategies
- Semantic search implementation
- Retrieval quality evaluation and tuning
- LLM prompt engineering for RAG
- Hybrid search (dense + sparse vectors)
- MCP server development for RAG tools
- Performance optimization and scaling

---

## When to Use This Mode

- Building new RAG systems from scratch
- Optimizing existing RAG pipelines
- Implementing vector search capabilities
- Troubleshooting retrieval quality issues
- Designing document ingestion workflows
- Integrating RAG with watsonx.ai
- Developing RAG MCP servers
- Evaluating and improving RAG accuracy

---

## Installing Bob Modes

This section provides step-by-step instructions for installing the custom Bob mode.

---

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/rag-builder.yaml`](base-modes/rag-builder.yaml)) defines the behavior, expertise, and capabilities of IBM Bob when working with RAG pipeline tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/rag-builder.yaml "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/rag-builder.yaml ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.