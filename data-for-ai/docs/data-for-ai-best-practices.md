# Data for AI Building Block — Best Practices

*(Zero-Copy Lakehouse · Vector Search · Q\&A · Data Security & Encryption)*

---

## 1) Clarity & Simplicity

* **Start with four crisp outcomes**:

  1. *Zero-Copy Lakehouse*: query where data lives; no ETL bloat.
  2. *Vector Search*: fast semantic lookup over governed content.
  3. *Q\&A (RAG)*: grounded answers with citations over enterprise docs.
  4. *Data Security & Encryption*: least-privilege, encrypted-by-default.
* **Offer safe, realistic sample datasets** (10–100 MB) on IBM COS with schemas that demonstrate text, tables, and images.
* **One-command demo path** (e.g., `./scripts/deploy.sh`) that spins up: sample Iceberg tables in watsonx.data, a small Milvus/Elastic collection, the RAG API service, and a Text2SQL demo notebook/UI.
* **Opinionated defaults** surface the value immediately: Docling chunker, dense+BM25 hybrid retrieval, rerank on top-k=50→RRF→k=8, and a compact watsonx.ai model preset.

---

## 2) Reusability & Modularity

Break the block into swappable modules:

* **Ingestion & Metadata**: loaders (PDF/HTML/Markdown/JSON), Docling processing, schema registry, lineage capture.
* **Lakehouse**: Iceberg external tables on COS, partitioning/compaction, schema evolution.
* **Vectorization**: embedding jobs (dense | sparse), Milvus/Elastic index builders, hybrid retrievers.
* **Generation**: prompt templates, model adapters for watsonx.ai, response post-processors (citation injector, redactor).
* **Security**: secrets, KMS/HPCS, RBAC/ABAC, row/column masking.
* **Extensibility**: flags to switch vector DB (Milvus↔Elastic), swap embedding models, enable rerankers (RRF, weighted, cross-encoder), add memory layers.

---

## 3) Parameterization

Expose settings in `values.yaml`, `variables.tf`, or `.env`:

* **watsonx.data**: `CATALOG`, `SCHEMA`, `ICEBERG_WAREHOUSE`, `CONNECTION_NAME`.
* **Vector DB (Milvus)**: `WXD_MILVUS_HOST`, `WXD_MILVUS_PORT`, `WXD_MILVUS_USER`, `WXD_MILVUS_PASSWORD`, `INDEX_TYPE` (HNSW/IVF\_PQ), `METRIC` (cosine/L2), `EF`, `M`.
* **Elasticsearch (optional)**: `ES_HOSTS`, `ES_USERNAME`, `ES_PASSWORD`, `ES_INDEX`, `BM25_TUNING`.
* **Embeddings**: `EMBED_MODEL_ID`, `DIM`, `HYBRID_SPARSE` (true/false), `BATCH_SIZE`.
* **RAG Retrieval**: `TOPK_RETRIEVE`, `TOPK_RERANK`, `RERANK_STRATEGY` (RRF/weighted/cross).
* **LLM**: `WATSONX_MODEL_ID`, `WATSONX_PROJECT_ID`, `WATSONX_URL`, `WATSONX_APIKEY`, `MAX_TOKENS`, `TEMP`.
* **Text2SQL**: `SQL_ENDPOINT` (watsonx.data), `DEFAULT_DATABASE`, `DIALECT`, `QUERY_TIMEOUT_MS`, `ROW_LIMIT`.
* **Security**: `REST_API_KEY`, `KMS_INSTANCE`, `KEY_CRN`, `TLS_ENFORCED=true`.

Provide **sensible defaults** that succeed out-of-the-box on a laptop/TechZone VM.


---

## 4) Documentation

Include in `README.md`:

* **Concepts primer**: Zero-copy lakehouse (Iceberg on COS), vector search, hybrid retrieval, RAG, Text2SQL, Data Security & Encryption.
* **Prereqs**: watsonx.data, watsonx.ai, IBM COS, Milvus/Elastic, Python3, optional Kubernetes/OpenShift.
* **Step-by-step**: *deploy → ingest/index → run RAG & Text2SQL → evaluate → secure → demo*.
* **Screenshots**: RAG Swagger, retrieval dashboard, Text2SQL UI.
* **Architecture diagram**: end-to-end with modules and data flows.
* **Troubleshooting**: index build stalls, TLS errors, auth scopes, OOM during embedding.

---

## 5) Safety, Privacy & Cost Control

* Keep **sample datasets small**; gate large embedding jobs behind a `--confirm-large` flag.
* **Read-only** SQL execution by default in Text2SQL with `ROW_LIMIT` and `TIMEOUT`.
* One-command teardown: `terraform destroy`, `./scripts/cleanup.sh`.

---

## 6) Provider & Authentication

* Use **IBM Cloud API Keys / Service IDs** with least-privilege; scope watsonx.data catalogs and buckets.
* Store secrets in **Vault/Kubernetes Secrets**; never commit `.env`. Provide `.env.template`.
* Enforce **TLS in transit**, **KMS/HPCS** for at-rest encryption (COS, block storage, Milvus disks).
* Network-level controls: private endpoints/VPC peering, IP allowlists for API services.

---

## 7) Showcasing Best Practices

* **Continuous optimization**: re-embed changed pages only; rolling index builds; drift detection re-triggers.
* **Hybrid retrieval as default**: BM25 + dense; show the lift from reranking.

---

## 8) Sample Folder Structure

```
data-for-ai-building-block/
├── README.md
├── terraform/
│   ├── main.tf                 # COS buckets, Milvus/ES, watsonx.data catalogs
│   ├── variables.tf
│   ├── outputs.tf
│   └── provider.tf
├── lakehouse/
│   ├── create_iceberg.sql      # External tables on COS
│   ├── schema/                 # Table schemas & evolution scripts
│   └── samples/                # Small seed datasets
├── ingestion/
│   ├── loaders/                # PDF/HTML/MD/JSON loaders (Docling etc.)
│   ├── chunkers/               # Docling/Markdown/Recursive splitters
│   └── ingest_job.py
├── vector-store/
│   ├── milvus/                 # Index params, create/compact scripts
│   └── elastic/                # Index templates & analyzers
├── rag-accelerator/
│   ├── app/                    # FastAPI service (RAG Service API)
│   ├── routers/                # /ingest-files, /query, /health
│   ├── prompts/
│   ├── rerankers/
│   ├── evaluation/             # golden sets, JudgeIt harness
│   └── .env.template
├── text2sql-accelerator/
│   ├── notebooks/              # Demo UI & evaluation
│   ├── semantic-layer/         # Table/column descriptions, examples
│   ├── guards/                 # AST checks, read-only enforcement
│   └── config.yaml
├── scripts/
│   ├── deploy.sh
│   ├── simulate_load.sh
│   └── cleanup.sh
└── docs/
    ├── architecture-diagram.png
    ├── data-for-ai-best-practices.md
    └── troubleshooting.md
```

---

## 9) Pattern-Specific Guidance

### A) Zero-Copy Lakehouse (watsonx.data + Iceberg on COS)

* **External tables on COS**; avoid copying—query in place.
* **Schema evolution** via Iceberg; keep evolution scripts versioned.
* **Partitioning**: use transforms (e.g., `day`, `bucket(n)` on high-card columns).
* **Compaction & file sizing**: schedule compaction; target 128–512 MB files for scan efficiency.
* **Caching & pushdown**: prefer engines that push filters/columns; minimize wide scans.
* **Lineage**: capture object URIs and snapshots; store lineage IDs alongside vector docs for citations.
* **Data contracts**: validate schema before publish; fail fast on breaking changes.

### B) Vector Search (Milvus or Elasticsearch)

* **Index choice**: start with dense index.
* **Hybrid retrieval**: combine BM25 + dense; normalize scores; tune `alpha`/RRF weights with a dev set.
* **Chunking**: 300–800 tokens; overlap 10–15%;
* **Metadata**: store `doc_id`, `source_uri`, `table_id`, `section`, `page`, `timestamp`.
* **Cold rebuild vs rolling updates**: use upsert with version fields; nightly compaction.

### C) Q\&A (RAG)

* **Prompting**: system prompt that mandates citations and refusal on missing evidence.
* **Reranking**: RRF or cross-encoder after `topk_retrieve=50`, keep final `k=6–10`.

### D) Data Security & Encryption

* **Encryption**: COS + block storage with KMS/HPCS keys; rotate keys; envelope encryption for vector payloads.
* **Access control**: watsonx.data RBAC/ABAC; column/row masking; policy as code.
* **Secrets**: store in Vault/Secrets Manager; rotate; short TTL tokens.
* **Network**: private endpoints, VPC peering, TLS everywhere, WAF for public APIs.

---

## 10) RAG Accelerator (Milvus RAG Service API) — Implementation Notes

* **APIs**: `POST /ingest-files`, `POST /query`, `GET /health`; protected by `REST_API_KEY`.
* **Config**: use `.env.template` for Milvus, watsonx.ai, COS; never commit `.env`.
* **Ingestion**: support Docling, Markdown, recursive text splitters; store ingestion stats in `/reports`.
* **Retrieval & Rerank**: enable hybrid, tune RRF/weights, expose `topk` params.
* **Swagger**: ship FastAPI docs at `/docs`; add curl + Python examples in README.
* **“Coming soon”** hooks: VLM image annotation, prompt guardrails, LLM-as-Judge evaluation, memory layers, structured error logging.

---

## 11) Text2SQL Accelerator — Best Practices

* **Semantic layer**: curated table/column descriptions, PK/FK graphs, sample queries by intent.
* **Dialect control**: set dialect (DB2/PostgreSQL/Trino) and enforce it in the prompt.
* **Pre-execution checks**: AST/static analysis for DDL/DML bans; **read-only** by default.
* **Safety rails**: limit `ROW_LIMIT`, add `TIMEOUT`, block cross-db joins unless whitelisted.
* **Execution sandbox**: route to watsonx.data/federated endpoint; show **explain plan** option.
* **Eval**: exact string match is brittle; include semantic equivalence (result-set compare) and execution success rate.
* **UX**: show generated SQL, **require user confirmation before execution**, display result preview with lineage.

---

## 12) Quick-Start (demo runbook)

1. `./scripts/deploy.sh` — provision COS buckets, watsonx.data catalog/schema, Milvus/ES, and RAG API.
2. `python ingestion/ingest_job.py --bucket demo-bucket --collection demo_docs --chunker DOCLING_DOCS`
3. Hit RAG Swagger `/docs` → `POST /query` with a sample question → verify citations to Iceberg URIs.
4. Open Text2SQL notebook → pick table → generate SQL → confirm → preview results.
5. Open dashboards → check retrieval metrics & latency; export `/reports/*`.
6. `./scripts/cleanup.sh` when done.

