# Context Hub

**Core Capability**: Context
**IBM Products**: IBM Confluent, IBM watsonx.data, IBM watsonx.data intelligence
**Product Components**: Apache Kafka; Apache Flink; Confluent connectors; Stream Governance; watsonx.data open lakehouse; Confluent Apache Iceberg Sink Connector; Confluent Tableflow; watsonx.data intelligence metadata enrichment

## Overview

**Context Hub** is a solution building block for combining **real-time events**, **enterprise data**, and **business metadata/governance** into a reusable context layer for applications, analytics and AI agents.

Most data platforms excel at storing and querying data at rest. Context Hub adds the **when** and **what it means** — live events from IBM Confluent streaming, enriched enterprise data from IBM watsonx.data, and business context from IBM watsonx.data intelligence — all accessible from a single governed foundation.

> **Architectural note**: Context Hub is an **architectural pattern**, not a single product SKU. The constituent building blocks are [Real-Time Streaming](../real-time-streaming/README.md), [Metadata Enrichment](../metadata-enrichment/README.md), and [Data Observability](../data-observability/README.md). The primary products are IBM Confluent, IBM watsonx.data, and IBM watsonx.data intelligence.

---

## When to Use

Use Context Hub when:

- AI agents need **real-time operational facts** (from IBM Confluent) plus historical or reference context (from IBM watsonx.data).
- Streaming events need to be enriched with governed enterprise data before downstream use.
- Multiple teams need a **reusable source of context** instead of building separate point-to-point integrations.
- You want live streaming data to become available for SQL analytics in open Iceberg table format.
- Governance, metadata, and lineage need to apply consistently across data used by analytics and AI.

---

## Business Value

| Outcome | What It Means |
|---|---|
| **Current context for AI** | Agents and applications can react to continuously changing operational state — not just last night's batch snapshot |
| **Trusted reuse** | Business meaning, lineage and governance make the same context safer to reuse across teams and AI systems |
| **Less point-to-point integration** | A streaming backbone plus open lakehouse reduces custom copies and brittle hand-offs |
| **Faster time to decision** | Real-time events become queryable and consumable without waiting for nightly batch windows |
| **Better explainability** | Metadata and lineage help users understand where context came from and how it changed |

---

## Reference Architecture

```
Systems of record                  IBM Confluent                     IBM watsonx.data
(Apps · IoT · SaaS)                Kafka + Connectors                open hybrid lakehouse
        │                                │                                   │
        └──── Managed connectors ────────┘                                   │
                                         │                                   │
                                  Apache Flink                               │
                                  filter / join / enrich                     │
                                         │                                   │
                               Kafka topics / Tableflow ──── Iceberg Sink ──▶│
                                         │                                   │
                               Stream Governance                  watsonx.data intelligence
                               Schema Registry                    metadata / lineage / terms / policy
                                         │                                   │
                                         └────────────────────────────────────┘
                                                              │
                                                    AI agents / Analytics / Automation
```

**Key integration point**: The **Confluent Apache Iceberg Sink Connector** writes Kafka topic data into Apache Iceberg tables inside IBM watsonx.data for near-real-time analytics. **Confluent Tableflow** provides a managed path for materializing Kafka topics as Iceberg or Delta tables.

---

## Core Product Roles

| Product | Role in Context Hub |
|---|---|
| **IBM Confluent** | Real-time backbone — Kafka event streaming, managed connectors, Apache Flink stream processing, Schema Registry, Stream Governance |
| **IBM watsonx.data** | Open hybrid data foundation — structured and unstructured data, multi-engine processing (Presto / Spark), open Iceberg table format, AI-ready data access |
| **IBM watsonx.data intelligence** | Business terms, AI-generated names and descriptions, classifications, relationships, lineage, quality signals and governance context |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **IBM Confluent** environment on IBM Cloud with at least one Kafka cluster
- **IBM watsonx.data** instance with Iceberg catalog and Presto engine
- **IBM watsonx.data intelligence** instance (for metadata enrichment and lineage)

### Recommended Implementation Path

Start with the smallest combination that solves the immediate use case:

1. **Real-time events only** → Use the [Real-Time Streaming](../real-time-streaming/README.md) building block.
2. **Real-time + open lakehouse** → Add the [Confluent Apache Iceberg Sink Connector](https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-confluent-apache-iceberg-sink-connector) to materialize Kafka topics as Iceberg tables in watsonx.data.
3. **Add business context** → Use the [Metadata Enrichment](../metadata-enrichment/README.md) building block to enrich the tables and columns written by the streaming layer.
4. **Add observability** → Use the [Data Observability](../data-observability/README.md) building block to monitor the streaming and ingestion pipelines.

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The Context Hub building block ships a **Bob Mode** and **Bob Skills** to assist with architecture, connector configuration, Flink SQL, Iceberg sink setup, and watsonx.data intelligence integration.

**Install the Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/context-hub-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/context-hub-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **Context Hub Builder** mode appears in the mode selector.

**Install Bob Skills**:
```bash
unzip bob-skills/confluent-watsonxdata-context.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI mode for Context Hub architecture, streaming-to-lakehouse integration, and metadata enrichment
  - **Install**: copy [`bob-modes/base-modes/context-hub-builder.zip`](./bob-modes/base-modes/context-hub-builder.zip) to your Bob modes directory
  - Assists with connector setup, Flink SQL, Iceberg sink configuration, and watsonx.data intelligence enrichment design

## Bob Skills

| Skill | Zip | Capabilities |
|---|---|---|
| `confluent-watsonxdata-context` | [`bob-skills/confluent-watsonxdata-context.zip`](./bob-skills/confluent-watsonxdata-context.zip) | IBM Confluent Kafka + Flink + connectors + Iceberg Sink → watsonx.data integration; watsonx.data intelligence metadata enrichment for streaming data |

See [`bob-skills/README.md`](./bob-skills/README.md) for installation instructions.

---

## Constituent Building Blocks

Context Hub is the **combined pattern**. The individual capabilities have their own dedicated building blocks:

| Building Block | Path | Capability |
|---|---|---|
| Real-Time Streaming | [`../real-time-streaming/`](../real-time-streaming/) | IBM Confluent — Kafka, Flink, connectors, Stream Governance |
| Metadata Enrichment | [`../metadata-enrichment/`](../metadata-enrichment/) | IBM watsonx.data intelligence — profiling, terms, quality, lineage |
| Data Observability | [`../data-observability/`](../data-observability/) | IBM Databand — pipeline and dataset monitoring, anomaly detection |

---

## IBM Cloud References

- [IBM Confluent](https://www.ibm.com/products/confluent)
- [IBM watsonx.data](https://www.ibm.com/products/watsonx-data)
- [IBM watsonx.data intelligence — Metadata Enrichment](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-enriching-your-assets)
- [Confluent Apache Iceberg Sink Connector for watsonx.data](https://www.ibm.com/docs/en/watsonxdata/saas?topic=integrations-integrating-confluent-apache-iceberg-sink-connector)
- [Confluent Cloud for Apache Flink](https://docs.confluent.io/cloud/current/flink/overview.html)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
