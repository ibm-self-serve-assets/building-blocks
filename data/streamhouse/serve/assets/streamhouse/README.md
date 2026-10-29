# Factory Pulse — IBM Carbon + Confluent Streamhouse

![Factory Pulse](https://img.shields.io/badge/Factory_Pulse-Demo-0f62fe) ![Kafka](https://img.shields.io/badge/Kafka-optional_live_Confluent-198038) ![Data](https://img.shields.io/badge/data-synthetic-orange)

A full-stack manufacturing showcase built around the IBM Streamhouse building blocks: **Stream → Transform → Govern → Serve**, plus open Iceberg analytical delivery and current-state AI context. Every simulation interaction works in a local mode; cloud mode can send **real Schema Registry encoded Kafka events** to Confluent Cloud.

## What you get

| Feature | Included | Runtime status |
|---|---|---|
| Six US factory locations, site selector and clickable plant map | React, Google Maps JS when key configured, offline SVG fallback | Local works; Google Maps requires restricted browser API key |
| 3D interactive animated factory floor | react-three-fiber / Three.js, robotic arms, conveyor and AGV | Local simulated geometry |
| IoT production stream with sensors / OEE / alerts | Python Flask simulation server + SSE updates | Local works |
| Bearing, thermal, quality and surge fault injection | Controlled through UI → backend | Local works |
| Real Confluent Kafka publisher | Python `confluent-kafka` with TLS/SASL + JSON Schema Registry subjects/key and value encoding | Requires Cloud secrets/topics |
| Confluent Cloud Flink SQL | SQL scripts for risk, shift KPIs, quality alerts | Run on your Flink compute pool |
| Flink Topic Actions showcase | Dedup/mask/transform operator walkthrough | Configure in Confluent Data Portal |
| Schema governance | JSON key/value schemas registered by live Kafka producer | Requires Schema Registry |
| Tableflow → Iceberg → watsonx.data | Reference architecture + setup runbook | Provision in Confluent and lakehouse |
| Confluent RTCE / MCP | Real remote tool discovery/calling through backend with secrets | Requires eligible RTCE and authentication |
| AI-style questions | Transparent local rules; not a real LLM | Local works |
| Simulated maintenance / acknowledgments | Actions UI + optional HTTPS webhook | Local works; external workflow opt-in |
| Technical demo story, architecture and deployment playbook | `docs/` | Included |

## One-command Confluent Cloud deployment (Terraform)

**New:** On Windows double-click `deploy\deploy-confluent.cmd`; on macOS/Linux run `./deploy/deploy-confluent.sh` (or use `python scripts/deploy.py up`). Provide your Confluent **Cloud API key AND secret** to the local prompt; confirm the billable plan. The script provisions an isolated AWS Kafka Standard environment, producer/consumer credentials and ACLs, JSON Schema Registry subjects, a Flink compute pool with four continuous transformations including a governed masking stream, Tableflow managed Apache Iceberg, and RTCE MCP, then writes a private `.env` and runs the Carbon/3D UI locally.

[Full deployment, verification, permissions, costs and teardown](docs/one-click-terraform.md). No credentials are included in this archive. The cloud Terraform plan and provider integration have **not** been executed in this authoring environment because Terraform/Internet were unavailable; use `python scripts/deploy.py plan` on a connected machine before live provisioning.

To destroy billable infrastructure after the demo, run `python scripts/deploy.py destroy`. The Cloud API key and secret are needed for destruction. **Closing the local app does not stop Confluent charges.**

## Run in two commands

**Prerequisites:** Node.js 20+ and npm; internet access for dependency installation. For 3D rendering, modern browser with WebGL.

```bash
cp .env.example .env
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The backend is at **http://localhost:4000**.

The first boot defaults to **SIMULATION MODE**. No cloud credentials or Google Maps account is required. The baseline generates telemetry continuously for 6 fictional US locations, 36 modeled robots and dozens of synthetic sensor records per minute. For enterprise deployment, read the security section in `docs/architecture.md`.

### Connect to Confluent Cloud

1. Create three Kafka source topics in your Confluent Cloud environment (names under `server/schemas.py`).
2. Configure `.env` secrets (`STREAM_MODE=kafka`, Kafka bootstrap/API key/secret, Schema Registry URL/API key/secret).
3. Restart; confirm `stream.status: connected` and `stream.sent` increasing at http://localhost:4000/api/health.
4. Optionally deploy the SQL scripts in `flink/`; enable derived consumer, Tableflow and RTCE as separately documented.

**Streamhouse Guide:** [docs/streamhouse-capabilities.md](docs/streamhouse-capabilities.md). **Full setup:** [docs/cloud-setup.md](docs/cloud-setup.md). **Feature coverage:** [docs/confluent-feature-matrix.md](docs/confluent-feature-matrix.md).

Alternatively, build and run the single-container image locally with podman:

    ./deploy/deploy-local.sh          # Windows: deploy\deploy-local.cmd
    ./deploy/deploy-local.sh logs     # follow logs
    ./deploy/deploy-local.sh down     # stop and remove

Open http://localhost:4000. The container serves the compiled frontend and API together. To deploy to IBM Cloud Code Engine: `./deploy/deploy-ce.sh` (`delete` to remove). It builds the image with podman, pushes it to IBM Cloud Container Registry, turns every non-empty value in `.env` into a Code Engine secret (except `PORT`, which Code Engine reserves), and runs the app from that image with the secret injected as environment variables. Requires `ibmcloud login` and the `code-engine` and `container-registry` plugins.

Without containers, start both dev servers with `scripts/start.sh` (or `scripts\start.cmd` on Windows).

## Software inventory

```text
factory-pulse-streamhouse/
├── frontend/src/
│   ├── App.jsx              Carbon-style control tower and 7 demonstration views
│   ├── components/
│   │   ├── PlantMap.jsx     Real Google Maps or labeled offline SVG map
│   │   └── FactoryTwin.jsx  3D robotics + AGV + conveyors
│   ├── twin/                3D kinematics, plantSim.js, plantProfiles.js, lineControl.js
│   ├── sim/                 Hybrid API layer (remote + local browser simulation)
│   ├── sql.js               Flink SQL as viewable source text
│   └── styles.scss          Carbon + industrial control room design
├── server/
│   ├── app.py               Python Flask server / SSE / control actions / MCP routes
│   ├── simulation.py        Sensor physics, 6 plant scenarios, fault injection
│   ├── kafka.py             Confluent Kafka producer + schemas, optional Flink consumer
│   ├── schemas.py           JSON Schema contracts (Draft-07)
│   ├── context.py           Rule-based demo context, explicitly not LLM
│   ├── mcp.py               Real remote Confluent RTCE MCP connector proxy
│   └── plants.py            Factory metadata
├── flink/                   Four deployable Flink SQL recipes
├── infra/terraform/         Full Confluent Cloud Terraform + 4 CTAS SQL queries
├── scripts/                 deploy.py (Terraform bootstrap), start.* (local dev), backup.*
├── deploy/                  Dockerfile + deploy-local.* (podman), deploy-ce.sh (Code Engine), deploy-confluent.*
├── docs/                    Streamhouse capabilities, Cloud setup, architecture, and playbooks
└── .env.example             Server-only secrets and Maps browser key
```

## Health and control API

| Route | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Real Kafka transport status and cloud publish acknowledgments |
| `/api/bootstrap` | GET | Snapshot, sites and supported scenarios |
| `/api/events` | GET | SSE stream; `snapshot`, `alert`, `scenario`, `action`, `cloud`, `flink` event types |
| `/api/simulate` | POST | `{ "siteId":"DET", "scenario":"bearing", "intensity":85 }` |
| `/api/control` | POST | `{ "siteId":"DET", "action":"maintenance" }` |
| `/api/context` | POST | `{ "siteId":"DET", "question":"Which robot needs maintenance?" }` |
| `/api/mcp/tools` | GET | List actual remote RTCE MCP tools if configured |
| `/api/mcp/call` | POST | `{ "name":"tool_from_list", "args":{} }` |
| `/api/stream` | GET | Kafka transport and optional actual Flink output |

## Test and package

```bash
npm test          # Node native test runner
npm run build     # Vite production frontend
npm run check     # both of the above
npm start         # serve compiled dist and API on port 4000
```

> Local quality check at packaging time: **6/6 Node simulation tests pass**. A Vite production build was **not verified** in this authoring environment because external npm dependency installation stalled; run `cd frontend
npm install && npm run check` in a network-enabled dev environment. No claim of live Confluent connectivity is made without credentials.

## Acknowledgement / reference docs

- IBM Streamhouse Building Blocks: https://ibm-self-serve-assets.github.io/building-blocks-docs/streamhouse-core/
- Confluent Cloud Docs: https://docs.confluent.io/cloud/current/
- Google Maps JS Docs: https://developers.google.com/maps/documentation/javascript/load-maps-js-api

Factory locations, assets, incidents, throughput, alerts and KPI values are **synthetic**, intended for demonstration and training only.
