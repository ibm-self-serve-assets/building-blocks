# IBM Databand OpenLineage Emitter

Python library and CLI for emitting **OpenLineage** run events to **IBM Databand** —  
IBM's data observability platform on IBM Cloud.

## IBM Cloud Products Used

| Product | Role |
|---|---|
| **IBM Databand** | Receives OpenLineage events, renders lineage graphs, surfaces pipeline anomalies |
| **IBM Cloud IAM** | Authentication — IBM API key → Bearer token |
| **IBM Cloud Object Storage (COS)** | Reference as dataset source/target in lineage events |
| **IBM watsonx.data (Presto/Iceberg)** | Reference as dataset namespace in lineage events |

## What's Included

```
openlineage-emitter/
├── emitter.py          # Library + CLI for emitting OpenLineage events
├── requirements.txt
├── Dockerfile
└── .env.example
```

## How It Works

IBM Databand exposes a Marquez-compatible HTTP transport at `/api/v1/lineage`.  
This emitter uses the official `openlineage-python` SDK to send **START**, **COMPLETE**,  
and **FAIL** events carrying dataset lineage (inputs → outputs) with optional schema facets.

Supported namespace conventions (automatically parsed from URI):

| URI Pattern | Namespace | Use Case |
|---|---|---|
| `cos://bucket/path` | `cos://bucket` | IBM COS datasets |
| `iceberg://catalog/schema.table` | `iceberg://catalog` | watsonx.data Iceberg tables |
| `db2://host/database.table` | `db2://host` | IBM Db2 tables |
| `kafka://broker/topic` | `kafka://broker` | Confluent Kafka topics |

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with DATABAND_URL and DATABAND_ACCESS_TOKEN

# Emit a COMPLETE event
python emitter.py \
  --pipeline customer_etl \
  --job      transform_orders \
  --inputs   "cos://raw-bucket/orders.csv" \
  --outputs  "iceberg://cos_catalog/sales.orders_curated" \
  --event-type COMPLETE
```

## Python SDK Usage

```python
from emitter import PipelineRun

# Context manager automatically emits START on entry,
# COMPLETE on clean exit, FAIL on exception.
with PipelineRun(
    pipeline_name="customer_etl",
    job_name="transform_orders",
    inputs=["cos://raw-bucket/orders.csv"],
    outputs=["iceberg://cos_catalog/sales.orders_curated"],
    output_schema=[
        {"name": "order_id", "type": "string"},
        {"name": "amount",   "type": "double"},
        {"name": "ts",       "type": "timestamp"},
    ],
) as run:
    # Your ETL logic here
    print(f"Run ID: {run.run_id}")
```

## IBM Cloud References

- [IBM Databand Documentation](https://www.ibm.com/docs/en/databand)
- [OpenLineage Specification](https://openlineage.io/spec)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
