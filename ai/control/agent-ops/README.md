# Agent Ops

Part of **[Control](../)** in the **[AI Control Plane](../../)**.

AI agents don't behave like traditional software — they can respond differently every time. That makes them harder to test, trust, and troubleshoot.

**Agent Ops** is a framework for testing, monitoring, and improving AI agents from development through production. Once an agent is live, [Guardrails](../guardrails/) keep it within policy at runtime, and [Cost Management](../cost-management/) tracks what it spends.

The capabilities below are built for **watsonx Orchestrate agents** using the Agent Development Kit (ADK). For LangGraph/LangChain agents, see [LangGraph Agent Evaluation](#langgraph-agent-evaluation).

![Evaluate, observe, and optimize your agents using the Agent Ops Building Block](images/agent-ops-overview.png)

---

## Key Highlights

- Catch failures before deployment, and keep monitoring your agents in production
- Automated testing with simulated users — no manual QA bottleneck
- Built-in security testing against 15 adversarial attack types
- Go from user stories to test suites in minutes, not days
- Traces and latency for every agent interaction

## Solves For

- Agents that don't work as expected
- Hard-to-diagnose failures
- Slow, manual testing cycles
- Latency problems and failures that hide in production

---

## Capabilities at a Glance

| Capability | Details |
|---|---|
| **Evaluate** | Simulate real users at scale to verify the agent does what it's supposed to do |
| **Analyze** | Pinpoint exactly where and why an agent went wrong |
| **Quick-Eval** | Fast sanity check — catch structural issues early without writing full test cases |
| **Generate** | Turn plain-English user stories into automated test scenarios |
| **Red-Team** | Stress-test agent security against prompt injection, social engineering, and jailbreaking |
| **Observe** | Trace tool calls, routing, and latency per interaction with full traceability |

For runtime enforcement — Agent Controls and Pass/Flag/Block checks — see [Guardrails](../guardrails/). For cost and token spend per agent, see [Cost Management](../cost-management/).

### Evaluation Workflow

`Quick-Eval → Generate → Evaluate → Analyze → Red-Team → Observe`

1. **Quick-Eval** — fast referenceless validation to catch tool schema issues
2. **Generate** — auto-create benchmarks from plain-English user stories
3. **Evaluate** — run full evaluation with LLM-simulated users
4. **Analyze** — diagnose failures with default and enhanced analysis modes
5. **Red-Team** — test against 15 adversarial attack types
6. **Observe** — trace tool calls, routing, and latency via Langfuse

> **From evaluation to governance evidence.** Evaluation metrics from watsonx Orchestrate agents can be captured automatically as governance evidence and tracked against policy thresholds — see [Enforcement Tracking](../compliance/#enforcement-tracking-for-watsonx-orchestrate) under Compliance.

### Metrics Reference

| Metric | Target | What It Measures |
|---|---|---|
| Journey Success | 1.0 | All goals completed (binary) |
| Journey Completion % | 100% | Percentage of goals met |
| Tool Call Precision | >= 0.5 | Correct calls / total calls made |
| Tool Call Recall | >= 0.9 | Expected calls made / total expected |
| Agent Routing F1 | >= 0.9 | Harmonic mean of precision and recall |
| Faithfulness (RAG) | >= 0.8 | Answer grounded in retrieved docs |
| Answer Relevancy (RAG) | >= 0.7 | Answer addresses the question |
| Response Confidence (RAG) | > 0.5 | LLM confidence in generated response |

**Red-teaming attack types** — on-policy: instruction_override, emotional_appeal, role_playing, hypothetical_scenario, authority_impersonation, crescendo_attack; off-policy: jailbreaking, prompt_leakage, topic_derailment, social_engineering, data_extraction.

---

## LangGraph Agent Evaluation

For teams building agents with **LangGraph or LangChain**, a Python SDK package (`wx_gov_agent_eval`) is included under [`assets/langgraph-agents/`](assets/langgraph-agents/). It provides three evaluator classes — BasicRAG, ToolCalling, and AdvancedRAG — integrated with IBM watsonx governance for metrics and factsheet tracking.

---

## What's Inside

### [Assets](assets/)
- [`assets/wxo-agents/`](assets/wxo-agents/) — six numbered scripts covering the full workflow for watsonx Orchestrate agents: evaluation, analysis, quick-eval, benchmark generation, red-teaming, and Langfuse observability, plus a sample agent and sample data. The Langfuse script also reports cost and tokens, covered under [Cost Management](../cost-management/).
- [`assets/langgraph-agents/`](assets/langgraph-agents/) — the `wx_gov_agent_eval` package for evaluating LangGraph/LangChain RAG and tool-calling agents.

### [Bob Modes](bob-modes/)
Guided AI-assisted workflow for automated agent evaluation of WXO agents — LLM-simulated conversations, tool-calling precision/recall, RAG faithfulness scoring, and adversarial red-teaming.

### [Bob Skills](bob-skills/)
The `agent-ops` skill gives Bob the expertise to plan and run evaluations, red-teaming, and runtime observability for watsonx Orchestrate agents across Developer Edition and SaaS. Related skills in Control:

| Skill | Use it for |
|---|---|
| [Agent Ops](bob-skills/) | Evaluation, benchmarks, analysis, red-teaming, observability for WXO agents |
| [Model Evaluation](model-evaluation/gen-ai-evaluations/bob-skills/) | Metric-level evaluation of prompts, RAG pipelines, LLM outputs, and agentic tool-calling |

The Agent Controls and Real-Time Guardrails skills are listed under [Guardrails](../guardrails/).

### [Model Evaluation](model-evaluation/)
Build-time evaluation of GenAI applications (RAG, LLM outputs, chatbot safety) with watsonx.governance metrics, plus predictive ML scoring examples — includes its own assets, Bob mode, and Bob skill.

---

## Getting Started
1. Explore [`assets/wxo-agents/`](assets/wxo-agents/) and run the numbered scripts in order against a sample agent.
2. Check [`bob-modes/`](bob-modes/) or [`bob-skills/`](bob-skills/) to let Bob drive the evaluation workflow.
3. Once the agent passes evaluation, add runtime enforcement with [Guardrails](../guardrails/) and track spend with [Cost Management](../cost-management/).

📖 Docs: [Agent Ops](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/agent-ops/)
