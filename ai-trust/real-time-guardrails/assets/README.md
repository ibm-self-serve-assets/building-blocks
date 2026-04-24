# Real-Time Guardrails — Technical Assets

Production-ready Python scripts for implementing real-time AI guardrails using IBM watsonx governance.

## What's Inside

| Script | What It Does |
|--------|-------------|
| `01_content_safety_guardrails.py` | Screen inputs/outputs for HAP, PII, jailbreak, social bias, violence with configurable BLOCK/FLAG/PASS thresholds |
| `02_rag_quality_guardrails.py` | Real-time RAG quality checks (faithfulness, relevance, context quality) with fallback responses |
| `03_custom_guardrails.py` | Define custom LLM-as-judge guardrails: answer completeness, conciseness, helpfulness |
| `04_guardrail_pipeline.py` | End-to-end pipeline: validate input → call model → validate output → return/block, with audit logging |

## Prerequisites

- Python >= 3.11
- IBM Cloud API key with access to watsonx governance
- For custom guardrails (script 03): watsonx governance project ID
- `pip install -r requirements.txt`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials
export WATSONX_APIKEY="your-ibm-cloud-api-key"
export WATSONX_REGION="us-south"
export WXG_PROJECT_ID="your-project-id"  # only for script 03

# 3. Run any script
python 01_content_safety_guardrails.py
```

## How Guardrails Work

```
User Input → [INPUT GUARDRAIL] → AI Model → [OUTPUT GUARDRAIL] → Response
                  │                                  │
                  ├─ BLOCK → Reject input            ├─ BLOCK → Fallback message
                  ├─ FLAG  → Allow + log             ├─ FLAG  → Allow + review
                  └─ PASS  → Continue                └─ PASS  → Serve response
```

## Guardrail Types

### Built-in Safety (Scripts 01, 02, 04)
Detects harmful content using pre-trained models — no additional setup needed.

| Guardrail | What It Catches |
|-----------|----------------|
| HAP | Hate speech, abuse, profanity |
| PII | Names, emails, SSNs, phone numbers, addresses |
| Jailbreak | Prompt injection and jailbreak attempts |
| Social Bias | Stereotyping and discriminatory language |
| Violence | Violent content |
| Faithfulness | Hallucinated content not grounded in context |
| Answer Relevance | Off-topic or irrelevant responses |

### Custom LLM-as-Judge (Script 03)
Define your own guardrail criteria using an LLM as evaluator. Two approaches:

1. **Prompt template** — full control over the evaluation prompt
2. **Criteria + Options** — structured rubric with named options and scores

### Pipeline Integration (Script 04)
Combines safety and quality guardrails into a single pipeline with:
- Input validation before model call
- Output validation before serving response
- Audit logging for compliance and review
