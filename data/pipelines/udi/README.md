# UDI — Unstructured Data Integration

**Core Capability**: Pipelines
**IBM Products**: IBM watsonx.data integration (Unstructured Data Integration), Docling for IBM watsonx
**Product Components**: IBM watsonx.data integration UDI visual flow designer; Docling document conversion; document chunking and enrichment stages; IBM COS

## What Is This Building Block?

**Unstructured Data Integration (UDI)** is the capability within IBM watsonx.data integration for ingesting, parsing, chunking, enriching and preparing **unstructured documents** — PDFs, presentations, DOCX files, HTML, scanned images — for downstream AI, RAG and search use cases.

UDI provides a visual, drag-and-drop flow experience with pre-built stages for document ingestion, OCR-based extraction, chunking and vector embedding. Flows can be scheduled so that only changed documents are processed. **Docling for IBM watsonx** converts complex documents into structured AI-ready output (Markdown, JSON, HTML), preserving tables, reading order and multi-column layouts.

> Enterprise knowledge is locked in PDFs, presentations and contracts. Poor document preparation is the leading cause of poor RAG quality. UDI and Docling address this directly by providing governed, repeatable document pipelines.

> **Scope note**: UDI covers unstructured document integration only. For structured relational database batch integration, see the **[ETL / ELT](../etl/README.md)** building block (IBM DataStage). For high-speed file/directory synchronization across WAN, see **[Data Sync](../data-sync/README.md)**. For near-real-time structured database replication via CDC, see the Data Replication capability note below.

---

## What Problem Does It Solve?

Raw documents in object storage — PDFs, DOCX, PPTX, HTML — are not directly usable by search systems or language models. UDI solves the document-to-AI-ready pipeline problem by:

- Extracting text and structure from complex document formats (including scanned PDFs)
- Chunking text into retrieval-optimized segments
- Generating dense embeddings for vector similarity search
- Indexing prepared chunks into a vector store (OpenSearch)
- Enriching chunks with document-level metadata for governance and filtering

---

## When to Use

| Scenario | Approach |
|---|---|
| Ingest PDFs, DOCX, HTML, images, or presentations into an AI or RAG pipeline | Use IBM watsonx.data integration UDI visual flow |
| Complex documents with tables, scanned pages, or multi-column layouts | Use Docling for IBM watsonx for high-quality extraction |
| Build a repeatable pipeline for continuously updated document sources in IBM COS | Schedule a UDI flow to detect and process only changed documents |
| Route prepared documents into OpenSearch for vector similarity search | [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/README.md) |
| Use Bob to design a document pipeline from a plain-English description | Activate the **UDI Unstructured Ingestion** Bob Skill |

## When NOT to Use

| Scenario | Use Instead |
|---|---|
| Structured relational database batch ingestion (Db2, PostgreSQL, MySQL, Oracle) | [`../etl/`](../etl/README.md) — IBM DataStage |
| Near-real-time structured database replication via CDC | See Data Replication note below |
| High-speed WAN file/directory synchronization | [`../data-sync/`](../data-sync/README.md) — IBM Aspera Sync |
| Streaming event ingestion | [`../../context/real-time-streaming/`](../../context/real-time-streaming/README.md) — IBM Confluent |

---

## Data Replication Note

IBM watsonx.data integration includes a **Data Replication** capability for near-real-time structured database replication using Change Data Capture (CDC). This is separate from UDI and from batch ETL. CDC-based replication — where changes in a source relational database (inserts, updates, deletes) are captured from transaction logs and replicated to a target — is not an unstructured integration pattern and is not part of this building block. If your requirement is structured CDC replication, evaluate the Data Replication capability within IBM watsonx.data integration directly.

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM watsonx.ai project** — houses the UDI flow and connections
- **Watson Machine Learning (WML) instance** — required for the OCR extraction step; must be active and linked to your watsonx.ai project
- **IBM Cloud Object Storage** instance and bucket — holds source documents
- **OpenSearch instance** — receives indexed chunks and vectors (IBM watsonx.data managed OpenSearch, or self-managed)
- **Python 3.12+** (for the automation scripts)

### Quick Start — UDI + OpenSearch Ingestion

```bash
cd assets/udi-ingestion-opensearch
cp scripts/.env.example scripts/.env
# Edit scripts/.env: IBM_CLOUD_API_KEY, PROJECT_ID, COS_BUCKET, COS_ENDPOINT,
#   COS_ACCESS_KEY, COS_SECRET_KEY, OPENSEARCH_HOST, OPENSEARCH_USERNAME, OPENSEARCH_PASSWORD
pip install -r scripts/requirements.txt

# Step 1: Provision connections and create the UDI flow (run once)
python scripts/setup.py

# Step 2: Run the ingestion (run on demand or on schedule)
python scripts/ingest.py
```

Full instructions, troubleshooting and optional settings are in the [asset README](assets/udi-ingestion-opensearch/README.md).

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The UDI building block ships a **Bob Mode** and **Bob Skills** for document pipeline design.

**Install the Bob Mode** — give Bob an Unstructured Data Integration specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/data-ingestion.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/data-ingestion.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Data Ingestion** mode appears in the mode selector.

**Install the unstructured Bob Skill**:
```bash
unzip bob-skills/data-ingestion-unstructured.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## Building Block

### UDI Document Ingestion — COS to OpenSearch

**Location**: [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/README.md)
**IBM Products**: IBM watsonx.data integration (UDI), IBM watsonx.ai (WML for OCR), IBM COS
**Description**: Two-part Python pipeline that registers connections, creates a UDI flow in watsonx.ai, and runs document ingestion from an IBM COS bucket into an OpenSearch index. Documents are extracted (with OCR where needed), chunked and embedded using the configured watsonx embedding model.

**Supported Document Types**:

| Format | Handling |
|---|---|
| `.pdf` | Text extraction + OCR via WML |
| `.docx`, `.doc` | Native text extraction |
| `.pptx`, `.ppt` | Slide text extraction |
| `.xlsx` | Tabular text extraction |
| `.html` | HTML text extraction |
| `.md`, `.txt` | Plain text |

**Key Pipeline Stages**:

```
IBM COS bucket (source documents)
        │
        │  UDI flow — ingest_cpd_connections
        ▼
extract_cpd  — OCR + text extraction (requires active WML instance)
        │
        ▼
chunker  — splits text into configurable chunks (default: 4000 tokens, 200 overlap)
        │
        ▼
embeddings  — 384-dim vectors (default: ibm/slate-30m-english-rtrvr-v2)
        │
        ▼
OpenSearch index  — udi_opensearch_index
  { text, vector_index, document_name, document_id, pk }
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for unstructured document ingestion pipeline design and UDI configuration
  - **Install**: copy [`bob-modes/base-modes/data-ingestion.zip`](./bob-modes/base-modes/data-ingestion.zip) to your Bob modes directory
  - Describe your document source and target → Bob assists with UDI flow design and Docling pipeline configuration

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `data-ingestion-unstructured` | [`bob-skills/data-ingestion-unstructured.zip`](./bob-skills/data-ingestion-unstructured.zip) | IBM UDI flow configuration, IBM Docling document parsing, IBM COS ingestion, multi-format chunking, metadata extraction, watsonx.ai embedding generation |
| `udi-opensearch` | [`bob-skills/udi-opensearch.zip`](./bob-skills/udi-opensearch.zip) | UDI + OpenSearch ingestion pipeline setup, connection registration, flow creation and execution via Watson Data API |

> **Note**: The `data-ingestion-structured.zip` skill (covering IBM DataStage batch patterns) is also present in the `bob-skills/` directory. That skill relates to structured ETL via DataStage and is better used alongside the **[ETL / ELT](../etl/README.md)** building block, not this one.

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM watsonx.data integration — UDI](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integration)** | Visual unstructured data integration flow designer; OCR extraction; chunking; embedding; COS and OpenSearch connectors |
| **[Docling for IBM watsonx](https://github.com/DS4SD/docling)** | High-quality document conversion — preserves tables, reading order, multi-column layouts in complex PDFs |
| **[IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)** | Document source for UDI flows |
| **[Watson Machine Learning](https://cloud.ibm.com/catalog/services/watson-machine-learning)** | Powers OCR extraction in UDI flows — must be active and linked to the watsonx.ai project |

---

## What Assets Are Included

| Asset | Type | Description |
|---|---|---|
| [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/) | Runnable Python pipeline | COS → UDI flow → OpenSearch ingestion with full setup and ingest scripts |
| [`bob-modes/base-modes/data-ingestion.zip`](bob-modes/base-modes/data-ingestion.zip) | Bob Mode | Unstructured data ingestion specialist persona |
| [`bob-skills/data-ingestion-unstructured.zip`](bob-skills/data-ingestion-unstructured.zip) | Bob Skill | UDI / Docling pipeline knowledge |
| [`bob-skills/udi-opensearch.zip`](bob-skills/udi-opensearch.zip) | Bob Skill | UDI + OpenSearch integration patterns |

---

## IBM Cloud References

- [IBM watsonx.data integration — UDI](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integration)
- [IBM UDI SDK on PyPI](https://pypi.org/project/ibm-udi/)
- [Docling for IBM watsonx on GitHub](https://github.com/DS4SD/docling)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM watsonx.data Documentation](https://cloud.ibm.com/docs/watsonxdata)
- [Watson Machine Learning](https://cloud.ibm.com/catalog/services/watson-machine-learning)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
