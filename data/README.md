# Data Building Blocks

Reusable implementation assets for the **IBM Data and AI portfolio**, organized by **Context**, **Pipelines**, and **Query Engines**.

This repository is intentionally code-first. Each building block gives developers enough information to understand the pattern, identify the IBM products involved, find the runnable/reference assets, and get to the detailed setup instructions quickly.

> Open-source technologies such as Apache Kafka, Apache Flink, Apache Iceberg, OpenSearch, and Milvus appear only where the implementation uses them. The building-block product anchor remains part of the IBM portfolio.

## Repository map

| Group | Building block | IBM product anchor | What you can build |
|---|---|---|---|
| Context | [Context Hub](context/context-hub/) | IBM Confluent, IBM watsonx.data, IBM watsonx.data intelligence | Live + governed context for apps and AI |
| Context | [Real-Time Streaming](context/real-time-streaming/) | IBM Confluent | Event streaming, schema governance, stream processing |
| Context | [Metadata Enrichment & Data Quality](context/metadata-enrichment/) | IBM watsonx.data intelligence | Metadata enrichment, quality, lineage |
| Context | [Data Observability](context/data-observability/) | IBM watsonx.data integration — Data Observability | Pipeline health, anomaly detection, alerts |
| Pipelines | [RAG](pipelines/rag/) | IBM watsonx.data OpenRAG, IBM watsonx.ai | Retrieval and grounded generation |
| Pipelines | [Unstructured Data Integration](pipelines/udi/) | IBM watsonx.data integration — UDI | Parse, enrich, chunk, and prepare documents |
| Pipelines | [Text2SQL](pipelines/text2sql/) | IBM watsonx.data intelligence | Natural-language-to-SQL with governed metadata |
| Pipelines | [ETL / ELT](pipelines/etl/) | IBM watsonx.data integration — DataStage | Structured batch transformation |
| Pipelines | [Data Sync](pipelines/data-sync/) | IBM Aspera Sync | High-speed file/directory synchronization |
| Query Engines | [Zero-Copy Lakehouse](query-engines/zero-copy-lakehouse/) | IBM watsonx.data | Federated/lakehouse SQL across supported sources |
| Query Engines | [Serverless Vector](query-engines/serverless-vector/) | IBM watsonx.data — Astra DB service | Vector search and NoSQL application patterns |

## How to use this repository

Start at a building-block README and then move into the implementation you need:

```text
<building-block>/
├── README.md        # developer overview, architecture, quick start, guardrails
├── assets/          # runnable/reference implementations, when present
├── bob-modes/       # IBM Bob modes, when present
└── bob-skills/      # IBM Bob skills, when present
```

A typical developer flow is:

1. Open the building-block README and confirm the capability matches your use case.
2. Review **Architecture / flow** to understand the IBM product boundary.
3. Pick a runnable/reference asset from **Included assets**.
4. Follow the detailed `assets/<asset>/README.md`.
5. Use IBM Bob modes/skills, if present, to accelerate implementation or troubleshooting.
6. Validate current product, model, API, and regional availability before production deployment.

## Common prerequisites

Most runnable assets expect some combination of:

- IBM Cloud account and access to the IBM products named by the building block
- IBM Cloud API key: https://cloud.ibm.com/iam/apikeys
- Python and/or Docker versions listed in the asset README
- Service-specific credentials supplied through `.env`, environment variables, or a secrets manager
- Network access between source/target services
- IAM roles required by the target IBM service

Never commit API keys, database passwords, application tokens, Terraform state containing secrets, or populated `.env` files.

## Model-dependent assets

Model IDs and availability change independently of this repository. The examples in code and `.env.example` files are defaults, not a permanent support contract.

Check these IBM pages before deployment:

- Supported foundation models: https://www.ibm.com/docs/en/watsonx/saas?topic=solutions-supported-foundation-models
- Supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- Foundation model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle

Current examples used by relevant assets include:

```text
ibm/granite-embedding-278m-multilingual
ibm/granite-4-h-small
```

Always confirm current availability for your region/deployment before relying on an example model.

## IBM watsonx.data availability

Some watsonx.data services are deployment- and region-specific. Check the current matrix before provisioning:

https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-feature_parity_wxd

## IBM Bob

`bob-modes/` and `bob-skills/` are optional accelerators. A runnable asset does not require Bob unless its own README explicitly says so.

Where a mode or skill is marked **Coming soon**, the repository contains guidance only; do not assume a ZIP implementation is already available.
