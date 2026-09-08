# Agents Building Blocks

Reusable implementation assets for **IBM watsonx Orchestrate** and **IBM Agentic AI**, organized across **Agent Builder** and **Multi-Agent Orchestration**.

This repository is structured code-first to help developers understand agent patterns, identify the IBM products involved, locate reference assets, and leverage IBM Bob modes and skills for guided acceleration.

---

## Repository Map

| Building block | IBM product anchor | What you can build |
|---|---|---|
| [Agent Builder](agent-builder/) | IBM watsonx Orchestrate Agentic Development Kit (ADK) | Autonomous, task-driven AI agents with tools, knowledge bases, voice channels, and REST APIs |
| [Multi-Agent Orchestration](multi-agent-orchestration/) | IBM watsonx Orchestrate, IBM watsonx.ai AI Gateway | Multi-agent collaboration, dynamic task delegation, shared context, and MCP/A2A integrations |

> **Note**: For agentic software development and engineering capabilities, refer to [AI Engineering](../ai-engineering/).

---

## How to Use This Repository

Start at a building-block README and then move into the implementation or guidance you need:

```text
<building-block>/
├── README.md        # Developer overview, architecture, quick start, guardrails
├── assets/          # Runnable / reference implementations and guides
├── bob-modes/       # IBM Bob custom modes (base-modes/ and custom-modes/)
└── bob-skills/      # IBM Bob skills references (pointing to building-blocks/ibm-bob/skills/)
```

A typical developer flow is:

1. Open the building-block [`README.md`](README.md) and confirm the capability matches your use case.
2. Review **Architecture / Flow** to understand the agent communication and tool boundaries.
3. Review **Included assets** and best practice guides.
4. Use **IBM Bob modes** under `bob-modes/` and **Bob skills** from [`building-blocks/ibm-bob/skills/`](../ibm-bob/skills/) to accelerate agent authoring, testing, and troubleshooting.
5. Validate target product configurations, IAM permissions, and regional availability before production deployment.

---

## Common Prerequisites

Most agent implementations and workflows expect:

- IBM Cloud account and provisioned **IBM watsonx Orchestrate** instance
- IBM Cloud IAM API Key: https://cloud.ibm.com/iam/apikeys
- Python 3.10+ / `uv` / Docker environment (as specified in individual asset guides)
- Service-specific credentials (e.g., watsonx Orchestrate instance URL, workspace ID, external API tokens)
- IBM Bob installed for mode and skill execution: https://bob.ibm.com/

Never commit API keys, service instance IDs, secret tokens, or populated `.env` files.

---

## IBM Bob Modes & Skills

- **Bob Modes**: Pre-configured developer modes with tailored permissions and instructions are located under `bob-modes/` in each building block folder.
- **Bob Skills**: Specialized domain skills are maintained centrally in [`building-blocks/ibm-bob/skills/`](../ibm-bob/skills/) (including `agent/` and `agent-ops/`).

---

## IBM References

- IBM watsonx Orchestrate: https://www.ibm.com/products/watsonx-orchestrate
- watsonx Orchestrate ADK Documentation: https://www.ibm.com/docs/en/watsonx/watson-orchestrate
- IBM watsonx.ai: https://www.ibm.com/products/watsonx-ai
- Model Context Protocol (MCP): https://modelcontextprotocol.io
