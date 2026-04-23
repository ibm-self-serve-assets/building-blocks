# Structured Data Ingestion

Ingest structured data from relational databases and data warehouses into IBM watsonx.data.

## Overview

Structured data ingestion enables automated data movement from RDBMS sources to watsonx.data with support for batch, streaming, and CDC (Change Data Capture) patterns.

## Prerequisites

1. IBM watsonx.data instance
2. Source database credentials
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
- `SOURCE_DB_TYPE`: Database type (db2, postgresql, mysql, oracle)
- `SOURCE_DB_HOST`: Source database host
- `SOURCE_DB_PORT`: Source database port
- `SOURCE_DB_NAME`: Source database name
- `SOURCE_DB_USER`: Source database username
- `SOURCE_DB_PASSWORD`: Source database password

### Usage

#### Batch Ingestion

```python
from structured_ingestion import BatchIngestion

# Initialize ingestion
ingestion = BatchIngestion()

# Ingest table
ingestion.ingest_table(
    source_table="customers",
    target_catalog="iceberg_data",
    target_schema="sales"
)
```

#### CDC (Change Data Capture)

```python
from structured_ingestion import CDCIngestion

# Initialize CDC
cdc = CDCIngestion()

# Start CDC pipeline
cdc.start_capture(
    source_tables=["orders", "customers"],
    target_catalog="iceberg_data"
)
```

## Supported Databases

- **IBM DB2**: On-premises and cloud
- **PostgreSQL**: 12+
- **MySQL**: 8.0+
- **Oracle**: 19c+
- **Microsoft SQL Server**: 2019+
- **Amazon Redshift**
- **Snowflake**

## Features

- Full and incremental loads
- CDC with minimal latency
- Schema evolution handling
- Data type mapping
- Parallel processing
- Error handling and recovery
- Performance monitoring
- Data validation

## Documentation

For detailed documentation, refer to:
- [IBM watsonx.data Documentation](https://www.ibm.com/docs/en/watsonxdata)
- [Database Connector Configuration](https://www.ibm.com/docs/en/watsonxdata/connectors)