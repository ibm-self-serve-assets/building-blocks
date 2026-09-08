# Query Engines — Building Blocks

The **Query Engines** use case provides fit-for-purpose execution for SQL analytics, large-scale processing, open lakehouse interoperability and vector retrieval — matching the engine to the workload rather than routing everything through a single technology.

---

## When to Use

| If you need to… | Building Block |
|---|---|
| Query distributed data across platforms without copying it | [`zero-copy-lakehouse/`](zero-copy-lakehouse/) |
| Run interactive SQL analytics across a governed lakehouse | [`zero-copy-lakehouse/`](zero-copy-lakehouse/) — Presto |
| Large-scale data processing, transformation or ML preparation | [`zero-copy-lakehouse/`](zero-copy-lakehouse/) — Spark |
| Store embeddings and run vector similarity search for RAG | [`serverless-vector/`](serverless-vector/) |
| Elastic, API-driven vector storage without cluster management | [`serverless-vector/`](serverless-vector/) |

---

## Available Building Blocks

| Building Block | Path | Products | Best Fit |
|---|---|---|---|
| **Zero-Copy Lakehouse** | [`zero-copy-lakehouse/`](zero-copy-lakehouse/) | IBM watsonx.data: Presto + Spark + Apache Iceberg | Federated access, interactive SQL, large-scale processing and open tables |
| **Serverless Vector** | [`serverless-vector/`](serverless-vector/) | IBM watsonx.data + Astra DB Serverless | Vector similarity search for RAG, semantic search and AI applications |

---

## Getting Started

### Prerequisites

All Query Engine building blocks require:
- **IBM Cloud API key** — [create at IBM Cloud IAM](https://cloud.ibm.com/iam/apikeys)
- **Python 3.10+** (for setup scripts and FastAPI assets)
- **IBM watsonx.data** instance
- Access to the IBM service listed in each building block's README header

### Common Setup Pattern

```bash
# 1. Navigate to the asset
cd <building-block>/assets/<asset-name>

# 2. Configure credentials
cp .env.example .env
# Edit .env: IBM_API_KEY and service-specific vars

# 3. Install and run
pip install -r requirements.txt
python main.py        # or: uvicorn app.server:app --host 0.0.0.0 --port 8080
# API docs → http://localhost:8080/docs
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
| **[IBM watsonx.data](https://www.ibm.com/products/watsonx-data)** | Unified data platform hosting Presto, Spark, Iceberg and Astra DB |
| **[Presto](https://www.ibm.com/docs/en/watsonxdata/saas?topic=overview)** | Interactive, distributed SQL query engine for analytics across connected sources |
| **[Apache Spark](https://www.ibm.com/docs/en/watsonxdata/saas?topic=spark-introduction-watsonxdata)** | Distributed processing for large-scale transformations, ingestion and ML workloads |
| **[Apache Iceberg](https://www.ibm.com/docs/en/watsonxdata/saas?topic=components-accessing-data-in-external-data-platforms)** | Open table format enabling multi-engine access with schema evolution and ACID properties |
| **[Astra DB Serverless](https://docs.datastax.com/en/astra-db-serverless/databases/create-database.html)** | Serverless vector database for embeddings, similarity search and RAG |
