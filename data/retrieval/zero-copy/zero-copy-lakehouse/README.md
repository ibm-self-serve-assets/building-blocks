# Zero-Copy Lakehouse

**Core Capability**: Retrieval
**IBM Products**: IBM watsonx.data
**Product Components**: Apache Iceberg; Delta Lake; Presto SQL engine; Apache Spark; IBM COS; IBM Db2; watsonx.data REST API v2

## Overview

Enable seamless federated analytics across databases, warehouses, and cloud object stores **without data duplication** using **IBM watsonx.data**. Register storage buckets and databases once, associate them with a Presto engine, and query across all sources using standard SQL — powered by open lakehouse formats including **Apache Iceberg** and **Delta Lake**.

## Building Blocks

### 1. Setup Lakehouse
**Location**: `assets/setup-lakehouse/`
**IBM Products**: IBM watsonx.data, IBM COS, IBM Db2, IBM Cloud IAM
**Description**: Python 3.12 automation script that provisions a complete watsonx.data environment — registers COS and S3 buckets, connects Db2 databases, associates Presto engine catalogs, creates Iceberg schemas, and loads sample data.

**Quick Start**:
```bash
cd assets/setup-lakehouse
# Edit config.json with your watsonx.data CRN, IBM Cloud API key, COS and Db2 credentials
python watsonxdata_setup.py
```

**What it provisions**:
- IBM COS bucket → registered as watsonx.data managed storage
- AWS S3 bucket (optional) → registered as external storage
- IBM Db2 database → registered as external database connection
- Presto engine catalog association
- Iceberg schema creation
- Sample data load (`account.csv`, `customer.csv`, `customer_summary.csv`)

**Sample Federated Queries**:
```sql
-- Query Iceberg table on COS
SELECT * FROM iceberg_data.sales_schema.customer LIMIT 10;

-- Join COS Iceberg table with Db2 table (zero-copy)
SELECT c.customer_id, c.name, a.balance
FROM iceberg_data.sales_schema.customer c
JOIN db2_catalog.finance_schema.accounts a
ON c.customer_id = a.customer_id
WHERE a.balance > 10000;
```

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for watsonx.data lakehouse setup, Iceberg design, and federated SQL
  - **Install**: copy [`bob-modes/base-modes/lakehouse-setup.zip`](./bob-modes/base-modes/lakehouse-setup.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `watsonxdata-lakehouse` | [`bob-skills/watsonxdata-lakehouse.zip`](./bob-skills/watsonxdata-lakehouse.zip) | watsonx.data REST API v2 bucket/database registration, Presto catalog association, Iceberg schema creation, federated SQL, `AuthInstanceId` CRN header patterns |
| `iceberg-table-management` | [`bob-skills/iceberg-table-management.zip`](./bob-skills/iceberg-table-management.zip) | Iceberg DDL with partition strategies, MERGE INTO upserts, time-travel queries, snapshot management, schema evolution, compaction via Presto procedures |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Supported Data Sources

| Source Type | Registration Method | Catalog Type |
|---|---|---|
| IBM Cloud Object Storage | `POST /bucket_registrations` | Iceberg / Hive |
| AWS S3 | `POST /bucket_registrations` | Iceberg / Hive |
| Azure ADLS Gen2 | `POST /bucket_registrations` | Iceberg |
| IBM Db2 | `POST /database_registrations` | External |
| PostgreSQL | `POST /database_registrations` | External |
| MySQL | `POST /database_registrations` | External |

## Architecture

```
IBM COS / AWS S3 / Azure ADLS
        │
        │  bucket_registrations (REST API v2)
        ▼
IBM watsonx.data
  Iceberg Catalog (open table format)
        │
        │  presto_engines/{id}/catalogs association
        ▼
Presto Query Engine
  Federated SQL across all registered sources
        │
        ▼
IBM Db2 / PostgreSQL / MySQL
  (external database_registrations)
```

## Watsonx.data Regions

| Region | Base URL |
|---|---|
| us-south (Dallas) | `https://us-south.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| eu-de (Frankfurt) | `https://eu-de.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| au-syd (Sydney) | `https://au-syd.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| jp-tok (Tokyo) | `https://jp-tok.lakehouse.cloud.ibm.com/lakehouse/api/v2` |

## IBM Cloud References

- [IBM watsonx.data on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/lakehouse)
- [IBM watsonx.data REST API v2 Reference](https://cloud.ibm.com/apidocs/watsonxdata)
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
