# Bob Skills for ETL / ELT with DataStage

Bob skills for **IBM DataStage** ETL/ELT flow design, enterprise connector configuration, and integration with **IBM watsonx.data** using **IBM watsonx.data integration**.

## Overview

These skills give IBM Bob expert knowledge of DataStage flow design, connector patterns, transformation stage configuration, and the integration between DataStage and IBM watsonx.data — enabling Bob to assist with building, troubleshooting, and modernizing batch data integration pipelines.

## Available Skills

> **Coming soon** — the Bob Skill zips for this building block have not yet been committed to this repository.

| Skill | Use When |
|---|---|
| `datastage-flow-design` | Designing DataStage ETL/ELT flows — connectors, stages, scheduling, monitoring |
| `datastage-watsonxdata-integration` | Connecting DataStage flows to IBM watsonx.data — Iceberg targets, Presto, catalog setup |

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

Installation instructions will be added when the zips are available.

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
