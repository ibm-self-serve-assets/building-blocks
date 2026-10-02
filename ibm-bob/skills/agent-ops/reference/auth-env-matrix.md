# Auth and environment matrix

**TRIGGER:** questions about SaaS vs Developer Edition vs on-prem, `orchestrate env add --type`, token expiry, `WO_API_KEY`, which capability works where, shared instances, DevEd `.env` and server flags, or Lima VM recovery.

Authoritative doc: https://developer.watson-orchestrate.ibm.com/environment/initiate_environment

---

## Targets

| Target | URL shape | `--type` (inferred; pass only if inference fails) | Notes |
|---|---|---|---|
| SaaS on IBM Cloud | `https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<id>` | `ibm_iam` | IBM Cloud IAM API key (user or service ID with WO User on the instance) |
| SaaS on AWS | `https://api.<region>.watson-orchestrate.ibm.com/instances/<id>` | `mcsp` (tries v2 then v1) | MCSP API key; 10 API keys per environment limit |
| Developer Edition | `http://localhost:4321` (environment `local`) | — | `orchestrate server start -e .env`; `-i` for traces, `-l` for Langfuse (not both) |
| On-prem CPD / Software Hub | `https://<host>:<port>/orchestrate/instances/<id>` | `cpd` (+ `--insecure` or `--verify <cert>`) | evaluations documented (`WO_USERNAME`/`WO_PASSWORD` or key; `MODEL_OVERRIDE` with IFM); the rest undocumented |

Other `--type` values: `mcsp_v1`, `mcsp_v2`, `k8s`.

### Add and activate (never type the key in chat)

```bash
orchestrate env add --name <env> --url <instance url>                      # registers; no prompt
orchestrate env activate <env> --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
orchestrate env list                                                       # (active) marker
```

`--api-key` belongs to `env activate`, not `env add`. `env add --activate` prompts interactively (fine for humans, breaks scripts).

### Tokens

- SaaS tokens cached in `~/.cache/orchestrate/credentials.yaml` expire after about two hours; re-run `env activate`.
- The evaluation framework uses the **active environment's** cached token (*observed on 2.18:* `--env-file` changed neither the instance nor the token). For long runs export `WO_API_KEY` (from the key file) so it can refresh.
- Developer Edition tokens do not expire.
- Reuse before add: if `env list` already has the instance, activate it; do not create a second environment for the same URL.

---

## Capability × target (curated; ✓ validated or documented, ~ expected but not validated, ⚠ undocumented)

| Capability | SaaS IBM Cloud | SaaS AWS | Developer Edition | On-prem CPD |
|---|---|---|---|---|
| `quick-eval`, `evaluate`, `analyze` | ✓ validated | ✓ documented | ✓ documented | ✓ documented (`MODEL_OVERRIDE` with IFM) |
| `RubricEvaluation` | ✓ validated | ~ | ~ (judge model must be served locally) | ~ |
| `record` | ✓ documented (SaaS chat URL) | ✓ documented | ✓ documented (`orchestrate chat start`) | ~ |
| `generate` | needs Langfuse credentials on 2.18 (observed) | same | same (`-l` provides Langfuse) | ~ |
| `red-teaming plan` / `run` | ✓ validated (`run` with hand-authored attacks; `plan` works, review output) | ~ | ~ (planner model via local gateway) | ⚠ |
| Traces CLI / Python / REST | ✓ validated (admin identity) | ~ documented | ✓ with `-i` | ⚠ |
| `orchestrate controls` (Guardrails block) | ✓ when enabled on the instance | ~ | ~ | ⚠ |
| Langfuse integration (Cost Management block) | Trial / Essentials / Standard non-isolated; one setting per instance | AWS commercial | `-l` local stack | ⚠ |

Documented constraints: remote evaluations run only against **draft** environments; non-Dallas regions may need `MODEL_OVERRIDE` for model-proxy based features.

---

## Models the framework uses

| Role | Config | Default | Pick on DevEd |
|---|---|---|---|
| judge / matcher | `evaluation_config.provider_config.model_id` (provider `gateway`) | `bedrock/openai.gpt-oss-120b-1:0` | a model from `orchestrate models list` |
| simulated user | `llm_user_config.model_id` | `meta-llama/llama-3-3-70b-instruct` | same |
| red-team planner and attacker | the same provider configuration | same | same |

Provider auto-selection when nothing is configured: `USE_GATEWAY_MODEL_PROVIDER` defaults to `true` → `gateway` through the active environment; `watsonx` (direct watsonx.ai) if set to `false`, which needs `WATSONX_APIKEY` and `WATSONX_SPACE_ID`/`WATSONX_PROJECT_ID`.

---

## Shared instances (RULE 6)

- `orchestrate agents list` and `orchestrate tools list` before any import; compare names.
- Prefix every asset of a project (`<project>_<name>`) when the instance hosts other teams; keep `display_name` equal to `name`.
- Never update, delete, or re-import an asset you did not create; `agents import` of an existing name updates it in place.
- Instance-level settings (Langfuse integration, controls on shared assets) belong to the instance owner.
- Service IDs scoped to one instance are the right identity for automation and public demos.

---

## Developer Edition specifics

`.env` (pass with `-e` on every start; it is not remembered):

```
WO_DEVELOPER_EDITION_SOURCE=orchestrate
WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<id>
WO_API_KEY=<key for that instance>
# optional, to use watsonx.ai models through the local gateway:
# WATSONX_APIKEY=...
# WATSONX_SPACE_ID=...   (or WATSONX_PROJECT_ID)
```

Server flags that matter here: `-i` traces, `-l` Langfuse (mutually exclusive), `-d` document processing, `--with-langflow`, `--with-ai-builder`. First start pulls images (~10 min, ~16 GB RAM, ~50 GB disk).

Keep the server `.env` **outside** any folder you run evaluations from: the framework auto-loads the nearest `.env` walking up from the current directory and a cloud `WO_INSTANCE` there overrides the local target (symptom: `400 Bad Request` from `iam.cloud.ibm.com`). Check with `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`.

Lima VM stuck (`docker --context ibm-watsonx-orchestrate ps` → `EOF`): `orchestrate server stop`, `mv ~/.lima/ibm-watsonx-orchestrate ~/.lima/ibm-watsonx-orchestrate.bak-$(date +%F)`, start again (fresh VM, ~10 min). `orchestrate server purge` deletes everything including imported agents; only on explicit request.

---

## Pre-flight recap

| Check | Command | On failure |
|---|---|---|
| venv | `echo "VENV_ACTIVATE=${VENV_ACTIVATE:-UNSET}"` | ask once |
| versions | `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` | emit upgrade; stop |
| environment | `orchestrate env list` | emit `env activate` |
| assets | `orchestrate agents list`, `orchestrate tools list` | emit imports; check collisions |
| ancestor `.env` | `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"` | move aside / override inline |
| DevEd server | `lsof -ti :4321` | emit `server start -e .env [-i]` |
| DevEd Lima | `docker --context ibm-watsonx-orchestrate ps 2>&1 \| head -3` | recovery recipe above |
