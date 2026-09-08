# Data Quality Bob Skills

Bob skills for data quality rule implementation using **IBM watsonx.data Intelligence** (DAI) on IBM Cloud.

## Overview

The `data-quality-rules` skill empowers IBM Bob to implement **IBM watsonx.data Intelligence** data quality capabilities — generating complete DQ rule CRUD code, async execution flows, column-level profiling jobs, quality score aggregation, and IBM COS report archiving following IBM building-blocks conventions.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `data-quality-rules` | [`data-quality-rules.zip`](data-quality-rules.zip) | Implementing data quality rules on IBM watsonx.data Intelligence: completeness, uniqueness, validity, consistency, accuracy |

---

### `data-quality-rules`

A comprehensive skill for implementing IBM watsonx.data Intelligence data quality capabilities:

- IBM Cloud IAM API key → Bearer token authentication with auto-refresh (`IAMTokenManager`)
- IBM watsonx.data Intelligence (DAI) REST API: `/data_quality/rules`, `/data_quality/results`, `/data_quality/profile_jobs`
- DQ rule creation for all five types: completeness, uniqueness, validity, consistency, accuracy
- Asynchronous rule execution and result polling
- Column-level data profiling job submission and status polling
- Quality score aggregation across project rules
- IBM COS report archiving with `ibm-cos-sdk` IAM OAuth
- `tenacity` retry decorators on all DAI API calls
- FastAPI service patterns matching IBM building-blocks conventions

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip data-quality-rules.zip
```

This will create:
```
.bob/skills/data-quality-rules/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `data-quality-rules`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What data quality skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Generate a completeness DQ rule for the email and customer_id columns in my orders dataset"*
- *"Create a validity rule using a regex pattern to validate US phone number format"*
- *"Submit a column profiling job for null_rate, distinct count, and histogram on the transactions table"*
- *"Build a FastAPI service that exposes DQ rule execution and quality score endpoints"*
- *"Archive my DQ results report to IBM COS using ibm-cos-sdk"*

---

## What Bob Can Help You Build

1. **DQ Rule Definitions**: All five rule types with correct payload structure
2. **Rule Execution Flows**: Async `POST /rules/{id}/execute` + polling patterns
3. **Column Profiling Jobs**: Submitting and polling `POST /profile_jobs`
4. **Quality Score Dashboards**: Aggregating scores across rules and assets
5. **IBM COS Archiving**: Quality report storage with IAM OAuth
6. **FastAPI Services**: RESTful DQ APIs matching building-blocks patterns

---

## DQ Rule Types Reference

| Rule Type | Use Case | Key Fields |
|---|---|---|
| `completeness` | Null / missing value check | `columns`, `threshold` (min non-null %) |
| `uniqueness` | Duplicate detection | `columns`, `threshold` (max duplicate %) |
| `validity` | Format / regex / enum check | `columns`, `regex_pattern` or `allowed_values` |
| `consistency` | Cross-column referential integrity | `columns`, `threshold` |
| `accuracy` | Comparison vs reference dataset | `columns`, `threshold` |

---

## Prerequisites

Before using this skill, ensure you have:

- IBM watsonx.data Intelligence instance provisioned on IBM Cloud
- A watsonx.data Intelligence Project ID (from the project Manage tab)
- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- (Optional) IBM Cloud Object Storage for report archiving

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **IAM Token Management** | Auto-refresh with 5-minute buffer |
| **DQ Rule Creation** | `completeness`, `uniqueness`, `validity`, `consistency`, `accuracy` |
| **Async Execution** | `POST /rules/{id}/execute` + status polling |
| **Column Profiling** | Null rate, distinct count, min/max, histogram |
| **Quality Score** | Aggregated pass/fail score across rules |
| **IBM COS Archiving** | `ibm-cos-sdk` IAM OAuth `put_object` |
| **Retry Logic** | `tenacity` decorators on all DAI API calls |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/data-quality-rules/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**DQ rule execution returns errors:**
1. Verify the `asset_id` is correct for the data asset in your project
2. Confirm the `project_id` from the DAI project Manage tab
3. DQ rules currently supported in `us-south` region

## Related

- [`../bob-modes/`](../bob-modes/) — Data Quality Builder Bob Mode
- [`../README.md`](../README.md) — Data Quality building block overview
- [`../assets/`](../assets/) — Deployable data quality service assets
