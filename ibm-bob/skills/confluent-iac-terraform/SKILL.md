---
name: confluent-iac-terraform
description: Expert guidance for building real-time streaming systems on Confluent Cloud using Infrastructure-as-Code (Terraform), Apache Flink SQL, and Python producers. Adapts to any streaming use case (IoT, finance, retail, healthcare, logistics) while maintaining production-ready quality.
---

# Confluent Cloud Streaming System Builder

You are a Confluent Cloud streaming architect. When given a streaming use case, generate a **complete streaming system**: Terraform IaC, Flink SQL, Python producer, and docs.

**Two-phase workflow — order is mandatory:**
- **Phase 1 — Terraform first:** deploys infrastructure and registers schemas in Schema Registry via Flink DDL.
- **Phase 2 — Python producer second:** retrieves schemas from Schema Registry and produces matching messages.

Generate complete working code without placeholders. State assumptions clearly when inferring requirements.

---

### 1. Domain Analysis & Requirements

Analyze the user's requirements to understand:

- **Domain**: What industry or business area? (retail, finance, IoT, healthcare, etc.)
- **Entities**: What are the key entities? (products, accounts, devices, patients, etc.)
- **Events**: What events occur? (sales, transactions, readings, updates, etc.)
- **Aggregation Pattern**: What processing is needed?
  - Running totals (inventory levels, account balances)
  - Windowed aggregations (hourly metrics, daily summaries)
  - Latest value (current status, most recent reading)
  - Event counting (error rates, transaction counts)
- **Scale**: Expected data volume and velocity
- **Business Rules**: Any specific logic or constraints

**Reference Implementation: Retail Inventory**
```
Domain: Retail inventory management
Entities: Products (SKU), Store branches
Events: ADDITION (stock in), SALE (stock out)
Aggregation: Running total of available quantity per SKU per branch
Scale: 100s of SKUs, 10s of branches, 1000s transactions/day
Business Rules: Track real-time inventory levels, alert on low stock
```

### 2. Schema Design

Design streaming data schemas based on domain analysis:

**Source Schema (Input Events)**
- Identify key fields (entity IDs, event types, values, timestamps)
- Choose appropriate data types (STRING, INT, BIGINT, DECIMAL, TIMESTAMP)
- Select distribution key for Flink partitioning
- Design for efficient aggregation

**Destination Schema (Aggregated Results)**
- Define aggregated fields (sums, averages, counts, latest values)
- Set primary keys for upsert semantics
- Ensure schema supports business queries

**Example Transformation:**
```
Inventory → Finance:
- sku → account_id
- branch → branch_id  
- quantity → amount
- transaction_type → transaction_type (DEPOSIT/WITHDRAWAL)
- transaction_time → transaction_time

Inventory → IoT:
- sku → device_id
- branch → location
- quantity → temperature
- transaction_type → reading_type
- transaction_time → reading_time
```

### 3. Terraform Infrastructure Generation

Generate production-ready Terraform configurations following this structure:

#### Phase 1: Provider & Variables (`terraform/providers.tf`, `terraform/variables.tf`)

**Critical Requirements:**
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = ">= 2.68.0"  # REQUIRED for Flink support
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.0"   # REQUIRED for RBAC delays
    }
  }
}
```

**Standard Variables:**
- `api_key`, `api_secret` (Confluent Cloud credentials)
- `environment_name` (e.g., "retail-inventory-env")
- `cluster_name` (e.g., "inventory-cluster")
- `region` (e.g., "us-east-1")
- `cloud_provider` (e.g., "AWS")
- `flink_max_cfu` (e.g., 5)

#### Phase 2: Core Resources (`terraform/main.tf`)

**Resource Creation Order (Critical for Dependencies):**
1. Data source: `confluent_organization`
2. Environment: `confluent_environment` — **do NOT add a `stream_governance` block**; omitting it lets Confluent auto-provision Schema Registry (adding `package = "ESSENTIALS"` does NOT provision Schema Registry and will cause `data.confluent_schema_registry_cluster` to fail with "no schema registry clusters found")
3. Kafka Cluster: `confluent_kafka_cluster` (Basic tier)
4. Service Account: `confluent_service_account`
5. Data source: `confluent_schema_registry_cluster` — must have `depends_on = [confluent_kafka_cluster.main]` (not the environment) so it resolves only after the cluster is ready
6. Flink Compute Pool: `confluent_flink_compute_pool` — must have `depends_on = [confluent_kafka_cluster.main]`
7. Data source: `confluent_flink_region` — must have `depends_on = [confluent_environment.main]`

**Do NOT declare `confluent_kafka_topic` resources** for topics that will be owned by Flink DDL. The `CREATE TABLE` Flink statement auto-creates the backing Kafka topic. Pre-declaring the topic as a Terraform resource causes:
- Partition count conflicts (Flink may create with different defaults)
- Read-only config errors on re-apply (`compression.type` etc.)
- State drift between Kafka topic resource and Flink catalog
Only declare `confluent_kafka_topic` resources for topics consumed by non-Flink systems that Flink will not `CREATE TABLE` against.

#### Phase 3: Security & Access

**API Keys (3 types with correct associations and `depends_on`):**

Each API key must depend on its **specific** role binding — not on `time_sleep.wait_for_rbac`. Using `time_sleep` as the dependency for all three is incorrect and can cause race conditions where a key is created before its permission is granted.

```hcl
# Flink API Key → Associated with Flink Region, depends on FlinkDeveloper role binding
resource "confluent_api_key" "flink" {
  owner {
    id          = confluent_service_account.app.id
    api_version = confluent_service_account.app.api_version
    kind        = confluent_service_account.app.kind
  }
  managed_resource {
    id          = data.confluent_flink_region.main.id
    api_version = data.confluent_flink_region.main.api_version
    kind        = data.confluent_flink_region.main.kind
    environment {
      id = confluent_environment.main.id
    }
  }
  depends_on = [confluent_role_binding.flink_developer]
}

# Kafka API Key → Associated with Kafka Cluster, depends on CloudClusterAdmin role binding
resource "confluent_api_key" "kafka_producer" {
  owner {
    id          = confluent_service_account.app.id
    api_version = confluent_service_account.app.api_version
    kind        = confluent_service_account.app.kind
  }
  managed_resource {
    id          = confluent_kafka_cluster.main.id
    api_version = confluent_kafka_cluster.main.api_version
    kind        = confluent_kafka_cluster.main.kind
    environment {
      id = confluent_environment.main.id
    }
  }
  depends_on = [confluent_role_binding.kafka_admin]
}

# Schema Registry API Key → Associated with Schema Registry, depends on EnvironmentAdmin role binding
resource "confluent_api_key" "schema_registry" {
  owner {
    id          = confluent_service_account.app.id
    api_version = confluent_service_account.app.api_version
    kind        = confluent_service_account.app.kind
  }
  managed_resource {
    id          = data.confluent_schema_registry_cluster.main.id
    api_version = data.confluent_schema_registry_cluster.main.api_version
    kind        = data.confluent_schema_registry_cluster.main.kind
    environment {
      id = confluent_environment.main.id
    }
  }
  depends_on = [confluent_role_binding.env_admin]
}
```

**Role Bindings (3 types with correct patterns):**
```hcl
# CloudClusterAdmin → Kafka (uses rbac_crn)
resource "confluent_role_binding" "kafka_admin" {
  principal   = "User:${confluent_service_account.app.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.main.rbac_crn
}

# FlinkDeveloper → Environment (uses resource_name, environment-level scope)
resource "confluent_role_binding" "flink_developer" {
  principal   = "User:${confluent_service_account.app.id}"
  role_name   = "FlinkDeveloper"
  crn_pattern = confluent_environment.main.resource_name
}

# EnvironmentAdmin → Environment (uses resource_name)
resource "confluent_role_binding" "env_admin" {
  principal   = "User:${confluent_service_account.app.id}"
  role_name   = "EnvironmentAdmin"
  crn_pattern = confluent_environment.main.resource_name
}
```

**RBAC Propagation Delay:**
```hcl
resource "time_sleep" "wait_for_rbac" {
  create_duration = "30s"
  depends_on = [
    confluent_role_binding.kafka_admin,
    confluent_role_binding.flink_developer,
    confluent_role_binding.env_admin
  ]
}
```

#### Phase 4: Flink SQL Statements

**Critical Flink SQL Requirements:**

❌ **NEVER Use These Properties:**
```sql
-- FORBIDDEN in Flink table definitions:
'connector' = 'kafka'
'topic' = 'my-topic'
'kafka.topic' = 'my-topic'
'bootstrap.servers' = '...'
```

✅ **ALWAYS Use These Patterns:**
```sql
-- 1. Specify BOTH key and value formats
'key.format' = 'json-registry',
'value.format' = 'json-registry'

-- 2. Use DISTRIBUTED BY for tables without PRIMARY KEY
DISTRIBUTED BY (key_column) INTO 4 BUCKETS

-- 3. Key columns FIRST in schema in SAME ORDER (applies to DISTRIBUTED BY and PRIMARY KEY)
CREATE TABLE example (
  key_col STRING,        -- Distribution key FIRST
  other_col STRING,
  value_col INT
) DISTRIBUTED BY (key_col) INTO 4 BUCKETS

-- 4. Use Table-Valued Function (TVF) syntax for windows
TABLE(TUMBLE(TABLE source, DESCRIPTOR(time_col), INTERVAL '1' HOUR))
```

**Source Table Example:**
```sql
CREATE TABLE inventory_transactions (
  sku STRING,                    -- Distribution key FIRST
  branch STRING,
  quantity INT,
  transaction_type STRING,
  transaction_time TIMESTAMP(3),
  WATERMARK FOR transaction_time AS transaction_time - INTERVAL '5' SECONDS
) DISTRIBUTED BY (sku) INTO 4 BUCKETS
WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-uncommitted'
);
```

**Destination Table Example:**
```sql
CREATE TABLE inventory_availability (
  sku STRING,                    -- PRIMARY KEY columns must be first
  branch STRING,                 -- in same order as PRIMARY KEY definition
  available_quantity BIGINT,
  PRIMARY KEY (sku, branch) NOT ENFORCED
) WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-uncommitted'
);
```

**CRITICAL: Kafka Consumer Isolation Level**
- **Always set** `'kafka.consumer.isolation-level' = 'read-uncommitted'` on **ALL tables** (both source and destination)
- This allows immediate visibility of streaming results without waiting for Kafka transaction commits
- Without this setting on source tables, Flink may not read newly produced messages immediately
- Without this setting on destination tables, INSERT statements may appear to run but results won't be visible in queries
- This is especially important for windowed aggregations and real-time dashboards
- **CRITICAL**: Set this on EVERY table definition in your Flink SQL statements

**CRITICAL: Watermark Advancement & Tumbling Window Alignment**

For time-based windows (TUMBLE, HOP, SESSION), Flink requires the watermark to advance beyond the window end to trigger results.

**Key Concepts:**
- Tumbling windows are fixed-size, non-overlapping intervals (e.g., 5-min: 00:00, 00:05, 00:10)
- Events group by timestamp, not arrival time
- All events must fall within the same window boundary

**Correct Pattern for Windowed Test Data (`--windowed` mode):**
```python
from datetime import datetime, timedelta, timezone

# ALWAYS use timezone-aware UTC — datetime.utcnow() is deprecated and interprets
# .timestamp() as local time on non-UTC machines, producing wrong window alignment.
now = datetime.now(timezone.utc)

# Round UP to the NEXT 5-minute boundary. Use second=0 (not second=10) so
# timestamps align exactly to epoch-aligned window boundaries.
minutes = ((now.minute // 5) + 1) * 5
if minutes < 60:
    base_time = now.replace(minute=minutes, second=0, microsecond=0)
else:
    base_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)

base_timestamp_ms = int(base_time.timestamp() * 1000)

# Generate events within window (leave 30s buffer before window end)
window_duration_ms = (5 * 60 - 30) * 1000
spacing_ms = window_duration_ms // 7  # For 8 events

events = []
for i in range(8):
    events.append({
        'entity_id': 'ENTITY-001',
        'event_time': base_timestamp_ms + (i * spacing_ms)
    })

# Watermark-advance event: use 7 minutes (not 6).
# Rule: advance_ts - watermark_slack > window_end on ALL partitions.
# With 10s slack and 5-min window: 7 min past window_start = 2 min past window_end + slack.
events.append({
    'entity_id': 'WATERMARK-TRIGGER',
    'event_time': base_timestamp_ms + (7 * 60 * 1000)  # 7 minutes — guaranteed closure
})
```

**Best Practices:**
1. Always use `datetime.now(timezone.utc)` — never `datetime.utcnow()` (deprecated, wrong on non-UTC hosts)
2. Always use `second=0, microsecond=0` — `second=10` misaligns timestamps past the window boundary
3. Spread events across window duration minus a 30-second buffer at the end
4. Watermark-advance event: `window_start + 7 min` (not 6×) to clear the 10s slack on all partitions
5. Set watermark slack (`INTERVAL '10' SECONDS`) based on out-of-order tolerance

**Aggregation Job Example:**
```sql
INSERT INTO inventory_availability
SELECT 
  sku,
  branch,
  SUM(quantity) as available_quantity
FROM inventory_transactions
GROUP BY sku, branch;
```

**Terraform Resource for Flink Statements:**
```hcl
resource "confluent_flink_statement" "create_source_table" {
  organization {
    id = data.confluent_organization.main.id
  }
  environment {
    id = confluent_environment.main.id
  }
  compute_pool {
    id = confluent_flink_compute_pool.main.id
  }
  principal {
    id = confluent_service_account.app.id
  }

  statement = "CREATE TABLE ..."

  properties = {
    "sql.current-catalog"  = confluent_environment.main.display_name
    "sql.current-database" = confluent_kafka_cluster.main.display_name
  }

  rest_endpoint = data.confluent_flink_region.main.rest_endpoint

  credentials {
    key    = confluent_api_key.flink.id
    secret = confluent_api_key.flink.secret
  }

  depends_on = [
    time_sleep.wait_for_rbac,
    confluent_api_key.flink
  ]

  lifecycle {
    prevent_destroy = false
  }
}
```

**Statement ordering:** The first `CREATE TABLE` statement (source table) depends on `[time_sleep.wait_for_rbac, confluent_api_key.flink]`. Each subsequent statement depends only on the preceding Flink statement resource — do not re-list `time_sleep` on later statements.

**Important Provider Note:**
- Do **not** rely on partial provider-level Flink environment variables for `confluent_flink_statement` resources.
- If you set any of `flink_api_key`, `flink_api_secret`, `flink_rest_endpoint`, `organization_id`, `environment_id`, `flink_compute_pool_id`, or `flink_principal_id` in the provider, the Confluent provider expects **all seven** to be configured together.
- The most reliable pattern is to keep the provider configured only with cloud credentials and specify `rest_endpoint`, `properties`, and inline `credentials` on every `confluent_flink_statement` resource.

#### Phase 5: Outputs & .env Generation (`terraform/outputs.tf`)

**Required Outputs:**
```hcl
output "kafka_bootstrap_servers" {
  value = confluent_kafka_cluster.main.bootstrap_endpoint
}

output "kafka_rest_endpoint" {
  value = confluent_kafka_cluster.main.rest_endpoint
}

output "kafka_producer_api_key" {
  value     = confluent_api_key.kafka_producer.id
  sensitive = true
}

output "kafka_producer_api_secret" {
  value     = confluent_api_key.kafka_producer.secret
  sensitive = true
}

output "flink_api_key" {
  value     = confluent_api_key.flink.id
  sensitive = true
}

output "flink_api_secret" {
  value     = confluent_api_key.flink.secret
  sensitive = true
}

output "schema_registry_url" {
  value = data.confluent_schema_registry_cluster.main.rest_endpoint
}

output "schema_registry_api_key" {
  value     = confluent_api_key.schema_registry.id
  sensitive = true
}

output "schema_registry_api_secret" {
  value     = confluent_api_key.schema_registry.secret
  sensitive = true
}

output "flink_rest_endpoint" {
  # Use the data source — do NOT hardcode a URL template
  value = data.confluent_flink_region.main.rest_endpoint
}

output "environment_id" {
  value = confluent_environment.main.id
}

output "cluster_id" {
  value = confluent_kafka_cluster.main.id
}
```

**.env File Generation:**
```hcl
resource "local_file" "env_file" {
  filename = "${path.module}/../python/.env"
  content  = <<-EOT
KAFKA_BOOTSTRAP_SERVERS=${replace(confluent_kafka_cluster.main.bootstrap_endpoint, "SASL_SSL://", "")}
KAFKA_API_KEY=${confluent_api_key.kafka_producer.id}
KAFKA_API_SECRET=${confluent_api_key.kafka_producer.secret}
SCHEMA_REGISTRY_URL=${data.confluent_schema_registry_cluster.main.rest_endpoint}
SCHEMA_REGISTRY_API_KEY=${confluent_api_key.schema_registry.id}
SCHEMA_REGISTRY_API_SECRET=${confluent_api_key.schema_registry.secret}
EOT

  depends_on = [
    confluent_api_key.kafka_producer,
    confluent_api_key.schema_registry
  ]
}
```

**CRITICAL:** The `bootstrap_endpoint` from Confluent provider may include the `SASL_SSL://` prefix. Use `replace()` to strip it, as the Python producer's `security.protocol` setting handles the protocol separately.

### 4. Python Producer Development

Generate production-ready Python producer with proper serialization.

**When adding sample transactions**, always create and use a Python virtual environment before running the producer to ensure proper dependency isolation.

#### Dependencies (`python/requirements.txt`)
```
confluent-kafka[schema-registry]>=2.3.0
orjson>=3.9.0
python-dotenv>=1.0.0
```

#### Sample Data Generation (`python/sample-transactions.json`)

Generate realistic domain-specific sample data with appropriate entity IDs, value ranges, and event types.

**CRITICAL — Never store absolute (epoch) timestamps in sample JSON files.** This is the root cause of frozen Flink watermarks: hardcoded values like `1700000010000` are in the distant past when the producer runs. The Flink job sets each partition's watermark to that historical value. The global watermark = `min(all partition watermarks)` — one stale partition permanently freezes it. No window in the present ever closes.

**The structural fix: store `offset_ms` (relative ms from first event), never an absolute timestamp.** The producer anchors to the current window boundary at runtime:

```json
[
  { "account_id": "ACC-FRAUD-01", "transaction_id": "TXN-FRAUD-01", "amount": 1500.00, "transaction_type": "PURCHASE", "merchant": "Offshore Casino",    "offset_ms": 0      },
  { "account_id": "ACC-FRAUD-01", "transaction_id": "TXN-FRAUD-02", "amount": 2300.50, "transaction_type": "TRANSFER", "merchant": "Anonymous Transfer", "offset_ms": 24545  },
  ...12 total fraud events with offset_ms 0–269995 (all within one 5-min window)...
  { "account_id": "ACC-WATERMARK", "transaction_id": "TXN-WATERMARK", "amount": 0.01, "transaction_type": "PURCHASE", "merchant": "Watermark Trigger", "offset_ms": 420000 }
]
```

**Always include a watermark-trigger record** as the last entry. Formula: `offset_ms = window_ms + slack_ms + buffer_ms`. For a 5-min window with 10s slack: `300000 + 10000 + 110000 = 420000 ms` (7 min). Without it, the last window never closes if the producer stops before wall-clock time reaches the window end.

**Producer anchoring — window-boundary alignment:**
```python
from datetime import datetime, timezone

# Anchor to the start of the CURRENT 5-min window boundary so all fraud events
# (offset_ms 0–269995) land in the same window → COUNT(*) = 12 > 10.
# WARNING: never use (now - max_offset) — it doesn't align to a boundary;
# events straddle two windows, counts split, HAVING COUNT(*) > 10 never fires.
window_ms = 5 * 60 * 1000
now_ms    = int(datetime.now(timezone.utc).timestamp() * 1000)
anchor_ms = (now_ms // window_ms) * window_ms   # floor now to window boundary

for tx in transactions:
    tx['transaction_time'] = anchor_ms + tx.pop('offset_ms')
```

#### Producer Script (`python/produce_messages.py`)

**Critical Requirements:**

1. **Message Key Format** (MUST be object, not string):
```python
# ✅ CORRECT: Key as object
key = {"sku": "LAPTOP-001"}

# ❌ WRONG: Key as string
key = "LAPTOP-001"
```

2. **Timestamp Format** (MUST be milliseconds since epoch):
```python
# ✅ CORRECT: Milliseconds since epoch
timestamp_ms = int(datetime.now().timestamp() * 1000)

# ❌ WRONG: ISO 8601 string
timestamp_str = "2024-01-01T12:00:00Z"
```

3. **Serializer Selection** (ALWAYS use JSON Schema):
```python
# ✅ CORRECT: Use JSONSerializer for Flink tables
from confluent_kafka.schema_registry.json_schema import JSONSerializer

key_serializer = JSONSerializer(key_schema.schema_str, sr_client)
value_serializer = JSONSerializer(value_schema.schema_str, sr_client)
```

**Critical Rule:** Always use JSON Schema serialization:
- Flink tables use `'key.format' = 'json-registry'` and `'value.format' = 'json-registry'`
- Python must use `JSONSerializer` to match this format
- This creates JSON Schema in Schema Registry (not other formats)

4. **Complete Producer Example:**
```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Schema Registry client
sr_client = SchemaRegistryClient({
    'url': os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('SCHEMA_REGISTRY_API_KEY')}:{os.getenv('SCHEMA_REGISTRY_API_SECRET')}"
})

# Retrieve schemas from Schema Registry
key_registered_schema = sr_client.get_latest_version('inventory_transactions-key')
value_registered_schema = sr_client.get_latest_version('inventory_transactions-value')
key_schema = key_registered_schema.schema
value_schema = value_registered_schema.schema

# Serializers
key_serializer = JSONSerializer(key_schema.schema_str, sr_client)
value_serializer = JSONSerializer(value_schema.schema_str, sr_client)

# Producer config
producer = Producer({
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': os.getenv('KAFKA_API_KEY'),
    'sasl.password': os.getenv('KAFKA_API_SECRET')
})

# Track confirmed delivery counts — NOT enqueue counts.
# success_count++ before flush() counts messages queued, not broker-confirmed;
# failures during flush() are silently counted as successes.
enqueue_count = 0; enqueue_errors = 0; delivered_count = 0; delivery_errors = 0

def _delivery_callback(err, msg):
    """Delivery report callback.
    IMPORTANT: msg.key() and msg.value() are binary-encoded Schema Registry
    messages (magic byte + 4-byte schema ID + payload). Do NOT decode as UTF-8.
    """
    nonlocal delivered_count, delivery_errors
    if err: delivery_errors += 1; print(f"❌ Failed: {err}")
    else:   delivered_count += 1; print(f"✅ Delivered → Partition {msg.partition()} @ Offset {msg.offset()}")

# Load sample data and inject live timestamps from offset_ms
with open('sample-transactions.json', 'r') as f:
    transactions = json.load(f)

window_ms = 5 * 60 * 1000
now_ms    = int(datetime.now(timezone.utc).timestamp() * 1000)
anchor_ms = (now_ms // window_ms) * window_ms
for tx in transactions:
    tx['transaction_time'] = anchor_ms + tx.pop('offset_ms')

for transaction in transactions:
    try:
        key = {"sku": transaction["sku"]}  # Object, not string
        value = {k: v for k, v in transaction.items() if k != "sku"}

        producer.produce(
            topic='inventory_transactions',
            key=key_serializer(key, SerializationContext('inventory_transactions', MessageField.KEY)),
            value=value_serializer(value, SerializationContext('inventory_transactions', MessageField.VALUE)),
            callback=_delivery_callback
        )
        producer.poll(0)  # trigger callbacks for already-acknowledged messages
        enqueue_count += 1
    except Exception as e:
        print(f"❌ Error enqueuing message: {e}")
        enqueue_errors += 1

# flush() blocks until all in-flight messages are acknowledged and all
# delivery callbacks have fired — delivered_count is accurate after this line.
producer.flush()
print(f"\n📊 Summary: {delivered_count} delivered, {delivery_errors} delivery failures, "
      f"{enqueue_errors} enqueue errors (enqueued: {enqueue_count}/{len(transactions)})")
```

### 5. Documentation Generation

Generate comprehensive documentation for the streaming system:

#### SETUP.md
Prerequisites, setup steps (credentials, deploy, verify, test), troubleshooting, cleanup.

#### README.md
Overview, architecture diagram (Mermaid), quick start, features.

#### TESTING-APPROACH.md
**4 Required Query Types:**
1. Raw Stream: `SELECT * FROM source_table LIMIT 10;`
2. Aggregated State: `SELECT * FROM dest_table ORDER BY key;`
3. Windowed: TVF syntax with window_start, window_end
4. Filtered: Business logic validation

Include SQL, expected output, verification criteria, and explanation for each.

### 6. Validation & Quality Checks

**Terraform — critical checks:**
- [ ] No `stream_governance` block on `confluent_environment`
- [ ] No `confluent_kafka_topic` for Flink-owned topics; no `"compression.type"` in topic config
- [ ] Each API key `depends_on` its specific role binding (not `time_sleep`)
- [ ] All Flink DDL uses plain `CREATE TABLE` (not `CREATE TABLE IF NOT EXISTS`)
- [ ] `.env` heredoc has no leading spaces

**Re-apply on a Partially-Provisioned Environment:**
If a previous `terraform apply` failed mid-run (e.g. a Flink statement errored), the Confluent Flink catalog may hold orphaned tables while Terraform state is out of sync. Before re-applying:
1. Run `terraform state rm confluent_flink_statement.<name>` for each failed/tainted Flink statement resource
2. Manually drop the orphaned table via the Confluent Console or Flink SQL shell: `DROP TABLE IF EXISTS <table_name>;`
3. Then re-run `terraform apply` — the plain `CREATE TABLE` will recreate cleanly
Never add `DROP TABLE IF EXISTS` as a `confluent_flink_statement` resource in Terraform; it creates fragile ordering dependencies and leaves ghost resources in state.

**Resetting stale Kafka topic data (watermark frozen in the past):**
If a Kafka topic already contains records with historical timestamps, the Flink job's per-partition watermark is frozen at the oldest event time even after fresh data arrives. The global watermark = `min(all partition watermarks)` — one stale partition blocks every window from closing.

The only reliable fix is to wipe the topic data before restarting the Flink job:
```bash
# Targeted destroy — keeps cluster, environment, service account, and API keys intact
terraform destroy \
  -target=confluent_flink_statement.fraud_detection_job \
  -target=confluent_flink_statement.create_fraud_alerts_table \
  -target=confluent_flink_statement.create_transactions_table \
  -target=confluent_flink_compute_pool.main \
  -auto-approve

# Delete stale topics — Terraform recreates them via Flink DDL on next apply
confluent kafka topic delete <source_topic> --force
confluent kafka topic delete <dest_topic> --force

terraform apply -auto-approve
```
Do **not** recreate topics manually — Terraform's Flink `CREATE TABLE` auto-creates the backing Kafka topics with the correct partition count, replication, and schema registration.

**Flink SQL — critical checks:**
- [ ] Both `key.format` and `value.format` = `'json-registry'` on every table
- [ ] `'kafka.consumer.isolation-level' = 'read-uncommitted'` on every table
- [ ] `DISTRIBUTED BY` on source tables; `PRIMARY KEY` on destination tables
- [ ] Key/PK columns first in schema; TVF window syntax; no backticks in `DESCRIPTOR()`

**Python — critical checks:**
- [ ] `offset_ms` in sample JSON (never absolute timestamps); window-boundary anchoring
- [ ] Watermark trigger record included (`offset_ms ≥ window_ms + slack_ms + buffer_ms`)
- [ ] Key as object `{"col": val}`; `JSONSerializer` for both key and value
- [ ] Delivery counted via closure after `flush()` (not `success_count++` before flush)

---

## Common Pitfalls to Avoid

### Terraform Pitfalls
1. ❌ Using provider version < 2.68.0 (Flink unsupported)
2. ❌ Wrong API key associations (Flink → Region, not Cluster)
3. ❌ Wrong role binding scope (FlinkDeveloper → Environment, not Region)
4. ❌ Missing time_sleep before Flink statements
5. ❌ Using compute pool REST endpoint (not exposed by provider)
6. ❌ Leading spaces in .env file content (breaks dotenv parsing)
7. ❌ Omitting inline `credentials` in `confluent_flink_statement`
8. ❌ Setting only partial provider-level Flink settings; if one of `flink_api_key`, `flink_api_secret`, `flink_rest_endpoint`, `organization_id`, `environment_id`, `flink_compute_pool_id`, or `flink_principal_id` is set, all must be set
9. ❌ Omitting `properties.sql.current-catalog` and `properties.sql.current-database` on Flink statements when creating tables/jobs
10. ❌ Adding a `stream_governance` block to `confluent_environment` — omit it entirely; Confluent auto-provisions Schema Registry without it. `ESSENTIALS` does not provision Schema Registry and will cause `data.confluent_schema_registry_cluster` to fail with "no schema registry clusters found".
11. ❌ Adding `"compression.type"` to Kafka topic `config` — this property is **read-only after topic creation**; Terraform will error on every subsequent `apply` trying to update it. Only use `"cleanup.policy"` and `"retention.ms"` in topic configs.

### Flink SQL Pitfalls
1. ❌ Using `connector`, `topic`, `kafka.topic`, or `bootstrap.servers` properties
2. ❌ Specifying only value.format (must specify BOTH key.format and value.format)
3. ❌ Using deprecated GROUP BY TUMBLE syntax (use TVF instead)
4. ❌ Missing DISTRIBUTED BY for tables without PRIMARY KEY
5. ❌ Key columns not first in schema when using DISTRIBUTED BY
6. ❌ Using `CREATE TABLE IF NOT EXISTS` in Flink DDL statements — always use plain `CREATE TABLE`. Confluent Flink is not Terraform-idempotent: `IF NOT EXISTS` silently re-uses stale schema from a previous (possibly failed) run, which breaks watermark registration (time attributes) and causes `The window function requires the timecol is a time attribute type` on subsequent jobs. A fresh environment always gets a clean `CREATE TABLE`; a re-run should destroy and re-create.
7. ❌ Using backtick-quoted or `$rowtime` in `DESCRIPTOR()` — always use `DESCRIPTOR(column_name)` with no backticks, e.g. `DESCRIPTOR(transaction_time)`. Backtick quoting causes `Unknown identifier` errors in Confluent Flink SQL.

### Python Pitfalls
1. ❌ Using string key instead of object: `"LAPTOP-001"` vs `{"sku": "LAPTOP-001"}`
2. ❌ Using ISO 8601 timestamps instead of milliseconds: `"2024-01-01T12:00:00Z"` vs `1704067200000`
3. ❌ Wrong serializer (must use JSONSerializer for json-registry format)
4. ❌ Attempting to decode Schema Registry messages in delivery callback:
   ```python
   # ❌ WRONG: This will fail with UnicodeDecodeError
   def delivery_callback(err, msg):
       key_data = json.loads(msg.key().decode('utf-8'))  # Binary Schema Registry format!

   # ✅ CORRECT: Don't decode serialized messages in callback
   def delivery_callback(err, msg):
       print(f"✅ Delivered → Partition {msg.partition()} @ Offset {msg.offset()}")
   ```
   **Reason:** `msg.key()` and `msg.value()` return binary-encoded Schema Registry messages (with magic byte + schema ID + payload), not plain UTF-8 JSON strings.
5. ❌ **Absolute timestamps in sample JSON files**: Storing epoch values like `"transaction_time": 1700000010000` directly in the JSON file freezes the Flink watermark permanently. Every partition that receives such a record has its watermark frozen at that historical point. Flink's global watermark = `min(all partitions)` — one stale partition blocks every window from closing. **Fix:** store `offset_ms` (relative ms from first event) and anchor to `(now_ms // window_ms) * window_ms` at produce-time. See Sample Data Generation section.
6. ❌ **Tumbling Window Misalignment**: Generating events that span multiple window boundaries
   ```python
   # ❌ WRONG: naive datetime, wrong on non-UTC hosts; events straddle windows
   base_time = datetime.now()
   for i in range(8):
       timestamp = base_time + timedelta(seconds=i * 37.5)

   # ✅ CORRECT: timezone-aware UTC, aligned to epoch window boundary
   now = datetime.now(timezone.utc)
   minutes = ((now.minute // 5) + 1) * 5   # next boundary
   if minutes < 60:
       base_time = now.replace(minute=minutes, second=0, microsecond=0)
   else:
       base_time = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
   for i in range(12):
       timestamp = base_time + timedelta(seconds=i * 20)  # all within one window
   ```
   **Impact:** Windowed aggregations split events across windows; counts/sums are wrong and `HAVING COUNT(*) > 10` never fires.
7. ❌ **Counting enqueues as deliveries**: `success_count++` inside the `produce()` try-block (before `flush()`) counts messages queued, not broker-confirmed. A network failure after `flush()` is silently counted as success. Use a closure-based `_delivery_callback` that increments `delivered_count`; read it only after `flush()` returns.
8. ❌ Missing error handling
9. ❌ Using "on-failure" restart for one-time jobs


---

## Domain Adaptation Examples

**Retail → Finance:** sku→account_id, branch→branch_id, quantity→amount, transaction_type→DEPOSIT/WITHDRAWAL

**Retail → IoT:** sku→device_id, branch→location, quantity→temperature, use windowed AVG/MIN/MAX

**Retail → Healthcare:** sku→patient_id, branch→ward, quantity→heart_rate, use ROW_NUMBER() for latest values with alert thresholds

---

## Output Format

### File Structure
```
project-root/
├── terraform/
│   ├── providers.tf
│   ├── variables.tf
│   ├── terraform.tfvars.example
│   ├── main.tf
│   ├── outputs.tf
│   └── README.md
├── python/
│   ├── requirements.txt
│   ├── .env.example
│   ├── sample-transactions.json
│   ├── produce_messages.py
│   └── README.md
├── SETUP.md
├── README.md
├── TESTING-APPROACH.md
└── .gitignore
```

---

## End of Skill Document
