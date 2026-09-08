# ETL / ELT

**IBM products**: IBM watsonx.data integration — DataStage

Use this building block for **structured batch integration**: extracting enterprise data, transforming it with DataStage, and loading it into operational stores, warehouses, or IBM watsonx.data.

## Use cases

- batch ingestion from enterprise databases;
- transformation, joins, lookups, aggregation, filtering, and standardization;
- incremental batch loads using a watermark/change-detection strategy;
- loading Apache Iceberg tables in IBM watsonx.data;
- ELT patterns where data is loaded first and transformed using a watsonx.data engine.

## Architecture

```text
Db2 / Oracle / PostgreSQL / files / SaaS
                  |
                  v
       IBM DataStage flows
 connectors + transformations + scheduling
                  |
          +-------+-------+
          |               |
          v               v
 target database    IBM watsonx.data
                    Iceberg / Presto
```

## Capability boundaries

- Structured **batch** transformation -> DataStage / this building block
- Structured near-real-time replication -> IBM watsonx.data integration Data Replication
- Unstructured documents -> [`../udi/`](../udi/)
- High-speed file repository synchronization -> [`../data-sync/`](../data-sync/)

## Repository status

This folder currently contains developer guidance under:

- [`bob-modes/`](bob-modes/)
- [`bob-skills/`](bob-skills/)

The Bob Mode/Skill ZIP implementations are currently marked **Coming soon**. No runnable `assets/` implementation is included yet.

## Developer checklist

Before building a DataStage flow, define:

1. Source and target connection types.
2. Batch frequency and expected data volume.
3. Full-load vs incremental/watermark strategy.
4. Transformation and schema-mapping rules.
5. Reject/error handling and restartability.
6. Parameterization and secret handling.
7. Target partitioning/table strategy when writing to watsonx.data.
8. Monitoring/SLA requirements.

For watsonx.data targets, IBM documents DataStage integration prerequisites including the watsonx.data connector, Data Access Service, Presto, and object storage depending on the deployment.

## IBM references

- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- IBM DataStage: https://www.ibm.com/products/datastage
- Integrating DataStage with watsonx.data: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-dc_integration
