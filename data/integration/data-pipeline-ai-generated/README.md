# Data Ingestion

**Core Capability**: Integration
**IBM Products**: IBM DataStage, IBM UDI (Unstructured Data Integration), IBM Docling, IBM Cloud IAM
**Product Components**: DataStage connectors; CDC (Change Data Capture); Docling document parsing; IBM COS

## Overview

Comprehensive data ingestion for IBM watsonx.data covering both **structured** data sources (relational databases via DataStage CDC connectors) and **unstructured** data (documents, PDFs, images via IBM Docling and UDI). AI-generated pipelines are created by IBM Bob using the included modes and skills — describe your source and target and Bob generates the ingestion pipeline automatically.

---

## When to Use

| Scenario | Asset |
|---|---|
| Ingest from IBM Db2, PostgreSQL, MySQL, or Oracle into watsonx.data | [`assets/structured-data/`](assets/structured-data/) — DataStage CDC patterns |
| Ingest PDFs, DOCX, HTML, images, or email documents into a pipeline | [`assets/unstructured-data/`](assets/unstructured-data/) — IBM Docling + UDI patterns |
| Use IBM UDI + OpenSearch for unstructured document search | [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/) |
| Ask Bob to generate a pipeline from a plain-English description | Activate **Data Ingestion** Bob Mode (`data-ingestion.zip`) |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM DataStage** instance (for structured ingestion)
- **IBM Docling** / **IBM UDI** (for unstructured ingestion)
- **IBM watsonx.data** instance as the data target

### Quick Start — UDI + OpenSearch Ingestion

```bash
cd assets/udi-ingestion-opensearch/scripts
cp .env.example .env
# Edit .env: IBM_API_KEY, OPENSEARCH_HOST, OPENSEARCH_PASSWORD, COS credentials
pip install -r requirements.txt
python setup.py      # provision OpenSearch index
python ingest.py     # run document ingestion
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Data Ingestion building block ships a **Bob Mode** and **Bob Skills** that let Bob generate complete DataStage or Docling ingestion pipelines from a plain-English description of your source and target.

**Install the Bob Mode** — give Bob a Data Ingestion specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/data-ingestion.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/data-ingestion.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Data Ingestion** mode appears in the mode selector. Describe your ingestion requirement and Bob generates the full pipeline.

**Install Bob Skills** — teach Bob the structured and unstructured patterns:
```bash
unzip bob-skills/data-ingestion-structured.zip
unzip bob-skills/data-ingestion-unstructured.zip
```
Open IBM Bob → Skills panel → enable the skill(s).

---

## Building Blocks

### 1. Structured Data Ingestion
**Location**: `assets/structured-data/`
**IBM Products**: IBM DataStage, IBM Cloud IAM
**Description**: AI-generated ingestion pipelines for relational databases using IBM DataStage connectors with CDC support. Covers DB2, PostgreSQL, MySQL, and Oracle sources with schema mapping, validation, and error handling.

**Supported Sources**:
- IBM Db2 (on-premises and IBM Cloud)
- PostgreSQL / Amazon RDS
- MySQL / MariaDB
- Oracle Database
- Microsoft SQL Server
- IBM Db2 Warehouse on Cloud

**Key Patterns**:
- Full-load batch ingestion
- CDC (Change Data Capture) incremental sync
- Schema mapping and type conversion
- Data validation and rejection handling

---

### 2. Unstructured Data Ingestion
**Location**: `assets/unstructured-data/`
**IBM Products**: IBM UDI, IBM Docling, IBM COS, IBM Cloud IAM
**Description**: AI-generated pipelines for ingesting documents, PDFs, images, and other unstructured content using IBM Docling for parsing and IBM UDI for transport to watsonx.data.

**Supported Document Types**:
- PDF (text, tables, figures)
- DOCX / PPTX / XLSX
- HTML / Markdown
- Images (PNG, JPG, TIFF — OCR)
- Email (EML, MSG)

**Key Patterns**:
- IBM Docling parse → chunk → embed pipeline
- IBM COS → watsonx.data ingestion
- Multi-format batch processing
- Metadata extraction and enrichment

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for automated data ingestion pipeline generation
  - **Install**: copy [`bob-modes/base-modes/data-ingestion.zip`](./bob-modes/base-modes/data-ingestion.zip) to your Bob modes directory
  - Describe your data source and target → Bob generates the full pipeline
  - Covers structured (DataStage CDC) and unstructured (Docling/UDI) patterns

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `data-ingestion-structured` | [`bob-skills/data-ingestion-structured.zip`](./bob-skills/data-ingestion-structured.zip) | IBM DataStage connector config, CDC pipeline design, schema mapping, DB2/PostgreSQL/MySQL/Oracle patterns, batch and incremental load strategies |
| `data-ingestion-unstructured` | [`bob-skills/data-ingestion-unstructured.zip`](./bob-skills/data-ingestion-unstructured.zip) | IBM Docling document parsing, UDI pipeline configuration, IBM COS ingestion, multi-format chunking, metadata extraction, Python 3.12 automation scripts |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## AI-Generated Pipeline Workflow

```
1. Activate Bob Mode (data-ingestion.zip)
   │
   ▼
2. Describe your ingestion requirement:
   "Ingest customer orders from PostgreSQL into watsonx.data Iceberg table with CDC"
   │
   ▼
3. Bob generates:
   ├─ DataStage flow definition (structured)
   │   or Docling pipeline script (unstructured)
   ├─ Schema mapping configuration
   ├─ .env.example with required credentials
   ├─ Dockerfile for containerization
   └─ README with deployment instructions
```

## Architecture

```
Structured Sources                    Unstructured Sources
(DB2 / PostgreSQL / MySQL)           (COS / Email / Web)
        │                                     │
        │  DataStage CDC connectors           │  IBM Docling parse
        ▼                                     ▼
IBM DataStage                         IBM UDI
  Schema mapping                      Chunk + embed
  Validation                          Metadata extract
        │                                     │
        └──────────────┬──────────────────────┘
                       │
                       ▼
             IBM watsonx.data
           (Iceberg / COS / Db2)
```

## IBM Cloud References

- [IBM DataStage Documentation](https://www.ibm.com/docs/en/datastage)
- [IBM Docling](https://github.com/DS4SD/docling)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
