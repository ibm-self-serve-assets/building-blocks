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

## Assets

### Real-Time Supply Chain Risk Control Tower

> **Path**: [`assets/supply-chain-risk-control-tower/`](./assets/supply-chain-risk-control-tower/)

A Confluent Cloud building block that detects, scores, and acts on supply-chain disruption risk in real time. Built for IBM partner demos, technical workshops, and proof-of-value engagements.

**Use when:**

- An IBM partner needs a self-contained demo covering risk scoring, event streams, recommendations, and alerts — runnable from a laptop with no access to a customer ERP or supplier system.
- A pre-sales or technical team is preparing for a workshop and needs a complete business story backed by running code.
- A customer has asked how IBM and Confluent can help reduce supply chain disruption risk and a technical proof point is needed.
- A solutions architect needs a reference implementation of streaming joins, risk scoring, schema enforcement, and AI integration as an end-to-end pattern.

**What it demonstrates:**

- Confluent Cloud as a real-time event correlation backbone for supply chain signals
- A Kafka topic model covering 7 supply chain domains: supplier, component, purchase orders, shipments, inventory, customer orders, and external risk events
- JSON Schema data contracts enforced via Confluent Schema Registry
- A Python risk engine that consumes multiple event streams concurrently and publishes scored risk events, recommendations, and control tower alerts
- Reference Flink SQL that implements the same risk scoring logic as a production streaming job on Confluent Cloud
- An IBM Carbon Design dashboard with a browser-based simulation mode and a live Kafka streaming mode
- watsonx.ai prompt templates covering executive risk summary, supplier escalation email, and procurement recommendation
- Terraform infrastructure-as-code for provisioning a complete Confluent Cloud environment
- IBM integration story covering watsonx.ai, watsonx.data, IBM Db2, IBM MQ, IBM OpenSearch, IBM Maximo, IBM Instana, Terraform, and Ansible

**Running modes:**

| Mode | What runs | Kafka needed | Python needed | Time to start |
|------|-----------|-------------|---------------|--------------|
| Browser simulation | In-browser JavaScript engine — open `code/ui/index.html` directly | No | No | Under 1 minute |
| Python dry run | Python risk engine with synthetic data, no Kafka required | No | Yes | Under 5 minutes |
| Full Confluent Cloud | Real Kafka topics, live event stream, Terraform provisioning | Yes | Yes | 15–30 minutes |

**IBM capabilities used:**

| IBM Capability | Role |
|----------------|------|
| IBM watsonx.ai | Executive summaries, supplier escalation emails, and next-best-action guidance from risk events |
| IBM watsonx.data | Governed analytical access to event history via Confluent Tableflow lakehouse integration |
| IBM Db2 | Source for supplier master data, purchase orders, and inventory via the Db2 managed connector |
| IBM MQ | Bridge for legacy EDI and supplier message feeds via the MQ Source connector |
| IBM OpenSearch | Operational risk dashboard consuming the three output topics |
| IBM Maximo | Automatic maintenance and logistics work orders from CRITICAL-severity alerts |
| IBM Instana | Performance and health monitoring of Kafka producers, consumers, and risk engine |
| Terraform / Ansible | Automated provisioning and configuration of the Confluent Cloud environment |

---

## IBM Cloud References

- [Confluent on IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/confluent)
- [Confluent Terraform Provider](https://registry.terraform.io/providers/confluentinc/confluent/latest/docs)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [Apache Flink Documentation](https://flink.apache.org/docs/stable/)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
