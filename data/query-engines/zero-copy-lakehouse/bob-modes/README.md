# Bob Mode for Zero-Copy Lakehouse

Custom IBM Bob mode configuration for **IBM watsonx.data** zero-copy lakehouse setup and federated analytics.

---

## Overview

This Bob mode provides specialized assistance for:

- **IBM watsonx.data Setup**: Bucket registration, database connections, Presto engine configuration via the watsonx.data REST API v2
- **Apache Iceberg**: Schema creation, table design, time-travel queries, partition strategies
- **Federated SQL**: Presto queries across IBM COS, AWS S3, Db2, and other connected sources
- **Zero-Copy Patterns**: Access data where it lives without replication
- **IBM COS Integration**: Registering COS buckets as watsonx.data managed storage

---

## What's Included

- **[`base-modes/lakehouse-setup.zip`](base-modes/lakehouse-setup.zip)**: Bob mode for watsonx.data lakehouse configuration

---

## Mode Capabilities

- IBM Cloud IAM authentication with token auto-refresh
- watsonx.data REST API v2 bucket and database registration
- Presto engine catalog association and schema creation
- Apache Iceberg table DDL and DML via Presto SQL
- Time-travel and snapshot management queries
- IBM COS HMAC credential management
- Zero-copy federated query design patterns
- Python scripting following `watsonxdata_setup.py` conventions

---

## When to Use This Mode

- Setting up IBM watsonx.data for the first time on IBM Cloud
- Registering new IBM COS buckets as watsonx.data storage
- Adding Db2, PostgreSQL, or MySQL as external database connections
- Designing Iceberg table schemas for analytical workloads
- Writing federated Presto SQL across heterogeneous data sources
- Troubleshooting watsonx.data API authentication or catalog issues
- Configuring Spark to write Iceberg tables on watsonx.data

---

## Installing Bob Modes

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/lakehouse-setup.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/lakehouse-setup.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
