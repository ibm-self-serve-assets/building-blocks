# NoSQL Astra DB — Building Blocks

**Core Capability**: Retrieval
**IBM Products**: IBM HCD (Astra DB / watsonx.data DataStax)
**Product Components**: Astra DB Data API; astrapy SDK; Apache Cassandra-compatible storage

> **Product options**: **Astra DB** is the SaaS offering on IBM Cloud HCD. **DataStax** in **IBM watsonx.data** is the software option for on-premises or private cloud deployments.

## Overview

Large-scale NoSQL document storage with Cassandra compatibility using **DataStax Astra DB** (SaaS) or **IBM watsonx.data DataStax** (software). Supports full CRUD via the Data API, MongoDB-style filter expressions, and optional vector search capabilities for AI applications.

---

## When to Use

| Scenario | Notes |
|---|---|
| Store and query large volumes of JSON documents without a fixed schema | Astra DB is schema-flexible by design |
| Need MongoDB-style filter queries (`$eq`, `$in`, `$and`, `$or`) at scale | Supported natively via `astrapy` Data API |
| Need Cassandra-compatible, highly available document storage | Use Astra DB (SaaS) or watsonx.data DataStax (software) |
| Need vector search on top of document storage | Combine with [`../../vector-search/datastax-astradb/`](../../vector-search/datastax-astradb/) |
| Already have a Cassandra cluster and want an IBM-managed option | Use watsonx.data DataStax (software deployment) |

---

## Getting Started

### Prerequisites

- **Astra DB instance** on IBM Cloud HCD — note your API endpoint and Application Token from the Astra DB console
- **Python 3.10+**

### Quick Start

```bash
cd assets/astradb-nosql-crud
cp .env.example .env
# Edit .env:
#   ASTRA_DB_API_ENDPOINT         — from Astra DB console → Connect
#   ASTRA_DB_APPLICATION_TOKEN    — AstraCS:... token from Astra DB console
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Insert documents:
```bash
curl -X POST http://localhost:8080/collections/insert \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "collection_name": "customers",
    "documents": [
      {"_id": "1", "name": "IBM Corp", "region": "us-south"},
      {"_id": "2", "name": "Acme Inc", "region": "eu-de"}
    ]
  }'
```

Query documents:
```bash
curl -X POST http://localhost:8080/collections/find \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"region": {"$eq": "us-south"}}, "limit": 10}'
```

### IBM Bob — Your Fellow Developer

**[IBM Bob](https://www.ibm.com/products/bob)** is IBM's AI coding assistant purpose-built for IBM Cloud and watsonx. The NoSQL building block ships a **Bob Mode** and **Bob Skill** that give Bob deep knowledge of Astra DB document modeling, MongoDB-style CRUD patterns, and IBM HCD integration.

**Install the Bob Mode** — give Bob an Astra DB NoSQL specialist persona:
```powershell
# Windows
Copy-Item assets/bob-modes/base-modes/nosql-astradb-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp bob-modes/base-modes/nosql-astradb-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **NoSQL Astra DB Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the Astra DB CRUD patterns:
```bash
unzip bob-skills/astradb-nosql-design.zip
```
Open IBM Bob → Skills panel → enable `astradb-nosql-design`.

---

## Building Blocks

### 1. Astra DB NoSQL CRUD Service
**Location**: [`assets/astradb-nosql-crud/`](assets/astradb-nosql-crud/)
**IBM Products**: IBM HCD (Astra DB)
**Description**: FastAPI service providing full CRUD operations on Astra DB NoSQL collections using `astrapy` Data API with MongoDB-style filter expressions.

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/collections/insert` | Insert one or many documents |
| `POST` | `/collections/find` | Query with MongoDB-style filters |
| `POST` | `/collections/update` | Update with `$set`, `$unset`, `$inc` |
| `POST` | `/collections/delete` | Delete matching documents |

---

## Bob Modes

- **[`bob-modes/`](./bob-modes/)**: AI assistant mode for Astra DB NoSQL data modeling and CRUD
  - **Install**: copy [`bob-modes/base-modes/nosql-astradb-builder.zip`](./bob-modes/base-modes/nosql-astradb-builder.zip) to your Bob modes directory
  - See [`bob-modes/README.md`](./bob-modes/README.md) for full details

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `astradb-nosql-design` | [`bob-skills/astradb-nosql-design.zip`](./bob-skills/astradb-nosql-design.zip) | Astra DB document modeling, MongoDB-style CRUD, bulk operations, collection schema design, data migration patterns |

See [`bob-skills/README.md`](./bob-skills/README.md) for full installation instructions.

---

## Architecture

```
Your Application
      │
      │  REST API (+ REST_API_KEY header)
      ▼
Astra DB CRUD Service (FastAPI)
      │
      │  astrapy DataAPIClient
      │  ASTRA_DB_APPLICATION_TOKEN
      ▼
DataStax Astra DB (IBM HCD)
  NoSQL Document Collections
  (Cassandra-compatible storage)
```

## IBM Cloud References

- [IBM HCD / DataStax Astra DB](https://cloud.ibm.com/catalog/services/hyper-converged-database)
- [DataStax Astra DB Data API Reference](https://docs.datastax.com/en/astra/astra-db-vector/api-reference/data-api.html)
- [astrapy SDK Documentation](https://github.com/datastax/astrapy)
- [IBM Cloud IAM API Keys](https://cloud.ibm.com/iam/apikeys)
