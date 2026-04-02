# Design-Time Evaluations

Evaluate your **Generative AI** and **Agentic AI** applications before deployment — using [Bob](https://bob.ibm.com) custom modes, IBM watsonx Orchestrate ADK, and IBM watsonx governance SDK.

## What's Here

| Directory | What it covers |
|-----------|---------------|
| [**agents-evaluations/**](agents-evaluations/) | WXO agent evaluation — automated benchmarks, tool-calling metrics, cost/latency analysis via Langfuse, and adversarial red-teaming |
| [**gen-ai-evaluations/**](gen-ai-evaluations/) | GenAI app evaluation — RAG quality, content safety, readability, agentic tool-call accuracy, and operational metrics via IBM watsonx governance |

Each directory contains **Bob modes** (custom modes for IBM's AI code assistant) that guide you through the evaluation workflow, plus any supporting tools (MCP servers, reference benchmarks).

## Prerequisites

- [Bob](https://bob.ibm.com) (IBM's AI code assistant — VSCode extension)
- IBM Cloud API key with access to the relevant services
- Python 3.12

See each directory's README for specific setup instructions.
