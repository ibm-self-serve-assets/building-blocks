# 🔍 RAG Builder Mode for IBM Bob

A specialized mode for IBM Bob that provides expert guidance on Retrieval-Augmented Generation (RAG) systems, vector databases, embedding strategies, and document processing pipelines.

## Overview

The RAG Builder mode transforms IBM Bob into a RAG systems expert with deep knowledge in:

- **Vector Databases**: OpenSearch, Milvus, Elasticsearch
- **Embedding Models**: IBM Watsonx, OpenAI, Cohere, HuggingFace
- **Document Processing**: Chunking strategies, metadata extraction, format handling
- **RAG Architectures**: Naive RAG, Advanced RAG, Modular RAG, Agentic RAG
- **Search Implementations**: Semantic search, hybrid search (BM25 + vector)
- **Optimization**: Reranking, query expansion, retrieval quality metrics
- **MCP Server Development**: FastMCP patterns, tool implementation
- **IBM Cloud Integration**: Watsonx, Cloud Object Storage, security best practices

## What RAG Builder Can Do

### 1. Document Processing & Ingestion

**Capabilities:**
- Analyze document formats and recommend appropriate loaders
- Design optimal chunking strategies based on document type and use case
- Implement metadata extraction and preservation (title, source, page numbers, timestamps)
- Configure semantic boundary detection for intelligent text splitting
- Set up document ingestion pipelines from various sources (COS, local files, URLs)

**Example Tasks:**
- "Design a chunking strategy for technical documentation"
- "Set up document ingestion from IBM Cloud Object Storage"
- "Extract metadata from PDF files during ingestion"
- "Optimize chunk size for better retrieval quality"

### 2. Embedding Strategy & Configuration

**Capabilities:**
- Recommend embedding models based on language, domain, and performance requirements
- Analyze embedding dimensions and their impact on storage and retrieval
- Design batch processing workflows for large document sets
- Implement error handling for embedding API calls
- Configure IBM Watsonx embeddings integration
- Compare embedding models (multilingual-e5-large, BGE, MiniLM, etc.)

**Example Tasks:**
- "Which embedding model should I use for multilingual technical docs?"
- "Configure IBM Watsonx embeddings for my RAG pipeline"
- "Optimize embedding batch size for cost efficiency"
- "Compare 384d vs 768d embeddings for my use case"

### 3. Vector Database Design & Optimization

**Capabilities:**
- Select appropriate vector database based on requirements (scale, latency, cost, features)
- Configure OpenSearch for hybrid search (BM25 + kNN)
- Set up Milvus for high-performance vector search
- Design index schemas and collection structures
- Optimize vector database parameters (ef_search, space_type, refresh_interval)
- Implement connection pooling and retry logic

**Example Tasks:**
- "Should I use OpenSearch or Milvus for my RAG system?"
- "Configure OpenSearch index for hybrid search"
- "Optimize Milvus collection for 10M+ vectors"
- "Set up vector database connection with proper error handling"

### 4. Retrieval Optimization

**Capabilities:**
- Implement hybrid search combining BM25 and dense vectors
- Design reranking strategies for improved relevance
- Configure metadata filtering to narrow search scope
- Implement query expansion and reformulation techniques
- Optimize retrieval parameters (k, similarity threshold, filters)
- Design MMR (Maximal Marginal Relevance) for result diversity

**Example Tasks:**
- "Implement hybrid search with BM25 and vector similarity"
- "Add reranking to improve retrieval precision"
- "Use metadata filters to search specific document sections"
- "Optimize k value for better recall/precision balance"

### 5. RAG Architecture Design

**Capabilities:**
- Design modular RAG pipelines with clear separation of concerns
- Implement comprehensive error handling and retry logic
- Design caching strategies for frequently accessed data
- Plan incremental updates and data freshness mechanisms
- Create naive RAG, advanced RAG, or agentic RAG architectures
- Design multi-stage retrieval pipelines

**Example Tasks:**
- "Design an end-to-end RAG pipeline for customer support"
- "Implement caching for frequently asked questions"
- "Create an agentic RAG system with tool use"
- "Design incremental document update workflow"

### 6. MCP Server Development

**Capabilities:**
- Build MCP servers following FastMCP patterns
- Implement tool definitions for RAG operations (ingest, retrieve, search)
- Design ENV-based configuration management
- Add bootstrap connectivity checks for all services
- Implement credential masking in logs and responses
- Create clear tool descriptions and parameter documentation
- Handle SSE (Server-Sent Events) for streaming responses

**Example Tasks:**
- "Create an MCP server for document ingestion"
- "Build retrieval tools with semantic and keyword search"
- "Implement configuration validation and bootstrap checks"
- "Add proper error handling to MCP tools"

### 7. IBM Cloud Integration

**Capabilities:**
- Configure IBM Watsonx for embeddings and LLM generation
- Set up IBM Cloud Object Storage for document sources
- Implement IBM Cloud security best practices
- Design UBI-based container images for deployment
- Configure IBM Cloud Code Engine deployment
- Implement IAM authentication and authorization

**Example Tasks:**
- "Integrate IBM Watsonx embeddings into my RAG pipeline"
- "Set up COS bucket for document ingestion"
- "Deploy RAG MCP server to IBM Cloud Code Engine"
- "Implement IAM-based authentication for MCP server"

### 8. RAG Evaluation & Quality Metrics

**Capabilities:**
- Implement retrieval quality metrics (precision@k, recall@k, F1)
- Measure faithfulness of generated answers to source documents
- Evaluate context precision and recall
- Design test suites with diverse query types
- Measure and optimize latency and throughput
- Implement A/B testing for chunking strategies
- Track embedding costs and vector storage usage

**Example Tasks:**
- "Implement precision@5 and recall@5 metrics"
- "Evaluate answer faithfulness to source documents"
- "Create test queries for RAG system evaluation"
- "Monitor and optimize retrieval latency"

### 9. Troubleshooting & Debugging

**Capabilities:**
- Diagnose connectivity issues (COS, embeddings, vector DB)
- Verify document format support and parsing
- Analyze chunking parameters for optimal size
- Validate embedding dimensions match vector DB schema
- Monitor API rate limits and quotas
- Debug vector DB index/collection configuration
- Identify and fix retrieval quality issues

**Example Tasks:**
- "Why is my document ingestion failing?"
- "Debug poor retrieval quality for technical queries"
- "Fix embedding dimension mismatch error"
- "Troubleshoot OpenSearch connection timeout"

### 10. Best Practices & Optimization

**Capabilities:**
- Validate configuration before processing
- Implement comprehensive error handling patterns
- Design logging for important events and metrics
- Optimize for scalability and maintainability
- Create clear documentation for configuration options
- Design testing strategies with sample documents
- Monitor and optimize costs (embeddings, storage, compute)

**Example Tasks:**
- "Review my RAG configuration for best practices"
- "Optimize embedding costs for large document sets"
- "Implement proper error handling throughout pipeline"
- "Design monitoring and alerting for RAG system"

## Integration with MCP Servers

RAG Builder mode works seamlessly with MCP servers for RAG operations:

### RAG Ingestion MCP Server
- **ingest_from_cos**: Ingest documents from IBM Cloud Object Storage
- **get_ingestion_configuration**: View current ingestion settings
- **get_server_info**: Check server status and environment

### RAG Retrieval MCP Server
- **retrieve**: Semantic search using embeddings
- **keyword_search**: BM25 keyword search (OpenSearch only)
- **get_retrieval_configuration**: View current retrieval settings

## Example Workflows

### Workflow 1: Setting Up a New RAG System

```
1. "Design a RAG architecture for technical documentation"
   → RAG Builder analyzes requirements and proposes architecture

2. "Configure OpenSearch for hybrid search"
   → RAG Builder provides index configuration and settings

3. "Set up document ingestion from COS"
   → RAG Builder configures ingestion pipeline with optimal chunking

4. "Implement retrieval with reranking"
   → RAG Builder designs retrieval flow with reranking strategy

5. "Add evaluation metrics"
   → RAG Builder implements precision, recall, and faithfulness metrics
```

### Workflow 2: Optimizing Existing RAG System

```
1. "Analyze my current RAG configuration"
   → RAG Builder reviews chunking, embeddings, retrieval settings

2. "Why is retrieval quality poor for technical terms?"
   → RAG Builder diagnoses issue and recommends hybrid search

3. "Implement the recommended improvements"
   → RAG Builder guides implementation of optimizations

4. "Measure improvement in retrieval quality"
   → RAG Builder sets up evaluation metrics and A/B testing
```

### Workflow 3: Building RAG MCP Server

```
1. "Create an MCP server for document ingestion"
   → RAG Builder scaffolds FastMCP server structure

2. "Add tools for COS ingestion and configuration"
   → RAG Builder implements tool definitions with proper schemas

3. "Implement error handling and validation"
   → RAG Builder adds comprehensive error handling patterns

4. "Deploy to IBM Cloud Code Engine"
   → RAG Builder provides deployment configuration and scripts
```

## Key Strengths

- **Comprehensive RAG Expertise**: Covers entire RAG pipeline from ingestion to retrieval
- **Vendor Agnostic**: Works with multiple vector databases and embedding providers
- **IBM Cloud Native**: Deep integration with IBM Watsonx and Cloud services
- **Production Ready**: Focuses on scalability, reliability, and best practices
- **MCP Server Patterns**: Expert in building RAG tools as MCP servers
- **Optimization Focused**: Emphasizes retrieval quality and cost efficiency
- **Troubleshooting**: Systematic approach to diagnosing and fixing issues

## When to Use RAG Builder Mode

Switch to RAG Builder mode when:

- ✅ Designing or implementing RAG systems
- ✅ Setting up vector databases and embeddings
- ✅ Creating document ingestion workflows
- ✅ Optimizing chunking and retrieval strategies
- ✅ Building MCP servers for RAG tools
- ✅ Integrating with IBM Watsonx or Cloud services
- ✅ Troubleshooting RAG performance issues
- ✅ Evaluating and improving RAG accuracy
- ✅ Implementing hybrid search capabilities
- ✅ Building knowledge base systems

## Related Resources

- IBM Watsonx Documentation
- OpenSearch Documentation
- Milvus Documentation
- FastMCP Documentation
- RAG Ingestion MCP Server
- RAG Retrieval MCP Server

---

**Ready to build RAG systems?** Switch to RAG Builder mode and start with:
- "Design a RAG pipeline for [your use case]"
- "Optimize my current RAG configuration"
- "Build an MCP server for document ingestion"
- "Troubleshoot poor retrieval quality"