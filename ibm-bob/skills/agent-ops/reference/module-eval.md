# Module: Eval

**TRIGGER:** the user wants to run `quick-eval` or `evaluate`, asks what goes in `config.yaml`, which model judges the run, how long a run takes, what the output files are, or hits an error while running.

Authoritative docs: https://developer.watson-orchestrate.ibm.com/evaluate/evaluate.md, `evaluate/quick_eval.md`, `evaluate/overview.md`.

---

## Two commands

| Command | Needs ground truth? | What it tells you |
|---|---|---|
| `orchestrate evaluations quick-eval` | No (uses `story` and `starting_sentence` only) | Per case: tool calls attempted, successful, failed on schema mismatch, failed on hallucinated tools. Python tools only (`--tools-path`). |
| `orchestrate evaluations evaluate` | Yes (`goals` / `goal_details`) | Per case: journey success, routing accuracy, tool-call recall and precision, missed and mis-parameterized calls, text match, steps, response time; full transcripts. |

Both simulate a user with an LLM and talk to the agent in the **active environment**. Two further LLM roles are independent of the agent under test:

- **Simulated user** — `llm_user_config.model_id` (default `meta-llama/llama-3-3-70b-instruct`); `user_response_style` steers it.
- **Judge / matcher** — `evaluation_config.provider_config.model_id` (default `bedrock/openai.gpt-oss-120b-1:0` through the `gateway` provider). On SaaS the default is served by the instance's gateway; on Developer Edition pick a model the local gateway serves (`orchestrate models list`).

---

## Inputs

- Active environment = the one where the agent, collaborators, and tools are imported (`orchestrate env list`).
- Test cases (`reference/module-benchmarks.md`) in a folder, or `quick-eval` with stories only.
- A `config.yaml` (recommended; everything else is flags).

## Read-only diagnostics (in order)

1. Versions (RULE 3).
2. `orchestrate env list` → the intended environment is active. On SaaS, check the token is fresh (activate again if the last activation was more than ~2 h ago).
3. `orchestrate agents list` → agent and collaborators present under the names used in the test cases.
4. Ancestor `.env`: `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`.
5. Test case JSON parses and `agent` matches a listed name (Bob reads the files).

---

## Config file (validated shape, ADK 2.18 / framework 1.5.2)

```yaml
# evaluations/eval_config.yaml
test_paths:
  - evaluations/testcases/              # files or directories
output_dir: results/evaluate/           # a timestamped folder is created inside
n_runs: 1                               # >1 to measure flakiness; files get .run<N>. in their names
num_workers: 2                          # parallel conversations
max_user_turns: 3                       # cap the simulated user (default 20); cases may override
enable_verbose_logging: true

evaluation_config:                      # judge / matcher model
  provider_config:
    provider: gateway
    model_id: watsonx/openai/gpt-oss-120b   # any model the active environment's gateway serves

llm_user_config:                        # simulated user
  user_response_style:
    - "Be concise"
    - "If the agent asks for missing information, provide it directly from your story"
    - "Once the task is complete, reply END and nothing else"

metrics:                                # name them; the framework default also includes the knowledge-base metrics and ToolParameterF1
  - JourneySuccessMetric
  - ToolCalling
  - OrchestrateAgentRoutingAccuracy
  - StepMetrics
  - AgentResponseTime
```

Notes:
- `auth_config` can be omitted: the framework uses the active environment and its cached token (*observed*; `--env-file` did not change the instance in our runs). The ADK doc's SaaS example sets `auth_config.url` plus `tenant_name: <environment name>`; use it only when you must pin the target.
- Top-level `provider_config` and `evaluation_model` still work but print deprecation warnings; `evaluation_config.provider_config` is the current field.
- `max_user_turns` at config level applies to every case; a case's own `max_user_turns` overrides it.
- Export `WO_API_KEY` (read from a key file) before long SaaS runs so the framework can refresh the token.
- For a knowledge-base agent add `KnowledgeBaseFaithfulness`, `KnowledgeBaseAnswerRelevancy`, `RetrievalConfidence`, `DocumentRetrievalQuality` to `metrics` and use `conversational_search` goals.

---

## Emitted commands

### `quick_eval` (smoke test)

```bash
# -t must point at the folder with the Python @tool modules; output lands in a timestamped folder under -o
source "$VENV_ACTIVATE" && \
orchestrate evaluations quick-eval \
  -p evaluations/testcases/ \
  -t tools/ \
  -o results/quick_eval/
```

*Observed:* about 2 minutes for five cases on SaaS; on multi-agent systems every `chat_with_collaborator_*` handoff is reported as a schema mismatch — ignore those rows and read the real tools.

### `evaluate_full`

```bash
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate -c evaluations/eval_config.yaml
```

### `evaluate_single_case`

```bash
# iterate on one case after a fix; -p overrides test_paths from the config
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate -c evaluations/eval_config.yaml \
  -p evaluations/testcases/tc02_self_employed_caution.json \
  -o results/evaluate_single/
```

### `evaluate_repeat` (flakiness)

Set `n_runs: 3` in the config (or a copy of it) and run `evaluate_full`; compare `is_success` across `*.run<N>.metrics.json`.

### Timing (observed, SaaS, app and instance in the same region)

Five cases, single run, `max_user_turns: 3`: 65–95 s. Each case is one real user turn plus 7–9 agent steps; cross-region round trips add up (a run makes about twenty API calls per case). Without the turn cap the simulated user chats to the 20-turn limit and a run takes minutes per case.

---

## Output (validated file list)

```
results/evaluate/2026-10-01_22-18-56/
├── summary_metrics.csv                     # one row per case (and per run); START HERE
├── average_metrics.json                    # numeric averages across cases
├── config.yml                              # the exact configuration used (reuse it)
├── <case>.metadata.json                    # thread / run identifiers for the conversation
├── messages/
│   ├── <case>.messages.json                # the conversation as the framework saw it
│   ├── <case>.messages.analyze.json        # each message paired with the judge's reason ("incorrect parameter", "expected": {...})
│   └── <case>.metrics.json                 # the per-case metric record
├── debug/evaluation_order.txt
└── knowledge_base_summary_metrics.json     # only when conversational_search goals exist
```

`summary_metrics.csv` columns (framework 1.5.2): `run_idx`, `orchestrate_agent_routing_accuracy`, `total_steps`, `llm_steps`, `average_agent_response_time`, `total_tool_calls`, `expected_tool_calls`, `correct_tool_calls`, `missed_tool_calls`, `relevant_tool_calls`, `tool_calls_with_incorrect_parameter`, `tool_call_recall`, `tool_call_precision`, `tool_match_success`, `keyword_match`, `semantic_match`, `text_match`, `is_success`, `dataset_name`, `text_match_comment`. Meanings and thresholds: `reference/module-analyze.md`.

The terminal table truncates in narrow windows; read the CSV instead (`python3 -c "import csv,sys;[print(r['dataset_name'], r['is_success'], r['tool_call_recall'], r['tool_call_precision'], r['orchestrate_agent_routing_accuracy']) for r in csv.DictReader(open(sys.argv[1]))]" results/evaluate/<run>/summary_metrics.csv`).

---

## Interpretation handoff

Once the user pastes the run path, Bob reads `summary_metrics.csv` and the `messages/*.messages.analyze.json` of each failed case (no need to ask the user to `cat` anything) and continues in `reference/module-analyze.md`.

---

## Common failures (curated; verify against the transcript)

| Symptom | Cause | Fix |
|---|---|---|
| `401` / `Unauthorized` part-way through a run | SaaS token expired (about 2 h) | Re-activate the environment with `--api-key "$(...)"`; export `WO_API_KEY` for refresh |
| The run hit a different instance than expected | the active environment is not the one you think; `--env-file` does not switch it | `orchestrate env list`, activate the right one |
| `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}` | key does not belong to the activated instance | Confirm which instance the key is for; activate that environment |
| `400 Bad Request` from `iam.cloud.ibm.com/identity/token` | ancestor `.env` overriding `WO_INSTANCE` / `WO_API_KEY` | Move it aside or prefix the command with `WO_INSTANCE= WO_API_KEY=` |
| Agent not found | `agent` in the case ≠ `orchestrate agents list` name, or wrong environment | Fix the field or the environment |
| Every case takes minutes; transcript shows small talk after the task | `max_user_turns` default 20 | `max_user_turns: 3` plus "reply END and nothing else" in the story |
| `model_not_supported` / 404 on the judge or simulator model | the active gateway does not serve that `model_id` (typical on DevEd) | `orchestrate models list`; set `evaluation_config.provider_config.model_id` and `llm_user_config.model_id` to served models |
| Run aborts with a missing `<case>.metadata.json` or `session_id=None` | one conversation failed transiently (gateway hiccup); the framework crashed on the missing file | Re-run; if persistent, check the agent responds in the chat UI |
| `KeyError: '<uuid>'` before any case runs; `agents list` prints many `Tool with ID … not found` | orphaned tool references on the tenant | Clean up (`agents update` without the dead refs) or evaluate on a clean instance |
| Agent narrates tool calls as text, or returns a parse-failure fallback | model does not tool-call reliably in this setup | Switch the agent's `llm` (in the loan example `watsonx/openai/gpt-oss-120b` was dependable) before touching instructions |
| Precision ≈ 0.5–0.6 with every case passing | handoffs not declared as goals | `reference/module-benchmarks.md` → handoff goals |
| Routing accuracy 0.0 although handoffs happened | `display_name` ≠ `name` on an agent | Set them equal and re-import |
| `analyze` fails later with a `text_match` validation error | framework 1.5.2 writes a number | Normalize a copy (`reference/module-analyze.md`) |

---

## Done when

- `summary_metrics.csv` exists for the run and Bob has stated journey success (x/n), routing accuracy, recall, precision, and the slowest case.
- Every failed case has a one-line cause with the step where it went wrong.
- The user has chosen: fix and re-run one case, run `analyze`, add a rubric, red-team, or stop.
