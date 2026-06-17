# Data Quality

**Core Capability**: Intelligence
**IBM Products**: IBM watsonx.data Intelligence
**Product Components**: Data Quality Rules API; Data Profiling API; IBM Cloud IAM; IBM Cloud Object Storage

## Overview

Ensure data quality through automated validation rules and quality checks using **IBM watsonx.data Intelligence** on IBM Cloud. Define completeness, uniqueness, validity, consistency, and accuracy rules against any data asset in your watsonx.data Intelligence project. Execute rules asynchronously, surface quality scores, and profile column statistics to catch data issues before they reach AI models.

---

## When to Use

| Scenario | Asset |
|---|---|
| Validate a dataset for null values, duplicates, or format violations before AI training | [`assets/quality-rules-engine/`](assets/quality-rules-engine/) — create + execute rules |
| Get an aggregate quality score for a watsonx.data project | [`assets/quality-rules-engine/`](assets/quality-rules-engine/) — `GET /rules/score` |
| Profile column statistics (null rate, distinct count, histograms) on a new dataset | [`assets/quality-rules-engine/`](assets/quality-rules-engine/) — `POST /profile` |
| Archive quality reports to IBM COS for audit or compliance | Quality Rules Engine — COS archiving |

---

## Getting Started

### Prerequisites

- **IBM watsonx.data Intelligence** instance — note your Project ID (`WXDI_PROJECT_ID`) and base URL
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**

### Quick Start

```bash
cd assets/quality-rules-engine
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, WXDI_BASE_URL
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Create your first completeness rule:
```bash
curl -X POST http://localhost:8080/rules \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"name": "email_not_null", "type": "completeness", "columns": ["email"], "threshold": 0.99}'
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Data Quality building block ships a **Bob Mode** and **Bob Skill** that give Bob expert knowledge of the watsonx.data Intelligence DQ Rules API, all 5 rule types, async execution, quality scoring, and data profiling.

**Install the Bob Mode** — give Bob a Data Quality specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/data-quality-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/data-quality-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Data Quality Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the DQ rule patterns:
```bash
unzip bob-skills/data-quality-rules.zip
```
Open IBM Bob → Skills panel → enable `data-quality-rules`.

---

## Building Blocks

### 1. Quality Rules Engine
**Location**: `assets/quality-rules-engine/`
**IBM Products**: watsonx.data Intelligence, IBM Cloud IAM, IBM COS
**Description**: FastAPI service wrapping the watsonx.data Intelligence (DAI) REST API — create rules, execute them, retrieve results, and surface aggregate quality scores.

**Quick Start**:
```bash
cd assets/quality-rules-engine
cp .env.example .env
# Edit .env: set IBM_API_KEY and WXDI_PROJECT_ID
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/rules` | Create a DQ rule (completeness, uniqueness, validity, consistency, accuracy) |
| `GET` | `/rules` | List all DQ rules in the project |
| `POST` | `/rules/{rule_id}/execute` | Execute a rule asynchronously |
| `GET` | `/rules/score` | Aggregate quality score (passed / total) |
| `GET` | `/results` | List execution results |
| `GET` | `/results/{id}` | Single result detail |
| `POST` | `/profile` | Submit column profiling job |
| `GET` | `/profile/{job_id}` | Poll profiling job status |

**Example — Create a completeness rule**:
```bash
curl -X POST http://localhost:8080/rules \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "customer_email_not_null",
    "type": "completeness",
    "asset_ref": {"asset_id": "your-asset-id"},
    "columns": ["email"],
    "threshold": 0.99
  }'
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for DQ rule authoring, quality score interpretation, and profiling strategy design
  - **Install**: copy [`bob-modes/base-modes/data-quality-builder.zip`](./bob-modes/base-modes/data-quality-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `data-quality-rules` | [`bob-skills/data-quality-rules.zip`](./bob-skills/data-quality-rules.zip) | watsonx.data Intelligence DQ rule authoring (all 5 rule types), async execution, quality score analysis, data profiling |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Supported Rule Types

| Type | Description | Use Case |
|---|---|---|
| `completeness` | Checks null/missing value rate | Email, phone must not be null |
| `uniqueness` | Detects duplicate records | Primary key uniqueness check |
| `validity` | Validates format/regex/enum | ISO date format, country code enum |
| `consistency` | Cross-column referential checks | Country + zip code must match |
| `accuracy` | Comparison to reference dataset | Match against master customer file |

## Architecture

```
Your Application
      │
      │  REST API (+ REST_API_KEY header)
      ▼
Quality Rules Engine (FastAPI)
      │
      │  IBM IAM (API key → Bearer token)
      ▼
watsonx.data Intelligence REST API
  /data_quality/rules
  /data_quality/results
  /data_quality/profile_jobs
      │
      ▼
IBM Cloud Object Storage
(quality report archives)
```

## IBM Cloud References

- [watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [watsonx.data Intelligence API Reference](https://cloud.ibm.com/apidocs/watsonx-data-intelligence)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
