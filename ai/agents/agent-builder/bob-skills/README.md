# IBM Bob Skills for Agent Builder

Bob skills provide specialized capabilities and domain instructions for building, integrating, controlling, and operating AI agents on **IBM watsonx Orchestrate**.

All central IBM Bob skills are maintained in [`building-blocks/ibm-bob/skills/`](../../../ibm-bob/skills/).

---

## 📦 The Unified `agent` Skill

The core skill for watsonx Orchestrate is [`ibm-bob/skills/agent/`](../../../ibm-bob/skills/agent/), which unifies the full agent lifecycle across 6 progressive domains:

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

### Domain Breakdown

| Domain | Folder | What It Covers |
|---|---|---|
| **1 — Build** | [`1-build/`](../../../ibm-bob/skills/agent/1-build/) | Agents, Python `@tool` definitions, knowledge bases, connections, embedded chat |
| **2 — Orchestrate** | [`2-orchestrate/`](../../../ibm-bob/skills/agent/2-orchestrate/) | Multi-agent supervisor-worker patterns, AI Gateway, MCP servers, A2A protocol |
| **3 — Integrate** | [`3-integrate/`](../../../ibm-bob/skills/agent/3-integrate/) | REST API integration, IAM/JWT auth, async polling, Python & Node.js clients |
| **4 — Voice** | [`4-voice/`](../../../ibm-bob/skills/agent/4-voice/) | Voice agents, STT/TTS (Watson, Google, Azure), phone (Genesys), WhatsApp/SMS, Slack |
| **5 — Controls** | [`5-controls/`](../../../ibm-bob/skills/agent/5-controls/) | Policy controls — PII filter, guardrails, secrets detection, SQL sanitizer, rate limits, model resilience |
| **6 — Flows** | [`6-flows/`](../../../ibm-bob/skills/agent/6-flows/) | Agentic workflows — `@flow` decorator, 14 node types, forms, data mapping, doc processing, callbacks, MCP |

---

## 🚀 How to Use

For complete installation, configuration, and usage instructions for Bob skills and modes, see the official documentation:

👉 **[IBM Bob Skills & Modes Guide](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/bob-skills-and-modes/)**
