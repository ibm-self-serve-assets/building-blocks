# Data Observability

**Core Capability**: Integration
**IBM Products**: IBM Databand
**Product Components**: Databand REST API v1; OpenLineage HTTP Transport; IBM Cloud IAM; IBM Cloud Object Storage

## Overview

Monitor and ensure data pipeline quality and reliability using **IBM Databand** — IBM's enterprise data observability platform. Track every pipeline run, surface data quality anomalies, enforce SLA thresholds, and maintain a complete OpenLineage-compliant lineage graph for all IBM Cloud data assets.

---

## When to Use

| Scenario | Asset |
|---|---|
| Monitor pipeline run health and surface quality anomalies via REST API | [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) |
| Emit OpenLineage events from a Python ETL, DataStage, or Spark job | [`assets/openlineage-emitter/`](assets/openlineage-emitter/) |
| Apply pre-built alert policies (null-rate, schema-drift, SLA-breach) to a pipeline | [`assets/databand-alert-templates/`](assets/databand-alert-templates/) |
| Archive pipeline run reports to IBM COS for audit compliance | [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) — COS archiving |

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
**Description**: FastAPI service that wraps the Databand REST API v1 — list pipelines, inspect run health, retrieve quality metrics, and manage alert policies programmatically.

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
**Description**: Python library and CLI that instruments any Python ETL script, IBM DataStage job, or Apache Spark application to emit OpenLineage events (START / COMPLETE / FAIL) to IBM Databand's `/api/v1/lineage` endpoint.

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
  /api/v1/runs             │  Metrics / Alerts
  /api/v1/alert_defs       ▼
                    IBM Cloud Object Storage
                    (archived run reports)
```

## IBM Cloud References

- [IBM Databand on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/databand)
- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [OpenLineage Specification](https://openlineage.io/spec)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
