# Data Observability Bob Skills

Bob skills for data observability and pipeline monitoring using **IBM Databand** on IBM Cloud, with **OpenLineage** event instrumentation.

## Overview

The `databand-pipeline-setup` skill empowers IBM Bob to instrument IBM data pipelines with observability — generating IBM Databand REST API integration code, OpenLineage event emission patterns, alert policy configurations, and COS report archiving — following IBM building-blocks conventions.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `databand-pipeline-setup` | [`databand-pipeline-setup.zip`](databand-pipeline-setup.zip) | Onboarding IBM data pipelines to IBM Databand: monitoring, alerts, OpenLineage, COS report archiving |

---

### `databand-pipeline-setup`

A comprehensive skill for monitoring IBM data pipelines with IBM Databand:

- IBM Cloud IAM authentication with automatic token refresh (`IAMTokenManager`)
- IBM Databand REST API v1 integration (pipelines, runs, metrics, alert_defs)
- OpenLineage event emission via `openlineage-python` SDK to Databand's `/api/v1/lineage`
- Alert policy creation for null_rate, schema_drift, row_count, SLA, quality_score thresholds
- IBM Cloud Object Storage report archiving with `ibm-cos-sdk` IAM OAuth
- FastAPI service patterns matching IBM building-blocks conventions
- `tenacity` retry decorators for resilient Databand API calls
- Pydantic v2 model definitions for all request/response bodies

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip databand-pipeline-setup.zip
```

This will create:
```
.bob/skills/databand-pipeline-setup/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `databand-pipeline-setup`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What data observability skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Generate IBM Databand pipeline registration code with OpenLineage event emission"*
- *"Create an alert policy for null_rate > 5% and schema drift on the customers pipeline"*
- *"Instrument my Python ETL script with OpenLineage START/COMPLETE/FAIL events"*
- *"Build a FastAPI service to monitor Databand pipeline runs and archive reports to IBM COS"*
- *"Show me IBM DataStage OpenLineage facet patterns for IBM Databand"*

---

## What Bob Can Help You Build

1. **Pipeline Onboarding**: IBM Databand REST API v1 pipeline registration code
2. **OpenLineage Instrumentation**: Wrapping Python ETL, DataStage, and Spark with OpenLineage events
3. **Alert Policies**: Threshold-based alerts for null_rate, row_count, schema drift, SLA
4. **Quality Score Analysis**: Interpreting aggregate scores and per-run quality metrics
5. **IBM COS Archiving**: Storing run reports using `ibm-cos-sdk` with IAM OAuth
6. **FastAPI Services**: RESTful observability APIs matching building-blocks patterns

---

## Prerequisites

Before using this skill, ensure you have:

- IBM Databand instance provisioned on IBM Cloud
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- (Optional) IBM Cloud Object Storage instance for report archiving

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **IAM Token Management** | Auto-refresh with 5-minute buffer |
| **Databand REST API v1** | Pipelines, runs, metrics, alert_defs endpoints |
| **OpenLineage Events** | START/COMPLETE/FAIL with dataset URIs |
| **Alert Policy Design** | null_rate, row_count, schema_drift, quality_score, SLA |
| **IBM COS Report Archiving** | `ibm-cos-sdk` IAM OAuth `put_object` |
| **Dataset URI Conventions** | COS, Iceberg, Db2, Kafka, DataStage namespaces |
| **Retry Logic** | `tenacity` decorators on all API calls |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/databand-pipeline-setup/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates wrong Databand API paths:**
1. Mention "IBM Databand REST API v1" explicitly
2. Provide your Databand instance URL: `https://<instance>.databand.ai`

## Related

- [`../bob-modes/`](../bob-modes/) — Data Observability Builder Bob Mode
- [`../README.md`](../README.md) — Data Observability building block overview
- [`../assets/`](../assets/) — Deployable Databand observability assets
