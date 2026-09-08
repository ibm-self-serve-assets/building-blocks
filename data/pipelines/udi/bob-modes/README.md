# Bob Mode for Data Ingestion

Custom IBM Bob mode configuration for AI-generated data ingestion pipelines using **IBM DataStage**, **IBM UDI (Unstructured Data Integration)**, and **IBM Docling** on IBM Cloud.

---

## Overview

This Bob mode provides specialized assistance for:

- **AI-Generated Pipelines**: Describe your ingestion requirement and Bob generates the full DataStage flow or Python ingestion script
- **Structured Data Ingestion**: IBM DataStage connector configuration for DB2, PostgreSQL, MySQL, Oracle, and SQL Server with CDC support
- **Unstructured Data Ingestion**: IBM Docling + UDI pipeline design for PDFs, DOCX, HTML, images, and email
- **IBM COS Integration**: Source document download via `ibm-cos-sdk` and target data archiving
- **Schema Mapping**: Source-to-target type conversion and Iceberg schema design

---

## What's Included

- **[`base-modes/data-ingestion.zip`](base-modes/data-ingestion.zip)**: Bob mode configuration for AI-generated data ingestion development

---

## Mode Capabilities

- IBM Cloud IAM authentication with automatic token refresh
- IBM DataStage batch and parallel job flow generation
- IBM Data Replication CDC (Change Data Capture) log-mining setup
- Schema mapping to Apache Iceberg data types
- IBM UDI (Unstructured Data Integration) DataStage connector configuration
- IBM Docling PDF and DOCX parsing with structure and table preservation
- `unstructured` library multi-format document parsing (HTML, PPTX, Excel, email)
- OCR configuration for scanned PDFs and image-based documents
- IBM COS source integration with `ibm-cos-sdk` IAM OAuth
- Chunking strategy selection: fixed-size, semantic, sentence-based
- Metadata extraction design (title, source, page number, chunk_seq)
- `.env.example` and `requirements.txt` generation following building-blocks conventions
- Docker containerization for IBM Code Engine deployment

---

## When to Use This Mode

- Generating a new IBM DataStage ingestion pipeline from a plain-English description
- Configuring CDC (Change Data Capture) from IBM Db2, PostgreSQL, or Oracle
- Building document ingestion pipelines with IBM Docling for AI workloads
- Designing schema mappings from relational sources to Apache Iceberg
- Troubleshooting IBM DataStage connector or UDI configuration issues
- Implementing batch or incremental ingestion with validation and error handling
- Setting up IBM COS as a document source for unstructured ingestion

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/data-ingestion.zip`](base-modes/data-ingestion.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with data ingestion tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/data-ingestion.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/data-ingestion.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.
