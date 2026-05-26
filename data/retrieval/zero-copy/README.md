# Zero Copy

**Core Capability**: Retrieval
**IBM Products**: watsonx.data
**Product Components**: Iceberg; Presto; Spark; Data connectors

## Overview

Federated analytics without copying data. Query data across distributed sources with open lakehouse architecture and federated access without copying all source data into a single repository.

## Building Blocks

### Zero-Copy Lakehouse
**Location**: `zero-copy-lakehouse/`
**IBM Products**: watsonx.data (Apache Iceberg + Presto)
**Description**: Zero-copy lakehouse with federated analytics

**Quick Start**:
```bash
cd zero-copy-lakehouse/setup-lakehouse
# Edit config.json with your watsonx.data credentials
python watsonxdata_setup.py
```

**What it does**:
- Creates Iceberg catalog
- Sets up schemas and tables
- Loads sample data
- Configures Presto engine

---

For detailed setup, see component README.