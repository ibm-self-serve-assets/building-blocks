# Federated Search Capability

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