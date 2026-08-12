---
name: rag-pipeline-builder
description: Expert guidance for designing end-to-end IBM RAG pipelines — covers chunking strategy selection, IBM watsonx.ai embedding model choice (ibm/slate-125m-english-rtrvr), vector DB selection (IBM watsonx.data Milvus vs OpenSearch), hybrid search tuning, IBM COS document source, reranking with IBM watsonx.ai cross-encoder models, and RAG pipeline evaluation. Generates production-ready Python 3.12 code following IBM building-blocks patterns.
---

# IBM RAG Pipeline Builder

## Purpose

Expert guidance for designing and implementing complete **IBM RAG (Retrieval-Augmented Generation)** pipelines using IBM Cloud services. Covers every stage from document ingestion to LLM answer generation.

## IBM Cloud Product Coverage

| IBM Cloud Product | RAG Stage |
|---|---|
| IBM Cloud Object Storage | Document source |
| IBM watsonx.ai | Embedding generation + LLM generation (Granite, Llama) |
| IBM watsonx.data (Milvus) | Primary vector store for high-scale RAG |
| IBM watsonx.data (OpenSearch) | Vector + BM25 hybrid search |
| IBM DataStax Astra DB (HCD) | Alternative vector store for global distribution |

## Rules

- Preferred embedding model: `ibm/slate-125m-english-rtrvr` (dim=768)
- Preferred generation models: `ibm/granite-3-8b-instruct`, `meta-llama/llama-3-3-70b-instruct`
- Use `ibm_watsonx_ai.foundation_models.Embeddings` for embedding generation
- Use `langchain_ibm.WatsonxLLM` or `ibm_watsonx_ai` inference API for generation
- Chunking default: `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)`
- Hybrid search: always combine vector + BM25 (weight: 70% vector, 30% BM25)
- Reranking: use `ibm/slate-125m-english-rtrvr` cross-encoder or BM25 score fusion

---

## Scope

- RAG architecture selection (Milvus vs OpenSearch vs AstraDB)
- Chunking strategy optimisation for different document types
- IBM watsonx.ai embedding and generation integration
- Hybrid search design and score normalisation
- RAG evaluation with RAGAS metrics
- MCP server design for RAG tool exposure

---

## RAG Architecture Decision Matrix

| Criterion | Milvus | OpenSearch | AstraDB |
|---|---|---|---|
| Scale | Billion-scale | Million-scale | Global scale |
| Hybrid search | Manual | Native BM25 | Manual |
| Deployment | IBM watsonx.data | IBM watsonx.data | IBM HCD SaaS |
| Best for | Large-scale RAG | Enterprise search + RAG | Global SaaS RAG |

---

## Procedure

### Phase 1: Embedding Generation

```python
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

embedder = Embeddings(
    model_id="ibm/slate-125m-english-rtrvr",
    credentials=Credentials(url="https://us-south.ml.cloud.ibm.com", api_key=IBM_API_KEY),
    project_id=WATSONX_PROJECT_ID,
)
query_vector = embedder.embed_query(user_question)
doc_vectors = embedder.embed_documents(chunks)
```

### Phase 2: Generation with IBM watsonx.ai

```python
from langchain_ibm import WatsonxLLM

llm = WatsonxLLM(
    model_id="ibm/granite-3-8b-instruct",
    url="https://us-south.ml.cloud.ibm.com",
    apikey=IBM_API_KEY,
    project_id=WATSONX_PROJECT_ID,
    params={"max_new_tokens": 512, "min_new_tokens": 1, "temperature": 0.7},
)

prompt = f"""Answer the question based on the context below.
Context: {retrieved_context}
Question: {user_question}
Answer:"""
answer = llm.invoke(prompt)
```

### Phase 3: Hybrid Search Score Fusion

```python
# Normalise vector search scores to [0, 1]
def normalize_scores(results: list) -> list:
    scores = [r["score"] for r in results]
    min_s, max_s = min(scores), max(scores)
    for r in results:
        r["normalized_score"] = (r["score"] - min_s) / (max_s - min_s + 1e-9)
    return results

# Reciprocal Rank Fusion (RRF)
def rrf_fusion(vector_results: list, bm25_results: list, k: int = 60) -> list:
    scores: dict = {}
    for rank, doc in enumerate(vector_results):
        scores[doc["id"]] = scores.get(doc["id"], 0) + 1 / (rank + k)
    for rank, doc in enumerate(bm25_results):
        scores[doc["id"]] = scores.get(doc["id"], 0) + 1 / (rank + k)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| IBM watsonx.ai (us-south) | `https://us-south.ml.cloud.ibm.com` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
