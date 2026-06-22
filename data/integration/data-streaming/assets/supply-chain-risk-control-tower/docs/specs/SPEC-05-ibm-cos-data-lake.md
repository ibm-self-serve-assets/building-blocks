# SPEC-05: IBM Cloud Object Storage Data Lake

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

The risk engine publishes events in real time but does not persist them. This spec adds a long-term data lake by configuring the **Confluent Cloud S3-compatible Sink Connector** to continuously archive all three output topics to IBM Cloud Object Storage (COS) in newline-delimited JSON format.

The result is a queryable, cost-effective event archive that enables:

- Historical trend analysis across risk scores, recommendations, and alerts.
- Model training data for future predictive risk models.
- Audit trail for compliance and governance requirements.
- Input for the watsonx.data / Tableflow integration in [SPEC-06](SPEC-06-watsonxdata-tableflow.md).

**Architecture layer extended:** Layer 5 — Data persistence and archival.

**Implementation approach:** Confluent Cloud managed connector (no code required). Configuration is HMAC key-based — IBM COS provides an S3-compatible API.

---

## 2. Input

| Property | Value |
|----------|-------|
| Topics archived | `supply_chain_risk_scores`, `supply_chain_recommendations`, `control_tower_alerts` |
| Format | Newline-delimited JSON (one Kafka message per line) |
| Partitioning | `TimeBasedPartitioner` — files partitioned by `yyyy/MM/dd/HH` |
| File rotation | Every 1,000 records or 10 minutes, whichever comes first |

---

## 3. Output

| Output | Description |
|--------|-------------|
| COS bucket path | `s3://YOUR_BUCKET/supply_chain_risk_scores/yyyy/MM/dd/HH/*.json` |
| File format | Newline-delimited JSON, one event per line |
| Compression | `gzip` (configurable) |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| IBM Cloud account | [https://cloud.ibm.com](https://cloud.ibm.com) |
| IBM Cloud Object Storage instance | Create a Standard tier COS instance |
| COS bucket | Create a bucket in the same region as your Confluent cluster |
| HMAC credentials | COS service credentials with HMAC enabled — gives `access_key_id` and `secret_access_key` |
| COS endpoint | Regional endpoint, e.g. `s3.us-east.cloud-object-storage.appdomain.cloud` |
| Confluent Cloud | Stream Governance or a Confluent Cloud environment with connector access |
| Confluent CLI or Cloud UI | To create and manage the connector |

### Creating HMAC credentials for COS

1. In IBM Cloud, open your COS instance.
2. Go to **Service credentials → New credential**.
3. Enable **Include HMAC Credential** (toggle on).
4. Click **Add**. Expand the credential and copy `cos_hmac_keys.access_key_id` and `cos_hmac_keys.secret_access_key`.

---

## 5. Implementation steps

### Step 1: Create the COS bucket

1. In the IBM Cloud console, open your COS instance.
2. Click **Create bucket → Quickly get started**.
3. Name it `scrc-data-lake` (or your preference).
4. Select **Cross Region** or **Regional** matching your Confluent cluster region.
5. Leave versioning and encryption at defaults. Click **Create bucket**.

### Step 2: Note the COS endpoint

1. In the COS instance, go to **Endpoints**.
2. Copy the **public** endpoint for your bucket's region, e.g. `s3.us-east.cloud-object-storage.appdomain.cloud`.

### Step 3: Add `.env` variables

Add the variables from section 7. These are used to populate the connector config in the next step.

### Step 4: Create the Confluent connector

Using the Confluent Cloud UI:

1. In your Confluent Cloud environment, open the cluster.
2. Go to **Connectors → Add connector → Amazon S3 Sink**.
3. Fill in the connector configuration using the values from section 6 (Connector configuration).
4. Click **Continue → Launch connector**.

Using the Confluent CLI:

```bash
confluent connect cluster create \
  --cluster YOUR_CLUSTER_ID \
  --environment YOUR_ENV_ID \
  --config-file code/terraform/cos-sink-connector.json
```

The connector config file is the JSON from section 6.

### Step 5: Verify data flow

After 2–3 minutes of the connector running, files should appear in the COS bucket.

---

## 6. Complete code

### Connector configuration — save as `code/terraform/cos-sink-connector.json`

Replace all `YOUR_*` placeholders with your actual values before applying.

```json
{
  "name": "scrc-cos-sink",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "1",
    "topics": "supply_chain_risk_scores,supply_chain_recommendations,control_tower_alerts",

    "s3.region": "us-east-1",
    "s3.bucket.name": "scrc-data-lake",
    "s3.part.size": "5242880",
    "store.url": "https://s3.us-east.cloud-object-storage.appdomain.cloud",

    "aws.access.key.id": "YOUR_COS_HMAC_ACCESS_KEY_ID",
    "aws.secret.access.key": "YOUR_COS_HMAC_SECRET_ACCESS_KEY",

    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.json.JsonFormat",
    "flush.size": "1000",
    "rotate.interval.ms": "600000",

    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "locale": "en_US",
    "timezone": "UTC",
    "timestamp.extractor": "RecordField",
    "timestamp.field": "event_time",

    "schema.compatibility": "NONE",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",

    "confluent.topic.bootstrap.servers": "YOUR_BOOTSTRAP_ENDPOINT",
    "confluent.topic.security.protocol": "SASL_SSL",
    "confluent.topic.sasl.mechanism": "PLAIN",
    "confluent.topic.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"YOUR_KAFKA_API_KEY\" password=\"YOUR_KAFKA_API_SECRET\";"
  }
}
```

### Terraform resource (optional) — add to `code/terraform/main.tf`

If you prefer to manage the connector as infrastructure code, add this resource after the topic block:

```hcl
resource "confluent_connector" "cos_sink" {
  environment {
    id = local.environment_id
  }
  kafka_cluster {
    id = confluent_kafka_cluster.scrc.id
  }

  config_sensitive = {
    "aws.access.key.id"     = var.cos_hmac_access_key_id
    "aws.secret.access.key" = var.cos_hmac_secret_access_key
  }

  config_nonsensitive = {
    "connector.class"         = "io.confluent.connect.s3.S3SinkConnector"
    "name"                    = "scrc-cos-sink"
    "tasks.max"               = "1"
    "topics"                  = "supply_chain_risk_scores,supply_chain_recommendations,control_tower_alerts"
    "s3.region"               = "us-east-1"
    "s3.bucket.name"          = var.cos_bucket_name
    "store.url"               = var.cos_endpoint
    "storage.class"           = "io.confluent.connect.s3.storage.S3Storage"
    "format.class"            = "io.confluent.connect.s3.format.json.JsonFormat"
    "flush.size"              = "1000"
    "rotate.interval.ms"      = "600000"
    "partitioner.class"       = "io.confluent.connect.storage.partitioner.TimeBasedPartitioner"
    "path.format"             = "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH"
    "locale"                  = "en_US"
    "timezone"                = "UTC"
    "timestamp.extractor"     = "RecordField"
    "timestamp.field"         = "event_time"
    "schema.compatibility"    = "NONE"
    "key.converter"           = "org.apache.kafka.connect.storage.StringConverter"
    "value.converter"         = "org.apache.kafka.connect.json.JsonConverter"
    "value.converter.schemas.enable" = "false"
  }

  depends_on = [
    confluent_kafka_topic.topics,
    confluent_role_binding.scrc_env_admin,
  ]
}
```

Add the corresponding variables to `code/terraform/variables.tf`:

```hcl
variable "cos_hmac_access_key_id" {
  description = "IBM COS HMAC access key ID for the S3 sink connector."
  type        = string
  sensitive   = true
  default     = ""
}

variable "cos_hmac_secret_access_key" {
  description = "IBM COS HMAC secret access key for the S3 sink connector."
  type        = string
  sensitive   = true
  default     = ""
}

variable "cos_bucket_name" {
  description = "IBM COS bucket name for the data lake."
  type        = string
  default     = "scrc-data-lake"
}

variable "cos_endpoint" {
  description = "IBM COS S3-compatible endpoint URL."
  type        = string
  default     = "https://s3.us-east.cloud-object-storage.appdomain.cloud"
}
```

---

## 7. New `.env` variables

Add to `.env` and `.env.example` for reference. These values are used in the connector config, not read by the Python application directly.

```dotenv
# IBM Cloud Object Storage — S3 sink connector (SPEC-05)
IBM_COS_HMAC_ACCESS_KEY_ID=your-cos-hmac-access-key-id
IBM_COS_HMAC_SECRET_ACCESS_KEY=your-cos-hmac-secret-access-key
IBM_COS_BUCKET_NAME=scrc-data-lake
IBM_COS_ENDPOINT=https://s3.us-east.cloud-object-storage.appdomain.cloud
```

---

## 8. Verification

1. Start the producer to generate events:

   ```bash
   source .venv/bin/activate
   python -m scrc.producer --scenario supplier_delay --count 50
   ```

2. In the Confluent Cloud UI, open **Connectors → scrc-cos-sink**. The connector status should show **Running** with messages being consumed.

3. After 2–3 minutes (before the flush interval), browse the COS bucket in the IBM Cloud console. You should see a folder structure like:

   ```
   supply_chain_risk_scores/year=2026/month=01/day=15/hour=10/
     supply_chain_risk_scores+0+0000000000.json
   ```

4. Download one file and inspect it:

   ```bash
   # Using IBM Cloud CLI
   ibmcloud cos download --bucket scrc-data-lake \
     --key "supply_chain_risk_scores/year=2026/month=01/day=15/hour=10/supply_chain_risk_scores+0+0000000000.json" \
     --output risk_events.json
   head -5 risk_events.json
   ```

   Each line should be a JSON object matching the `RiskResult` schema.

5. If no files appear after 10 minutes, check the connector logs in the Confluent Cloud UI for authentication errors. The most common cause is an incorrect `store.url` — it must include `https://` and match the COS regional endpoint exactly.
