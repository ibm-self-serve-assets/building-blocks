
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

![alt text](image.png)

Embeddable capabilities across key domains:

- **AI Agents** – APIs and SDKs from watsonx Orchestrate, watsonx.ai, and open source that enable orchestration and intelligent task automation.
- **Trusted AI** – Capabilities from watsonx.governance and watsonx.ai that support model validation, guardrails, and governance workflows.
- **Data for AI** – Solutions powered by watsonx.data and watsonx.ai for tasks such as Auto-RAG, model fine-tuning, and Text-to-SQL.
- **Automation** – Automated engineering patterns across Operate (IaC, configuration), Secure (secrets, continuous compliance, quantum-safe), and Optimize (observability, FinOps, performance).

---

## AI Control Plane — Agents, Control, and Engineering

The **[AI Control Plane](ai/README.md)** is a composable foundation for building, controlling, and engineering enterprise AI systems. Its building blocks are organized into three groups:

| Group | Building Block | Primary Products / Capabilities |
|---|---|---|
| **Agents** | [Agent Builder](ai/agents/agent-builder/) | IBM watsonx Orchestrate ADK + Tools + Knowledge Bases |
| **Agents** | [Multi-Agent Orchestration](ai/agents/multi-agent-orchestration/) | IBM watsonx Orchestrate + AI Gateway + MCP/A2A |
| **Control** | [Agent Ops](ai/control/agent-ops/) | IBM watsonx Orchestrate + watsonx.governance — evaluation, red-teaming, traces |
| **Control** | [Guardrails](ai/control/guardrails/) | Agent Controls + Real-Time Guardrails SDK (watsonx.governance) |
| **Control** | [Cost Management](ai/control/cost-management/) | Per-interaction cost and token tracking with Langfuse |
| **Control** | [Compliance](ai/control/compliance/) | IBM watsonx.governance + OpenPages — regulation mapping and Enforcement Tracking |
| **Engineering** | [Agentic SDLC](ai/engineering/agentic-sdlc/) | IBM Bob + In-IDE Agentic Development |
| **Engineering** | [Code Modernization](ai/engineering/code-modernization/) | IBM Bob + Legacy Refactoring + Java/Maximo |
| **Engineering** | [headlessbob](ai/engineering/headless-bob/) | Node.js + REST/ACP APIs + Threads UI |
| **Engineering** | [Integrate as Code](ai/engineering/integrate-as-code/) | IBM iPaaS + watsonx Orchestrate Workflows |

[Explore the AI Control Plane →](ai/README.md)

---

## Automation — Enterprise IT & Cloud Automation

The **[Automation Building Blocks](automation/README.md)** deliver automated engineering patterns, infrastructure code, observability, compliance, and cost optimization capabilities. They are organized into three domains:

| Domain | Building Block | Primary Products / Capabilities |
|---|---|---|
| **Operate** | [Infrastructure as Code](automation/operate/infrastructure-as-code/) | Terraform + OpenTofu + JMeter + Multi-Cloud |
| **Operate** | [Configure & Automate](automation/operate/configure-and-automate/) | Ansible + Automation Playbooks |
| **Operate** | [Workload Orchestration & Scheduling](automation/operate/workload-orchestration-and-scheduling/) | IBM Workload Automation + Enterprise Scheduling |
| **Operate** | [Asset Management](automation/operate/asset-management/) | IBM Maximo Application Suite + Code Modernization |
| **Secure** | [Non-Human Identity & Secret Management](automation/secure/non-human-identity-and-secret-management/) | IBM Security Verify + HashiCorp Vault |
| **Secure** | [Application Risk & Continuous Compliance](automation/secure/application-risk-and-continuous-compliance/) | IBM Concert + Continuous Resilience |
| **Secure** | [Cryptographic & Quantum-Safe Readiness](automation/secure/cryptographic-and-quantum-safe-readiness/) | IBM Quantum Safe Explorer + IBM Guardium |
| **Optimize** | [Full-Stack Application Observability](automation/optimize/full-stack-application-observability/) | IBM Instana + OpenTelemetry |
| **Optimize** | [Application Performance](automation/optimize/application-performance/) | IBM Turbonomic |
| **Optimize** | [Technology Financial Management & FinOps](automation/optimize/technology-financial-management-and-finops/) | IBM Apptio + Cloudability |
| **Optimize** | [Network Performance Management](automation/optimize/network-performance-management/) | Network Observability & Diagnostics |
| **Optimize** | [Budget & Forecasting](automation/optimize/budget-and-forecasting/) | IBM Planning Analytics (TM1) |

[Explore all Automation building blocks →](automation/README.md)

---

## Data — Intelligent Data Platform

The **[Data Building Blocks](data/README.md)** provide a composable foundation for making enterprise data connected, contextual, trusted, and ready for analytics and AI. They are organized into three pillars:

| Pillar | Building Block | Primary Products |
|---|---|---|
| **Streamhouse** | [Real-Time Streaming](data/streamhouse/real-time-streaming/) | IBM Confluent — Connectors and Kafka |
| **Streamhouse** | [Transform](data/streamhouse/transform/) | IBM Confluent (Apache Flink) |
| **Streamhouse** | [Govern](data/streamhouse/govern/) | IBM Confluent — Stream Governance |
| **Streamhouse** | [Serve](data/streamhouse/serve/) | IBM Confluent — RTCE and Tableflow |
| **Pipelines** | [RAG](data/pipelines/rag/) | IBM watsonx.data OpenRAG + IBM watsonx.ai |
| **Pipelines** | [Unstructured Data Integration](data/pipelines/udi/) | IBM watsonx.data integration — UDI |
| **Pipelines** | [Text2SQL](data/pipelines/text2sql/) | IBM watsonx.data intelligence |
| **Pipelines** | [ETL / ELT](data/pipelines/etl/) | IBM watsonx.data integration — DataStage |
| **Pipelines** | [Data Sync](data/pipelines/data-sync/) | IBM Aspera Sync |
| **Lakehouse** | [Metadata Enrichment & Quality](data/lakehouse/metadata-enrichment/) | IBM watsonx.data intelligence |
| **Lakehouse** | [Data Observability](data/lakehouse/data-observability/) | IBM watsonx.data integration — Databand |
| **Lakehouse** | [Zero-Copy Lakehouse](data/lakehouse/zero-copy-lakehouse/) | IBM watsonx.data (Presto + Spark + Apache Iceberg) |
| **Lakehouse** | [Serverless Vector](data/lakehouse/serverless-vector/) | IBM watsonx.data — Astra DB Serverless |

[Explore all Data building blocks →](data/README.md)

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).
