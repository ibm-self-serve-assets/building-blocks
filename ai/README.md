# AI Control Plane

The **AI Control Plane** is a practical, composable foundation for building, controlling, and engineering enterprise AI systems. It brings together three groups of building blocks:

- **[Agents](agents/)** — build, orchestrate, and deploy autonomous AI agents that act across business systems.
- **[Control](control/)** — evaluate, observe, enforce policy on, and govern every agent and model in production, including cost and compliance.
- **[Engineering](engineering/)** — accelerate software delivery with IBM Bob, from new builds to legacy modernization and integration.

This repository is intentionally code-first. Each building block gives developers enough information to understand the pattern, identify the IBM products involved, find the runnable and reference assets, and get to the detailed setup instructions quickly.

📖 Full documentation: [AI Control Plane on the Building Blocks docs site](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/)

---

## Repository Map

| Group | Building Block | IBM Product Anchor | What You Can Build |
|---|---|---|---|
| **Agents** | [Agent Builder](agents/agent-builder/) | IBM watsonx Orchestrate ADK | Autonomous, task-driven AI agents with tools, knowledge bases, voice channels, and REST APIs |
| **Agents** | [Multi-Agent Orchestration](agents/multi-agent-orchestration/) | IBM watsonx Orchestrate, IBM watsonx.ai AI Gateway | Multi-agent collaboration, dynamic task delegation, shared context, and MCP/A2A integrations |
| **Control** | [Agent Ops](control/agent-ops/) | IBM watsonx Orchestrate, IBM watsonx.governance | Agent evaluation, red-teaming, failure analysis, traces, and latency |
| **Control** | [Guardrails](control/guardrails/) | IBM watsonx Orchestrate, IBM watsonx.governance | Runtime policy enforcement — Agent Controls and the Real-Time Guardrails SDK |
| **Control** | [Cost Management](control/cost-management/) | IBM watsonx Orchestrate (with Langfuse) | Token and dollar cost tracking for agents — per trace, session, model, and evaluation scenario — with context-growth analysis and production cost projection |
| **Control** | [Compliance](control/compliance/) | IBM watsonx.governance, IBM OpenPages | Use case inventory, regulation mapping, and Enforcement Tracking |
| **Engineering** | [Agentic SDLC](engineering/agentic-sdlc/) | IBM Bob | IDE-native agentic software development and full-lifecycle automation |
| **Engineering** | [Code Modernization](engineering/code-modernization/) | IBM Bob, watsonx Code Assistant | Automated legacy codebase refactoring, debt analysis, and Java/Maximo modernization |
| **Engineering** | [Headless Bob](engineering/headless-bob/) | IBM Bob Shell, Bobserver | Server-side and pipeline-driven autonomous execution via REST and MCP APIs |
| **Engineering** | [Integrate as Code](engineering/integrate-as-code/) | IBM iPaaS, watsonx Orchestrate | Enterprise integration flows, event-driven connectors, and automated iPaaS patterns |

---

## How to Use This Repository

Start at a building-block README and then move into the implementation you need:

```text
ai/                     # AI Control Plane
├── agents/             # watsonx Orchestrate agent authoring and multi-agent orchestration
├── control/            # Agent Ops, Guardrails, Cost Management, Compliance
└── engineering/        # IDE and headless agentic engineering, code modernization, and iPaaS
```

---

## IBM References

- IBM watsonx: https://www.ibm.com/watsonx
- IBM watsonx Orchestrate: https://www.ibm.com/products/watsonx-orchestrate
- IBM watsonx.governance: https://www.ibm.com/products/watsonx-governance
- IBM Bob: https://bob.ibm.com/
