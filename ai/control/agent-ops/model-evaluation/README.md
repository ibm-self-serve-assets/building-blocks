# Model Evaluation

Part of the **[Agent Ops](../)** building block in **[Control](../../)** — the build-time evaluation layer. Evaluate here before deployment; enforce at runtime with [Guardrails](../../guardrails/).

Evaluate generative AI applications — RAG pipelines, LLM outputs, and chatbot safety — with IBM watsonx.governance metrics before they reach production.

---

## Key Highlights

- Score **answer quality, faithfulness, retrieval quality, content safety, and readability** with IBM watsonx.governance metrics
- Catch hallucination, PII leakage, and unsafe responses before release, with reproducible scores you can keep as evidence
- Run the same checks from a script, from the SDK, or by letting Bob drive

## Solves For

- Inaccurate or ungrounded output
- Undesired GenAI behaviour
- No reproducible evidence of quality and safety before release
- Complexity of model selection and prompt approach (zero-shot, 1-shot, etc.)

---

## What's Inside

### [Gen AI Evaluations](gen-ai-evaluations/)

- [`assets/`](gen-ai-evaluations/assets/) — numbered evaluation scripts (RAG quality, content safety, LLM-as-judge, readability, end-to-end RAG with evaluation) and the `wx_gov_prompt_eval` SDK
- [`bob-modes/`](gen-ai-evaluations/bob-modes/) — the Build-time GenAI Evaluator Bob mode
- [`bob-skills/`](gen-ai-evaluations/bob-skills/) — the `build-time-gen-ai-evals` Bob skill, which also covers agentic tool-call evaluation

---

## Getting Started

1. Start with the scripts in [`gen-ai-evaluations/assets/`](gen-ai-evaluations/assets/); the folder README covers credentials and setup.
2. Let Bob drive with the mode in [`gen-ai-evaluations/bob-modes/`](gen-ai-evaluations/bob-modes/) or the skill in [`gen-ai-evaluations/bob-skills/`](gen-ai-evaluations/bob-skills/).

📖 Docs: [Model Evaluation](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/model-evaluation/) · [Agent Ops](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/agent-ops/)
