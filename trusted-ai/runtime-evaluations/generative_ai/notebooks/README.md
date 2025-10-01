# Runtime Evaluation for Generative AI via Jupyter Notebook

This directory contains notebooks and assets related to prompt evaluation and custom metrics monitoring for production environments.

---

## Project Structure
```
.
├── 00-runtime-evaluation-realtime
│   └── Manual_Prompt_Evaluation_for_Production.ipynb
├── 01-runtime-evaluation-scheduled
│   └── Automated_Prompt_Evaluation_for_Production.ipynb
├── 02-custom-metrics-monitoring-deployment
│   └── Custom_Metrics_Monitoring_and_Deployment.ipynb
├── README.md
└── assets
    ├── RAG_data.csv
    └── summarisation.csv
```
---

## Notebooks Summary

| Notebook Name                                    | Description                                         |
|-------------------------------------------------|-----------------------------------------------------|
| [Manual_Prompt_Evaluation_for_Production.ipynb](00-runtime-evaluation-realtime/Manual_Prompt_Evaluation_for_Production.ipynb)  | Manual evaluation of prompts in real-time scenarios |
| [Automated_Prompt_Evaluation_for_Production.ipynb](01-runtime-evaluation-scheduled/Automated_Prompt_Evaluation_for_Production.ipynb) | Automated, scheduled evaluation of prompts          |
| [Custom_Metrics_Monitoring_and_Deployment.ipynb](02-custom-metrics-monitoring-deployment/Custom_Metrics_Monitoring_and_Deployment.ipynb)  | Custom metrics monitoring and deployment strategies |

---
## Prerequisites

1. Python3.10+
2. Jupyter Notebook Environment

---
## Getting Started

1. Clone the repository
   ```
   git clone https://github.com/ibm-self-serve-assets/building-blocks.git
   ```
2. Go to notebooks directory for runtime-evaluations
   ```
   cd building-blocks/trusted-ai/runtime-evaluations/generative_ai/notebooks
   ```
3. Launch notebooks as needed using Jupyter Notebook or JupyterLab.
   ```
   jupyter notebook
   ```  
---

## Data

The data files used by notebooks are stored in the **assets** folder.


