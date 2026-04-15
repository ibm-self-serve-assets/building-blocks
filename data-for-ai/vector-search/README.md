# Vector Search Capability

## Building Blocks

### 1. Milvus
**Location**: `milvus/`  
**IBM Products**: Milvus, watsonx.data  
**Description**: Vector database for semantic search

**Quick Start**:
```bash
cd milvus/data-ingestion-asset
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
python main.py
```

### 2. OpenSearch
**Location**: `opensearch/`  
**IBM Products**: watsonx.data OpenSearch  
**Description**: OpenSearch with vector search capabilities

**Status**: See individual asset README

### 3. DataStax Astra DB
**Location**: `datastax-astradb/`  
**IBM Products**: DataStax Astra DB  
**Description**: Cloud-native NoSQL with vector search

**Status**: See individual asset README

---

For detailed setup, see individual component READMEs.