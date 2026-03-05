# Question and Answer

Natural language interfaces to interact with data through RAG (Retrieval-Augmented Generation) and Text-to-SQL powered by IBM watsonx.

## What's Included

### RAG (Retrieval-Augmented Generation)

- **[RAG Accelerator](./rag/assets/rag-accelerator/)**: Complete RAG pipeline with document processing, embedding, and querying
- **[RAG Ingestion MCP Server](./rag/assets/rag-ingestion-sse-mcp-server/)**: MCP server for document ingestion from IBM COS
- **[RAG Retrieval MCP Server](./rag/assets/rag-retrieval-sse-mcp-server/)**: MCP server for semantic and keyword search
- **[Base SSE MCP Server](./rag/assets/base-sse-mcp-server/)**: Template for building custom MCP servers
- **[Bob Modes](./rag/bob-modes/)**: AI assistant mode specialized for RAG development

### Text-to-SQL

- **[Metadata Enrichment](./text-to-sql/assets/asset-1/metadata_enrichment_text2sql/)**: Enhance SQL generation with enriched metadata
- **[Applications](./text-to-sql/applications/)**: FastAPI tools for Text-to-SQL services
- **[Deployment Guides](./text-to-sql/applications/)**: OpenShift and Code Engine deployment instructions

## Quick Start

### RAG Quick Start

1. **Choose your path**:
   - **Complete pipeline**: Navigate to `rag/assets/rag-accelerator/`
   - **MCP servers**: Navigate to `rag/assets/rag-ingestion-sse-mcp-server/` or `rag/assets/rag-retrieval-sse-mcp-server/`

2. **Follow the detailed README** in each directory for setup instructions

### Text-to-SQL Quick Start

1. **Choose your deployment**:
   - **Metadata enrichment**: Navigate to `text-to-sql/assets/asset-1/metadata_enrichment_text2sql/`
   - **FastAPI application**: Navigate to `text-to-sql/assets/asset-1/applications/`
   - **Deployment**: Check `text-to-sql/assets/asset-1/applications/code-engine-setup/` or `text-to-sql/assets/asset-1/applications/openshift-setup/`

2. **Follow the detailed README** in each directory
