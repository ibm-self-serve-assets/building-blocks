# Bob Modes for GenAI Evaluation

## What Are Bob Modes?

[Bob](https://bob.ibm.com) is IBM's AI code assistant. **Custom modes** extend Bob with domain-specific expertise — giving it specialized knowledge, workflows, and rules for a particular task. When you activate a mode, Bob becomes a guided expert in that domain rather than a general-purpose assistant.

A Bob mode is a `.bob/` folder containing:
- **Mode config** (`custom_modes.yaml`) — who Bob is in this mode, mandatory rules, and references
- **Workflow and rule files** — detailed phase-by-phase instructions Bob follows
- **MCP server config** — connects Bob to external tools and APIs

Drop the `.bob/` folder into your project, switch to the mode in Bob's mode selector, and Bob is ready to go.

## Modes in This Directory

### Base Modes

Production-ready modes maintained by the team.

| Mode | Description |
|------|-------------|
| [Build-time GenAI Evaluator](base-modes/) | Evaluate GenAI apps (RAG pipelines, LLM outputs, chatbot safety, AI agent tool-calling) before deployment using IBM watsonx governance metrics |

### Custom Modes

Community and experimental modes.

| Mode | Description |
|------|-------------|
| Coming soon | — |

## Prerequisites

All modes in this directory require:
- [Bob](https://bob.ibm.com) (IBM's AI code assistant — VSCode extension)
- `watsonx-gov` MCP server — bridges Bob to IBM watsonx governance APIs
- IBM Cloud API key with a provisioned watsonx.governance service instance

The `watsonx-gov` MCP server is included in the `build-time-evals-gen-ai.zip` download in `base-modes/`.

See each mode's README for detailed setup and usage instructions.
