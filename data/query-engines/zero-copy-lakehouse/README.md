# Zero-Copy Lakehouse

**IBM product**: IBM watsonx.data

Use this building block to query supported external data platforms and open lakehouse tables through IBM watsonx.data **without introducing unnecessary copies or ETL pipelines**.

“Zero-copy” means data can be queried in place for supported integrations. It is not a guarantee that every query, cache, optimization, or operation performs zero physical data movement.

## Architecture

```text
IBM COS / S3 / supported external platforms
                 |
                 | register/connect
                 v
           IBM watsonx.data
       catalogs + Apache Iceberg
                 |
          +------+------+
          |             |
          v             v
       Presto         Spark
          |
          v
   federated / lakehouse SQL
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/setup-lakehouse/`](assets/setup-lakehouse/) | Reference automation/setup for watsonx.data sources, catalogs, and queries |
| [`bob-modes/`](bob-modes/) | IBM Bob lakehouse mode |
| [`bob-skills/watsonxdata-lakehouse.zip`](bob-skills/watsonxdata-lakehouse.zip) | Bob skill for watsonx.data lakehouse setup |
| [`bob-skills/iceberg-table-management.zip`](bob-skills/iceberg-table-management.zip) | Bob skill for Iceberg table operations |

## What the reference asset demonstrates

The setup asset includes patterns for:

- IBM Cloud Object Storage;
- optional S3 storage;
- IBM Db2 connectivity;
- Presto catalog association;
- Apache Iceberg schemas/tables;
- sample federated SQL across registered sources.

## Quick start

```bash
cd assets/setup-lakehouse
# Review README.md and config.json before running.
# Populate your watsonx.data, IBM Cloud, storage, and database settings.
python watsonxdata_setup.py
```

The setup script creates/modifies cloud resources. Review the asset README and configuration before executing it against a shared environment.

## Example query pattern

```sql
SELECT c.customer_id, c.name, a.balance
FROM iceberg_data.sales_schema.customer c
JOIN db2_catalog.finance_schema.accounts a
  ON c.customer_id = a.customer_id
WHERE a.balance > 10000;
```

Catalog/schema names are examples from the reference asset.

## Developer guidance

- Choose the correct connector/catalog for the source system.
- Keep object-storage and database credentials out of source control.
- Validate connector limitations before promising zero-copy access to a source.
- Design Iceberg partitioning based on query patterns and data volume.
- Use query-engine controls and source-system permissions appropriate to the workload.
- Treat any hard-coded endpoint/region in sample configuration as an example, not a universal endpoint.

## IBM references

- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- Access external data platforms / zero-copy federation: https://www.ibm.com/docs/en/watsonxdata/saas?topic=components-accessing-data-in-external-data-platforms
- IBM watsonx.data documentation: https://cloud.ibm.com/docs/watsonxdata
