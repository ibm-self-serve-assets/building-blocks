# NoSQL Database — Astra DB / watsonx.data DataStax

**Core Capability**: Retrieval
**IBM Products**: IBM HCD (Astra DB / watsonx.data DataStax)
**Product Components**: Astra DB Data API; astrapy SDK; Apache Cassandra-compatible storage

> **Product options**: **Astra DB** is the SaaS offering on IBM Cloud HCD. **DataStax** in **IBM watsonx.data** is the software option for on-premises or private cloud deployments.

## Overview

Provides large-scale NoSQL storage with Cassandra compatibility using **DataStax Astra DB** (SaaS) or **IBM watsonx.data DataStax** (software). Part of the IBM Cloud HCD (Hyper-Converged Database) portfolio. Supports document-based CRUD via the Data API and optional vector capabilities for AI and application workloads.

---

## When to Use

| Scenario | Notes |
|---|---|
| Store and retrieve large volumes of JSON documents without a fixed schema | Ideal — Astra DB is schema-flexible |
| Need MongoDB-style filter queries (`$eq`, `$in`, `$and`, `$or`) at scale | Supported natively via astrapy Data API |
| Need Cassandra-compatible, highly available document storage for an AI application | Use Astra DB (SaaS) or watsonx.data DataStax (software) |
| Need vector search on top of document storage | Combine with [`vector-search/datastax-astradb/`](../vector-search/datastax-astradb/) |
| Already have a Cassandra cluster and want an IBM-managed option | Use watsonx.data DataStax (software deployment) |

---

## Getting Started

### Prerequisites

- **Astra DB instance** on IBM Cloud HCD — note your API endpoint and Application Token from the Astra DB console
- **Python 3.10+**

### Quick Start

```bash
cd astradb/assets/astradb-nosql-crud
cp .env.example .env
# Edit .env: ASTRA_DB_API_ENDPOINT, ASTRA_DB_APPLICATION_TOKEN
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

Insert documents:
```bash
curl -X POST http://localhost:8080/collections/insert \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "documents": [{"_id": "1", "name": "IBM Corp", "region": "us-south"}]}'
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
Copy-Item astradb/bob-modes/base-modes/nosql-astradb-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```
```bash
# Linux / macOS
cp astradb/bob-modes/base-modes/nosql-astradb-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```
Restart IBM Bob — **NoSQL Astra DB Builder** mode appears in the mode selector.

**Install the Bob Skill** — teach Bob the Astra DB CRUD patterns:
```bash
unzip astradb/bob-skills/astradb-nosql-design.zip
```
Open IBM Bob → Skills panel → enable `astradb-nosql-design`.

---

## Building Blocks

### 1. Astra DB NoSQL CRUD Service
**Location**: `astradb/assets/astradb-nosql-crud/`
**IBM Products**: IBM HCD (Astra DB)
**Description**: FastAPI service providing full CRUD operations on Astra DB NoSQL collections using `astrapy` Data API with MongoDB-style filter expressions.

**Quick Start**:
```bash
cd astradb/assets/astradb-nosql-crud
cp .env.example .env
# Edit .env: ASTRA_DB_API_ENDPOINT, ASTRA_DB_APPLICATION_TOKEN
pip install -r requirements.txt
python main.py
# Swagger UI → http://localhost:8080/docs
```

**Example — Insert documents**:
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

**Example — Query documents**:
```bash
curl -X POST http://localhost:8080/collections/find \
  -H "REST_API_KEY: your_key" \
  -H "Content-Type: application/json" \
  -d '{"collection_name": "customers", "filter": {"region": {"$eq": "us-south"}}, "limit": 10}'
```

**API Endpoints**:

| Method | Path | Description |
|---|---|---|
| `POST` | `/collections/insert` | Insert one or many documents |
| `POST` | `/collections/find` | Query with MongoDB-style filters |
| `POST` | `/collections/update` | Update with `$set`, `$unset`, `$inc` |
| `POST` | `/collections/delete` | Delete matching documents |

---

## Bob Modes

- **[`astradb/bob-modes/`](./astradb/bob-modes/)**: AI mode for Astra DB NoSQL data modeling and CRUD
  - **Install**: copy [`astradb/bob-modes/base-modes/nosql-astradb-builder.zip`](./astradb/bob-modes/base-modes/nosql-astradb-builder.zip) to your Bob modes directory

## Bob Skills

Install by extracting the zip into your Bob workspace `.bob/skills/` directory:

| Skill | Zip | Capabilities |
|---|---|---|
| `astradb-nosql-design` | [`astradb/bob-skills/astradb-nosql-design.zip`](./astradb/bob-skills/astradb-nosql-design.zip) | Astra DB document modeling, MongoDB-style CRUD, bulk operations, collection schema design, data migration patterns |

See [`astradb/bob-skills/README.md`](./astradb/bob-skills/README.md) for full installation instructions.

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
