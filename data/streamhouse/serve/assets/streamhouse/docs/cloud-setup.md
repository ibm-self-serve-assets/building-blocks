> **Automated path now available:** See [one-click Terraform](one-click-terraform.md), which provisions the live Confluent environment, source schemas, Flink, managed Tableflow, and RTCE where eligible. The remainder of this document is the manual / existing-cluster setup path.

# Confluent Cloud end-to-end setup

The cloud components cannot be configured without an account/credentials. This runbook covers the exact steps after you supply them locally. It reflects Confluent documentation reviewed in October 2026. Feature availability, permissions and billing can change.

## 0. Start locally

```bash
# Copy environment configuration
cp .env.example .env

# Start with Python orchestrator (starts Vite frontend on 5173 + Python Flask backend on 4000)
python scripts/start.py

# Or on Windows:
scripts\start.cmd

# Or on Linux/macOS:
./scripts/start.sh
```

Visit `http://localhost:5173` (Frontend) and `http://localhost:4000/api/health` (Backend). The application initially operates in local simulation mode even if you never enable cloud services.

## 1. Confluent resources

In an existing IBM Confluent / Confluent Cloud environment:

1. Provision Kafka cluster, note **Kafka bootstrap server**, **cluster ID**, environment and region.
2. Create a Kafka cluster API key and secret with permission to write source topics and, if reading derived Flink results, read output topics. Use a separate service account per least privilege.
3. Ensure **Schema Registry** is available; create Schema Registry API key and secret with subjects read/write.
4. Create `factory-iot-telemetry`, `factory-asset-state`, and `factory-maintenance-events` as Kafka topics (3 partitions recommended). Do not give them custom schemas yet; the producer will register its schemas. Optionally set cleanup.policy=compact for `factory-asset-state` before enabling RTCE upsert mode. For Tableflow review additional key/value schema and changelog requirements.
5. Set these variables in **backend** `.env`:

```dotenv
STREAM_MODE=kafka
KAFKA_BOOTSTRAP_SERVERS=pkc-xxxx.us-east-1.aws.confluent.cloud:9092
KAFKA_API_KEY=xxxx
KAFKA_API_SECRET=xxxx
SCHEMA_REGISTRY_URL=https://psrc-xxxx.us-east-1.aws.confluent.cloud
SCHEMA_REGISTRY_API_KEY=xxxx
SCHEMA_REGISTRY_API_SECRET=xxxx
# false = topics already created. true = try to create with admin permissions.
KAFKA_AUTO_CREATE_TOPICS=false
```

Restart the application (`python scripts/start.py`), inspect `http://localhost:4000/api/health`, and confirm `stream.status: connected`. `stream.sent` increases only after Kafka producer acknowledgements. Verify sample records under Confluent Cloud → Topics → Messages and `-key` / `-value` subjects in Schema Registry.

**Do not use** the Kafka REST Proxy schemaless JSON endpoint as a shortcut for Tableflow/RTCE; both require schema information. This project uses Python `confluent-kafka` with Confluent wire-framed schema encoding (`server/kafka.py`).

## 2. Flink SQL — live transformations

1. Create an Apache Flink compute pool in the same environment and region; ensure Flink permissions and access to the source topics.
2. Open a Flink workspace with the current environment and Kafka cluster selected.
3. Run `flink/01-create-tables.sql`: inspect the inferred source table schemas, then run each of the three `CREATE TABLE` statements independently. If your organization applies custom Flink naming conventions, qualify tables accordingly.
4. Start persistent statements from `flink/02-risk-signal.sql`, `flink/03-shift-kpis.sql`, `flink/04-quality-alerts.sql` (each in its own statement).
5. Confirm `factory-risk-signals`, `factory-shift-kpis`, `factory-quality-alerts` topics receive derived messages. Validate inferred field names with `DESCRIBE` before executing. Some catalog/schema combinations may need minor environment-specific adaptations.
6. To view actual Flink output in the UI, give a consumer group read ACLs, then set `KAFKA_CONSUME_DERIVED=true` and restart. Output is displayed in the Flink SQL page under "Derived topic monitor". This is **real Kafka consumption**, not simulator scoring.

## 3. Confluent Topic Actions

In Confluent Cloud Data Portal, open `factory-iot-telemetry` (or a derived stream) → Actions. Demonstrate:

- **Transform topic:** rename or mask a field, change key or serialization format. A managed Flink statement is generated through Confluent UI.
- **Deduplicate:** remove duplicate events, if available in your UI/region.
- **Mask fields:** create an appropriate governed downstream copy, if available in your UI/region.

Do not execute the provided demo's maintenance button as though it were a Flink Topic Action: it is a separate simulated business workflow. The optional `ACTION_WEBHOOK_URL` sends maintenance activity to an external HTTPS endpoint; secure that integration before sharing.

## 4. Tableflow → open lakehouse

1. In Confluent Cloud select the **schema-bearing** `factory-iot-telemetry` or `factory-asset-state` topic, review Tableflow eligibility, and enable Tableflow for **Apache Iceberg**.
2. Choose Confluent-managed storage for simplest proof-of-concept, or supported custom object storage if you need external catalog synchronization or other lakehouse access. Confluent-managed storage has catalog integration restrictions.
3. If external analytics access is needed, configure custom storage and supported catalog integration according to your cloud deployment; publish/consume the Iceberg tables through an Iceberg-capable query engine such as IBM watsonx.data (subject to credential/catalog support in your environment).
4. Validate newly materialized records and snapshots before describing zero-ETL analytics as operational.

Tableflow does not support schema-less topics. Both key and value require schemas. Tableflow eligibility and storage integration vary by cloud and networking configuration.

## 5. Real-Time Context Engine / MCP

Confluent RTCE currently requires **a supported AWS region and supported Kafka cluster type**, with registered topic schemas and appropriate access rights. Verify the precise availability of your cluster/region in the product console.

1. Enable RTCE on `factory-asset-state` in Confluent Cloud → Topics → Context engine. Choose append/upsert behavior using the topic cleanup policy, and ensure your key schema meets requirements.
2. Copy the cluster's MCP endpoint. Confluent documents the pattern:

```
https://mcp.<region>.aws.confluent.cloud/mcp/v1/context-engine/organizations/<org_id>/environments/<env_id>/kafka-clusters/<lkc_id>
```

3. Create appropriate credential token (`base64(key:secret)`) with required `DeveloperRead` permissions. Set:

```dotenv
RTCE_MCP_ENDPOINT=https://mcp.us-east-1.aws.confluent.cloud/mcp/v1/context-engine/organizations/.../environments/.../kafka-clusters/...
RTCE_MCP_BASIC_TOKEN=<base64-of-RTCE-credential-pair>
```

4. Restart backend, go to **AI context / MCP**, press "Discover remote MCP tools" and select the actual tool name/schema exposed by your RTCE endpoint. Supply valid JSON arguments (reflect the discovered tool's JSON schema), then invoke it.

This is a generic MCP tool explorer rather than an LLM agent. For a full AI story, connect your watsonx Orchestrate / agent through the same RTCE MCP endpoint, with independent auth and operator controls. Agentic workflows, model reasoning and physical action execution are not silently emulated by the backend.

## 6. Google Maps

Enable Maps JavaScript API and billing on Google Cloud, restrict browser key by HTTP referrer (e.g., localhost and your demo origin), then add:

```dotenv
VITE_GOOGLE_MAPS_API_KEY=your_restricted_browser_key
VITE_GOOGLE_MAPS_MAP_ID=optional_map_id
```

Restart Vite. Click a factory marker to navigate the connected digital twin. Without a key, the UI displays a clearly labeled illustrative US map with the same interactions. Factory site names are fictional; coordinates represent cities, not industrial addresses.

## Sources

- Confluent Cloud KafkaJS + Schema Registry: https://kafkajs.github.io/confluent-schema-registry/docs/usage/
- Confluent Flink tables: https://docs.confluent.io/cloud/current/flink/reference/statements/create-table.html
- Confluent Flink SQL statements: https://docs.confluent.io/cloud/current/flink/operate-and-deploy/flink-rest-api.html
- Confluent Topic Actions: https://docs.confluent.io/cloud/current/flink/how-to-guides/transform-topic.html
- Tableflow docs: https://docs.confluent.io/cloud/current/topics/tableflow/overview.html
- RTCE overview: https://docs.confluent.io/cloud/current/ai/real-time-context-engine/overview.html
- RTCE MCP setup: https://docs.confluent.io/cloud/current/ai/real-time-context-engine/get-started.html
- Google Maps JS: https://developers.google.com/maps/documentation/javascript/load-maps-js-api
