---
name: astradb-nosql-design
description: Expert guidance for DataStax Astra DB NoSQL data modeling on IBM Cloud (HCD portfolio) — covers astrapy Document API for collection CRUD, MongoDB-style filter expressions, Cassandra-compatible data modeling, collection schema design without vector, bulk insert patterns, and $set/$unset update operators. Generates production-ready Python 3.12 FastAPI services.
---

# DataStax Astra DB NoSQL Data Modeling Builder

## Purpose

Expert guidance for building **DataStax Astra DB** NoSQL document applications — part of the IBM Cloud HCD (Hyper-Converged Database) portfolio. Generates Python 3.12 FastAPI services using `astrapy` SDK for non-vector document collections.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| IBM HCD / DataStax Astra DB | Document API (non-vector): insert, find, update, delete |
| IBM Cloud IAM | (optional) — Astra DB uses its own token-based auth |

## Rules

- Use `astrapy>=1.5.2` Data API client
- Non-vector collections: create with `db.create_collection(name)` — no dimension
- Filter expressions follow MongoDB operator conventions: `$eq`, `$gt`, `$in`, `$and`, `$or`
- Update expressions: `{"$set": {...}}`, `{"$unset": {...}}`, `{"$inc": {...}}`
- `_id` field: Astra DB auto-generates UUIDs if not provided
- Batch: use `insert_many()` for bulk inserts — no strict limit unlike vector collections
- Always handle `AstraDBException` and provide meaningful error messages

---

## Scope

- Astra DB NoSQL collection creation and management
- MongoDB-style CRUD operations via Data API
- Cassandra-inspired data modeling (wide rows, partition keys)
- Bulk insert patterns
- Update and upsert operations
- Collection listing and introspection

---

## Procedure

### Phase 1: Astra DB Connection

```python
from astrapy import DataAPIClient

client = DataAPIClient(token=ASTRA_DB_APPLICATION_TOKEN)
db = client.get_database(ASTRA_DB_API_ENDPOINT)
```

### Phase 2: Create / Get Collection (Non-Vector)

```python
# Non-vector collection — no dimension argument
collection = db.create_collection("customers")

# Get existing
collection = db.get_collection("customers")
```

### Phase 3: Insert Documents

```python
# Single insert
collection.insert_one({
    "_id": "cust-001",
    "name": "IBM Corp",
    "email": "info@ibm.com",
    "created_at": "2024-01-15",
})

# Bulk insert
result = collection.insert_many([
    {"_id": "1", "name": "Alice"},
    {"_id": "2", "name": "Bob"},
], ordered=False)
print(result.inserted_ids)
```

### Phase 4: Query Documents

```python
# Filter: all customers in "US"
docs = collection.find(
    filter={"country": {"$eq": "US"}},
    limit=50,
    projection={"name": True, "email": True},
)
for doc in docs:
    print(doc["name"])
```

### Phase 5: Update Documents

```python
# Set field on matching documents
collection.update_many(
    filter={"status": "pending"},
    update={"$set": {"status": "active", "updated_at": "2024-06-01"}},
    upsert=False,
)
```

### Phase 6: Delete Documents

```python
collection.delete_many(filter={"status": {"$eq": "archived"}})
```

### Astra DB Token Format

```
ASTRA_DB_APPLICATION_TOKEN = AstraCS:<base64-token>
ASTRA_DB_API_ENDPOINT = https://<DB_ID>-<REGION>.apps.astra.datastax.com
```
