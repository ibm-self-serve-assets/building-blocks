# Query Capabilities

This directory contains building blocks for data query - enabling efficient data access through various query patterns and search capabilities.

## Building Blocks

### 1. Natural Language to structured data query
**Location**: [`natural-language-to-structured-data-query/`](natural-language-to-structured-data-query/)  
**IBM Products**: watsonx.data Intelligence  
**Product Components**: Text to SQL

Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines. Convert natural language questions into SQL queries with metadata-enriched context.

**Key Features**:
- Natural language to SQL conversion
- Metadata-enriched query generation
- Enterprise Q&A capabilities
- Configurable retrieval pipelines
- Text-to-SQL query generation

[View Details →](natural-language-to-structured-data-query/)

---

### 2. Vector Search
**Location**: [`vector-search/`](vector-search/)  
**IBM Products**: watsonx.data (OpenSearch), Open RAG, RAG Accelerator (Asset)  
**Product Components**: Vector ingestion, embedding, retrieval; smaller scale, elastic search

Vector ingestion, embedding, retrieval; semantic search and similarity matching using vector embeddings.

**Key Features**:
- Vector similarity search
- Multiple vector database options (Milvus, OpenSearch, AstraDB)
- Semantic search capabilities
- Embedding generation and storage
- Scalable vector indexing

[View Details →](vector-search/)

---

### 3. No SQL database
**Location**: [`nosql-database/`](nosql-database/)  
**IBM Products**: AstraDB, HCD (Hyper-converged DB)  
**Product Components**: Apache Cassandra-based serverless database; vector collections; Data API / CQL

Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads.

**Key Features**:
- Massive scale NoSQL storage
- Apache Cassandra compatibility
- Serverless architecture
- Vector collections support
- Global distribution
- Data API and CQL access

[View Details →](nosql-database/)

---

### 4. Federated search
**Location**: [`federated-search/`](federated-search/)  
**IBM Products**: watsonx.data  
**Product Components**: Zero-Copy Lakehouse

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

1. Choose the query capability that matches your AI application needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **Natural Language Queries**: Convert questions to SQL queries
- **Semantic Search**: Find similar documents based on meaning
- **Scalable Storage**: Store and retrieve massive amounts of data with NoSQL
- **Data Federation**: Query data across multiple sources without copying
- **AI Applications**: Power AI applications with efficient data access patterns