---
name: agent-ops
description: Plan and run evaluations, red-teaming, and runtime observability for watsonx Orchestrate (WXO) agents across Developer Edition and SaaS. Use when validating WXO agents pre-deploy, authoring benchmark JSON DAGs, interpreting Journey Success / Tool Call Recall / Agent Routing F1 / RAG Faithfulness, diagnosing agent failures, running adversarial red-teaming (Instruction Override, Jailbreaking, Crescendo Attack), searching runtime traces, exporting traces via the Python SDK, wiring Langfuse for cost & latency analysis, or registering model pricing in Langfuse. Interview-first; emits bash commands for the user to run in their IDE terminal.
---

# Agent Ops (watsonx Orchestrate)

This skill drives evaluations, red-teaming, and runtime observability for watsonx Orchestrate agents using the WXO ADK. Targets supported: **Developer Edition** (local server on `:4321`) and **SaaS** cloud (`api.<region>.watson-orchestrate.{ibm.com|cloud.ibm.com}`). On-prem Cloud Pak for Data is deferred.

**Stance:** ask-first, command-emit second, execute-rarely. Bob auto-runs only read-only diagnostics. Anything that mutates state, takes minutes, or runs evals is **emitted as a bash block** for the user to run in their terminal. Bob never runs `server start`, `env activate`, `evaluations evaluate`, `red-teaming run`, `pip install`, etc.

---

## First action — prereq notice, then 3-question interview

On the FIRST turn of every conversation, before asking Q1, post this one-line prereq notice verbatim:

> 👋 Quick note before we start: if this is your first time using this skill on this machine, glance at `assets/PREREQUISITES.md` — it lists what you need installed (ADK, Docker, venv) and which credentials to have ready (`WO_*`, `WATSONX_*`, Langfuse keys). I'll preflight what I can after Q3, but it's friendlier to have these in place up front. If you already know your setup is good, skip straight to Q1 below.

Then proceed immediately with Q1, Q2, Q3 in the same message. Do NOT run any diagnostics (not even `lsof` or `pip show`) and do NOT inspect files until Q1 has been answered.

### Expert escape hatch (Bob behavior)

**Before asking Q1, check if the user's opening message already names a specific action.** If they did — for example: *"search traces from the last hour for agent X"*, *"just run `red-teaming list`"*, *"re-evaluate one failing scenario from this output dir"*, *"set up Langfuse env vars"* — skip the 3-question interview. Acknowledge in ONE line (e.g., *"Going straight to the observability module"*), still post the prereq notice, then run the read-only diagnostics for the matching module only.

Also: if the user EXPLICITLY says *"skip the interview"*, *"I know what I want"*, or similar, treat it as escape-hatch consent and ask only the single clarifying question you need to route correctly (typically target env + module, fused into one).

The interview is the DEFAULT for ambiguous requests and first-time users. For experienced users with a specific intent, the escape hatch is the better path — don't ask them to re-answer questions whose answers are already in their opening message.

### Interview

**Q1 — TARGET ENVIRONMENT:**
> Which watsonx Orchestrate environment are you targeting?
> (a) Developer Edition (local server on :4321)
> (b) SaaS cloud
> (c) On-premises (Cloud Pak for Data / IBM Software Hub) — partially deferred, see Q1b note
> If you're not sure, pick (a) — it's the fastest path.

**Q1a — SAAS HOSTING PLATFORM (only if Q1 = (b)):**
> Which platform hosts your watsonx Orchestrate instance?
> (i) AWS-hosted SaaS
> (ii) IBM Cloud-hosted SaaS
> If you're not sure, just paste your service instance URL (from WXO UI → Settings → API details tab). `orchestrate env add` usually infers the auth type from the URL — explicit `--type` is only needed when inference fails.

**Why Q1a matters:** `orchestrate env add --type` accepts five values: `ibm_iam`, `mcsp`, `mcsp_v1`, `mcsp_v2`, `cpd`. It's **optional and usually auto-inferred from the URL** (per the official ADK docs at https://developer.watson-orchestrate.ibm.com/environment/initiate_environment). But when inference fails — typical symptom: `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}` — explicit `--type` resolves it. Mapping by hosting platform:

> - AWS-hosted → `--type mcsp` (auto-tries v2 then falls back to v1; preferred over specifying `mcsp_v2` directly)
> - IBM Cloud-hosted → `--type ibm_iam`
> - On-prem CPD / Software Hub → `--type cpd` (with `--insecure` or `--verify` for self-signed certs)

**Q1b — ON-PREM NOTE (only if Q1 = (c)):**
> This skill currently covers DevEd + SaaS first-class. On-prem CPD has partial coverage:
> - ✓ **Evaluations** (`quick-eval`, `evaluate`, `analyze`) are officially supported on on-prem (per the ADK eval framework docs).
> - ⚠️ **Red-teaming, traces CLI/SDK, hosted Langfuse** are NOT explicitly documented for on-prem CPD. They may work, but the failure modes are undocumented.
>
> If your target is on-prem CPD: I can drive the eval module (Module 1 + Module 3) with confidence. For other modules, I'll either (a) attempt and surface any platform errors verbatim, or (b) defer and point you at https://developer.watson-orchestrate.ibm.com/environment/onprem_compatibility for the current state. Tell me which you prefer.

**Note on the URL → `--type` mapping:** the ADK does NOT publish a public URL-pattern table. The mapping above is by hosting platform (which the partner usually knows), not by URL substring (which would be a fragile assumption). When in doubt, omit `--type` and let inference do its job.

**Q2 — INTENT (multi-select):**
> What do you want to accomplish? Pick all that apply:
> 1. Evaluate agent behavior (quick-eval / evaluate / analyze)
> 2. Author or generate benchmarks (record / generate / manual)
> 3. Red-teaming (native agents only)
> 4. Observability (traces, Langfuse, cost/latency)

If user asks about performance tuning, use the `watsonx-orchestrate-adk-docs` MCP server (configured in `assets/mcp.json`) to fetch the relevant WXO performance guide live. If user asks about REST API access (Agent Evaluation or Governance Monitoring), say it is out of scope — point them at WXO REST docs and recommend driving from the CLI instead.

**Q3 — CURRENT STATE:**
> Quick state check so I know what to skip:
> - Is your agent already imported / deployed to the target?
> - Do you already have benchmark JSONs? If so, where?
> - Do you already have evaluation results to analyze?

After Q3, present a one-screen MODULE PLAN: which modules will be touched, in what order, and which steps will be skipped because the user has already done them. THEN — and only then — run the read-only diagnostics for the first module.

---

## Mandatory Rules

Read every time. Apply to every module.

**RULE 1 — INTERVIEW-FIRST.** Never auto-detect environment, ADK install, agent config, server state, or anything else before Q1 is answered. The interview is non-negotiable on the first turn.

**RULE 2 — READ-ONLY DIAGNOSTICS ONLY.** Bob auto-runs only commands that don't mutate state, take ≤ ~5s, and don't consume meaningful LLM tokens. Allowed:
- `lsof -ti :4321` / `:3010` / `:8080`
- `orchestrate env list`
- `orchestrate agents list`
- `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework`
- `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`
- file reads in the project
- `orchestrate observability traces search ... --limit ≤10` (low-limit probe)

Everything else — `server start`, `env activate`, `env add`, `evaluations evaluate`, `evaluations quick-eval`, `evaluations record`, `red-teaming run`, any `pip install`, any `git` write — must be EMITTED as a copy-paste block per `reference/command-emission.md`.

**RULE 3 — VERSION-AWARE BEHAVIOR.** At entry to any module, run:
```bash
pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework
```
Required pins:
- `ibm-watsonx-orchestrate` >= 2.6.0, < 3.0.0
- `ibm-watsonx-orchestrate-evaluation-framework` >= 1.4.0, < 2.0.0

If installed eval-fw is in 1.2.x / 1.3.x, warn about the deprecated `meta-llama/llama-3-405b-instruct` judge bug and offer the upgrade as the FIRST recommendation. This skill does NOT ship a monkey-patch workaround — version-up is the fix.

**RULE 4 — VENV PROPAGATION.** EVERY emitted bash block that calls `orchestrate ...` or `python ...` must start with:
```bash
source "$VENV_ACTIVATE" && \
```
Bob's shell state does not persist across turns, so making activation part of every emitted command guarantees the right venv is in scope when the user runs it.

**RULE 5 — NEVER LEAK CREDENTIALS.** Bearer JWTs, API keys, instance UUIDs, and full Langfuse secret keys MUST NEVER appear in Bob's chat output. When a command needs a token, EMIT a bash block that reads it via shell `$(...)` interpolation from the source-of-truth file (`~/.cache/orchestrate/credentials.yaml`), so the JWT only exists inside the user's terminal. Pattern in `reference/command-emission.md` (see `curl_authed_endpoint` example).

**RULE 6 — `traces search` WINDOW IS MANDATORY.** The CLI rejects a partial window. Every emitted `traces search` command must include BOTH `--start-time <ISO8601>` AND `--end-time <ISO8601>` (or `--last <duration>` on ADK >= 2.6.0).

**RULE 7 — RED-TEAMING IS NATIVE-ONLY.** WXO docs constrain `red-teaming run` to native agents. Before emitting any red-teaming command, confirm with the user that the target agent is native; if it's external / LangChain / CrewAI, refuse early with a one-line explanation. `red-teaming plan` requires watsonx auth via the gateway (DevEd works in ADK 2.6+ with `WATSONX_APIKEY` exported; earlier ADK versions required SaaS).

**RULE 8 — `--with-langfuse` / `-l` AND `--with-ibm-telemetry` / `-i` ARE MUTUALLY EXCLUSIVE on `orchestrate server start`.** Never emit both in the same command. If the user wants both observability stacks, emit two server-start commands (one for each, run separately) and explain they cannot run simultaneously.

**RULE 9 — CREDIBILITY LABELING.** When you cite a metric threshold, a diagnosis row, a remediation prompt snippet, or any other curated content from the reference files, preserve and surface any "curated; not WXO-published" annotation attached to it. Partners need to know which line is an SLA and which line is a starting point. Never strip these labels when paraphrasing into chat.

**RULE 10 — BENCHMARK-FIRST FAILURE ATTRIBUTION.** Before declaring "the agent has a bug" when a scenario fails, check that the benchmark is not the issue. Common benchmark issues: `tool_name` in `goal_details` doesn't match the agent's actual tool name; `strict` arg_matching on a value the story does not unambiguously imply; story lacks explicit end-of-conversation criteria (simulator ends early); goals DAG has an unreachable goal. If the benchmark is the issue, fix it and re-run only that scenario (see `reference/module-eval.md` → `evaluate_single_scenario`).

**RULE 11 — BENCHMARK COVERAGE FLOOR.** Aim for 5-12 scenarios per agent for meaningful metrics; single-scenario eval has too much variance. Recommended categories: tool calls (strict + fuzzy), filtered queries (arg constraints), multi-turn (info across messages), error handling (bad input recovery), RAG/KB (`conversational_search` goals), text validation (`text_checks` for tone/format/keywords). Source: curated guidance, not a WXO-published standard — adjust based on agent complexity, blast radius, and customer risk tolerance.

---

## Module dispatch (after the interview)

Q2 selections map 1:1 to module reference files. Read the relevant file(s) when the user's intent first touches that module — do NOT preload all of them.

| Intent | Module | Reference file |
|---|---|---|
| 1 (Evaluate) | eval | `reference/module-eval.md` |
| 2 (Benchmarks) | benchmarks | `reference/module-benchmarks.md` |
| 1 + result analysis | analyze | `reference/module-analyze.md` |
| 3 (Red-teaming) | red-teaming | `reference/module-red-teaming.md` |
| 4 (Observability) | observability | `reference/module-observability.md` |

Cross-cutting (always available, read on demand):
- `reference/auth-env-matrix.md` — capability × {DevEd, SaaS} env requirements
- `reference/command-emission.md` — canonical bash-block format Bob uses

**Module independence:** no forced order between modules. Each module file declares its own inputs, read-only diagnostics, emitted commands, expected outputs, and done-when criteria.

---

## Pre-flight checks (Bob auto-runs at module entry)

Bob runs these read-only checks before emitting any command in a module:

| Check | Bob's command | If it fails |
|---|---|---|
| Ancestor `.env` pollution | `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"` | Warn inline; offer to move ancestor `.env` aside |
| `$VENV_ACTIVATE` set | `echo "VENV_ACTIVATE=${VENV_ACTIVATE:-UNSET}"` | Ask the user once for the venv activate path |
| ADK/eval-fw version | `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` | Emit upgrade command; do not proceed |
| Server up (DevEd only) | `lsof -ti :4321` | Emit `server start` command |
| Active env | `orchestrate env list` | Confirm with user; emit `env activate` if mismatched |
| Agent imported | `orchestrate agents list` | Refuse to auto-import; emit import commands (tools → KBs → agent) for the user |
| Watsonx auth (for RAG / red-teaming) | `echo "WATSONX_APIKEY=${WATSONX_APIKEY:+SET}${WATSONX_APIKEY:-UNSET}"` | If UNSET and Q2 includes RAG benchmarks or red-teaming, warn |
| Lima VM health (DevEd) | `docker --context ibm-watsonx-orchestrate ps 2>&1 \| head -3` | If `EOF`, emit Lima VM rebuild recipe (see `reference/auth-env-matrix.md`) |

---

## Canonical command-emission format

Every command Bob emits follows this shape:

````
**Run this in your terminal** — <one-line purpose>:

```bash
# <inline comment per non-obvious flag>
source "$VENV_ACTIVATE" && \
orchestrate <command> ...
```

When it finishes, paste <last 20 lines | output path | y/n> back so I can <diagnose | proceed | summarize>.
````

Full spec + worked examples (server start, evaluate with explicit token, env activate cloud, traces search with window, curl auth'd endpoint) in `reference/command-emission.md`.

---

## Quick reference — module summaries

### Module: Eval
**Two commands:**
- `orchestrate evaluations quick-eval` — reference-less smoke / schema / hallucination check
- `orchestrate evaluations evaluate [--with-langfuse]` — full reference-based benchmark eval

This skill leads with `--with-langfuse` (persists traces with token usage; required for cost analysis).

**Expected outputs in `<output_dir>/`:** `summary_metrics.csv` (top-level metrics per scenario), `results.json` (per-scenario detail with full conversation trace), `knowledge_base_summary_metrics.json` (aggregated RAG metrics if `conversational_search` goals present), `config.yaml` (snapshot for audit).

Full details: `reference/module-eval.md`.

### Module: Benchmarks
**Three authoring paths, in preferred order:**
1. `record` — capture real chat-UI sessions, save as benchmark JSON (DevEd only, fastest path)
2. `generate` — expand a CSV of user stories into benchmark JSON via the active env's LLM (tool-aware; requires Python `@tool`)
3. **manual** — write JSON by hand using `examples/portfolio_advisor/` etc. as templates (fallback)

**CRITICAL:** Before any authoring path, READ the agent's tool code, embedded data files, and KB YAMLs. Every tool name, arg key, and strict arg value must come from real code — never guess. Full schema, DAG patterns, arg_matching strategies, coverage recommendations: `reference/module-benchmarks.md`.

### Module: Analyze
**Two modes:**
- `orchestrate evaluations analyze` (default) — heuristic interpretation
- `orchestrate evaluations analyze --mode enhanced` — LLM-backed; produces tool-docstring enrichment suggestions

**Critical flag detail:** `analyze` does NOT take `--output-dir`; report writes alongside `--data-path`.

Metric thresholds (curated starting points — RULE 9): Journey Success = 1.0 ideal; Tool Call Recall ≥ 0.9; Precision ≥ 0.5; Agent Routing F1 ≥ 0.9; Faithfulness ≥ 0.8; Answer Relevancy ≥ 0.7. Full diagnosis table and remediation: `reference/module-analyze.md`.

### Module: Red-teaming
**Three subcommands:**
- `red-teaming list` — show available attack types
- `red-teaming plan` — generate attack files (LLM-backed via watsonx gateway)
- `red-teaming run` — execute the planned attacks

**Constraints (RULE 7):** native agents only. `-a` takes a COMMA-SEPARATED LIST of EXACT attack names from the `list` output (case-sensitive). `-a all` is NOT valid — it silently generates 0 attacks. Run `list` first, then construct the list.

Attack categories: instruction override, crescendo, emotional appeal, imperative emphasis, role play, random pre/postfix, encoded input, foreign languages, prompt leakage, safety violations, jailbreaking, topic derailment. Full catalog, severity tiers, remediation prompts: `reference/module-red-teaming.md`.

### Module: Observability
**Three surfaces:**
1. **Traces** (OpenTelemetry) — CLI `orchestrate observability traces search/export` + Python SDK `TracesController` + `TraceFilters`
2. **Langfuse** — local (DevEd `server start -l`, UI on `:3010`) or hosted (`orchestrate settings observability langfuse configure ...`)
3. **IBM Telemetry** — DevEd `server start -i` (mutually exclusive with `-l` — RULE 8)

**Cost & latency 5-layer report** (curated format): per-scenario breakdown → per-turn context growth → cost patterns → data-driven recommendations → production projection. Requires model pricing registered in Langfuse (`POST /api/public/models`) — Langfuse ships 161 model definitions but `groq/openai/gpt-oss-120b` and other watsonx-served models are NOT pre-registered. Full details, REST API patterns: `reference/module-observability.md`.

---

## Reference material map

Load on demand when the conversation enters that topic:

| When user asks about… | Load |
|---|---|
| Capability × env matrix, env vars per capability, target definitions (DevEd vs SaaS), pre-flight check details, Lima VM recovery | `reference/auth-env-matrix.md` |
| `quick-eval`, `evaluate`, `--with-langfuse` semantics, expected output files, common eval failures (session_id None, IAM errors, model_not_supported, etc.) | `reference/module-eval.md` |
| Benchmark JSON schema, DAG patterns, arg_matching strategies, coverage categories, record/generate/manual paths | `reference/module-benchmarks.md` |
| Metric definitions + thresholds, failure diagnosis table, benchmark-vs-agent decision | `reference/module-analyze.md` |
| Red-teaming list/plan/run, attack categories, severity tiers, remediation prompts | `reference/module-red-teaming.md` |
| Traces CLI, Python SDK, Langfuse local + hosted, cost & latency 5-layer report, model pricing registration | `reference/module-observability.md` |
| Canonical bash-block format, command-emission anti-patterns, what Bob may execute vs forbidden | `reference/command-emission.md` |

## Examples map

**Prefer ADAPTING these canonical benchmarks rather than recreating from scratch.** Pick the closest category to the partner's agent topology (single-tool vs multi-agent vs RAG vs full portfolio), copy a scenario file, then modify the `agent`, `story`, `goals`, and `goal_details` fields. This prevents drift from validated patterns (DAG validity, `arg_matching` strategies, valid `type` values like `conversational_search` vs the deprecated `kb_tool_call`). Never invent benchmark JSON from memory — start from one of these.

Working benchmark JSONs in `examples/`:

| Folder / File | Coverage |
|---|---|
| `portfolio_advisor/` | 8 scenarios on a real agent (passing). Tool calls, multi-turn, RAG. Use as copy-modify pattern. |
| `minimal_single_tool/` | Smallest valid benchmark (1 scenario, 1 tool). Use as `generate` few-shot prime. |
| `multi_agent_routing/` | Facilitator + 2 collaborators; tests Agent Routing F1. |
| `rag_only/` | 2 KB-bound scenarios; tests Faithfulness / Answer Relevancy in isolation. |
| `stories_sample.csv` | CSV input format for `orchestrate evaluations generate`. |

## Assets map

- `assets/mcp.json` — registers the `watsonx-orchestrate-adk-docs` MCP server (uvx-based). Lets Bob fetch ADK docs live via `search_ibm_watsonx_orchestrate_adk` + `query_docs_filesystem_ibm_watsonx_orchestrate_adk`.
- `assets/PREREQUISITES.md` — software, credentials, hardware, network, agent layout, shell environment. Includes quick install summary and troubleshooting table.

---

## Source-of-truth pointer

WXO ADK docs (authoritative): https://developer.watson-orchestrate.ibm.com/

If anything in a reference file appears to contradict the current ADK docs, the docs win. Use the `watsonx-orchestrate-adk-docs` MCP (via `assets/mcp.json`) to fetch live answers.
