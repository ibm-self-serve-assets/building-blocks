# Real-Time Guardrails — Asset Tutorials

Four self-contained Python scripts that walk you through integrating
`real-time-guardrails` into your AI/RAG agent. Each script is runnable
standalone (`python 0X_*.py`) and uses curated test data from
[`sample_data/`](sample_data/).

The tutorials build on top of the production SDK in [`sdk/`](sdk/). Start
here for a guided walkthrough; consult [`sdk/README.md`](sdk/README.md) for
the full reference.

## What's Inside

| Script | What It Teaches |
|---|---|
| [`01_content_safety_guardrails.py`](01_content_safety_guardrails.py) | Input + output safety on 5 canned scenarios. Shows the 3-state Pass / Flag / Block action model and how to surface fallback messages. |
| [`02_rag_quality_guardrails.py`](02_rag_quality_guardrails.py) | RAG retrieval (multi-doc ranking) vs RAG generation (faithfulness on the LLM's answer). Two stages of a RAG pipeline. |
| [`03_custom_guardrails.py`](03_custom_guardrails.py) | Author custom LLM-as-judge metrics in both styles (`criteria + Option` for rubrics, `prompt_template` for full prompt control), then register them in the evaluator's registry. |
| [`04_guardrail_pipeline.py`](04_guardrail_pipeline.py) | End-to-end: `GuardrailedAgent` wrapping the 4 choke points (input → retrieval → generation → output) with built-in audit logging. The template you copy into production. |

## Prerequisites

- Python 3.11, 3.12, or 3.13 (IBM SDK chain doesn't yet support 3.14)
- IBM Cloud account + watsonx.governance instance
- *Optional*: watsonx.ai project (required only for LLM-as-judge metrics — scripts 03 and 04)

## Quick Start

```bash
# 1. Install the SDK (covers all four tutorials)
pip install -e ./sdk[all]

# 2. Configure credentials (don't paste the API key into chat history; use read -s)
cp ./sdk/.env.example ./.env
chmod 600 ./.env

# 3. Run any tutorial — they print scored results to stdout
python 01_content_safety_guardrails.py
python 02_rag_quality_guardrails.py
python 03_custom_guardrails.py   # needs WXG_PROJECT_ID
python 04_guardrail_pipeline.py  # needs WXG_PROJECT_ID
```

Once you've worked through the four tutorials, you're ready to wire the SDK
into your own agent. See [`sdk/README.md`](sdk/README.md) for the integration
patterns (library / REST / MCP) and the 28-metric catalog.

## Learning Path

1. **Tutorial 01** — get a feel for the SDK's API surface and the three-state
   action model on basic input/output safety.
2. **Tutorial 02** — see how RAG retrieval and RAG generation guardrails fit
   different stages of a RAG pipeline.
3. **Tutorial 03** — author your own LLM-as-judge metric when the 28-metric
   catalog doesn't cover a domain-specific concern.
4. **Tutorial 04** — assemble everything into a production-shaped pipeline
   class with audit logging.

## Want to See What's Under the Hood?

The SDK is a thin opinionated wrapper over [`ibm-watsonx-gov`](https://pypi.org/project/ibm-watsonx-gov/).
If you want to understand the raw IBM SDK calls our wrapper makes — useful
for debugging or for features we don't expose — see
[`under_the_hood.md`](under_the_hood.md) for side-by-side comparisons.
