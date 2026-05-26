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

❌ **NEVER Use:**
```sql
'connector' = 'kafka'
'topic' = 'my-topic'
'kafka.topic' = 'my-topic'
'bootstrap.servers' = '...'
```

✅ **ALWAYS Use:**
```sql
-- 1. Specify BOTH formats
'key.format' = 'json-registry',
'value.format' = 'json-registry'

-- 2. Use DISTRIBUTED BY for tables without PRIMARY KEY
DISTRIBUTED BY (key_column) INTO 4 BUCKETS

-- 3. Key columns FIRST in schema
CREATE TABLE example (
  key_col STRING,        -- Distribution key FIRST
  other_col STRING,
  value_col INT
) DISTRIBUTED BY (key_col) INTO 4 BUCKETS

-- 4. Set consumer isolation level on ALL tables
'kafka.consumer.isolation-level' = 'read-uncommitted'

-- 5. Use ARRAY_AGG(DISTINCT column) for collecting distinct values
ARRAY_AGG(DISTINCT hazard_type) as hazard_types
```

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
  'kafka.consumer.isolation-level' = 'read-uncommitted'
);
```

**Destination Table Pattern:**
```sql
CREATE TABLE fraud_alerts (
  customer_id STRING,              -- PRIMARY KEY columns FIRST
  alert_time TIMESTAMP(3),
  alert_type STRING,
  risk_score DECIMAL(5, 2),
  PRIMARY KEY (customer_id, alert_time) NOT ENFORCED
) WITH (
  'key.format' = 'json-registry',
  'value.format' = 'json-registry',
  'kafka.consumer.isolation-level' = 'read-uncommitted'
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
  'kafka.consumer.isolation-level' = 'read-uncommitted'
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

4. **String Concatenation and Functions:**
```sql
-- Generate unique IDs
CONCAT('ALERT-', CAST(UNIX_TIMESTAMP() AS STRING), '-', device_id) as alert_id

-- Build messages
CONCAT('Temperature alert: ', CAST(temperature AS STRING), '°C at ', device_id) as message
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
- [ ] No forbidden properties
- [ ] Both key.format and value.format specified
- [ ] DISTRIBUTED BY or PRIMARY KEY present
- [ ] Key columns first in schema
- [ ] Consumer isolation level set on all tables
- [ ] Statements depend on time_sleep
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
1. ❌ Using forbidden connector properties
2. ❌ Specifying only value.format
3. ❌ Missing DISTRIBUTED BY
4. ❌ Key columns not first
5. ❌ Missing consumer isolation level

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
'kafka.consumer.isolation-level' = 'read-uncommitted'
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