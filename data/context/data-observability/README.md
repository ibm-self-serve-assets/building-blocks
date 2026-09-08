# Data Observability

**IBM product**: IBM watsonx.data integration — Data Observability

Monitor integration workloads for failures, abnormal behavior, pipeline/run health, operational data-quality signals, and alerts. Some reference assets retain `databand` names because they wrap Databand-compatible functionality within the IBM observability portfolio.

## Included assets

| Path | Purpose |
|---|---|
| [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) | Reference client/service for pipeline and run health |
| [`assets/openlineage-emitter/`](assets/openlineage-emitter/) | OpenLineage event emission for operational monitoring |
| [`assets/databand-alert-templates/`](assets/databand-alert-templates/) | Alert policy templates/reference tooling |
| [`bob-modes/`](bob-modes/) | IBM Bob observability mode |
| [`bob-skills/databand-pipeline-setup.zip`](bob-skills/databand-pipeline-setup.zip) | IBM Bob observability setup skill |

## Boundary

Data Observability is for operational health and alerts. For enterprise lineage graphs, impact analysis, and governance, use [`../metadata-enrichment/data-lineage/`](../metadata-enrichment/data-lineage/).

## IBM references

- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- watsonx.data integration documentation: https://www.ibm.com/docs/en/software-hub/5.4.x?topic=services-watsonxdata-integration
