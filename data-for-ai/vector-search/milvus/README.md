# Milvus Vector Search

High-performance vector database optimized for billion-scale vector search with IBM watsonx integration.

## What's Included

### Assets

- **[Data Ingestion Asset](./assets/data-ingestion-asset/)**: FastAPI service for document ingestion into Milvus
  - Ingest documents from IBM COS
  - Process with Docling-based parsing
  - Generate embeddings using IBM Watsonx
  - Store and index vectors in Milvus
  - Swagger UI for API testing

### Bob Mode

- **[Base Mode](./bob-mode/base-mode/)**: AI assistant configuration for Milvus development
  - Milvus setup and configuration
  - Collection schema design
  - Index optimization
  - Query performance tuning

## Quick Start

1. **For document ingestion**: Navigate to [`assets/data-ingestion-asset`](./assets/data-ingestion-asset/) and follow the README

2. **For AI assistance**: Use the Bob Mode configuration in [`bob-mode/base-mode`](./bob-mode/base-mode/) with IBM Bob
