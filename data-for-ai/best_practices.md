
# Data for AI Building Block

**Scope:** Zero-Copy Lakehouse · Vector Search · Q\&A: RAG, Text2SQL · Data Security and Encryption

---

## Folder Structure

```
data-for-ai/
├── README.md
├── .env.example                        # API keys & endpoints (copy to .env)
├── configs/
│   ├── connections.yaml                # COS, watsonx.data, vector backend
│   └── rag.yaml                        # small set of RAG knobs
├── lakehouse/
│   ├── create_iceberg.sql              # zero-copy external tables on COS
│   └── samples/                        # tiny demo docs/tables (10–100MB)
├── vector-search/
│   ├── ingest_job.py                   # load → chunk → embed → upsert vectors
│   └── utils/                          # loaders.py, chunkers.py
├── q-and-a/
│   ├── rag-api/                        # FastAPI: /health, /ingest, /query
│   │   ├── app.py
│   │   ├── routers.py
│   │   ├── prompts/
│   │   └── clients/                    # milvus_client.py / elastic_client.py / wxai_client.py
│   └── text2sql/
│       ├── demo_notebook.ipynb         # read-only Text2SQL demo
│       └── semantic_layer.yaml         # table/column docs + 3–5 examples
├── scripts/
│   ├── seed_data.sh                    # create tables, copy samples, build small index
│   ├── start_local.sh                  # export env; start RAG API; open notebook
│   └── cleanup.sh                      # drop demo tables/index; remove temp data
└── docs/
    ├── architecture.png                # single-page diagram
    └── troubleshooting.md              # short, practical fixes
```

---

## What’s Inside (and why)

* **Zero-Copy Lakehouse:** Iceberg external tables over COS; no ETL copies.
* **Vector Search:** Document parsing and chunking using Docling and ingesting chunked documents into Milvus with **hybrid retrieval** (BM25 + dense).
* **Q\&A (RAG):** FastAPI with `/ingest` and `/query`.
* **Q\&A Text2SQL:** Notebook that shows SQL before execution.
* **Data Security & Enrcyption:** 

---

## Prerequisites

* Python 3.10+
* Access to **IBM watsonx.ai**, **watsonx.data**, and an **IBM COS** bucket
* A vector backend: **Milvus** (recommended) or **Elasticsearch** (optional)

---

## Quickstart

```bash
# 1) Configure
cp .env.example .env
# Fill in WATSONX_* , COS_* , and either MILVUS_* or ES_* ; set REST_API_KEY

# 2) Seed data (creates Iceberg external tables, uploads samples, tiny index)
bash scripts/seed_data.sh

# 3) Run services (RAG API + open Text2SQL notebook)
bash scripts/start_local.sh
# Swagger UI: http://localhost:4050/docs

# 4) Try a query (replace YOUR_KEY)
curl -s -X POST "http://localhost:4050/query" \
  -H "REST_API_KEY: YOUR_KEY" -H "Content-Type: application/json" \
  -d '{"q":"What is in the demo docs?"}' | jq .

# 5) Cleanup
bash scripts/cleanup.sh
```

---

## Configuration (minimal)

### `.env.example`

```bash
# watsonx.ai
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_APIKEY=replace-me
WATSONX_PROJECT_ID=replace-me

# IBM COS
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_AUTH_ENDPOINT=https://iam.cloud.ibm.com/identity/token
COS_BUCKET=demo-datasets
IBM_CLOUD_API_KEY=replace-me

# Vector backend (choose one)
VECTOR_BACKEND=milvus            # or: elastic

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=root
MILVUS_PASSWORD=replace-me

# Elasticsearch (optional)
ES_HOSTS=http://localhost:9200
ES_USERNAME=elastic
ES_PASSWORD=replace-me

# RAG API
REST_API_KEY=change-me
ENABLE_TLS=false
```

### `configs/connections.yaml`

```yaml
lakehouse:
  catalog: demo_catalog
  schema: demo_schema
  iceberg_warehouse: s3a://demo-cos/warehouse

object_store:
  bucket: demo-datasets
  endpoint: https://s3.us-south.cloud-object-storage.appdomain.cloud

vector:
  backend: ${VECTOR_BACKEND}   # milvus | elastic
  milvus:
    host: ${MILVUS_HOST}
    port: ${MILVUS_PORT}
    user: ${MILVUS_USER}
    password: ${MILVUS_PASSWORD}
    collection: demo_docs
    index:
      type: HNSW
      metric: COSINE
      M: 32
      efConstruction: 200
  elastic:
    hosts: [${ES_HOSTS}]
    username: ${ES_USERNAME}
    password: ${ES_PASSWORD}
    index: demo_docs
```

### `configs/rag.yaml`

```yaml
embedding:
  model_id: <your-embed-model>       # placeholder
  dim: 768
  batch_size: 32
  hybrid_sparse: true

chunking:
  type: DOCLING_DOCS                  # MARKDOWN | RECURSIVE
  target_tokens: 500
  overlap: 0.12

retrieval:
  topk_retrieve: 30
  topk_final: 8
  rerank: rrf                         # none | rrf | weighted | cross

generation:
  model_id: <your-gen-model>          # placeholder
  max_tokens: 600
  temperature: 0.2
  require_citations: true
```

---

## RAG API

* `POST /ingest` – ingest new files from COS → chunks → embeddings → upsert
* `POST /query` – returns concise answer + citations (source URI/page/section)

---

## Text2SQL

* **semantic\_layer.yaml**: brief table/column descriptions + 3–5 example Q→SQL pairs.
* Notebook flow:

  1. Select a table from `demo_schema`
  2. Generate SQL (show SQL first)
  3. Confirm to run (read-only; `LIMIT 200`; `TIMEOUT 15s`)
  4. Show results + execution plan (optional)

---

## Best Practices

### Zero-Copy Lakehouse

* Use **Iceberg external tables** on COS; avoid duplicating data.
* Keep sample data **small**; partition by date or bucket high-cardinality columns.
* Run compaction occasionally; prefer engines with predicate/column pushdown.

### Vector Search

* Default to **hybrid retrieval** (BM25 + dense).
* Chunk at **400–600 tokens** with **10–15% overlap**; preserve table/image references in metadata.
* Store clear metadata: `doc_id, source_uri, page, section, ts`.

### Q\&A (RAG)

* Retrieval: `topk=30` → rerank (RRF) → final `k=8`.
* Cache answers for repeated queries; dedupe embeddings on content hash.

### Text2SQL

* Read-only by default; enforce row limit & timeout.
* Show SQL before execution; require click-to-confirm.
* Keep a tiny **semantic layer** (table/column descriptions, examples).

### Data Security & Encryption 

* **Encrypt at rest:** COS server-side encryption with IBM Key Protect/HPCS (BYOK); rotate keys regularly.
* **Encrypt in transit:** Enforce TLS for watsonx.data and COS (`ssl=true` in connection strings).
* **Least-privilege access:** Roles/grants at catalog/schema/table; demo reader role = SELECT only.
* **Fine-grained protection:** Column masking and row-level filters defined in watsonx.data.
* **Secrets & audit (minimal):** Use Service IDs + API keys from `.env` (not in git); enable watsonx.data query logs and COS access logs.

---

## Operations

* **Seeding:** `seed_data.sh` creates external tables, uploads samples to COS, builds a small index.
* **Running:** `start_local.sh` exports env, launches RAG API (Uvicorn), and opens the Text2SQL notebook.
* **Cleanup:** `cleanup.sh` drops demo tables/collections and removes temp objects.

---

## Troubleshooting

* **401 Unauthorized:** missing/incorrect `REST_API_KEY`.
* **Vector connect error:** check `VECTOR_BACKEND` and Milvus/ES host/port.
* **No results:** verify `ingest_job.py` ran and collection/index exist.
* **Slow queries:** reduce `topk_retrieve`, enable rerank `rrf`, or compact index.
* **COS auth:** confirm `IBM_CLOUD_API_KEY` and bucket/endpoint values.
* **Model errors:** verify `WATSONX_*` and chosen model IDs are available to your project.

---

## Next Steps (other building blocks)

* **Automation:** add Terraform/Helm, CI/CD, scheduled index builds.
* **Trusted AI:** add guardrails, golden-set evaluation, audit/reporting.

