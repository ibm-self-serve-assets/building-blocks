# Data Building Blocks

Reusable implementation assets for IBM Data and AI products. Building blocks are grouped by **Context**, **Pipelines**, and **Query Engines**.

> Product names in this repository are IBM portfolio products. Open-source projects such as Apache Kafka, Apache Flink, Apache Iceberg, OpenSearch, and Milvus are referenced only where they are implementation technologies within an IBM product or solution pattern.

## Building blocks

| Group | Building block | IBM product anchor |
|---|---|---|
| Context | [Context Hub](context/context-hub/) | IBM Confluent, IBM watsonx.data, IBM watsonx.data intelligence |
| Context | [Real-Time Streaming](context/real-time-streaming/) | IBM Confluent |
| Context | [Metadata Enrichment & Data Quality](context/metadata-enrichment/) | IBM watsonx.data intelligence |
| Context | [Data Observability](context/data-observability/) | IBM watsonx.data integration — Data Observability |
| Pipelines | [RAG](pipelines/rag/) | IBM watsonx.data OpenRAG, IBM watsonx.ai |
| Pipelines | [Unstructured Data Integration](pipelines/udi/) | IBM watsonx.data integration — Unstructured Data Integration |
| Pipelines | [Text2SQL](pipelines/text2sql/) | IBM watsonx.data intelligence |
| Pipelines | [ETL / ELT](pipelines/etl/) | IBM watsonx.data integration — DataStage |
| Pipelines | [Data Sync](pipelines/data-sync/) | IBM Aspera Sync |
| Query Engines | [Zero-Copy Lakehouse](query-engines/zero-copy-lakehouse/) | IBM watsonx.data |
| Query Engines | [Serverless Vector](query-engines/serverless-vector/) | IBM watsonx.data — Astra DB service |

## Repository convention

A building block can contain:

```text
<building-block>/
├── README.md        # scope, prerequisites, assets, IBM references
├── assets/          # runnable/reference implementation
├── bob-modes/       # IBM Bob modes, when available
└── bob-skills/      # IBM Bob skills, when available
```

Detailed setup belongs in the relevant `assets/<asset>/README.md`. Top-level READMEs intentionally stay concise.

## Common prerequisites

- IBM Cloud account and the IBM services required by the selected building block
- IBM Cloud API key: https://cloud.ibm.com/iam/apikeys
- Python version and other runtime prerequisites listed by the specific asset
- Secrets supplied through environment variables or a secrets manager; never commit credentials

## Keep model and service information current

Model and regional availability changes over time. Before deployment, validate against IBM's current documentation:

- IBM watsonx.ai supported foundation models: https://www.ibm.com/docs/en/watsonx/saas?topic=solutions-supported-foundation-models
- IBM watsonx.ai supported embedding models: https://www.ibm.com/docs/en/watsonx/saas?topic=models-supported-embedding
- IBM watsonx.ai foundation model lifecycle: https://www.ibm.com/docs/en/watsonx/saas?topic=model-foundation-lifecycle
- IBM watsonx.data cloud availability: https://cloud.ibm.com/docs/watsonxdata?topic=watsonxdata-feature_parity_wxd
- IBM watsonx.data integration: https://www.ibm.com/docs/en/software-hub/5.4.x?topic=services-watsonxdata-integration

The model IDs in `.env.example` files are working examples, not a substitute for the current IBM support matrix.

## IBM Bob

Where present, `bob-modes/` and `bob-skills/` provide IBM Bob-specific assistance for the building block. Runnable assets do not require Bob unless their README explicitly says otherwise.
