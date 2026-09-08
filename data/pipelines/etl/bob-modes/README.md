# Bob Mode for ETL / ELT with DataStage

Custom IBM Bob mode configuration for **IBM DataStage ETL/ELT** flow design and integration with **IBM watsonx.data** using **IBM watsonx.data integration**.

---

## Overview

This Bob mode provides specialized assistance for:

- **Visual Flow Design**: Designing DataStage flows with enterprise source connectors, transformation stages, and target connectors
- **ETL and ELT Patterns**: Selecting and implementing the right pattern — transform-before-load or load-then-transform at the target engine
- **watsonx.data Integration**: Configuring DataStage to write into IBM watsonx.data Iceberg tables via the supported connectors
- **Operational Governance**: Scheduling, monitoring, run-history review, and restartability for production batch jobs
- **Legacy Migration**: Guidance for re-authoring or migrating existing DataStage assets to the current platform

---

## What's Included

- **[`base-modes/datastage-etl-builder.zip`](base-modes/datastage-etl-builder.zip)**: Bob mode configuration for DataStage ETL/ELT development

---

## Mode Capabilities

- IBM Cloud IAM authentication patterns for DataStage and watsonx.data
- DataStage connector configuration — Db2, PostgreSQL, MySQL, Oracle, SQL Server, IBM COS, SaaS sources
- Transformation stage design — Transformer, Join, Filter, Aggregate, Sort, Lookup, Funnel
- IBM watsonx.data Iceberg table as DataStage target — schema mapping, partition design
- ELT pattern using watsonx.data Presto or Spark as the transformation layer
- Incremental load design — watermark columns, change detection, CDC patterns
- Job parameter sets — separating credentials and environment config from flow logic
- DataStage scheduler configuration for recurring batch runs
- Row-count monitoring and alerting best practices
- `.env.example` and configuration file generation following building-blocks conventions

---

## When to Use This Mode

- Designing a new batch ETL or ELT flow in IBM DataStage
- Configuring an enterprise source connector to extract from Db2, PostgreSQL, or Oracle
- Writing transformed data into IBM watsonx.data Iceberg tables
- Migrating legacy ETL scripts or flows to DataStage on watsonx.data integration
- Troubleshooting DataStage connector failures or transformation stage errors
- Selecting between ETL and ELT patterns for a specific use case

---

## Installing the Bob Mode

**Windows**
```powershell
Copy-Item base-modes/datastage-etl-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**
```bash
cp base-modes/datastage-etl-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available in the mode selector.

---

## Related

- [`../bob-skills/`](../bob-skills/) — DataStage flow design and watsonx.data integration skills
- [`../README.md`](../README.md) — ETL / ELT building block overview
- [`../assets/`](../assets/) — Reference assets and configuration examples
