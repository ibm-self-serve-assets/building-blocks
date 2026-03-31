# GenAI Evaluation — Bob Modes

Bob custom modes for evaluating GenAI applications before deployment using IBM watsonx governance.

## What Are Bob Modes?

Bob is a framework for creating custom AI assistant modes in Claude Code. Each mode bundles a role definition, workflow rules, and MCP server configuration into a `.bob/` directory that Claude Code picks up automatically.

## Modes in This Directory

### [`base-modes/`](./base-modes/)

**🧪 GenAI Build-Time Evaluator** (`gen-ai-build-time-eval`)

Guides you through build-time evaluation of RAG pipelines, LLM outputs, and AI agents using IBM watsonx governance metrics. Covers:

| App Type | Evaluation |
|---|---|
| RAG pipeline | Answer relevance, faithfulness, context relevance, retrieval precision |
| LLM / chatbot | HAP, PII, social bias detection |
| User input | Jailbreak detection, prompt safety risk |
| AI agent traces | Tool call accuracy, parameter accuracy, syntactic validity |

See [`base-modes/README.md`](./base-modes/README.md) for setup and usage instructions.

### [`custom-modes/`](./custom-modes/)

Project-specific extensions and customizations of the base modes. Coming soon.

## Prerequisites

All modes in this directory require:
- **watsonx-gov MCP server** — the MCP that bridges Claude Code to IBM watsonx governance APIs
- **IBM Cloud API key** with a provisioned watsonx.governance service instance

The watsonx-gov MCP server must be set up separately. Once set up, update `.bob/.mcp.json` in the mode directory with your installation path and API key.
