# Retrieval-Augmented Generation (RAG)

**IBM products**: IBM watsonx.data, IBM watsonx.ai, IBM Cloud Object Storage

This folder contains a **custom/reference RAG implementation** for developers who want to understand or extend ingestion, embeddings, vector retrieval, MCP/REST access, and answer generation.

For new managed deployments, evaluate **IBM watsonx.data OpenRAG** first. The code here is not the managed OpenRAG service.

## Architecture

```text
IBM Cloud Object Storage
          |
          v
 document parsing / chunking
          |
          v
     IBM watsonx.ai
        embeddings
          |
          v
 OpenSearch or Milvus
      vector index
          |
          v
 semantic / keyword retrieval
          |
          v
     IBM watsonx.ai
        generation
          |
          v
 REST / MCP / application
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/rag-accelerator/`](assets/rag-accelerator/) | Combined ingestion, vector search, and Q&A FastAPI service |
| [`assets/opensearch-data-ingestion/`](assets/opensearch-data-ingestion/) | COS -> chunk -> embedding -> OpenSearch ingestion |
| [`assets/rag-ingestion-sse-mcp-server/`](assets/rag-ingestion-sse-mcp-server/) | MCP tools for ingestion |
| [`assets/rag-retrieval-fastapi-server/`](assets/rag-retrieval-fastapi-server/) | REST retrieval service |
| [`assets/rag-retrieval-sse-mcp-server/`](assets/rag-retrieval-sse-mcp-server/) | MCP retrieval tools |
| [`bob-modes/`](bob-modes/) | 4 IBM Bob modes |
| [`bob-skills/`](bob-skills/) | 3 IBM Bob skills |

## Pick an asset

- Want one service for ingestion + retrieval + Q&A? Start with [`rag-accelerator`](assets/rag-accelerator/).
- Want a focused OpenSearch ingestion pipeline? Use [`opensearch-data-ingestion`](assets/opensearch-data-ingestion/).
- Need retrieval as a REST API? Use [`rag-retrieval-fastapi-server`](assets/rag-retrieval-fastapi-server/).
- Need Bob/agent tool access? Use one of the MCP server assets.

## Quick start

For the combined accelerator:

```bash
cd assets/rag-accelerator
cp .env.example .env
# Configure IBM Cloud, watsonx.ai, COS, and your selected vector store.
pip install -r requirements.txt
python main.py
```

Read [`assets/rag-accelerator/README.md`](assets/rag-accelerator/README.md) before running because required variables differ by vector-store choice.

## Model defaults

The package uses current IBM examples such as:

```text
WATSONX_EMBEDDING_MODEL_ID=ibm/granite-embedding-278m-multilingual
WATSONX_GENERATION_MODEL_ID=ibm/granite-4-h-small
```

Do not treat these IDs as permanent. Verify the target deployment before provisioning indexes or deploying an application:

- Supported foundation models: https://www.ibm.com/docs/en/watsonx/saas?topic=solutions-supported-foundation-models
- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

Embedding dimensions must match the configured vector index/collection.

## Production checklist

- Use TLS certificate verification.
- Store credentials outside source control.
- Apply access control at source, retrieval, and generation layers.
- Test retrieval with representative enterprise questions.
- Validate chunking and metadata strategy against your data.
- Define grounding/citation behavior in the consuming application.
- Monitor latency, token usage, recall, and answer quality.
- Re-index when changing to an embedding model with incompatible dimensions.

## IBM references

- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- IBM watsonx.data OpenRAG provisioning: https://www.ibm.com/docs/en/watsonxdata/saas?topic=openrag-provisioning
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
