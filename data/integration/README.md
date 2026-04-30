# Integration Capabilities

This directory contains building blocks for data integration - enabling data pipelines, streaming, and observability for AI applications.

## Building Blocks

### 1. Data pipeline (AI Generated)
**Location**: [`data-pipeline-ai-generated/`](data-pipeline-ai-generated/)
**IBM Products**: Bob + Docling + RAG accelerator + watsonx.data integration
**Product Components**: DataStage; StreamSets; Data Replication; Unstructured Data Integration(UDI)

Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support.

**Key Features**:
- Batch processing for large-scale data ingestion
- Real-time pipelines for immediate data availability
- Data replication across systems
- Unstructured data processing with Docling
- Pipeline observability and monitoring

[View Details →](data-pipeline-ai-generated/)

---

### 2. Data streaming
**Location**: [`data-streaming/`](data-streaming/)  
**IBM Products**: Confluent  
**Product Components**: Kafka topics; Connectors; Apache Flink; Stream Governance; Confluent Hub

Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases.

**Key Features**:
- Real-time event ingestion
- Apache Kafka integration
- Apache Flink stream processing
- Stream governance
- Operational and analytical use cases
- Continuous data flow

**Status**: Coming Soon

[View Details →](data-streaming/)

---

### 3. Data Observability
**Location**: [`data-observability/`](data-observability/)  
**IBM Products**: Databand  
**Product Components**: Databand

Monitor and ensure data pipeline quality and reliability.

**Key Features**:
- Pipeline monitoring
- Data quality tracking
- Anomaly detection
- Performance metrics
- Alert management

**Status**: Coming Soon

[View Details →](data-observability/)

---

## Quick Start

1. Choose the integration capability that matches your needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **Data Pipeline Automation**: Automate data ingestion and transformation
- **Real-time Processing**: Process streaming data for immediate insights
- **Batch Processing**: Handle large-scale data ingestion
- **Pipeline Monitoring**: Track pipeline health and performance
- **Hybrid Integration**: Connect on-premises and cloud data sources