# Agent Ops

Part of **[Control](../)** in the **[AI Control Plane](../../)**.

AI agents don't behave like traditional software — the same request can take a different path every time. **Agent Ops** is how you find out, before release and after every change, whether an agent routes correctly, calls the right tools with the right arguments, reaches the right decision, respects the policies you wrote, and holds up under pressure — and how you explain a conversation after the fact.

The capabilities below are built for **watsonx Orchestrate agents** with the evaluation framework in the Agent Development Kit (ADK 2.18+), on **SaaS** or **Developer Edition**. Once an agent is live, [Guardrails](../guardrails/) keep it within policy at runtime and [Cost Management](../cost-management/) tracks what it spends. For LangGraph/LangChain agents, see [LangGraph Agent Evaluation](#langgraph-agent-evaluation).

![Evaluate, observe, and optimize your agents using the Agent Ops Building Block](images/agent-ops-overview.png)

---

## Key Highlights

- Ground-truth test cases are files: a regression suite you re-run after every prompt, tool, or model change, in about a minute
- An LLM-simulated user plays each case; metrics per case, full transcripts, and root causes
- Plain-language policies become pass/fail checks a risk team can own (rubrics)
- Red-teaming with 15 attack types shows how the agent behaves when a user pushes for an exception
- Platform traces explain any conversation: handoffs, tool calls, model, tokens, latency
- A validated multi-agent example (loan underwriting, two versions) shows every capability finding a real defect

## Solves For

- "It works in the chat" — but nobody can say how often it takes the right path
- Failures that are hard to diagnose: wrong tool, wrong argument, skipped step, fabricated result
- Compliance rules that live in a document instead of a test
- Manual QA that does not keep up with prompt and model changes
- Production conversations that need explaining

---

## Capabilities at a Glance

| Capability | Command | What it gives you |
|---|---|---|
| **Quick-eval** | `orchestrate evaluations quick-eval` | Smoke test without ground truth: tool calls attempted, schema mismatches, hallucinated tools |
| **Test cases** | `record`, `generate`, or a generator script | Ground-truth cases with goal DAGs, handoff goals, and per-argument matching rules |
| **Evaluate** | `orchestrate evaluations evaluate` | Journey success, routing accuracy, tool-call recall and precision, text match, response time, per case |
| **Analyze** | `orchestrate evaluations analyze` | Expected vs actual calls, parameter mismatches, conversation history, tool docstring checks |
| **Rubric** | `evaluate` with `RubricEvaluation` | Pass/fail per plain-language rule with the judge's reasoning |
| **Red-team** | `red-teaming list / plan / run` | Attack success rate per attack and the transcript of every success |
| **Observe** | `observability traces search / export`, Python, REST | The span tree per conversation; dashboards in the Agentic Control Plane |

For runtime enforcement — Agent Controls (PII filter, content guardrails, secrets detection, rate limits, model fallback) and Pass/Flag/Block checks — see [Guardrails](../guardrails/). For cost and token spend in dollars, see [Cost Management](../cost-management/).

### Evaluation Workflow

`Quick-eval → Test cases → Evaluate → Analyze → Rubric → Red-team` — with traces whenever a conversation needs explaining.

> **From evaluation to governance evidence.** Evaluation metrics from watsonx Orchestrate agents can be captured automatically as governance evidence and tracked against policy thresholds — see [Enforcement Tracking](../compliance/#enforcement-tracking-for-watsonx-orchestrate) under Compliance.

### Metrics Reference (framework 1.5)

| Metric (`summary_metrics.csv`) | What it measures | Curated target |
|---|---|---|
| `is_success` (Journey Success) | every goal met in order with matching arguments, final answer matched | True |
| `orchestrate_agent_routing_accuracy` | handoffs to the expected collaborators | ≥ 0.9 |
| `tool_call_recall` | expected tool calls made | ≥ 0.9 |
| `tool_call_precision` | made tool calls that were expected (declare handoffs as goals) | ≥ 0.8 |
| `tool_calls_with_incorrect_parameter` | argument mismatches | 0 |
| `text_match`, `keyword_match`, `semantic_match` | the final-answer goal | match |
| `average_agent_response_time` | seconds per agent response | track |
| Faithfulness / Answer Relevancy / Retrieval Confidence (RAG) | knowledge-base cases | ≥ 0.8 / ≥ 0.7 / > 0.5 |
| `RubricEvaluation` | one pass/fail column per criterion, `overall_score`, comments | all pass |

Targets are starting points from engagements, not product SLAs.

**Red-teaming attacks** — on-policy: Instruction Override, Crescendo Attack, Emotional Appeal, Imperative Emphasis, Role Playing, Random Prefix, Random Postfix, Encoded Input, Foreign Languages; off-policy: Crescendo Prompt Leakage, Functionality Based Attacks, Undermine Model, Unsafe Topics, Jailbreaking, Topic Derailment. Native agents only.

---

## The loan-underwriting example

[`assets/wxo-agents/examples/loan-underwriting/`](assets/wxo-agents/examples/loan-underwriting/) is a four-agent underwriting system (orchestrator, intake, credit risk, compliance; five deterministic tools) in two versions. **v1** ships with a defect: the compliance agent skips anti-money-laundering screening for self-employed applicants. **v2** is the same system after evaluating and fixing.

| | v1 | v2 |
|---|---|---|
| Journey success (5 cases) | 3/5 — routing stays 1.0, so the orchestrator is fine and one agent's instructions are not | 5/5 |
| Rubric (4 compliance rules × 5 cases) | 18/20 | 20/20 |
| Red team (3 attacks on the AML policy) | 3/3 succeed on the first turn | 0/3 |

The folder holds the agents, tools, test cases for both versions, rubric and evaluation configs, hand-authored attacks, an import script that is safe on shared instances, and the design notes that made the framework's numbers trustworthy (handoff goals, `display_name`, argument order, turn caps, orchestrator style, model choice). Validated with ADK 2.18.0 / framework 1.5.2.

---

## LangGraph Agent Evaluation

For teams building agents with **LangGraph or LangChain**, a Python SDK package (`wx_gov_agent_eval`) is included under [`assets/langgraph-agents/`](assets/langgraph-agents/). It provides three evaluator classes — BasicRAG, ToolCalling, and AdvancedRAG — integrated with IBM watsonx.governance for metrics and factsheet tracking.

---

## What's Inside

### [Assets](assets/)
- [`assets/wxo-agents/`](assets/wxo-agents/) — scripts for the workflow (quick-eval, generate, evaluate, analyze, red-teaming), a single-agent sample with a knowledge base, and the loan-underwriting example.
- [`assets/langgraph-agents/`](assets/langgraph-agents/) — the `wx_gov_agent_eval` package for LangGraph/LangChain RAG and tool-calling agents.

### [Bob Skills](bob-skills/)
The `agent-ops` skill (also at [`ibm-bob/skills/agent-ops/`](../../../ibm-bob/skills/agent-ops/)) gives Bob the expertise to plan evaluations, write and validate test cases, interpret metrics, write rubrics, run red-teaming, and read traces for watsonx Orchestrate agents on SaaS or Developer Edition. Advisory stance: Bob emits the commands, you run them.

| Skill | Use it for |
|---|---|
| [Agent Ops](bob-skills/) | Evaluation, test cases, analysis, rubrics, red-teaming, traces for WXO agents |
| [Model Evaluation](model-evaluation/gen-ai-evaluations/bob-skills/) | Metric-level evaluation of prompts, RAG pipelines, LLM outputs, and agentic tool-calling with watsonx.governance |

The Agent Controls and Real-Time Guardrails skills are listed under [Guardrails](../guardrails/).

### [Bob Modes](bob-modes/)
The hands-on variant: Bob runs the commands, reads the results, and proposes fixes, phase by phase. Ships the validated loan-underwriting reference cases.

### [Model Evaluation](model-evaluation/)
Build-time evaluation of GenAI applications (RAG, LLM outputs, chatbot safety) with watsonx.governance metrics, plus predictive ML scoring examples — includes its own assets, Bob mode, and Bob skill.

---

## Getting Started

1. Install the ADK (`pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"`) and activate the environment where your agent lives.
2. Run the loan-underwriting example end to end ([`assets/wxo-agents/examples/loan-underwriting/`](assets/wxo-agents/examples/loan-underwriting/)) to see every capability on a system with a known defect.
3. Point the Bob [skill](bob-skills/) or [mode](bob-modes/) at your own agent.
4. Once the agent passes, add runtime enforcement with [Guardrails](../guardrails/) and track spend with [Cost Management](../cost-management/).

📖 Docs: [Agent Ops](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/agent-ops/)
