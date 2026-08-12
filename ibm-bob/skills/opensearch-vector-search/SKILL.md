---
name: opensearch-vector-search
description: Expert guidance for IBM watsonx.data OpenSearch vector search — covers k-NN index design with HNSW, IBM watsonx.ai embedding integration (ibm/slate-125m-english-rtrvr), document ingestion from IBM COS, hybrid search (BM25 + k-NN), score normalisation, and performance tuning. Generates production-ready Python 3.12 FastAPI services following IBM building-blocks conventions.
---

# IBM watsonx.data OpenSearch Vector Search Builder

## Purpose

This skill defines the complete workflow for building **IBM watsonx.data OpenSearch** vector search applications using **IBM watsonx.ai embeddings** and **IBM Cloud Object Storage** as the document source. Generates deployable Python 3.12 FastAPI services.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| IBM watsonx.data (OpenSearch) | k-NN vector index, BM25 full-text search, hybrid search |
| IBM watsonx.ai | Embedding generation: ibm/slate-125m-english-rtrvr, ibm/slate-30m-english-rtrvr |
| IBM Cloud Object Storage | Document source bucket with ibm-cos-sdk download |
| IBM Cloud IAM | POST /identity/token (apikey grant) for watsonx.ai auth |

## Objective

Transform natural language vector search requirements into **deployable services** that:

- Create optimised k-NN indexes in IBM watsonx.data OpenSearch
- Generate embeddings using IBM watsonx.ai models
- Ingest documents from IBM COS with chunking via `unstructured`
- Perform vector, keyword, and hybrid search
- Follow Python 3.12 best practices with Pydantic v2

## Rules

- Always use `ibm_watsonx_ai.foundation_models.Embeddings` for IBM embeddings
- IBM watsonx.ai base URL: `https://us-south.ml.cloud.ibm.com` (or configured region)
- Use `opensearch-py` with SSL/TLS for watsonx.data managed OpenSearch
- Default embedding model: `ibm/slate-125m-english-rtrvr` (dim=768)
- Wrap IBM COS calls with `ibm-cos-sdk` (IAM OAuth, not HMAC)

---

## Scope

- IBM watsonx.data OpenSearch k-NN index creation and management
- IBM watsonx.ai embedding generation for ingestion and query
- Document ingestion from IBM COS using `unstructured`
- k-NN vector search, BM25 keyword search, hybrid search
- Score normalisation and result reranking

---

## Procedure

### Phase 1: IBM watsonx.ai Embeddings

```python
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import Embeddings

embedder = Embeddings(
    model_id="ibm/slate-125m-english-rtrvr",   # dim=768
    credentials=Credentials(url="https://us-south.ml.cloud.ibm.com", api_key=IBM_API_KEY),
    project_id=WATSONX_PROJECT_ID,
)
vectors = embedder.embed_documents(["text chunk 1", "text chunk 2"])
```

### Phase 2: k-NN Index Mapping

```python
body = {
    "settings": {"index": {"knn": True}},
    "mappings": {
        "properties": {
            "vector": {
                "type": "knn_vector",
                "dimension": 768,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "nmslib",
                    "parameters": {"ef_construction": 128, "m": 24},
                },
            },
            "text":  {"type": "text"},
            "title": {"type": "keyword"},
        }
    },
}
client.indices.create(index=index_name, body=body)
```

### Phase 3: Hybrid Search Query

```python
query_vector = embedder.embed_query(user_query)

hybrid_query = {
    "query": {
        "bool": {
            "should": [
                # k-NN vector search
                {"knn": {"vector": {"vector": query_vector, "k": 10}}},
                # BM25 keyword search
                {"match": {"text": {"query": user_query, "boost": 0.3}}},
            ]
        }
    },
    "_source": ["text", "title", "source", "page_number"],
    "size": 10,
}
results = client.search(index=index_name, body=hybrid_query)
```

### Phase 4: IBM COS Document Source

```python
import ibm_boto3
from ibm_botocore.client import Config

cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
)
cos.download_file(bucket, key, local_path)
```

### Phase 5: Document Chunking

```python
from unstructured.partition.auto import partition
from langchain_text_splitters import RecursiveCharacterTextSplitter

elements = partition(filename=path)
text = "\n".join(str(e) for e in elements)
chunks = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128).split_text(text)
```

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| IBM watsonx.ai (us-south) | `https://us-south.ml.cloud.ibm.com` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |

### Embedding Model Reference

| Model ID | Dimension | Use Case |
|---|---|---|
| `ibm/slate-125m-english-rtrvr` | 768 | English RAG (recommended) |
| `ibm/slate-30m-english-rtrvr` | 384 | Lightweight English RAG |
| `intfloat/multilingual-e5-large` | 1024 | Multilingual RAG |
