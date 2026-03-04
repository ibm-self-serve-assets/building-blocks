# Semi-Structured Data Ingestion

Ingest semi-structured data formats (JSON, XML, CSV, logs) into IBM watsonx.data.

## Overview

Semi-structured data ingestion enables processing and loading of JSON, XML, CSV, log files, and API responses into watsonx.data with automatic schema inference and data transformation.

## Prerequisites

1. IBM watsonx.data instance
2. IBM Cloud Object Storage (COS) or local file access
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
- `COS_ENDPOINT`: IBM COS endpoint (if using COS)
- `COS_BUCKET`: Source bucket name
- `COS_API_KEY`: IBM COS API Key

### Usage

#### JSON Ingestion

```python
from semi_structured_ingestion import JSONIngestion

# Initialize ingestion
ingestion = JSONIngestion()

# Ingest JSON files
ingestion.ingest_json(
    source_path="s3://bucket/data/*.json",
    target_catalog="iceberg_data",
    target_table="events"
)
```

#### CSV Ingestion

```python
from semi_structured_ingestion import CSVIngestion

# Initialize ingestion
ingestion = CSVIngestion()

# Ingest CSV files
ingestion.ingest_csv(
    source_path="./data/sales.csv",
    target_catalog="iceberg_data",
    target_table="sales_data",
    delimiter=",",
    header=True
)
```

#### Log File Ingestion

```python
from semi_structured_ingestion import LogIngestion

# Initialize ingestion
ingestion = LogIngestion()

# Ingest log files
ingestion.ingest_logs(
    source_path="./logs/*.log",
    target_catalog="iceberg_data",
    target_table="application_logs",
    log_format="apache"
)
```

## Supported Formats

- **JSON**: Single and multi-line JSON, JSONL, NDJSON
- **XML**: Well-formed XML documents
- **CSV/TSV**: Delimited text files with various separators
- **Parquet**: Columnar format
- **Avro**: Binary serialization format
- **Log Files**: Apache, Nginx, application logs
- **API Responses**: REST API JSON/XML responses

## Features

- Automatic schema inference
- Nested structure flattening
- Data type detection
- Custom transformations
- Batch and streaming processing
- Error handling and validation
- Compression support (gzip, bzip2, snappy)
- Partitioning strategies

## Documentation

For detailed documentation, refer to:
- [IBM watsonx.data Documentation](https://www.ibm.com/docs/en/watsonxdata)
- [Data Format Support](https://www.ibm.com/docs/en/watsonxdata/formats)