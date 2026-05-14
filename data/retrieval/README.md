# Retrieval Capabilities

This directory contains building blocks for data retrieval - enabling efficient data access through various retrieval patterns and search capabilities.

## Building Blocks

### 1. RAG (Retrieval-Augmented Generation)
**Location**: [`RAG/`](RAG/)
**IBM Products**: watsonx.ai, watsonx.data, IBM COS
**Product Components**: RAG Accelerator; Milvus; OpenSearch; Watsonx Embeddings; MCP Servers

Complete RAG pipeline with document ingestion, embedding generation, vector storage, and semantic search. Includes MCP servers for AI assistant integration.

**Key Features**:
- Complete RAG pipeline implementation
- Document ingestion from IBM COS
- Embedding generation with IBM Watsonx
- Vector storage in Milvus or OpenSearch
- Semantic and keyword search
- Hybrid search capabilities
- MCP server integration for AI assistants
- Docker deployment ready
- FastAPI-based architecture

[View Details →](RAG/)

---

### 2. Vector Search
**Location**: [`vector-search/`](vector-search/)  
**IBM Products**: watsonx.data (OpenSearch), Open RAG, RAG Accelerator (Asset)  
**Product Components**: Opensearch; Milvus; ElasticSearch

Build RAG solutions using - vector ingestion, embedding, reranking and generative models, retrieval.

**Key Features**:
- Vector similarity search
- Multiple vector database options (Milvus, OpenSearch, ElasticSearch)
- Semantic search capabilities
- Embedding generation and storage
- Scalable vector indexing
- Reranking capabilities

[View Details →](vector-search/)

---

### 3. No SQL database
**Location**: [`no-sql-database/`](no-sql-database/)  
**IBM Products**: AstraDB, HCD (Hyper-converged DB)  
**Product Components**: AstraDB(Cassandra)

Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads.

**Key Features**:
- Massive scale NoSQL storage
- Apache Cassandra compatibility
- Serverless architecture
- Vector collections support
- Global distribution
- Data API and CQL access

[View Details →](no-sql-database/)

---

### 4. Zero Copy
**Location**: [`zero-copy/`](zero-copy/)  
**IBM Products**: watsonx.data  
**Product Components**: Iceberg; Presto; Spark; Data connectors

Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository.

**Key Features**:
- Zero-copy data access
- Apache Iceberg lakehouse format
- Presto query engine
- Spark integration
- Federated analytics
- Query across distributed sources
- No data duplication required

[View Details →](zero-copy/)

---

## Quick Start

1. Choose the retrieval capability that matches your AI application needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **RAG Question Answering**: Build complete RAG systems with document processing and semantic search
- **AI Assistant Integration**: Connect RAG capabilities to AI assistants via MCP servers
- **Semantic Search**: Find similar documents based on meaning
- **RAG Applications**: Build retrieval-augmented generation systems
- **Scalable Storage**: Store and retrieve massive amounts of data with NoSQL
- **Data Federation**: Query data across multiple sources without copying
- **Multi-modal Retrieval**: Retrieve data across different modalities
- **Vector-based Search**: Enable meaning-based search across documents and data