# Bob Mode for Data Observability

Custom IBM Bob mode configuration for data observability workflows using **IBM Databand** on IBM Cloud.

---

## Overview

This Bob mode provides specialized assistance for:

- **IBM Databand Setup**: Provisioning and configuring Databand on IBM Cloud
- **Pipeline Registration**: Onboarding DataStage, Spark, and Python pipelines to Databand
- **OpenLineage Instrumentation**: Emitting lineage events using the `openlineage-python` SDK
- **Alert Policy Authoring**: Creating null-rate, schema-drift, SLA-breach, and quality-score alerts
- **Data Quality Monitoring**: Interpreting Databand quality scores and anomaly reports
- **IBM COS Integration**: Archiving pipeline run reports to IBM Cloud Object Storage

---

## What's Included

- **[`base-modes/data-observability-builder.zip`](base-modes/data-observability-builder.zip)**: Bob mode configuration for data observability development

---

## Mode Capabilities

- IBM Databand API authentication (IAM API key → Bearer token)
- Pipeline run monitoring and health status interpretation
- OpenLineage event emission (START / COMPLETE / FAIL)
- Dataset lineage registration with IBM COS / Iceberg / Db2 namespaces
- Alert policy creation via Databand REST API v1
- Quality score analysis and anomaly root-cause guidance
- IBM Cloud Object Storage report archiving with ibm-cos-sdk
- FastAPI service development for Databand integrations
- Docker containerization for IBM Code Engine deployment

---

## When to Use This Mode

- Setting up IBM Databand for a new IBM Cloud project
- Instrumenting Python / DataStage / Spark pipelines with OpenLineage
- Designing alert policies for pipeline quality thresholds
- Troubleshooting Databand API connectivity or authentication
- Building custom observability dashboards consuming Databand metrics
- Configuring COS archiving for pipeline audit reports

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/data-observability-builder.zip`](base-modes/data-observability-builder.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with data observability tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/data-observability-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/data-observability-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

If you prefer not to copy files, you can configure IBM Bob to reference this directory directly.

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob

This approach is useful for development and version-controlled mode updates.
