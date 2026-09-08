# Bob Modes for RAG

Custom IBM Bob mode configurations for **RAG (Retrieval-Augmented Generation)** pipeline development using **IBM watsonx.ai**, **IBM watsonx.data**, and **IBM Cloud Object Storage**.

---

## Overview

Three focused Bob modes covering the full RAG lifecycle — end-to-end pipeline design, ingestion specialist, and retrieval + generation specialist.

---

## What's Included

- **[`base-modes/rag-builder.zip`](base-modes/rag-builder.zip)**: End-to-end RAG pipeline expert mode
- **[`base-modes/rag-ingestion.zip`](base-modes/rag-ingestion.zip)**: RAG ingestion specialist mode
- **[`base-modes/rag-retrieval.zip`](base-modes/rag-retrieval.zip)**: RAG retrieval + generation specialist mode

---

## Mode Descriptions

### RAG Builder (`rag-builder.zip`)

Full end-to-end RAG architect — use when you need to design or build a complete RAG system from scratch.

**Capabilities**:
- RAG architecture design using IBM watsonx.data OpenSearch as the hybrid search backend
- Chunking strategy selection for PDF, DOCX, HTML, Markdown, and TXT documents
- IBM watsonx.ai embedding model selection (`ibm/slate-125m-english-rtrvr` vs multilingual)
- OpenSearch k-NN index design (HNSW, cosine) and hybrid search score fusion
- MCP server design for AI assistant integration (SSE transport, FastMCP)
- RAG evaluation framework (RAGAS: faithfulness, answer relevancy, context precision)
- FastAPI service architecture for `/ingest`, `/query`, and `/qna` endpoints
- Docker containerization and IBM Code Engine deployment

---

### RAG Ingestion Builder (`rag-ingestion.zip`)

Focused ingestion specialist — use when building or debugging document ingestion pipelines.

**Capabilities**:
- IBM COS document source integration with `ibm-cos-sdk` IAM OAuth
- LangChain document loaders: PDF, DOCX, PPTX, HTML, Markdown, TXT
- `RecursiveCharacterTextSplitter` chunking with `chunk_size` and `chunk_overlap` tuning
- IBM watsonx.ai `Embeddings.embed_documents()` batch call patterns
- OpenSearch bulk indexing via `opensearch-py.helpers.bulk()`
- IBM Databand OpenLineage event emission for ingestion pipeline observability
- MCP ingestion tool design: `ingest_from_cos`, `list_indexed_documents`, `delete_document`
- `.env.example` and `requirements.txt` generation following building-blocks conventions

---

### RAG Retrieval Builder (`rag-retrieval.zip`)

Focused retrieval and generation specialist — use when building or tuning RAG search and Q&A.

**Capabilities**:
- Hybrid search (dense vector + BM25 keyword) on IBM watsonx.data OpenSearch
- Top-K cosine vector similarity search via OpenSearch k-NN plugin
- IBM watsonx.ai LLM generation (`ibm/granite-13b-instruct-v2`) for RAG Q&A
- `langchain_ibm.WatsonxLLM` prompt template design for retrieval-augmented answers
- Reranking patterns with cross-encoder models
- RAGAS evaluation metrics: faithfulness, answer relevancy, context recall, context precision
- Streaming SSE response generation for real-time answer delivery
- MCP retrieval tool design: `search_documents`, `keyword_search`, `ask_question`
- FastAPI `/retrieve`, `/keyword_search`, `/health` endpoint patterns

---

## When to Use Each Mode

| Scenario | Recommended Mode |
|---|---|
| Designing a new RAG system end-to-end | `rag-builder.zip` |
| Building document ingestion from IBM COS | `rag-ingestion.zip` |
| Debugging chunking or embedding issues | `rag-ingestion.zip` |
| Optimising vector search recall | `rag-retrieval.zip` |
| Building a RAG Q&A API | `rag-retrieval.zip` |
| Evaluating RAG quality with RAGAS | `rag-retrieval.zip` |
| Designing MCP server tools for Bob/Claude | `rag-builder.zip` |

---

## Installing Bob Modes

### Installing a Custom Bob Mode

Each mode zip ([`base-modes/rag-builder.zip`](base-modes/rag-builder.zip), [`base-modes/rag-ingestion.zip`](base-modes/rag-ingestion.zip), [`base-modes/rag-retrieval.zip`](base-modes/rag-retrieval.zip)) defines the behavior, expertise, and capabilities of IBM Bob for that RAG specialisation.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/rag-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
Copy-Item base-modes/rag-ingestion.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
Copy-Item base-modes/rag-retrieval.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/rag-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
cp base-modes/rag-ingestion.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
cp base-modes/rag-retrieval.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new modes to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.
