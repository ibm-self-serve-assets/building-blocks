# Text2SQL

**Core Capability**: Intelligence
**IBM Products**: IBM watsonx.data Intelligence
**Product Components**: Text2SQL API; DAI Metadata Enrichment API; IBM Cloud IAM; FastAPI application

## Overview

Convert natural language questions to SQL queries using **IBM watsonx.data Intelligence** Text2SQL capability. Enrich database metadata (table descriptions, column synonyms, query examples) via the DAI REST API to maximize query accuracy, then submit natural language questions and receive validated, executable SQL — all without writing a single line of SQL manually.

---

## When to Use

| Scenario | Asset |
|---|---|
| Expose a natural language query interface over an existing database | [`assets/applications/text_to_sql_app/`](assets/applications/text_to_sql_app/) |
| Improve Text2SQL accuracy by enriching table and column metadata | [`assets/metadata_enrichment_text2sql/`](assets/metadata_enrichment_text2sql/) |
| Deploy the Text2SQL app to IBM Cloud (serverless or container) | Code Engine or OpenShift — see the deployment guides in the asset |
| Let business users self-serve SQL without SQL expertise | Use the FastAPI `/query` endpoint as a backend for a UI |

> **Metadata enrichment matters**: Text2SQL accuracy improves significantly when tables and columns have descriptions, synonyms, and query examples. Run the metadata enrichment toolkit before evaluating query quality.

---

## Getting Started

### Prerequisites

- **IBM watsonx.data Intelligence** instance — note your Project ID (`WXDI_PROJECT_ID`) and base URL (`WXDI_BASE_URL`)
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**

### Quick Start — Text2SQL Application

```bash
cd assets/applications/text_to_sql_app
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, WXDI_BASE_URL
pip install -r requirements.txt
python app.py
# Swagger UI → http://localhost:8080/docs
```

Ask your first natural language question:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me total revenue by region for Q3 2024"}'
```

### Improve Accuracy — Metadata Enrichment

```bash
cd assets/metadata_enrichment_text2sql
# Edit config.py: IBM_API_KEY, WXDI_PROJECT_ID
python enrich_metadata.py
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Text2SQL building block ships a **Bob Mode** and **two Bob Skills** that give Bob expert knowledge of the watsonx.data Intelligence Text2SQL API, metadata enrichment patterns, model selection, and SQL accuracy evaluation.

**Install the Bob Mode** — give Bob a Text2SQL specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/text-to-sql.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/text-to-sql.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Text2SQL** mode appears in the mode selector.

**Install Bob Skills** — teach Bob the Text2SQL and metadata details:
```bash
unzip bob-skills/text2sql-metadata-enrichment.zip
unzip bob-skills/text2sql-query-optimizer.zip
```
Open IBM Bob → Skills panel → enable both skills. Bob will use them as active context for every prompt in this workspace.

---

## Building Blocks

### 1. Text2SQL Application
**Location**: `assets/applications/text_to_sql_app/`
**IBM Products**: watsonx.data Intelligence, IBM Cloud IAM
**Description**: FastAPI application that wraps the watsonx.data Intelligence Text2SQL endpoint — accepts natural language queries, routes them to the DAI API, and returns SQL with execution results.

**Quick Start**:
```bash
cd assets/applications/text_to_sql_app
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, WXDI_BASE_URL
pip install -r requirements.txt
python app.py
# Swagger UI → http://localhost:8080/docs
```

**Example — Natural language to SQL**:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me total revenue by region for Q3 2024"}'
```

**Response**:
```json
{
  "sql": "SELECT region, SUM(revenue) AS total_revenue FROM sales.transactions WHERE quarter = 'Q3' AND year = 2024 GROUP BY region ORDER BY total_revenue DESC",
  "confidence": 0.94
}
```

**Deployment Options**:
- **IBM Code Engine**: see [`assets/applications/code-engine-setup/`](./assets/applications/code-engine-setup/)
- **Red Hat OpenShift**: see [`assets/applications/openshift-setup/`](./assets/applications/openshift-setup/)

---

### 2. Metadata Enrichment Toolkit
**Location**: `assets/metadata_enrichment_text2sql/`
**IBM Products**: watsonx.data Intelligence, IBM Cloud IAM
**Description**: Python toolkit for enriching watsonx.data Intelligence project metadata — adds table descriptions, column descriptions, synonyms, and query examples to significantly improve Text2SQL accuracy.

**Quick Start**:
```bash
cd assets/metadata_enrichment_text2sql
# Edit config.py: IBM_API_KEY, WXDI_PROJECT_ID
python enrich_metadata.py
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for Text2SQL development, metadata enrichment, and query optimization
  - **Install**: copy [`bob-modes/base-modes/text-to-sql.zip`](./bob-modes/base-modes/text-to-sql.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `text2sql-metadata-enrichment` | [`bob-skills/text2sql-metadata-enrichment.zip`](./bob-skills/text2sql-metadata-enrichment.zip) | watsonx.data Intelligence project onboarding, table/column description enrichment, synonym design, query example authoring, accuracy measurement |
| `text2sql-query-optimizer` | [`bob-skills/text2sql-query-optimizer.zip`](./bob-skills/text2sql-query-optimizer.zip) | Model selection (Granite vs Llama), SQL safety validation, accuracy evaluation (exact-match + execution accuracy), error pattern diagnosis, dialect tuning |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Supported SQL Dialects

| Dialect | Use Case |
|---|---|
| `presto` | IBM watsonx.data Presto engine (default) |
| `postgresql` | PostgreSQL / IBM Db2 Warehouse |
| `mssql` | Microsoft SQL Server |
| `oracle` | Oracle Database |
| `snowflake` | Snowflake |

## Architecture

```
User Natural Language Question
        │
        │  POST /query
        ▼
Text2SQL App (FastAPI)
        │
        │  IBM IAM token (API key → Bearer)
        ▼
watsonx.data Intelligence
  Text2SQL API
  /v2/text_to_sql/generate
        │
        │  Enriched metadata (tables, columns, synonyms)
        ▼
Generated SQL
        │
        ▼
Presto / DB2 / PostgreSQL execution
```

## IBM Cloud References

- [IBM watsonx.data Intelligence on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonx-data-intelligence)
- [watsonx.data Intelligence API Reference](https://cloud.ibm.com/apidocs/watsonx-data-intelligence)
- [IBM Code Engine Documentation](https://cloud.ibm.com/docs/codeengine)
- [Red Hat OpenShift on IBM Cloud](https://cloud.ibm.com/docs/openshift)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
