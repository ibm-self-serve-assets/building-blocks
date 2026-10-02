# Confluent Cloud Cluster Setup Specification

**Project:** FactoryPulse Streamhouse — Continuous RAG Demo
**Version:** 1.1
**Date:** 2025
**Scope:** Provision all Confluent Cloud resources required to run the FactoryPulse application end-to-end.

---

## 1. Overview

This specification defines the Confluent Cloud resources that must be provisioned before the FactoryPulse application can start.

**Two provisioning methods are provided:**

| Method | Location | Best for |
|---|---|---|
| **Terraform (recommended)** | `infra/confluent/terraform/` | Repeatable, version-controlled IaC deployments |
| **Python REST script** | `infra/confluent/provision_cluster.py` | Quick ad-hoc provisioning without Terraform |

Both methods are **idempotent** — re-running will skip resources that already exist.

The Terraform method follows the `data-streaming-confluent` skill conventions (Confluent provider ≥ 2.68.0, schema registry timing, RBAC delays, topic ownership rules).

---

## 2. Credentials Required

| Variable | Source | Description |
|---|---|---|
| `CONFLUENT_CLOUD_API_KEY` | Confluent Cloud → API Keys → Cloud resource management | Management-plane API key (not a Kafka data-plane key) |
| `CONFLUENT_CLOUD_API_SECRET` | Same as above | Corresponding secret |

> **Note:** The API key `UBHPSOUE22BCLNPJ` with Global resource scope is the Cloud management API key. It is used **only** for provisioning and is distinct from the Kafka data-plane API key that will be generated during provisioning.

---

## 3. Resources to Provision

### 3.1 Confluent Cloud Environment

| Property | Value |
|---|---|
| Name | `factorypulse-streamhouse` |
| Purpose | Namespace isolating all FactoryPulse resources |

### 3.2 Kafka Cluster

| Property | Value |
|---|---|
| Name | `factorypulse-cluster` |
| Type | `BASIC` (sufficient for demo; upgrade to `STANDARD` for Schema Registry + Tableflow) |
| Cloud Provider | `aws` |
| Region | `us-east-2` |
| Availability | Single zone |

> For production, use `STANDARD` or `DEDICATED` and multi-zone availability.

### 3.3 Kafka Data-Plane API Key

| Property | Value |
|---|---|
| Display name | `factorypulse-app-key` |
| Scope | Cluster-scoped (the `factorypulse-cluster` above) |
| Purpose | Used by the FastAPI app and topic provisioning scripts as `CONFLUENT_KAFKA_API_KEY` / `CONFLUENT_KAFKA_API_SECRET` |

### 3.4 Schema Registry (Optional — Flink Profile)

| Property | Value |
|---|---|
| Package | `ESSENTIALS` (bundled with the environment when cluster type ≥ `STANDARD`) |
| Purpose | Required for `SERIALIZATION_MODE=schema-registry-json` and managed Flink embedding pipeline |

> Schema Registry is provisioned automatically when the environment is created on `STANDARD` clusters. For `BASIC` clusters it is not available — `SERIALIZATION_MODE` must remain `plain-json`.

### 3.5 Kafka Topics

All topics are created with **3 partitions** and **replication factor −1** (broker-managed default).

| Topic | Cleanup Policy | Owner | Purpose |
|---|---|---|---|
| `factory.machine.telemetry` | delete | app / simulator | Raw machine/PLC sensor events |
| `factory.production.events` | delete | app / simulator | MES production progress events |
| `factory.quality.events` | delete | app / simulator | Inspection and defect events |
| `factory.maintenance.events` | delete | app / simulator | Maintenance operational events |
| `factory.state` | delete | app / simulator | Continuously derived current factory state |
| `factory.exceptions` | delete | app / simulator | Correlated business exception events |
| `rag.knowledge.raw` | delete | API / integrations | Raw enterprise knowledge documents |
| `rag.knowledge.embeddings` | **compact** | local indexer / Flink | Materialized knowledge chunks + vectors |
| `rag.query.requests` | delete | FastAPI | Interactive query embedding requests (Flink mode) |
| `rag.query.embeddings` | **compact** | Flink | Correlated query embedding results (Flink mode) |

---

## 4. Provisioning — Method A: Terraform (Recommended)

**Location:** `infra/confluent/terraform/`
**Tool:** Terraform ≥ 1.0, Confluent provider ≥ 2.68.0

### Usage

```bash
bash infra/confluent/scripts/setup.sh
```

Or step by step:
```bash
cd infra/confluent/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with credentials
terraform init && terraform apply
```

### What Terraform creates (in order)

1. **Organization** (data source)
2. **Environment** `factorypulse-streamhouse`
3. **Kafka Cluster** `factorypulse-cluster`
4. **Service Account** `factorypulse-app`
5. **Schema Registry wait** (60 s — prevents race condition)
6. **Schema Registry** (data source — auto-provisioned with cluster)
7. **Flink Compute Pool + Region** (STANDARD only)
8. **API Keys** — Kafka data-plane; Schema Registry; Flink (STANDARD)
9. **Role Bindings** — CloudClusterAdmin / FlinkDeveloper / EnvironmentAdmin
10. **RBAC wait** (30 s)
11. **All 10 Kafka topics** with correct cleanup policies
12. **`.env` file** written to repo root with resolved values

## 4b. Provisioning — Method B: Python REST Script

**Location:** `infra/confluent/provision_cluster.py`
**Runtime:** Python 3.12
**Dependencies:** `requests`

### Usage

```bash
export CONFLUENT_CLOUD_API_KEY=UBHPSOUE22BCLNPJ
export CONFLUENT_CLOUD_API_SECRET=<secret>
python infra/confluent/provision_cluster.py
```

### What the script does (in order)

1. **Create or reuse environment** `factorypulse-streamhouse`
2. **Create or reuse Kafka cluster** `factorypulse-cluster` (BASIC, AWS us-east-2)
3. **Wait for cluster provisioning** (polls until `RUNNING`)
4. **Create or reuse data-plane API key** scoped to the cluster
5. **Print bootstrap servers + data-plane key/secret** for `.env` population
6. **Create all 10 Kafka topics** (idempotent — skips existing)
7. **Write `.env`** with all resolved values (does NOT overwrite existing credentials already in `.env`)

---

## 5. Output: Environment Variables Produced

After running the provisioning script the following variables are set in `.env`:

```dotenv
CONFLUENT_ENABLED=true
CONFLUENT_BOOTSTRAP_SERVERS=<cluster>.aws.confluent.cloud:9092
CONFLUENT_KAFKA_API_KEY=<generated-data-plane-key>
CONFLUENT_KAFKA_API_SECRET=<generated-data-plane-secret>
SERIALIZATION_MODE=plain-json
RAG_PIPELINE_MODE=local
LLM_PROVIDER=none
```

---

## 6. Flink Extension (Optional)

To enable the managed Flink chunking and embedding pipeline:

1. Upgrade the cluster to `STANDARD` (enables Schema Registry).
2. Create a Flink compute pool in the same environment/region.
3. Run `infra/flink/continuous_rag.sql` in the Confluent Cloud Flink editor.
4. Set in `.env`:
   ```dotenv
   RAG_PIPELINE_MODE=flink
   SERIALIZATION_MODE=schema-registry-json
   CONFLUENT_SCHEMA_REGISTRY_URL=https://psrc-xxxxx...
   CONFLUENT_SCHEMA_REGISTRY_API_KEY=...
   CONFLUENT_SCHEMA_REGISTRY_API_SECRET=...
   ```

---

## 7. Security Notes

- The management API key (`CONFLUENT_CLOUD_API_KEY`) is used **only** during provisioning and is never written to `.env` or baked into the container image.
- The data-plane API key written to `.env` has cluster-scoped permissions only — it cannot create or delete clusters.
- Never commit `.env` to source control (it is in `.gitignore`).
- For IBM Code Engine deployment, store the data-plane key as a Code Engine secret per `docs/DEPLOY_CODE_ENGINE.md`.

---

## 8. Teardown

To remove all provisioned resources:

```bash
python infra/confluent/provision_cluster.py --teardown
```

This deletes (in order): topics → data-plane API key → Kafka cluster → environment.  
**Destructive and irreversible.** All topic data is permanently lost.

---

## 9. References

- [Confluent Cloud REST API v3](https://docs.confluent.io/cloud/current/api.html)
- `infra/confluent/provision_cluster.py` — provisioning script
- `scripts/create_topics.py` — topic-only creation (requires cluster already running)
- `infra/flink/continuous_rag.sql` — Flink SQL for managed embedding pipeline
- `docs/ARCHITECTURE.md` — full system architecture
- `support/confluent-resource-map.md` — topic-level resource map
