# Data Lineage

**Core Capability**: Intelligence
**IBM Products**: IBM watsonx.data Intelligence (Manta data lineage), IBM Databand
**Product Components**: Manta Data Lineage; OpenLineage HTTP Transport; IBM Cloud IAM; IBM Cloud Object Storage

## Overview

Track data transformations and maintain a full lineage graph for all IBM Cloud data assets using **IBM watsonx.data Intelligence** (powered by Manta) and **IBM Databand**. Emit OpenLineage events from any Python ETL, IBM DataStage, or Apache Spark pipeline and query the resulting lineage graph for governance, impact analysis, and compliance reporting.

---

## When to Use

| Scenario | Asset |
|---|---|
| Instrument a Python ETL, DataStage, or Spark job to emit lineage events | [`assets/openlineage-collector/`](assets/openlineage-collector/) |
| Collect and forward OpenLineage events to IBM Databand from a central service | [`assets/openlineage-collector/`](assets/openlineage-collector/) — FastAPI endpoint |
| Find all downstream assets affected by a schema or data change | [`assets/lineage-impact-analyzer/`](assets/lineage-impact-analyzer/) — CLI tool |
| Archive lineage and impact reports to IBM COS for audit compliance | [`assets/lineage-impact-analyzer/`](assets/lineage-impact-analyzer/) — `--archive-cos` |

---

## Getting Started

### Prerequisites

- **IBM watsonx.data Intelligence** instance with Manta lineage enabled — note `WXDI_PROJECT_ID` and base URL
- **IBM Databand** instance — note `DATABAND_URL` and `DATABAND_ACCESS_TOKEN`
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**

### Quick Start — OpenLineage Collector

```bash
cd assets/openlineage-collector
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, DATABAND_URL, DATABAND_ACCESS_TOKEN
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Emit your first lineage event:
```bash
curl -X POST http://localhost:8080/events/lineage \
  -H "Content-Type: application/json" \
  -d '{"pipeline": "customer_etl", "job": "transform_orders", "eventType": "COMPLETE"}'
```

### Quick Start — Impact Analyzer

```bash
cd assets/lineage-impact-analyzer
pip install -r requirements.txt
python impact_analyzer.py --asset-id your-asset-id
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Data Lineage building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of OpenLineage event construction, IBM Databand integration, Manta lineage graph queries, and impact analysis patterns.

**Install the Bob Mode** — give Bob a Data Lineage specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/data-lineage-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/data-lineage-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Data Lineage Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the OpenLineage and Manta patterns:
```bash
unzip bob-skills/openlineage-instrumentation.zip
```
Open IBM Bob → Skills panel → enable `openlineage-instrumentation`.

---

## Building Blocks

### 1. OpenLineage Collector
**Location**: `assets/openlineage-collector/`
**IBM Products**: watsonx.data Intelligence, IBM Databand, IBM Cloud IAM
**Description**: FastAPI service that accepts OpenLineage events and forwards them to IBM Databand's Marquez endpoint. Also exposes Manta lineage graph queries via the watsonx.data Intelligence REST API.

**Quick Start**:
```bash
cd assets/openlineage-collector
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, DATABAND_URL, DATABAND_ACCESS_TOKEN
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/events/lineage` | Ingest OpenLineage event → forwards to IBM Databand |
| `GET` | `/lineage/assets` | List all Manta-tracked assets |
| `POST` | `/lineage/graph` | Get upstream/downstream lineage graph |
| `POST` | `/lineage/impact` | Downstream impact analysis for an asset |

---

### 2. Lineage Impact Analyzer
**Location**: `assets/lineage-impact-analyzer/`
**IBM Products**: watsonx.data Intelligence, IBM COS, IBM Cloud IAM
**Description**: CLI tool for downstream impact analysis — given a source asset, renders a full dependency tree and archives a JSON impact report to IBM COS.

**Quick Start**:
```bash
cd assets/lineage-impact-analyzer
pip install -r requirements.txt

# Show downstream impact tree
python impact_analyzer.py --asset-id your-asset-id

# Save report to file
python impact_analyzer.py --asset-id your-asset-id --output impact_report.json

# Archive to IBM COS
python impact_analyzer.py --asset-id your-asset-id --archive-cos
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for OpenLineage instrumentation, Manta query authoring, and impact analysis
  - **Install**: copy [`bob-modes/base-modes/data-lineage-builder.zip`](./bob-modes/base-modes/data-lineage-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `openlineage-instrumentation` | [`bob-skills/openlineage-instrumentation.zip`](./bob-skills/openlineage-instrumentation.zip) | OpenLineage event construction, IBM Databand integration, Manta lineage graph queries, impact analysis patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Architecture

```
Python ETL / DataStage / Spark
        │
        │  OpenLineage events (START / COMPLETE / FAIL)
        ▼
OpenLineage Collector (FastAPI)
        │
        ├── POST /api/v1/lineage → IBM Databand (Marquez)
        │                              │
        │                              ▼
        │                        Manta Lineage Graph
        │
        └── GET /data_lineage/*  → watsonx.data Intelligence
                                   (Manta REST API)

Impact Analyzer CLI
        │
        └── GET /data_lineage/impact_analysis
                │
                ▼ IBM Cloud Object Storage (archived reports)
```

## IBM Cloud References

- [watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [watsonx.data Intelligence API Reference](https://cloud.ibm.com/apidocs/watsonx-data-intelligence)
- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [OpenLineage Specification](https://openlineage.io/spec)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
