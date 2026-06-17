# Zero Copy

**Core Capability**: Retrieval
**IBM Products**: IBM watsonx.data
**Product Components**: Apache Iceberg; Delta Lake; Presto SQL engine; Apache Spark; IBM COS; IBM Db2; watsonx.data REST API v2

## Overview

Federated analytics without copying data. Query across IBM COS, AWS S3, IBM Db2, PostgreSQL, and MySQL from a single **Presto** engine using open lakehouse formats — **Apache Iceberg** and **Delta Lake** — all via **IBM watsonx.data** — without data duplication.

---

## When to Use

| Scenario | Notes |
|---|---|
| Query data in IBM COS or S3 with SQL — without moving or copying it | Core use case — register bucket, query via Presto |
| Join tables from Db2 and S3 in a single SQL query | Federated join across registered sources |
| Need open lakehouse table format with time-travel, schema evolution, and compaction | Use Apache Iceberg tables |
| Need Delta Lake table compatibility (Databricks workloads) | Delta Lake is supported alongside Iceberg |
| Provision a complete watsonx.data environment from code | Use the `setup-lakehouse` automation script |

---

## Getting Started

### Prerequisites

- **IBM watsonx.data** instance — note your CRN and instance URL
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.12+**
- (Optional) IBM COS bucket, IBM Db2 credentials for registration

### Quick Start

```bash
cd zero-copy-lakehouse/assets/setup-lakehouse
# Edit config.json: watsonx.data CRN, IBM_API_KEY, COS credentials, Db2 credentials
python watsonxdata_setup.py
```

This provisions:
- IBM COS bucket → registered as watsonx.data managed storage
- Presto engine catalog association
- Iceberg schema + sample tables

Then run a federated query:
```sql
-- In the watsonx.data Presto console or via the REST API
SELECT * FROM iceberg_data.sales_schema.customer LIMIT 10;
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Zero Copy building block ships a **Bob Mode** and **two Bob Skills** that give Bob expert knowledge of the watsonx.data REST API v2, Iceberg DDL/DML, Delta Lake patterns, and federated SQL across registered sources.

**Install the Bob Mode** — give Bob a lakehouse specialist persona:
```powershell
# Windows
Copy-Item zero-copy-lakehouse/bob-modes/base-modes/lakehouse-setup.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp zero-copy-lakehouse/bob-modes/base-modes/lakehouse-setup.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Lakehouse Setup** mode appears in the mode selector.

**Install Bob Skills** — teach Bob the watsonx.data and Iceberg details:
```bash
unzip zero-copy-lakehouse/bob-skills/watsonxdata-lakehouse.zip
unzip zero-copy-lakehouse/bob-skills/iceberg-table-management.zip
```
Open IBM Bob → Skills panel → enable both skills. Bob will use them as active context for every prompt in this workspace.

---

## Building Blocks

### Zero-Copy Lakehouse
**Location**: [`zero-copy-lakehouse/`](zero-copy-lakehouse/)
**IBM Products**: IBM watsonx.data (Apache Iceberg + Presto), IBM COS, IBM Db2
**Description**: Complete zero-copy lakehouse implementation — Python automation script for watsonx.data environment provisioning, federated SQL patterns, and Iceberg table lifecycle management.

**Quick Start**:
```bash
cd zero-copy-lakehouse/assets/setup-lakehouse
# Edit config.json with your watsonx.data CRN, IBM Cloud API key, COS and Db2 credentials
python watsonxdata_setup.py
```

**What it provisions**:
- IBM COS bucket → watsonx.data managed storage
- AWS S3 bucket (optional) → external storage
- IBM Db2 → external database connection
- Presto engine catalog association
- Iceberg schema + table creation
- Sample data load

**Bob Assets**:
- `bob-modes/base-modes/lakehouse-setup.zip` — Lakehouse setup and federated SQL mode
- `bob-skills/watsonxdata-lakehouse.zip` — watsonx.data REST API v2 provisioning skill
- `bob-skills/iceberg-table-management.zip` — Iceberg DDL, DML, time-travel, compaction skill

[View Details →](zero-copy-lakehouse/)

---

## IBM Cloud References

- [IBM watsonx.data on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/lakehouse)
- [IBM watsonx.data REST API v2 Reference](https://cloud.ibm.com/apidocs/watsonxdata)
- [Apache Iceberg Documentation](https://iceberg.apache.org/docs/latest/)
- [IBM Cloud Object Storage](https://cloud.ibm.com/docs/cloud-object-storage)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
