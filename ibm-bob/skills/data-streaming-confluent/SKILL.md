---
name: data-streaming-confluent
description: Expert Confluent Cloud architect specializing in creating complete, production-ready streaming solutions with Infrastructure-as-Code (Terraform), Apache Flink SQL, and Python producers. Generates structured artifacts organized by domain (code, scripts, documentation) for repeatable, business-focused streaming architectures.
---

# Data Streaming Confluent Skill

## ⚠️ Critical Configuration Requirements

**MANDATORY: These configurations MUST be included in all generated solutions to prevent deployment failures.**

### 1. Schema Registry Timing Dependency
**Problem:** `Error: error reading Schema Registry Clusters: there are no SR clusters in environment`

**Solution:** Schema Registry is auto-provisioned when Kafka cluster is created. MUST wait 60s before reading it.

```hcl
# Wait for Schema Registry auto-provisioning
resource "time_sleep" "wait_for_schema_registry" {
  create_duration = "60s"
  depends_on = [confluent_kafka_cluster.main]
}

# Schema Registry data source with wait
data "confluent_schema_registry_cluster" "main" {
  environment {
    id = confluent_environment.main.id
  }
  depends_on = [time_sleep.wait_for_schema_registry]
}
```

### 2. API Key Environment Blocks
**Problem:** `Error: Environment of the referred resource, if env-scoped`

**Solution:** ALL API keys (Kafka, Flink, Schema Registry) MUST include environment block in managed_resource.

```hcl
resource "confluent_api_key" "kafka_producer" {
  owner { ... }
  managed_resource {
    id = confluent_kafka_cluster.main.id
    # REQUIRED: Environment block
    environment {
      id = confluent_environment.main.id
    }
  }
}
```

### 3. Flink Table / Kafka Topic Ownership
**Problem:** Creating a Kafka topic with Terraform and then running `CREATE TABLE IF NOT EXISTS` for the same name can leave Flink using the already-inferred table (including raw `VARBINARY` columns when schemas are not registered yet). `IF NOT EXISTS` does not redefine the existing inferred table.

**MANDATORY Solution:** Pick exactly one ownership pattern for each Flink-visible stream:

- **Default — Flink-owned typed stream:** do **not** create that topic with `confluent_kafka_topic`. Use Flink `CREATE TABLE`; Confluent creates the backing topic and Schema Registry subjects.
- **Terraform-owned existing topic:** create the topic and register compatible key/value schemas first, then use the **inferred Flink table**. Do **not** run `CREATE TABLE` for the same topic. Use `ALTER TABLE` only for supported metadata/watermark/property changes.

Never generate both `confluent_kafka_topic.<x>` and a Flink `CREATE TABLE <same-topic>` unless the generated design explicitly documents why they are not competing owners.

### 4. Deterministic Continuous Flink SQL
**Problem:** Continuous joins and keyed tables can emit updates/retractions (`UB`/`UA`/`D`), not only inserts. Non-deterministic functions in those pipelines can be rejected by the Flink planner with errors such as `can not satisfy the determinism requirement`.

**MANDATORY Solution:** In continuous `INSERT INTO ... SELECT` jobs that can process updates:

- Do **not** derive IDs, severity, status, `detected_at`, `assessed_at`, or filters from processing-time/random functions such as `LOCALTIMESTAMP`, `CURRENT_TIMESTAMP`, `NOW()`, `CURRENT_DATE`, `CURRENT_TIME`, `CURRENT_ROW_TIMESTAMP`, `UNIX_TIMESTAMP()`, `UUID()`, `RAND()` or `RAND_INTEGER()`.
- Derive timestamps from source event-time columns (`occurred_at`, `event_time`, `reading_time`) or deterministic window boundaries (`window_start`, `window_end`).
- Derive sink keys/IDs from stable business keys, source event IDs, and/or deterministic window boundaries.
- If a rule truly must change only because wall-clock time passes, generate an explicit timer/tick event stream or use an event-time timer/process-table-function pattern. Do not hide wall-clock logic inside `NOW()`/`LOCALTIMESTAMP` in an updating join.

---

## Purpose
This skill transforms business problems into **complete, deployable Confluent Cloud streaming solutions** with:
- **Structured Artifact Organization**: Separate directories for code, scripts, documentation, and configurations
- **Business Domain Focus**: Topic naming and architecture aligned with user's business domain
- **Repeatable Solutions**: Templates and patterns for common use cases (fraud detection, IoT monitoring, inventory management)
- **Production-Ready Infrastructure**: Terraform IaC with proper RBAC, security, and monitoring
- **End-to-End Testing**: Comprehensive testing approach with validation queries

## Objective
Generate **complete streaming architectures** that:
- Solve specific business problems (fraud detection, real-time analytics, event processing)
- Create properly configured Confluent clusters with domain-specific topics
- Provide step-by-step setup, configuration, and testing instructions
- Organize all artifacts in a structured, maintainable directory layout
- Enable users to deploy and test solutions independently

## Key Capabilities

### 1. Business Problem Analysis
- Understand user's business domain and requirements
- Identify key entities, events, and data flows
- Design appropriate streaming architecture patterns
- Select optimal Confluent components (Kafka, Flink, Schema Registry)

### 2. Structured Artifact Generation
```
solution-name/
├── terraform/           # Infrastructure as Code
│   ├── providers.tf
│   ├── variables.tf
│   ├── main.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── python/             # Data producers and consumers
│   ├── producers/
│   ├── consumers/
│   ├── requirements.txt
│   └── .env.example
├── flink/              # Stream processing SQL
│   ├── tables/
│   ├── jobs/
│   └── queries/
├── scripts/            # Automation and utilities
│   ├── setup.sh
│   ├── deploy.sh
│   ├── test.sh
│   └── cleanup.sh
├── docs/               # Documentation
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   ├── TESTING.md
│   └── TROUBLESHOOTING.md
├── config/             # Configuration files
│   └── sample-data/
└── README.md           # Quick start guide
```

### 3. Domain-Specific Topic Design
- Name topics based on business entities and events
- Examples:
  - **Fraud Detection**: `transactions`, `fraud-alerts`, `customer-profiles`
  - **IoT Monitoring**: `sensor-readings`, `device-status`, `alerts`
  - **Order Management**: `orders`, `inventory-updates`, `shipments`

### 4. Complete Solution Components

#### Infrastructure (Terraform)
- Confluent Cloud environment and cluster
- Domain-specific Kafka topics with proper configuration
- Schema Registry integration
- Flink compute pools
- Service accounts and RBAC
- API keys and security

#### Stream Processing (Flink SQL)
- Source table definitions
- Transformation logic
- Aggregation patterns
- Destination tables
- Continuous queries

#### Data Producers (Python)
- Schema-aware message production
- Sample data generation
- Error handling and monitoring
- Delivery callbacks

#### Documentation
- Architecture diagrams
- Setup instructions
- Testing procedures
- Troubleshooting guides

## Workflow

### Phase 1: Requirements Analysis
1. **Understand Business Problem**
   - What business problem are we solving?
   - What are the key entities and events?
   - What insights or actions are needed?

2. **Design Architecture**
   - Identify data sources and sinks
   - Define topic structure and naming
   - Plan stream processing logic
   - Determine aggregation patterns

3. **Define Success Criteria**
   - What does a successful deployment look like?
   - What queries validate the solution?
   - What metrics indicate proper operation?

### Mandatory Flink SQL Generation Gate

Before returning any generated Terraform/Flink solution, perform these checks on the generated artifacts. If any check fails, revise the solution before presenting it.

1. **Build a stream ownership matrix** with one row per Kafka/Flink stream:
   - stream/topic name;
   - owner = `FLINK_CREATE_TABLE` or `TERRAFORM_TOPIC_INFERRED_TABLE`;
   - key schema/key columns;
   - value schema;
   - append vs upsert intent.

2. **Reject ownership collisions:** the intersection between Terraform `confluent_kafka_topic.topic_name` values and Flink `CREATE TABLE` names must be empty for Flink-owned typed streams. Existing Terraform-owned streams must use registered schemas + inferred tables instead of duplicate `CREATE TABLE` DDL.

3. **Build a job determinism matrix** for every continuous `INSERT INTO ... SELECT`:
   - source tables and whether they can emit updates/retractions;
   - sink primary key;
   - output/event timestamp source;
   - ID/key derivation;
   - time-based rule reference timestamp;
   - join state strategy;
   - forbidden/dynamic functions found = **NONE**.

4. **Static forbidden-function scan for continuous jobs:** reject executable job SQL containing `LOCALTIMESTAMP`, `CURRENT_TIMESTAMP`, `CURRENT_TIME`, `CURRENT_DATE`, `CURRENT_ROW_TIMESTAMP`, `NOW(`, `UNIX_TIMESTAMP(`, `UUID(`, `RAND(` or `RAND_INTEGER(` unless the statement is explicitly a one-off/ad-hoc query rather than a continuous materialization job.

5. **Key validation:** confirm every declared primary key is actually unique at the business grain. Use composite keys when needed. Confirm the sink key stays identical when the same logical result is updated/replayed.

6. **Event-time validation:** output timestamps such as `detected_at`, `assessed_at`, `alert_time`, and deadline/severity calculations must come from source event time or deterministic window boundaries. If wall-clock progression is required, generate an explicit tick/timer-event design.

7. **State validation:** every regular join/non-windowed aggregation must either be intentionally unbounded with explicit justification, have an acceptable TTL, or be redesigned as interval/window/temporal processing. Generate `EXPLAIN` SQL files for stateful jobs.

8. **Deployment ordering:** processing statements depend on the Flink DDL or schema/inferred-table resources they reference, plus RBAC readiness. Never add a dependency from Flink DDL to a Terraform topic of the same name when Flink owns the stream.

### Phase 2: Infrastructure Generation

#### Step 1: Terraform Configuration
Generate complete Terraform infrastructure:

**Critical Requirements:**
```hcl
terraform {
  required_version = ">= 1.0"
  required_providers {
    confluent = {
      source  = "confluentinc/confluent"
      version = ">= 2.68.0"  # Required for Flink support
    }
    time = {
      source  = "hashicorp/time"
      version = ">= 0.9.0"   # Required for RBAC and SR provisioning delays
    }
  }
}
```

**Resource Creation Order:**
1. Organization (data source)
2. Environment
3. Kafka Cluster (Basic tier)
4. Service Account
5. **Schema Registry Provisioning Wait (60s)** - Wait for auto-provisioning
6. Schema Registry (data source) - **MUST depend on Kafka cluster**
7. Flink Compute Pool
8. Flink Region (data source)
9. API Keys (3 types: Kafka, Flink, Schema Registry)
10. Role Bindings (CloudClusterAdmin, FlinkDeveloper, EnvironmentAdmin)
11. RBAC Propagation Delay (30s)

**Schema Registry Provisioning (Critical):**

**IMPORTANT:** Schema Registry is auto-provisioned when the first Kafka cluster is created, but it takes time to become available. The data source MUST wait for provisioning to complete.

```hcl
# Wait for Schema Registry to be auto-provisioned
resource "time_sleep" "wait_for_schema_registry" {
  create_duration = "60s"
  
  depends_on = [confluent_kafka_cluster.main]
}

# Schema Registry data source
data "confluent_schema_registry_cluster" "main" {
  environment {
    id = confluent_environment.main.id
  }
  
  # CRITICAL: Must wait for auto-provisioning
  depends_on = [time_sleep.wait_for_schema_registry]
}
```

**API Key Associations (Critical):**

**IMPORTANT:** ALL API keys MUST include an `environment` block within `managed_resource` because all Confluent resources (Kafka clusters, Flink regions, Schema Registry) are environment-scoped.

```hcl
# Kafka API Key → Kafka Cluster (MUST include environment block)
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
    
    # REQUIRED: All resources are environment-scoped
    environment {
      id = confluent_environment.main.id
    }
  }
}

# Flink API Key → Flink Region (MUST include environment block)
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
    
    # REQUIRED: All resources are environment-scoped
    environment {
      id = confluent_environment.main.id
    }
  }
}

# Schema Registry API Key → Schema Registry (MUST include environment block)
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
    
    # REQUIRED: All resources are environment-scoped
    environment {
      id = confluent_environment.main.id
    }
  }
}
```

**Role Bindings (Critical Patterns):**
```hcl
# CloudClusterAdmin → Kafka Cluster (uses rbac_crn)
resource "confluent_role_binding" "kafka_admin" {
  principal   = "User:${confluent_service_account.app.id}"
  role_name   = "CloudClusterAdmin"
  crn_pattern = confluent_kafka_cluster.main.rbac_crn
}

# FlinkDeveloper → Environment (uses resource_name)
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

#### Step 2: Flink SQL Statements

**Critical Flink SQL Rules:**

### A. Topic/Table Ownership — choose one owner

❌ **NEVER generate both of these for the same typed stream by default:**
```hcl
resource "confluent_kafka_topic" "orders" {
  topic_name = "orders"
}
```
```sql
CREATE TABLE orders (...);
```

✅ **Preferred for a new typed Flink stream:** let Flink own it.
```sql
CREATE TABLE orders (...)
WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry'
);
```
Do not create `orders` separately with `confluent_kafka_topic`.

✅ **For an existing/Terraform-owned topic:** create/register the topic and key/value schemas first and consume the inferred Flink table. Use `ALTER TABLE` when a supported table property or watermark needs changing; do not try to redefine it with `CREATE TABLE IF NOT EXISTS`.

### B. Connector/table options

❌ **NEVER use Apache Kafka connector properties in Confluent Cloud Flink SQL:**
```sql
'connector' = 'kafka'
'topic' = 'my-topic'
'kafka.topic' = 'my-topic'
'bootstrap.servers' = '...'
```

✅ **Use Schema Registry formats for typed tables:**
```sql
'key.format' = 'json-registry',
'value.format' = 'json-registry'
```

- Use `DISTRIBUTED BY` for append tables without a declared primary key.
- Use `PRIMARY KEY (...) NOT ENFORCED` only when it represents the real business/upsert key. Use composite keys when uniqueness requires multiple columns.
- Keep key columns first in generated schemas for clarity and serializer alignment.
- Default to `'kafka.consumer.isolation-level' = 'read-committed'`. Use `read-uncommitted` only when the user explicitly accepts possible duplicate/aborted transactional visibility in exchange for lower latency.

### C. Determinism — mandatory for continuous update pipelines

❌ **Do not use these to create keys, timestamps, severity/status, or predicates in continuous updating jobs:**
```sql
LOCALTIMESTAMP
CURRENT_TIMESTAMP
NOW()
CURRENT_DATE
CURRENT_TIME
CURRENT_ROW_TIMESTAMP
UNIX_TIMESTAMP()
UUID()
RAND()
RAND_INTEGER(...)
```

✅ **Use source event time and stable keys instead:**
```sql
-- Stable ID for the same logical risk across replay/update
CONCAT('RISK-', shipment_id, '-', requirement_id) AS risk_id

-- Deterministic event-time timestamp
CASE
  WHEN shipment_occurred_at >= requirement_occurred_at THEN shipment_occurred_at
  ELSE requirement_occurred_at
END AS detected_at
```

For threshold logic that previously used `NOW()`/`LOCALTIMESTAMP`, evaluate relative to the latest relevant event time:
```sql
TIMESTAMPDIFF(
  HOUR,
  CASE
    WHEN s.occurred_at >= r.occurred_at THEN s.occurred_at
    ELSE r.occurred_at
  END,
  r.required_by
)
```

If no new input arrives, that expression intentionally does not "wake up" as wall-clock time passes. If automatic time-based escalation is required, generate a timer/tick event stream or use an event-time timer pattern.

### D. Joins and state

- Assume regular joins between keyed/upsert tables can emit insert/update-before/update-after/delete changelogs.
- Prefer interval joins, windowed joins, or temporal joins when business semantics permit.
- If a regular join is unavoidable, define a defensible state-retention strategy. Generate `STATE_TTL` hints or `sql.state-ttl` only when expiry semantics are acceptable, and document that expired state can change later match behavior.
- Use `EXPLAIN` for every non-trivial continuous `INSERT` before production deployment and review determinism and unbounded-state warnings.

Example TTL hint:
```sql
SELECT /*+ STATE_TTL('s'='30d', 'r'='90d') */
  ...
FROM shipments s
JOIN requirements r
  ON s.material_id = r.material_id;
```

### E. Sink identity

- Every upsert sink must have a stable, deterministic primary key.
- Never use a generated current timestamp or random UUID as the logical primary key of a continuously updated result.
- Windowed results should normally use business key + deterministic `window_start`/`window_end`.

**Source Table Pattern:**
```sql
CREATE TABLE transactions (
  transaction_id STRING,           -- Key column FIRST
  customer_id STRING,
  amount DECIMAL(10, 2),
  transaction_type STRING,
  transaction_time TIMESTAMP(3),
  WATERMARK FOR transaction_time AS transaction_time - INTERVAL '5' SECONDS
) DISTRIBUTED BY (transaction_id) INTO 4 BUCKETS
WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-committed'
);
```

**Destination Table Pattern:**
```sql
CREATE TABLE fraud_alerts (
  alert_id STRING,                 -- Stable deterministic key FIRST
  customer_id STRING,
  alert_time TIMESTAMP(3),         -- Source event time or window boundary
  alert_type STRING,
  risk_score DECIMAL(5, 2),
  PRIMARY KEY (alert_id) NOT ENFORCED
) WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-committed'
);
```

**Advanced Flink SQL Patterns:**

1. **Tumbling Window Aggregation:**
```sql
INSERT INTO aggregated_results
SELECT
  key_column,
  window_end as result_timestamp,
  AVG(metric) as avg_metric,
  MIN(metric) as min_metric,
  MAX(metric) as max_metric,
  COUNT(DISTINCT id) as unique_count,
  ARRAY_AGG(DISTINCT category) as categories
FROM TABLE(
  TUMBLE(TABLE source_table, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTES)
)
GROUP BY key_column, window_start, window_end;
```

2. **Complex Data Types (Arrays and Rows):**
```sql
-- Table with nested structures
CREATE TABLE orders (
  order_id STRING,
  items ARRAY<ROW(sku STRING, quantity INT, price DECIMAL(10,2))>,
  shipping_address ROW(street STRING, city STRING, state STRING, zip STRING),
  WATERMARK FOR order_date AS order_date - INTERVAL '30' SECONDS
) DISTRIBUTED BY (order_id) INTO 6 BUCKETS
WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-committed'
);

-- Unnesting arrays with CROSS JOIN UNNEST
INSERT INTO line_items
SELECT
  order_id,
  item.sku,
  item.quantity,
  item.price
FROM orders
CROSS JOIN UNNEST(orders.items) AS item;
```

3. **Conditional Aggregation with CASE:**
```sql
INSERT INTO alerts
SELECT
  segment_id,
  window_end as alert_timestamp,
  AVG(quality_score) as avg_quality,
  CASE
    WHEN MIN(quality_score) < 0.3 THEN 'CRITICAL'
    WHEN MIN(quality_score) < 0.5 THEN 'HIGH'
    WHEN MIN(quality_score) < 0.7 THEN 'MEDIUM'
    ELSE 'LOW'
  END as severity
FROM TABLE(
  TUMBLE(TABLE road_conditions, DESCRIPTOR(event_timestamp), INTERVAL '5' MINUTES)
)
GROUP BY segment_id, window_start, window_end
HAVING MIN(quality_score) < 0.8;
```

4. **Deterministic IDs and String Functions:**
```sql
-- Stable ID from business/event identity. Safe across replay and updates.
CONCAT('ALERT-', device_id, '-', event_id) AS alert_id

-- For a window result, use the deterministic window boundary.
CONCAT('ALERT-', device_id, '-', CAST(window_end AS STRING)) AS window_alert_id

-- Build messages with deterministic source fields.
CONCAT('Temperature alert: ', CAST(temperature AS STRING), '°C at ', device_id) AS message
```

5. **Array Aggregation:**
```sql
-- Collect distinct values into array
ARRAY_AGG(DISTINCT hazard_type) as hazard_types

-- Create array of rows
ARRAY[ROW(status, timestamp)] as status_history
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
}
```

**Important:** Do NOT rely on partial provider-level Flink configuration. Always specify `rest_endpoint`, `properties`, and inline `credentials` on every `confluent_flink_statement`.

**Statement ordering:**
- A processing job must `depends_on` every Flink table/DDL statement it references.
- Do not make a Flink `CREATE TABLE` depend on a Terraform topic of the same name when Flink is supposed to own that stream.
- For Terraform-owned topics, make schema registration complete before any job that relies on the inferred table schema.

#### Step 3: Environment Configuration

**Auto-generate .env file:**
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
}
```

**Critical:** Strip `SASL_SSL://` prefix from bootstrap endpoint using `replace()`.

### Phase 3: Python Producer Development

**Dependencies (python/requirements.txt):**
```
confluent-kafka[schema-registry]>=2.3.0
orjson>=3.9.0
python-dotenv>=1.0.0
```

**Producer Pattern (python/producers/produce_messages.py):**

**Critical Requirements:**

1. **Message Key Format** (MUST be object):
```python
# ✅ CORRECT
key = {"transaction_id": "TXN-001"}

# ❌ WRONG
key = "TXN-001"
```

2. **Timestamp Format** (MUST be milliseconds):
```python
# ✅ CORRECT
timestamp_ms = int(datetime.now().timestamp() * 1000)

# ❌ WRONG
timestamp_str = "2024-01-01T12:00:00Z"
```

3. **Serializer Selection** (ALWAYS JSON Schema):
```python
from confluent_kafka.schema_registry.json_schema import JSONSerializer

key_serializer = JSONSerializer(key_schema.schema_str, sr_client)
value_serializer = JSONSerializer(value_schema.schema_str, sr_client)
```

**Complete Producer Example:**
```python
from confluent_kafka import Producer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Schema Registry client
sr_client = SchemaRegistryClient({
    'url': os.getenv('SCHEMA_REGISTRY_URL'),
    'basic.auth.user.info': f"{os.getenv('SCHEMA_REGISTRY_API_KEY')}:{os.getenv('SCHEMA_REGISTRY_API_SECRET')}"
})

# Retrieve schemas
key_schema = sr_client.get_latest_version('transactions-key').schema
value_schema = sr_client.get_latest_version('transactions-value').schema

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

def delivery_callback(err, msg):
    """IMPORTANT: msg.key() and msg.value() are binary Schema Registry messages.
    Do NOT decode them as UTF-8 strings."""
    if err:
        print(f"❌ Failed: {err}")
    else:
        print(f"✅ Delivered → Partition {msg.partition()} @ Offset {msg.offset()}")

# Load and produce
with open('sample-data.json', 'r') as f:
    messages = json.load(f)

for msg in messages:
    key = {"transaction_id": msg["transaction_id"]}
    value = {k: v for k, v in msg.items() if k != "transaction_id"}
    
    producer.produce(
        topic='transactions',
        key=key_serializer(key, SerializationContext('transactions', MessageField.KEY)),
        value=value_serializer(value, SerializationContext('transactions', MessageField.VALUE)),
        callback=delivery_callback
    )

producer.flush()
```

### Phase 4: Documentation Generation

#### docs/ARCHITECTURE.md
- Business problem overview
- Solution architecture diagram (Mermaid)
- Component descriptions
- Data flow explanation
- Topic design rationale

#### docs/SETUP.md
- Prerequisites
- Confluent Cloud account setup
- Terraform deployment steps
- Environment configuration
- Verification procedures

#### docs/TESTING.md
**4 Required Query Types:**

1. **Raw Stream Query:**
```sql
SELECT * FROM transactions LIMIT 10;
```
Expected: Recent transaction records
Verification: ✅ Data flowing from producer

2. **Aggregated State Query:**
```sql
SELECT * FROM fraud_alerts ORDER BY alert_time DESC;
```
Expected: Fraud alerts with risk scores
Verification: ✅ Aggregation logic working

3. **Windowed Query:**
```sql
SELECT 
  window_start,
  window_end,
  customer_id,
  COUNT(*) as transaction_count,
  SUM(amount) as total_amount
FROM TABLE(
  TUMBLE(TABLE transactions, DESCRIPTOR(transaction_time), INTERVAL '5' MINUTES)
)
GROUP BY window_start, window_end, customer_id;
```
Expected: 5-minute transaction summaries
Verification: ✅ Windowed aggregations working

4. **Filtered Query:**
```sql
SELECT * FROM fraud_alerts WHERE risk_score > 0.8;
```
Expected: High-risk fraud alerts only
Verification: ✅ Business logic filtering working

#### docs/TROUBLESHOOTING.md
- Common deployment issues
- RBAC permission errors
- Schema Registry problems
- Flink SQL errors
- Producer connection issues

#### scripts/setup.sh
```bash
#!/bin/bash
set -e

echo "🚀 Setting up Confluent Cloud streaming solution..."

# Check prerequisites
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform required"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }

# Deploy infrastructure
cd terraform
terraform init
terraform plan
terraform apply -auto-approve

# Setup Python environment
cd ../python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete!"
```

#### scripts/test.sh
```bash
#!/bin/bash
set -e

echo "🧪 Testing streaming solution..."

# Produce test data
cd python
source venv/bin/activate
python producers/produce_messages.py

echo "✅ Test data produced. Check Flink SQL queries in docs/TESTING.md"
```

#### scripts/cleanup.sh
```bash
#!/bin/bash
set -e

echo "🧹 Cleaning up resources..."

cd terraform
terraform destroy -auto-approve

echo "✅ Cleanup complete!"
```

## Use Case Templates

### 1. Fraud Detection
**Business Problem:** Detect fraudulent transactions in real-time

**Topics:**
- `transactions` - All financial transactions
- `fraud-alerts` - Detected fraud cases
- `customer-profiles` - Customer behavior patterns

**Processing Logic:**
- Calculate transaction velocity per customer
- Detect unusual amounts or locations
- Generate risk scores
- Alert on high-risk transactions

### 2. IoT Sensor Monitoring
**Business Problem:** Monitor device health and environmental conditions

**Topics:**
- `sensor-readings` - Raw sensor data
- `device-status` - Device health metrics
- `alerts` - Threshold violations

**Processing Logic:**
- Calculate rolling averages
- Detect anomalies
- Track device connectivity
- Generate alerts on thresholds

### 3. Order Management
**Business Problem:** Track orders and inventory in real-time

**Topics:**
- `orders` - Customer orders
- `inventory-updates` - Stock changes
- `shipments` - Delivery tracking

**Processing Logic:**
- Update inventory levels
- Calculate order fulfillment times
- Track shipment status
- Alert on low stock

### 4. Customer Analytics
**Business Problem:** Analyze customer behavior in real-time

**Topics:**
- `user-events` - User interactions
- `session-analytics` - Session summaries
- `customer-segments` - Behavioral segments

**Processing Logic:**
- Session aggregation
- Behavior pattern detection
- Segment classification
- Engagement metrics

## Validation Checklist

### Terraform Validation
- [ ] `terraform init` succeeds
- [ ] `terraform validate` passes
- [ ] `terraform plan` shows expected resources
- [ ] No circular dependencies
- [ ] **ALL API keys have environment block in managed_resource** (Kafka, Flink, Schema Registry)
- [ ] Correct API key associations
- [ ] Correct role binding patterns
- [ ] .env file auto-generated
- [ ] All outputs defined

### Flink SQL Validation
- [ ] No forbidden Apache Kafka connector properties
- [ ] Exactly one owner per stream: Flink `CREATE TABLE` **or** Terraform topic + registered schema/inferred table
- [ ] Both `key.format` and `value.format` specified for Flink-owned typed tables
- [ ] `DISTRIBUTED BY` or a business-correct `PRIMARY KEY` present
- [ ] Composite primary keys used where one column is not truly unique
- [ ] Sink keys/IDs are deterministic and stable across replay/update
- [ ] Continuous updating jobs contain no processing-time/random functions (`LOCALTIMESTAMP`, `CURRENT_TIMESTAMP`, `NOW`, `UNIX_TIMESTAMP`, `UUID`, `RAND`, etc.) in keys, output timestamps, severity/status, or predicates
- [ ] `detected_at` / `assessed_at` / alert timestamps come from source event time or deterministic window boundaries
- [ ] Regular joins have bounded-state design (interval/window/temporal join preferred; otherwise documented TTL strategy)
- [ ] `EXPLAIN` generated/reviewed for joins, aggregations, and other stateful jobs
- [ ] Default consumer isolation is `read-committed`; any `read-uncommitted` use is explicitly justified
- [ ] Statements depend on required RBAC/table/schema resources
- [ ] Correct TVF syntax for windows

### Python Validation
- [ ] Valid Python syntax
- [ ] Correct serializer (JSONSerializer)
- [ ] Key as object, not string
- [ ] Timestamps as milliseconds
- [ ] Proper error handling
- [ ] Delivery callbacks implemented
- [ ] Schema retrieval from Registry

### Documentation Validation
- [ ] All required files present
- [ ] Clear step-by-step instructions
- [ ] Architecture diagram included
- [ ] Testing queries provided
- [ ] Troubleshooting guide complete
- [ ] Cleanup documented

### Artifact Organization Validation
- [ ] Proper directory structure
- [ ] Separation of concerns (terraform/python/flink/docs/scripts)
- [ ] Configuration files in correct locations
- [ ] Scripts are executable
- [ ] Sample data provided

## Common Pitfalls to Avoid

### Terraform Pitfalls
1. ❌ **Missing Schema Registry provisioning wait** (causes "no SR clusters" error)
2. ❌ **Schema Registry data source without depends_on** (timing issue)
3. ❌ Provider version < 2.68.0
4. ❌ Wrong API key associations
5. ❌ **Missing environment block in ANY API key's managed_resource** (Kafka, Flink, Schema Registry)
6. ❌ Wrong role binding scope
7. ❌ Missing time_sleep before Flink statements
8. ❌ Leading spaces in .env content
9. ❌ Partial provider-level Flink settings

### Flink SQL Pitfalls
1. ❌ Creating a Terraform Kafka topic and then trying to redefine the same inferred table with Flink `CREATE TABLE IF NOT EXISTS`
2. ❌ Using `LOCALTIMESTAMP`, `CURRENT_TIMESTAMP`, `NOW()`, `UNIX_TIMESTAMP()`, `UUID()`, `RAND()` or similar functions in continuous update/retraction pipelines
3. ❌ Generating sink IDs from wall-clock time or randomness instead of stable business/event keys
4. ❌ Using a primary key that is not actually unique (for example `supplier_id` when state is really per `supplier_id + material_id`)
5. ❌ Regular stream-stream joins with no interval/window/temporal bound and no documented TTL strategy
6. ❌ Assuming a `NOW()`-based rule will automatically re-evaluate when no new event arrives
7. ❌ Using forbidden Apache Kafka connector properties
8. ❌ Specifying only `value.format` for a keyed typed table
9. ❌ Missing `DISTRIBUTED BY` on append tables or missing a correct primary key on upsert tables
10. ❌ Forcing `read-uncommitted` everywhere without understanding the delivery trade-off
11. ❌ Deploying a stateful job without reviewing `EXPLAIN` warnings

### Python Pitfalls
1. ❌ String key instead of object
2. ❌ ISO timestamps instead of milliseconds
3. ❌ Wrong serializer
4. ❌ Decoding Schema Registry messages in callback
5. ❌ Tumbling window misalignment
6. ❌ Missing error handling

### Organization Pitfalls
1. ❌ Mixed concerns in single directory
2. ❌ Hardcoded credentials
3. ❌ Missing documentation
4. ❌ No automation scripts
5. ❌ Unclear file naming

## Quick Reference

### Terraform Versions
```hcl
confluent >= 2.68.0  # Flink support
time >= 0.9.0        # RBAC delays
terraform >= 1.0     # Modern syntax
```

### Flink Format Specification
```sql
'key.format' = 'json-registry',
'value.format' = 'json-registry',
'kafka.consumer.isolation-level' = 'read-committed'
```

### Python Dependencies
```
confluent-kafka[schema-registry]>=2.3.0
orjson>=3.9.0
python-dotenv>=1.0.0
```

### Directory Structure
```
solution-name/
├── terraform/      # Infrastructure
├── python/         # Producers/Consumers
├── flink/          # SQL statements
├── scripts/        # Automation
├── docs/           # Documentation
├── config/         # Configuration
└── README.md       # Quick start
```

## Flink Determinism Failure Playbook

If deployment reports a message similar to:

```text
column(s) ... generated by non-deterministic function ...
can not satisfy the determinism requirement for correctly processing update message
```

apply this sequence:

1. Read the relational plan and confirm whether the query emits updates/retractions (`UB`, `UA`, `D`).
2. Remove dynamic/random functions from projected values, keys, timestamps, severity/status calculations, and filters.
3. Replace processing-time values with source event-time columns or deterministic window boundaries.
4. Replace random/time-based IDs with stable business keys or source event IDs.
5. Check that the sink primary key represents the same logical result across updates.
6. Run `EXPLAIN` again and review determinism plus state warnings before re-applying Terraform.

Do **not** "fix" `LOCALTIMESTAMP` by swapping it for `CURRENT_TIMESTAMP` or `NOW()`; those are also dynamic in streaming execution.

## Confluent Cloud References for These Rules

The generation rules above follow current Confluent Cloud for Apache Flink behavior:

- Determinism and non-deterministic updates: `https://docs.confluent.io/cloud/current/flink/concepts/determinism.html`
- Confluent Cloud vs Apache Flink table/topic behavior: `https://docs.confluent.io/cloud/current/flink/concepts/comparison-with-apache-flink.html`
- SQL hints and `STATE_TTL`: `https://docs.confluent.io/cloud/current/flink/reference/statements/hints.html`
- Query profiler / unbounded state guidance: `https://docs.confluent.io/cloud/current/flink/operate-and-deploy/query-profiler.html`

## Usage Instructions

### To Use This Skill:

1. **Describe Your Business Problem**
   ```
   Example: "I need to detect fraudulent credit card transactions in real-time.
   We process 10,000 transactions per minute and need to flag suspicious
   patterns within seconds."
   ```

2. **Specify Domain Details** (optional)
   - Industry (finance, retail, IoT, healthcare)
   - Scale (volume, velocity)
   - Specific requirements or constraints

3. **Review Generated Solution**
   - Validate architecture design
   - Check topic naming
   - Review processing logic
   - Verify documentation

4. **Deploy Solution**
   ```bash
   ./scripts/setup.sh
   ```

5. **Test Solution**
   ```bash
   ./scripts/test.sh
   ```

6. **Iterate as Needed**
   - Request modifications
   - Add new features
   - Adjust configurations

## Success Metrics

### Infrastructure
- ✅ All resources created successfully
- ✅ Proper RBAC configured
- ✅ Auto-generated credentials
- ✅ No manual configuration needed

### Stream Processing
- ✅ Tables created with correct schemas
- ✅ Jobs running successfully
- ✅ Data flowing through pipeline
- ✅ Correct results in destination

### Code Quality
- ✅ Production-ready error handling
- ✅ Proper schema serialization
- ✅ Clear, comprehensive documentation
- ✅ Organized artifact structure

### User Experience
- ✅ Reproducible from documentation
- ✅ Clear step-by-step instructions
- ✅ Working test queries
- ✅ Troubleshooting guidance
- ✅ Easy cleanup process

## End of Skill Document