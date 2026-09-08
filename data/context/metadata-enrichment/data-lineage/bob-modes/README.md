# Bob Mode for Data Lineage

Custom IBM Bob mode configuration for data lineage workflows using **IBM watsonx.data Intelligence** (Manta) and **IBM Databand** on IBM Cloud.

---

## Overview

This Bob mode provides specialized assistance for:

- **OpenLineage Instrumentation**: Emitting START / COMPLETE / FAIL events from Python, DataStage, and Spark
- **IBM Databand Integration**: Forwarding OpenLineage events to the Marquez-compatible `/api/v1/lineage` endpoint
- **Manta Lineage Queries**: Traversing upstream/downstream lineage graphs via watsonx.data Intelligence REST API
- **Impact Analysis**: Identifying all downstream assets affected by schema or data changes
- **IBM COS Archiving**: Storing lineage and impact reports in IBM Cloud Object Storage

---

## What's Included

- **[`base-modes/data-lineage-builder.zip`](base-modes/data-lineage-builder.zip)**: Bob mode configuration for data lineage development

---

## Mode Capabilities

- IBM Cloud IAM authentication (API key → Bearer token)
- OpenLineage event construction with correct IBM Cloud dataset URIs
- IBM Databand Marquez endpoint integration
- watsonx.data Intelligence Manta lineage graph queries
- Column-level downstream impact analysis
- Lineage report archiving to IBM COS
- FastAPI service development for lineage event collection

---

## When to Use This Mode

- Instrumenting Python ETL scripts with OpenLineage context managers
- Adding DataStage job lineage tracking via custom OpenLineage facets
- Querying Manta lineage graphs for governance or audit purposes
- Performing impact analysis before schema migrations
- Building lineage-aware data pipelines on IBM Cloud
- Troubleshooting lineage event forwarding to Databand

---

## Installing Bob Modes

### Installing the Custom Bob Mode

The custom Bob mode ([`base-modes/data-lineage-builder.zip`](base-modes/data-lineage-builder.zip)) defines the behavior, expertise, and capabilities of IBM Bob when working with data lineage tasks.

For detailed information about custom modes, see the [IBM Bob Custom Modes Documentation](https://internal.bob.ibm.com/docs/ide/features/custom-modes).

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/data-lineage-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/data-lineage-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
