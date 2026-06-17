# Data Lineage Bob Skills

Bob skills for data lineage instrumentation and querying using **IBM watsonx.data Intelligence** (Manta) and **IBM Databand** on IBM Cloud.

## Overview

The `openlineage-instrumentation` skill empowers IBM Bob to instrument IBM data pipelines (Python ETL, IBM DataStage, Apache Spark) with **OpenLineage**, forward events to IBM Databand, and query Manta lineage graphs via IBM watsonx.data Intelligence — generating production-ready Python 3.12 code with IBM IAM authentication.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `openlineage-instrumentation` | [`openlineage-instrumentation.zip`](openlineage-instrumentation.zip) | Instrumenting pipelines with OpenLineage and querying Manta lineage graphs via watsonx.data Intelligence |

---

### `openlineage-instrumentation`

A comprehensive skill for instrumenting IBM data pipelines with OpenLineage:

- IBM Cloud IAM authentication with automatic token refresh (`IAMTokenManager`)
- OpenLineage event emission (START/COMPLETE/FAIL) using `openlineage-python` SDK
- IBM Databand Marquez-compatible `/api/v1/lineage` endpoint integration
- Dataset URI conventions for IBM Cloud assets (COS, Iceberg, Db2, Kafka, DataStage)
- IBM watsonx.data Intelligence Manta lineage graph queries (`/data_lineage/graphs`)
- Column-level downstream impact analysis (`/data_lineage/impact_analysis`)
- IBM COS archiving of lineage and impact reports
- `tenacity` retry decorators for resilient API calls

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip openlineage-instrumentation.zip
```

This will create:
```
.bob/skills/openlineage-instrumentation/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `openlineage-instrumentation`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What data lineage skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Instrument my Python ETL script with OpenLineage events pointing to IBM Databand"*
- *"Generate OpenLineage event code for IBM DataStage job runs with custom facets"*
- *"Query the Manta lineage graph for downstream assets affected by a schema change in my COS dataset"*
- *"Create a column-level impact analysis report using watsonx.data Intelligence"*
- *"Show me the correct OpenLineage dataset URI format for IBM COS and Iceberg tables"*

---

## What Bob Can Help You Build

1. **Pipeline Instrumentation**: Python context managers emitting OpenLineage START/COMPLETE/FAIL
2. **Dataset URI Patterns**: IBM-standard namespaces for COS, Iceberg, Db2, Kafka, DataStage
3. **IBM Databand Integration**: `HttpTransport` client pointing at Databand's Marquez endpoint
4. **Manta Lineage Queries**: Upstream/downstream lineage graph traversal
5. **Impact Analysis Reports**: Identifying downstream assets affected by data changes
6. **IBM COS Archiving**: Lineage report storage using `ibm-cos-sdk`

---

## IBM Cloud Dataset URI Reference

| URI Pattern | IBM Asset |
|---|---|
| `cos://bucket-name/path/to/file.csv` | IBM Cloud Object Storage |
| `iceberg://catalog_name/schema.table` | IBM watsonx.data Iceberg |
| `db2://hostname/database.table` | IBM Db2 |
| `kafka://broker-host/topic-name` | Confluent/IBM MQ Kafka |
| `datastage://project/job.stage` | IBM DataStage |

---

## Prerequisites

Before using this skill, ensure you have:

- IBM watsonx.data Intelligence instance with Manta lineage enabled
- IBM Databand instance for OpenLineage event ingestion
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- (Optional) IBM Cloud Object Storage for report archiving

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **IAM Token Management** | Auto-refresh with 5-minute buffer |
| **OpenLineage Events** | START/COMPLETE/FAIL via `openlineage-python` |
| **IBM Databand Integration** | Marquez-compatible `/api/v1/lineage` endpoint |
| **Dataset URI Design** | IBM-standard namespace conventions |
| **Manta Lineage Queries** | Upstream/downstream graph traversal |
| **Impact Analysis** | Column-level downstream impact via DAI API |
| **IBM COS Report Archiving** | `ibm-cos-sdk` IAM OAuth `put_object` |
| **Retry Logic** | `tenacity` decorators on all API calls |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/openlineage-instrumentation/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates wrong OpenLineage dataset URIs:**
1. Specify the IBM Cloud asset type explicitly (COS, Iceberg, Db2)
2. Provide the actual host/bucket/catalog name for accurate URI generation

## Related

- [`../bob-modes/`](../bob-modes/) — Data Lineage Builder Bob Mode
- [`../README.md`](../README.md) — Data Lineage building block overview
- [`../assets/`](../assets/) — Deployable lineage instrumentation assets
