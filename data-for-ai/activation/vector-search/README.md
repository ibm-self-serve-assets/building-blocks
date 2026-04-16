# Vector Search Capability

**Core Capability**: Activation  
**IBM Products**: watsonx.data OpenSearch  
**Product Components**: Vector index via Milvus integration

## Overview

Vector ingestion, embedding, retrieval; smaller scale, elastic search. This capability enables semantic search and similarity matching using vector embeddings for AI-powered applications.

## Building Blocks

### 1. Milvus Vector Database
**Location**: `milvus/`  
**Description**: Open-source vector database for AI applications

**Key Features**:
- High-performance vector similarity search
- Scalable architecture for large datasets
- Multiple index types for optimization
- Integration with watsonx.data OpenSearch
- Support for various embedding models

**Quick Start**:
```bash
cd milvus/assets/data-ingestion-asset
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
python main.py
```

### 2. DataStax Astra DB
**Location**: `datastax-astradb/`  
**Description**: Cloud-native vector database with Cassandra compatibility

**Key Features**:
- Serverless vector database
- Global distribution
- Built on Apache Cassandra
- Vector collections support
- Integrated with IBM Watsonx embeddings

### 3. OpenSearch
**Location**: `opensearch/`  
**Description**: Open-source search and analytics engine with vector capabilities

**Key Features**:
- Full-text and vector search
- Real-time indexing
- Distributed architecture
- Integration with watsonx.data

## Use Cases

- **Semantic Search**: Find similar documents based on meaning
- **Recommendation Systems**: Content and product recommendations
- **Question Answering**: RAG-based Q&A systems
- **Image Search**: Visual similarity matching
- **Anomaly Detection**: Identify unusual patterns

## Bob Modes

AI-assisted development modes available for vector search implementation:
- Vector search builder mode
- Data ingestion automation
- Index optimization guidance

---

For detailed setup, see individual component READMEs.