# ETL / ELT with DataStage

**Core Capability**: Pipelines
**IBM Products**: IBM DataStage (IBM watsonx.data integration), IBM watsonx.data
**Product Components**: DataStage visual flow designer; enterprise connectors; transformation stages; scheduling; IBM watsonx.data integration with DataStage

## Overview

Build governed, repeatable batch integration flows using **IBM DataStage** — the enterprise ETL/ELT engine inside **IBM watsonx.data integration**. DataStage provides a visual drag-and-drop flow designer with a large catalog of enterprise connectors, reusable transformation stages, and operational scheduling — delivering structured data from source systems into IBM watsonx.data and other targets without custom scripting every pipeline.

IBM DataStage supports both **ETL** (transform then load) and **ELT** (load raw then transform at target) patterns, making it a fit for a wide range of data preparation, migration, and modernization scenarios.

---

## When to Use

| Scenario | Approach |
|---|---|
| Batch ingestion from relational databases (Db2, PostgreSQL, MySQL, Oracle, SQL Server) | DataStage source connector → transform stages → watsonx.data target |
| Move and transform data between on-premises and IBM Cloud | DataStage with hybrid connectivity |
| Migrate legacy ETL assets to a modern governed platform | Import / re-author existing DataStage flows |
| Prepare and cleanse data before loading into an Iceberg lakehouse | DataStage ELT → watsonx.data Iceberg catalog |
| Repeatable batch jobs with operational scheduling and monitoring | DataStage job scheduler + run history |
| Push transformations down to the target engine (ELT pattern) | Use watsonx.data compute as transformation layer |

!!! tip
    For sub-second or event-driven requirements, use the **[Real-Time Streaming](../../context/real-time-streaming/README.md)** building block instead. DataStage is designed for batch-oriented workloads with enterprise operational governance.

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM watsonx.data integration** instance with DataStage enabled
- **IBM watsonx.data** instance (for Iceberg / lakehouse target use cases)
- Source system credentials (database user, JDBC connection details, or file/API access)

### Quick Start — Creating a DataStage Flow

1. Open **IBM watsonx.data integration** and navigate to **DataStage**.
2. Create a new flow and add a **Data source** connector for your source system.
3. Inspect the source schema — DataStage automatically detects column names and types.
4. Add transformation stages as needed: **Transformer**, **Join**, **Filter**, **Aggregate**, **Sort**, or **Lookup**.
5. Add a **Data target** connector — for watsonx.data, use the Iceberg or Presto connector.
6. Compile and run the job. Inspect the execution summary and row counts.
7. Schedule the job for regular execution using the DataStage scheduler.

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The ETL/ELT building block documents **Bob Mode** and **Bob Skill** assets for DataStage flow design, connector configuration, transformation patterns, and watsonx.data integration.

> **Asset availability note**: The `datastage-etl-builder.zip` Bob Mode and DataStage Bob Skills are defined in this building block. Check [`bob-modes/base-modes/`](bob-modes/base-modes/) and [`bob-skills/`](bob-skills/) for current file availability.

---

## DataStage Flow Model

A DataStage flow consists of connected components on a visual canvas:

| Component | Role |
|---|---|
| **Data source stage** | Read from databases, files, SaaS, APIs, cloud object stores, and more |
| **Transformation stage** | Transform, cleanse, join, filter, derive columns, or aggregate data |
| **Data target stage** | Write results to watsonx.data, warehouses, files, or other systems |
| **Link** | Connects sources, transformation stages, and targets into a directed flow |

```
Source systems                  Transformation              Target systems
(DB2 / PostgreSQL / Files)      (DataStage stages)          (watsonx.data / Warehouse)
        │                              │                              │
  Source connector               Transformer                  Target connector
  Schema detection               Join / Filter                Iceberg table write
  Type mapping                   Aggregation                  Presto INSERT INTO
  Incremental load               Derivation                   Quality validation
        │                              │                              │
        └──────────────────────────────┴──────────────────────────────┘
                                       │
                              IBM watsonx.data integration
                              (job scheduler + monitoring)
```

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM DataStage](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=datastage-designing-flows)** | Visual ETL/ELT flow designer with enterprise connectors, stages and transformations |
| **[IBM watsonx.data integration](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integration)** | Integration platform hosting DataStage plus scheduling, monitoring and governance |
| **[IBM watsonx.data](https://www.ibm.com/products/watsonx-data)** | Target open lakehouse platform — Iceberg tables, Presto engine, governance |
| **[DataStage integration with watsonx.data](https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-datastage)** | Connector support for reading from and writing into watsonx.data |

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for DataStage ETL/ELT flow design and watsonx.data integration
  - **Install**: copy [`bob-modes/base-modes/datastage-etl-builder.zip`](./bob-modes/base-modes/datastage-etl-builder.zip) to your Bob modes directory
  - Describe your source and target → Bob assists with flow design, transformation logic, and connector configuration

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `datastage-flow-design` | [`bob-skills/datastage-flow-design.zip`](./bob-skills/datastage-flow-design.zip) | DataStage visual flow design, connector setup, transformation stage configuration, scheduling, monitoring |
| `datastage-watsonxdata-integration` | [`bob-skills/datastage-watsonxdata-integration.zip`](./bob-skills/datastage-watsonxdata-integration.zip) | Connecting DataStage to IBM watsonx.data — Iceberg targets, Presto, catalog configuration, ELT patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

---

## Design Considerations

- **Prefer ELT when the target engine is optimized for transformation** — loading raw data into watsonx.data and transforming with Presto or Spark often reduces data movement compared to pre-transforming in DataStage.
- **Design restartability and idempotence** — long-running batch jobs should be able to restart from a checkpoint without duplicating or losing data.
- **Use explicit data contracts** — define expected schemas for important source/target connections and validate at runtime.
- **Separate environment-specific configuration from flow logic** — store connection credentials in parameter sets, not hardcoded in flows.
- **Monitor row counts and job durations** — unexpected changes in these metrics are early signals of upstream data issues.

---

## IBM Cloud References

- [IBM DataStage — Designing Flows](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=datastage-designing-flows)
- [IBM watsonx.data integration](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-integration)
- [DataStage integration with watsonx.data](https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-datastage)
- [IBM watsonx.data Documentation](https://www.ibm.com/products/watsonx-data)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
