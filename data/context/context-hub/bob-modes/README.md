# Bob Mode for Context Hub

Custom IBM Bob mode configuration for the **Context Hub** building block — combining **IBM Confluent** real-time streaming with **IBM watsonx.data** and **IBM watsonx.data intelligence** to deliver a governed, reusable context layer for applications, analytics and AI agents.

---

## Overview

This Bob mode provides specialized assistance for:

- **Streaming-to-Lakehouse Integration**: Configuring the Confluent Apache Iceberg Sink Connector to materialize Kafka topic data as Iceberg tables in IBM watsonx.data
- **Confluent Tableflow**: Setting up Tableflow for managed topic materialization to open table formats
- **Apache Flink SQL**: Writing and deploying Flink SQL transformations to filter, join, and enrich streams
- **IBM watsonx.data intelligence**: Enriching Iceberg tables and columns with business terms, descriptions, and governance context
- **Context Hub Architecture**: Designing the end-to-end pattern from event sources through streaming, lakehouse, and metadata enrichment to AI consumers

---

## What's Included

> **Coming soon** — `context-hub-builder.zip` is not yet committed to this repository. The documentation below describes the intended mode capabilities. Check [`base-modes/`](base-modes/) for availability.

- **`base-modes/context-hub-builder.zip`**: Bob mode configuration for Context Hub development

---

## Mode Capabilities

- IBM Confluent Kafka topic design and partition strategy
- Confluent managed connector setup for IBM Cloud sources and sinks
- Apache Flink SQL for real-time filtering, joining, enrichment and aggregation
- Confluent Stream Governance — Schema Registry, data contracts, lineage
- Confluent Apache Iceberg Sink Connector configuration for watsonx.data
- IBM watsonx.data Iceberg catalog and table schema design for streaming targets
- IBM watsonx.data intelligence metadata enrichment for streaming-sourced tables
- IBM Cloud IAM authentication for Confluent and watsonx.data APIs
- Context Hub reference architecture guidance and component selection

---

## When to Use This Mode

- Designing a Context Hub architecture combining Confluent and watsonx.data
- Configuring the Iceberg Sink Connector to write Kafka topics into watsonx.data
- Writing Flink SQL to enrich or transform a stream before it reaches the lakehouse
- Enriching watsonx.data tables written by streaming pipelines with business metadata
- Troubleshooting connector configuration, schema compatibility, or Flink SQL errors

---

## Installing the Bob Mode

**Windows**
```powershell
Copy-Item base-modes/context-hub-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**
```bash
cp base-modes/context-hub-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available in the mode selector.

---

## Related

- [`../bob-skills/`](../bob-skills/) — Context Hub knowledge skill
- [`../README.md`](../README.md) — Context Hub building block overview
- [`../../real-time-streaming/`](../../real-time-streaming/) — Real-Time Streaming building block
- [`../../metadata-enrichment/`](../../metadata-enrichment/) — Metadata Enrichment building block
