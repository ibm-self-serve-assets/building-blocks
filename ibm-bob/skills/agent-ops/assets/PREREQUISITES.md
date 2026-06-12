# 🛡️ Agent Ops — Prerequisites

Everything a developer needs in place before invoking this Bob skill. Confirmed during validation against a real WXO agent on ADK 2.9.0 / eval-framework 1.4.9.

If any prerequisite is missing, Bob will tell you — but having these ready up front avoids a stop-and-fetch loop mid-conversation.

---

## 1. Software

| Component | Version | Purpose | Install |
|---|---|---|---|
| **[Bob](https://bob.ibm.com)** | latest | The skill runs inside Bob | See bob.ibm.com for install |
| **Python** | **3.12** (3.11 may work; **3.13+ not supported** — eval-fw has C-extension wheels for 3.12 only at present) | venv for the WXO ADK | `pyenv install 3.12` or system Python |
| **Docker runtime** | recent | Required for WXO Developer Edition Lima VM (the WXO server, Langfuse, Milvus, OpenSearch, ClickHouse, ~20 containers total) | Docker Desktop, Rancher Desktop, or Colima |
| **`uv` / `uvx`** | latest | Launches the WXO docs MCP server (see `mcp.json`) | `pip install uv` |
| **WXO ADK with `[agentops]` extra** | `>= 2.6.0, < 3.0.0` (pulls eval-fw `>= 1.4.0, < 2.0.0`) | The CLI Bob emits commands for | `pip install "ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0"` |

### Why this ADK/eval-fw floor

- ADK 2.1.0 added `--with-langfuse` Langfuse-judge path.
- ADK 2.5.0 added the traces CLI + Python SDK.
- ADK 2.6.0 added `traces search --last` flag + a red-teaming `plan`/`run` stability fix.
- Eval-framework 1.4.x clears 1.2.x (deprecated 405b judge crash) and 1.3.x (breaking changes).

Bob runs a `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` check at the entry to any module. If your installed versions are below the floor, Bob will tell you and emit the upgrade command.

---

## 2. Credentials

### 2a. For DevEd `.env` (Docker image pull authentication)

Drop into `<your-agent>/.env`:

```
WO_DEVELOPER_EDITION_SOURCE=orchestrate
WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<your-instance-id>
WO_API_KEY=<your-WXO-SaaS-API-key>
```

These are only used by the DevEd server to pull its private container images from `registry.dl.watson-orchestrate.ibm.com`. Any valid SaaS WXO key works; the local server doesn't actually call out to the SaaS instance during eval.

### 2b. For watsonx.ai (required for RAG judges)

The eval framework's judges (Faithfulness, Relevancy, etc.) call watsonx.ai. You need:

```
WATSONX_APIKEY=<your IBM Cloud IAM API key>
WATSONX_PROJECT_ID=<your watsonx project ID>          # OR
WATSONX_SPACE_ID=<your WML-bound deployment space ID>
```

Where to get them:
- `WATSONX_APIKEY` → IBM Cloud → Manage → Access (IAM) → API keys → Create
- `WATSONX_PROJECT_ID` → watsonx.ai console → your project → Manage tab → Project ID
- `WATSONX_SPACE_ID` → watsonx.ai console → deployments → your space → space ID. **The space must be associated with a watsonx Machine Learning instance** — confirm in the space's "Manage" tab. Projects are usually pre-bound; spaces sometimes are not.

If you skip this, the agent conversation will run but RAG metrics (`kb_metrics.csv`) will be empty and the judges will error with `403` from `*.ml.cloud.ibm.com`.

### 2c. For Langfuse (required for cost/latency analysis)

After `orchestrate server start -e .env -l` brings up the bundled Langfuse on `http://localhost:3010`:

1. Log into the Langfuse UI:
   - URL: `http://localhost:3010`
   - User: `orchestrate@ibm.com`
   - Password: printed in the terminal on the **first** `server start` (set by you on subsequent logins). If you've forgotten it and want a reset, `orchestrate server purge` wipes everything.
2. Settings → API Keys → Create new API keys.
3. Export:
   ```
   export LANGFUSE_BASE_URL="http://localhost:3010"
   export LANGFUSE_PUBLIC_KEY="pk-lf-..."
   export LANGFUSE_SECRET_KEY="sk-lf-..."
   ```
4. These are **session-scoped** env vars; re-export them in any new terminal.

For cost computation to work, you also need to register your agent's model in Langfuse — see [`../reference/module-observability.md`](../reference/module-observability.md) → `register_model_pricing` for the `POST /api/public/models` recipe. Bob will offer to do this if cost data shows as `0`.

---

## 3. Hardware

| Resource | Minimum | Notes |
|---|---|---|
| **RAM** | 16 GB free for Docker | The Lima VM is allocated 16 GiB by default. WXO server + Langfuse + Milvus + OpenSearch + ClickHouse + ~15 other containers compete for it. |
| **Disk** | ~50 GB free | Docker image pull is one-time but heavy (multi-GB images for WXO, Langfuse, ClickHouse, OpenSearch, Milvus). |
| **First-time setup** | ~10 minutes | Image pull + bootstrap. Subsequent server starts ~30 seconds. |

---

## 4. Network access

The mode needs outbound access to:

| Host | Purpose |
|---|---|
| `registry.dl.watson-orchestrate.ibm.com` | Pulling WXO Dev Edition images |
| `docker.io` / `quay.io` | Pulling Langfuse, Milvus, OpenSearch, ClickHouse, Redis, MinIO images |
| `developer.watson-orchestrate.ibm.com` | WXO docs MCP server (used by Bob for live doc search) |
| `*.ml.cloud.ibm.com` | watsonx.ai endpoint for RAG judges |
| `iam.cloud.ibm.com` | IBM Cloud IAM token exchange (for the watsonx API key) |

If you're behind a corporate proxy, configure Docker / `pip` / `curl` to use it before running the server-start.

---

## 5. The agent you want to evaluate

For the full skill capability set:

- **Native WXO agent** — red-teaming (`evaluations red-teaming plan/run`) only supports native agents. External / LangChain / CrewAI agents can still do `quick-eval`, `evaluate`, `analyze`, and observability but not red-teaming.
- **Python `@tool`-decorated functions** — required for `generate` (benchmark synthesis from stories.csv) and `analyze --mode enhanced` (tool docstring enrichment).
- **Standard WXO directory layout**:
  ```
  <your-agent>/
  ├── agent_config.yaml        # required; the `name:` field is referenced in benchmarks
  ├── tools/                   # one or more Python modules with @tool functions
  ├── knowledge_bases/         # optional; YAML config per KB
  └── data/                    # optional; source docs for KBs (CSVs, .txt, .pdf)
  ```
- **Importable into the target env** (DevEd via `orchestrate tools import -k python -f tools/<module>.py`, then `knowledge-bases import`, then `agents import`).

---

## 6. Shell environment

Bob's emitted commands reference one mandatory env var:

```bash
export VENV_ACTIVATE=/path/to/your/.venv/bin/activate
```

Set it in your shell rc (`~/.zshrc`, `~/.bashrc`) so it persists. Every emitted command starts with `source "$VENV_ACTIVATE" && ...` to ensure the venv is active per-invocation.

Also recommended (for the SaaS REST APIs and Langfuse REST queries):

```bash
# Optional — used by emitted curl templates
export LANGFUSE_BASE_URL=...
export LANGFUSE_PUBLIC_KEY=...
export LANGFUSE_SECRET_KEY=...
export WATSONX_APIKEY=...
export WATSONX_PROJECT_ID=...      # OR WATSONX_SPACE_ID=...
```

---

## 7. Quick install summary

If everything above lines up, this is the one-time setup:

```bash
# 1. Create + activate venv
python3.12 -m venv ~/agent-ops-venv
source ~/agent-ops-venv/bin/activate
echo "export VENV_ACTIVATE=$HOME/agent-ops-venv/bin/activate" >> ~/.zshrc

# 2. Install ADK with agentops extra
pip install "ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0"

# 3. Install uv (for the MCP)
pip install uv

# 4. Drop .env into your agent folder (see §2a)
#    Make sure your Docker runtime is running (Rancher Desktop / Docker Desktop / Colima)

# 5. Start the DevEd server with Langfuse
cd <your-agent>
orchestrate server start -e .env -l

# 6. Activate the local env
orchestrate env activate local

# 7. Import your agent
orchestrate tools import -k python -f tools/<your_tools>.py
orchestrate knowledge-bases import -f knowledge_bases/<your_kb>.yaml
orchestrate agents import -f agent_config.yaml

# 8. Open Bob in the agent's project root → invoke the "🛡️ Agent Ops" skill → start
```

---

## 8. Troubleshooting prerequisites

| Symptom | Cause | Fix |
|---|---|---|
| `docker.sock` returns EOF on the `ibm-watsonx-orchestrate` context | Pre-existing Lima VM from an older ADK version in a degraded state | Stop server, move `~/.lima/ibm-watsonx-orchestrate/` aside to a `.bak/` suffix, re-run `orchestrate server start -e .env -l`. ADK will create a fresh VM. |
| `Server started` but `:4321` doesn't accept connections | Containers still bootstrapping (first run can take 7+ min) | Watch the server-start log; the bottleneck is usually Milvus, OpenSearch, or ClickHouse. |
| `403` from `iam.cloud.ibm.com/identity/token` | Ancestor `.env` polluting `WO_INSTANCE` | Run `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"` from your project root. If the path is outside your project, move it aside (`mv <ancestor>/.env <ancestor>/.env.disabled`) for the session. |
| `RuntimeError: WO_API_KEY must be specified for SaaS or IBM IAM auth` | `auth_config.url` in config.yaml is pointing at a cloud URL by mistake | Confirm `config.yaml`'s `auth_config.url` matches your active env. |
| `model_not_supported` for a watsonx model | The model isn't available in your project/space | List supported models in the watsonx.ai console; pick one and update `model_id` in config.yaml. `meta-llama/llama-3-3-70b-instruct` is a common choice. |
| `apikey must be specified` from the eval framework | `WATSONX_APIKEY` env var not exported | `export WATSONX_APIKEY=...` (re-export per shell session). |
| Langfuse `port 3010` connection refused | Server wasn't started with `-l` | Restart with `orchestrate server start -e .env -l`. Remember `-l` and `-i` are mutually exclusive. |
| `space_id ... is not associated with a WML instance` | The watsonx space exists but isn't bound to a Machine Learning instance | Use `WATSONX_PROJECT_ID` instead (projects are usually pre-bound) OR bind your space to a WML instance in IBM Cloud → Resource list. |
| `knowledge-bases import` fails after retries with `MilvusException ... UNAVAILABLE: ipv4:<host>:<port>: recvmsg:Connection reset by peer` (or similar Milvus RPC errors) | **Server-side infrastructure issue on the SaaS tenant's vector DB** — not your environment, not your config. The ADK retries ~75 times before giving up; the failure isn't recoverable from the client side. | Try the KB import again in a few minutes (transient outages usually recover). If persistent, check the IBM watsonx Orchestrate status page or open a support ticket — this is a platform-side issue. **Workaround:** the agent itself may still import successfully even if its KB fails. For tool-only benchmarks (no `conversational_search` goals), you can proceed with `evaluate` despite a failed KB. |
| `KeyError: '<uuid>'` from `evaluate` before any benchmark runs | Tenant has orphaned tool references (agents pointing at deleted tools). The eval framework loads tenant context at startup and crashes on the dead reference. Diagnostic signal: many `[WARNING] - Tool with ID '<uuid>' not found` lines during `orchestrate agents list`. | Clean up via `orchestrate tools remove` / re-import the affected agents without the dead refs. For partner demos, use a fresh tenant. See `reference/module-eval.md` Common failures for the full diagnosis. |

---

## 9. What you do NOT need

For clarity, the following are NOT prerequisites:

- AWS Bedrock credentials — this skill routes judges through watsonx, not Bedrock, when configured per the recipe.
- Groq API key — same reason; `groq/openai/gpt-oss-120b` is available via watsonx.ai.
- A SaaS WXO subscription for the agent's actual deployment — DevEd is sufficient for all 6 capabilities. SaaS is only needed if you want to evaluate an agent already deployed in the cloud.
- An on-prem Cloud Pak for Data instance — this skill supports DevEd + SaaS only. On-prem CPD is out of scope.
