# Continuous Production-Grade Monitoring with IBM WatsonX Governance

This repository contains: 

- **Continuous Runtime Evaluations** for **Prompt Governance** in **Large Language Models (LLMs)** using the **IBM WatsonX Governance SDK**. 
- **Continuous Runtime Monitoring** for **Traditional AI Model Governance** 

These evaluations ensure that your AI models are compliant, transparent, and fair during their deployment in real-time.

---

## Technology Stack

- **Python 3.10+**
- **IBM watsonx.governance SDK**: for model governance, prompt evaluations, and monitoring.
- **IBM watsonx openscale SDK**: for model continuous monitoring and evaluation.
- **IBM Watson Machine Learning SDK**: for lifecycle governance and deployment space management
- **Jupyter Notebooks**: for interactive development and experimentation.
- **python-dotenv**: for managing environment configurations.
- **IBM Cloud SDK**: for authentication with IBM Cloud services.

---

## Prerequisites

Before you can start working with Runtime Evaluations for Prompt Governance, make sure you have the following:

### 1. **IBM WatsonX Governance Service Instance**
   - Create an instance of the **IBM WatsonX Governance** service via the [IBM Cloud Catalog](https://cloud.ibm.com/catalog) to access the necessary tools and APIs for prompt governance.

### 2. **IBM Cloud API Key**
   - Generate an **API Key** for authenticating with IBM Cloud using the [IBM Cloud API Key Generator](https://cloud.ibm.com/docs/account?topic=account-userapikey).

### 3. **Access to IBM WatsonX Governance Service**
   - Ensure you have appropriate access to the **watsonx.governance** service instance to monitor prompts, track model performance, and run evaluations.

---
## Project Structure

```
.
├── README.md
├── generative_ai
│   ├── LICENSE
│   ├── README.md
│   ├── dashboard-ui
│   │   ├── app.py
│   │   └── requirements.txt
│   └── notebooks
│       ├── 00-runtime-evaluation-realtime
│       │   ├── Manual_Prompt_Evaluation_for_Production.ipynb
│       │   └── README.md
│       ├── 01-runtime-evaluation-scheduled
│       │   ├── Automated_Prompt_Evaluation_for_Production.ipynb
│       │   └── README.md
│       ├── 02-custom-metrics-monitoring-deployment
│       │   ├── Custom_Metrics_Monitoring_and_Deployment.ipynb
│       │   └── README.md
│       ├── README.md
│       └── assets
│           ├── RAG_data.csv
│           └── summarisation.csv
└── traditional_ai
    └── notebooks
        ├── Custom_Monitors_and_Custom_Metrics_Deployment.ipynb
        ├── Fairness_Monitoring_with_Indirect_Bias_Mechanism.ipynb
        └── Model_Risk_Management.ipynb
```

---

# Repository Top-Level Overview

| Name             | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| [README.md](README.md)      | Root-level documentation for the repository.                               |
| [generative_ai](generative_ai/README.md)  | Contains generative AI workflows, notebooks, dashboards, and assets for prompt evaluation, monitoring, and custom metrics. |
| [traditional_ai](traditional_ai) | Contains traditional AI/ML workflows, notebooks for fairness, monitoring, and risk management. |

---

## References

1. https://github.com/IBM/watson-openscale-samples
2. https://client-docs.aiopenscale.cloud.ibm.com/html/index.html

---










