# IBM Building Blocks for AI Trust

Welcome to the **AI Trust** building blocks.  
This resource helps you get started on designing, building, and deploying AI systems that are reliable, transparent, secure, and compliant. These capabilities are powered by **IBM watsonx governance** and **IBM watsonx orchestrate**.

Building trust in AI requires a holistic approach across the full AI lifecycle — from model evaluation and agent operations to real-time safeguards and regulatory compliance. This repository provides frameworks, best practices, and tools to ensure your AI solutions are trustworthy and enterprise-ready.

---

## 📂 Repository Structure  

The content is organized into 4 main categories:  

![AI Trust Building Blocks](model-evaluation/gen-ai-evaluations/assets/evaluation-scripts/images/ai-trust-mapping.png)

### 1. **[Model Evaluation](model-evaluation/)**  
Evaluate your AI and ML models for a range of key metrics — performance quality, fairness, reliability, drift, bias, and more — throughout the AI lifecycle. Unvalidated systems fail at the edges: LLM pipelines can hallucinate, leak sensitive data, or degrade when upstream data changes. Model evaluation surfaces these issues and provides the evidence that regulatory frameworks like the EU AI Act and NIST AI RMF require.

- **Gen AI Evaluations** — RAG pipelines, LLM outputs, chatbot safety (quality, safety, readability metrics)
- **Predictive ML Evaluations** — traditional ML model scoring, confidence assessment, credit risk prediction

### 2. **[Agent Ops](agent-ops/)**  
AI agents don't behave like traditional software — they can respond differently every time. Agent Ops is a framework for testing, monitoring, and improving AI agents from development through production. Catch failures before deployment, automate testing with simulated users, and get full cost and performance visibility per interaction.

- **Evaluate** — simulate real users at scale to verify agents work as expected
- **Analyze** — pinpoint exactly where and why an agent went wrong
- **Quick-Eval** — fast sanity check without writing full test cases
- **Generate** — turn plain-English user stories into automated test scenarios
- **Red-Team** — stress-test agent security against 15 adversarial attack types
- **Observe** — track cost, latency, and token usage with full traceability

### 3. **[Real-Time Guardrails](real-time-guardrails/)**  
Enforce safety boundaries and operational constraints to keep your AI applications within desired behavior in production. Guardrails evaluate every AI input and output against configurable thresholds — blocking, flagging, or passing content before it reaches users. Production failures are visible and costly, and safety can't be solved at design time alone. Real-time guardrails provide the last line of defense.

- **Content Safety** — HAP, PII, jailbreak, social bias, violence detection (15 metrics)
- **RAG Quality** — faithfulness, answer relevance, context relevance checks
- **Custom Guardrails** — define your own LLM-as-judge criteria (completeness, conciseness, helpfulness)
- **Pipeline Integration** — end-to-end input → model → output guardrail pipeline with audit logging

### 4. **[AI Compliance](ai-compliance/)**  
AI regulations are multiplying fast and every AI use case may fall under different rules. Without a systematic approach, compliance becomes a bottleneck to deploying AI — or a risk if missed entirely. AI Compliance helps you map use cases to regulations, surface compliance gaps, and streamline assessment workflows.

- **Use Case Inventory** — create and manage AI use cases with compliance metadata using the IBM AI Governance Facts Client SDK
- **Governed Tool Catalog** — register, list, and manage AI tools in the watsonx governance tool catalog
- **OpenPages Governance Console** — regulation mapping, risk assessment, and position reporting via the integrated GRC platform

---

## 🚀 Getting Started  
1. Browse the category that best fits your needs — model evaluation, agent ops, guardrails, or compliance.  
2. Explore the `assets/` folder in each category for ready-to-use code samples and SDKs.  
3. Check `bob-modes/` for AI-assisted evaluation workflows (available for Model Evaluation and Agent Ops).  

---

## 🤝 Contributing  
We welcome contributions! Please submit issues, suggest improvements, or open pull requests to expand the resources and keep this repository valuable for all partners.
