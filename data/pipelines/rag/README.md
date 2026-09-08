# Retrieval-Augmented Generation (RAG)

**IBM products**: IBM watsonx.data, IBM watsonx.ai, IBM Cloud Object Storage

Reference assets for document ingestion, vector retrieval, MCP/REST access, and answer generation. This repository includes a **custom/reference implementation**; it is not the managed IBM watsonx.data OpenRAG service itself.

## Included assets

| Path | Purpose |
|---|---|
| [`assets/rag-accelerator/`](assets/rag-accelerator/) | Combined ingestion and Q&A reference service |
| [`assets/opensearch-data-ingestion/`](assets/opensearch-data-ingestion/) | COS → chunk → embedding → OpenSearch ingestion |
| [`assets/rag-ingestion-sse-mcp-server/`](assets/rag-ingestion-sse-mcp-server/) | MCP ingestion tools for IBM Bob |
| [`assets/rag-retrieval-fastapi-server/`](assets/rag-retrieval-fastapi-server/) | REST retrieval/Q&A service |
| [`assets/rag-retrieval-sse-mcp-server/`](assets/rag-retrieval-sse-mcp-server/) | MCP retrieval tools for IBM Bob |
| [`bob-modes/`](bob-modes/) | 4 IBM Bob modes: RAG, ingestion, retrieval, OpenSearch |
| [`bob-skills/`](bob-skills/) | 3 IBM Bob skills: pipeline, vector search, MCP server |

## Product positioning

For new managed RAG deployments, evaluate **IBM watsonx.data OpenRAG** first. Use these assets when you need a transparent/custom reference pipeline or need to extend existing OpenSearch-based implementations.

OpenSearch is an implementation technology in these assets; the IBM product anchors are watsonx.data and watsonx.ai.

## Model defaults

```text
WATSONX_EMBEDDING_MODEL_ID=ibm/granite-embedding-278m-multilingual
WATSONX_GENERATION_MODEL_ID=ibm/granite-4-h-small
```

Treat these as examples. Availability varies by deployment and region.

- Supported foundation models: https://www.ibm.com/docs/en/watsonx/saas?topic=solutions-supported-foundation-models
- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

## Security and production checks

- Keep credentials in environment variables or a secrets manager.
- Use TLS verification; do not disable certificate validation.
- Apply access control at the source, vector store, and generation layers.
- Evaluate retrieval quality with representative enterprise queries before production.
- Keep embedding dimensions aligned with the configured vector index.

## IBM references

- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- IBM watsonx.data OpenRAG provisioning/availability: https://www.ibm.com/docs/en/watsonxdata/saas?topic=openrag-provisioning
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
- IBM watsonx.ai RAG model selection: https://www.ibm.com/docs/en/watsonx/saas?topic=models-choosing-model
