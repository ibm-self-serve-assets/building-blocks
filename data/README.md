# Data for AI - Building Blocks

## Overview

IBM's data-for-AI building blocks organized by Core Capabilities, providing comprehensive solutions for AI data management, integration, intelligence, and query capabilities.

## Building Blocks

```
├── integration/                                          # Data Integration Capabilities
│   ├── ai-generated-data-pipeline/                       # AI-generated data pipeline
│   └── data-streaming/                                   # Data streaming
│
├── intelligence/                                         # Data Intelligence Capabilities
│   ├── data-enrichment/                                  # Data Enrichment
│   └── quality-and-lineage/                              # Quality & Lineage
│
└── query/                                                # Data Query Capabilities
    ├── natural-language-to-structured-data-query/        # Natural Language to structured data query
    ├── vector-search/                                    # Vector Search
    ├── nosql-database/                                   # No SQL database
    └── federated-search/                                 # Federated search
```

## Capability Matrix

Based on IBM's Data for AI framework:

### Integration Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Integration** | AI-generated data pipeline | Bob + Docling + RAG accelerator + watsonx.data | DataStage; StreamSets; Data Replication; Unstructured Data Integration; Data Observability | Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support |
| **Integration** | Data streaming | Confluent | IBM integration with Apache Kafka topics, connectors, and Apache Flink | Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases |

### Intelligence Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Intelligence** | Data Enrichment | watsonx.data Intelligence | Governance and Catalog; Data Quality; Data Lineage; Metadata enrichment; Intelligent search; Data product sharing | Improves trust and usability of enterprise data through cataloging, governance, quality controls, lineage, metadata enrichment, and discovery |
| **Intelligence** | Quality & Lineage | watsonx.data Intelligence | Text to SQL; Data Quality; Data Lineage | Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines |

### Query Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Query** | Natural Language to structured data query | watsonx.data Intelligence | Text to SQL | Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines |
| **Query** | Vector Search | watsonx.data (OpenSearch), Open RAG, RAG Accelerator (Asset) | Vector ingestion, embedding, retrieval; smaller scale, elastic search | Vector ingestion, embedding, retrieval; semantic search and similarity matching |
| **Query** | No SQL database | AstraDB, HCD (Hyper-converged DB) | Apache Cassandra-based serverless database; vector collections; Data API / CQL | Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads |
| **Query** | Federated search | watsonx.data | Zero-Copy Lakehouse | Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository |

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
- Real-time event streaming and processing
- Batch and real-time data pipelines
- Hybrid integration support

### Intelligence
- Data quality assessment and validation
- Metadata enrichment and cataloging
- Data governance and lineage tracking
- RAG-based Q&A systems with quality controls

### Query
- Natural language database queries
- Semantic search across documents
- Large-scale NoSQL data storage
- Federated analytics without data copying