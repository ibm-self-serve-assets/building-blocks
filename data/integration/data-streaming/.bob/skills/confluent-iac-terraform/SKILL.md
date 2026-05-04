---
name: confluent-iac-terraform
description: Expert guidance for building real-time streaming systems on Confluent Cloud using Infrastructure-as-Code (Terraform), Apache Flink SQL, and Python producers. Adapts to any streaming use case (IoT, finance, retail, healthcare, logistics) while maintaining production-ready quality.
---

# Confluent Cloud Streaming System Builder

## Purpose
This skill defines the process for analyzing streaming use case requirements and generating **complete, production-ready streaming systems** on Confluent Cloud that include:
- Terraform Infrastructure-as-Code for Confluent Cloud resources
- Apache Flink SQL for real-time stream processing
- Python producers with proper schema serialization
- Comprehensive documentation and testing approaches

## Objective
Transform natural language streaming requirements into **deployable streaming systems** that:
- Can be deployed to Confluent Cloud with minimal configuration
- Follow Infrastructure-as-Code best practices
- Implement correct Flink SQL patterns for stream processing
- Include production-ready error handling and monitoring
- Provide clear documentation for reproduction
- Adapt to any streaming domain while maintaining technical correctness

## Documentation Principles
**IMPORTANT**: Generate specifications based on user requirements and streaming best practices.

**Rules:**
- Analyze the user's domain and infer appropriate streaming patterns
- Design schemas that match the business entities and events
- Select aggregation patterns based on use case requirements
- Generate complete, working code without placeholders
- Include all critical technical requirements (versions, formats, RBAC)
- Provide realistic sample data for the domain
- Document testing approaches with specific queries
- State assumptions clearly when inferring requirements

---

## Scope
This skill applies to:
- Real-time data streaming use cases
- Event-driven architectures
- Stream processing and aggregation
- IoT sensor data processing
- Financial transaction processing
- Retail inventory management
- Healthcare vitals monitoring
- Logistics tracking systems
- Any domain requiring real-time data processing

The output is a **complete streaming system** with Terraform, Flink SQL, Python, and documentation.

---

## Procedure

You are a Confluent Cloud streaming architect specializing in Infrastructure-as-Code and real-time data processing. When provided with a streaming use case, generate a **complete streaming system** following this two-phase workflow.

## CRITICAL: Two-Phase Generation Workflow

**Phase 1: Terraform Infrastructure** (defines schema, creates Flink tables)
- Generate all Terraform files
- Deploy infrastructure
- Flink creates schemas in Schema Registry

**Phase 2: Python Producer** (matches deployed schema)
- Retrieve schemas from Schema Registry
- Generate producer matching exact schema
- Test data flow

**Why This Matters:** The Python producer MUST match the schema that Flink registers in Schema Registry. Always generate Terraform first, deploy it, then generate Python.

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
2. Environment: `confluent_environment`
3. Kafka Cluster: `confluent_kafka_cluster` (Basic tier)
4. Service Account: `confluent_service_account`
5. Data source: `confluent_schema_registry_cluster` (auto-provisioned)
6. Flink Compute Pool: `confluent_flink_compute_pool`
7. Data source: `confluent_flink_region`

#### Phase 3: Security & Access

**API Keys (3 types with correct associations):**
```hcl
# Flink API Key → Associated with Flink Region
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
  }
}

# Kafka API Key → Associated with Kafka Cluster
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
  }
}

# Schema Registry API Key → Associated with Schema Registry
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
  }
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

-- 3. Key columns FIRST in schema when using DISTRIBUTED BY
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
  sku STRING,
  branch STRING,
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

**Correct Pattern for Windowed Test Data:**
```python
from datetime import datetime, timedelta

# Round to next window boundary
now = datetime.now()
minutes = ((now.minute // 5) + 1) * 5
base_time = now.replace(minute=minutes if minutes < 60 else 0, second=10, microsecond=0)
if minutes >= 60:
    base_time += timedelta(hours=1)

base_timestamp_ms = int(base_time.timestamp() * 1000)

# Generate events within window (leave 10s buffer)
window_duration_ms = (5 * 60 - 20) * 1000
spacing_ms = window_duration_ms // 7  # For 8 events

events = []
for i in range(8):
    events.append({
        'entity_id': 'ENTITY-001',
        'event_time': base_timestamp_ms + (i * spacing_ms)
    })

# CRITICAL: Add event after window to advance watermark
events.append({
    'entity_id': 'WATERMARK-TRIGGER',
    'event_time': base_timestamp_ms + (6 * 60 * 1000)  # 6 minutes later
})
```

**Best Practices:**
1. Align test data to window boundaries
2. Spread events across window duration minus buffers
3. Include events AFTER window to trigger closure
4. Set watermark delay based on out-of-order tolerance (5-30 seconds)

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
}
```

**Important Provider Note:**
- Do **not** rely on partial provider-level Flink environment variables for [`confluent_flink_statement`](terraform/main.tf:205).
- If you set any of [`flink_api_key`](terraform/providers.tf:15), [`flink_api_secret`](terraform/providers.tf:15), [`flink_rest_endpoint`](terraform/providers.tf:15), [`organization_id`](terraform/main.tf:206), [`environment_id`](terraform/main.tf:209), [`flink_compute_pool_id`](terraform/main.tf:212), or [`flink_principal_id`](terraform/main.tf:215) in the provider, the Confluent provider expects **all seven** to be configured together.
- The most reliable pattern is to keep the provider configured only with cloud credentials and specify [`rest_endpoint`](terraform/main.tf:235), [`properties`](terraform/main.tf:235), and inline [`credentials`](terraform/main.tf:241) on every [`confluent_flink_statement`](terraform/main.tf:205).

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
  value = "https://flink.${var.region}.${var.cloud_provider}.confluent.cloud"
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
KAFKA_BOOTSTRAP_SERVERS=${confluent_kafka_cluster.main.bootstrap_endpoint}
KAFKA_API_KEY=${confluent_api_key.kafka_producer.id}
KAFKA_API_SECRET=${confluent_api_key.kafka_producer.secret}
SCHEMA_REGISTRY_URL=${data.confluent_schema_registry_cluster.main.rest_endpoint}
SCHEMA_REGISTRY_API_KEY=${confluent_api_key.schema_registry.id}
SCHEMA_REGISTRY_API_SECRET=${confluent_api_key.schema_registry.secret}
EOT
}
```

### 4. Python Producer Development

Generate production-ready Python producer with proper serialization:

#### Dependencies (`python/requirements.txt`)
```
confluent-kafka[schema-registry]>=2.3.0
orjson>=3.9.0
python-dotenv>=1.0.0
```

#### Sample Data Generation (`python/sample-transactions.json`)

Generate realistic domain-specific sample data with appropriate entity IDs, value ranges, event types, and timestamps (milliseconds since epoch).

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

# Retrieve schemas
key_schema = sr_client.get_latest_version('inventory_transactions-key').schema
value_schema = sr_client.get_latest_version('inventory_transactions-value').schema

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

# Delivery callback
def delivery_callback(err, msg):
    """Callback for message delivery reports
    
    IMPORTANT: msg.key() and msg.value() are binary-encoded Schema Registry messages.
    Do NOT attempt to decode them as UTF-8 strings in the callback.
    """
    if err:
        print(f"❌ Failed: {err}")
    else:
        print(f"✅ Delivered → Partition {msg.partition()} @ Offset {msg.offset()}")

# Load and produce messages
with open('sample-transactions.json', 'r') as f:
    transactions = json.load(f)

success_count = 0
failure_count = 0

for transaction in transactions:
    try:
        key = {"sku": transaction["sku"]}  # Object, not string
        value = {k: v for k, v in transaction.items() if k != "sku"}
        
        producer.produce(
            topic='inventory_transactions',
            key=key_serializer(key, SerializationContext('inventory_transactions', MessageField.KEY)),
            value=value_serializer(value, SerializationContext('inventory_transactions', MessageField.VALUE)),
            callback=delivery_callback
        )
        success_count += 1
    except Exception as e:
        print(f"❌ Error producing message: {e}")
        failure_count += 1

producer.flush()
print(f"\n📊 Summary: {success_count} successful, {failure_count} failed")
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

Before delivering the streaming system, validate:

**Terraform Validation:**
- [ ] `terraform init` succeeds
- [ ] `terraform validate` passes
- [ ] `terraform plan` shows expected resources
- [ ] No circular dependencies
- [ ] Correct API key associations
- [ ] Correct role binding patterns
- [ ] .env file auto-generated

**Flink SQL Validation:**
- [ ] No forbidden properties (connector, topic, kafka.topic, bootstrap.servers)
- [ ] Both key.format and value.format specified
- [ ] DISTRIBUTED BY or PRIMARY KEY present
- [ ] Key columns first in schema (when using DISTRIBUTED BY)
- [ ] Correct TVF syntax for windows
- [ ] Statements depend on time_sleep

**Python Validation:**
- [ ] Valid Python syntax
- [ ] Correct serializer (JSONSerializer for json-registry)
- [ ] Key as object, not string
- [ ] Timestamps as milliseconds, not ISO strings
- [ ] Proper error handling
- [ ] Delivery callbacks implemented


**Documentation Validation:**
- [ ] All required files present
- [ ] Clear step-by-step instructions
- [ ] Testing queries provided
- [ ] Troubleshooting included
- [ ] Cleanup documented

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

### Flink SQL Pitfalls
1. ❌ Using `connector`, `topic`, `kafka.topic`, or `bootstrap.servers` properties
2. ❌ Specifying only value.format (must specify BOTH key.format and value.format)
3. ❌ Using deprecated GROUP BY TUMBLE syntax (use TVF instead)
4. ❌ Missing DISTRIBUTED BY for tables without PRIMARY KEY
5. ❌ Key columns not first in schema when using DISTRIBUTED BY

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
5. ❌ **Tumbling Window Misalignment**: Generating events that span multiple window boundaries
   ```python
   # ❌ WRONG: Events spread across windows
   base_time = datetime.now()  # e.g., 10:03:15
   for i in range(8):
       timestamp = base_time + timedelta(seconds=i * 37.5)
   # Results: Some events in 10:00-10:05 window, others in 10:05-10:10 window
   
   # ✅ CORRECT: Align to window boundary
   now = datetime.now()
   minutes = ((now.minute // 5) + 1) * 5  # Round to next 5-min boundary
   base_time = now.replace(minute=minutes, second=10, microsecond=0)
   # All events now fall within the same window
   ```
   **Impact:** Windowed aggregations (TUMBLE, HOP) will split events across windows, causing incorrect counts/sums and failed fraud detection patterns.
6. ❌ Missing error handling
7. ❌ Using "on-failure" restart for one-time jobs


---

## Domain Adaptation Examples

**Retail → Finance:** sku→account_id, branch→branch_id, quantity→amount, transaction_type→DEPOSIT/WITHDRAWAL

**Retail → IoT:** sku→device_id, branch→location, quantity→temperature, use windowed AVG/MIN/MAX

**Retail → Healthcare:** sku→patient_id, branch→ward, quantity→heart_rate, use ROW_NUMBER() for latest values with alert thresholds

---

## Quick Reference

### Terraform Versions
```hcl
confluent >= 2.68.0  # Flink support
time >= 0.9.0        # RBAC delays
terraform >= 1.0     # Modern syntax
```

### Flink Format Specification
```sql
-- ALWAYS specify BOTH:
'key.format' = 'json-registry',
'value.format' = 'json-registry'
```

### Python Dependencies
```
confluent-kafka[schema-registry]>=2.3.0
orjson>=3.9.0
python-dotenv>=1.0.0
```

### Schema Naming Convention
```
{table_name}-key
{table_name}-value
```

### Flink REST Endpoint
```hcl
# In statements:
rest_endpoint = data.confluent_flink_region.main.rest_endpoint

# In outputs:
"https://flink.${region}.${cloud}.confluent.cloud"
```

### Flink Statement Authentication
```hcl
properties = {
  "sql.current-catalog"  = confluent_environment.main.display_name
  "sql.current-database" = confluent_kafka_cluster.main.display_name
}

credentials {
  key    = confluent_api_key.flink.id
  secret = confluent_api_key.flink.secret
}
```

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

### Execution Workflow
1. ✅ Analyze user requirements and domain
2. ✅ Design schemas and aggregation patterns
3. ✅ Generate Terraform infrastructure files
4. ✅ Generate Flink SQL statements
5. ✅ Generate Python producer with sample data
6. ✅ Generate documentation (SETUP, README, TESTING)
8. ✅ Validate all components
9. ✅ Present complete system to user

---

## Usage Instructions

### To Use This Skill:

1. **Describe Your Use Case**: Provide a natural language description of your streaming requirements
2. **Specify Domain** (optional): Industry, scale, specific constraints
3. **Review Generated System**: Validate schemas, aggregations, and logic
4. **Deploy**: Follow SETUP.md for deployment
5. **Test**: Use TESTING-APPROACH.md queries to verify
6. **Iterate**: Request modifications as needed

### Example Request (IoT):

```
Build a real-time IoT sensor monitoring system that:
- Collects temperature readings from 100+ devices
- Calculates 5-minute average temperatures per location
- Alerts when temperature exceeds thresholds
- Tracks device health and connectivity
- Processes readings every second
```

---

## Success Metrics

### Infrastructure
- ✅ All Terraform resources created successfully
- ✅ API keys and role bindings configured correctly
- ✅ .env file auto-generated
- ✅ No manual configuration required

### Stream Processing
- ✅ Flink tables created with correct schemas
- ✅ Aggregation job running successfully
- ✅ Data flowing through pipeline
- ✅ Correct results in destination table

### Code Quality
- ✅ Production-ready error handling
- ✅ Proper schema serialization
- ✅ Clear, comprehensive documentation

### User Experience
- ✅ Reproducible deployment from documentation
- ✅ Clear step-by-step instructions
- ✅ Working test queries provided
- ✅ Troubleshooting guidance included

---

## Testing Phase Requirements

**MANDATORY**: After deployment, generate `TESTING-APPROACH.md` with:

**4 Required Test Queries:**
1. Raw Stream: `SELECT * FROM source_table LIMIT 10;`
2. Aggregated State: `SELECT * FROM aggregated_table ORDER BY key;`
3. Windowed: TVF syntax with window_start, window_end
4. Filtered: Business logic validation

Each query needs: SQL, expected output table, verification criteria (✅), explanation.

---

## End of Skill Document