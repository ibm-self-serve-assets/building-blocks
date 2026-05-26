# IBM UDI (Unstructured Data Ingestion)

IBM Unstructured Data Ingestion service for processing and ingesting unstructured data into IBM watsonx.data.

## Overview

IBM UDI enables automated ingestion of unstructured data from various sources including documents, images, emails, and web content.

## Prerequisites

1. IBM watsonx.data instance
2. IBM Cloud Object Storage (COS) for staging
3. IBM Cloud API Key
4. Python 3.12+

## Getting Started

### Installation

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Configuration

Copy the environment template and configure your credentials:

```powershell
cp env .env
```

Required environment variables:
- `WATSONX_DATA_URL`: watsonx.data instance URL
- `WATSONX_APIKEY`: IBM Cloud API Key
- `COS_ENDPOINT`: IBM COS endpoint
- `COS_BUCKET`: Target bucket name
- `COS_API_KEY`: IBM COS API Key

### Usage

```python
from udi_client import UDIClient

# Initialize client
client = UDIClient()

# Ingest documents
client.ingest_documents(
    source_path="./documents",
    target_catalog="udi_catalog"
)
```

## Supported Formats

- **Documents**: PDF, DOCX, TXT, HTML, Markdown
- **Images**: JPG, PNG, TIFF (with OCR)
- **Archives**: ZIP, TAR, GZ
- **Email**: MSG, EML, MBOX
- **Web**: HTML, XML

## Features

- Automatic format detection
- Metadata extraction
- Text extraction and OCR
- Batch processing
- Error handling and retry logic
- Progress tracking

## Documentation

For detailed documentation, refer to:
- [IBM watsonx.data UDI Documentation](https://www.ibm.com/docs/en/watsonxdata)
- [IBM Cloud Object Storage Documentation](https://cloud.ibm.com/docs/cloud-object-storage)