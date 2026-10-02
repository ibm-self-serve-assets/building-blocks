# Module: Analyze

**TRIGGER:** the user has a run folder (`summary_metrics.csv`, `messages/`), asks what a metric means, why a case failed, whether precision 0.6 matters, how to run `analyze`, or whether to fix the test case, the agent, or the model.

Authoritative doc: https://developer.watson-orchestrate.ibm.com/evaluate/analyze.md

---

## Metrics (summary_metrics.csv, framework 1.5.2)

Names and semantics are the framework's; **thresholds are curated starting points, not WXO-published SLAs** (RULE 10).

| Column | Meaning | Curated threshold |
|---|---|---|
| `is_success` | Journey Success: every goal met in DAG order with matching arguments, and the text goal matched | `True` on every case you intend to ship |
| `orchestrate_agent_routing_accuracy` | handoffs to the expected collaborators (0.0 when there is no routing in the case) | ≥ 0.9 |
| `tool_call_recall` | expected tool calls that were made, in order | ≥ 0.9 |
| `tool_call_precision` | made tool calls that were expected | ≥ 0.8 once handoffs are declared as goals; 0.5–0.6 usually means they are not |
| `missed_tool_calls` / `tool_calls_with_incorrect_parameter` | counts behind recall and precision | 0 |
| `expected_tool_calls`, `total_tool_calls`, `correct_tool_calls`, `relevant_tool_calls` | raw counts | — |
| `tool_match_success` | all expected tool calls matched | `True` |
| `keyword_match`, `semantic_match`, `text_match`, `text_match_comment` | the `text` goal: keywords present, semantic similarity, overall ("Matched 0/1 text goals") | match |
| `total_steps`, `llm_steps` | conversation length | watch for growth after prompt changes |
| `average_agent_response_time` | seconds per agent response | regression-based |
| `run_idx`, `dataset_name` | run number (`n_runs`), case name | — |

`average_metrics.json` holds the numeric averages. Knowledge-base cases add `knowledge_base_summary_metrics.json` with faithfulness (≥ 0.8), answer relevancy (≥ 0.7), retrieval and response confidence (> 0.5).

Other metric names in the framework registry (add to `metrics:` to compute; not all are documented): `ToolParameterF1`, `TextMatchMetric`, `SemanticMatchMetric`, `KeywordMatchMetric`, `WordCountMetric`, `ToolNameLeakageMetric`, `KnowledgeBaseFaithfulness`, `KnowledgeBaseAnswerRelevancy`, `RetrievalConfidence`, `DocumentRetrievalQuality`, `RubricEvaluation` (`reference/module-rubric.md`), `AttackSuccessMetric` (red-teaming).

---

## Reading a failed case

`messages/<case>.messages.analyze.json` is a list of `{"message": ..., "reason": ...}`:

- `message.type` is `tool_call` (content is JSON `{"name": ..., "args": ...}`), `tool_response`, or a plain message with `role` `user` / `assistant`;
- `reason.reason` explains the judge's verdict for that step (for example `"incorrect parameter"`) and `reason.expected` shows what the goal wanted.

Bob reads the failed case's file, finds the first step whose `reason` is not a pass, and quotes the tool name, the arguments made, and the arguments expected. That one line is usually the whole diagnosis.

---

## `analyze`

```bash
# default mode: expected vs actual tool calls, parameter mismatches, missed calls, conversation history, summary
source "$VENV_ACTIVATE" && \
COLUMNS=170 orchestrate evaluations analyze -d results/evaluate/<timestamp>/
```

```bash
# enhanced mode adds docstring quality checks and enrichment suggestions for the tools that failed
# GATE_TOOL_ENRICHMENTS=false lifts the "minimal descriptions only" gate
source "$VENV_ACTIVATE" && \
COLUMNS=170 GATE_TOOL_ENRICHMENTS=false orchestrate evaluations analyze \
  -d results/evaluate/<timestamp>/ \
  -t tools/ \
  --mode enhanced
```

Flags: `-d/--data-path` (the **timestamped** run folder, required), `-t/--tools-path`, `-m/--mode default|enhanced`, `-e/--env-file`. There is no `--output-dir`; the report prints to the terminal (widen it or set `COLUMNS`).

### `text_match` validation error (observed on 1.5.2)

`analyze` validates `text_match` in `messages/*.metrics.json` as one of `Summary Matched`, `Partially Match`, `Summary MisMatched`, `NA`, while `evaluate` writes a number. Analyze a normalized copy:

```bash
# writes results/evaluate/<timestamp>-analyze/ with text_match as the enum string, then runs analyze on it
source "$VENV_ACTIVATE" && \
SRC=results/evaluate/<timestamp> DST=results/evaluate/<timestamp>-analyze python3 - <<'PY'
import glob, json, os, shutil
src, dst = os.environ["SRC"], os.environ["DST"]
shutil.rmtree(dst, ignore_errors=True); shutil.copytree(src, dst)
for mf in glob.glob(os.path.join(dst, "messages", "*.metrics.json")):
    m = json.load(open(mf)); tm = m.get("text_match")
    if isinstance(tm, (int, float)) and not isinstance(tm, bool):
        m["text_match"] = "Summary Matched" if tm >= 1 else "Summary MisMatched" if tm <= 0 else "Partially Match"
        json.dump(m, open(mf, "w"))
PY
COLUMNS=170 orchestrate evaluations analyze -d results/evaluate/<timestamp>-analyze/ -t tools/
```

---

## Diagnosis table (curated)

| Symptom | Likely cause | Check |
|---|---|---|
| recall < 1, one tool missed, routing 1.0 | the agent that owns the tool skipped it (instructions, or the model talked instead of calling) | transcript: did the collaborator reach that step? In the loan example v1's compliance agent skipped AML for self-employed applicants by instruction |
| recall 1.0, precision 0.5–0.6, cases pass | handoffs counted as unexpected calls | add `chat_with_collaborator_*` goals |
| routing accuracy 0.0 although handoffs happened | `display_name` ≠ `name` | fix YAML, re-import |
| `tool_calls_with_incorrect_parameter` > 0 | strict value the story never stated, or the agent transformed the value | `reason.expected` vs made; is the story explicit? is the strict field listed before a fuzzy one? |
| final tool missed on an "obvious" case; the agent wrote the result as text | orchestrator skipped the tool (react-style orchestrators do this more; a residual flake remains with planner style) | `style: planner`, orchestrator owns the final tool, instruction "this is a real tool call, never print its arguments"; re-run to confirm the rate |
| text goal mismatch, everything else passes | keywords too specific or the answer phrased differently | relax `keywords`; keep `response` descriptive |
| long transcripts, many user turns after the task | `max_user_turns` default | cap to 3 + END |
| every case fails identically with a 401/403 | token expired or wrong environment | re-activate; `env list` |
| one case fails with a crash, others fine; `metadata.json` missing | transient conversation failure | re-run that case |
| agent returns a "could not parse" fallback or narrates calls | model not tool-calling reliably | switch the agent's `llm`; re-run before editing prompts |
| faithfulness < 0.8 (RAG) | answer not grounded in retrieved text | inspect retrieved chunks; instruct to cite; check KB content |
| response time regression | tool or model latency | export the trace (`reference/module-observability.md`) and read span durations |

---

## Attribution (RULE 11)

1. **Test case.** Wrong `tool_name` or collaborator name; strict match on a value the story does not state; missing handoff goal; unreachable goal; no stop signal. Fix the case and re-run only it.
2. **Agent.** Instructions allow or require the wrong behaviour (v1 compliance agent: "do not call AML for self-employed"); orchestrator style; tool ownership; collaborator descriptions that do not say when to use them.
3. **Model.** The same prompt and case pass on one model and fail on another; parse-failure fallbacks; narrated tool calls.
4. **Infrastructure.** Transient failures, expired tokens, rate limits.

State it as: *"tc02 failed because \<test case | agent | model | infra\>: \<one line\>. Fix: \<one action\>."*

---

## Done when

- `summary_metrics.csv` read; each failed case attributed with the failing step quoted.
- `analyze` run (default, and enhanced when tool docstrings are suspect) and its findings folded into the attribution.
- Concrete next actions listed per case; the user has picked which to apply, and whether to re-run one case or the suite.
