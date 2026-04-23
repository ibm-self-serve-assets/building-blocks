# Activation Capabilities

This directory contains building blocks for data activation - enabling AI applications to access and utilize data effectively.

## Building Blocks

### 1. Q&A (Question & Answer)
**Location**: [`qna/`](qna/)  
**IBM Products**: watsonx.data  
**Product Components**: RAG accelerator

Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines.

**Key Features**:
- Retrieval-augmented generation (RAG)
- Question answering over documents
- Text-to-SQL query generation
- Configurable retrieval pipelines
- Enterprise-grade Q&A systems

[View Details →](qna/)

---

### 2. Vector Search
**Location**: [`vector-search/`](vector-search/)  
**IBM Products**: watsonx.data OpenSearch  
**Product Components**: Vector index via Milvus integration

Vector ingestion, embedding, retrieval; smaller scale, elastic search. Enables semantic search and similarity matching using vector embeddings.

**Key Features**:
- Vector similarity search
- Multiple vector database options (Milvus, OpenSearch, AstraDB)
- Semantic search capabilities
- Embedding generation and storage
- Scalable vector indexing

[View Details →](vector-search/)

---

### 3. NoSQL Database
**Location**: [`nosql-database/`](nosql-database/)  
**IBM Products**: AstraDB  
**Product Components**: Apache Cassandra-based serverless database; vector collections; Data API / CQL

nosql - huge scale, Cassandra. Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads.

**Key Features**:
- Massive scale NoSQL storage
- Apache Cassandra compatibility
- Serverless architecture
- Vector collections support
- Global distribution
- Data API and CQL access

[View Details →](nosql-database/)

---

### 4. Federated Search
**Location**: [`federated-search/`](federated-search/)  
**IBM Products**: watsonx.data  
**Product Components**: Open lakehouse (Apache Iceberg + Presto)

Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository.

**Key Features**:
- Zero-copy data access
- Apache Iceberg lakehouse format
- Presto query engine
- Federated analytics
- Query across distributed sources
- No data duplication required

[View Details →](federated-search/)

---

## Quick Start

1. Choose the activation capability that matches your AI application needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **Enterprise Q&A**: Build intelligent question-answering systems over your data
- **Semantic Search**: Enable meaning-based search across documents and data
- **Scalable Storage**: Store and retrieve massive amounts of data with NoSQL
- **Data Federation**: Query data across multiple sources without copying
- **AI Applications**: Power AI applications with efficient data access patterns