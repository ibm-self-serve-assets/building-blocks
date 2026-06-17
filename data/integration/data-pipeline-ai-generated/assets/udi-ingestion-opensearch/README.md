# UDI Document Ingestion — OpenSearch

A two-part Python pipeline that ingests documents from **IBM Cloud Object Storage (COS)** into an **OpenSearch index** using IBM watsonx UDI (Unstructured Data Integration).

```
 Your documents                              OpenSearch
 ─────────────                               ──────────
 COS bucket/                                 index: udi_opensearch_index
 └── udi_documents/          ──────────►    { text, vector_index,
     ├── report.pdf           UDI flow         document_name, pk, ... }
     ├── manual.docx          (watsonx)
     └── slides.pptx
```

---

## What you need to provide

### Infrastructure prerequisites (provision before running)

| Resource | Purpose | Where to create |
|---|---|---|
| **IBM Cloud account** | Required for all services | [cloud.ibm.com](https://cloud.ibm.com) |
| **IBM Cloud API key** | Authenticates all API calls | IBM Cloud → Manage → Access (IAM) → API keys |
| **watsonx.ai project** | Houses the UDI flow and connections | [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com) → New project |
| **Watson Machine Learning (WML) instance** | Powers the OCR extraction step | IBM Cloud catalogue → Watson Machine Learning → link to your project |
| **Cloud Object Storage instance + bucket** | Holds source documents | IBM Cloud catalogue → Cloud Object Storage |
| **COS HMAC credentials** | Lets UDI read from COS at runtime | COS instance → Service credentials → Create → enable **HMAC** toggle |
| **OpenSearch instance** | Receives indexed chunks + vectors | IBM Cloud catalogue → watsonx.data (Lakehouse), or self-managed |

> ⚠️ **WML must be active.** The OCR extraction step requires an active WML instance linked to your watsonx.ai project. If the instance is paused or suspended, the flow will fail with `invalid_instance_status_error`. Check its status in the IBM Cloud dashboard before running.

### Credentials to collect

| Variable | What it is | Where to find it |
|---|---|---|
| `IBM_CLOUD_API_KEY` | IBM Cloud API key | IBM Cloud → Manage → Access (IAM) → API keys |
| `PROJECT_ID` | watsonx.ai project ID | watsonx console → project → Manage → General → Project ID |
| `COS_BUCKET` | COS bucket name | COS instance → Buckets |
| `COS_ENDPOINT` | COS S3 endpoint URL | e.g. `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
| `COS_REGION` | COS region (used if endpoint not set) | e.g. `us-south` |
| `COS_ACCESS_KEY` | HMAC access key ID | COS → Service credentials (HMAC) → `cos_hmac_keys.access_key_id` |
| `COS_SECRET_KEY` | HMAC secret access key | COS → Service credentials (HMAC) → `cos_hmac_keys.secret_access_key` |
| `OPENSEARCH_HOST` | OpenSearch hostname | From your OpenSearch / Lakehouse instance details |
| `OPENSEARCH_PORT` | OpenSearch port | Default: `9200` |
| `OPENSEARCH_USERNAME` | OpenSearch username | IBM Lakehouse: `ibmlhapikey_<your-ibm-cloud-email>` |
| `OPENSEARCH_PASSWORD` | OpenSearch password | IBM Lakehouse: your IBM Cloud API key |

> **How to get COS HMAC credentials:**
> 1. Go to your COS instance in the IBM Cloud console.
> 2. Click **Service credentials** → **New credential**.
> 3. Expand **Advanced options** and enable the **Include HMAC Credential** toggle.
> 4. Click **Add**.
> 5. Expand the new credential and copy:
>    - `cos_hmac_keys.access_key_id` → `COS_ACCESS_KEY`
>    - `cos_hmac_keys.secret_access_key` → `COS_SECRET_KEY`

> **IBM Lakehouse OpenSearch credentials:**
> - Username: `ibmlhapikey_<your-ibm-cloud-email>`
> - Password: your IBM Cloud API key (same as `IBM_CLOUD_API_KEY`)
> - Host: from the Lakehouse instance details page

---

## Where to put your documents

Upload documents into your COS bucket inside a folder whose name matches `COLLECTION_NAME` (default: `udi_documents`):

```
my-cos-bucket/          ← COS_BUCKET
└── udi_documents/      ← COLLECTION_NAME (folder inside the bucket)
    ├── report.pdf
    ├── manual.docx
    ├── slides.pptx
    ├── notes.txt
    └── ...
```

Upload files via the IBM Cloud console, the `ibmcloud cos` CLI, or any S3-compatible client (e.g. `aws s3 cp --endpoint-url <cos-endpoint>`).

**Supported file types:** `.pdf`, `.docx`, `.pptx`, `.doc`, `.ppt`, `.md`, `.txt`, `.xlsx`, `.html`

To use a different folder name, set `COLLECTION_NAME` in `scripts/.env` **before running setup**. The folder must already exist and contain at least one supported file, otherwise setup will abort.

---

## Where your data ends up

After ingestion, every document is split into chunks and indexed in OpenSearch under `INDEX_NAME` (default: `udi_opensearch_index`):

| OpenSearch field | Content |
|---|---|
| `text` | Extracted text chunk |
| `vector_index` | 384-dimensional embedding vector |
| `document_name` | Original filename |
| `document_id` | Unique document identifier |
| `pk` | Chunk hash (primary key) |

UDI creates the index automatically on the first run. Subsequent runs append new/updated chunks without recreating the index.

Set `INDEX_NAME` in `scripts/.env` before running setup if you want a custom index name.

---

## Quick start

### Step 1 — Configure credentials

```bash
cp scripts/.env.example scripts/.env
# Open scripts/.env and fill in all required values
```

Minimum required fields:

```dotenv
IBM_CLOUD_API_KEY=<your-ibm-cloud-api-key>
PROJECT_ID=<your-watsonx-project-id>

COS_BUCKET=<your-cos-bucket-name>
COS_ENDPOINT=https://s3.us-south.cloud-object-storage.appdomain.cloud
COS_ACCESS_KEY=<hmac-access-key-id>
COS_SECRET_KEY=<hmac-secret-access-key>

OPENSEARCH_HOST=<opensearch-hostname>
OPENSEARCH_PORT=9200
OPENSEARCH_USERNAME=<opensearch-username>
OPENSEARCH_PASSWORD=<opensearch-password>
```

### Step 2 — Install Python dependencies

```bash
pip install -r scripts/requirements.txt
```

Requires Python ≥ 3.12.

### Step 3 — Part 1: Setup (run once)

```bash
bash scripts/setup.sh
```

On Windows:
```cmd
python scripts\setup.py
```

What setup does:
1. Fetches an IAM bearer token from IBM Cloud
2. Registers your OpenSearch instance as a named connection in watsonx.ai
3. Registers your COS bucket as a named connection in watsonx.ai (HMAC auth)
4. Enumerates all supported files under `COLLECTION_NAME` in COS
5. Creates the UDI flow with all pipeline stages configured
6. Saves all generated IDs to `scripts/udi_config.json`

Expected output:
```
✓ IAM token obtained
✓ OpenSearch connection registered: <connection-id>
✓ COS connection registered: <connection-id>
✓ Found 42 files to ingest
✓ Flow created — flow_id: <id> | job_id: <id>
✓ Setup complete
  Config saved to: scripts/udi_config.json
```

Verify that `scripts/udi_config.json` was created and contains `flow_id` and `job_id` before proceeding.

### Step 4 — Part 2: Ingest (run every time)

```bash
bash scripts/ingest.sh
```

On Windows:
```cmd
python scripts\ingest.py
```

What ingest does:
1. Reads `scripts/udi_config.json` (written by setup)
2. Starts a new run of the existing UDI flow
3. Polls status every 20 seconds (configurable via `POLL_INTERVAL`)
4. Prints execution logs on any non-`Completed` terminal state
5. Records the run result back into `udi_config.json`

Expected output:
```
✓ UDI client initialized
✓ Flow run started — run_id: <id>
[3/3] Polling run status (interval=20s, timeout=1800s)...
✓ Ingestion run COMPLETED successfully
```

Run this step whenever new documents are added to the COS folder, on a schedule, or on demand.

---

## Optional settings

Set these in `scripts/.env` before running setup:

| Variable | Default | Description |
|---|---|---|
| `COLLECTION_NAME` | `udi_documents` | Folder inside the COS bucket containing source documents |
| `INDEX_NAME` | `udi_opensearch_index` | OpenSearch index to create and write to |
| `CHUNK_SIZE` | `4000` | Max tokens per chunk (1–10000) |
| `CHUNK_OVERLAP` | `200` | Overlap tokens between adjacent chunks (must be < `CHUNK_SIZE`) |
| `EMBEDDINGS_MODEL_ID` | `ibm/slate-30m-english-rtrvr-v2` | watsonx embedding model ID |
| `FLOW_NAME` | `udi_opensearch_flow` | Base name — a timestamp is appended on each setup run to ensure uniqueness |
| `WATSONX_URL` | `https://api.dataplatform.cloud.ibm.com` | Watson Data API base URL |
| `WATSONX_ENV` | `cloud-prod` | UDI environment: `cloud-prod` \| `cloud-dev` \| `cloud-test` \| `cpd` |
| `POLL_INTERVAL` | `20` | Seconds between status polls during ingestion |
| `POLL_TIMEOUT` | `1800` | Max seconds to wait before timing out |

---

## Files generated at runtime

These files are created when the scripts run. They are covered by `.gitignore` and must not be committed.

| File | Location | Contents |
|---|---|---|
| `udi_config.json` | `scripts/udi_config.json` | Connection IDs, flow ID, job ID, run history |
| `udi_setup.log` | `scripts/udi_setup.log` | Full log from the last `setup.py` run |
| `udi_ingest.log` | `scripts/udi_ingest.log` | Full log from the last `ingest.py` run |

---

## Troubleshooting

### `invalid_instance_status_error` during extraction

The Watson Machine Learning instance linked to your watsonx.ai project is inactive. Go to IBM Cloud → Resource list → Watson Machine Learning → activate the instance, then re-run `ingest.py`.

### `CDICO2034E` at flow runtime

You are using IAM credentials (`COS_API_KEY` + `COS_INSTANCE_CRN`) for COS. IAM mode registers the connection successfully but fails at UDI runtime. Switch to HMAC credentials (`COS_ACCESS_KEY` + `COS_SECRET_KEY`).

### `No supported files found`

- `COS_BUCKET` must match the exact bucket name (case-sensitive).
- `COLLECTION_NAME` must match the exact folder name inside the bucket.
- At least one supported file must exist in that folder before running setup.

### Setup succeeds but ingestion processes 0 documents

The `paths` value in the UDI flow must be `/<bucket>/<collection>` (bucket-prefixed absolute path). `setup.py` builds this automatically from `COS_BUCKET` and `COLLECTION_NAME`. Do not edit `setup.py`'s `paths` parameter manually.

### `HTTP 403` when registering connections

Cloudflare WAF blocks Python's default User-Agent. All Watson Data API requests in `setup.py` include `User-Agent: ibm-udi-client/1.0` — do not remove this header.

### `Required environment variable not set`

Copy `scripts/.env.example` to `scripts/.env` and fill in every required field. No required variable can be left blank.

### `ibm-udi package not installed`

```bash
pip install -r scripts/requirements.txt
```

---

## Pipeline stages

```
┌────────────────────────────────────────────────────────────────┐
│                          UDI Flow                              │
│                                                                │
│  ┌──────────────────────────┐                                  │
│  │  ingest_cpd_connections  │  reads files from COS           │
│  │  (COS connection)        │  paths: [/<bucket>/<folder>]    │
│  └────────────┬─────────────┘                                  │
│               ↓                                                │
│  ┌──────────────────────────┐                                  │
│  │       extract_cpd        │  OCR + text extraction          │
│  │  (WML, high_quality)     │  requires active WML instance   │
│  └────────────┬─────────────┘                                  │
│               ↓                                                │
│  ┌──────────────────────────┐                                  │
│  │         chunker          │  splits text into chunks        │
│  │   chunk_size=4000        │  overlap=200 tokens             │
│  └────────────┬─────────────┘                                  │
│               ↓                                                │
│  ┌──────────────────────────┐                                  │
│  │        embeddings        │  384-dim vectors                │
│  │  ibm/slate-30m-english-* │                                  │
│  └────────────┬─────────────┘                                  │
│               ↓                                                │
│  ┌──────────────────────────┐                                  │
│  │        opensearch        │  writes to OpenSearch index     │
│  │  (OpenSearch connection) │  engine: lucene                 │
│  └──────────────────────────┘                                  │
└────────────────────────────────────────────────────────────────┘
```

---

## References

- [IBM watsonx.ai Documentation](https://cloud.ibm.com/docs/watsonx)
- [IBM UDI SDK on PyPI](https://pypi.org/project/ibm-udi/)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM watsonx.data (Lakehouse)](https://cloud.ibm.com/docs/watsonxdata)
- [Watson Machine Learning](https://cloud.ibm.com/catalog/services/watson-machine-learning)
