---
id: rag
name: RAG
group: pipelines
capability: data
description: "Retrieval-Augmented Generation pipeline: document ingestion from IBM COS, watsonx.ai embeddings, vector storage in Milvus or OpenSearch, and hybrid semantic + BM25 search. Ships with a FastAPI service plus ingestion and retrieval MCP servers."
repo_path: streamhouse/pipelines/rag
docs_path: data-core/pipelines/rag/index.md
products:
  - watsonx.ai
  - watsonx.data
tags:
  - data
  - rag
  - retrieval
  - embeddings
  - milvus
  - opensearch
  - watsonx
  - ibm-cos
  - hybrid-search
  - bob-modes
bob_modes:
  - name: rag-builder
    type: base-modes
  - name: data-generator
    type: base-modes
---
<!-- New block — RAG. Ships with two Bob modes. -->

# RAG

Retrieval-Augmented Generation pipeline: document ingestion from IBM COS, watsonx.ai embeddings, vector storage in Milvus or OpenSearch, and hybrid semantic + BM25 search. Ships with a FastAPI service plus ingestion and retrieval MCP servers.

- **Repo**: [streamhouse/pipelines/rag](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/streamhouse/pipelines/rag)
- **Docs**: [data-core/pipelines/rag/index.md](https://ibm-self-serve-assets.github.io/building-blocks-docs/data-core/pipelines/rag/)

<!--
  Add longer-form description, screenshots, "when to use this block", and
  links to relevant Bob modes below. Anything outside the frontmatter is
  human-facing context and is NOT used for MCP queries.
-->
