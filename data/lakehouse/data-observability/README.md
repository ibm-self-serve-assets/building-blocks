# Data Observability

**IBM product**: IBM watsonx.data integration — Data Observability

Use this building block to monitor **pipeline runs, tasks, dataset health, anomalies, SLAs, and alertable operational conditions** before unreliable data affects downstream applications or AI workloads.

## What this building block covers

- Pipeline/run health monitoring
- Operational data-quality signals
- SLA and freshness monitoring
- Alert policy patterns
- OpenLineage event emission for operational/lineage integrations
- Reference FastAPI services for API-driven monitoring workflows

This is **not** the enterprise lineage graph. For governed lineage and impact analysis, use [`../metadata-enrichment/data-lineage/`](../metadata-enrichment/data-lineage/).

## Architecture

```text
DataStage / Spark / pipelines
          |
          +------ run/task/dataset telemetry ------+
          |                                         |
          v                                         v
IBM watsonx.data integration                 OpenLineage events
     Data Observability                            |
          |                                        |
          v                                        v
 alerts / SLA / anomaly                   lineage consumers
 operational monitoring              (for example data intelligence)
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/databand-pipeline-monitor/`](assets/databand-pipeline-monitor/) | Reference API for pipeline and run health |
| [`assets/openlineage-emitter/`](assets/openlineage-emitter/) | Emit START/COMPLETE/FAIL OpenLineage events |
| [`assets/databand-alert-templates/`](assets/databand-alert-templates/) | Apply reusable alert-policy templates |
| [`bob-modes/`](bob-modes/) | IBM Bob Data Observability mode |
| [`bob-skills/databand-pipeline-setup.zip`](bob-skills/databand-pipeline-setup.zip) | IBM Bob observability setup skill |

## Quick start

Try the pipeline monitor:

```bash
cd assets/databand-pipeline-monitor
cp .env.example .env
# Set the observability endpoint/token and IBM credentials required by the asset.
pip install -r requirements.txt
python main.py
# Swagger UI: http://localhost:8080/docs
```

Or test alert templates without changing a live environment:

```bash
cd assets/databand-alert-templates
cp .env.example .env
pip install requests pyyaml python-dotenv click tenacity
python apply_alert_templates.py --all --pipeline customer_pipeline --dry-run
```

See each asset README for the exact environment variables and supported endpoints.

## Production notes

- Treat alert thresholds as workload-specific; do not copy demo thresholds into production unchanged.
- Keep observability credentials in a secrets manager or protected environment variables.
- Validate Databand/Data Observability API assumptions against the target product version.
- Use watsonx.data intelligence when the requirement is governed end-to-end lineage and impact analysis.

## IBM references

- IBM Data Observability: https://www.ibm.com/products/watsonx-data-integration/data-observability
- IBM watsonx.data integration: https://www.ibm.com/products/watsonx-data-integration
- watsonx.data integration documentation: https://www.ibm.com/docs/en/software-hub/5.4.x?topic=services-watsonxdata-integration
- OpenLineage integration across watsonx: https://www.ibm.com/docs/en/ws-and-kc?topic=lineage-openlineage-integration
