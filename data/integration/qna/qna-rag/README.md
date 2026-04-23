# RAG (Retrieval-Augmented Generation)

Semantic search and question answering over documents using vector embeddings and LLMs.

## What's Included

### Assets

- **[RAG Accelerator](./assets/rag-accelerator/)**: Complete RAG pipeline with document processing, embedding, and querying
  - Ingest documents from IBM COS
  - Generate embeddings with IBM Watsonx
  - Store vectors in Milvus or OpenSearch
  - Perform semantic and keyword search

- **[RAG Ingestion MCP Server](./assets/rag-ingestion-sse-mcp-server/)**: MCP server for document ingestion from IBM COS
  - Deploy as remote MCP server
  - Integrate with AI assistants
  - Automated document processing

- **[RAG Retrieval MCP Server](./assets/rag-retrieval-sse-mcp-server/)**: MCP server for semantic and keyword search
  - Semantic retrieval with embeddings
  - Keyword search capabilities
  - Hybrid search support

- **[Base SSE MCP Server](./assets/base-sse-mcp-server/)**: Template for building custom MCP servers
  - Streamable HTTP transport
  - FastAPI-based architecture
  - Docker deployment ready

### Bob Modes

- **[Base Modes](./bob-modes/base-modes/)**: AI assistant mode specialized for RAG development
  - RAG pipeline design guidance
  - Vector database configuration
  - Document processing strategies
  - MCP server development

## Quick Start

1. **For complete RAG pipeline**: Navigate to [`assets/rag-accelerator`](./assets/rag-accelerator/) and follow the README

2. **For MCP servers**: Choose from ingestion, retrieval, or base server templates in the Assets directory

3. **For AI assistance**: Use the Bob Mode configuration in [`bob-modes/base-modes`](./bob-modes/base-modes/) with IBM Bob
