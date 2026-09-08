# Metadata Enrichment & Data Quality

This directory contains building blocks for **Metadata Enrichment & Data Quality** using **IBM watsonx.data intelligence** and related lineage capabilities.

The documentation page for this building block is at:
[Building Blocks — Metadata Enrichment & Data Quality](https://ibm-self-serve-assets.github.io/building-blocks-docs/data-core/context/metadata-enrichment/)

---

## Purpose

Add business meaning, quality rules, descriptions, terms, classifications and relationships to technical data assets so users and AI systems can find, understand and use data more effectively.

Raw schemas contain abbreviations, numeric codes and technical names that only original developers understand. AI systems — especially Text2SQL and RAG — depend on rich, meaningful metadata to produce accurate results. This building block automates the process of profiling data, assigning business terms, generating descriptions, applying quality rules and identifying relationships at scale.

---

## Available Building Blocks

| Building Block | Path | Description |
|---|---|---|
| **Data Quality** | [`data-quality/`](data-quality/) | Automated validation rules and quality scoring using IBM watsonx.data intelligence |
| **Data Lineage** | [`data-lineage/`](data-lineage/) | End-to-end lineage graph from source to AI model consumption using OpenLineage and IBM Manta |

---

## When to Use

| Scenario | Building Block |
|---|---|
| Validate dataset completeness, uniqueness, and accuracy before feeding data to an AI model | [`data-quality/`](data-quality/README.md) |
| Apply automated profiling, business term assignment, and enrichment to technical schemas | [`data-quality/`](data-quality/README.md) |
| Track where data came from and how it was transformed — end-to-end lineage graph | [`data-lineage/`](data-lineage/README.md) |
| Know which downstream reports or models break when an upstream column changes | [`data-lineage/`](data-lineage/README.md) |
| Improve Text2SQL accuracy by enriching table and column metadata with descriptions and terms | [`data-quality/`](data-quality/README.md) |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+**
- **IBM watsonx.data intelligence** instance (for data-quality, enrichment, and lineage graph capabilities)

> **Prerequisite note**: IBM Databand is required only when you are also using pipeline observability features. It is not a prerequisite for metadata enrichment, data quality or Manta lineage graph capabilities, which are provided directly by IBM watsonx.data intelligence. See the [Data Observability](../data-observability/README.md) building block for Databand-specific observability patterns.

### Common Setup Pattern

```bash
# 1. Navigate to the building block asset
cd <building-block>/assets/<asset-name>

# 2. Configure credentials
cp .env.example .env
# Edit .env: IBM_API_KEY, WXDI_PROJECT_ID, and service-specific vars

# 3. Install and run
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
# Swagger docs → http://localhost:8080/docs
```

### IBM Bob — Your Fellow Developer

Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs).

**Install a Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

**Install a Bob Skill**:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM watsonx.data intelligence](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-enriching-your-assets)** | Metadata enrichment, profiling, business glossary, classifications, quality rules, relationships, lineage (via Manta) |
