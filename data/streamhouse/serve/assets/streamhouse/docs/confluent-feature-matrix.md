# Confluent feature coverage and honest deployment state

The goal is a cohesive, comprehensive *factory story*, not to falsely claim every Confluent commercial capability is provisioned. The new optional **one-click Terraform deployment** (see [one-click-terraform.md](one-click-terraform.md)) provisions Kafka, schemas, Flink SQL, Tableflow and RTCE when run in an eligible account; this has **not been applied or live-verified** in the authoring environment. Confluent Cloud offerings can vary by region, cluster, entitlements and release channel.

| Building block / capability | Factory Pulse user story | Shipped evidence | What is required to activate in cloud |
|---|---|---|---|
| **Stream: Apache Kafka** | Continuous IoT sensor backbone (3 source topics) | Python `confluent-kafka` producer with Schema Registry wire format (`server/kafka.py`) | Provisioned by `infra/terraform` or existing Confluent Cloud Kafka cluster; credentials in `.env` |
| **Govern: Schema Registry & Contracts** | Contract-first telemetry topics (`factory-iot-telemetry`, `factory-asset-state`, `factory-maintenance-events`) | Draft-07 JSON schemas for keys & values (`server/schemas.py`) | 6 registered JSON subjects + Registry key; lineage visible in Confluent Cloud Stream Governance console |
| **Kafka Connect / Edge Connectors** | Plug into existing MES, ERP, SCADA, OPC-UA gateways | Architectural extension point in Streamhouse story | Appropriate Kafka Connector (e.g. MQTT/OPC-UA/CDC), gateway source and credentials |
| **Transform: Apache Flink SQL (Risk)** | Condition-based predictive risk detection (bearing wear, thermal excursion, quality drift) | `flink/02-risk-ctas.sql` / `flink/02-risk-signal.sql` | Flink compute pool + CTAS statement emitting to `factory-risk-signals` |
| **Transform: Flink Windowed Aggregations** | Production shift / 1-minute tumbling window KPIs (OEE, throughput, energy kWh) | `flink/04-shift-kpis-ctas.sql` / `flink/03-shift-kpis.sql` | Flink compute pool + CTAS statement emitting to `factory-shift-kpis` |
| **Transform: Flink Quality Decisions** | Automated batch-level quarantine and inspection routing | `flink/03-quality-ctas.sql` / `flink/04-quality-alerts.sql` | Flink compute pool + CTAS statement emitting to `factory-quality-alerts` |
| **Govern: Flink Topic Actions / Masking** | PII masking and field governance for downstream sharing | `flink/05-governed-topic-ctas.sql` | Terraform provisions masked CTAS stream (`factory-governed-telemetry`); console Topic Action is also supported |
| **Serve: Tableflow / Apache Iceberg** | Zero-ETL real-time Kafka to Iceberg table conversion for lakehouse analytics | Architecture + Tableflow configuration | Terraform provisions managed Iceberg table on `factory-iot-telemetry`; queryable by Iceberg engines |
| **Serve: Real-Time Context Engine (RTCE)** | Low-latency state materialization for GenAI context retrieval | MCP explorer in UI + `server/mcp.py` + RTCE topic enablement | Terraform enables RTCE on `factory-asset-state` in AWS supported region |
| **Serve: Model Context Protocol (MCP)** | Allow AI agents to dynamically discover and call operational factory tools | Remote MCP reverse proxy (`server/mcp.py`, `/api/mcp/tools`, `/api/mcp/call`) | Global API key + RTCE MCP streamable HTTP endpoint |
| **Confluent Intelligence AI functions** | Time-series anomaly detection with model inference (`AI_DETECT_ANOMALIES`) | Design template and documentation | Availability of Confluent ML functions on Flink compute pool |
| **Confluent Streaming Agents** | Event-driven AI reasoning and tool calling (`AI_RUN_AGENT`) | Design specification and SQL agent template | Supported model, MCP connections, Flink runtime |
| **Operational Business Actions** | Dispatch maintenance work orders and acknowledge incidents | In-app actions (`/api/control`) + optional HTTPS webhook | Service endpoint (e.g. Maximo / ServiceNow), webhook URL configured in `ACTION_WEBHOOK_URL` |
| **IBM watsonx.data Lakehouse** | Unified BI, SQL, and historical analytics over Iceberg tables | Lakehouse integration design | Connect watsonx.data Presto/Trino engine to Iceberg storage/catalog materialized by Tableflow |
| **IBM watsonx Orchestrate** | Autonomous agentic reasoning & execution over factory state | Agent spec (`docs/watsonx-orchestrate-agent-spec.md`) | Provisioned watsonx Orchestrate agent using RTCE MCP tool endpoints |

## Optional anomaly detection

Confluent documentation describes the model-based **AI_DETECT_ANOMALIES** function (Early Access Program as of October 2026), along with other available or preview ML anomaly-detection functions. Use a time-aligned stream of per-asset vibration readings to build a forecast, flag readings outside prediction intervals, then route anomalies to a governed topic.

Reference: https://docs.confluent.io/cloud/current/ai/builtin-functions/detect-anomalies.html

## Optional streaming agent flow

1. Input: `factory-risk-signals` topic from Flink.
2. Agent: read risk type, factory, asset and severity; enrich with current RTCE context or equipment manual retrieval; recommend a safe, human-reviewed maintenance plan.
3. Tool: use Confluent `CREATE CONNECTION` + `CREATE TOOL` to connect to an approved remote MCP service with *read-only discovery* first.
4. Output: recommendation topic with asset, suggested priority and rationale. A separate operator approves work-order submission.
5. Model: configure `CREATE MODEL`, `CREATE AGENT`, and `AI_RUN_AGENT` in Confluent Cloud in a supported region and with the customer's actual model credentials.

Reference: https://docs.confluent.io/cloud/current/ai/streaming-agents/create-and-run-streaming-agents.html

**Confluent Flink Topic Actions, agent tool calls, and factory workflow actions are three distinct concepts.**
