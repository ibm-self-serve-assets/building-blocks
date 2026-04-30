# Data pipeline (AI Generated)

**Core Capability**: Integration
**IBM Products**: Bob + Docling + RAG accelerator + watsonx.data integration
**Product Components**: DataStage; StreamSets; Data Replication; Unstructured Data Integration; Data Observability

## Overview

Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support. This capability enables automated data pipeline generation using AI-powered tools.

## Building Blocks

### Data Ingestion
**Location**: `data-ingestion/`
**Description**: Automated data ingestion for structured and unstructured data

**Components**:
- `assets/structured-data/` - Structured data ingestion pipelines
- `assets/unstructured-data/` - Document processing with Docling
- `bob-modes/` - Bob AI assistant modes for automation

**Quick Start with Bob**:
1. Import `bob-modes/data-ingestion.zip` into Bob
2. Describe your data source and target
3. Bob generates the ingestion pipeline automatically

**Manual Setup**:
```bash
cd data-ingestion/assets/structured-data
# Follow individual asset README
```

## Key Features

- **Batch Processing**: Large-scale data ingestion and transformation
- **Real-time Pipelines**: Stream processing for immediate data availability
- **Replication**: Data synchronization across systems
- **Unstructured Data**: Document parsing and processing with Docling
- **Observability**: Pipeline monitoring and data quality tracking
- **Hybrid Integration**: Support for cloud and on-premises data sources

---

For detailed setup, see individual component READMEs.