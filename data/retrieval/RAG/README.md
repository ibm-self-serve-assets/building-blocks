# RAG (Retrieval-Augmented Generation)

Complete RAG pipeline with document ingestion, embedding generation, vector storage, and semantic search capabilities. Supports both Milvus and OpenSearch as vector databases with IBM Watsonx embeddings.

## What's Included

### Assets

- **[RAG Accelerator](./assets/rag-accelerator/)**: Complete RAG pipeline with document processing, embedding, and querying
  - Ingest documents from IBM Cloud Object Storage (COS)
  - Generate embeddings with IBM Watsonx.ai
  - Store vectors in **Milvus** or **OpenSearch**
  - Perform semantic search with vector similarity
  - Keyword search with BM25 algorithm
  - Hybrid search combining semantic and keyword approaches
  - FastAPI-based REST API
  - Docker deployment ready

- **[RAG Ingestion MCP Server](./assets/rag-ingestion-sse-mcp-server/)**: MCP server for document ingestion from IBM COS
  - Deploy as remote MCP server via SSE transport
  - Integrate with AI assistants (IBM Bob, Claude, etc.)
  - Automated document processing and chunking
  - Support for multiple document formats
  - Batch ingestion capabilities

- **[RAG Retrieval MCP Server](./assets/rag-retrieval-sse-mcp-server/)**: MCP server for semantic and keyword search
  - Semantic retrieval with Watsonx embeddings
  - Keyword search with BM25
  - Hybrid search combining both approaches
  - Works with both Milvus and OpenSearch backends
  - Configurable reranking options

### Bob Modes

- **[Base Modes](./bob-modes/base-modes/)**: AI assistant modes specialized for RAG development
  - **RAG Builder Mode**: Guidance for building RAG pipelines
  - **Data Generator Mode**: Help with test data generation
  - Vector database configuration (Milvus/OpenSearch)
  - Document processing and chunking strategies
  - MCP server development assistance
  - Embedding model selection and optimization

## Vector Database Support

This RAG implementation supports two enterprise-grade vector databases:

### Milvus
- High-performance vector similarity search
- Scalable distributed architecture
- Support for multiple index types (IVF_FLAT, HNSW, etc.)
- Rich filtering capabilities
- Ideal for large-scale deployments

### OpenSearch
- Combines vector search with full-text search
- Built-in BM25 keyword search
- Powerful aggregations and analytics
- Familiar Elasticsearch-compatible API
- Excellent for hybrid search scenarios

## Quick Start

1. **For complete RAG pipeline**: Navigate to [`assets/rag-accelerator`](./assets/rag-accelerator/) and follow the README
   - Configure your vector database (Milvus or OpenSearch)
   - Set up IBM Watsonx.ai credentials
   - Configure IBM COS for document storage
   - Deploy via Docker or run locally

2. **For MCP servers**: Choose from ingestion or retrieval MCP servers in the Assets directory
   - Deploy as remote SSE-based MCP servers
   - Integrate with AI coding assistants
   - Enable RAG capabilities in your AI workflows

3. **For AI assistance**: Use the Bob Mode configurations in [`bob-modes/base-modes`](./bob-modes/base-modes/) with IBM Bob
   - Import the RAG Builder or Data Generator modes
   - Get expert guidance on RAG implementation
   - Optimize your RAG pipeline design

## Use Cases

- **Question Answering**: Build intelligent Q&A systems over your documents
- **Semantic Search**: Find relevant information based on meaning, not just keywords
- **Document Analysis**: Extract insights from large document collections
- **Knowledge Management**: Create searchable knowledge bases from unstructured data
- **AI Assistant Integration**: Add RAG capabilities to AI coding assistants via MCP
- **Hybrid Search**: Combine semantic understanding with keyword precision
