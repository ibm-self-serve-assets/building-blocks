# Bob Skills for Context Hub

Bob skills for the **Context Hub** building block — IBM Confluent streaming integration with **IBM watsonx.data** and **IBM watsonx.data intelligence** for a governed, reusable context layer.

## Overview

This skill gives IBM Bob expert knowledge of the integration between IBM Confluent Kafka, Confluent Tableflow, the Confluent Apache Iceberg Sink Connector, IBM watsonx.data, and IBM watsonx.data intelligence — enabling Bob to assist with architecture, connector configuration, Flink SQL, schema governance, and metadata enrichment for streaming-sourced data.

## Available Skills

> **Coming soon** — the Bob Skill zip for this building block has not yet been committed to this repository.

| Skill | Use When |
|---|---|
| `confluent-watsonxdata-context` | Building the streaming-to-lakehouse integration and enriching streaming data with governed business context |

---

### `confluent-watsonxdata-context`

A comprehensive skill for the Context Hub pattern:

- IBM Confluent Kafka topic design and Confluent Cloud environment setup
- Confluent managed connector catalog — source and sink connectors for IBM Cloud services
- Apache Flink SQL on Confluent Cloud — filter, join, window, and enrich patterns
- Confluent Stream Governance — Schema Registry, data contracts, compatibility rules, stream lineage
- Confluent Apache Iceberg Sink Connector — configuration, schema mapping, partition design, watsonx.data target
- Confluent Tableflow — managed topic-to-Iceberg materialization
- IBM watsonx.data Iceberg catalog configuration for streaming-written tables
- IBM watsonx.data intelligence metadata enrichment API for business terms, descriptions, classifications
- IBM Cloud IAM authentication for both Confluent and watsonx.data APIs
- Context Hub reference architecture — component selection and integration sequencing

---

## Installation

Installation instructions will be added when the zip is available.

---

## Usage Examples

- *"How do I configure the Confluent Apache Iceberg Sink Connector to write into a watsonx.data catalog?"*
- *"Write a Flink SQL statement that joins an order stream with a product reference stream and outputs enriched events"*
- *"What Schema Registry settings should I use for a Kafka topic that will be consumed by an Iceberg sink?"*
- *"How do I enrich the columns written by my streaming pipeline using watsonx.data intelligence metadata enrichment?"*
- *"Design a Context Hub architecture for an AI agent that needs live supply chain events plus historical order data"*

---

## Prerequisites

Before using this skill, ensure you have:

- IBM Cloud API key ([IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys))
- IBM Confluent environment on IBM Cloud
- IBM watsonx.data instance with Iceberg catalog
- IBM watsonx.data intelligence instance (for metadata enrichment)

---

## Related

- [`../bob-modes/`](../bob-modes/) — Context Hub Builder Bob Mode
- [`../README.md`](../README.md) — Context Hub building block overview
- [`../../real-time-streaming/bob-skills/`](../../real-time-streaming/bob-skills/) — Real-Time Streaming skills
- [`../../metadata-enrichment/`](../../metadata-enrichment/) — Metadata Enrichment building block
