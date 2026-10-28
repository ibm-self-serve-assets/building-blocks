# Factory Pulse — One-command Confluent Cloud deployment

**Scope:** Provisions a NEW demo environment using the official Confluent Terraform provider. Creates managed infrastructure and boots the existing IBM Carbon + 3D Factory Pulse application locally. The live app emits synthetic factory IoT telemetry to **real Confluent Cloud Kafka** using Schema Registry. No physical robot/factory is connected.

**Status:** Infrastructure code and local orchestration are packaged but **not applied to any Cloud organization**. The authoring environment did not have Terraform or external DNS, so `terraform init`, `terraform validate`, `terraform plan`, provider-API calls, npm installation and Cloud end-to-end smoke tests have **not been executed**. Inspect the plan and verify Confluent product eligibility in your account before applying. This is a demo-grade starting point, not a certified/production Terraform module.

## Quick start

Prerequisites: Python **3.10+**, Terraform **1.5+**, Node.js **20+**, npm, internet access to Confluent APIs + Terraform Registry + npm; Confluent Cloud account with billing enabled. Create a **Confluent Cloud resource-management API key and secret** associated with an identity allowed to create environments, clusters, service accounts, API keys and organization-scoped role bindings (typically `OrganizationAdmin`). You need both the **key and secret**, not only the key ID. It is not a Kafka topic API key. **Do not paste credentials into chat, Git, Terraform variable files, screenshots or a frontend form.** The scripts will prompt securely; alternatively export `CONFLUENT_CLOUD_API_KEY` and `CONFLUENT_CLOUD_API_SECRET` in your local shell/CI secrets manager.

### Windows (command line / script)

```cmd
deploy\deploy-confluent.cmd
```

Or run directly with Python:

```cmd
python scripts/deploy.py up
```

Enter the Confluent Cloud API key and secret locally and type **`DEPLOY`** after reviewing the Terraform plan / billing warning. The terminal launches the UI when provisioning succeeds. Keep the terminal open while demonstrating.

### macOS/Linux (single terminal command)

```bash
./deploy/deploy-confluent.sh
```

Or, for all operating systems with Python on PATH:

```bash
python scripts/deploy.py up
```

When complete, visit **http://localhost:5173** and `http://localhost:4000/api/health`. The UI is **local** and Google Maps is optional (no Google Maps cloud project is provisioned). The script uses the offline US map until you add a restricted Google Maps JavaScript browser key in `.env`.

**Unattended build/CI** (billable, review plan beforehand):

```bash
export CONFLUENT_CLOUD_API_KEY='...'    # set via secrets manager if possible
export CONFLUENT_CLOUD_API_SECRET='...' # never commit this value
python scripts/deploy.py up --yes --no-launch
```

## What gets provisioned

| Feature | Terraform object / resulting behavior | Default |
|---|---|---|
| Cloud account isolation | New AWS `us-east-2` Confluent environment with Stream Governance Essentials | On |
| Kafka | Standard single-zone cluster and 3 source topics, 3 partitions each, 7-day retention | On |
| Service identity | Automation admin service account, application service account; Kafka + Schema Registry scoped keys; source write / output read ACLs | On |
| Schema Registry | Six JSON subjects (`-key` and `-value` for the 3 source topics), identical to the Node simulation schemas | On |
| Flink SQL | 5-CFU compute pool, 4 continuous CTAS jobs: failure risk, quality flags, shift KPIs, and a governed/masked downstream topic | On |
| Tableflow | Confluent-managed storage and an ICEBERG table for `factory-iot-telemetry` | On |
| RTCE / MCP | Enable RTCE on `factory-asset-state` in **append** mode, global API key, generated MCP URL and Basic token | On |
| Carbon + digital twin | Installed/run locally using the existing Node.js + Vite app | On |
| Google Maps | Add browser-key manually (Google billing, referrer restriction) | Off |
| Flink Topic Actions | A working **Flink masking transformation** creates `factory-governed-telemetry` automatically. **Creating a named native Topic Action through Confluent's console remains a separate user interaction**. | Guided |
| IBM watsonx.data external catalog | Requires an external catalog/credentials and typically BYOS instead of managed storage. Not provisioned by this Confluent-only stack. | Off |

**Cloud region note:** The default is US East (Ohio) AWS `us-east-2`, in Confluent's October 2026 support matrix for Kafka, Flink, Tableflow, and RTCE. You can change it with `--region us-east-1` or `--region us-west-2` if compatible. Avoid unsupported regions for the full profile.

## Actual environment wiring

```text
Click synthetic US factory -> animated 3D robots -> Python Flask simulation
       -> Schema Registry JSON key/value wire format encoding
       -> Confluent Cloud Kafka Standard (3 source topics)
          -> Flink CTAS: risk / KPI / quality / governed streams
              -> Kafka derived results -> SSE/API monitor in Factory Pulse
          -> Tableflow (Confluent-managed Apache Iceberg)
          -> RTCE materialization -> Global-key MCP endpoint -> Backend MCP tools
```

`STREAM_MODE=kafka` is generated only after a successful `terraform apply`. Never place Kafka/SR/RTCE secrets in `VITE_` variables. The bootstrap URL is normalized from `SASL_SSL://host:9092`. The simulator reports `stream.status: connected` and positive `stream.sent` only after producer acknowledgements. RTCE tools may take additional time to materialize; Tableflow likewise is not immediately queryable after resource activation.

## Configuration / recovery commands

Run these from the unpacked project folder:

```bash
python scripts/deploy.py plan                        # Cloud read and tentative billable plan only
python scripts/deploy.py up --no-rtce                # skip RTCE if not entitled
python scripts/deploy.py up --no-tableflow           # skip Tableflow if unsupported
python scripts/deploy.py up --no-flink               # core Kafka + schemas (no derived topics)
python scripts/deploy.py up --no-launch              # configure Cloud & .env, don't run UI
python scripts/deploy.py run                         # local UI again; Cloud resources unchanged
python scripts/deploy.py status                      # sanitized Terraform outputs (no secrets)
python scripts/deploy.py destroy                     # delete Cloud demo resources and data
```

Optional flags: `--name demo-sandbox-1`, `--region us-west-2`, `--max-cfu 5|10|20|30|40|50`, `--yes` (billable auto-approve). **Keep the same name and region when re-running an existing state.** `plan/up/destroy` prompts for the Cloud API credentials unless provided through environment variables. `status/run` don't require them. If you disable an add-on after it has already been created, Terraform *will plan its removal*; always review the plan and carefully choose the flags used at initial deployment. If a full deployment stops partway through, review the Terraform error and state before retrying with a narrower profile; Terraform is incremental and will not necessarily roll back already-created resources.

To verify:

1. Read `http://localhost:4000/api/health`; the `stream` object should show **connected** and `sent` increasing. Distinguish **simulator state** from **Confluent producer acknowledgement**.
2. In Confluent Cloud, inspect `factory-iot-telemetry`, `factory-asset-state`, and `factory-maintenance-events`, plus key/value JSON subjects. Trigger a bearing failure from the UI.
3. Open Flink statements in the new environment and verify four CTAS pipelines remain RUNNING; check derived `factory-risk-signals`, `factory-quality-alerts`, `factory-shift-kpis`, and `factory-governed-telemetry` topics. All source data is synthetic.
4. For Tableflow, check the topic's Iceberg materialization and catalog after it has ingested records.
5. For RTCE, use the backend `/api/mcp/tools` and the UI's MCP tool explorer to validate real remote tool discovery. **The local question-answering rule engine is not an LLM and does not prove real MCP connectivity.**

### If deployment fails

- **403 / unauthorized:** Cloud provisioning principal may lack `OrganizationAdmin` or permissions to grant it; newly created role grants can take time to propagate. Use a dedicated demo organization with sufficient rights.
- **Flink says table not found:** Schema Registry propagation/catalog inference may lag; rerun Terraform after confirming the subjects and topics exist, or check the `DESCRIBE` statements in `flink/01-create-tables.sql`.
- **Flink SQL rejects a CTAS query:** inspect the three statements in `infra/terraform/sql/`; Flink SQL capabilities and inferred schema types may vary across account/region. Do not claim success if the deployment only partially completed.
- **Tableflow fails:** check Tableflow eligibility, table/subject schema readiness and regional support, retry with `--no-tableflow` after reviewing planned destroys.
- **RTCE fails:** check product eligibility, schema support, and append-mode key semantics. Run `up --no-rtce` for Kafka/Flink/Tableflow only. Current source `factory-asset-state` topic is intentionally not compacted because JSON Schema keys are incompatible with RTCE's raw-byte-only upsert mode.
- **Kafka publisher won't connect:** check port 9092 outbound, DNS, SASL, account keys and topic ACL propagation; Cloud API keys alone cannot be used as Kafka API keys.
- **npm install fails:** npm registry or local environment blocked; the Cloud configuration may already exist. Run `npm install` then `python scripts/deploy.py run` when network access is restored.
- **No Flink output in UI:** CTAS statements may not yet be running, the output topic may not exist yet, or the consumer might lack a group/topic ACL. Backend reports a consumer error rather than fabricating Cloud output.

## Cost and security

**Resources incur real charges.** Standard Kafka, Flink statements/CFUs, Schema Registry usage, Tableflow, and RTCE may all be billable. Flink's `max_cfu=5` is a ceiling, not a statement of cost or zero-cost idle behavior. After your demo run **`python scripts/deploy.py destroy`** and confirm in Confluent Cloud that the environment and resources have disappeared. Stopping the local app **does not stop Cloud billing**. `terraform destroy` also deletes demo data and Tableflow managed snapshots; review carefully.

Terraform state (`infra/terraform/terraform.tfstate`) **contains generated API secrets**. The project `.env` also contains real runtime secrets. Both are gitignored and local files get owner-only permissions on Unix, but Terraform state is not automatically encrypted at rest. Use an encrypted remote backend, secure workstation and appropriate filesystem controls for shared environments, and rotate/destroy demo credentials after use. The manager role is intentionally `OrganizationAdmin` to minimize initial provisioning friction; **not suitable for production**. The app uses a separate Kafka API key with scoped ACLs, but the Schema Registry key and RTCE Global key are owned by the elevated demo manager principal and must not be reused for production. The local Flask demo endpoints are unauthenticated and should **never be exposed publicly**.

## References (verified October 2026)

- [Official Confluent Terraform provider overview](https://docs.confluent.io/cloud/current/clusters/terraform-provider.html)
- [Flink Terraform and statements](https://docs.confluent.io/cloud/current/flink/operate-and-deploy/terraform.html)
- [Confluent Tableflow managed storage](https://docs.confluent.io/cloud/current/topics/tableflow/get-started/quick-start-managed-storage.html)
- [RTCE topics and MCP](https://docs.confluent.io/cloud/current/ai/real-time-context-engine/get-started.html)
- [Supported regions and features](https://docs.confluent.io/cloud/current/get-started/regions.html)
- [Terraform CLI](https://developer.hashicorp.com/terraform/install)
