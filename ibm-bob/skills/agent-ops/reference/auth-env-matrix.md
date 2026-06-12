# Auth & Environment Matrix

**TRIGGER:** Load when user asks about env vars per capability, the DevEd vs SaaS difference, how to add a SaaS env, what `--type mcsp_v2` vs `ibm_iam` means, ancestor `.env` pollution, Lima VM recovery, or which preflight check applies before a given command.

---

## Targets

### `dev_ed` — Local Developer Edition
- Server runs on `http://localhost:4321`.
- Tools and agents are imported locally.
- Required `.env` (in user's project root):

| Var | Required | Purpose |
|---|---|---|
| `WO_DEVELOPER_EDITION_SOURCE=orchestrate` | yes | Tells the server to pull Dev Edition images |
| `WO_INSTANCE` | yes | Any valid SaaS instance URL; used ONLY to authenticate image pulls |
| `WO_API_KEY` | yes | API key matching `WO_INSTANCE`; used ONLY for image pulls |

**Activation:** `orchestrate env activate local`

No API key re-entry needed for `local`. Cached token at `~/.cache/orchestrate/credentials.yaml.auth.local.wxo_mcsp_token`.

### `saas` — SaaS cloud
- Managed WXO. No local server.
- Auth via JWT cached after `env add --activate`.
- JWT **expires every 2 hours** (per official ADK docs); re-run `env activate` after expiry. This behavior does not exist in `local`/DevEd.

**Hosting platforms (`--type` per the official ADK docs):**

| Hosting platform | `--type` value | Auth mechanism |
|---|---|---|
| AWS-hosted SaaS | `mcsp` *(preferred — auto-tries v2 then v1)* OR `mcsp_v2` / `mcsp_v1` explicitly | Multi-Cloud SaaS Platform (MCSP) tokens |
| IBM Cloud-hosted SaaS | `ibm_iam` | IBM Cloud Identity and Access Management (IAM) |
| On-premises (CPD / Software Hub) | `cpd` (with `--insecure` or `--verify` for self-signed certs) | Username/password OR API key |

**`--type` is OPTIONAL.** Per the ADK docs (https://developer.watson-orchestrate.ibm.com/environment/initiate_environment): *"Optional, usually inferred based on the URL provided."* Specify explicitly only when inference fails. The ADK does NOT publish a public URL-substring → type mapping; the inference is implemented in private `client/utils` helpers (`is_cpd_env`, `is_ibm_cloud_platform`, `is_local_dev`) that check runtime state, not just URL patterns. If you've seen specific URL patterns map to specific types (e.g., `.ibm.com` → AWS/MCSP, `.cloud.ibm.com` → IBM Cloud/IAM), treat that as empirical observation, not a documented contract.

**Activation:**
```bash
orchestrate env add -n <name> -u <URL> [--type <type>] --activate
```

**Common gotcha — `--api-key` is NOT a valid flag on `env add`.** Partner instinct is often to chain `orchestrate env add -n <name> -u <url> --type <type> --api-key <key>` in one shot. The ADK rejects it with `No such option: --api-key`. `--api-key` belongs to `orchestrate env activate`. For non-interactive (scripted) flows, use the two-step pattern:
```bash
orchestrate env add -n <name> -u <URL> --type <type>          # registers env, no auth prompt
orchestrate env activate <name> --api-key <key>               # activates with explicit key
```
`--activate` on `env add` triggers an *interactive* key prompt — fine for humans, breaks scripts.

**REUSE before ADD:** if `orchestrate env list` shows a cached env whose `wxo_mcsp_token_expiry` is in the future, just `activate` it — no re-entry needed. Ask the user which instance their API key is for before guessing.

**HIPAA-regulated clusters:** require `--iam-url`:
```bash
orchestrate env add -n <name> --iam-url https://<iam-url> -u <instance-url>
```

---

## Capability × hosting-platform availability

| Capability | DevEd | AWS SaaS | IBM Cloud SaaS | On-prem CPD / Software Hub |
|---|---|---|---|---|
| Evaluations (`quick-eval`, `evaluate`, `analyze`) | ✓ default | ✓ | ✓ | ✓ **explicitly supported** per ADK eval docs |
| Red-teaming (`list` / `plan` / `run`) | ✓ w/ watsonx auth | ✓ native agents only | ✓ native agents only | ⚠️ undocumented |
| Traces CLI/SDK | ✓ w/ `-i` flag | ❓ docs mention only IBM Cloud SaaS | ✓ default-on | ⚠️ undocumented |
| Langfuse (local) | ✓ w/ `-l` flag | n/a | n/a | n/a |
| Langfuse (hosted) | n/a | ✓ via `settings observability langfuse configure` | ✓ same | ⚠️ undocumented |
| IBM Telemetry | ✓ w/ `-i` flag | n/a | n/a | n/a |

**Important constraints documented in the ADK docs:**
- Evaluations on remote instances run **only in `draft` environments**, NOT production.
- Non-Dallas regions require the `MODEL_OVERRIDE` flag for the eval framework.
- AWS-hosted SaaS has a **10 API key limit per environment**.
- Remote JWTs expire every 2 hours; DevEd tokens don't expire.

**On-prem CPD coverage:** this skill covers DevEd + SaaS first-class. On-prem CPD is **partially supported**: evaluations are officially supported per the ADK docs, but red-teaming / traces CLI / hosted Langfuse availability on CPD is not explicitly documented. If a partner targets on-prem CPD, route to the eval module with confidence; for other modules, attempt and surface platform errors verbatim, OR point to https://developer.watson-orchestrate.ibm.com/environment/onprem_compatibility for the current state.

---

## Capability × target matrix

### `server_up`
- **DevEd:** `orchestrate server start -e .env [-l] [-i]` — pick `-l` (Langfuse) OR `-i` (IBM Telemetry), never both (RULE 8). First run pulls Docker images ~7 min. Subsequent starts ~30 s. Check with `lsof -ti :4321`.
- **SaaS:** N/A — server-less from user perspective.

### `env_activate`
- **DevEd:** `orchestrate env activate local`
- **SaaS:** `orchestrate env add -n <name> -u <URL> --type <type> --activate` then `orchestrate env activate <name>`. If "Scope not found" appears, the API key does not match the env's instance UUID — ask which instance the key is for.

### `evaluate` / `quick-eval`
- **DevEd:** `config.yaml` with `auth_config.url=http://localhost:4321`, `provider: gateway`, explicit token interpolated via heredoc.
  ```yaml
  auth_config:
    url: http://localhost:4321
    tenant_name: local
    token: <mcsp JWT from credentials.yaml — interpolate via shell $()>
  provider_config:
    provider: gateway
    model_id: meta-llama/llama-3-3-70b-instruct
  ```
  The `token:` field does NOT auto-resolve on the gateway provider. Interpolate at command time via the `evaluate_with_explicit_token` pattern in `reference/command-emission.md`.

  Optional env var: `USE_LEGACY_EVAL=FALSE` was used in early drafts to opt into the Langfuse-based judge path. **Superseded** by the `--with-langfuse` flag in ADK 2.1.0+; do not emit the env var.

- **SaaS:** `config.yaml` with cloud URL, `provider: gateway` / `model_proxy` / `watsonx` per the table below:

  | Env vars set | provider | Notes |
  |---|---|---|
  | `WATSONX_SPACE_ID + WATSONX_APIKEY` | `watsonx` | Direct call to `iam.cloud.ibm.com` — bypasses WXO |
  | `WO_INSTANCE + WO_API_KEY` | `model_proxy` | Routes through the activated WXO env |
  | (none of above; `--config gateway`) | `gateway` | Default. Uses cached mcsp JWT. |

### `red_teaming_plan`
- **DevEd:** Supported in ADK 2.6+ IF watsonx auth env vars exported (`WATSONX_APIKEY` + `WATSONX_PROJECT_ID` or `WATSONX_SPACE_ID`). Earlier ADK required SaaS. Refuse if no watsonx auth.
- **SaaS:** `orchestrate env activate <cloud_env>` then `orchestrate evaluations red-teaming plan -a <attacks> -d <datasets> -g <agents> -t <target> -o <output> [-n <max-variants>]`

### `red_teaming_run`
- **DevEd:** `orchestrate env activate local` then `orchestrate evaluations red-teaming run -a <attack-paths> -o <output>`. Native agents only.
- **SaaS:** Same command; native agents only.

### `record`
- **DevEd:** `orchestrate server start -e .env` (no `-l`/`-i` needed), then `orchestrate evaluations record -o <output>`. Captures chat-UI sessions on `:4321`. User chats in browser; record emits `<thread_id>_annotated_data.json` per session.
- **SaaS:** Not supported (requires local chat UI).

### `generate`
- **Both:** `orchestrate evaluations generate -s <stories.csv> -t <tools-path> -o <output>`. Requires Python `@tool`-decorated functions. Active env's LLM expands stories into benchmark JSON.

### `analyze`
- **Both:** `orchestrate evaluations analyze -d <eval_results_dir> [-t <tools-path>] [--mode default|enhanced]`. `--mode enhanced` is LLM-backed; uses `GATE_TOOL_ENRICHMENTS=false` for docstring enrichment suggestions.

### `traces_search` / `traces_export`
- **DevEd:** `orchestrate server start -e .env -i` (mandatory for traces — without `-i`, search returns empty). Then `orchestrate observability traces search --start-time <ISO> --end-time <ISO> [filters]`.
- **SaaS:** Traces on by default — no flag needed. Same `traces search` command.

### `langfuse_local`
- **DevEd:** `orchestrate server start -e .env -l`. Env vars:
  ```
  LANGFUSE_BASE_URL=http://localhost:3010
  LANGFUSE_PUBLIC_KEY=<from UI — Settings → API Keys>
  LANGFUSE_SECRET_KEY=<from UI>
  ```
  First-time login: `orchestrate@ibm.com`, password printed on first server start.
  **ALWAYS** ask user to fetch keys from UI — never extract from logs.

### `langfuse_hosted`
- **SaaS:** `orchestrate settings observability langfuse configure --url <hosted_url> --api-key <key> [...]`. Connects cloud tenant to external Langfuse (self-hosted or Langfuse Cloud). YAML config shape in `reference/module-observability.md`.

---

## Pre-flight checks (Bob auto-runs, read-only)

### Ancestor `.env` pollution
**Why:** `dotenv.load_dotenv()` walks UP the directory tree. A stale `.env` in any ancestor (e.g., `~/src/.env`) gets auto-loaded and silently overrides `config.yaml`'s `auth_config.url` via `os.environ.get("WO_INSTANCE", instance_url)`. Symptom: mysterious `400 Bad Request from iam.cloud.ibm.com/identity/token`.

**Bob runs:**
```bash
python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"
```

**If outside project directory:** warn inline before emitting any eval command. Offer two fixes:
- (a) move ancestor `.env` aside: `mv <ancestor>/.env <ancestor>/.env.disabled`
- (b) override polluting vars inline: `WO_INSTANCE= WO_API_KEY= orchestrate evaluations ...`

### `$VENV_ACTIVATE` set
**Bob runs:**
```bash
echo "VENV_ACTIVATE=${VENV_ACTIVATE:-UNSET}"
```
**If unset:** ask once: "What's the path to your venv's activate script? I'll use it via `$VENV_ACTIVATE` in every emitted command. You can `export VENV_ACTIVATE=/path/to/venv/bin/activate` in your shell rc to make it permanent."

### Watsonx auth
**Why:** For DevEd, gateway provider routes eval framework judges through watsonx. Without `WATSONX_APIKEY` + `WATSONX_PROJECT_ID` (or `WATSONX_SPACE_ID`), RAG judges and red-teaming `plan` fail with 403/401. Pure tool-calling scenarios (no `conversational_search`, no red-teaming) work WITHOUT these vars.

**Bob runs:**
```bash
echo "WATSONX_APIKEY=${WATSONX_APIKEY:+SET}${WATSONX_APIKEY:-UNSET} | WATSONX_PROJECT_ID=${WATSONX_PROJECT_ID:+SET}${WATSONX_PROJECT_ID:-UNSET} | WATSONX_SPACE_ID=${WATSONX_SPACE_ID:+SET}${WATSONX_SPACE_ID:-UNSET}"
```

**If UNSET and Q2 includes red-teaming or benchmarks with `conversational_search`:** warn user and ask them to export.

### Lima VM health
**Why:** WXO ADK bundles its own Lima VM (separate from any Rancher Desktop / Docker Desktop VM). Pre-existing Lima VMs from older ADK versions can end up in degraded state where `docker --context ibm-watsonx-orchestrate ps` returns EOF. This blocks `server start`.

**Bob runs:**
```bash
docker --context ibm-watsonx-orchestrate ps 2>&1 | head -3
```

**If `EOF`:** recovery recipe (preserves old VM as backup):
1. `orchestrate server stop`
2. `mv ~/.lima/ibm-watsonx-orchestrate ~/.lima/ibm-watsonx-orchestrate.bak-$(date +%Y-%m-%d)`
3. `orchestrate server start -e .env -l` (ADK creates fresh VM, ~10 min first run)

**DO NOT use `orchestrate server purge`** unless user explicitly opts in — that nukes the VM without backup, losing any cached images.

### ADK version (RULE 3)
**Bob runs:**
```bash
pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework 2>/dev/null | grep -E "^(Name|Version):"
```

**Pinned versions:**
- `ibm-watsonx-orchestrate` >= 2.6.0, < 3.0.0
- `ibm-watsonx-orchestrate-evaluation-framework` >= 1.4.0, < 2.0.0

**On violation:** tell user installed + required versions. EMIT upgrade (do not run):
```bash
pip install --upgrade "ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0"
```

---

## Why this matrix exists

The WXO docs do NOT publish a consolidated capability × target matrix. This skill owns it. Every module reference file defers HERE instead of restating env-var lists per-command.
