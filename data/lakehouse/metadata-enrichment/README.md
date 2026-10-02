# Metadata Enrichment & Data Quality

**IBM product**: IBM watsonx.data intelligence

Use this building block to make enterprise data easier to **discover, understand, trust, govern, and reuse** by adding metadata enrichment, data-quality assessment, and lineage context.

## Capabilities

| Capability | Path | Developer focus |
|---|---|---|
| Data Quality | [`data-quality/`](data-quality/) | Rules, profiling, quality scores, exceptions |
| Data Lineage | [`data-lineage/`](data-lineage/) | OpenLineage ingestion, lineage queries, impact analysis |

Metadata enrichment in watsonx.data intelligence can combine profiling, business vocabulary, classifications, generated descriptions/names, quality checks, and relationship analysis depending on the target deployment and configuration.

## Typical flow

```text
Source connections
      |
      v
Metadata import / profiling
      |
      v
IBM watsonx.data intelligence
      |
      +--> names / descriptions / classifications
      +--> business-term assignment
      +--> quality checks / scores
      +--> lineage / impact context
      |
      v
Catalogs / governed data / AI-ready context
```

## Developer path

1. Use [`data-quality/`](data-quality/) when you need executable quality-rule patterns or a quality API.
2. Use [`data-lineage/`](data-lineage/) when you need OpenLineage instrumentation or impact analysis.
3. Use [Data Observability](../data-observability/) separately for operational run health, anomaly detection, and alerts.

## Important boundary

**Data Observability is not a prerequisite for metadata enrichment, data quality, or enterprise lineage.** Use it only when operational pipeline monitoring is also part of the solution.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- Metadata enrichment settings: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=tools-metadata-enrichment
- Metadata imports: https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=metadata-creating-imports
- OpenLineage integration: https://www.ibm.com/docs/en/ws-and-kc?topic=lineage-openlineage-integration
