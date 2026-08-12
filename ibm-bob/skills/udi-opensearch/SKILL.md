---
name: udi-opensearch
description: Use when the user wants to create a UDI flow, ingest documents into OpenSearch, set up a UDI data ingestion pipeline, run UDI document processing, configure UDI embeddings, or manage the UDI (Unstructured Data Integration) lifecycle on IBM Cloud watsonx — including registering COS and OpenSearch connections and running the pipeline.
---

# UDI Skill — Document Ingestion into OpenSearch

This skill scaffolds a **pure-Python** two-part UDI pipeline:

- **Part 1 — `setup.py`** — run once: registers COS + OpenSearch connections, creates the UDI flow, saves all IDs to `udi_config.json`
- **Part 2 — `ingest.py`** — run every time: reads `udi_config.json` and starts a new flow run

No Terraform required — infrastructure (COS, WML, OpenSearch) is a user prerequisite.

## Skill directory layout

```
.bob/skills/udi-opensearch/
├── SKILL.md
├── .gitignore           → .gitignore
└── scripts/
    ├── .env.example     → scripts/.env.example     (copy to scripts/.env)
    ├── setup.sh         → scripts/setup.sh         (Part 1 — run once)
    ├── ingest.sh        → scripts/ingest.sh        (Part 2 — run repeatedly)
    ├── setup.py         → scripts/setup.py         (called by setup.sh)
    ├── ingest.py        → scripts/ingest.py        (called by ingest.sh)
    └── requirements.txt → scripts/requirements.txt
```

---

## Pipeline overview

```
COS bucket → extract text (OCR) → chunk → watsonx embeddings → OpenSearch index
```

| # | UDI Operator | Role |
|---|---|---|
| 1 | `ingest_cpd_connections` | Reads documents from COS via a registered watsonx connection |
| 2 | `extract_cpd` | Extracts text with OCR (high quality mode) |
| 3 | `chunker` | Splits text into overlapping chunks |
| 4 | `embeddings` | Generates vector embeddings (`ibm/slate-30m-english-rtrvr-v2`) |
| 5 | `opensearch` | Indexes chunks + vectors into an OpenSearch index |

---

## Step 0a — Detect the host OS

**Before issuing any shell commands**, detect the OS:

```python
python -c "import platform; print(platform.system())"
```

| OS result | Shell | Python binary | Set env var |
|---|---|---|---|
| `Linux` or `Darwin` | bash | `python3` | `export KEY="val"` |
| `Windows` | cmd / PowerShell | `python` | `set KEY=val` (cmd) or `$env:KEY="val"` (PS) |

---

## Step 0b — Prerequisites checklist

Before proceeding, confirm the user has all of the following.
Present as a checklist using `ask_followup_question` if anything is unclear.

### ✅ Handled automatically by the Python scripts

| What | How |
|---|---|
| IAM bearer token | `setup.py` fetches it from `iam.cloud.ibm.com` |
| COS connection registered in watsonx | `setup.py` calls Watson Data API |
| OpenSearch connection registered in watsonx | `setup.py` calls Watson Data API |
| UDI flow created | `setup.py` uses the `ibm-udi` SDK |
| UDI flow run triggered | `ingest.py` uses the `ibm-udi` SDK |

### ❌ Must be pre-provisioned by the user

| Prerequisite | Where to get it |
|---|---|
| IBM Cloud account with active subscription | [cloud.ibm.com](https://cloud.ibm.com) |
| IBM Cloud API key | IBM Cloud → Manage → Access (IAM) → API keys |
| watsonx.ai project | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → New project |
| Watson Machine Learning instance | IBM Cloud catalogue → Watson Machine Learning → link to project |
| COS instance + bucket | IBM Cloud catalogue → Cloud Object Storage |
| COS HMAC credentials | COS instance → Service credentials → create with HMAC enabled → `cos_hmac_keys` |
| OpenSearch instance | IBM Cloud catalogue → watsonx.data (Lakehouse), or self-managed |
| OpenSearch credentials | From your OpenSearch provider |
| Python ≥ 3.12 | [python.org](https://python.org) |

> **IBM Lakehouse OpenSearch credentials:**
> - Username: `ibmlhapikey_<your-ibm-cloud-email>`
> - Password: your IBM Cloud API key
> - Host: from Lakehouse instance details

> **COS authentication — HMAC is required:**
> The Watson Data API `cloudobjectstorage` connection supports both HMAC and IAM
> (`api_key` + `resource_instance_id`) modes at registration time. However, IAM
> mode is known to fail at UDI flow runtime with error `CDICO2034E`. **Always use
> HMAC credentials** (`COS_ACCESS_KEY` + `COS_SECRET_KEY`).
>
> To get HMAC keys: COS instance → Service credentials → Create credential →
> enable the **HMAC** toggle → copy `cos_hmac_keys.access_key_id` and
> `cos_hmac_keys.secret_access_key`.
>
> If only a CRN/API key is available and no HMAC credential exists, create one
> in the IBM Cloud console first.

If any prerequisite is missing, stop and guide the user to set it up first.

---

## Step 1 — Identify the Workflow

Ask the user which task they want using `ask_followup_question`:

- **First time setup** → Go to Step 2a (Part 1)
- **Run ingestion** (setup already done) → Go to Step 2b (Part 2)
- **Understand what the pipeline does** → Explain pipeline overview above

---

## Step 2a — Setup (Part 1 — run once)

### 2a-1 · Scaffold project files

Use `read_file` to read each file from the skill directory, then `write_file`
to place it in the user's project. Do all files in one batch:

| Source (skill) | Destination (user project) |
|---|---|
| `.gitignore` | `.gitignore` |
| `scripts/.env.example` | `scripts/.env.example` |
| `scripts/setup.sh` | `scripts/setup.sh` |
| `scripts/ingest.sh` | `scripts/ingest.sh` |
| `scripts/setup.py` | `scripts/setup.py` |
| `scripts/ingest.py` | `scripts/ingest.py` |
| `scripts/requirements.txt` | `scripts/requirements.txt` |

### 2a-2 · Install Python dependencies

```bash
pip install -r scripts/requirements.txt
```

### 2a-3 · Configure `.env`

```bash
cp scripts/.env.example scripts/.env
# fill in values — see table below
```

| Variable | What it is | Where to find it |
|---|---|---|
| `IBM_CLOUD_API_KEY` | IBM Cloud API key | IBM Cloud → Manage → Access (IAM) → API keys |
| `PROJECT_ID` | watsonx.ai project ID | watsonx console → project → Manage → General → Project ID |
| `COS_BUCKET` | COS bucket name | COS instance → Buckets |
| `COS_ENDPOINT` | COS S3 endpoint URL | e.g. `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
| `COS_ACCESS_KEY` | HMAC access key | COS → Service credentials (HMAC) → `cos_hmac_keys.access_key_id` |
| `COS_SECRET_KEY` | HMAC secret key | COS → Service credentials (HMAC) → `cos_hmac_keys.secret_access_key` |
| `OPENSEARCH_HOST` | OpenSearch hostname | From your OpenSearch / Lakehouse instance |
| `OPENSEARCH_PORT` | OpenSearch port | Default: `9200` |
| `OPENSEARCH_USERNAME` | OpenSearch username | IBM Lakehouse: `ibmlhapikey_<email>` |
| `OPENSEARCH_PASSWORD` | OpenSearch password | IBM Lakehouse: IBM Cloud API key |

### 2a-4 · Run setup

```bash
bash scripts/setup.sh
```

The script validates `.env`, checks Python, auto-installs dependencies if needed,
then calls `setup.py` which:
1. Gets an IAM bearer token
2. Registers the OpenSearch connection in watsonx
3. Registers the COS connection in watsonx (HMAC auth)
4. Creates the UDI flow + job
5. Writes `scripts/udi_config.json` with all IDs

### 2a-5 · Verify

Check that `scripts/udi_config.json` was created and contains `flow_id` and `job_id`.

---

## Step 2b — Ingest (Part 2 — run every time)

Setup must be complete (`scripts/udi_config.json` must exist). The `.env` file is
still required (for `IBM_CLOUD_API_KEY`).

```bash
bash scripts/ingest.sh
```

The script validates `.env`, checks `udi_config.json` exists, then calls `ingest.py`
which initialises the UDI client, starts a new run of the existing flow, and
appends the `run_id` to `udi_config.json`.

### Verify

Track progress in the watsonx console:
```
https://dataplatform.cloud.ibm.com/projects/<PROJECT_ID>/assets
```

---

## Optional configuration (setup.py)

| Variable | Default | Description |
|---|---|---|
| `WATSONX_URL` | `https://api.dataplatform.cloud.ibm.com` | Watson Data API base URL |
| `WATSONX_ENV` | `cloud-prod` | UDI environment: `cloud-prod` \| `cloud-dev` \| `cloud-test` \| `cpd` |
| `COLLECTION_NAME` | `udi_documents` | Folder path (prefix) inside the COS bucket |
| `INDEX_NAME` | `udi_opensearch_index` | OpenSearch index to write to |
| `CHUNK_SIZE` | `4000` | Token chunk size (1–10000) |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks (must be < `CHUNK_SIZE`) |
| `EMBEDDINGS_MODEL_ID` | `ibm/slate-30m-english-rtrvr-v2` | watsonx embedding model |
| `FLOW_NAME` | `udi_opensearch_flow` | Base name — a timestamp is appended on each setup run to ensure uniqueness |

---

## Key technical facts (discovered through live API testing)

- **COS auth — HMAC is mandatory:** HMAC (`COS_ACCESS_KEY` + `COS_SECRET_KEY`) is the only mode confirmed to work end-to-end at UDI runtime. IAM (`api_key` + `resource_instance_id`) registers successfully but fails at flow execution with `CDICO2034E`. Always use HMAC.
- **COS instance CRN:** Must end in `::` (service instance CRN). Bucket-level CRNs (ending in `:bucket:<name>`) are auto-stripped by `setup.py`.
- **`paths` format is critical:** The `ingest_cpd_connections` node requires `paths: ["/<bucket>/<collection>"]` — a bucket-prefixed absolute path. Using `[collection]`, `["/collection"]`, or `[]` causes UDI to scan nothing at runtime. `setup.py` builds this correctly automatically.
- **Watson Data API test endpoint:** No connection test endpoint exists for `cloudobjectstorage` — registration success (HTTP 201) is the only confirmation available before running the flow.
- **WML instance must be active:** The `extract_cpd` step uses Watson Machine Learning for OCR. If the WML instance linked to the watsonx.ai project is inactive (paused/suspended), the flow will fail with `invalid_instance_status_error`. Ensure the WML instance is active in IBM Cloud before running.
- **`WATSONX_URL`:** Must be `https://api.dataplatform.cloud.ibm.com` — this is where `/udp/v1/` is routed.
- **User-Agent header:** All Watson Data API requests must include `User-Agent: ibm-udi-client/1.0` — Cloudflare WAF blocks Python's default UA.
- **Flow name uniqueness:** UDI rejects duplicate flow names — `setup.py` appends a timestamp (`YYYYMMDD_HHMMSS`) to avoid conflicts on re-run. `ingest.py` reads the actual `flow_id` from `udi_config.json`, so re-runs always target the correct flow.
- **`udi_config.json` location:** Written to `scripts/udi_config.json` (same directory as the scripts). Set `UDI_CONFIG` env var to override.
- **`boto3` dependency:** `setup.py` uses `boto3` to enumerate COS files and build the correct `paths` list. It is included in `requirements.txt` — install with `pip install -r scripts/requirements.txt`.
- **`pydantic` dependency:** `ibm-udi` uses `pydantic` internally but does not declare it — included in `requirements.txt`.
- **Windows encoding:** Log stream handlers use `encoding='utf-8'` explicitly to prevent `UnicodeEncodeError` from checkmark characters on Windows cp1252 terminals.

---

## References

- [IBM watsonx.ai Documentation](https://cloud.ibm.com/docs/watsonx)
- [IBM UDI SDK](https://pypi.org/project/ibm-udi/)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM watsonx.data (Lakehouse)](https://cloud.ibm.com/docs/watsonxdata)
