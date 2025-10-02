# 🛡️ IBM Trusted AI: Runtime Evaluation

A Streamlit-based application that enables users to evaluate **LLM prompts in production** using **IBM Watsonx**, **Watson OpenScale**, and **Watsonx.governance**. 

This tool helps teams **configure**, **deploy**, and **monitor** large language model (LLM) prompts (e.g., for RAG or Summarization) with **metrics-based evaluation**, **payload logging**, and a live **evaluation dashboard**.

---

## 🔧 Features

- Save and manage **system prompts** via Streamlit UI.
- Publish prompts to **Watsonx.ai** as **detached prompt templates**.
- Create deployments for prompt evaluation in **Watsonx.ai**.
- Log payloads and configure **OpenScale** subscriptions for runtime metrics.
- Evaluate using metrics like:
  - Faithfulness
  - Unsuccessful Requests
  - Answer Relevance
  - Context Relevance
  - Answer Similarity
- Drift monitoring support (confidence, prediction, metadata drift).
- 📈 Evaluation Dashboard with charts.
- Factsheet generation and linking.
- Streaming LLM inference using `ModelInference`.

---

## Folder Structure

```plaintext
dashboard_ui
├── app.py                # Streamlit main app
├── config.yaml           # Configuration file for IBM Cloud credentials
└── README.md             # Doucmentation for streamlit application
```
---

## Getting Started

1. Clone the Repository
```
git clone https://github.com/ibm-self-serve-assets/building-blocks.git
cd building-blocks/trusted-ai/runtime-evaluations/generative_ai/dashboard_ui
```
2. Install Requirements
Ensure you're using Python 3.9+ and install the dependencies:
```
pip install -r requirements.txt
```
3. Create config.yaml

Create a config.yaml file in the root directory with your Watsonx and OpenScale credentials:
```
watsonx:
  api_key: "<your-ibm-cloud-api-key>"
  url: "https://us-south.ml.cloud.ibm.com"
  dataplatform_url: "https://dataplatform.cloud.ibm.com"
  project_id: "<your-project-id>"
  space_id: "<your-space-id>"

openscale:
  url: "https://us-south.ml.monitoring.cloud.ibm.com"
  service_instance_id: "<your-openscale-instance-id>"
```
4. Run streamlit application
```
streamlit run app.py
```
---

## How It Works

1. Prompt Creation & Deployment
   - Write a system prompt and LLM parameters (model, temp, etc.)
   - Save it to Watsonx as a detached prompt
   - Promote it to a space & deploy for evaluation
   - OpenScale monitors are automatically configured

2. **Runtime Evaluation**
   - Choose a deployed prompt
   - Enter context and question
   - Call Watsonx and log the generated response
   - Metrics are evaluated through OpenScale

3. **Evaluation Dashboard**
   - View charts for:
   - Generative AI quality metrics
   - Drift scores
   - Includes link to the Watsonx Factsheet

---

## Tech Stack

1. Streamlit
 — UI & Dashboard
2. IBM Watsonx.ai
 — Model Inference & Prompt Management
3. IBM Watson OpenScale
 — Monitoring & Quality Metrics
4. Watsonx.governance
 — Evaluation & Prompt Factsheets

---

## License

This project is licensed under the Apache 2.0 License


