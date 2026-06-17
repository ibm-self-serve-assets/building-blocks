# Data Streaming

**Core Capability**: Integration
**IBM Products**: Confluent (on IBM Cloud)
**Product Components**: Apache Kafka topics; Confluent Schema Registry; Apache Flink SQL; Confluent Connectors; Stream Governance; Confluent Hub

## Overview

Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases using **Confluent** on IBM Cloud. This capability enables continuous data flow with enterprise-grade schema governance, Flink SQL stream processing, and infrastructure-as-code provisioning via Terraform.

## Key Features

- **Real-time Event Ingestion**: Capture and process events as they occur with Apache Kafka
- **Apache Flink Stream Processing**: Stateful stream transformations with Flink SQL statements
- **Schema Registry**: Avro, JSON Schema, and Protobuf schema management with Schema Registry
- **Confluent Connectors**: Pre-built source and sink connectors for databases, cloud storage, and SaaS
- **Stream Governance**: Data lineage, schema evolution policies, and data quality on streams
- **Terraform IaC**: Provision entire Confluent environments with the Confluent Terraform provider
- **Python Producers/Consumers**: `confluent-kafka` client patterns with Schema Registry integration
- **Operational + Analytical**: Real-time monitoring, alerting, CDC, and stream analytics

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `data-streaming-confluent` | [`bob-skills/data-streaming-confluent.zip`](./bob-skills/data-streaming-confluent.zip) | Confluent infrastructure Terraform IaC, Kafka topic + Schema Registry setup, Python producer/consumer with Avro schemas, Flink SQL stream processing statements, multi-environment backbone creation |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

## Typical Streaming Architecture

```
Data Sources (DB, App Events, IoT)
        │
        │  Confluent Source Connectors / Python Producers
        ▼
Apache Kafka Topics
  (Confluent Cloud on IBM Cloud)
        │
        ├─ Schema Registry (Avro / JSON / Protobuf)
        │
        ├─ Apache Flink SQL (stream processing)
        │   ├─ Filtering, aggregation, joins
        │   └─ Enrichment with reference tables
        │
        └─ Confluent Sink Connectors
                │
                ▼
        IBM watsonx.data / IBM COS / DB2
        (analytical destinations)
```

## Terraform IaC Modules (via Bob Skill)

The `data-streaming-confluent` skill generates:

```
terraform/
├── providers.tf          # Confluent + IBM Cloud providers
├── variables.tf          # Environment-specific variables
├── main.tf               # Topics, schemas, connectors, ACLs
└── outputs.tf            # Bootstrap servers, API keys, .env output

python/
├── requirements.txt      # confluent-kafka, fastavro
├── produce_messages.py   # Schema Registry-aware producer
└── sample-transactions.json

flink/
└── statements.sql        # Flink SQL stream processing jobs
```

## IBM Cloud References

- [Confluent on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/confluent)
- [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/docs/stable/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
