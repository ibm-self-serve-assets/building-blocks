# Data Lineage

**IBM product**: IBM watsonx.data intelligence

Reference assets for OpenLineage instrumentation, lineage ingestion, lineage queries, and downstream impact analysis.

## Product boundary

IBM uses OpenLineage as a common lineage-exchange standard across the watsonx platform:

- watsonx.data and watsonx.data integration can act as **OpenLineage producers**;
- watsonx.data intelligence acts as an **OpenLineage consumer** and correlates lineage with other collected metadata;
- Data Observability remains a separate operational monitoring capability.

## Architecture

```text
DataStage / Spark / Python / watsonx.data
                |
                | OpenLineage / lineage metadata
                v
      IBM watsonx.data intelligence
       lineage + impact + governance
                |
                v
        governed consumers

Pipeline operational health
                |
                v
watsonx.data integration — Data Observability
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/openlineage-collector/`](assets/openlineage-collector/) | Reference collector/API for OpenLineage events |
| [`assets/lineage-impact-analyzer/`](assets/lineage-impact-analyzer/) | Downstream impact analysis/reporting reference |
| [`bob-modes/`](bob-modes/) | IBM Bob lineage mode |
| [`bob-skills/openlineage-instrumentation.zip`](bob-skills/openlineage-instrumentation.zip) | IBM Bob lineage/instrumentation skill |

## Quick start

Run the collector:

```bash
cd assets/openlineage-collector
cp .env.example .env
# Configure the target IBM services/credentials described in the asset README.
pip install -r requirements.txt
python main.py
# Swagger UI: http://localhost:8080/docs
```

Run impact analysis:

```bash
cd assets/lineage-impact-analyzer
pip install -r requirements.txt
python impact_analyzer.py --asset-id <asset-id>
```

The impact analyzer can also emit a JSON report; see its README for available options and IBM COS archival support.

## Production notes

- Treat OpenLineage event payloads as lineage metadata, not as authorization assertions.
- Validate namespace/job/dataset naming conventions before integrating multiple producers.
- Use watsonx.data intelligence for the governed lineage view; do not model Databand as the enterprise lineage repository.

## IBM references

- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- OpenLineage integration: https://www.ibm.com/docs/en/ws-and-kc?topic=lineage-openlineage-integration
