# Intelligence Capabilities

This directory contains building blocks for data intelligence — preparing and enhancing data quality, governance, and intelligent operations for AI workloads.

---

## When to Use

| Scenario | Building Block |
|---|---|
| Validate dataset completeness, uniqueness, and accuracy before feeding data to an AI model | [`data-quality/`](data-quality/) |
| Track where data came from and how it was transformed — end-to-end lineage graph | [`data-lineage/`](data-lineage/) |
| Know which downstream reports or models break when an upstream column changes | [`data-lineage/`](data-lineage/) |
| Let business users query databases with plain English instead of SQL | [`text2sql/`](text2sql/) |
| Improve Text2SQL accuracy by enriching table/column metadata with descriptions and synonyms | [`text2sql/`](text2sql/) |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**
- **IBM watsonx.data Intelligence** instance (for data-quality, data-lineage, text2sql)
- **IBM Databand** access (for data-lineage and data-observability lineage emission)

### Common Setup Pattern

```bash
# 1. Navigate to the asset
cd <building-block>/assets/<asset-name>

# 2. Configure credentials
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, and service-specific vars

# 3. Install and run
pip install -r requirements.txt
python app.py        # or: uvicorn app.server:app --host 0.0.0.0 --port 8080
# Swagger docs → http://localhost:8080/docs
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs) so Bob already knows the APIs, schemas, and IBM Cloud patterns for the capability you're working on.

**Install a Bob Mode** — give Bob a specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the mode appears in the mode selector. Switch to it before starting development.

**Install a Bob Skill** — teach Bob the details of this building block:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill. Bob will use it as active context for every prompt in this workspace.

---

## Building Blocks

### 1. Data Quality
**Location**: [`data-quality/`](data-quality/README.md)
**IBM Products**: IBM watsonx.data Intelligence
**Product Components**: Data Quality Rules API; Data Profiling API; IBM Cloud IAM; IBM Cloud Object Storage

Ensure data quality through automated validation rules and quality checks using IBM watsonx.data Intelligence. Define completeness, uniqueness, validity, consistency, and accuracy rules, execute them asynchronously, and surface quality scores.

**Key Features**:
- Five rule types: completeness, uniqueness, validity, consistency, accuracy
- Asynchronous rule execution via watsonx.data Intelligence REST API
- Aggregate quality score and per-rule result retrieval
- Column-level data profiling
- IBM COS archiving of quality reports
- FastAPI service wrapping the DAI API

**Bob Assets**:
- [`data-quality/bob-modes/base-modes/data-quality-builder.zip`](data-quality/bob-modes/base-modes/data-quality-builder.zip) — Bob mode for DQ rule authoring
- [`data-quality/bob-skills/data-quality-rules.zip`](data-quality/bob-skills/data-quality-rules.zip) — DQ rule implementation skill (all 5 types)

[View Details →](data-quality/README.md)

---

### 2. Data Lineage
**Location**: [`data-lineage/`](data-lineage/README.md)
**IBM Products**: IBM watsonx.data Intelligence (Manta data lineage), IBM Databand
**Product Components**: Manta data lineage REST API; OpenLineage HTTP transport; IBM Cloud IAM; IBM COS

Track data transformations and maintain a full lineage graph for all IBM Cloud data assets using IBM watsonx.data Intelligence (Manta) and IBM Databand. Emit OpenLineage events from any Python ETL, DataStage, or Spark pipeline.

**Key Features**:
- OpenLineage event ingestion (START / COMPLETE / FAIL) forwarded to IBM Databand
- Manta lineage graph queries — upstream/downstream traversal
- Column-level impact analysis
- IBM COS archiving of lineage and impact reports
- CLI tool for downstream impact analysis
- FastAPI service for event collection

**Bob Assets**:
- [`data-lineage/bob-modes/base-modes/data-lineage-builder.zip`](data-lineage/bob-modes/base-modes/data-lineage-builder.zip) — Bob mode for lineage instrumentation
- [`data-lineage/bob-skills/openlineage-instrumentation.zip`](data-lineage/bob-skills/openlineage-instrumentation.zip) — OpenLineage + Manta integration skill

[View Details →](data-lineage/README.md)

---

### 3. Text2SQL
**Location**: [`text2sql/`](text2sql/README.md)
**IBM Products**: IBM watsonx.data Intelligence
**Product Components**: Text2SQL API; DAI Metadata Enrichment API; IBM Cloud IAM

Convert natural language questions to SQL queries using IBM watsonx.data Intelligence. Enrich database metadata to maximize accuracy, then submit plain-English queries and receive validated, executable SQL.

**Key Features**:
- Natural language to SQL conversion via watsonx.data Intelligence Text2SQL API
- Metadata enrichment: table/column descriptions, synonyms, query examples
- Multi-dialect support: Presto, PostgreSQL, SQL Server, Oracle, Snowflake
- Model selection guidance (Granite vs Llama for query complexity)
- SQL safety validation and accuracy evaluation
- Deployable via IBM Code Engine or Red Hat OpenShift

**Bob Assets**:
- [`text2sql/bob-modes/base-modes/text-to-sql.zip`](text2sql/bob-modes/base-modes/text-to-sql.zip) — Bob mode for Text2SQL development
- [`text2sql/bob-skills/text2sql-metadata-enrichment.zip`](text2sql/bob-skills/text2sql-metadata-enrichment.zip) — Metadata enrichment skill
- [`text2sql/bob-skills/text2sql-query-optimizer.zip`](text2sql/bob-skills/text2sql-query-optimizer.zip) — Query accuracy optimization skill

[View Details →](text2sql/README.md)

---

## Quick Start

1. Choose the intelligence capability that matches your needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **Data Quality Management**: Validate datasets before they reach AI models
- **Natural Language Queries**: Convert business questions to SQL without SQL expertise
- **Data Governance**: Track every transformation in the lineage graph
- **Impact Analysis**: Identify all downstream assets affected by a schema change
- **Compliance Reporting**: Full audit trail from source to consumption
