# Unstructured Data Integration (UDI)

**IBM product**: IBM watsonx.data integration — Unstructured Data Integration

Use UDI to ingest and prepare **documents and other unstructured enterprise content** for retrieval, search, analytics, and AI.

## What UDI does

A typical UDI flow can:

- ingest documents from supported sources;
- extract text/structure;
- apply document processing/OCR where required;
- chunk content;
- enrich metadata;
- create AI-ready output for search/RAG targets.

Current IBM releases also add capabilities such as semantic chunking and AI-assisted chunk summarization; verify the target watsonx.data integration / data intelligence version before relying on a feature.

## Architecture for the included reference asset

```text
IBM Cloud Object Storage
        |
        v
watsonx UDI document flow
 extract -> transform -> chunk -> enrich
        |
        v
   IBM watsonx.ai
      embeddings
        |
        v
     OpenSearch
 searchable chunks + vectors
```

OpenSearch is an implementation target in the included asset; the UDI product anchor is IBM watsonx.data integration.

## Scope boundaries

- Structured batch ETL/ELT -> [`../etl/`](../etl/)
- Structured near-real-time database replication -> IBM watsonx.data integration Data Replication
- File/directory synchronization -> [`../data-sync/`](../data-sync/)

## Included assets

| Path | Purpose |
|---|---|
| [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/) | COS -> UDI/document processing -> watsonx.ai embeddings -> OpenSearch |
| [`bob-modes/`](bob-modes/) | IBM Bob ingestion mode |
| [`bob-skills/data-ingestion-unstructured.zip`](bob-skills/data-ingestion-unstructured.zip) | Bob skill for UDI/document ingestion |
| [`bob-skills/udi-opensearch.zip`](bob-skills/udi-opensearch.zip) | Bob skill for the UDI + OpenSearch reference flow |
| [`bob-skills/data-ingestion-structured.zip`](bob-skills/data-ingestion-structured.zip) | Structured-ingestion companion guidance retained in the existing hierarchy; it is **not UDI** |

## Quick start

Start with the reference asset:

```bash
cd assets/udi-ingestion-opensearch
cp scripts/.env.example scripts/.env
# Populate the IBM Cloud, project, COS, and target credentials described in the asset README.
pip install -r requirements.txt
python scripts/setup.py
python scripts/ingest.py
```

Read [`assets/udi-ingestion-opensearch/README.md`](assets/udi-ingestion-opensearch/README.md) first. It documents required IBM services, COS HMAC credentials, input folder layout, generated resources, and troubleshooting.

## Model default

```text
ibm/granite-embedding-278m-multilingual
```

The model is configurable. Verify current support and dimensions:

- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Foundation model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

## Production checklist

- Verify supported UDI operators and file types for the target deployment.
- Keep COS and target credentials outside source control.
- Confirm OCR/document-processing service prerequisites before running.
- Define chunking based on retrieval use case, not only document size.
- Preserve source/document identifiers in metadata for traceability.
- Verify downstream index mapping when changing embedding models.

## IBM references

- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- watsonx.data intelligence / UDI updates: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=new-watsonxdata-intelligence
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
- IBM Cloud Object Storage: https://cloud.ibm.com/docs/cloud-object-storage
