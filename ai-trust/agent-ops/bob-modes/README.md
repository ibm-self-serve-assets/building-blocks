# Bob Modes for Agent Evaluation

## What Are Bob Modes?

[Bob](https://bob.ibm.com) is IBM's AI code assistant. **Custom modes** extend Bob with domain-specific expertise — giving it specialized knowledge, workflows, and rules for a particular task. When you activate a mode, Bob becomes a guided expert in that domain rather than a general-purpose assistant.

A Bob mode is a `.bob/` folder containing:
- **Mode config** (`custom_modes.yaml`) — who Bob is in this mode, mandatory rules, and references
- **Workflow and rule files** — detailed phase-by-phase instructions Bob follows
- **Reference examples** — working artifacts Bob uses as templates

Drop the `.bob/` folder into your project, switch to the mode in Bob's mode selector, and Bob is ready to go.

## Modes in This Directory

### Base Modes

Production-ready modes maintained by the team.

| Mode | Description |
|------|-------------|
| [Build-time AgentOps Evaluator](base-modes/) | Evaluate WXO agents before deployment — automated benchmarks, metrics analysis, cost/latency tracking via Langfuse, and adversarial red-teaming across 15 attack vectors |

### Custom Modes

Community and experimental modes.

| Mode | Description |
|------|-------------|
| Coming soon | — |

## Prerequisites

All modes in this directory require:
- [Bob](https://bob.ibm.com) (IBM's AI code assistant)
- WXO Developer Edition (local server on port 8080)
- IBM watsonx Orchestrate ADK (2.5.1 or 2.6.x — **not** 2.7.0):
  ```bash
  pip install "ibm-watsonx-orchestrate[agentops]>=2.5.1,<2.7.0"
  pip install "ibm-watsonx-orchestrate-evaluation-framework==1.2.7"
  pip install "langfuse<4"
  ```
- Python 3.12 (3.11 and lower are not supported)

See each mode's README for additional prerequisites and installation instructions.
