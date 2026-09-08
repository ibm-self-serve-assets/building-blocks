# AI Building Blocks

Reusable implementation assets for **IBM Data and AI**, organized by **Agents**, **AI Engineering**, and **AI Trust**.

This repository is intentionally code-first. Each building block gives developers enough information to understand the pattern, identify the IBM products involved, find the runnable/reference assets, and get to the detailed setup instructions quickly.

---

## Repository Map

| Domain | Building Block | IBM Product Anchor | What You Can Build |
|---|---|---|---|
| **Agents** | [Agent Builder](agents/agent-builder/) | IBM watsonx Orchestrate ADK | Autonomous, task-driven AI agents with tools, knowledge bases, voice channels, and REST APIs |
| **Agents** | [Multi-Agent Orchestration](agents/multi-agent-orchestration/) | IBM watsonx Orchestrate, IBM watsonx.ai AI Gateway | Multi-agent collaboration, dynamic task delegation, shared context, and MCP/A2A integrations |
| **AI Engineering** | [Agentic SDLC](ai-engineering/agentic-sdlc/) | IBM Bob | IDE-native agentic software development and full-lifecycle automation |
| **AI Engineering** | [Code Modernization](ai-engineering/code-modernization/) | IBM Bob, watsonx Code Assistant | Automated legacy codebase refactoring, debt analysis, and Java/Maximo modernization |
| **AI Engineering** | [Headless Bob](ai-engineering/headless-bob/) | IBM Bob Shell, Bobserver | Server-side and pipeline-driven autonomous execution via REST and MCP APIs |
| **AI Engineering** | [Integrate as Code](ai-engineering/integrate-as-code/) | IBM iPaaS, watsonx Orchestrate | Enterprise integration flows, event-driven connectors, and automated iPaaS patterns |
| **AI Trust** | [AI Trust Overview](ai-trust/) | IBM watsonx.governance | Comprehensive governance, model evaluation, agent ops, and real-time guardrails |

---

## How to Use This Repository

Start at a building-block README and then move into the implementation you need:

```text
ai/
├── agents/             # watsonx Orchestrate agent authoring & multi-agent orchestration
├── ai-engineering/     # IDE and headless agentic engineering, code modernization, and iPaaS
└── ai-trust/           # watsonx.governance evaluations, real-time guardrails, and compliance
```

---

## IBM References

- IBM watsonx: https://www.ibm.com/watsonx
- IBM watsonx Orchestrate: https://www.ibm.com/products/watsonx-orchestrate
- IBM watsonx.governance: https://www.ibm.com/products/watsonx-governance
- IBM Bob: https://bob.ibm.com/
