# Bob Mode for UDI — Unstructured Data Integration

Custom IBM Bob mode configuration for **unstructured document ingestion** using **IBM UDI (Unstructured Data Integration)** and **IBM Docling** on IBM Cloud.

> **Scope note**: This mode focuses on unstructured document ingestion (PDFs, DOCX, HTML, images). For structured relational database batch integration patterns, use the ETL/ELT building block's Bob Mode instead.

---

## Overview

This Bob mode provides specialized assistance for:

- **Unstructured Data Ingestion**: IBM UDI visual flow configuration and IBM Docling document pipeline design for PDFs, DOCX, HTML, images
- **IBM COS Integration**: Source document download from IBM COS via HMAC credentials
- **Watson Data API**: Connection registration, UDI flow creation, job execution
- **Document Processing**: Chunking strategy design, embedding generation, metadata extraction
- **OpenSearch Indexing**: Preparing and indexing document chunks for vector search and RAG

---

## What's Included

- **[`base-modes/data-ingestion.zip`](base-modes/data-ingestion.zip)**: Bob mode configuration for UDI unstructured document ingestion development

---

## Mode Capabilities

- IBM Cloud IAM authentication (API key → bearer token)
- IBM watsonx.ai project setup for UDI flows
- Watson Machine Learning instance activation (required for OCR extraction)
- IBM UDI (Unstructured Data Integration) flow configuration via Watson Data API
- IBM Docling PDF and DOCX parsing with structure and table preservation
- OCR configuration for scanned PDFs and image-based documents
- IBM COS source integration with HMAC credentials
- Chunking strategy selection: fixed-size, semantic, sentence-based
- IBM watsonx.ai embedding generation for vectorised chunks
- OpenSearch target index configuration and vector ingestion
- Metadata extraction design (document_name, document_id, chunk hash)
- `.env.example` generation following building-blocks conventions
- Troubleshooting UDI flow failures and WML instance status errors

---

## When to Use This Mode

- Configuring an IBM UDI flow to ingest documents from IBM COS into OpenSearch
- Building document parsing pipelines with IBM Docling for AI/RAG workloads
- Setting up WML instance linkage and OCR extraction for UDI flows
- Designing chunking strategies and embedding configurations for document content
- Troubleshooting UDI flow configuration, connection registration, or OCR failures

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/data-ingestion.zip`](base-modes/data-ingestion.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with UDI unstructured data integration tasks.

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
