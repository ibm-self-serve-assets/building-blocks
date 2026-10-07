# Deploying to IBM Cloud Code Engine

This guide walks through building both service images, pushing them to IBM Cloud Container Registry (ICR), and deploying them as Code Engine applications — from zero to running in production.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  IBM Cloud Code Engine project                               │
│                                                              │
│  ┌──────────────────────┐    ┌──────────────────────────┐   │
│  │   schema-retriever   │    │     sql-executor          │   │
│  │   (port 8080)        │    │     (port 8000)           │   │
│  │                      │    │                           │   │
│  │  POST /retrieve-     │    │  POST /run-sql            │   │
│  │       schema         │    │  GET  /health             │   │
│  │  POST /retrieve-     │    └──────────┬────────────────┘   │
│  │       schema/hybrid  │               │                    │
│  │  GET  /health        │               ▼                    │
│  └──────────┬───────────┘       Target PostgreSQL DB         │
│             │                                                │
│             ▼                                                │
│      IBM OpenSearch                                          │
│      (schema_embeddings index)                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

| Tool | Install |
|---|---|
| `ibmcloud` CLI | https://cloud.ibm.com/docs/cli |
| container-registry plugin | `ibmcloud plugin install container-registry` |
| code-engine plugin | `ibmcloud plugin install code-engine` |
| Docker (or Podman) | https://docs.docker.com/get-docker/ |
| Git | for automatic image tagging |

### IBM Cloud services required

| Service | Purpose |
|---|---|
| **IBM Cloud Container Registry** (ICR) | Stores the two Docker images |
| **IBM Code Engine** (project) | Runs both services as serverless apps |
| **IBM OpenSearch** (or self-hosted) | Stores schema embeddings |
| **IBM watsonx.ai** (optional) | Embedding provider (or use sentence-transformers locally) |
| **PostgreSQL** | The source database the LLM queries |

---

## Step 1 — Login and setup

```bash
ibmcloud login --sso                        # or: --apikey <YOUR_API_KEY>
ibmcloud target -r eu-de                    # Frankfurt; use us-south for Dallas
ibmcloud cr region-set eu-central           # match your ICR region

# Create an ICR namespace (once only)
ibmcloud cr namespace-add your-namespace
```

---

## Step 2 — Prepare secrets (.env files)

Use the **single root `.env`** at `NL2SQL/.env` for all services (recommended), or create per-service `.env` files inside each service directory:

```bash
# Option A — single root file (recommended)
cp NL2SQL/.env.example NL2SQL/.env
nano NL2SQL/.env        # fill in OpenSearch, watsonx, and PostgreSQL credentials

# Option B — per-service files (for Code Engine secret isolation)
cp docker-build/backend/schema-retriever/.env.example docker-build/backend/schema-retriever/.env
cp docker-build/backend/sql-executor/.env.example     docker-build/backend/sql-executor/.env
```

> **Never commit `.env` files.** They are in `.gitignore`.

---

## Step 3 — Full deploy (build + push + deploy)

The `deploy.sh` script at the root of `docker-build/` does everything in one shot:

```bash
cd NL2SQL/docker-build

export ICR_NAMESPACE=your-namespace          # required
export CE_PROJECT=your-code-engine-project   # required
export ICR_REGION=de.icr.io                  # Frankfurt (default)
export CE_REGION=eu-de                        # Frankfurt (default)

chmod +x deploy.sh backend/schema-retriever/build.sh backend/sql-executor/build.sh
./deploy.sh
```

The script will:
1. Build both images with `--platform linux/amd64` (required for Code Engine)
2. Tag with the current git short-SHA and `:latest`
3. Push to ICR
4. Sync `.env` contents into Code Engine secrets
5. Create or update both Code Engine applications
6. Print the public URLs when done

---

## Step 4 — Build only (no deploy)

To build and push images without touching Code Engine (e.g. CI pipeline):

```bash
BUILD_ONLY=true ./deploy.sh
```

Or build a single service:

```bash
cd docker-build/backend/schema-retriever
ICR_NAMESPACE=your-namespace ./build.sh
```

---

## Step 5 — Manual Code Engine commands (reference)

If you prefer `ibmcloud ce` commands directly instead of the deploy script:

```bash
# Create secret from .env file
ibmcloud ce secret create \
  --name schema-retriever-secrets \
  --from-env-file docker-build/backend/schema-retriever/.env

# Create application
ibmcloud ce app create \
  --name schema-retriever \
  --image de.icr.io/your-namespace/schema-retriever-service:latest \
  --port 8080 \
  --cpu 2 \
  --memory 3G \
  --min-scale 1 \
  --max-scale 10 \
  --env-from-secret schema-retriever-secrets \
  --wait

# Update image after a new build
ibmcloud ce app update \
  --name schema-retriever \
  --image de.icr.io/your-namespace/schema-retriever-service:abc1234
```

---

## Step 6 — Verify

```bash
# Get URLs
ibmcloud ce app get --name schema-retriever
ibmcloud ce app get --name sql-executor

# Health check
curl https://<schema-retriever-url>/health
curl https://<sql-executor-url>/health

# Test retrieval
curl -X POST https://<schema-retriever-url>/retrieve-schema \
  -H "Content-Type: application/json" \
  -d '{"user_query": "find all customer orders", "top_k": 3}' | python -m json.tool
```

---

## Resource sizing reference

| Service | CPU | Memory | Notes |
|---|---|---|---|
| `schema-retriever` (watsonx embed) | 0.5–1 | 512 MB | No local model |
| `schema-retriever` (ST embed) | 1–2 | 2–3 GB | bge-base model ~1.5 GB RAM |
| `sql-executor` | 0.25–1 | 256–512 MB | Stateless; pool of 1–5 PG connections |

Code Engine **min-scale 1** keeps one warm instance; set to `0` to scale-to-zero (cold start ~5 s for watsonx, ~30 s for sentence-transformers).

---

## Updating secrets

```bash
# Re-sync all secrets and trigger a new revision
ibmcloud ce secret update \
  --name schema-retriever-secrets \
  --from-env-file docker-build/backend/schema-retriever/.env

# Force a new revision to pick up the secret changes
ibmcloud ce app update --name schema-retriever --wait
```

---

## Directory structure

```
docker-build/
├── deploy.sh                          ← full orchestrator (build + push + deploy)
├── README.md                          ← this file
│
└── backend/
    ├── schema-retriever/
    │   ├── Dockerfile                 ← multi-stage, non-root, HEALTHCHECK
    │   ├── .dockerignore
    │   ├── .env.example               ← copy to .env and fill in (or use root .env)
    │   ├── ce-app.yaml                ← Code Engine app spec (reference)
    │   └── build.sh                   ← build + push to ICR
    │
    └── sql-executor/
        ├── Dockerfile                 ← multi-stage, non-root, HEALTHCHECK
        ├── .dockerignore
        ├── .env.example
        ├── ce-app.yaml
        └── build.sh
```
