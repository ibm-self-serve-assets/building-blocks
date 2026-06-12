# Module: Analyze

**TRIGGER:** Load when user has eval results (a `summary_metrics.csv` / `results.json` / `knowledge_base_summary_metrics.json` from a prior `evaluate` or `quick-eval`), asks "what does this metric mean", asks "why did this scenario fail", asks about `--mode enhanced`, or needs the benchmark-vs-agent attribution heuristic (RULE 10).

---

## Two modes

```
orchestrate evaluations analyze                  # default — heuristic interpretation
orchestrate evaluations analyze --mode enhanced  # LLM-backed; produces tool-docstring enrichment suggestions
```

This module is invoked after `evaluate` or `quick-eval` produces an output directory (see `reference/module-eval.md` expected outputs).

**Authoritative doc:** https://developer.watson-orchestrate.ibm.com/evaluate/analyze.md

---

## Inputs

- **Required:** an eval output dir from `evaluate` or `quick-eval`.
- **Required for `--mode enhanced`:** active env with LLM access (DevEd local or SaaS cloud).
- **Optional:** `--tools-path` (for tool-aware enrichment).

## Read-only diagnostics

- Result dir exists and contains `summary_metrics.csv`. Read the directory listing.
- Read `summary_metrics.csv` and `results.json` (with limited offsets — never load full `results.json` into chat).

---

## Emitted commands

### `analyze_default`
```bash
# `analyze` writes its report alongside --data-path (no --output-dir flag).
source "$VENV_ACTIVATE" && \
orchestrate evaluations analyze \
  --data-path <eval_output_dir>
```

### `analyze_enhanced`
```bash
# GATE_TOOL_ENRICHMENTS=false enables docstring enrichment recommendations.
# --mode enhanced calls an LLM — needs active env with LLM access (watsonx).
# `analyze` does NOT take --output-dir; report writes alongside --data-path.
source "$VENV_ACTIVATE" && \
GATE_TOOL_ENRICHMENTS=false \
orchestrate evaluations analyze \
  --data-path <eval_output_dir> \
  --tools-path agent/tools \
  --mode enhanced
```

---

## Flags reference (authoritative from `--help`, ADK 2.9.0)

- `--data-path` / `-d` — path to dir with saved eval results (REQUIRED). **Point at the timestamped output dir** produced by your `evaluate` run (e.g., `eval_results/20260607-173652/`), **NOT** the parent `eval_results/` dir. The parent typically contains many timestamped subdirs from prior runs; `analyze` only reads `summary_metrics.csv` directly inside `--data-path` and will fail with `FileNotFoundError: [Errno 2] No such file or directory: '<path>/summary_metrics.csv'` if you point at the parent.
- `--tools-path` / `-t` — path to tool definitions (used by `--mode enhanced`)
- `--env-file` / `-e` — path to `.env`
- `--mode` / `-m` — `default` or `enhanced` (LLM-backed)

**NOT valid flags for `analyze`:**
- `--output-dir` (does not exist; report writes alongside `--data-path`)
- `--config` (analyze reads config from the data-path's saved run)

**Tip — finding the right `--data-path` when you have many old runs:** `ls -td eval_results/*/ | head -1` gives the most recent timestamped subdir.

---

## Metric definitions and thresholds

**SOURCE NOTE (RULE 9):** Metric NAMES and SEMANTICS are WXO-published (computed by the eval framework). **Threshold VALUES below (e.g., ">= 0.9") are curated starting points** based on real engagement experience, **NOT WXO-published SLAs**. Adjust per your domain and customer risk tolerance.

### Agent metrics

| Metric | Type | Threshold | Notes |
|---|---|---|---|
| Journey Success | binary 0\|1 | 1.0 ideally | **STRICTEST.** All goals met in correct order per the DAG. |
| Journey Completion | 0-100% | >= 80% | How far the agent got through the goals before stopping. |
| Tool Call Recall | 0-1 | >= 0.9 | Of expected tool calls, fraction actually made. |
| Tool Call Precision | 0-1 | >= 0.5 | Of actual tool calls, fraction that were expected. Low precision = extra calls. |
| Agent Routing F1 | 0-1 | >= 0.9 | Facilitator → collaborator routing accuracy in multi-agent setups. |
| Text Match | match \| no_match | only "Summary Matched" is passing | Used with `text_checks`. |
| Avg Response Time | ms | regression-based | Track over time; alert on increase. |

### RAG metrics

| Metric | Type | Threshold | Notes |
|---|---|---|---|
| Faithfulness | 0-1 | >= 0.8 | Generated answer is supported by retrieved context. |
| Answer Relevancy | 0-1 | >= 0.7 | Generated answer addresses the user question. |
| Response Confidence | 0-1 | > 0.5 | |
| Retrieval Confidence | 0-1 | > 0.5 | |

---

## Failure diagnosis table

**SOURCE NOTE (RULE 9):** curated; not WXO-published. Symptom→cause→investigation mappings below are starting points drawn from real engagement experience. Verify against the actual trace and agent code before acting on a recommendation.

| Symptom | Cause | Investigations |
|---|---|---|
| Recall < 1.0, tool never called | Agent did not invoke the expected tool | Verify tool import; check agent instructions; check story clarity; verify benchmark `tool_name` matches code |
| Recall = 1.0, Precision < 1.0 | Agent called extra tools | Usually fine if tools are read-only; review the trace; consider adding missing goals to benchmark |
| Recall < 1.0, strict-match arg failure | Agent called the right tool with wrong args | Check story arg specificity; check tool arg names match exactly; check `arg_matching` strategy |
| Journey Completion < 100%, `session_id = None` | Simulator infrastructure crash | Re-run scenario; non-deterministic. If persistent across 3 runs, check provider config. |
| Routing F1 < 0.9 | Facilitator delegated to wrong collaborator OR did not delegate | Check facilitator's `whenToUse` for each collaborator; check story clarity about intent |
| Faithfulness < 0.8 | Agent hallucinated content not in retrieved context | Inspect retrieved chunks; review agent instructions for "cite sources only"; check KB embedding quality |
| Answer Relevancy < 0.7 | Agent retrieved wrong chunks | Check query reformulation; check KB content coverage; review chunk size / overlap |
| Text Match = 'No Match' | Required keywords absent from response | Check `text_checks` keywords for over-specificity; consider whether keywords should be fuzzy |
| Avg Response Time regression | Tool latency or LLM throttling | Export traces and inspect span durations (`reference/module-observability.md`); check provider rate-limits |
| All scenarios fail with 401/403 | Token expired or wrong env active | `orchestrate env list`; re-activate; regenerate `config.yaml` token |

---

## Benchmark vs agent — attribution heuristic (RULE 10)

**SOURCE NOTE (RULE 9):** curated; not WXO-published. Apply judgment.

**Before declaring "the agent has a bug", check the benchmark is not the issue.** Common benchmark issues:

- `tool_name` in `goal_details` does NOT match the agent's actual tool name
- `strict` `arg_matching` on a value that the story does NOT unambiguously imply
- Story lacks explicit end-of-conversation criteria (simulator ends early)
- Goals DAG has an unreachable goal (no path from the starting goal)

**If the benchmark is the issue:** fix the benchmark and re-run only that scenario (see `reference/module-eval.md` → `evaluate_single_scenario`).

---

## Done-when criteria

- Bob has read `summary_metrics.csv` and the relevant rows of `results.json`.
- Each failing scenario has been classified as benchmark issue, agent issue, or infrastructure issue.
- Concrete next actions have been listed (per-scenario), and user has picked which to apply.
