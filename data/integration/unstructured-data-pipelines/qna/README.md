# Search Capability

**Core Capability**: Activation
**IBM Products**: watsonx.data
**Product Components**: RAG accelerator

## Overview

Build grounded enterprise Q&A over documents and data using retrieval-augmented generation with configurable retrieval and response pipelines.

## Building Blocks

### 1. QnA RAG
**Location**: `qna-rag/`
**IBM Products**: watsonx.data, RAG accelerator, Milvus/OpenSearch
**Description**: Question & Answer with Retrieval Augmented Generation

**Quick Start**:
```bash
cd qna-rag/rag-accelerator
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
python main.py
```

**Components**:
- `rag-accelerator/` - Main RAG application
- `rag-ingestion-sse-mcp-server/` - MCP server for ingestion
- `rag-retrieval-sse-mcp-server/` - MCP server for retrieval
- `base-sse-mcp-server/` - Base MCP server template
- `bob-modes/` - Bob AI assistant modes

### 2. Text-to-SQL
**Location**: `text-to-sql/`  
**IBM Products**: watsonx.data, watsonx.ai  
**Description**: Natural language to SQL query generation

**Quick Start**:
```bash
cd text-to-sql/asset-1/applications/text_to_sql_app
cp .env.example .env
# Edit .env with your credentials
pip install -r requirements.txt
python app.py
```

**Components**:
- `asset-1/applications/text_to_sql_app/` - Web application
- `asset-1/metadata_enrichment_text2sql/` - Metadata enrichment
- `bob-modes/` - Bob AI assistant modes

---

For detailed setup, see individual component READMEs.