# Control

Control is part of the **[AI Control Plane](../)**, alongside [Agents](../agents/) and [Engineering](../engineering/).

Running AI in production takes more than building agents — it takes continuous visibility and control across the full AI lifecycle: evaluating and observing agents, enforcing policies at runtime, managing cost, and proving regulatory compliance. These capabilities are powered by **IBM watsonx.governance** and **IBM watsonx Orchestrate**.

The Control building blocks provide frameworks, production-ready code samples, and tools to help you run AI that is reliable, transparent, and compliant.

![Control building blocks — Agent Ops, Guardrails, Cost Management, Compliance](images/control-architecture.png)

---

## 🧩 Building Blocks

| Building Block | What It Does | Status |
|---|---|---|
| **[Agent Ops](agent-ops/)** | Evaluate, observe, and optimize your AI agents throughout the lifecycle — benchmarking, red-teaming, failure analysis, traces, and latency | Available |
| **[Guardrails](guardrails/)** | Enforce runtime policy on agents, tools, and models — Agent Controls for watsonx Orchestrate, and the Real-Time Guardrails SDK with Pass/Flag/Block checks for any framework | Available |
| **[Cost Management](cost-management/)** | Track cost and token usage per agent interaction; enterprise allocation and budgets are coming soon | Partly available |
| **[Compliance](compliance/)** | Ensure your AI applications meet regulatory requirements and industry standards for responsible AI use — and prove it continuously with Enforcement Tracking | Available |

<!-- Hidden for now — restore this row to the table above:
| **[Lifecycle Management](lifecycle-management/)** | Manage AI models and agents across their full lifecycle, from onboarding to retirement | Coming soon |
-->

---

## 📂 Repository Structure

```text
ai/control/
├── agent-ops/                   # Agent Ops — evaluate, analyze, red-team, and observe agents
│   ├── assets/                  #   WXO ADK evaluation scripts + LangGraph evaluation SDK (wx_gov_agent_eval)
│   ├── bob-modes/               #   Agent Ops Bob mode
│   ├── bob-skills/              #   Agent Ops Bob skill
│   └── model-evaluation/        #   Build-time evaluation of GenAI apps, plus predictive ML scoring examples (+ Bob mode and skill)
├── guardrails/                  # Guardrails — Agent Controls guidance + Real-Time Guardrails SDK (+ Bob mode and skill)
├── cost-management/             # Cost Management — per-interaction cost and token tracking
└── compliance/                  # Compliance — use case inventory, governed tool catalog, OpenPages, Enforcement Tracking
```

### Which folder do I need?

| Stage | Folder | What you get |
|---|---|---|
| **Build time — evaluate** | [`agent-ops/`](agent-ops/) | Quick-eval, benchmark generation, LLM-simulated-user evaluation, failure analysis, and red-teaming for watsonx Orchestrate agents; a LangGraph/LangChain evaluation SDK |
| **Build time — evaluate** | [`agent-ops/model-evaluation/`](agent-ops/model-evaluation/) | Metric-level evaluation of GenAI applications (RAG, LLM outputs, chatbot safety) with watsonx.governance, plus predictive ML scoring examples |
| **Runtime — enforce** | [`guardrails/`](guardrails/) | Agent Controls for watsonx Orchestrate agents, and Pass/Flag/Block guardrails on input, retrieval, generation, and output for any framework |
| **Runtime — observe** | [`agent-ops/`](agent-ops/) | Traces of tool calls and routing, and latency per interaction |
| **Runtime — cost** | [`cost-management/`](cost-management/) | Cost and token usage per interaction and per evaluation scenario, with Langfuse |
| **Governance** | [`compliance/`](compliance/) | Regulation mapping, risk assessment, and continuous evidence from agent evaluations |

---

## 🤖 Bob Skills and Modes

| Skill / Mode | Type | Where |
|---|---|---|
| Agent Ops | Skill + Mode | [`agent-ops/bob-skills/`](agent-ops/bob-skills/), [`agent-ops/bob-modes/`](agent-ops/bob-modes/), [`ibm-bob/skills/agent-ops/`](../../ibm-bob/skills/agent-ops/) |
| Model Evaluation (Build-Time GenAI Evals) | Skill + Mode | [`agent-ops/model-evaluation/gen-ai-evaluations/bob-skills/`](agent-ops/model-evaluation/gen-ai-evaluations/bob-skills/), [`agent-ops/model-evaluation/gen-ai-evaluations/bob-modes/`](agent-ops/model-evaluation/gen-ai-evaluations/bob-modes/), [`ibm-bob/skills/build-time-gen-ai-evals/`](../../ibm-bob/skills/build-time-gen-ai-evals/) |
| Agent Controls | Skill | [Bob skills catalog on the docs site](https://ibm-self-serve-assets.github.io/building-blocks-docs/ibm-bob/skills/) |
| Real-Time Guardrails | Skill + Mode | [`guardrails/bob-skills/`](guardrails/bob-skills/), [`guardrails/bob-modes/`](guardrails/bob-modes/), [`ibm-bob/skills/real-time-guardrails/`](../../ibm-bob/skills/real-time-guardrails/) |

The Agent Ops skill also covers Langfuse cost analysis — see [Cost Management](cost-management/).

---

## 🚀 Getting Started

1. Choose the building block that matches your current need — Agent Ops to evaluate and observe, Guardrails to enforce policy at runtime, Cost Management to track spend, Compliance for regulatory mapping and evidence.
2. Explore the `assets/` folder in each building block for ready-to-use code samples and SDKs.
3. Check `bob-modes/` and `bob-skills/` for AI-assisted workflows that let Bob drive the work for you.

📖 Full documentation: [Control on the Building Blocks docs site](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/)

---

## 🤝 Contributing

We welcome contributions! Please submit issues, suggest improvements, or open pull requests to expand the resources and keep this repository valuable for all partners.
