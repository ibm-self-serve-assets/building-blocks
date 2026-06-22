# SPEC-06: watsonx.data and Confluent Tableflow

Back to [specs index](README.md) | [main README](../../README.md)

---

## 1. Purpose

The risk engine produces a continuous stream of scored events, but analytics teams need to query that history — trend analysis, model training, compliance reporting. This spec connects the three output Kafka topics to **IBM watsonx.data** via **Confluent Tableflow**, which continuously materialises each topic into a governed **Apache Iceberg** table.

Once the Iceberg tables exist in watsonx.data, analytics teams can:

- Run SQL queries against the full risk event history using the Presto/Trino engine.
- Join risk scores against historical supplier data and customer orders.
- Train predictive risk models on months of scored events.
- Schedule reports on risk trend by component, supplier, and time window.

**Architecture layer extended:** Layer 5 — Governed analytics.

**Implementation approach:** Confluent Tableflow configuration + watsonx.data catalog registration. No Python code changes required.

---

## 2. Input

| Property | Value |
|----------|-------|
| Topics | `supply_chain_risk_scores`, `supply_chain_recommendations`, `control_tower_alerts` |
| Tableflow storage | Confluent-managed Apache Iceberg tables in an S3-compatible store |
| Sync mechanism | Confluent Tableflow (built-in, no connector needed) |
| Schema source | Confluent Schema Registry — JSON Schema registered for each topic |

---

## 3. Output

| Output | Description |
|--------|-------------|
| Iceberg tables | One Iceberg table per topic in the watsonx.data catalog |
| Table names | `supply_chain_risk_scores`, `supply_chain_recommendations`, `control_tower_alerts` |
| Query engine | IBM watsonx.data Presto/Trino — query via console or JDBC |
| Latency | Near real-time — new Kafka messages appear in Iceberg tables within 1–5 minutes |

---

## 4. Prerequisites

| Requirement | Details |
|-------------|---------|
| Confluent Cloud | Stream Governance package (required for Tableflow) |
| Schema Registry | Schemas must be registered — run `scripts/register_schemas.sh` first |
| IBM watsonx.data | Provision a watsonx.data instance on IBM Cloud |
| Object storage | IBM COS bucket or AWS S3 bucket for Iceberg data files |
| watsonx.data catalog | Create a catalog connected to the COS/S3 bucket |

### Stream Governance requirement

Tableflow is part of the Confluent Cloud Stream Governance package. Enable it in the Confluent Cloud console under **Environment → Stream Governance → Upgrade to Advanced** (or verify it is already included in your contract).

---

## 5. Implementation steps

### Step 1: Register schemas (if not already done)

Tableflow uses the Schema Registry schema to define the Iceberg table structure. Schemas must be registered before enabling Tableflow.

```bash
source .venv/bin/activate
bash scripts/register_schemas.sh
```

Verify registration:

```bash
curl -u "${SCHEMA_REGISTRY_API_KEY}:${SCHEMA_REGISTRY_API_SECRET}" \
  "${SCHEMA_REGISTRY_URL}/subjects" | python -m json.tool
```

### Step 2: Create the COS / S3 bucket for Iceberg data

If using IBM COS, create a bucket named `scrc-tableflow-iceberg` (or your preference) following the IBM COS steps in [SPEC-05](SPEC-05-ibm-cos-data-lake.md), steps 1–2. Note the bucket name and endpoint.

If using AWS S3, create a standard bucket in the same region as your Confluent cluster.

### Step 3: Enable Tableflow on each output topic

In the Confluent Cloud UI:

1. Open your cluster → **Topics**.
2. Click `supply_chain_risk_scores` → **Tableflow → Enable**.
3. Select the storage backend (IBM COS / S3) and enter the bucket name and credentials.
4. Choose the catalog (see step 4 — return here after setting up watsonx.data).
5. Repeat for `supply_chain_recommendations` and `control_tower_alerts`.

Using the Confluent CLI:

```bash
confluent tableflow enable \
  --cluster YOUR_CLUSTER_ID \
  --environment YOUR_ENV_ID \
  --topic supply_chain_risk_scores \
  --storage-type s3 \
  --s3-bucket scrc-tableflow-iceberg \
  --s3-endpoint https://s3.us-east.cloud-object-storage.appdomain.cloud \
  --aws-access-key-id YOUR_HMAC_ACCESS_KEY \
  --aws-secret-access-key YOUR_HMAC_SECRET_KEY
```

### Step 4: Provision IBM watsonx.data

1. In IBM Cloud, search for **watsonx.data** and provision an instance (Lite tier is available).
2. Open the watsonx.data console.
3. Go to **Infrastructure manager → Add component → Add bucket**.
4. Select **IBM Cloud Object Storage**, enter the bucket name (`scrc-tableflow-iceberg`), endpoint, and HMAC credentials from step 2.
5. Activate the bucket as an Iceberg catalog named `scrc_risk`.

### Step 5: Register the Iceberg tables in watsonx.data

Once Tableflow is writing Iceberg metadata to the COS bucket, register the tables in watsonx.data:

1. In the watsonx.data console, go to **Data manager → Add table**.
2. Select the `scrc_risk` catalog.
3. Click **Register Iceberg table** and point to the Iceberg metadata file in the bucket:
   ```
   s3://scrc-tableflow-iceberg/supply_chain_risk_scores/metadata/v1.metadata.json
   ```
4. Repeat for `supply_chain_recommendations` and `control_tower_alerts`.

Alternatively, use the Presto query engine to create the tables directly:

```sql
CREATE TABLE scrc_risk.supply_chain_risk_scores
USING ICEBERG
LOCATION 's3://scrc-tableflow-iceberg/supply_chain_risk_scores/';
```

### Step 6: Query the data

In the watsonx.data SQL editor:

```sql
-- Most recent CRITICAL events
SELECT
    event_time,
    component_id,
    supplier_id,
    risk_score,
    root_cause,
    days_of_supply
FROM scrc_risk.supply_chain_risk_scores
WHERE risk_band = 'CRITICAL'
ORDER BY event_time DESC
LIMIT 20;
```

```sql
-- Risk score trend by component over the last 7 days
SELECT
    DATE_TRUNC('hour', CAST(event_time AS TIMESTAMP)) AS hour,
    component_id,
    AVG(risk_score)     AS avg_risk_score,
    MAX(risk_score)     AS max_risk_score,
    COUNT(*)            AS event_count
FROM scrc_risk.supply_chain_risk_scores
WHERE event_time >= CAST(NOW() - INTERVAL '7' DAY AS VARCHAR)
GROUP BY 1, 2
ORDER BY 1 DESC, 3 DESC;
```

```sql
-- Join risk scores with recommendations
SELECT
    r.event_time,
    r.component_id,
    r.risk_band,
    r.risk_score,
    rec.recommended_action,
    rec.confidence
FROM scrc_risk.supply_chain_risk_scores r
JOIN scrc_risk.supply_chain_recommendations rec
  ON r.risk_id = rec.risk_id
WHERE r.risk_band IN ('HIGH', 'CRITICAL')
ORDER BY r.event_time DESC
LIMIT 50;
```

---

## 6. Complete code

No Python code changes are required for this spec. The entire integration is configuration-driven through Confluent Cloud and watsonx.data.

### Reference SQL queries — save as `code/flink-sql/watsonxdata_queries.sql`

```sql
-- ============================================================
-- watsonx.data reference queries for SCRC Iceberg tables
-- Run these in the watsonx.data SQL editor after SPEC-06 setup
-- ============================================================

-- 1. Current risk state per component (latest score)
SELECT
    component_id,
    supplier_id,
    risk_score,
    risk_band,
    days_of_supply,
    root_cause,
    event_time
FROM (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY component_id ORDER BY event_time DESC) AS rn
    FROM scrc_risk.supply_chain_risk_scores
) t
WHERE rn = 1
ORDER BY risk_score DESC;

-- 2. Supplier reliability ranking (average risk score contributed)
SELECT
    supplier_id,
    COUNT(*)            AS total_events,
    AVG(risk_score)     AS avg_risk_score,
    SUM(CASE WHEN risk_band = 'CRITICAL' THEN 1 ELSE 0 END) AS critical_count,
    SUM(CASE WHEN risk_band = 'HIGH' THEN 1 ELSE 0 END)     AS high_count
FROM scrc_risk.supply_chain_risk_scores
GROUP BY supplier_id
ORDER BY critical_count DESC, avg_risk_score DESC;

-- 3. Alert response audit (match alerts to recommendations)
SELECT
    a.alert_id,
    a.severity,
    a.title,
    a.event_time   AS alert_time,
    r.recommended_action,
    r.confidence
FROM scrc_risk.control_tower_alerts a
LEFT JOIN scrc_risk.supply_chain_recommendations r ON a.risk_id = r.risk_id
WHERE a.severity IN ('HIGH', 'CRITICAL')
ORDER BY a.event_time DESC;
```

---

## 7. New `.env` variables

No new variables are added to the Python application. The COS credentials are entered directly in the Confluent Cloud Tableflow UI or stored in `terraform.tfvars` if using the Terraform connector resource from SPEC-05.

---

## 8. Verification

1. Confirm Tableflow is active on each topic in the Confluent Cloud UI: **Topics → supply_chain_risk_scores → Tableflow → Status: Running**.

2. Produce events:

   ```bash
   source .venv/bin/activate
   python -m scrc.producer --scenario supplier_delay --count 100
   ```

3. Wait 2–5 minutes for Tableflow to flush the first Iceberg data file. In the COS bucket, you should see files under:

   ```
   supply_chain_risk_scores/data/
   supply_chain_risk_scores/metadata/
   ```

4. In the watsonx.data SQL editor, run:

   ```sql
   SELECT COUNT(*) FROM scrc_risk.supply_chain_risk_scores;
   ```

   The count should match the number of risk score events produced.

5. If no data appears after 10 minutes:
   - Check the Schema Registry topic subjects: `supply_chain_risk_scores-value` must exist.
   - Check the Tableflow status in Confluent Cloud for error messages.
   - Verify the HMAC credentials have read-write access to the COS bucket.
