# Context — Building Blocks

The **Context** use case brings together data in motion, data at rest, metadata, governance and observability so applications and AI agents can operate on information that is both **current and understandable**.

---

## When to Use

| Scenario | Building Block |
|---|---|
| AI agents need live facts plus historical or reference context | [`context-hub/`](context-hub/) |
| You need to stream, enrich and govern events in real time | [`real-time-streaming/`](real-time-streaming/) |
| Column names and schemas are cryptic or missing business context | [`metadata-enrichment/`](metadata-enrichment/) |
| Pipelines break and the impact is discovered too late | [`data-observability/`](data-observability/) |
| Text2SQL accuracy is poor because metadata is weak | [`metadata-enrichment/`](metadata-enrichment/) |

---

## Available Building Blocks

| Building Block | Path | Products | Best Fit |
|---|---|---|---|
| **Context Hub** | [`context-hub/`](context-hub/) | IBM Confluent + IBM watsonx.data + IBM watsonx.data intelligence | Build a governed context layer across streaming and enterprise data |
| **Real-Time Streaming** | [`real-time-streaming/`](real-time-streaming/) | IBM Confluent (Kafka + Flink + connectors + governance) | Capture, process and govern continuously changing events |
| **Metadata Enrichment & Data Quality** | [`metadata-enrichment/`](metadata-enrichment/) | IBM watsonx.data intelligence | Add business meaning, quality rules and governance metadata to technical assets |
| **Data Observability** | [`data-observability/`](data-observability/) | IBM watsonx.data integration + IBM Data Observability by Databand | Detect anomalies, failures and freshness/SLA issues in data operations |

---

## Getting Started

### Prerequisites

- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+** (for observability and metadata enrichment FastAPI assets)
- **Terraform ≥ 1.5** (for real-time-streaming IaC assets)
- Access to the IBM service listed in each building block's README header

### Common Setup Pattern

**For FastAPI assets** (data-observability, metadata-enrichment):
```bash
cd <building-block>/assets/<asset-name>
cp .env.example .env
# Edit .env: IBM_API_KEY and service-specific values
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
# Swagger docs → http://localhost:8080/docs
```

**For Terraform assets** (real-time-streaming):
```bash
cd assets/<asset-name>/code/terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: CONFLUENT_API_KEY, CONFLUENT_API_SECRET
terraform init && terraform plan && terraform apply
```

### IBM Bob — Your Fellow Developer

Each building block ships a **Bob Mode** (specialist persona) and **Bob Skills** (reusable knowledge packs).

**Install a Bob Mode**:
```powershell
# Windows
Copy-Item bob-modes/base-modes/<mode>.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/<mode>.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

**Install a Bob Skill**:
```bash
unzip bob-skills/<skill>.zip
```
Open IBM Bob → Skills panel → enable the skill.

---

## IBM Products Used

| Product | Role |
|---|---|
| **[IBM Confluent](https://www.ibm.com/products/confluent)** | Managed Kafka + Apache Flink + connectors + Stream Governance for real-time data |
| **[IBM watsonx.data](https://www.ibm.com/products/watsonx-data)** | Open hybrid lakehouse — storage, Presto, Spark, Iceberg |
| **[IBM watsonx.data intelligence](https://www.ibm.com/docs/en/watsonx/wdi/2.4.x?topic=data-enriching-your-assets)** | Metadata enrichment, business glossary, classifications, lineage, quality |
| **[IBM Data Observability by Databand](https://www.ibm.com/products/watsonx-data-integration/data-observability)** | Pipeline and dataset monitoring, anomaly detection, alerting |
