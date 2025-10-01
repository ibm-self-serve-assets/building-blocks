# Runtime Evaluation of Generative AI Prompts using Watsonx.governance

This repository contains assets, workflows, and notebooks to support the runtime evaluation of Generative AI prompts using IBM watsonx.governance. It is designed to help AI teams ensure trustworthy, compliant, and safe usage of large language models (LLMs) in regulated and enterprise environments.

---

## Overview

Generative AI models can exhibit unpredictable behavior at runtime. This project enables real-time prompt monitoring, evaluation, and governance using watsonx.governance capabilities. It includes:

1. Prompt logging and metadata capture
2. Policy-based runtime evaluation
3. Custom metric definition
4. Integration with watsonx.governance dashboards
5. Alerting and audit capabilities

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

## Module Structure
```
.
├── LICENSE
├── README.md
├── dashboard-ui
│   ├── app.py
│   └── requirements.txt
└── notebooks
    ├── 00-runtime-evaluation-realtime
    │   ├── Manual_Prompt_Evaluation_for_Production.ipynb
    │   └── README.md
    ├── 01-runtime-evaluation-scheduled
    │   ├── Automated_Prompt_Evaluation_for_Production.ipynb
    │   └── README.md
    ├── 02-custom-metrics-monitoring-deployment
    │   ├── Custom_Metrics_Monitoring_and_Deployment.ipynb
    │   └── README.md
    ├── README.md
    └── assets
        ├── RAG_data.csv
        └── summarisation.csv
```

---

## File Description

| Path                                           | Description                                                               |
| ---------------------------------------------- | ------------------------------------------------------------------------- |
| [LICENSE](LICENSE)                                     | Project license file.                                                     |
| [README.md](README.md)                                    | Root-level documentation for the repository.                              |
| [dashboard-ui](dashboard-ui)                                | Contains the interactive Streamlit dashboard for visualizing evaluations. |
|     [app.py](app.py)                                   | Streamlit app for dashboard UI.                                           |
|     [requirements.txt](requirements.txt)                         | Python dependencies for the dashboard.                                    |
| [notebooks](notebooks)                                   | Collection of Jupyter notebooks for evaluation workflows.                 |
|     [00-runtime-evaluation-realtime](00-runtime-evaluation-realtime)          | Manual, real-time prompt evaluation notebook.                             |
|     [01-runtime-evaluation-scheduled](01-runtime-evaluation-scheduled)        | Scheduled, automated prompt evaluation workflow.                          |
|     [02-custom-metrics-monitoring-deployment](02-custom-metrics-monitoring-deployment)  | Custom metrics setup and deployment monitoring.                           |
| [README.md](README.md)                                | Overview of the notebooks and structure.                                  |
| [assets](assets)                                  | CSV files used for evaluation (e.g., RAG and summarization datasets).     |

---

## Getting Started

1. Clone the git repo
2. Go to directory
3. notebooks
4. dashboard-ui

---

## License

Licensing details are present in [LICENSE](LICENSE) file.

---

## References

1. https://github.com/IBM/watson-openscale-samples
2. https://client-docs.aiopenscale.cloud.ibm.com/html/index.html

---
