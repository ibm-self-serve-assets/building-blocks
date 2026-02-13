# RAG Ingestion MCP Server

This MCP server’s only job is to **ingest files from IBM Cloud Object Storage (COS)** into a **vector database** so you can later use them for RAG (retrieval augmented generation).

It is built on the **MCP Python SDK (FastMCP)** using the Streamable HTTP transport (`/mcp`).

---

## What it does

1. Lists objects under a COS bucket + prefix
2. Downloads files to a temp directory
3. Loads & parses documents (PDF / TXT / MD / HTML / DOCX)
4. Splits into chunks (configurable)
5. Embeds chunks using **watsonx.ai Embeddings**
6. Writes embeddings + text + metadata to the configured **vector DB**
   - Supported in this template: **OpenSearch** and **Milvus**
   - Elasticsearch reserved (not implemented in the template)

---

## Tools

- `get_ingestion_config_status`  
  Shows what is configured (env vs runtime).

- `configure_cos(endpoint_url, api_key, resource_instance_id, bucket?, prefix?)`  
  Configure COS at runtime (only in-memory).

- `configure_embeddings(watsonx_api_key, watsonx_url, watsonx_project_id, embedding_model_id)`  
  Configure watsonx embeddings at runtime (only in-memory).

- `configure_chunking(chunk_size, chunk_overlap)`  
  Configure chunking.

- `configure_vector_db(vector_db_type, params_json)`  
  Configure the vector DB at runtime.
  - `vector_db_type`: `opensearch` or `milvus`
  - `params_json` examples:
    - OpenSearch:
      ```json
      {"url":"https://host:9200","index":"myindex","username":"admin","password":"***"}
      ```
    - Milvus:
      ```json
      {"host":"milvus.example.com","port":"19530","username":"user","password":"***","database":"default","collection":"mycol"}
      ```

- `ingest_from_cos(bucket?, prefix?, max_files?, allowed_extensions_csv?, dry_run?)`  
  Runs the ingestion.

---

## Environment variables

### Server
- `PORT` (default `8080`)
- `APP_BEARER_TOKEN` (optional)
- `PUBLIC_BASE_URL` (recommended on Code Engine)
- `ALLOWED_HOSTS`, `ALLOWED_ORIGINS` (optional overrides)

### COS (recommended to set via env)
- `COS_ENDPOINT_URL`
- `COS_API_KEY`
- `COS_RESOURCE_INSTANCE_ID`
- `COS_BUCKET`
- `COS_PREFIX` (optional)

### watsonx embeddings
- `WATSONX_API_KEY`
- `WATSONX_URL`
- `WATSONX_PROJECT_ID`
- `EMBEDDING_MODEL_ID`

### Chunking
- `CHUNK_SIZE` (default `1000`)
- `CHUNK_OVERLAP` (default `200`)

### Vector DB
- `VECTOR_DB_TYPE` = `opensearch` or `milvus`

#### OpenSearch
- `OPENSEARCH_URL`
- `OPENSEARCH_INDEX`
- `OPENSEARCH_USERNAME` (optional)
- `OPENSEARCH_PASSWORD` (optional)
- `OPENSEARCH_SSL_CERTIFICATE` (optional PEM content)

#### Milvus
- `MILVUS_HOST`
- `MILVUS_PORT`
- `MILVUS_USERNAME`
- `MILVUS_PASSWORD`
- `MILVUS_DATABASE` (optional, default `default`)
- `MILVUS_COLLECTION`
- `MILVUS_SSL_CERTIFICATE` (optional PEM content)

---

## Minimal `requirements.txt`

This depends on which loaders/DB you use, but a practical baseline is:

- `mcp`
- `starlette`
- `uvicorn`
- `ibm-cos-sdk`
- `ibm-watsonx-ai`
- `langchain`
- `langchain-community`
- `pypdf`
- `unstructured`
- `docx2txt`
- `opensearch-py` (if using OpenSearch)
- `pymilvus` (if using Milvus)

---

## Run locally

```bash
export PORT=8080
export COS_ENDPOINT_URL=...
export COS_API_KEY=...
export COS_RESOURCE_INSTANCE_ID=...
export COS_BUCKET=...
export COS_PREFIX=my-folder/

export WATSONX_API_KEY=...
export WATSONX_URL=https://us-south.ml.cloud.ibm.com
export WATSONX_PROJECT_ID=...
export EMBEDDING_MODEL_ID=...

export VECTOR_DB_TYPE=opensearch
export OPENSEARCH_URL=https://localhost:9200
export OPENSEARCH_INDEX=myindex
export OPENSEARCH_USERNAME=admin
export OPENSEARCH_PASSWORD=admin

python server_ingestion.py
```

Then call the MCP tool `ingest_from_cos` (or set `dry_run=true` first).

---

## Notes

- Runtime configuration tools **store values only in memory** (good for quick tests). In production, set env vars.
- If you want to keep *exact* parsing/chunking behavior from your notebook, you can port those functions into this server and replace:
  - `load_documents()`
  - `split_documents()`
  - `WatsonxEmbedder.embed_texts()`
- If you need additional document types (pptx, xlsx, etc.), add loaders in `_guess_loader()`.
