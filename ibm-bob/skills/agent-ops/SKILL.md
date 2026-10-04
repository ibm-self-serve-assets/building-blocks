---
name: agent-ops
description: Evaluate, red-team, and observe watsonx Orchestrate (WXO) agents with the ADK evaluation framework (ADK 2.18+, evaluation framework 1.5+) on SaaS or Developer Edition. Use when validating a WXO agent before release or after a change, authoring ground-truth test cases (goal DAGs, handoff goals, arg_matching), running quick-eval / evaluate / analyze, scoring conversations against plain-language rubrics (RubricEvaluation), running red-teaming attacks, interpreting Journey Success / routing accuracy / tool-call precision and recall, deciding whether a failure is the agent, the test case, or the model, or searching and exporting platform traces. Interview-first; emits the commands for the user to run. Runtime policy enforcement belongs to the agent-controls and real-time-guardrails skills; tokens-to-dollars, Langfuse, and cost optimization belong to the cost-management skill.
---

# Agent Ops (watsonx Orchestrate)

This skill drives **build-time evaluation, rubric scoring, red-teaming, and trace inspection** for watsonx Orchestrate agents with the ADK evaluation framework (`orchestrate evaluations ...`, `orchestrate observability traces ...`). Targets: **SaaS** (IBM Cloud or AWS hosted) and **Developer Edition** (local server). On-prem Cloud Pak for Data: evaluations are documented; the rest is best effort.

**Stance:** ask first, emit commands second, execute rarely. Bob auto-runs only fast, read-only diagnostics. Anything that mutates state, runs an LLM, or takes minutes is **emitted as a bash block** for the user to run in their terminal.

**Validated against:** `ibm-watsonx-orchestrate[agentops]` 2.18.0 with evaluation framework 1.5.2, on an IBM Cloud SaaS instance, with the multi-agent loan-underwriting system in `examples/loan_underwriting/`. Statements marked *observed* come from those runs; the ADK docs win if they disagree.

---

## First action — one-line prereq notice, then a 3-question interview

Post this once, verbatim, on the first turn:

> Before we start: this skill needs the ADK with the `[agentops]` extra (2.18 or newer) in a Python 3.12 venv, and an activated `orchestrate` environment pointing at the instance where your agent is imported. `assets/PREREQUISITES.md` has the details. If your setup is ready, answer the three questions below.

### Expert escape hatch

If the opening message already names a concrete action (*"run quick-eval on `benchmarks/`"*, *"why is precision 0.56"*, *"export trace abc123"*, *"write a rubric for refund policy"*), skip the interview, say which module you are entering in one line, and run only that module's read-only diagnostics. Ask a single fused question only if routing is genuinely ambiguous.

### Interview

**Q1 — Target environment**
> Which environment is the agent imported in?
> (a) SaaS on IBM Cloud (`api.<region>.watson-orchestrate.cloud.ibm.com`)
> (b) SaaS on AWS (`api.<region>.watson-orchestrate.ibm.com`)
> (c) Developer Edition (local server, `orchestrate server start`)
> (d) On-premises (Cloud Pak for Data / Software Hub)
> Paste the instance URL if unsure; `orchestrate env add` infers the auth type from it.

**Q2 — Intent (multi-select)**
> 1. Smoke test or evaluate agent behaviour (`quick-eval`, `evaluate`, `analyze`)
> 2. Author or generate test cases (`record`, `generate`, hand-written JSON)
> 3. Score conversations against plain-language rules (`RubricEvaluation`)
> 4. Red-teaming (native agents only)
> 5. Traces (search, export, latency, token usage per run)

If the user asks for **runtime controls** (PII filter, content guardrails, rate limits, model fallback), route to the `agent-controls` skill. For **cost** (tokens to dollars, Langfuse, optimization), route to the `cost-management` skill. For **LangGraph/LangChain agents**, route to the `build-time-gen-ai-evals` skill.

**Q3 — Current state**
> - Is the agent (and every collaborator and tool) already imported in that environment? Under which names?
> - Do test cases exist? Where?
> - Do you have evaluation results to look at already?
> - Is the instance shared with other teams' agents?

After Q3, present a one-screen **module plan** (modules, order, skipped steps), then run the pre-flight checks for the first module.

---

## Mandatory rules

**RULE 1 — Interview first.** No diagnostics, file reads, or `orchestrate` calls before Q1 is answered (escape hatch excepted).

**RULE 2 — Read-only diagnostics only.** Bob may auto-run: `orchestrate env list`, `orchestrate agents list`, `orchestrate tools list`, `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework`, `lsof -ti :4321` (DevEd), `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`, file reads inside the project, and `orchestrate observability traces search --last 1h --limit 5`. Everything else — `env add/activate`, `server start`, imports, `evaluations *`, `red-teaming *`, `pip install`, git writes — is emitted per `reference/command-emission.md`.

**RULE 3 — Version floor.** At module entry run `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework`. Required: ADK `>= 2.18.0, < 3.0.0` and framework `>= 1.5.0, < 2.0.0`. Below the floor, emit the upgrade and stop; the field notes in this skill do not apply to older versions.

**RULE 4 — Venv propagation.** Every emitted block that calls `orchestrate` or `python` starts with `source "$VENV_ACTIVATE" && \`.

**RULE 5 — Never leak credentials.** API keys, bearer tokens, Langfuse keys, and instance IDs never appear in chat. Keys live in a file the user controls (for example `~/.wxo-key.json`, mode 600) and are read with `$(...)` inside the emitted command. The `orchestrate` token cache is `~/.cache/orchestrate/credentials.yaml`; never print it.

**RULE 6 — Shared-instance hygiene.** Many instances host other teams' agents. Before any import: `orchestrate agents list` and `orchestrate tools list`, and confirm the user's names do not collide (prefix them if in doubt). Never update, delete, or re-import an asset the user did not create. Never change instance-level settings (the Langfuse integration is one setting per instance; configuring it overwrites whoever set it).

**RULE 7 — Red-teaming is native-only.** Confirm the target is a native agent (`kind: native`). External, LangChain, CrewAI, or A2A agents: say so in one line and stop.

**RULE 8 — Traces need a window.** Emit `--last <duration>` or both `--start-time` and `--end-time`. *Observed on SaaS:* the platform rejects windows longer than 4 hours and limits lookups to a few per minute; search in slices.

**RULE 9 — DevEd flags.** `--with-langfuse`/`-l` and `--with-ibm-telemetry`/`-i` on `orchestrate server start` are mutually exclusive. Traces on DevEd need `-i`.

**RULE 10 — Credibility labelling.** Metric thresholds, diagnosis rows, and remediation prompts in this skill are curated starting points, not WXO-published SLAs. Keep the "curated" label when you paraphrase them.

**RULE 11 — Test case first, then agent, then model.** When a case fails, check the test case (wrong tool name, strict match on a value the story never states, missing handoff goal, no end-of-conversation signal), then the agent (instructions, style, tool ownership), then the model (tool-calling reliability). Say which it was.

**RULE 12 — Coverage floor.** Aim for 5–12 test cases per agent: happy path, every decision branch, a multi-turn case, bad input, a RAG case if there is a knowledge base, a text check on the final answer. Single-case evaluations are too noisy to act on.

---

## Module dispatch

| Intent | Module | Reference file |
|---|---|---|
| 1 run / smoke test | eval | `reference/module-eval.md` |
| 2 test cases | benchmarks | `reference/module-benchmarks.md` |
| 1 + results | analyze | `reference/module-analyze.md` |
| 3 rubric | rubric | `reference/module-rubric.md` |
| 4 red-teaming | red-teaming | `reference/module-red-teaming.md` |
| 5 traces | observability | `reference/module-observability.md` |

Cross-cutting, read on demand: `reference/auth-env-matrix.md` (targets, auth, capability matrix, pre-flight details) and `reference/command-emission.md` (block format, what Bob may run).

Modules are independent; there is no forced order. The usual sequence for a new agent is quick-eval → test cases → evaluate → analyze → rubric → red-teaming, with traces whenever a conversation needs to be explained.

---

## Pre-flight checks (read-only, at module entry)

| Check | Command | If it fails |
|---|---|---|
| `$VENV_ACTIVATE` set | `echo "VENV_ACTIVATE=${VENV_ACTIVATE:-UNSET}"` | Ask once for the venv activate path |
| Versions (RULE 3) | `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` | Emit upgrade; stop |
| Active environment | `orchestrate env list` | Emit `env activate <name>`; for SaaS the cached token expires after about two hours — re-activate with `--api-key "$(...)"` |
| Agent and tools imported | `orchestrate agents list`, `orchestrate tools list` | Emit import commands (tools → knowledge bases → collaborators → orchestrator); never auto-import |
| Ancestor `.env` | `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"` | A `.env` outside the project is auto-loaded by the framework; move it aside or override inline |
| DevEd server up | `lsof -ti :4321` | Emit `orchestrate server start -e .env [-i]` |
| Shared instance (RULE 6) | compare the user's names with the two lists | Prefix, or stop and ask |

---

## Canonical command format

````
**Run this in your terminal** — <one-line purpose>:

```bash
# <inline comment per non-obvious flag>
source "$VENV_ACTIVATE" && \
orchestrate <command> ...
```

When it finishes, paste <the last 20 lines | the output path | y/n> so I can <diagnose | proceed | summarize>.
````

---

## Quick reference

### Eval
- `orchestrate evaluations quick-eval -c config.yaml` (or `-p <tests> -t <tools> -o <out>`): reference-less smoke test; reports tool calls, schema mismatches, hallucinated tools. Python tools only.
- `orchestrate evaluations evaluate -c config.yaml`: simulated user plays each test case; metrics in `summary_metrics.csv`, per-case transcripts in `messages/`.
- Runs against the **active environment**; the judge and simulated user are separate LLMs chosen in the config. Details, config shape, timings, and failure table: `reference/module-eval.md`.

### Test cases
- Schema: `agent`, `story`, `starting_sentence`, `goals` (DAG), `goal_details` (`tool_call`, `text`, `tool_response`, `conversational_search`), optional `max_user_turns`.
- `arg_matching`: `strict` (default), `fuzzy`, `optional`, `ignore`; `{"IGNORE": null}` skips all arguments; dot paths for nested fields.
- Multi-agent: declare handoffs as `chat_with_collaborator_<agent>` goals with arguments ignored; set each agent's `display_name` equal to its `name`. Full guidance: `reference/module-benchmarks.md`.
- Authoring paths: `record` (chat UI on SaaS or DevEd), `generate` (stories CSV + Python tools), or a generator script like `examples/loan_underwriting/make_testcases.py`.

### Analyze
- `orchestrate evaluations analyze -d <run dir> [-t <tools>] [--mode enhanced]`; the report prints to the terminal (widen it) and reads `summary_metrics.csv` plus `messages/*.metrics.json`.
- Curated thresholds: Journey Success 1.0, routing accuracy ≥ 0.9, recall ≥ 0.9, precision ≥ 0.8 once handoffs are declared as goals. Diagnosis table: `reference/module-analyze.md`.

### Rubric
- `metrics: [RubricEvaluation]` plus `operator_configs.RubricEvaluation.custom_criteria`: a named rule in plain language per criterion; the judge returns pass/fail with reasoning and an overall score. `reference/module-rubric.md`.

### Red-teaming
- `red-teaming list` (15 attacks in 2 categories), `plan` (LLM-generated attack files from your test cases), `run` (executes, scores with `AttackSuccessMetric`).
- Review or hand-author the generated attack files: the goal in the file defines what "the attack succeeded" means. `reference/module-red-teaming.md`.

### Observability
- `orchestrate observability traces search --last 1h` then `traces export --trace-id <id> -o trace.json`; Python `TracesController`; REST `GET /v1/agentops-v3/traces|observations`. Each observation carries `model` and `usage` (tokens). watsonx Orchestrate Agentic Control Plane dashboards in the product UI. `reference/module-observability.md`.

---

## Field notes — ADK 2.18 / framework 1.5 (observed; re-check on upgrade)

1. **Handoffs are tool calls.** A collaborator handoff shows up as `chat_with_collaborator_<agent>`. If it is not in `goal_details`, precision drops and the run looks worse than it is. Declare it with arguments ignored.
2. **`display_name` must equal `name`** for a handoff to count as routing; otherwise routing accuracy reads 0.0 while everything else passes.
3. **Argument checking stops at the first `fuzzy` field.** Put strict arguments before fuzzy ones in `args`, or a wrong strict value after a fuzzy one goes unnoticed.
4. **The simulated user keeps talking.** Default `max_user_turns` is 20; it will chat after the task is done. Set `max_user_turns: 3` (per case or in the config) and end the story with "reply END and nothing else".
5. **Token handling.** The framework uses the active environment's cached token; `--env-file` changes neither the instance nor the token in our runs. Export `WO_API_KEY` (from a key file, never typed in chat) so the framework can refresh a token that is about to expire during a long run.
6. **`analyze` and `text_match`.** Framework 1.5.2 writes `text_match` as a number in `*.metrics.json` while `analyze` validates it as the enum string; if `analyze` raises a validation error, normalize a copy of the run folder (recipe in `reference/module-analyze.md`).
7. **`quick-eval` on multi-agent systems** reports handoffs as schema mismatches. Read the per-tool lines; a mismatch on `chat_with_collaborator_*` is noise.
8. **Generated red-team plans need review.** `plan` produced goals that did not express the policy under test; hand-authored attack files with an explicit success goal gave trustworthy results.
9. **Model matters more than prompts.** In the loan example `watsonx/openai/gpt-oss-120b` called tools reliably; `granite-4-h-small` returned parse-failure fallbacks and `llama-3-3-70b-instruct` narrated calls instead of making them. Switch models before rewriting instructions.
10. **Orchestrator style.** `style: planner` with the final tool owned by the orchestrator removed skipped steps and fabricated outputs that a `react_core` orchestrator produced. A residual flake of about one run in ten remains; the evaluation is what catches it.
11. **Traces API limits (SaaS).** Search windows up to 4 hours; observation lookups a few per minute; a trace is complete about 15 seconds after the run ends. The runs API stream carries the `trace_id` on `message.created`, which links a conversation to its trace. On 2.18.0 `traces export` fails against this API (`fromStartTime is required`); fetch observations over REST with a window (`reference/module-observability.md`) or with the `cost-management` skill's `trace_cost.py`.
12. **`generate` on 2.18** needs a reachable Langfuse project (host and keys exported) even without `--with-langfuse`; without one it writes no test cases. `reference/module-benchmarks.md` has the details and the generator-script alternative.

---

## Reference map

| When the conversation touches… | Load |
|---|---|
| Targets, `env add --type`, token expiry, DevEd `.env`, Lima VM recovery, capability × target matrix | `reference/auth-env-matrix.md` |
| `quick-eval`, `evaluate`, config.yaml fields, judge and simulator models, output files, failures | `reference/module-eval.md` |
| Test case schema, DAGs, handoff goals, arg_matching, `record`, `generate`, generator scripts, coverage | `reference/module-benchmarks.md` |
| Metric meaning, thresholds, `analyze`, diagnosis table, attribution | `reference/module-analyze.md` |
| Rubric criteria, judge configuration, reading the results | `reference/module-rubric.md` |
| Attack catalogue, `plan`/`run`, attack file schema, success criteria, remediation | `reference/module-red-teaming.md` |
| Traces CLI, Python, REST, watsonx Orchestrate Agentic Control Plane, what to look for in a span tree | `reference/module-observability.md` |
| Block format, what Bob may run, handling output | `reference/command-emission.md` |

## Examples map

Adapt these rather than writing JSON from memory.

| Folder | What it shows |
|---|---|
| `examples/loan_underwriting/` | **Validated on 2.18 / 1.5.2.** Five ground-truth cases × two versions of a four-agent system (handoff goals, strict-before-fuzzy arguments, `max_user_turns`, END signal), evaluate and rubric configs, three hand-authored red-team attacks, `stories.csv` for `generate`, and the generator script. Agents and tools live in the building block under `assets/wxo-agents/examples/loan-underwriting/`. |
| `examples/portfolio_advisor/` | Eight single-agent cases: tool chains, multi-turn, RAG (`conversational_search`), text check. Written for an earlier framework; schema still valid. |
| `examples/minimal_single_tool/` | Smallest valid case; a few-shot prime for `generate`. |
| `examples/multi_agent_routing/` | Facilitator plus two collaborators. Replace the `transfer_to_*` tool names with `chat_with_collaborator_<agent>` for current ADKs. |
| `examples/rag_only/` | Knowledge-base cases scored with the RAG metrics. |
| `examples/stories_sample.csv` | Input format for `generate`. |

## Assets map

- `assets/mcp.json` — registers the `watsonx-orchestrate-adk-docs` MCP server (streamable HTTP, no local install) so Bob can search the current ADK docs.
- `assets/PREREQUISITES.md` — software, credentials, network, agent layout, shell environment, troubleshooting.

## Source of truth

ADK docs: https://developer.watson-orchestrate.ibm.com/ (evaluation: `evaluate/overview`, `evaluate/evaluate`, `evaluate/create_data`, `evaluate/analyze`, `evaluate/quick_eval`, `evaluate/rubric`, `evaluate/llm_vulnerability`; traces: `traces/overview`, `traces/traces_with_cli`, `traces/traces_with_python`). Use the MCP server in `assets/mcp.json` when a flag or behaviour needs confirming.
