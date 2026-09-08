# Bob Skills for ETL / ELT with DataStage

Bob skills for **IBM DataStage** ETL/ELT flow design, enterprise connector configuration, and integration with **IBM watsonx.data** using **IBM watsonx.data integration**.

## Overview

These skills give IBM Bob expert knowledge of DataStage flow design, connector patterns, transformation stage configuration, and the integration between DataStage and IBM watsonx.data — enabling Bob to assist with building, troubleshooting, and modernizing batch data integration pipelines.

## Available Skills

> **Coming soon** — `datastage-flow-design.zip` and `datastage-watsonxdata-integration.zip` are not yet committed to this repository. The documentation below describes the intended skill capabilities. Check this directory for availability.

| Skill | Zip | Use When |
|---|---|---|
| `datastage-flow-design` | `datastage-flow-design.zip` | Designing DataStage ETL/ELT flows — connectors, stages, scheduling, monitoring |
| `datastage-watsonxdata-integration` | `datastage-watsonxdata-integration.zip` | Connecting DataStage flows to IBM watsonx.data — Iceberg targets, Presto, catalog setup |

---

### `datastage-flow-design`

A comprehensive skill for building DataStage batch integration flows:

- DataStage flow canvas — sources, stages, targets, links
- Enterprise source connectors: Db2, PostgreSQL, MySQL, Oracle, SQL Server, IBM COS, SaaS
- Transformation stages: Transformer, Join, Filter, Aggregate, Sort, Lookup, Funnel
- Incremental load patterns — watermark columns, change detection, delta identification
- Parameter sets for separating credentials from flow logic
- Job scheduler configuration for recurring batch runs
- Row-count and duration monitoring
- Error handling, retry, and dead-letter patterns

### `datastage-watsonxdata-integration`

A comprehensive skill for integrating DataStage with IBM watsonx.data:

- IBM watsonx.data integration DataStage connector setup
- Writing DataStage output into Apache Iceberg tables in watsonx.data
- ELT pattern — load raw into watsonx.data, then transform with Presto or Spark
- IBM Cloud IAM authentication for watsonx.data REST API access
- Catalog and schema configuration in watsonx.data for DataStage targets
- Partition strategy design for Iceberg tables written by DataStage
- Schema evolution handling — adding columns without breaking downstream consumers
- `watsonx.data` → DataStage source patterns for reading from the lakehouse

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip datastage-flow-design.zip
unzip datastage-watsonxdata-integration.zip
```

This will create:
```
.bob/skills/datastage-flow-design/SKILL.md
.bob/skills/datastage-watsonxdata-integration/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What DataStage ETL skills do you have active?"*

---

## Usage Examples

### datastage-flow-design
- *"Design a DataStage batch job that reads from Oracle and writes to a staging table in DB2"*
- *"Configure incremental load from PostgreSQL using a watermark on the updated_at column"*
- *"What DataStage stages should I use to join two sources on customer_id and filter nulls?"*

### datastage-watsonxdata-integration
- *"How do I configure DataStage to write into an Iceberg table in IBM watsonx.data?"*
- *"Set up an ELT pattern where DataStage loads raw data into watsonx.data and Presto handles the transformation"*
- *"What connector and authentication do I need to read from watsonx.data in a DataStage source stage?"*

---

## Prerequisites

Before using these skills, ensure you have:

- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- IBM watsonx.data integration instance with DataStage enabled
- IBM watsonx.data instance (for Iceberg / Presto / Spark target patterns)
- Source system credentials (database, file, or API access)

---

## Related

- [`../bob-modes/`](../bob-modes/) — DataStage ETL Builder Bob Mode
- [`../README.md`](../README.md) — ETL / ELT building block overview
- [`../assets/`](../assets/) — Reference configuration and flow assets
