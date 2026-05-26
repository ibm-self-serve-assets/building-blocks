# No SQL database

**Core Capability**: Retrieval
**IBM Products**: AstraDB, HCD (Hyper-converged DB)
**Product Components**: AstraDB(Cassandra)

## Overview

Provides large-scale NoSQL storage with Cassandra compatibility and optional vector capabilities for AI and application workloads.

## Building Blocks

### DataStax Astra DB
**Location**: `astradb/`
**IBM Products**: DataStax Astra DB
**Description**: Cloud-native NoSQL database with vector search

**Quick Start**:
```bash
pip install cassandra-driver astrapy

# Python example
from astrapy.db import AstraDB

db = AstraDB(
    token='your-token',
    api_endpoint='your-endpoint'
)

collection = db.create_collection('my_collection')
collection.insert_one({'id': '1', 'name': 'example'})
```

**Configuration**:
- `ASTRA_DB_ID`: Database ID
- `ASTRA_DB_REGION`: Region
- `ASTRA_DB_TOKEN`: Application token
- `ASTRA_DB_KEYSPACE`: Keyspace name

---

For detailed setup, see component README.
