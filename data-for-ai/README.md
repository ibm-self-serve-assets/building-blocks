# Data for AI - Building Blocks

## Overview

IBM's data-for-AI building blocks organized by Core Capabilities, providing comprehensive solutions for AI data management, enrichment, activation, and security.

## Building Blocks

```
├── enrichment/                      # Data Enrichment Capabilities
│   ├── ai-generated-data-pipeline/  # Automated Data Pipelines
│   ├── data-streaming/              # Real-time Data Streaming
│   └── data-enrichment-quality/     # Data Quality & Governance
│
└── activation/                      # Data Activation Capabilities
    ├── qna/                         # Q&A and Search
    ├── vector-search/               # Vector Search
    ├── nosql-database/              # NoSQL Database
    └── federated-search/            # Zero-Copy Lakehouse
```

## Capability Matrix

Based on IBM's Data for AI framework:

### Enrichment Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Enrichment** | AI-generated data pipeline | Bob + Docling + RAG accelerator + watsonx.data | DataStage; StreamSets; Data Replication; Unstructured Data Integration; Data Observability | Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support |
| **Enrichment** | Data Streaming | Confluent | IBM integration with Apache Kafka topics, connectors, and Apache Flink | Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases |
| **Enrichment** | Data enrichment & quality | watsonx.data Intelligence | Governance and Catalog; Data Quality; Data Lineage; Metadata enrichment; Intelligent search; Data product sharing | Text-to-SQL, NLQ-to-SQL, governed RAG/Q&A, Open RAG. Improves trust and usability of enterprise data through cataloging, governance, quality controls, lineage, metadata enrichment, and discovery |

### Activation Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Activation** | Q&A | watsonx.data | RAG accelerator | Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines |
| **Activation** | Vector Search | watsonx.data OpenSearch | Vector index via Milvus integration | Vector ingestion, embedding, retrieval; smaller scale, elastic search |
| **Activation** | NoSQL database | AstraDB | Apache Cassandra-based serverless database; vector collections; Data API / CQL | nosql - huge scale, Cassandra. Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads |
| **Activation** | Federated search | watsonx.data | Open lakehouse (Apache Iceberg + Presto) | Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository |

## Quick Start

1. Navigate to the capability folder that matches your use case:
   - For data preparation: [`enrichment/`](enrichment/)
   - For AI applications: [`activation/`](activation/)
2. Follow the README instructions in each folder
3. Check individual asset READMEs for detailed setup and configuration

## Architecture

This repository follows IBM's Data for AI framework:
- **Enrichment**: Prepare and enhance data for AI workloads
- **Activation**: Enable AI applications to access and utilize data effectively

## Migration Note

The repository has been reorganized to align with IBM's Data for AI capability framework. See [`MIGRATION_GUIDE.md`](MIGRATION_GUIDE.md) for details on the new structure and how to update your references.

---

**Last Updated**: April 2026