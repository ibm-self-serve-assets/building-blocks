# Unstructured Data Integration (UDI)

**IBM product**: IBM watsonx.data integration — Unstructured Data Integration

Prepare unstructured enterprise content for AI and retrieval workflows: ingest documents, extract structure, enrich metadata, chunk content, and write AI-ready output to supported targets.

## Scope

Use UDI for PDFs, Office documents, HTML, images, and other unstructured content. Do not use this building block for relational CDC or batch ETL.

- Structured batch ETL/ELT → [`../etl/`](../etl/)
- Structured near-real-time replication → IBM watsonx.data integration Data Replication
- File synchronization → [`../data-sync/`](../data-sync/)

## Included assets

| Path | Purpose |
|---|---|
| [`assets/udi-ingestion-opensearch/`](assets/udi-ingestion-opensearch/) | Reference ingestion pipeline using IBM COS, UDI/document processing, IBM watsonx.ai embeddings, and an OpenSearch target |
| [`bob-modes/`](bob-modes/) | IBM Bob mode for unstructured ingestion workflows |
| [`bob-skills/data-ingestion-unstructured.zip`](bob-skills/data-ingestion-unstructured.zip) | IBM Bob skill for UDI/document processing |
| [`bob-skills/udi-opensearch.zip`](bob-skills/udi-opensearch.zip) | IBM Bob skill for the OpenSearch-target reference pattern |

## Model defaults

The reference asset currently uses:

```text
ibm/granite-embedding-278m-multilingual
```

The model is configurable. Verify current model availability and dimensions before deployment:

- Supported IBM embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Foundation model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

## IBM references

- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- watsonx.data integration documentation: https://www.ibm.com/docs/en/software-hub/5.4.x?topic=services-watsonxdata-integration
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
- IBM Cloud Object Storage: https://cloud.ibm.com/docs/cloud-object-storage
