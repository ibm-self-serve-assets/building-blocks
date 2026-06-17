# Bob Mode for Data Quality

Custom IBM Bob mode configuration for data quality workflows using **IBM watsonx.data Intelligence** on IBM Cloud.

---

## Overview

This Bob mode provides specialized assistance for:

- **watsonx.data Intelligence DQ Rules**: Creating and managing completeness, uniqueness, validity, consistency, and accuracy rules
- **Rule Execution**: Triggering asynchronous rule evaluation via the DAI REST API
- **Quality Score Analysis**: Interpreting aggregate quality scores and per-rule results
- **Data Profiling**: Submitting column-level profiling jobs to watsonx.data Intelligence
- **IBM COS Integration**: Archiving quality reports to IBM Cloud Object Storage

---

## What's Included

- **[`base-modes/data-quality-builder.zip`](base-modes/data-quality-builder.zip)**: Bob mode configuration for data quality development

---

## Mode Capabilities

- IBM Cloud IAM authentication (API key → Bearer token with auto-refresh)
- watsonx.data Intelligence project and asset management
- DQ rule authoring for all five rule types
- Asynchronous rule execution and result polling
- Column-level data profiling job submission
- Quality score aggregation and trend analysis
- IBM COS report archiving with `ibm-cos-sdk`
- FastAPI service development for DQ integrations
- Docker containerization for IBM Code Engine deployment

---

## When to Use This Mode

- Implementing data quality rules for IBM watsonx.data Intelligence projects
- Designing quality thresholds for completeness, uniqueness, or validity
- Building automated DQ pipelines with rule execution and scoring
- Troubleshooting DAI API authentication or rule execution failures
- Profiling new datasets before adding them to AI pipelines
- Archiving quality reports to IBM COS for audit compliance

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/data-quality-builder.zip`](base-modes/data-quality-builder.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with data quality tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/data-quality-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/data-quality-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
