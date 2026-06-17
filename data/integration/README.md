# Integration Capabilities

This directory contains building blocks for data integration — enabling data pipelines, streaming, and observability for AI applications.

---

## When to Use

| Scenario | Building Block |
|---|---|
| Need AI to generate a DataStage ingestion pipeline from a plain-English description | [`data-pipeline-ai-generated/`](data-pipeline-ai-generated/) |
| Ingest PDFs, DOCX, or HTML documents into a structured pipeline | [`data-pipeline-ai-generated/data-ingestion/`](data-pipeline-ai-generated/data-ingestion/) |
| Process real-time Kafka event streams with Flink SQL or Python producers/consumers | [`data-streaming/`](data-streaming/) |
| Provision a complete Confluent environment as Terraform IaC | [`data-streaming/`](data-streaming/) |
| Monitor data pipeline health, surface quality anomalies, and track SLA breaches | [`data-observability/`](data-observability/) |
| Emit OpenLineage events from any Python, DataStage, or Spark pipeline | [`data-observability/`](data-observability/) |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+** (for observability FastAPI assets)
- **Terraform ≥ 1.5** (for data-streaming IaC)
- Access to the IBM service listed in each building block's README header

### Common Setup Pattern

**For FastAPI assets** (data-observability):
```bash
cd <building-block>/assets/<asset-name>
cp .env.example .env
# Edit .env: IBM_API_KEY and service-specific values
pip install -r requirements.txt
uvicorn app.server:app --host 0.0.0.0 --port 8080
# Swagger docs → http://localhost:8080/docs
```

**For Terraform assets** (data-streaming):
```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: CONFLUENT_API_KEY, CONFLUENT_API_SECRET
terraform init && terraform plan && terraform apply
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs) so Bob already knows the APIs, schemas, and IBM Cloud patterns for the capability you're working on.

**Install a Bob Mode** — give Bob a specialist persona:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — the mode appears in the mode selector. Switch to it before starting development.

**Install a Bob Skill** — teach Bob the details of this building block:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill. Bob will use it as active context for every prompt in this workspace.

---

## Building Blocks

### 1. Data Pipeline (AI Generated)
**Location**: [`data-pipeline-ai-generated/`](data-pipeline-ai-generated/)
**IBM Products**: IBM Bob, IBM DataStage, IBM UDI, IBM Docling, IBM watsonx.data
**Product Components**: DataStage connectors; CDC (Change Data Capture); Docling document parsing; Unstructured Data Integration (UDI); IBM COS

Build and run batch, real-time, replication, and unstructured data pipelines with observability and hybrid integration support. AI-generated pipelines created by IBM Bob from a plain-English description.

**Key Features**:
- Structured data ingestion (DB2, PostgreSQL, MySQL, Oracle) via DataStage CDC connectors
- Unstructured data ingestion (PDF, DOCX, HTML, images) via IBM Docling + UDI
- AI-generated pipeline code via Bob modes and skills
- Schema mapping, validation, and error handling

**Bob Assets**:
- `data-ingestion/bob-modes/base-modes/data-ingestion.zip` — Bob mode for AI-generated pipelines
- `data-ingestion/bob-skills/data-ingestion-structured.zip` — Structured ingestion skill
- `data-ingestion/bob-skills/data-ingestion-unstructured.zip` — Unstructured ingestion skill

[View Details →](data-pipeline-ai-generated/)

---

### 2. Data Streaming
**Location**: [`data-streaming/`](data-streaming/)
**IBM Products**: Confluent (on IBM Cloud)
**Product Components**: Apache Kafka topics; Confluent Schema Registry; Apache Flink SQL; Confluent Connectors; Stream Governance; Terraform IaC

> **Technology**: This block uses **Confluent** (the streaming platform) on IBM Cloud. "Confluent Hub" refers specifically to the connector marketplace — the platform itself is Confluent.

Supports real-time event ingestion, streaming pipelines, and stream processing for operational and analytical use cases using Confluent on IBM Cloud. Includes Terraform IaC for full environment provisioning and Python producer/consumer patterns.

**Key Features**:
- Apache Kafka topic and Schema Registry management
- Apache Flink SQL stream processing
- Confluent Terraform provider — provision entire environments as code
- Python producer/consumer with Avro schema support
- Source and sink connectors for IBM services (COS, Db2, watsonx.data)

**Bob Assets**:
- `bob-skills/data-streaming-confluent.zip` — Confluent Terraform IaC + Flink SQL + Python patterns skill

[View Details →](data-streaming/)

---

### 3. Data Observability
**Location**: [`data-observability/`](data-observability/)
**IBM Products**: IBM Databand
**Product Components**: Databand REST API v1; OpenLineage HTTP transport; IBM Cloud IAM; IBM Cloud Object Storage

Monitor and ensure data pipeline quality and reliability using IBM Databand — IBM's enterprise data observability platform. Track every pipeline run, surface data quality anomalies, enforce SLA thresholds, and maintain a complete OpenLineage-compliant lineage graph.

**Key Features**:
- Pipeline run monitoring and health status via Databand REST API v1
- OpenLineage event emission from Python, DataStage, and Spark pipelines
- Alert policy management (null-rate, schema-drift, SLA-breach, quality-score)
- IBM COS archiving of pipeline run reports
- FastAPI service for Databand API integration

**Bob Assets**:
- `bob-modes/base-modes/data-observability-builder.zip` — Bob mode for observability development
- `bob-skills/databand-pipeline-setup.zip` — Databand pipeline onboarding skill

[View Details →](data-observability/)

---

## Quick Start

1. Choose the integration capability that matches your needs
2. Navigate to the specific building block directory
3. Follow the README instructions for setup and configuration

## Use Cases

- **AI-Generated Pipelines**: Describe your ingestion requirement to Bob → get production-ready code
- **Real-time Processing**: Process streaming data with Confluent Kafka + Flink SQL
- **Batch Ingestion**: DataStage CDC pipelines for structured databases
- **Unstructured Ingestion**: IBM Docling + UDI for documents, PDFs, and images
- **Pipeline Monitoring**: Track pipeline health and data quality with IBM Databand
- **Hybrid Integration**: Connect on-premises and IBM Cloud data sources
