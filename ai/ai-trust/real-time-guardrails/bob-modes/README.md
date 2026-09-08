# Bob Modes for Real-Time Guardrails

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
| [Real-Time Guardrails](base-modes/) | Wire IBM watsonx.governance-backed guardrails into an AI/RAG agent across **4 choke points** (input safety, retrieval quality, generation faithfulness, output compliance) with a **3-state Pass/Flag/Block** action model, audit logging, and threshold policy as code. Bob picks metrics from a **28-metric catalog**, tunes thresholds against your sample workload, wires the right auto-trigger (HTTP middleware / Python decorator / framework callback / watsonx Orchestrate tool wrap / service middleware / frontend BFF), and enforces **19 mandatory rules** covering credential hygiene, threshold precedence, never-bypass-a-Block, and partner-boundary integration for managed-agent topologies. |

## Prerequisites

All modes in this directory require:
- [Bob](https://bob.ibm.com) (IBM's AI code assistant)
- Python 3.11, 3.12, or 3.13 (**not** 3.14 — the IBM SDK chain doesn't support it yet)
- IBM Cloud account with a **watsonx.governance** subscription
- The `real-time-guardrails` package with the `[all]` extra:
  ```bash
  pip install "real-time-guardrails[all]"
  ```
  The `[all]` extra is mandatory — without `[metrics,llmaj]`, the registry build fails with `ModuleNotFoundError: No module named 'unitxt'`.
- A `.env` file (chmod 600) with `WATSONX_APIKEY` and `WXG_SERVICE_INSTANCE_ID`. `WXG_PROJECT_ID` (a watsonx.ai project ID) is optional — it unlocks the 3 LLM-as-judge metrics; without it you still get 25 of the 28 catalog metrics.

See each mode's README for additional prerequisites and installation instructions.
