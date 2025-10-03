# Secure your AI Gateway with IBM Guardium AI Security

---

## ✨ Overview
This repository provides:
- A **Streamlit chatbot application** (WIP) for interacting with LLMs through Guardium AI Gateway.  
- A **notebook and supporting Python scripts** to test different LLM providers and experiment with Gateway rules via the CLI.

---

## 🚀 Features
- Run a chatbot UI powered by Streamlit.
- Select an LLM provider and route requests through the Guardium Gateway.
- Experiment with rule enforcement via CLI using `openai-via-proxy.ipynb`.
- Explore configuration with `.env` variables.

---

## 📂 Project Structure
```text
.
├── app/
│   └── main.py          # Streamlit chatbot app
├── notebooks/
│   └── openai-via-proxy.ipynb  # Experiment with LLM Gateway rules
├── requirements.txt
├── .env.example
└── README.md

