# Gen AI Model Evaluation — Technical Assets

Production-ready Python scripts for evaluating generative AI applications using IBM watsonx governance.

## What's Inside

| Script | What It Does |
|--------|-------------|
| `01_rag_quality_evaluation.py` | Evaluate RAG pipelines for answer relevance, faithfulness, context relevance, retrieval precision, and NDCG |
| `02_content_safety_evaluation.py` | Screen AI inputs/outputs for HAP, PII, jailbreak, social bias, violence, and 10+ additional safety metrics |
| `03_llm_as_judge_evaluation.py` | Detect evasive responses and off-topic answers using LLM-as-judge and topic relevance metrics |
| `04_readability_and_operational.py` | Measure reading grade level and reading ease of generated text |
| `05_end_to_end_rag_with_eval.py` | Evaluate pre-computed RAG outputs for both quality and safety with a pass/fail deployment readiness check |

## Prerequisites

- Python >= 3.11
- IBM Cloud API key with access to watsonx governance
- `pip install -r requirements.txt`

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set credentials
export WATSONX_APIKEY="your-ibm-cloud-api-key"
export WATSONX_REGION="us-south"

# 3. Run any script
python 01_rag_quality_evaluation.py
```

## Metrics Reference

### RAG Quality (Script 01)
| Metric | What It Measures |
|--------|-----------------|
| Answer Relevance | Does the answer address the question? |
| Faithfulness | Is the answer grounded in the provided context? |
| Context Relevance | Is the retrieved context relevant to the question? |
| Answer Similarity | How similar is the answer to a reference/ground-truth? |
| Retrieval Precision | What fraction of retrieved chunks are relevant? |
| NDCG | Ranking quality of retrieved results |

### Content Safety (Script 02)
| Metric | What It Detects |
|--------|----------------|
| HAP | Hate, abuse, and profanity |
| PII | Personal data (names, emails, SSNs, phone numbers) |
| Jailbreak | Prompt injection / jailbreak attempts |
| Social Bias | Stereotyping, discrimination, biased language |
| Prompt Safety Risk | General risk score for input prompts |
| Violence, Profanity, Harm | Granular content category detection |

### Quality (Script 03)
| Metric | What It Measures |
|--------|-----------------|
| Evasiveness | Is the model dodging the question? |
| Topic Relevance | Is the response on-topic? (supports system prompt boundary) |

### Readability (Script 04)
| Metric | What It Measures |
|--------|-----------------|
| Text Grade Level | US school grade needed to understand the text |
| Text Reading Ease | Flesch Reading Ease score (0-100, higher = easier) |

## SDK Pattern

All scripts follow the same core pattern:

```python
from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.config import GenAIConfiguration
from ibm_watsonx_gov.metrics import AnswerRelevanceMetric, FaithfulnessMetric

# 1. Configure field mappings
config = GenAIConfiguration(
    input_fields=["question"],
    context_fields=["context"],
    output_fields=["generated_text"],
)

# 2. Choose metrics
metrics = [AnswerRelevanceMetric(), FaithfulnessMetric()]

# 3. Run evaluation
evaluator = MetricsEvaluator(configuration=config)
result = evaluator.evaluate(data=dataframe, metrics=metrics)

# 4. Read results
for metric in result.metrics_result:
    print(f"{metric.name}: {metric.mean:.4f}")
```
