# Build-Time GenAI Evaluations — Bob Skill

A Bob skill that drives **pre-deployment evaluation of GenAI applications** — RAG pipelines, LLM/chatbot outputs, AI agents with tool-calling, and **custom LLM-as-judge guardrails** — using IBM watsonx.governance metrics via the `ibm-watsonx-gov` Python SDK.

## What this skill does

When a developer says they want to evaluate a GenAI app before shipping, this skill walks them through a 5-phase workflow:

1. **Understand the app** — silently scan the workspace for code, data, traces
2. **Data preparation** — show exact SDK record shape BEFORE asking for data
3. **Evaluation planning** — map app type → metric classes, with one-sentence rationale per metric
4. **Run evaluations** — call the SDK in-process, handle errors with clear guidance
5. **Interpret + recommend** — every score against its threshold (✅ PASS / ❌ FAIL), with prioritized [CRITICAL]/[WARNING]/[INFO] recommendations

Partners install the `ibm-watsonx-gov` SDK directly into a dedicated venv and call it from Python. **No MCP server, no hosted dependency, no Code Engine deployment.** Evaluation runs locally; only the underlying watsonx.governance / watsonx.ai API calls hit IBM Cloud.

## When to use this skill

- Evaluating a RAG pipeline's output quality (relevance, faithfulness, context relevance)
- Screening LLM or chatbot outputs for HAP / PII / social bias before shipping
- Gating user inputs for jailbreak / prompt safety risk
- Evaluating AI agent tool-call accuracy from recorded traces
- **Authoring custom LLM-as-judge metrics** for domain-specific guardrails the catalog doesn't cover (e.g., *"does this answer correctly cite our compliance policy?"*)
- Preparing eval datasets in the SDK's expected shape
- Interpreting scores against pass/fail thresholds
- Producing prioritized fix recommendations

## When NOT to use this skill — see instead

- **Evaluate a watsonx Orchestrate agent end-to-end with benchmark scenarios + simulated users + red-teaming** → use the **agent-ops** skill. This skill (build-time-gen-ai-evals) is for batch evaluation of dataset records; agent-ops is for WXO-specific scenario-based evaluation with the ADK CLI.
- **Add runtime safety/quality guardrails to an AI agent in production** (4-choke-point Pass/Flag/Block enforcement per request) → use the **real-time-guardrails** skill. This skill scores a dataset BEFORE deploy; real-time-guardrails enforces per-request at runtime. Both skills share the underlying `ibm-watsonx-gov` SDK — patterns are interoperable.

| Skill | Lifecycle stage | Trigger |
|---|---|---|
| **build-time-gen-ai-evals** (this one) | Build-time (pre-deploy) | Dataset of inputs/outputs/traces ready to score |
| real-time-guardrails | Runtime (per-request) | Production traffic |
| agent-ops | Build-time (pre-deploy) | WXO agent ready for scenario-based validation |

## Prerequisites

- Python 3.11, 3.12, or 3.13 (3.14+ not yet supported by the SDK's wheel surface)
- IBM Cloud account with watsonx.governance subscription
- `WATSONX_APIKEY` (IBM Cloud → Manage → Access (IAM) → API keys → Create)
- `WATSONX_PROJECT_ID` or `WATSONX_SPACE_ID` (required for LLM-as-judge metrics; the project/space must be WML-bound)
- Outbound HTTPS to `*.ml.cloud.ibm.com` + `iam.cloud.ibm.com`
- A dedicated venv (the `setup.sh` script provisions this; don't install into your existing project venv)

Full prerequisites: `assets/PREREQUISITES.md`.

## What's in this skill

```
build-time-gen-ai-evals/
├── SKILL.md                       # Bob loads this on every invocation
├── README.md                      # this file (partner-facing overview)
├── USAGE-GUIDE.md                 # install + first-run walkthrough
├── setup.sh                       # one-command venv + dep pre-flight + SDK install
├── reference/                     # detailed knowledge, Bob loads on demand
│   ├── evaluation-workflow.md     # phase-by-phase workflow + SDK call patterns + LLM-as-judge authoring
│   └── metrics-reference.md       # all metric classes: definitions, thresholds, diagnoses, GenAIConfiguration fields
├── examples/                      # working record shape examples
│   ├── rag_quality_records.json
│   ├── safety_input_records.json
│   ├── safety_output_records.json
│   └── agentic_records.json
└── assets/
    └── PREREQUISITES.md           # software, credentials, hardware, network, troubleshooting
```

## Installing this skill

```bash
# 1. Drop the skill folder into your Bob skill directory
cp -r build-time-gen-ai-evals ~/your-repo/.bob/skills/

# 2. Run the bundled setup script (creates venv, installs SDK with dep-conflict fixes)
bash ~/your-repo/.bob/skills/build-time-gen-ai-evals/setup.sh

# 3. Open your project in Bob and start a conversation
```

Then ask Bob something like:

- *"Evaluate my RAG pipeline against this test set"*
- *"Screen my chatbot outputs for HAP and PII before we ship"*
- *"My agent's tool-call accuracy dropped — help me figure out why"*
- *"I have agent traces in `traces.jsonl` — how do I run tool-call eval?"*
- *"I need a custom LLM-as-judge metric for compliance citation accuracy — help me author it"*

## Architecture note: why partner-install (not a hosted MCP)

Earlier versions of this skill talked to a hosted MCP server on IBM Code Engine. We removed that path because:

1. **Portfolio consistency.** All three AI Trust skills (real-time-guardrails, agent-ops, this one) now follow the same shape: partner installs the SDK, configures auth, asks Bob.
2. **Data sovereignty.** Partner records stay on the partner's machine. The hosted MCP path required sending all records to a centralized endpoint.
3. **EU / JP / on-prem coverage.** The hosted MCP was US-South-only and didn't survive air-gap or data-residency constraints.
4. **Custom LLM-as-judge support.** The hosted MCP's install profile omitted the `[llmaj]` extra; custom LLM-judge authoring (`LLMAsJudgeMetric`, `LLMValidationMetric`) only works via direct SDK install.
5. **No operational liability.** No Code Engine deployment to maintain on behalf of partners.

If IBM ships an official, supported, multi-region MCP for watsonx.governance in the future, this skill can adopt it as an optional fast path. Today, partner-install is the only documented path.

## Source

This skill is derived from the [Build-Time GenAI Evaluations Bob mode](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/ai-trust/model-evaluation/gen-ai-evaluations) in the IBM Building Blocks portfolio. The underlying SDK is `ibm-watsonx-gov`. Source of truth for watsonx.governance: https://www.ibm.com/products/watsonx-governance.
