# Data for AI - Building Blocks

## Overview

IBM's data-for-AI building blocks organized by Core Capabilities, providing comprehensive solutions for AI data management, integration, intelligence, and retrieval capabilities.

## Building Blocks

```
├── integration/                                          # Data Integration Capabilities
│   ├── data-pipeline-ai-generated/                       # Data pipeline (AI Generated)
│   ├── data-streaming/                                   # Data streaming
│   └── data-observability/                               # Data Observability
│
├── intelligence/                                         # Data Intelligence Capabilities
│   ├── data-quality/                                     # Data Quality
│   ├── data-lineage/                                     # Data Lineage
│   └── text2sql/                                         # Text2SQL
│
└── retrieval/                                            # Data Retrieval Capabilities
    ├── vector-search/                                    # Vector Search
    ├── no-sql-database/                                  # No SQL database
    └── zero-copy/                                        # Zero Copy
```

## Capability Matrix

Based on IBM's Data for AI framework:

### Integration Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Integration** | Data pipeline (AI Generated) | Bob + Docling + RAG accelerator + watsonx.data | DataStage; StreamSets; Data Replication; Unstructured Data Integration(UDI) | Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support |
| **Integration** | Data streaming | Confluent | Kafka topics; Connectors; Apache Flink; Stream Governance; Confluent Hub | Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases |
| **Integration** | Data Observability | Databand | Databand | Monitor and ensure data pipeline quality and reliability |

### Intelligence Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Intelligence** | Data Quality | watsonx.data Intelligence | Data quality rules | Ensure data quality through validation rules and quality checks |
| **Intelligence** | Data Lineage | watsonx.data Intelligence | Manta data lineage | Track data transformations using OpenLineage spec |
| **Intelligence** | Text2SQL | watsonx.data Intelligence | Text2SQL | Convert natural language questions to SQL |

### Retrieval Capabilities

| Core Capability | Building Block | IBM Product(s) | Product Components | Description |
|----------------|----------------|----------------|-------------------|-------------|
| **Retrieval** | Vector Search | watsonx.data (OpenSearch), Open RAG, RAG Accelerator (Asset) | Opensearch; Milvus; ElasticSearch | Build RAG solutions using - vector ingestion, embedding, reranking and generative models, retrieval |
| **Retrieval** | No SQL database | AstraDB, HCD (Hyper-converged DB) | AstraDB(Cassandra) | Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads |
| **Retrieval** | Zero Copy | watsonx.data | Iceberg; Presto; Spark; Data connectors | Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository |

## Quick Start

1. Navigate to the capability folder that matches your use case:
   - For data pipelines and integration: [`integration/`](integration/)
   - For data quality, lineage, and intelligence: [`intelligence/`](intelligence/)
   - For data retrieval and search: [`retrieval/`](retrieval/)
2. Follow the README instructions in each folder
3. Check individual asset READMEs for detailed setup and configuration

## Architecture

This repository follows IBM's Data for AI framework:
- **Integration**: Build and manage data pipelines for structured and unstructured data
- **Intelligence**: Enhance data quality, governance, and enable intelligent data operations
- **Retrieval**: Enable efficient data access through various retrieval patterns and search capabilities

## Use Cases

### Integration
- Automated data ingestion from multiple sources
- Real-time event streaming and processing
- Batch and real-time data pipelines
- Data pipeline observability and monitoring

### Intelligence
- Data quality assessment and validation
- Metadata enrichment and cataloging
- Data governance and lineage tracking
- Natural language to SQL conversion
- RAG-based Q&A systems with quality controls

### Retrieval
- Vector-based semantic search
- Large-scale NoSQL data storage
- Federated analytics without data copying
- Multi-modal data retrieval