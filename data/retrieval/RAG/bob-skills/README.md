# RAG Bob Skills

Bob skills for **RAG (Retrieval-Augmented Generation)** pipeline development using **IBM watsonx.ai**, **IBM watsonx.data OpenSearch**, and **IBM Cloud Object Storage**.

## Overview

These skills empower IBM Bob to help you design, build, and deploy end-to-end IBM RAG pipelines — from document ingestion to hybrid search and LLM-powered Q&A — and to expose RAG capabilities as MCP tools for AI assistants.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `rag-pipeline-builder` | [`rag-pipeline-builder.zip`](rag-pipeline-builder.zip) | Designing or building a complete RAG pipeline — ingestion, embedding, indexing, hybrid search, Q&A |
| `rag-mcp-server-builder` | [`rag-mcp-server-builder.zip`](rag-mcp-server-builder.zip) | Building MCP servers that expose RAG ingestion or retrieval as AI tools for Bob/Claude |

---

### `rag-pipeline-builder`

A comprehensive skill for designing end-to-end IBM RAG pipelines:

- IBM watsonx.ai embedding generation (`ibm/slate-125m-english-rtrvr`, dim=768)
- IBM watsonx.ai LLM generation (Granite, Llama) with `langchain_ibm.WatsonxLLM`
- Chunking strategy optimisation for PDF, DOCX, HTML, Markdown, TXT
- IBM watsonx.data OpenSearch hybrid search design (vector + BM25 with score fusion)
- RAG evaluation metrics (RAGAS: faithfulness, answer relevancy, context precision)
- IBM COS document source integration with `ibm-cos-sdk` IAM OAuth
- FastAPI service patterns for `/ingest`, `/query`, `/qna` endpoints

### `rag-mcp-server-builder`

A comprehensive skill for building RAG MCP servers:

- MCP server scaffolding with FastMCP (SSE Streamable HTTP transport)
- Tool patterns: `ingest_from_cos`, `search_documents`, `keyword_search`, `ask_question`
- IBM watsonx.ai embedding integration inside MCP tool handlers
- IBM watsonx.data OpenSearch integration (index creation, bulk insert, k-NN search)
- IBM Code Engine deployment for remote SSE-based MCP servers
- IBM Bob and Claude MCP integration configuration
- Pydantic v2 input validation for MCP tool arguments

---

## Installation

### Step 1 — Install the skill

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip rag-pipeline-builder.zip
unzip rag-mcp-server-builder.zip
```

This will create:
```
.bob/skills/rag-pipeline-builder/SKILL.md
.bob/skills/rag-mcp-server-builder/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What RAG skills do you have active?"* — Bob should confirm the skill is loaded.

---

## Usage Examples

Once activated, you can ask Bob:

- *"Design a RAG pipeline for PDF documents stored in IBM COS, using OpenSearch hybrid search"*
- *"Generate the ingestion FastAPI endpoint for chunking and embedding documents"*
- *"Build an MCP server that exposes a `search_documents` tool using IBM watsonx.data OpenSearch"*
- *"Evaluate my RAG pipeline with RAGAS metrics"*
- *"Deploy my RAG MCP server to IBM Code Engine"*

---

## What Bob Can Help You Build

With these skills, Bob can generate:

1. **Complete RAG Services**: FastAPI apps with `/ingest`, `/query`, and `/qna` endpoints
2. **MCP Servers**: SSE-transport servers exposable to Bob, Claude, and other MCP clients
3. **Hybrid Search Queries**: OpenSearch k-NN + BM25 queries with score fusion
4. **Embedding Pipelines**: IBM watsonx.ai embedding code for batch and query embedding
5. **Chunking Logic**: Adaptive text splitting strategies for different document types
6. **Deployment Configs**: IBM Code Engine deployment manifests for RAG services

---

## Prerequisites

- IBM watsonx.ai project with embedding and generation model access
- IBM watsonx.data instance with OpenSearch provisioned for vector storage
- IBM Cloud Object Storage bucket with source documents
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))

## Skill Capabilities Summary

| Capability | rag-pipeline-builder | rag-mcp-server-builder |
|---|---|---|
| Embedding generation (IBM watsonx.ai) | ✅ | ✅ |
| OpenSearch k-NN index creation | ✅ | ✅ |
| Hybrid search (vector + BM25) | ✅ | ✅ |
| LLM generation (Granite, Llama) | ✅ | — |
| MCP tool registration | — | ✅ |
| SSE transport server | — | ✅ |
| IBM Code Engine deployment | — | ✅ |
| RAG evaluation (RAGAS) | ✅ | — |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/rag-pipeline-builder/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob doesn't use RAG patterns:**
1. Mention IBM watsonx.data OpenSearch explicitly in your prompt
2. Reference the skill by name: *"Using the rag-pipeline-builder skill..."*

## Related

- [`../bob-modes/`](../bob-modes/) — Bob Modes for RAG (RAG Builder, Ingestion Builder, Retrieval Builder)
- [`../README.md`](../README.md) — RAG building block overview and Getting Started guide
- [`../assets/`](../assets/) — Deployable RAG server assets (FastAPI, MCP servers)
