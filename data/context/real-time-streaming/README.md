# Real-Time Streaming

**IBM product**: IBM Confluent

Reference implementation for building and demonstrating event streaming, schema governance, stream processing, and infrastructure automation with IBM Confluent.

## What developers get

The main runnable asset is a **Supply Chain Risk Control Tower** that demonstrates:

- Kafka topics for enterprise and external events;
- JSON Schema contracts with Schema Registry;
- a Python streaming risk engine;
- reference Apache Flink SQL;
- Terraform for Confluent infrastructure;
- an IBM Carbon-based dashboard;
- integration points for IBM watsonx.ai and other IBM enterprise systems.

Apache Kafka and Apache Flink are implementation technologies within the IBM Confluent solution; the product anchor for this building block is IBM Confluent.

## Architecture

```text
ERP / suppliers / logistics / risk feeds
                 |
                 v
          IBM Confluent
     Kafka + Schema Registry
                 |
        +--------+---------+
        |                  |
        v                  v
 Python risk engine    Flink SQL reference
        |                  |
        +--------+---------+
                 |
                 v
 risk scores / recommendations / alerts
                 |
                 v
      dashboard / downstream apps
```

## Included assets

| Path | Purpose |
|---|---|
| [`assets/supply-chain-risk-control-tower/`](assets/supply-chain-risk-control-tower/) | Runnable supply-chain streaming reference solution |
| [`assets/live-context-for-supply-chain-resilience/`](assets/live-context-for-supply-chain-resilience/) | Full-stack AI demo: real-time risk detection + watsonx Orchestrate agents + Carbon React control tower |
| [`bob-skills/data-streaming-confluent.zip`](bob-skills/data-streaming-confluent.zip) | IBM Bob streaming skill |
| [`bob-skills/confluent-iac-terraform.zip`](bob-skills/confluent-iac-terraform.zip) | IBM Bob Terraform/IaC skill |

## Quick start

The supply-chain asset supports three useful developer modes.

### 1. Browser simulation

No Kafka cluster is required:

```bash
python -m http.server 8080 --directory assets/supply-chain-risk-control-tower/code/ui
```

### 2. Python dry run

Use the asset README to create the virtual environment, then run:

```bash
cd assets/supply-chain-risk-control-tower
python -m scrc.risk_engine --dry-run
```

### 3. Full IBM Confluent deployment

The asset includes Terraform, schemas, producers, a risk engine, and UI bridge. Start here:

[`assets/supply-chain-risk-control-tower/README.md`](assets/supply-chain-risk-control-tower/README.md)

## What to customize for a real project

- topic names, partitions, retention, and schema-compatibility policy;
- source/sink connectors;
- risk/scoring logic;
- Flink SQL transformations;
- IAM/service-account strategy;
- downstream application and alerting integrations.

The included risk model is a demo/reference implementation, not a universal production risk model.

## IBM references

- IBM Confluent: https://www.ibm.com/products/confluent
- Confluent Iceberg Sink integration with watsonx.data: https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-confluent-apache-iceberg-sink-connector
