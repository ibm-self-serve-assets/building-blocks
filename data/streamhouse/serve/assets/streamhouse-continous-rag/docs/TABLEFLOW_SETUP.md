# Tableflow setup

Tableflow materializes selected Kafka topics as Iceberg or Delta tables, exposing them to analytical and AI workloads through an open-table format. In FactoryPulse, Tableflow is the **analytical / historical path** — it is not involved in the synchronous RAG retrieval latency path (see [ADR-005](DECISIONS.md#adr-005--tableflow-is-not-in-the-synchronous-rag-path)).

---

## What gets materialized

| Kafka topic | Tableflow name | Why |
|---|---|---|
| `factory.state` | `factory-state-tableflow` | Continuous factory health record — enables trend analysis, shift comparison, ML forecasting |
| `factory.exceptions` | `factory-exceptions-tableflow` | Exception history — enables root-cause pattern mining, MTTR analysis, SLA reporting |

These topics are produced by either:
- The Flink operational pipeline (`infra/flink/factory_operations.sql`) on STANDARD clusters.
- The Python demo step API (`/api/demo/step/{step}`) for quick demos without a Flink compute pool.

---

## How to enable

### Step 1 — Configure a cloud storage integration

Tableflow requires a cloud storage destination (S3, GCS, or Azure ADLS) configured in the Confluent Cloud console before applying Terraform.

1. In **Confluent Cloud Console** → your environment → **Tableflow** → **Storage integration**, add a storage integration pointing to your S3 bucket (or equivalent).
2. Note the integration name — you will need it if you add `managed_resource` blocks to the Terraform resources.

### Step 2 — Enable in Terraform

In `infra/confluent/terraform/terraform.tfvars`:

```hcl
enable_tableflow = true
```

Then apply:

```bash
cd infra/confluent/terraform
terraform apply
```

Terraform will create two `confluent_tableflow_topic` resources for `factory.state` and `factory.exceptions`.

### Step 3 — Enable in the app

Set in your `.env` (or Code Engine secret):

```bash
TABLEFLOW_ENABLED=true
```

The `GET /api/tableflow/status` endpoint and the Settings UI card will then show `Enabled` and list the materialized topics.

---

## What it is not

- **Not part of the RAG retrieval path.** The synchronous RAG path is: `rag.knowledge.raw` → Flink chunk + embed → `rag.knowledge.embeddings` → in-process vector index → answer. Tableflow runs independently and asynchronously.
- **Not a replacement for Kafka.** Topics remain on Kafka for low-latency consumption. Tableflow is an additional analytical view, not a migration.
- **Not a vector store.** For semantic search at scale, use a supported external vector store with `VECTOR_SEARCH_AGG` — see `infra/flink/external_vector_search_example.sql`.

---

## Downstream consumption

Once Tableflow is running, the materialized Iceberg/Delta tables can be consumed by:

- **Apache Spark / Databricks** — `spark.read.format("iceberg").load("<table_uri>")`
- **Snowflake / BigQuery** — external table pointed at the Iceberg metadata location
- **Flink batch jobs** — for historical ML feature engineering
- **Tableau / Looker** — via an Iceberg-compatible catalog connector

The tables are schema-governed through Schema Registry (active automatically when SR credentials are present). Schema evolution is tracked in the Confluent Schema Registry and reflected in the Iceberg table metadata.

---

## Architecture position

```
factory.state (Kafka, compacted)
        │
        ├──→ FastAPI UI consumer          (live operational view)
        ├──→ Alerts / Actions             (exception-to-action)
        └──→ Tableflow → Iceberg/Delta    (historical analytics / AI)
                              │
                              └──→ Spark / Snowflake / BI tools
```

The key point: **the same event that drives the live operational dashboard also feeds the analytical lakehouse** — there is no separate ETL pipeline.
