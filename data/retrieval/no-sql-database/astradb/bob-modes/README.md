# Bob Mode for NoSQL Astra DB

Custom IBM Bob mode configuration for **DataStax Astra DB** NoSQL document operations — part of the IBM Cloud HCD portfolio.

---

## Overview

This Bob mode provides specialized assistance for:

- **Astra DB Document API**: Full CRUD on NoSQL collections using `astrapy`
- **Collection Schema Design**: Partition-key-aware document modeling
- **MongoDB-Style Queries**: `$eq`, `$gt`, `$in`, `$and`, `$or` filter expressions
- **Bulk Operations**: Efficient `insert_many()` and `delete_many()` patterns
- **Data Migration**: Migrating relational (PostgreSQL/MySQL) data to Astra DB

---

## What's Included

- **[`base-modes/nosql-astradb-builder.zip`](base-modes/nosql-astradb-builder.zip)**: Bob mode for Astra DB NoSQL development

---

## Mode Capabilities

- DataStax Astra DB Data API collection management
- MongoDB-style CRUD operations with astrapy
- Cassandra data modeling best practices
- Bulk insert and update patterns
- Collection listing and introspection
- Error handling for AstraDB API exceptions
- FastAPI service development for Astra DB integrations

---

## When to Use This Mode

- Designing Astra DB NoSQL document collections for IBM HCD applications
- Implementing full CRUD operations with MongoDB-style filter expressions
- Building bulk insert or delete patterns for large dataset operations
- Migrating relational (PostgreSQL / MySQL) data to Astra DB document model
- Troubleshooting Astra DB token or API endpoint configuration
- Designing Cassandra-compatible data models with proper partition keys

---

## Installing Bob Modes

#### Method 1: Copy to Bob's Global Modes Directory (Recommended)

**Windows**

```powershell
Copy-Item base-modes/nosql-astradb-builder.zip "$env:APPDATA\IBM Bob\User\globalStorage\ibm.bob-code\modes\"
```

**Linux / macOS**

```bash
cp base-modes/nosql-astradb-builder.zip ~/.config/IBM\ Bob/User/globalStorage/ibm.bob-code/modes/
```

After copying, restart IBM Bob for the new mode to become available.

---

#### Method 2: Reference Modes from Current Repository

1. Open IBM Bob configuration settings
2. Add the local directory path under custom modes
3. Restart IBM Bob
