# Agent Ops

Part of the **[AI Control Plane](../)** building blocks.

AI agents don't behave like traditional software — they can respond differently every time. That makes them harder to test, trust, and troubleshoot.

**Agent Ops** is a framework for testing, monitoring, and improving AI agents from development through production — and for keeping them within policy at runtime through [Agent Controls](#agent-controls--runtime-policy-enforcement).

The capabilities below are built for **watsonx Orchestrate agents** using the Agent Development Kit (ADK). For LangGraph/LangChain agents, see [LangGraph Agent Evaluation](#langgraph-agent-evaluation).

![Evaluate, observe, and optimize your agents using the Agent Ops Building Block](model-evaluation/gen-ai-evaluations/assets/evaluation-scripts/images/Agent%20Ops%20Evaluation-2026-04-21-220937_150.png)

---

## Key Highlights

- Catch failures before deployment, and keep monitoring your agents in production
- Automated testing with simulated users — no manual QA bottleneck
- Built-in security testing against 15 adversarial attack types
- Go from user stories to test suites in minutes, not days
- Full cost and performance visibility per agent interaction
- Runtime policy controls — PII filters, guardrails, secrets detection, rate limits, model fallback — as configuration, not code

## Solves For

- Agents that don't work as expected
- Hard-to-diagnose failures
- Slow, manual testing cycles
- Unpredictable cost and latency
- Unguarded outputs containing PII, credentials, or harmful content that must be blocked at runtime, not found afterwards

---

## Capabilities at a Glance

| Capability | Details |
|---|---|
| **Evaluate** | Simulate real users at scale to verify the agent does what it's supposed to do |
| **Analyze** | Pinpoint exactly where and why an agent went wrong |
| **Quick-Eval** | Fast sanity check — catch structural issues early without writing full test cases |
| **Generate** | Turn plain-English user stories into automated test scenarios |
| **Red-Team** | Stress-test agent security against prompt injection, social engineering, and jailbreaking |
| **Observe** | Track cost, latency, and token usage per interaction with full traceability |
| **Enforce** | Attach runtime policy controls — guardrails, PII filters, rate limits, model fallback — to agents, tools, and models as configuration, not code |

### Evaluation Workflow

`Quick-Eval → Generate → Evaluate → Analyze → Red-Team → Observe`

1. **Quick-Eval** — fast referenceless validation to catch tool schema issues
2. **Generate** — auto-create benchmarks from plain-English user stories
3. **Evaluate** — run full evaluation with LLM-simulated users
4. **Analyze** — diagnose failures with default and enhanced analysis modes
5. **Red-Team** — test against 15 adversarial attack types
6. **Observe** — track cost, latency, and token usage via Langfuse

> **From evaluation to governance evidence.** Evaluation metrics from watsonx Orchestrate agents can be captured automatically as governance evidence and tracked against policy thresholds — see [Enforcement Tracking](../ai-compliance/#enforcement-tracking-for-watsonx-orchestrate) under AI Compliance.

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

## Agent Controls — Runtime Policy Enforcement

Evaluation tells you how an agent behaves; **Agent Controls** ensure it stays within authorized boundaries once deployed. Powered by the watsonx Orchestrate Controls framework, controls are reusable policy artifacts — PII filters, content guardrails, secrets detection, rate limits, SQL sanitization, and model routing — attached to agents, tools, and models **as configuration, not code**. Policies can be added, changed, or removed without touching the agent's implementation, and the same agent can carry different policies per environment.

A control combines four things: a **policy artifact** (the rule), an **asset** (the agent, tool, or model it protects), an **execution hook** (the pipeline stage where it fires, e.g. `agent_pre_invoke`, `tool_pre_invoke`), and a **priority** (lower numbers run first). If a control blocks, the pipeline halts immediately and nothing downstream runs.

| Layer | Control | What It Enforces |
|---|---|---|
| **Agent** | PII Filter | Detects and masks SSNs, emails, phone numbers, credit cards — redact, partial, hash, tokenize, or remove |
| **Agent** | Content Guardrails | Blocks jailbreaks, hate/abuse/profanity (HAP), violence, sexual content, and bias on input and output |
| **Agent** | Secrets Detector | Catches AWS keys, JWTs, API keys, private key blocks — redact or block |
| **Agent** | Output Length Guard / Regex Pattern | Enforces response size limits; redacts or blocks custom patterns |
| **Tool** | Rate Limiter | Caps tool invocations per minute, per tool and per tenant — stops runaway agent loops |
| **Tool** | SQL Sanitizer | Blocks destructive SQL (DROP, TRUNCATE, unscoped DELETE/UPDATE) and injection comments before execution |
| **Tool** | Guardrails / Secrets / Output Length | Same protections as the agent layer, applied at the tool input/output boundary |
| **Model** | Fallback / Retry | Routes to backup models on errors (429, 5xx) with configurable retries — no agent code change |
| **Model** | Load Balance | Distributes requests across providers using weighted ratios |

**Typical scenarios:** PII compliance for customer-service agents, SQL-injection protection for Text-to-SQL agents, secrets-leakage prevention in finance, and model fallback for high availability.

Agent Controls are watsonx Orchestrate-native. If your agent runs on another framework, or you need custom LLM-as-judge criteria and threshold policy as code, use the [Real-Time Guardrails](real-time-guardrails/) SDK instead — it delivers the same Pass/Flag/Block enforcement as a library, REST API, or MCP server.

📖 Full control reference, hook diagram, and priority guidance: [Agent Ops on the docs site](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/ai-control-plane/agent-ops/#agent-controls-runtime-policy-enforcement)

---

## LangGraph Agent Evaluation

For teams building agents with **LangGraph or LangChain**, a Python SDK package (`wx_gov_agent_eval`) is included under [`assets/langgraph-agents/`](assets/langgraph-agents/). It provides three evaluator classes — BasicRAG, ToolCalling, and AdvancedRAG — integrated with IBM watsonx governance for metrics and factsheet tracking.

---

## What's Inside

### [Assets](assets/)
- [`assets/wxo-agents/`](assets/wxo-agents/) — six numbered scripts covering the full workflow for watsonx Orchestrate agents: evaluation, analysis, quick-eval, benchmark generation, red-teaming, and Langfuse observability, plus a sample agent and sample data.
- [`assets/langgraph-agents/`](assets/langgraph-agents/) — the `wx_gov_agent_eval` package for evaluating LangGraph/LangChain RAG and tool-calling agents.

### [Bob Modes](bob-modes/)
Guided AI-assisted workflow for automated agent evaluation of WXO agents — LLM-simulated conversations, tool-calling precision/recall, RAG faithfulness scoring, and adversarial red-teaming.

### [Bob Skills](bob-skills/)
The `agent-ops` skill gives Bob the expertise to plan and run evaluations, red-teaming, and runtime observability for watsonx Orchestrate agents across Developer Edition and SaaS. Related skills in the AI Control Plane:

| Skill | Use it for |
|---|---|
| [Agent Ops](bob-skills/) | Evaluation, benchmarks, analysis, red-teaming, observability for WXO agents |
| [Agent Controls](https://ibm-self-serve-assets.github.io/building-blocks-docs/ibm-bob/skills/) | Artifact selection, hook assignment, priority layering, defence-in-depth stacking |
| [Model Evaluation](model-evaluation/gen-ai-evaluations/bob-skills/) | Metric-level evaluation of prompts, RAG pipelines, LLM outputs, and agentic tool-calling |
| [Real-Time Guardrails](real-time-guardrails/bob-skills/) | Runtime Pass/Flag/Block guardrails at input, retrieval, generation, and output |

### [Model Evaluation](model-evaluation/)
Build-time evaluation of GenAI applications (RAG, LLM outputs, chatbot safety) and predictive ML models with watsonx.governance metrics — includes its own assets, Bob mode, and Bob skill.

### [Real-Time Guardrails](real-time-guardrails/)
Framework-agnostic runtime enforcement SDK — Pass/Flag/Block at input, retrieval, generation, and output, as a library, REST API, or MCP server — includes its own assets, Bob mode, and Bob skill.

---

## Getting Started
1. Explore [`assets/wxo-agents/`](assets/wxo-agents/) and run the numbered scripts in order against a sample agent.
2. Check [`bob-modes/`](bob-modes/) or [`bob-skills/`](bob-skills/) to let Bob drive the evaluation workflow.
3. Once the agent passes evaluation, add runtime enforcement with Agent Controls (WXO) or the [Real-Time Guardrails](real-time-guardrails/) SDK.

📖 Docs: [Agent Ops](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/ai-control-plane/agent-ops/)
