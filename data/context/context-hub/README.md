# Context Hub

**IBM products**: IBM Confluent, IBM watsonx.data, IBM watsonx.data intelligence

Context Hub is an **architectural pattern**, not a standalone IBM product. Use it when an application or AI agent needs a combination of **live operational events**, **queryable enterprise data**, and **governed business context**.

## When to use

Use this pattern when:

- AI agents need current operational state plus historical/reference data.
- Kafka events need to become queryable through an open lakehouse.
- Streaming data must be enriched with business metadata, quality, or lineage context.
- Multiple applications should consume the same governed context instead of building point-to-point integrations.

If you only need one capability, use its dedicated building block rather than implementing the full pattern.

## Reference architecture

```text
Apps / IoT / ERP / SaaS
          |
          v
     IBM Confluent
 Kafka + Flink + governance
          |
          | streaming data
          v
 Apache Iceberg / open tables
          |
          v
    IBM watsonx.data
 lakehouse + query engines
          |
          v
IBM watsonx.data intelligence
 metadata + quality + lineage
          |
          v
 Apps / analytics / AI agents
```

A common implementation path is to materialize selected Kafka topics into Apache Iceberg tables that are queryable from watsonx.data, then enrich those assets with business context in watsonx.data intelligence.

## Compose from this repository

| Capability | Building block |
|---|---|
| Kafka/Flink event streaming | [`../real-time-streaming/`](../real-time-streaming/) |
| Metadata, quality, lineage | [`../metadata-enrichment/`](../metadata-enrichment/) |
| Pipeline health and alerts | [`../data-observability/`](../data-observability/) |
| Lakehouse/federated query | [`../../query-engines/zero-copy-lakehouse/`](../../query-engines/zero-copy-lakehouse/) |
| Retrieval for AI | [`../../pipelines/rag/`](../../pipelines/rag/) |

## Developer path

There is no standalone runnable `assets/` implementation in this folder. Build the pattern by composing the relevant implementation assets from the building blocks above.

Recommended sequence:

1. Start with a working event stream in [Real-Time Streaming](../real-time-streaming/).
2. Materialize the required stream into a watsonx.data-supported lakehouse target where appropriate.
3. Validate the data with watsonx.data query engines.
4. Enrich/catalog the resulting assets through [Metadata Enrichment](../metadata-enrichment/).
5. Add [Data Observability](../data-observability/) for operational pipeline monitoring.
6. Add [RAG](../../pipelines/rag/) only when the consumer requires grounded natural-language access.

## Prerequisites

Depending on the selected composition:

- IBM Confluent environment and Kafka cluster
- IBM watsonx.data instance with the required engine/catalog
- IBM watsonx.data intelligence for metadata/governance
- IBM Cloud IAM credentials
- Source-system and target-storage access

## IBM Bob

This folder includes Bob guidance under [`bob-modes/`](bob-modes/) and [`bob-skills/`](bob-skills/). The ZIP implementations are currently marked **Coming soon**; use the constituent building-block Bob assets where available.

## IBM references

- IBM Confluent: https://www.ibm.com/products/confluent
- IBM watsonx.data: https://www.ibm.com/products/watsonx-data
- IBM watsonx.data intelligence: https://www.ibm.com/products/watsonx-data-intelligence
- Confluent Apache Iceberg Sink Connector with watsonx.data: https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-confluent-apache-iceberg-sink-connector
