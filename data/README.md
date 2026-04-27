# Data for AI - Building Blocks

## Overview

IBM's data-for-AI building blocks organized by Core Capabilities, providing comprehensive solutions for AI data management, integration, intelligence, and query capabilities.

## Building Blocks

```
├── integration/                           # Data Integration Capabilities
│   ├── ai-generated-data-pipeline/        # Automated Data Pipelines
│   └── unstructured-data-pipelines/       # Unstructured Data Processing
│       └── qna/                           # Q&A Systems (RAG, Text-to-SQL)
│
├── intelligence/                          # Data Intelligence Capabilities
│   ├── data-enrichment-quality/           # Data Quality & Governance
│   └── data-streaming/                    # Real-time Data Streaming
│
└── query/                                 # Data Query Capabilities
    ├── text-to-sql/                       # Natural Language to SQL
    ├── vector-search/                     # Vector Search & Similarity
    ├── nosql-database/                    # NoSQL Database Solutions
    └── federated-search/                  # Zero-Copy Lakehouse
```

## Capability Matrix

Based on IBM's Data for AI framework:

### Integration Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Integration** | AI-generated data pipeline | Bob + Docling + RAG accelerator + watsonx.data | DataStage; StreamSets; Data Replication; Unstructured Data Integration; Data Observability | Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support |
| **Integration** | Unstructured data pipelines | Bob + Docling + watsonx.data | RAG accelerator; Text-to-SQL; Document processing | Process unstructured data for Q&A systems, RAG applications, and text-to-SQL query generation |

### Intelligence Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Intelligence** | Data enrichment & quality | watsonx.data Intelligence | Governance and Catalog; Data Quality; Data Lineage; Metadata enrichment; Intelligent search; Data product sharing | Improves trust and usability of enterprise data through cataloging, governance, quality controls, lineage, metadata enrichment, and discovery |
| **Intelligence** | Data Streaming | Confluent | IBM integration with Apache Kafka topics, connectors, and Apache Flink | Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases |

### Query Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Query** | Text-to-SQL | watsonx.data Intelligence | Metadata enrichment; Natural language processing | Convert natural language questions into SQL queries with metadata-enriched context |
| **Query** | Vector Search | watsonx.data OpenSearch | Vector index via Milvus integration | Vector ingestion, embedding, retrieval; semantic search and similarity matching |
| **Query** | NoSQL database | AstraDB | Apache Cassandra-based serverless database; vector collections; Data API / CQL | Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads |
| **Query** | Federated search | watsonx.data | Open lakehouse (Apache Iceberg + Presto) | Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture |

## Quick Start

1. Navigate to the capability folder that matches your use case:
   - For data pipelines and integration: [`integration/`](integration/)
   - For data quality and streaming: [`intelligence/`](intelligence/)
   - For querying and search: [`query/`](query/)
2. Follow the README instructions in each folder
3. Check individual asset READMEs for detailed setup and configuration

## Architecture

This repository follows IBM's Data for AI framework:
- **Integration**: Build and manage data pipelines for structured and unstructured data
- **Intelligence**: Enhance data quality, governance, and enable real-time streaming
- **Query**: Enable efficient data access through various query patterns and search capabilities

## Use Cases

### Integration
- Automated data ingestion from multiple sources
- Unstructured document processing with Docling
- RAG-based Q&A systems
- Text-to-SQL query generation

### Intelligence
- Data quality assessment and validation
- Real-time event streaming and processing
- Metadata enrichment and cataloging
- Data governance and lineage tracking

### Query
- Natural language database queries
- Semantic search across documents
- Large-scale NoSQL data storage
- Federated analytics without data copying