# Zero-Copy Lakehouse Bob Skills

Bob skills for **IBM watsonx.data** zero-copy lakehouse configuration and **Apache Iceberg** table lifecycle management.

## Overview

These skills empower IBM Bob to configure IBM watsonx.data as a zero-copy lakehouse (registering buckets, connecting databases, associating catalogs) and to manage Apache Iceberg table lifecycles — from DDL design through DML, time-travel, schema evolution, and compaction.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `watsonxdata-lakehouse` | [`watsonxdata-lakehouse.zip`](watsonxdata-lakehouse.zip) | Configuring IBM watsonx.data: registering COS/S3 buckets, database connections, Presto catalog association |
| `iceberg-table-management` | [`iceberg-table-management.zip`](iceberg-table-management.zip) | Apache Iceberg table DDL, DML, time-travel, compaction, schema evolution on IBM watsonx.data |

---

### `watsonxdata-lakehouse`

A comprehensive skill for configuring IBM watsonx.data as a zero-copy lakehouse:

- IBM Cloud IAM authentication with automatic token refresh (`IAMTokenManager`)
- IBM watsonx.data REST API v2 bucket registration (IBM COS, AWS S3, Azure ADLS)
- External database registration (IBM Db2, PostgreSQL, MySQL) via `/database_registrations`
- Presto engine catalog association via `/presto_engines/{id}/catalogs`
- Apache Iceberg schema and table creation via Presto SQL
- Federated query design across heterogeneous data sources without data copying
- `watsonxdata_setup.py` script patterns following building-blocks conventions
- `AuthInstanceId` (CRN) header management for all watsonx.data API calls

### `iceberg-table-management`

A comprehensive skill for Apache Iceberg table lifecycle management:

- Iceberg table DDL with partition strategy design (`day()`, `month()`, `bucket()`, `truncate()`)
- DML patterns: INSERT INTO, MERGE INTO (upsert), DELETE, UPDATE via Presto SQL
- Time-travel queries using `FOR VERSION AS OF` (snapshot ID) and `FOR TIMESTAMP AS OF`
- Snapshot management: `expire_snapshots`, rollback, cherry-pick via Presto procedures
- Schema evolution: add/rename/drop columns following Iceberg field-ID safety rules
- Compaction via `CALL system.rewrite_data_files()` with sort strategy and file-size targets
- Manifest optimization via `CALL system.rewrite_manifests()`
- Python 3.12 automation scripts for Iceberg maintenance jobs
- Iceberg hidden metadata tables (`$snapshots`, `$files`, `$manifests`, `$partitions`, `$history`)

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip watsonxdata-lakehouse.zip
unzip iceberg-table-management.zip
```

This will create:
```
.bob/skills/watsonxdata-lakehouse/SKILL.md
.bob/skills/iceberg-table-management/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What lakehouse skills do you have active?"*

---

## Usage Examples

### watsonxdata-lakehouse
- *"Register my IBM COS bucket in watsonx.data using the REST API v2"*
- *"Connect my IBM Db2 on Cloud instance to watsonx.data as an external database"*
- *"Associate the cos_catalog catalog with my Presto engine"*
- *"Generate a watsonxdata_setup.py script to configure my lakehouse environment"*

### iceberg-table-management
- *"Create an Iceberg table for IoT sensor events (10M events/day) with day-partitioning and weekly compaction"*
- *"Write a MERGE INTO upsert for the transactions Iceberg table"*
- *"Show me a time-travel query to view the table as of 2024-06-15"*
- *"Schedule compaction and snapshot expiry for my Iceberg maintenance pipeline"*

---

## What Bob Can Help You Build

1. **Lakehouse Configuration Scripts**: Complete `watsonxdata_setup.py` with IAM auth, bucket and DB registration
2. **Federated SQL Queries**: Presto queries spanning COS, Db2, and other registered sources
3. **Iceberg DDL**: `CREATE TABLE` with optimal partition transforms for your data volume
4. **Upsert Patterns**: `MERGE INTO` with both MATCHED and NOT MATCHED branches
5. **Maintenance Pipelines**: Python scripts for compaction, snapshot expiry, and manifest rewrite
6. **Schema Evolution**: Safe `ALTER TABLE ADD/RENAME/DROP COLUMN` sequences

---

## Prerequisites

Before using these skills, ensure you have:

- IBM watsonx.data instance provisioned on IBM Cloud
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- watsonx.data CRN (for `AuthInstanceId` header)
- Presto engine >= 0.281 for compaction procedures (`iceberg-table-management`)

## Supported watsonx.data Regions

| Region | Base URL |
|---|---|
| us-south (Dallas) | `https://us-south.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| eu-de (Frankfurt) | `https://eu-de.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| au-syd (Sydney) | `https://au-syd.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| jp-tok (Tokyo) | `https://jp-tok.lakehouse.cloud.ibm.com/lakehouse/api/v2` |

## Skill Capabilities Summary

| Capability | watsonxdata-lakehouse | iceberg-table-management |
|---|---|---|
| IAM Token Management | ✅ | ✅ |
| COS/S3 Bucket Registration | ✅ | — |
| Database Connections (Db2, PG) | ✅ | — |
| Presto Catalog Association | ✅ | — |
| Iceberg Table DDL | — | ✅ |
| MERGE INTO / Time-Travel | — | ✅ |
| Compaction & Maintenance | — | ✅ |
| Schema Evolution | — | ✅ |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/watsonxdata-lakehouse/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates wrong API endpoint:**
1. Specify your watsonx.data region explicitly
2. The `AuthInstanceId` header must be the watsonx.data CRN — not the IBM Cloud account CRN

## Related

- [`../bob-modes/`](../bob-modes/) — Lakehouse Setup Bob Mode
- [`../README.md`](../README.md) — Zero-Copy Lakehouse building block overview
- [`../assets/`](../assets/) — Deployable lakehouse setup assets
