# NoSQL Database Capability

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
