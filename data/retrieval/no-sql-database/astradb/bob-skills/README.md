# NoSQL Astra DB Bob Skills

Bob skills for **DataStax Astra DB** (IBM Cloud HCD portfolio) NoSQL document operations — non-vector collections using the `astrapy` Data API.

## Overview

The `astradb-nosql-design` skill empowers IBM Bob to design and build NoSQL document applications on **DataStax Astra DB** — covering collection CRUD, MongoDB-style filter expressions, Cassandra-inspired data modeling, bulk insert patterns, and update operations — without vector dimensions.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `astradb-nosql-design` | [`astradb-nosql-design.zip`](astradb-nosql-design.zip) | Building NoSQL document collections on DataStax Astra DB (IBM HCD) — no vector search required |

---

### `astradb-nosql-design`

A comprehensive skill for building DataStax Astra DB NoSQL document applications:

- `astrapy>=1.5.2` Data API client for non-vector document CRUD operations
- Collection creation without vector dimensions (`db.create_collection(name)`)
- MongoDB-style filter expressions: `$eq`, `$gt`, `$lt`, `$in`, `$and`, `$or`
- Update operations: `{"$set": {...}}`, `{"$unset": {...}}`, `{"$inc": {...}}`
- Bulk insert with `insert_many(ordered=False)` for efficient loading
- Cassandra-compatible data modeling best practices (partition keys, wide rows)
- Upsert patterns and `delete_many()` with filter conditions
- AstraDB token format and API endpoint configuration
- Error handling for `AstraDBException` with meaningful messages

---

## Installation

### Step 1 — Install the skill

The zip file is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip astradb-nosql-design.zip
```

This will create:
```
.bob/skills/astradb-nosql-design/SKILL.md
```

### Step 2 — Enable in IBM Bob

Open IBM Bob → Skills panel → enable `astradb-nosql-design`. Bob will use it as active context for every prompt in this workspace.

### Step 3 — Verify

Ask Bob: *"What Astra DB NoSQL skills do you have active?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Create an Astra DB collection for customer records without vector dimensions"*
- *"Generate a bulk insert script for 10,000 customer documents using astrapy"*
- *"Write a MongoDB-style filter to find all orders with status 'pending' and amount > 100"*
- *"Show me how to update documents in Astra DB using $set and $inc operators"*
- *"Design a Cassandra-inspired data model for a time-series event store in Astra DB"*

---

## What Bob Can Help You Build

1. **Collection Design**: Non-vector collections with Cassandra-compatible schema patterns
2. **CRUD Operations**: Insert, find, update, delete with `astrapy` Document API
3. **MongoDB-Style Filters**: `$eq`, `$gt`, `$in`, `$and`, `$or` query expressions
4. **Bulk Patterns**: Efficient `insert_many()` and `delete_many()` operations
5. **Update Operators**: `$set`, `$unset`, `$inc` update expression patterns
6. **FastAPI Services**: RESTful CRUD services backed by Astra DB

---

## Prerequisites

Before using this skill, ensure you have:

- DataStax Astra DB instance (IBM Cloud HCD portfolio)
- Astra DB Application Token (`AstraCS:...`)
- Astra DB API endpoint URL (`https://<DB_ID>-<REGION>.apps.astra.datastax.com`)

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **Non-Vector Collections** | `db.create_collection(name)` — no dimension required |
| **Insert Operations** | `insert_one()`, `insert_many(ordered=False)` |
| **Filter Queries** | MongoDB-compatible `$eq`, `$gt`, `$in`, `$and`, `$or` |
| **Update Operations** | `$set`, `$unset`, `$inc` update expressions |
| **Delete Operations** | `delete_one()`, `delete_many()` with filters |
| **Cassandra Modeling** | Partition key selection, wide-row design patterns |
| **Error Handling** | `AstraDBException` handling patterns |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/astradb-nosql-design/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure you've enabled the Skills button in your current mode

**Bob generates vector collection syntax:**
1. Specify "non-vector" or "NoSQL" in your prompt
2. Explicitly say: *"I do not need vector search, just document storage"*

## Related

- [`../bob-modes/`](../bob-modes/) — NoSQL Astra DB Builder Bob Mode
- [`../README.md`](../README.md) — NoSQL Astra DB building block overview
- [`../../../vector-search/datastax-astradb/bob-skills/`](../../../vector-search/datastax-astradb/bob-skills/) — Astra DB vector search skills
