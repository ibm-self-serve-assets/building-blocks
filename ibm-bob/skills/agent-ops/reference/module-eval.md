# Module: Eval

**TRIGGER:** Load when user wants to run `orchestrate evaluations quick-eval` or `evaluate`, asks about `--with-langfuse`, asks about config.yaml shape, asks about common eval failures (`session_id=None`, `400 Bad Request from iam.cloud.ibm.com`, `Scope not found`, `model_not_supported`, RAG judges 403/401), or asks for the canonical eval expected outputs.

---

## Two CLI commands

```
orchestrate evaluations quick-eval   # reference-less smoke / schema / hallucination check
orchestrate evaluations evaluate     # full reference-based benchmark eval
```

**This skill leads with the Langfuse-based judge path:** `evaluate --with-langfuse` + server started with `-l`. Persists traces (including judge observations with token usage) to Langfuse. Required for cost analysis (see `reference/module-observability.md`). The eval-fw >= 1.4.0 version floor sidesteps the eval-fw 1.2.x deprecated 405b judge crash entirely.

**Authoritative docs:**
- `evaluate`: https://developer.watson-orchestrate.ibm.com/evaluate/evaluate.md
- `quick-eval`: https://developer.watson-orchestrate.ibm.com/evaluate/quick_eval.md
- Overview / arg matching: https://developer.watson-orchestrate.ibm.com/evaluate/overview.md

---

## Inputs

- **Required:** target env from Q1.
- **Required:** agent imported into active env.
- **Required:** benchmark JSONs exist (OR run `quick-eval` first for a connectivity check).
- **Optional:** existing `config.yaml` in project root.
- **Optional:** `.env` (Bob pre-flights for ancestor pollution).

## Read-only diagnostics (strict order)

1. **ADK + eval-fw version floor (RULE 3):** `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` → fail action: emit upgrade command, do not proceed.
2. **Ancestor `.env` pollution:** `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"` → if outside project, warn and offer remediation from `reference/auth-env-matrix.md`.
3. **DevEd: server up:** `lsof -ti :4321` → fail action: emit `orchestrate server start -e .env [-l|-i]`.
4. **Active env matches Q1:** `orchestrate env list` → fail action: emit `orchestrate env activate <target>`.
5. **Agent imported:** `orchestrate agents list` → fail action: refuse — point to WXO import flow. Do NOT auto-import.
6. **`config.yaml` exists with explicit token:** read `./config.yaml`, confirm `auth_config.token` is non-empty → fail action: emit `evaluate_with_explicit_token` block from `reference/command-emission.md`.

---

## Emitted commands

### `quick_eval` (smoke test)
**Purpose:** reference-less smoke / connectivity / schema check. Runs 2 scenarios (or whatever user has) without ground-truth comparison. Detects schema mismatches and tool-call hallucinations.

```bash
# --tools-path is required for quick-eval (Python @tool functions).
# Output lands in quick_eval_results/<timestamp>/
source "$VENV_ACTIVATE" && \
orchestrate evaluations quick-eval \
  --test-paths benchmarks/ \
  --tools-path agent/tools \
  --output-dir quick_eval_results/$(date +%Y%m%d-%H%M%S) \
  --config ./config.yaml
```

### `evaluate_full` (RECOMMENDED default)
**Purpose:** reference-based benchmark eval. LLM simulates a user playing each scenario; framework compares actual goal completion against benchmark's expected goals. `--with-langfuse` persists traces (including judge observations with token usage) — required for cost computation per `reference/module-observability.md`.

**Prerequisites (confirm with user before emitting):**
1. Server started with `-l` (Langfuse on `:3010`).
2. `LANGFUSE_BASE_URL` / `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` exported in current shell.
3. `WATSONX_APIKEY` + (`WATSONX_PROJECT_ID` or `WATSONX_SPACE_ID`) exported, IF benchmarks contain `conversational_search` (RAG) goals. Without these, RAG judges (Faithfulness, Relevancy) will 403/401. Non-RAG scenarios run fine without watsonx auth.
4. `config.yaml` uses `provider: gateway` and `model_id` is a watsonx-supported model (e.g., `meta-llama/llama-3-3-70b-instruct`).

```bash
# --with-langfuse persists traces with token usage. Server must be started with `-l`,
# LANGFUSE_* exported. For RAG benchmarks, WATSONX_APIKEY + WATSONX_PROJECT_ID/SPACE_ID also needed.
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate \
  --test-paths benchmarks/ \
  --output-dir eval_results/$(date +%Y%m%d-%H%M%S) \
  --config ./config.yaml \
  --with-langfuse
```

### `evaluate_without_langfuse`
**Purpose:** when you don't need cost/latency analysis OR Langfuse isn't running. Faster setup, no token/cost data.

```bash
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate \
  --test-paths benchmarks/ \
  --output-dir eval_results/$(date +%Y%m%d-%H%M%S) \
  --config ./config.yaml
```

### `evaluate_single_scenario`
**Purpose:** run a single benchmark JSON — useful for iterating on one scenario after a fix.

```bash
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate \
  --test-paths benchmarks/<scenario.json> \
  --output-dir eval_results/$(date +%Y%m%d-%H%M%S)-single \
  --config ./config.yaml \
  --with-langfuse
```

---

## Flags reference (authoritative from `--help`, ADK 2.9.0)

**`orchestrate evaluations evaluate`:**
- `--config` / `-c` — path to YAML config
- `--test-paths` / `-p` — paths to test files or dirs (comma-separated)
- `--output-dir` / `-o` — dir to save results
- `--env-file` / `-e` — path to `.env` (overrides default.env)
- `--with-langfuse` / `-l` — enable Langfuse-based judge path + trace persistence

**NOT valid flags for `evaluate`** (these belong to `quick-eval` / `analyze`):
- `--tools-path` (only for `quick-eval` and `analyze`)

**Deprecated env var:** earlier drafts referenced `USE_LEGACY_EVAL=FALSE`. Superseded by `--with-langfuse` in ADK 2.1.0+; do not emit the env var.

---

## Expected outputs (in `<output_dir>/`)

| File | Purpose |
|---|---|
| `summary_metrics.csv` | Top-level metrics per scenario. **Start here.** Columns: Journey Success, Journey Completion, Tool Call Recall, Tool Call Precision, Agent Routing F1, Text Match, Avg Response Time. |
| `results.json` | Per-scenario detail with full conversation trace, tool calls, and goal evaluation. |
| `knowledge_base_summary_metrics.json` | Aggregated RAG metrics across scenarios with `conversational_search` goals: Faithfulness, Answer Relevancy, Response Confidence, Retrieval Confidence. Requires `WATSONX_APIKEY` + `WATSONX_PROJECT_ID`/`SPACE_ID` for judges to actually score. |
| `config.yaml` | Snapshot of config used for this run (read-only audit). |

---

## Interpretation handoff

Once user pastes the output path, Bob reads the result files with the Read tool (no need to ask user to `cat` them) and switches to `reference/module-analyze.md` for metric interpretation and failure diagnosis.

---

## Done-when criteria

- `summary_metrics.csv` exists at the output path.
- Bob has summarized headline metrics (Journey Success rate, Tool Call Recall, Avg Response Time) in 3-5 bullets.
- User has explicitly chosen next action: (a) iterate on failing scenario, (b) run `analyze` for deeper diagnosis, (c) move to red-teaming, (d) stop.

---

## Common failures

**SOURCE NOTE (RULE 9):** symptom→cause→fix mappings below are curated starting points drawn from real engagement experience; not WXO-published. The underlying error messages are real ADK output, but the diagnoses are interpretations — confirm against the trace and current eval-fw release notes before acting.

| Symptom | Cause | Fix |
|---|---|---|
| `session_id=None` in `results.json` | LLM-simulator infrastructure crash (non-deterministic). NOT an agent bug. | Re-run failing scenario(s). If persistent across 3 runs, check provider config + active env. |
| `400 Bad Request from iam.cloud.ibm.com/identity/token` | Ancestor `.env` pollution overriding `WO_INSTANCE` | Run `find_dotenv` check; move ancestor `.env` aside or pass overrides inline. |
| `RuntimeError: WO_API_KEY must be specified for SaaS or IBM IAM auth` | `auth_config.url` in `config.yaml` is a cloud URL, OR `WO_INSTANCE` env var leaking from ancestor `.env` | Confirm `config.yaml.auth_config.url` matches active env URL. Re-run `find_dotenv` pre-flight. |
| `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}` | Active env's instance UUID doesn't match API key. Common with multiple SaaS instances. | Ask user which instance their key belongs to. Activate matching env, or `env add` new one with correct URL. |
| `model_not_supported` / 404 on judge model from watsonx | `model_id` in `config.yaml` isn't supported by your watsonx project/space | Set `model_id: meta-llama/llama-3-3-70b-instruct` (commonly available). If still 404, list supported models in watsonx.ai console. |
| RAG judges 403/401: 'invalid bedrock API key' or 'groq error: Invalid API Key' | Local DevEd gateway has no Bedrock/Groq creds. Default judge `bedrock/openai.gpt-oss-120b-1:0` (eval-fw 1.4.x) and override `groq/openai/gpt-oss-120b` both fail without those providers' keys. | Use `provider: gateway` in `config.yaml` with `model_id: meta-llama/llama-3-3-70b-instruct` AND export `WATSONX_APIKEY` + `WATSONX_PROJECT_ID` (or `WATSONX_SPACE_ID` if WML-bound). Gateway routes the model through watsonx.ai using these creds. See `reference/auth-env-matrix.md`. |
| `space_id ... is not associated with a WML instance` | Watsonx space exists but isn't bound to a Machine Learning service | Either bind in IBM Cloud → Resource list → WML service → Manage → Add to space, OR switch to `WATSONX_PROJECT_ID`, OR use a WML-bound space ID. |
| `apikey must be specified` on `provider: watsonx` (not gateway) | Switched to `provider: watsonx` directly without exporting `WATSONX_APIKEY` | Export `WATSONX_APIKEY`. Note: `provider: gateway` is preferred over `provider: watsonx` direct (better caching, same env vars). |
| `KeyError: '<uuid>'` raised by eval-fw before any benchmark runs (during simulator setup or agent-context loading) | Tenant has **orphaned tool references**: agents that reference tool IDs no longer in the tenant. A diagnostic signal is many `[WARNING] - Tool with ID '<uuid>' not found. Returning Tool ID` lines during `orchestrate agents list`. The eval framework loads tenant context at startup and can crash on the dead reference. Long-lived SaaS tenants accumulate these over time. | Clean up the orphaned references via `orchestrate tools remove <id-or-name>` and `orchestrate agents update` (remove dead tool refs from the agent specs). For partner demos, use a fresh/clean SaaS tenant or DevEd. If cleanup isn't feasible, `quick-eval` may still work since it doesn't load the full agent context — use it for at least connectivity/schema validation. |
