
## Introduction

The **Technology Building Block** is a curated set of IBM capabilities developed by the Build Engineering team to accelerate solution delivery and demonstrate the value of the IBM technology stack, with a focus on Embeddable AI and Automation.

These building blocks showcase seamless integration across IBM Data & AI and Automation platforms, delivering reusable engineering patterns that simplify implementation and reduce time-to-value.

> **Note**: The building blocks are **AI-tool agnostic** — they can be used with **IBM Bob**, **Claude**, **GitHub Copilot**, or any other AI coding assistant. Bob is the recommended tool for the included modes and skills, but all runnable assets (FastAPI services, Python scripts, Terraform IaC) work independently of any AI assistant.

For more information, see the [documentation](https://ibm-self-serve-assets.github.io/building-blocks-docs/)

---

## What is the Technology Building Block?

The Building Block is a **reference implementation framework** that accelerates engineering and partner-facing engagements. It enables teams to:

- Rapidly **prototype, deploy, and validate** AI-powered applications.
- Seamlessly **integrate IBM services** like **watsonx.ai**, **watsonx.data**, **Instana**, **Turbonomic** and other IBM offerings with partner and open-source ecosystems.
- Present **business-aligned outcomes** showcasing seamless integration and value delivery through reusable building blocks that highlight the full potential of IBM's capabilities.

<img width="1393" height="740" alt="Screenshot 2026-06-23 at 1 21 34 PM" src="https://github.com/user-attachments/assets/a4458c25-220e-4fc4-831c-b03b01d1ac1a" />

Embeddable capabilities across key domains:

- **AI Agents** – APIs and SDKs from watsonx Orchestrate, watsonx.ai, and open source that enable orchestration and intelligent task automation.
- **Trusted AI** – Capabilities from watsonx.governance and watsonx.ai that support model validation, guardrails, and governance workflows.
- **Data for AI** – Solutions powered by watsonx.data and watsonx.ai for tasks such as Auto-RAG, model fine-tuning, and Text-to-SQL.
- **Build & Deploy** – Tools for infrastructure automation and AI-assisted development using Infrastructure-as-Code and code generation.
- **Modernize** – Observability capabilities including dependency mapping, anomaly detection, and application monitoring.
- **Optimize** – AI-driven solutions for cost optimization, risk detection, and automated remediation across application environments.

---

## Data — Intelligent Data Platform

The **[Data Building Blocks](data/README.md)** provide a composable foundation for making enterprise data connected, contextual, trusted, and ready for analytics and AI. They are organized into three use-case groups:

| Group | Building Block | Primary Products |
|---|---|---|
| **Context** | [Context Hub](data/context/context-hub/) | IBM Confluent + IBM watsonx.data + IBM watsonx.data intelligence |
| **Context** | [Real-Time Streaming](data/context/real-time-streaming/) | IBM Confluent (Kafka + Flink + connectors + governance) |
| **Context** | [Metadata Enrichment & Data Quality](data/context/metadata-enrichment/) | IBM watsonx.data intelligence |
| **Context** | [Data Observability](data/context/data-observability/) | IBM watsonx.data integration + IBM Data Observability by Databand |
| **Pipelines** | [RAG](data/pipelines/rag/) | IBM watsonx.data OpenRAG + OpenSearch |
| **Pipelines** | [UDI — Unstructured Data Integration](data/pipelines/udi/) | IBM watsonx.data integration + Docling for IBM watsonx |
| **Pipelines** | [Text2SQL](data/pipelines/text2sql/) | IBM watsonx.data intelligence |
| **Pipelines** | [ETL / ELT](data/pipelines/etl/) | IBM DataStage (watsonx.data integration) + IBM watsonx.data |
| **Pipelines** | [Data Sync](data/pipelines/data-sync/) | IBM Aspera Sync |
| **Query Engines** | [Zero-Copy Lakehouse](data/query-engines/zero-copy-lakehouse/) | IBM watsonx.data (Presto + Spark + Apache Iceberg) |
| **Query Engines** | [Serverless Vector](data/query-engines/serverless-vector/) | IBM watsonx.data + Astra DB Serverless |

[Explore all Data building blocks →](data/README.md)

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
