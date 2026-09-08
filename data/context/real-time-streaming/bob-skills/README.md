# Data Streaming Bob Skills

Bob skills for real-time data streaming using **Confluent** on IBM Cloud, with Apache Kafka, Apache Flink, and Infrastructure-as-Code support.

## Overview

These skills empower IBM Bob to design and build Confluent-based streaming pipelines on IBM Cloud — covering Terraform IaC provisioning, Kafka topic design, Schema Registry integration, Python producer/consumer patterns, and Apache Flink SQL stream processing.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `data-streaming-confluent` | [`data-streaming-confluent.zip`](data-streaming-confluent.zip) | Building end-to-end Confluent streaming pipelines: IaC, Kafka topics, schemas, Python clients, Flink SQL |
| `confluent-iac-terraform` | [`confluent-iac-terraform.zip`](confluent-iac-terraform.zip) | Confluent infrastructure-as-code: Terraform provider for environments, clusters, topics, ACLs, service accounts |

---

### `data-streaming-confluent`

A comprehensive skill for building Confluent-based streaming pipelines on IBM Cloud:

- Confluent Terraform provider infrastructure-as-code: environment, cluster, topics, Schema Registry, ACLs, service accounts, API keys
- Apache Kafka topic design (partitions, retention, compaction, replication factor)
- Avro / JSON Schema / Protobuf schema authoring and Schema Registry integration
- `confluent-kafka` Python producer with Schema Registry-aware serializer (`AvroSerializer`)
- `confluent-kafka` Python consumer with `AvroDeserializer` and consumer-group offset management
- Apache Flink SQL statement generation for stream filtering, aggregation, and enrichment
- Confluent Source/Sink connector configuration (IBM COS, IBM Db2, PostgreSQL, S3)
- Stream Governance: data lineage policy, schema compatibility levels, stream quality rules
- Multi-environment backbone creation (dev / staging / prod)

### `confluent-iac-terraform`

A focused skill for Confluent infrastructure-as-code with Terraform:

- Confluent Terraform provider (`confluentinc/confluent`) configuration
- Environment, cluster, topic, Schema Registry resource definitions
- Service account, API key, and RBAC ACL patterns
- Variable management with `variables.tf` and `terraform.tfvars`
- Output blocks for bootstrap servers and API key export

---

## Installation

### Step 1 — Install the skill(s)

The zip files are pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip data-streaming-confluent.zip
unzip confluent-iac-terraform.zip
```

This will create:
```
.bob/skills/data-streaming-confluent/SKILL.md
.bob/skills/confluent-iac-terraform/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable the desired skill(s). Bob will use them as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What data streaming skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Create a Confluent environment and Kafka cluster using Terraform for IBM Cloud"*
- *"Design Kafka topics for an IoT sensor events pipeline with 12 partitions and 7-day retention"*
- *"Generate a Python Avro producer with Schema Registry for Confluent on IBM Cloud"*
- *"Write a Flink SQL statement to aggregate sensor events by device and 5-minute windows"*
- *"Configure a Confluent IBM COS sink connector to archive Kafka topics to object storage"*

---

## What Bob Can Help You Build

With these skills, Bob can generate:

```
terraform/
├── providers.tf          # Confluent + IBM Cloud providers
├── variables.tf          # Environment-specific inputs
├── main.tf               # Topics, schemas, connectors, ACLs, service accounts
└── outputs.tf            # Bootstrap servers, API keys, .env output

python/
├── requirements.txt      # confluent-kafka[avro], fastavro
├── produce_messages.py   # Schema Registry-aware Avro producer
├── consume_messages.py   # Avro consumer with consumer-group management
└── sample-transactions.json

flink/
└── statements.sql        # Flink SQL stream processing jobs
```

---

## Prerequisites

Before using these skills, ensure you have:

- Confluent Cloud account on IBM Cloud
- Confluent Cloud API key and secret
- Terraform >= 1.3 (for infrastructure provisioning)
- Python 3.10+ with `confluent-kafka[avro]` and `fastavro`

## Skill Capabilities Summary

| Capability | data-streaming-confluent | confluent-iac-terraform |
|---|---|---|
| Terraform IaC | ✅ | ✅ |
| Kafka Topic Design | ✅ | ✅ |
| Avro/JSON Schema Registry | ✅ | ✅ |
| Python Producer/Consumer | ✅ | — |
| Apache Flink SQL | ✅ | — |
| Connector Config (COS, Db2) | ✅ | — |
| Stream Governance | ✅ | — |
| ACL & RBAC Patterns | ✅ | ✅ |

## Confluent Resource Reference

| Resource | Terraform Resource | Description |
|---|---|---|
| Environment | `confluent_environment` | Logical namespace for clusters |
| Kafka Cluster | `confluent_kafka_cluster` | Basic / Standard / Dedicated |
| Topic | `confluent_kafka_topic` | Event stream with partition config |
| Schema Registry | `confluent_schema_registry_cluster` | Avro/JSON/Protobuf schema store |
| Service Account | `confluent_service_account` | Auth principal for producers/consumers |
| API Key | `confluent_api_key` | Kafka and Schema Registry credentials |
| Connector | `confluent_connector` | Managed source/sink for external systems |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/data-streaming-confluent/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates incorrect Kafka producer code:**
1. Specify `confluent-kafka` not `kafka-python` in your request
2. Mention Schema Registry if using Avro serialization

## Related

- [`../README.md`](../README.md) — Data Streaming building block overview
- [`../assets/`](../assets/) — Deployable Confluent streaming assets
