# Data Lineage

**IBM product**: IBM watsonx.data intelligence

Reference assets for OpenLineage instrumentation, lineage queries, and impact analysis. IBM watsonx.data intelligence is the lineage/governance product anchor; Data Observability is a separate operational monitoring capability.

## Included assets

| Path | Purpose |
|---|---|
| [`assets/openlineage-collector/`](assets/openlineage-collector/) | OpenLineage event collection/reference integration |
| [`assets/lineage-impact-analyzer/`](assets/lineage-impact-analyzer/) | Lineage impact analysis/reporting reference asset |
| [`bob-modes/`](bob-modes/) | IBM Bob lineage mode |
| [`bob-skills/openlineage-instrumentation.zip`](bob-skills/openlineage-instrumentation.zip) | IBM Bob OpenLineage/lineage skill |

## Architecture boundary

```text
DataStage / Spark / Python pipelines
              |
              | OpenLineage / lineage metadata
              v
IBM watsonx.data intelligence
   lineage, impact analysis, governance

Operational pipeline health and alerting
              |
              v
IBM watsonx.data integration — Data Observability
```

Do not treat Data Observability/Databand as the enterprise lineage graph repository.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
