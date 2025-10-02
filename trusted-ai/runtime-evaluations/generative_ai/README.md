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

Follow these steps to set up and run the Generative AI evaluation notebooks and the dashboard UI for runtime prompt evaluation using watsonx.governance.

#### Clone the git Repository
```
git clone https://github.com/ibm-self-serve-assets/building-blocks.git
cd building-blocks/trusted-ai/runtime-evaluations/generative_ai
```

a.)  Run Evaluation Notebooks

The notebooks are organized under the notebooks/ directory.

#### Prerequisites

1. Python 3.10+
2. Jupyter Notebook or JupyterLab
3. (Optional) Virtual environment recommended
```
python -m venv runtime
source runtime/bin/activate (or runtimse/Scripts/activate for windows)
```
4. following python package dependencies
```
pip install pandas transformers matplotlib seaborn jupyter
```
5. Launch Jupyter
```
cd notebooks
jupyter notebook
```
6. Open notebooks in the folders below to get started:
| Folder                                     | Description                                     |
| ------------------------------------------ | ----------------------------------------------- |
| `00-runtime-evaluation-realtime/`          | Manual prompt evaluation in real-time.          |
| `01-runtime-evaluation-scheduled/`         | Automated scheduled prompt evaluations.         |
| `02-custom-metrics-monitoring-deployment/` | Custom metrics setup and deployment monitoring. |
| `assets/`                                  | Sample datasets used for evaluation.            |

b.) The dashboard is a Streamlit app located in the dashboard-ui/ folder.

#### Prerequisites

1. Python 3.10+
2. streamlit
3. Install Dependencies
```
cd dashboard-ui
pip install -r requirements.txt
```
4. Launch the Dashboard
```
streamlit run app.py
```
5. The dashboard will open in your browser at http://localhost:8501
   
Note: Make sure evaluation outputs (e.g., CSVs from notebooks) are accessible by the dashboard or update paths in app.py accordingly.

---

## License

Licensing details are present in [LICENSE](LICENSE) file.

---

## References

1. https://github.com/IBM/watson-openscale-samples
2. https://client-docs.aiopenscale.cloud.ibm.com/html/index.html

---
