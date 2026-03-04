# Vector Search

Vector-based retrieval services for GenAI pipelines, enabling semantic similarity search for RAG applications.

## What's Included

### Milvus

High-performance vector database optimized for billion-scale vector search.

- **[Data Ingestion Asset](./milvus/assets/data-ingestion-asset/)**: FastAPI service for document ingestion
- **[Bob Mode](./milvus/bob-mode/)**: AI assistant configuration for Milvus development

### OpenSearch

Open-source search and analytics engine with vector search capabilities.

- **[Assets](./opensearch/assets/)**: Integration examples and configurations
- **[Bob Mode](./opensearch/bob-mode/)**: AI assistant for OpenSearch development

### Datastax Astra DB

Cloud-native serverless vector database built on Apache Cassandra.

- **[Assets](./datastax-astradb/assets/)**: Configuration and setup guides
- **[Bob Mode](./datastax-astradb/bob-mode/)**: AI assistant for Astra DB development

## Quick Start

1. **Choose your vector database**:
   - **Milvus**: For high-performance, large-scale deployments
   - **OpenSearch**: For hybrid search and analytics
   - **Datastax Astra DB**: For serverless, globally distributed applications

2. **Navigate to the specific directory**:
   ```bash
   # For Milvus
   cd milvus/assets/data-ingestion-asset/
   
   # For OpenSearch
   cd opensearch/
   
   # For Astra DB
   cd datastax-astradb/
   ```

3. **Follow the detailed README** in each directory for setup instructions
