# IBM Bob Skills for Multi-Agent Orchestration

Bob skills provide specialized capabilities and domain instructions for coordinating multi-agent systems, designing agent flows, and operating agent workflows on **IBM watsonx Orchestrate**.

All central IBM Bob skills are maintained in [`building-blocks/ibm-bob/skills/`](../../ibm-bob/skills/).

---

## 📦 The Unified `agent` Skill

The core skill for watsonx Orchestrate is [`ibm-bob/skills/agent/`](../../ibm-bob/skills/agent/), which unifies multi-agent orchestration and workflow design:

```text
agent/
├── SKILL.md                        ← Unified skill entry point
├── README.md                       ← Skill guide & domain index
├── 1-build/                        ← Agent, tool, KB, connection development
├── 2-orchestrate/                  ← Multi-agent systems & cross-framework integrations
├── 3-integrate/                    ← REST API integration into apps
├── 4-voice/                        ← Voice agents & channel integrations
├── 5-controls/                     ← Policy controls (PII, guardrails, SQL, rate limits)
└── 6-flows/                        ← Agentic workflows — @flow decorator, all 14 node types
```

### Orchestration & Flow Domains

| Domain | Folder | What It Covers |
|---|---|---|
| **2 — Orchestrate** | [`2-orchestrate/`](../../ibm-bob/skills/agent/2-orchestrate/) | Dynamic task routing, supervisor-worker patterns, A2A protocol (v0.3.0), AI Gateway provider templates, MCP servers |
| **6 — Flows** | [`6-flows/`](../../ibm-bob/skills/agent/6-flows/) | Agentic workflows with `@flow` decorator — 14 node types, forms/userflow, parallel branches, loops, data mapping, doc processing, callbacks, MCP flow servers |
| **5 — Controls** | [`5-controls/`](../../ibm-bob/skills/agent/5-controls/) | Policy enforcement across multi-agent systems — model fallbacks, rate limiting, and output safety |

---

## 🚀 How to Use

For complete installation, configuration, and usage instructions for Bob skills and modes, see the official documentation:

👉 **[IBM Bob Skills & Modes Guide](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/bob-skills-and-modes/)**
