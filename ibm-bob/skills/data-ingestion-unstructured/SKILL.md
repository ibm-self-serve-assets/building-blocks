---
name: data-ingestion-unstructured
description: Expert guidance for IBM UDI (Unstructured Data Ingestion) and IBM Docling-based pipeline design — covers PDF, DOCX, HTML, image (OCR) parsing, IBM COS document source, watsonx.data target, metadata extraction, chunking strategy selection, and IBM Cloud IAM authentication. Generates production-ready Python 3.12 ingestion scripts.
---

# IBM Unstructured Data Ingestion Builder

## Purpose

Expert guidance for building **unstructured data ingestion pipelines** using **IBM UDI (Unstructured Data Ingestion)** and **IBM Docling** — processing documents (PDF, DOCX, HTML, images) from **IBM COS** into **IBM watsonx.data** vector storage.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| IBM UDI (Unstructured Data Integration) | DataStage-based unstructured document processing |
| IBM watsonx.data | Target: Iceberg tables for metadata; Milvus/OpenSearch for vectors |
| IBM Cloud Object Storage | Source document storage |
| IBM watsonx.ai | Embedding generation for vectorised chunks |
| IBM Cloud IAM | POST /identity/token (apikey grant) |

## Rules

- Use `docling` for high-quality PDF/DOCX parsing (IBM's document AI library)
- Use `unstructured` as fallback for broad format support (HTML, PPTX, email)
- IBM UDI via DataStage: use `IBM.UDI` connector in DataStage job definition
- Chunking: `RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)` for RAG
- Always extract title, source path, page number, and chunk_seq as metadata
- COS download: always use `ibm-cos-sdk` with IAM OAuth (not HMAC) in Python

---

## Scope

- IBM UDI DataStage connector configuration
- IBM Docling document parsing (PDF, DOCX, images)
- unstructured.io multi-format parsing (HTML, PPTX, email, Excel)
- OCR for scanned PDFs and image-based documents
- Chunking strategies: fixed-size, semantic, sentence-based
- Metadata extraction and enrichment
- IBM COS to watsonx.data pipeline patterns

---

## Procedure

### Phase 1: IBM Docling PDF Parsing

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert(cos_local_path)
doc = result.document

# Extract text preserving document structure
markdown_text = doc.export_to_markdown()
# or JSON structure
json_doc = doc.export_to_dict()
```

### Phase 2: IBM COS Document Download

```python
import ibm_boto3
from ibm_botocore.client import Config

cos = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY,
    ibm_service_instance_id=COS_INSTANCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT,
)
cos.download_file(bucket, key, local_path)
```

### Phase 3: Chunking Strategy Selection

| Strategy | Use Case | Config |
|---|---|---|
| Fixed-size | General RAG | `chunk_size=512, chunk_overlap=128` |
| Sentence-based | Q&A systems | `nltk.sent_tokenize` + grouping |
| Semantic | High-precision retrieval | `SemanticChunker(embeddings)` |
| Hierarchical | Document structure preservation | Docling section boundaries |

### Phase 4: Metadata Extraction

```python
metadata = {
    "title": os.path.basename(file_path),
    "source": cos_key,
    "document_url": f"cos://{bucket}/{cos_key}",
    "page_number": str(page_num),
    "chunk_seq": chunk_index,
    "file_type": file_extension,
    "ingested_at": datetime.now(timezone.utc).isoformat(),
}
```

### Phase 5: IBM UDI DataStage Connector

IBM UDI exposes a DataStage connector called `IBM.UDI` that:
- Reads from IBM COS (`source_type: ibm_cos`)
- Extracts text and metadata from unstructured documents
- Outputs tabular records with: `document_id`, `text`, `metadata_json`

```json
{
  "stage_type": "IBM.UDI",
  "properties": {
    "source_type": "ibm_cos",
    "cos_endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
    "cos_bucket": "my-docs",
    "cos_prefix": "documents/",
    "output_format": "chunks",
    "chunk_size": 512,
    "chunk_overlap": 128
  }
}
```

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
| IBM DataStage REST API | `https://api.us-south.dataplatform.cloud.ibm.com/v3/data_intg_flows` |
| IBM watsonx.ai (us-south) | `https://us-south.ml.cloud.ibm.com` |
