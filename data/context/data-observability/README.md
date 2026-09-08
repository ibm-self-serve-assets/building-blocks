# Data Observability

**Core Capability**: Context
**IBM Products**: IBM watsonx.data integration, IBM Data Observability by Databand
**Product Components**: watsonx.data integration Data Observability; Databand REST API v1; OpenLineage HTTP Transport; IBM Cloud IAM; IBM Cloud Object Storage

## What Is This Building Block?

**Data Observability** provides operational visibility into your data pipelines — monitoring pipeline run health, detecting data quality anomalies, enforcing SLA thresholds and surfacing alertable conditions before unreliable data affects downstream analytics or AI.

This building block is centred on **IBM Data Observability by Databand** and **IBM watsonx.data integration Data Observability**. IBM watsonx.data integration provides the observability capability for monitoring integration processes and investigating incidents. IBM Databand adds pipeline, run, task and dataset monitoring, anomaly detection and alerting — including integration with watsonx.data Spark monitoring.

> **Scope note — Observability vs Enterprise Lineage**: Data Observability / Databand focuses on pipeline operational health: runs, tasks, datasets, anomaly detection, SLA monitoring and operational quality signals. Databand is not, by itself, a complete enterprise lineage repository for all IBM Cloud data assets. Broader lineage capabilities — including Manta-powered end-to-end lineage graphs — are part of **IBM watsonx.data intelligence**. OpenLineage events emitted from pipelines can flow into both Databand (for operational monitoring) and watsonx.data intelligence (for lineage governance). See the **[Data Lineage](../metadata-enrichment/data-lineage/README.md)** building block for lineage graph scenarios.

---

## What Problem Does It Solve?

| Problem | What This Building Block Provides |
|---|---|
| Silent pipeline failures go undetected | Databand monitors every pipeline run and surfaces failures immediately |
| Data quality degrades without warning | Anomaly detection on row counts, null rates, schema drift and quality scores |
| SLA violations are discovered too late | Threshold-based alerts for run duration and data freshness |
| Incident investigation requires manual log trawling | REST API access to run history, task metrics and alert policies |
| Pipeline health reports need archiving for compliance | COS archiving of run reports via the included pipeline monitor |

---

## When to Use

| Scenario | Asset |
|---|---|
| Monitor pipeline run health and surface quality anomalies via REST API | [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) |
| Emit OpenLineage events from a Python ETL, DataStage, or Spark job | [`assets/openlineage-emitter/`](assets/openlineage-emitter/) |
| Apply pre-built alert policies (null-rate, schema-drift, SLA-breach) to a pipeline | [`assets/databand-alert-templates/`](assets/databand-alert-templates/) |
| Archive pipeline run reports to IBM COS for audit compliance | [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) — COS archiving |

## When NOT to Use

| Scenario | Use Instead |
|---|---|
| End-to-end data lineage governance (column-level, cross-platform) | [`../metadata-enrichment/data-lineage/`](../metadata-enrichment/data-lineage/README.md) — IBM watsonx.data intelligence (Manta) |
| Metadata enrichment, business glossary, quality rules | [`../metadata-enrichment/`](../metadata-enrichment/README.md) — IBM watsonx.data intelligence |

---

## Getting Started

### Prerequisites

- **IBM Databand** instance on IBM Cloud — note your `DATABAND_URL` and `DATABAND_ACCESS_TOKEN`
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**

### Quick Start — Pipeline Monitor

```bash
cd assets/databand-pipeline-monitor
cp .env.example .env
# Edit .env: DATABAND_URL, DATABAND_ACCESS_TOKEN, IBM_API_KEY
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

### Quick Start — OpenLineage Emitter

```bash
cd assets/openlineage-emitter
pip install -r requirements.txt

# Instrument a Python job
python emitter.py \
  --pipeline customer_etl \
  --job transform_orders \
  --inputs "cos://raw-bucket/orders.csv" \
  --outputs "iceberg://cos_catalog/sales.orders" \
  --event-type COMPLETE
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Data Observability building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of IBM Databand pipeline onboarding, OpenLineage event design, alert policy authoring, and IBM COS report archiving.

**Install the Bob Mode** — give Bob a Data Observability specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/data-observability-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/data-observability-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Data Observability Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the Databand patterns:
```bash
unzip bob-skills/databand-pipeline-setup.zip
```
Open IBM Bob → Skills panel → enable `databand-pipeline-setup`.

---

## Building Blocks

### 1. Databand Pipeline Monitor
**Location**: `assets/databand-pipeline-monitor/`
**IBM Products**: IBM Databand, IBM Cloud IAM, IBM COS
**Description**: FastAPI service that wraps the Databand REST API v1 — list pipelines, inspect run health, retrieve quality metrics, and manage alert policies programmatically. Supports optional archiving of run reports to IBM COS.

**Quick Start**:
```bash
cd assets/databand-pipeline-monitor
cp .env.example .env
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**API Endpoints**:
- `GET  /pipelines` — List all Databand-monitored pipelines
- `POST /pipelines/runs` — Run history with date filtering
- `GET  /pipelines/runs/{uid}` — Full run detail + per-task metrics
- `GET  /alerts` — List alert policies
- `POST /alerts` — Create threshold-based alert policy
- `POST /metrics/quality-summary` — Aggregated quality score for a run

---

### 2. OpenLineage Emitter
**Location**: `assets/openlineage-emitter/`
**IBM Products**: IBM Databand, IBM Cloud IAM
**Description**: Python library and CLI that instruments any Python ETL script, IBM DataStage job, or Apache Spark application to emit OpenLineage events (START / COMPLETE / FAIL) to IBM Databand's `/api/v1/lineage` endpoint. OpenLineage events forwarded to Databand are used for operational pipeline observability. For consumption in a lineage graph (impact analysis, governance), see the [Data Lineage](../metadata-enrichment/data-lineage/README.md) building block.

**Quick Start**:
```bash
cd assets/openlineage-emitter
pip install -r requirements.txt

# CLI usage
python emitter.py \
  --pipeline customer_etl \
  --job      transform_orders \
  --inputs   "cos://raw-bucket/orders.csv" \
  --outputs  "iceberg://cos_catalog/sales.orders_curated" \
  --event-type COMPLETE

# Python context manager
from emitter import PipelineRun

with PipelineRun(
    pipeline_name="customer_etl",
    job_name="transform_orders",
    inputs=["cos://raw-bucket/orders.csv"],
    outputs=["iceberg://cos_catalog/sales.orders"],
):
    # ETL code here
    pass
```

---

### 3. Databand Alert Templates
**Location**: `assets/databand-alert-templates/`
**IBM Products**: IBM Databand, IBM Cloud IAM
**Description**: Pre-built YAML alert policy templates for common data quality failure modes, with a CLI tool to apply them to any Databand instance.

**Included Templates**:

| Template | Condition | Severity |
|---|---|---|
| `null_rate_policy` | null rate > 5% | High |
| `row_count_drop_policy` | row count < 80% of prior run | Critical |
| `schema_drift_policy` | schema change detected | High |
| `sla_breach_policy` | run duration > 2 hours | Medium |
| `quality_score_policy` | quality score < 0.85 | High |
| `duplicate_rate_policy` | duplicate rate > 2% | Medium |

**Quick Start**:
```bash
cd assets/databand-alert-templates

# Apply all templates to a pipeline
python apply_alert_templates.py --all --pipeline customer_pipeline

# Dry-run: preview payloads
python apply_alert_templates.py --all --pipeline customer_pipeline --dry-run
```

---

## What Assets Are Included

| Asset | Type | Description |
|---|---|---|
| [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) | Runnable FastAPI service | REST API client for pipeline run health and COS archiving |
| [`assets/openlineage-emitter/`](assets/openlineage-emitter/) | Python library + CLI | Emit OpenLineage events from Python / DataStage / Spark to Databand |
| [`assets/databand-alert-templates/`](assets/databand-alert-templates/) | YAML templates + CLI | Pre-built alert policies: null-rate, schema-drift, SLA-breach |
| [`bob-modes/base-modes/data-observability-builder.zip`](bob-modes/base-modes/data-observability-builder.zip) | Bob Mode | Data Observability specialist persona |
| [`bob-skills/databand-pipeline-setup.zip`](bob-skills/databand-pipeline-setup.zip) | Bob Skill | Databand pipeline onboarding and alert policy authoring |

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI assistant mode for data observability development
  - IBM Databand API integration patterns
  - OpenLineage instrumentation for Python / DataStage / Spark
  - Alert policy design and quality threshold tuning
  - IBM COS report archiving
  - **Install**: copy [`bob-modes/base-modes/data-observability-builder.zip`](./bob-modes/base-modes/data-observability-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `databand-pipeline-setup` | [`bob-skills/databand-pipeline-setup.zip`](./bob-skills/databand-pipeline-setup.zip) | Databand pipeline onboarding, OpenLineage event design, alert policy authoring, IBM IAM auth patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Architecture

```
IBM Data Pipeline (DataStage / Spark / Python)
        │
        │  OpenLineage events (START / COMPLETE / FAIL)
        ▼
IBM Databand  ←─── Databand Pipeline Monitor (REST API)
  /api/v1/lineage          │
  /api/v1/runs             │  Metrics / Alerts / Run Health
  /api/v1/alert_defs       ▼
                     IBM Cloud Object Storage
                     (archived run reports)

Note: OpenLineage events can also be forwarded to IBM watsonx.data intelligence
for lineage graph consumption — see the Data Lineage building block.
```

## Limitations and Considerations

- IBM Databand provides operational pipeline observability and anomaly detection. It is not a complete enterprise lineage repository for all IBM Cloud data assets.
- For end-to-end lineage graphs (column-level, cross-platform, impact analysis), use the **[Data Lineage](../metadata-enrichment/data-lineage/README.md)** building block with IBM watsonx.data intelligence (Manta).
- Databand availability and specific API capabilities may vary by deployment version. Verify your instance version against the [Databand documentation](https://www.ibm.com/docs/en/databand).

## IBM Cloud References

- [IBM Databand on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/databand)
- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [OpenLineage Specification](https://openlineage.io/spec)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
