---
name: watsonxdata-lakehouse
description: Expert guidance for IBM watsonx.data zero-copy lakehouse configuration — covers Iceberg catalog setup, IBM COS and AWS S3 bucket registration via the watsonx.data REST API v2, Presto engine catalog association, Spark configuration, schema creation, and federated SQL queries. Generates production-ready Python 3.12 scripts using IBM IAM authentication following existing watsonxdata_setup.py patterns.
---

# IBM watsonx.data Zero-Copy Lakehouse Builder

## Purpose

Expert guidance for configuring **IBM watsonx.data** as a zero-copy lakehouse — registering storage buckets, connecting databases, associating catalogs with Presto engines, and running federated SQL queries — all via the watsonx.data REST API v2.

## IBM Cloud Product Coverage

| IBM Cloud Product | Usage |
|---|---|
| IBM watsonx.data | REST API v2: /bucket_registrations, /presto_engines, /catalogs, /database_registrations |
| IBM Cloud IAM | POST /identity/token (apikey grant) — with auto-refresh |
| IBM Cloud Object Storage | Registered as managed bucket in watsonx.data |
| IBM Db2 | Registered as external database connection |
| Apache Iceberg | Table format for open lakehouse storage |
| Apache Spark | Heavy ETL jobs on Iceberg tables |
| Presto | Interactive federated SQL queries |

## Objective

Generate **production-ready Python 3.12 scripts** that:

- Authenticate to IBM Cloud via `IAMTokenManager` (5-minute buffer refresh)
- Register IBM COS, AWS S3, and other buckets as watsonx.data storage
- Connect Db2, PostgreSQL, MySQL databases to watsonx.data
- Associate catalogs with Presto engines for federated queries
- Create Iceberg schemas and tables
- Follow the existing `watsonxdata_setup.py` patterns exactly

## Rules

- Base URL pattern: `https://{region}.lakehouse.cloud.ibm.com/lakehouse/api/v2`
- Always build headers with `{"Authorization": "Bearer {token}", "AuthInstanceId": AUTH_INSTANCE_ID, "Content-Type": "application/json"}`
- The `AuthInstanceId` is the watsonx.data CRN (from config)
- Use `wait_with_progress(seconds)` for delays between API operations
- All resource registrations are synchronous — allow 30–90 second waits for catalog propagation
- Supported regions: `us-south`, `eu-de`, `au-syd`, `jp-tok`

---

## Scope

- IBM watsonx.data instance configuration and bucket registration
- IBM COS, AWS S3, Azure ADLS bucket registration
- IBM Db2, PostgreSQL, MySQL database connections
- Presto engine catalog association
- Apache Iceberg schema and table creation via Presto SQL
- Apache Spark job configuration for Iceberg ETL
- Federated query patterns across heterogeneous sources

---

## Procedure

### Phase 1: IAM Authentication

```python
class IAMTokenManager:
    def __init__(self, api_key: str) -> None:
        self.api_key, self.token, self.expiry = api_key, None, 0.0

    def get_token(self) -> str:
        if not self.token or time.time() >= self.expiry:
            self._refresh()
        return self.token

    def _refresh(self) -> None:
        resp = requests.post("https://iam.cloud.ibm.com/identity/token",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": self.api_key},
            timeout=30)
        resp.raise_for_status()
        body = resp.json()
        self.token = body["access_token"]
        self.expiry = time.time() + int(body.get("expires_in", 3600)) - 300
```

### Phase 2: watsonx.data API Headers

```python
def build_headers(token: str, auth_instance_id: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "AuthInstanceId": auth_instance_id,    # watsonx.data CRN
        "Content-Type": "application/json",
    }
```

### Phase 3: Register IBM COS Bucket

```python
payload = {
    "bucket_display_name": "cos_bucket",
    "bucket_type": "ibm_cos",
    "managed_by": "customer",
    "region": "us-south",
    "bucket_details": {
        "bucket_name": "my-bucket",
        "endpoint": "https://s3.us-south.cloud-object-storage.appdomain.cloud",
        "access_key": "HMAC_ACCESS_KEY",
        "secret_key": "HMAC_SECRET_KEY",
    },
    "associated_catalog": {
        "catalog_name": "cos_catalog",
        "catalog_type": "hive-hadoop2",
    },
}
requests.post(f"{BASE_URL}/bucket_registrations", headers=headers, json=payload)
```

### Phase 4: Register External Database (Db2)

```python
payload = {
    "database_details": {
        "database_name": "bludb",
        "hostname": "db2-host.appdomain.cloud",
        "password": "db2_pass",
        "port": 50000,
        "ssl": True,
        "username": "db2_user",
    },
    "database_display_name": "db2_source",
    "database_type": "db2",
    "associated_catalog": {"catalog_name": "db2_catalog", "catalog_type": "iceberg"},
}
requests.post(f"{BASE_URL}/database_registrations", headers=headers, json=payload)
```

### Phase 5: Associate Catalog to Presto Engine

```python
# Get engine ID first
presto_resp = requests.get(f"{BASE_URL}/presto_engines", headers=headers)
engine_id = presto_resp.json()["presto_engines"][0]["engine_id"]

# Associate
requests.post(f"{BASE_URL}/presto_engines/{engine_id}/catalogs",
              headers=headers, json={"catalog_names": "cos_catalog"})
```

### Phase 6: Create Iceberg Schema

```python
payload = {
    "bucket_name": "my-bucket",
    "custom_path": "/schemas/customers",
    "schema_name": "customers",
}
requests.post(f"{BASE_URL}/catalogs/cos_catalog/schemas?engine_id={engine_id}",
              headers=headers, json=payload)
```

### Key IBM Cloud URLs

| Service | URL Pattern |
|---|---|
| IBM IAM Token | `https://iam.cloud.ibm.com/identity/token` |
| watsonx.data API (us-south) | `https://us-south.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| IBM COS (us-south) | `https://s3.us-south.cloud-object-storage.appdomain.cloud` |

### Supported watsonx.data Regions

| Region | Base URL |
|---|---|
| us-south (Dallas) | `https://us-south.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| eu-de (Frankfurt) | `https://eu-de.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| au-syd (Sydney) | `https://au-syd.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
| jp-tok (Tokyo) | `https://jp-tok.lakehouse.cloud.ibm.com/lakehouse/api/v2` |
