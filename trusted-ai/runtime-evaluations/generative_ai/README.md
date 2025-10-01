#Runtime Evaluation of Generative AI Prompts using Watsonx.governance

This repository contains assets, workflows, and notebooks to support the runtime evaluation of Generative AI prompts using IBM watsonx.governance. It is designed to help AI teams ensure trustworthy, compliant, and safe usage of large language models (LLMs) in regulated and enterprise environments.

## Overview

Generative AI models can exhibit unpredictable behavior at runtime. This project enables real-time prompt monitoring, evaluation, and governance using watsonx.governance capabilities. It includes:

---

## Prompt logging and metadata capture
1. Policy-based runtime evaluation
2. Custom metric definition
3. Integration with watsonx.governance dashboards
4. Alerting and audit capabilities

---

## Features
1. Real-time Prompt Evaluation: Evaluate LLM prompts and responses as they are processed.
2. Custom Governance Metrics: Define and compute domain-specific quality and risk metrics.
3. Policy Enforcement: Apply business rules, usage guidelines, and compliance policies.
4. Watsonx.governance Integration: Seamless integration with the watsonx.governance platform for logging, dashboards, and audits.
5. Model Agnostic: Can be integrated with any LLM provider (OpenAI, Anthropic, Meta, IBM Granite, etc.).

---

## Design-time vs Runtime Metrics for GenAI Use Cases  


| **Use Case**               | **Design-time Metrics**                                                                                                                  | **Runtime Metrics**                                                                                                                       |
|----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------|
| **Text Summarization**     | - ROUGE (1, 2, L)  <br> - SARI  <br> - METEOR <br> - Readability scores <br> - Sentence similarity                                       | - ROUGE/SARI drift <br> - Input/output similarity changes <br> - Latency, token count <br> - Policy violations (PII, HAP)                |
| **Content Generation**     | - BLEU, METEOR <br> - Novelty/diversity (e.g., self-BLEU) <br> - Perplexity <br> - Fluency/coherence ratings                             | - Degradation in BLEU/similarity <br> - Safety violations (toxicity, PII) <br> - Failed generations <br> - Latency, throughput           |
| **Question Answering (QA)**| - F1 score <br> - Exact Match <br> - ROUGE <br> - Faithfulness <br> - Relevance scoring                                                  | - Decline in F1/EM <br> - Hallucination rate <br> - Irrelevant/empty answers <br> - Response time <br> - Output violations               |
| **Entity Extraction**      | - Precision, Recall, F1 <br> - Span-level accuracy                                                                                        | - Drop in entity detection accuracy <br> - Latency <br> - PII in extracted text                                                          |
| **RAG (Retrieval-Augmented Generation)** | - Retrieval recall@k <br> - nDCG <br> - Faithfulness <br> - ROUGE (answer quality)                                 | - Retrieval drift <br> - Faithfulness decline <br> - Failed retrievals <br> - Latency, policy violations                                |
| **Code Generation**        | - CodeBLEU <br> - Syntax correctness <br> - Unit test pass rate                                                                           | - Code execution failures <br> - Unsafe/insecure patterns <br> - Latency, hallucinated code blocks                                      |
| **General Governance & Health** | —                                                                                                                           | - Latency, throughput <br> - Input/output token volume <br> - Embedding drift <br> - Metadata drift <br> - Alerts, error rates           |

---
## Prerequisites

1. Python 3.10 +
2. ibm-watsonx-governance SDK
3. ibm-openscale SDK
4. ibm-watson-machine-learning SDK
5. Jupyter Notebook or VS Code

---
## Getting Started

---

