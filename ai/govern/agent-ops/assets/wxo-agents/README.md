# Agent Ops — assets for watsonx Orchestrate agents

Scripts and examples for the **evaluation framework in the watsonx Orchestrate ADK** (`orchestrate evaluations …`, `orchestrate observability traces …`). Works against **SaaS** instances and **Developer Edition**; validated with ADK 2.18.0 / evaluation framework 1.5.2.

## What is inside

| Path | What it is |
|---|---|
| `01_agent_evaluation.py` | Runs `evaluate` from a config file and prints a per-case table from `summary_metrics.csv` |
| `02_agent_analysis.py` | Runs `analyze` (default and enhanced) on the latest run, with the framework-1.5 `text_match` workaround |
| `03_quick_eval.py` | Runs `quick-eval`: reference-less smoke test for tool calls, schema mismatches, hallucinated tools |
| `04_benchmark_generation.py` | Runs `generate` from a stories CSV and a Python tools file; reviews the generated cases |
| `05_red_teaming.py` | Lists attacks, plans them from your test cases, runs them, summarizes success per attack |
| `examples/loan-underwriting/` | **Validated multi-agent example** — four agents in two versions, five deterministic tools, 5 ground-truth cases × v1/v2, rubric, 3 hand-authored attacks, import script |
| `sample_agent/`, `sample_data/` | A single customer-support agent with a knowledge base, three benchmark cases, stories CSV, and an evaluate config — the quickest smoke test |

Cost in dollars (Langfuse) moved to the [Cost Management](../../../cost-management/assets/langfuse/) building block.

## Prerequisites

- Python 3.12 and the ADK with the agentops extra:
  ```bash
  python3.12 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt        # ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0
  ```
- An activated environment pointing at the instance where the agent is imported:
  ```bash
  orchestrate env add --name <env> --url https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<id>
  orchestrate env activate <env> --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
  ```
  SaaS tokens expire after about two hours; the framework evaluates whatever environment is active. For Developer Edition: `orchestrate server start -e .env` (see `.env.template`; add `-i` for traces) and `orchestrate env activate local`.
- On a **shared instance**, list before importing (`orchestrate agents list`) and keep a prefix on your asset names; never update assets you did not create.

## Quick start (single agent)

```bash
# import the sample agent
orchestrate tools import -k python -f sample_agent/tools/support_tools.py
orchestrate knowledge-bases import -f sample_agent/knowledge_bases/product_kb.yaml
orchestrate agents import -f sample_agent/agent_config.yaml

python 03_quick_eval.py                 # smoke test
python 01_agent_evaluation.py           # evaluate with sample_data/eval_config.yaml
python 02_agent_analysis.py             # analyze the latest run
python 05_red_teaming.py --plan-only    # generate attack files, review them, then run without --plan-only
```

Every script takes `ORC=<path to orchestrate>` if the CLI is not on `PATH`, and prints the exact command it runs.

## The loan-underwriting example (multi-agent)

```bash
cd examples/loan-underwriting
./import.sh                                                    # collision check, tools, collaborators, orchestrators
orchestrate evaluations evaluate -c evaluations/eval_config_v1.yaml      # v1: ships with a compliance defect
orchestrate evaluations evaluate -c evaluations/eval_config_v2.yaml      # v2: after evaluating and fixing
orchestrate evaluations evaluate -c evaluations/rubric_config_v2.yaml    # plain-language compliance rules
orchestrate evaluations red-teaming run -a evaluations/red_team_v2 -o results/red_team_v2
python scripts/summarize.py results/evaluate_v1
```

See [`examples/loan-underwriting/README.md`](examples/loan-underwriting/README.md) for the story, the expected results, and the design notes (handoff goals, `display_name`, strict-before-fuzzy arguments, `max_user_turns`, planner-style orchestrator).

## Workflow

```
quick-eval → test cases → evaluate → analyze → rubric → red-team      (traces whenever a conversation needs explaining)
   (03)      (04 / script)   (01)      (02)                 (05)
```

## Metrics (summary_metrics.csv, framework 1.5)

| Column | Meaning | Curated target |
|---|---|---|
| `is_success` | all goals met in order with matching arguments; text goal matched | True |
| `orchestrate_agent_routing_accuracy` | handoffs to the expected collaborators | ≥ 0.9 |
| `tool_call_recall` / `missed_tool_calls` | expected tool calls made | ≥ 0.9 / 0 |
| `tool_call_precision` | made calls that were expected (declare handoffs as goals or this drops) | ≥ 0.8 |
| `tool_calls_with_incorrect_parameter` | argument mismatches | 0 |
| `keyword_match`, `semantic_match`, `text_match` | the final-answer goal | match |
| `average_agent_response_time` | seconds per agent response | track |

Knowledge-base cases add faithfulness, answer relevancy, retrieval and response confidence. `RubricEvaluation` adds `overall_score`, one column per criterion, and the judge's comments. Targets are starting points, not product SLAs.

## Red-teaming attacks (framework 1.5)

On-policy: Instruction Override, Crescendo Attack, Emotional Appeal, Imperative Emphasis, Role Playing, Random Prefix, Random Postfix, Encoded Input, Foreign Languages. Off-policy: Crescendo Prompt Leakage, Functionality Based Attacks, Undermine Model, Unsafe Topics, Jailbreaking, Topic Derailment. Native agents only. Review every generated attack file: its goal defines what "the attack succeeded" means.

## Test case format

```json
{
  "agent": "agent_name",
  "story": "Who the user is, the facts they know, what they want. Once <done>, reply END and nothing else.",
  "starting_sentence": "First user message",
  "max_user_turns": 3,
  "goals": { "route_x": ["tool_a"], "tool_a": ["summarize"], "summarize": [] },
  "goal_details": [
    { "type": "tool_call", "name": "route_x", "tool_name": "chat_with_collaborator_<agent>", "args": {"message": "IGNORE"}, "arg_matching": {"message": "ignore"} },
    { "type": "tool_call", "name": "tool_a", "tool_name": "tool_a", "args": {"id": "X1", "note": "free text"}, "arg_matching": {"note": "fuzzy"} },
    { "type": "text", "name": "summarize", "response": "expected gist", "keywords": ["must appear"] }
  ]
}
```

`arg_matching`: `strict` (default), `fuzzy`, `optional`, `ignore`; `{"IGNORE": null}` skips all arguments. Strict fields before fuzzy ones. Docs: https://developer.watson-orchestrate.ibm.com/evaluate/overview
