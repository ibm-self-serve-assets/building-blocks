---
name: data-ingestion-structured
description: Expert guidance for building IBM watsonx.data structured data ingestion pipelines — covers DB2, PostgreSQL, MySQL, Oracle connectors via IBM DataStage and StreamSets, CDC with log-based capture, batch and incremental load patterns, schema evolution handling, and IBM Cloud IAM authentication. Generates production-ready Python 3.12 scripts and DataStage job configurations.
---

# IBM watsonx.data Structured Data Ingestion Builder

## Purpose

Expert guidance for building **structured data ingestion pipelines** that move data from RDBMS sources into **IBM watsonx.data** (Iceberg tables) using **IBM DataStage**, **StreamSets**, and **IBM Data Replication**. Generates production-ready code following IBM building-blocks conventions.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| IBM watsonx.data | Target: Iceberg tables via Presto; source metadata via REST API |
| IBM DataStage | Pipeline design: batch/streaming/replication jobs |
| IBM Data Replication (CDC) | Log-based Change Data Capture from Db2, PostgreSQL, Oracle |
| IBM Cloud IAM | POST /identity/token (apikey grant) |
| IBM Cloud Object Storage | Staging area for batch file loads |

## Rules

- Always generate IAM auth with `IAMTokenManager` (5-minute buffer)
- IBM watsonx.data API base: `https://{region}.lakehouse.cloud.ibm.com/lakehouse/api/v2`
- For DataStage jobs: use IBM DataStage on Cloud REST API (`/v3/data_intg_flows`)
- CDC uses IBM Data Replication — source connector must match DB type (db2, postgresql, oracle, mysql)
- Staging to COS uses HMAC credentials for bulk loads
- Schema evolution: detect added/dropped columns via schema comparison before load

---

## Scope

- IBM Db2 (on-prem and IBM Cloud) batch, incremental, and CDC ingestion
- PostgreSQL, MySQL, Oracle, MS SQL Server connectors
- IBM DataStage batch job generation (Sequence jobs, Parallel jobs)
- IBM StreamSets pipeline configuration for real-time ingestion
- IBM Data Replication CDC log-mining setup
- Schema mapping to Iceberg data types
- Error handling, retry logic, and dead-letter patterns

---

## Procedure

### Phase 1: IAM Authentication

```python
class IAMTokenManager:
    def get_token(self) -> str:
        if not self._token or time.time() >= self._expiry:
            self._refresh()
        return self._token

    def _refresh(self) -> None:
        resp = requests.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self._api_key},
            timeout=30)
        resp.raise_for_status()
        body = resp.json()
        self._token, self._expiry = body["access_token"], time.time() + int(body.get("expires_in", 3600)) - 300
```

### Phase 2: Supported Source Connectors

| Source DB | Connector Type | CDC Method |
|---|---|---|
| IBM Db2 | `db2` | Log-based (IBM Data Replication) |
| PostgreSQL | `postgresql` | Logical replication (pglogical) |
| MySQL | `mysql` | Binary log (binlog) |
| Oracle | `oracle` | LogMiner / Redo log |
| MS SQL Server | `mssql` | CDC via SQL Server Agent |
| Amazon Redshift | `redshift` | Batch via UNLOAD to S3 |
| Snowflake | `snowflake` | Batch via COPY INTO |

### Phase 3: Batch Ingestion Pattern

```python
import pyarrow as pa
import pyarrow.parquet as pq

# 1. Extract from source DB
rows = cursor.execute("SELECT * FROM customers WHERE updated_at > ?", [last_watermark])
df = pd.DataFrame(rows)

# 2. Write to IBM COS staging
buffer = io.BytesIO()
pq.write_table(pa.Table.from_pandas(df), buffer)
cos_client.put_object(Bucket=bucket, Key=f"staging/customers/{ts}.parquet", Body=buffer.getvalue())

# 3. Load into watsonx.data Iceberg via Presto
presto.execute(f"""
    INSERT INTO iceberg_catalog.sales.customers
    SELECT * FROM cos_catalog.staging.customers
    WHERE file_modified_date = '{ts}'
""")
```

### Phase 4: CDC Pattern (IBM Data Replication)

```python
# IBM Data Replication REST API
# POST /api/v1/subscriptions — create CDC subscription
subscription = {
    "name": "customers_cdc",
    "source": {"type": "db2", "host": DB2_HOST, "port": 50000, "database": "BLUDB"},
    "target": {"type": "kafka", "brokers": KAFKA_BROKERS, "topic": "customers_changes"},
    "tables": ["SALES.CUSTOMERS", "SALES.ORDERS"],
    "capture_ddl": True,
}
```

### Phase 5: Iceberg Type Mapping

| RDBMS Type | Apache Iceberg Type |
|---|---|
| `VARCHAR(n)` | `string` |
| `INTEGER` | `int` |
| `BIGINT` | `long` |
| `DECIMAL(p,s)` | `decimal(p, s)` |
| `TIMESTAMP` | `timestamp` |
| `DATE` | `date` |
| `BOOLEAN` | `boolean` |

### Key IBM Cloud URLs

| Service | URL |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| watsonx.data API (us-south) | `https://us-south.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| IBM DataStage REST API | `https://api.us-south.dataplatform.cloud.ibm.com/v3/data_intg_flows` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |
