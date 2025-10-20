# Design Time Evaluations for Agentic AI Solutions

This folder contains self-serve notebooks for comprehensive evaluation and monitoring of Agentic AI solutions using IBM watsonx.governance SDK.

## Prerequisites

1. **IBM watsonx.governance Service Instance**  
   - Create an instance at [IBM Cloud Catalog](https://cloud.ibm.com/catalog/services/watsonxgovernance)

2. **IBM Cloud API Key**  
   - Generate at [IBM Cloud API Keys](https://cloud.ibm.com/iam/apikeys)  
   - Requires access to watsonx.governance service

---

## Technology Stack

- **Python 3.11+**
- **IBM watsonx.governance SDK**
- **Jupyter Notebooks** for interactive development
- **python-dotenv** for environment configuration
- **IBM Cloud SDK** for authentication

---

## 📚 Table of Contents
- [Basic AI Agents Evaluation](#basic-ai-agents-evaluation)
- [Tool Calling Evaluation of Agents](#tool-calling-evaluation-of-agents)
- [Advanced Design-Time Evaluation of Agents](#advanced-design-time-evaluation-of-agents)

---

## Basic AI Agents Evaluation

In *basic-design-time-eval-for-agents* notebook, you will create a LangGraph RAG agent and use watsonx Agentic AI evaluator to evaluate the agent’s performance.

<p align="center">
  <img src="../images/Basic_Agent.png" width="14%"/>
</p>

**Metrics evaluated:**
- Answer similarity
- Context relevance
- Faithfulness
- Retrieval latency
- Generation latency
- Interaction cost
- Interaction duration
- Input token count
- Output token count

---

## Tool Calling Evaluation of Agents

In *design-time-eval-for-agentic-toolCalling* notebook, you will create a question answering agent that is equipped with two custom tools. Given the user’s query, an LLM routes it to the relevant tool. If there is not a relevant tool to answer that question, the agent will generate without a tool. 

<p align="center">
  <img src="../images/Tool Calling_Agent.png" width="20%"/>
</p>

We will use the Agentic AI evaluators from IBM watsonx.governance Python SDK to evaluate the tool calling functionality of the agent.

**Metrics evaluated:**
- Tool call accuracy
- Tool call relevance
- Tool call latency

---

## Advanced Design-Time Evaluation of Agents

In *advanced-design-time-eval-for-agents* notebook, we first create a question answering agent that can use local documents or web search to answer the question. The agent will use context relevance to decide which tool to apply. 

<p align="center">
  <img src="../images/Advanced_Agent.png" width="30%"/>
</p>

We then use the Agentic AI evaluators from IBM watsonx.governance Python SDK to evaluate this agent.

**Metrics evaluated:**
- Retrieval context relevance
- Web search context relevance
- Retrieval precision
- Web search precision
- PII
- HAP
- HARM
- Jailbreak
- Sexual content
- Latency
- Cost
