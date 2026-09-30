# Model Evaluation Bob Skills

Bob skill for **pre-deployment evaluation of GenAI applications** — RAG pipelines, LLM/chatbot outputs, AI agents with tool-calling, and **custom LLM-as-judge guardrails** — using IBM **watsonx.governance** metrics via the `ibm-watsonx-gov` Python SDK.

## Overview

The `build-time-gen-ai-evals` skill turns IBM Bob into a build-time evaluation assistant for generative AI apps. When you ask Bob to evaluate an app before shipping, it walks you through a 5-phase workflow — understand the app, prepare data in the exact SDK record shape, plan which metrics to run, execute the evaluation in-process, and interpret each score against its threshold with prioritized recommendations. The SDK runs locally; only the underlying watsonx.governance / watsonx.ai API calls hit IBM Cloud.

## Available Skills

| Skill | Zip | Use When |
|---|---|---|
| `build-time-gen-ai-evals` | [`build-time-gen-ai-evals.zip`](build-time-gen-ai-evals.zip) | Evaluating a GenAI app (RAG, LLM/chatbot, agentic tool-calling) against watsonx.governance metrics before deploy |

---

### `build-time-gen-ai-evals`

A five-phase, in-process evaluation workflow:

1. **Understand the app** — silently scan the workspace for code, data, and traces
2. **Data preparation** — show the exact SDK record shape before asking for data
3. **Evaluation planning** — map app type → metric classes, with a one-sentence rationale per metric
4. **Run evaluations** — call the `ibm-watsonx-gov` SDK in-process, with clear error handling
5. **Interpret + recommend** — every score against its threshold (✅ PASS / ❌ FAIL), with prioritized `[CRITICAL]` / `[WARNING]` / `[INFO]` recommendations

Partners install the SDK directly into a dedicated venv — **no MCP server, no hosted dependency, no Code Engine deployment.** Also supports **authoring custom LLM-as-judge metrics** for domain-specific guardrails the catalog doesn't cover.

---

## Installation

### Step 1 — Install the skill

The zip is pre-structured with `.bob/skills/<skill-folder>/` internally. Extract from your **project root**:

```bash
# From the root of your Bob workspace project
unzip build-time-gen-ai-evals.zip
```

This creates:

```
.bob/skills/build-time-gen-ai-evals/SKILL.md
```

(along with the skill's `reference/`, `examples/`, `assets/`, and `setup.sh`).

### Step 2 — Run the bundled setup script

The skill ships a `setup.sh` that creates a dedicated venv and installs the SDK with dependency-conflict fixes (don't install into your existing project venv):

```bash
bash .bob/skills/build-time-gen-ai-evals/setup.sh
```

### Step 3 — Enable in IBM Bob and verify

Open IBM Bob → Skills panel → enable `build-time-gen-ai-evals`, then ask Bob: *"What GenAI evaluation metrics can you run?"*

---

## Usage Examples

Once activated, you can ask Bob:

- *"Evaluate my RAG pipeline against this test set"*
- *"Screen my chatbot outputs for HAP and PII before we ship"*
- *"Gate my user inputs for jailbreak / prompt-injection risk"*
- *"My agent's tool-call accuracy dropped — help me figure out why"*
- *"I need a custom LLM-as-judge metric for compliance-citation accuracy — help me author it"*

---

## What Bob Can Help You Build

1. **RAG quality evaluation**: answer relevance, faithfulness, context relevance, retrieval precision
2. **Content safety screening**: HAP, PII, social bias on inputs and outputs
3. **Agentic evaluation**: tool-call accuracy from recorded traces
4. **Custom guardrails**: domain-specific LLM-as-judge metrics
5. **Dataset preparation & scoring**: records in the SDK's expected shape, scored against pass/fail thresholds

---

## Prerequisites

Before using this skill, ensure you have:

- **Python 3.11, 3.12, or 3.13** (3.14+ not yet supported by the SDK's wheels)
- **IBM Cloud** account with a **watsonx.governance** subscription
- `WATSONX_APIKEY` (IBM Cloud → Manage → Access (IAM) → API keys)
- `WATSONX_PROJECT_ID` or `WATSONX_SPACE_ID` — required for LLM-as-judge metrics (project/space must be WML-bound)
- Outbound HTTPS to `*.ml.cloud.ibm.com` + `iam.cloud.ibm.com`
- A **dedicated venv** (provisioned by the bundled `setup.sh`)

See [`.bob/skills/build-time-gen-ai-evals/assets/PREREQUISITES.md`](build-time-gen-ai-evals.zip) inside the zip for the full software, credentials, hardware, network, and troubleshooting details.

## Skill Capabilities Summary

| Capability | Description |
|---|---|
| **RAG quality** | Answer relevance, faithfulness, context relevance, retrieval precision, NDCG |
| **Content safety** | HAP, PII, jailbreak, social bias screening |
| **Agentic eval** | Tool-call accuracy from recorded traces |
| **Custom LLM-as-judge** | Author domain-specific guardrail metrics (`LLMAsJudgeMetric`) |
| **Threshold scoring** | Every metric scored ✅ PASS / ❌ FAIL against its threshold |
| **Local execution** | SDK runs in-process; only gov/ai API calls leave the machine |

## Troubleshooting

**Skill doesn't appear after installation:**
1. Verify `.bob/skills/build-time-gen-ai-evals/SKILL.md` exists
2. Restart Bob to refresh the skills list
3. Ensure the Skills button is enabled in your current mode

**LLM-as-judge metrics fail:**
1. Confirm `WATSONX_PROJECT_ID` (or `WATSONX_SPACE_ID`) is set and WML-bound
2. Verify the `[llmaj]` extra installed correctly (re-run `setup.sh`)

## Related

- [`../bob-modes/`](../bob-modes/) — Gen AI Evaluations Bob Modes
- [`../assets/`](../assets/) — Evaluation scripts and the `wx_gov_prompt_eval` SDK
- [`../../README.md`](../../README.md) — Model Evaluation building block overview
