# Best Practices for IBM watsonx Code Assistant Building Blocks Development

This document lists best practices for building demos with **IBM watsonx Code Assistant** in combination with:

- **Agentic AI** → watsonx.orchestrate  
- **Governance** → watsonx.governance  
- **Data for AI** → watsonx.data & watsonx.ai  

---

## Best Practices

### 1. Demo Design & Storyboarding
- Define **end-to-end use case flow** (problem → orchestration → governance → AI output).  
- Keep the demo **modular** so each component (code assistant, orchestrate, governance, data/AI) can be shown independently or in combination.  
- Maintain **realistic but synthetic data** for compliance and reproducibility.  

### 2. Code Assistant Development
- Use **watsonx Code Assistant** for generating boilerplate code and automating repetitive tasks.  
- Always review, refine, and annotate generated code with comments — highlight AI contributions for building blocks clarity.  
- Include **before/after code examples** to showcase productivity gains.  
- Enforce **coding standards, linting, and formatting** in the repo.  

### 3. Agentic AI with watsonx.orchestrate
- Wrap code assistant workflows in orchestrate agents for **step-by-step automation**.  
- Configure **least-privilege access** for agents (restricted APIs, data).  
- Add **human-in-the-loop approvals** for critical steps (e.g., deployment).  
- Use orchestration to **chain tasks** (e.g., generate code → validate → deploy to sandbox).  

### 4. Governance with watsonx.governance
- Register demo datasets, models, and generated artifacts in **watsonx.governance**.  
- Track **lineage** → which model/code/data produced which output.  
- Apply **bias/fairness checks** for demo outputs (when applicable).  
- Set up **policy-as-code** to show automated gates (only deploy if governance criteria are met).  

### 5. Data & AI with watsonx.data + watsonx.ai
- Use watsonx.data for **cataloging, schema validation, and query federation** in demos.  
- Ensure **dataset versioning** for repeatability.  
- For watsonx.ai:  
  - Use clear prompts and prompt templates.  
  - Demonstrate fine-tuning or RAG (retrieval-augmented generation) using watsonx.data sources.  
  - Capture latency and cost metrics for transparency.  
 
### 6. Documentation & Demo Usability
- Provide a **README walkthrough** with step-by-step demo instructions.  
- Add **screenshots or recordings** for offline reference.  
- Clearly mark **AI-generated code vs manually written code** in the repo.  
- Provide a **troubleshooting guide** for setup errors.  

---

## 📂 Recommended Folder Structure

A practical folder layout for demos:

```
/watsonx-code-assistant-demo
├── README.md # Demo overview & quickstart
├── LICENSE
├── .gitignore
│
├── /docs
│ ├── architecture-diagram.png
│ ├── demo-script.md # Narration / flow
│ └── troubleshooting.md
│
├── /infra
│ ├── terraform/ # Infra as Code for demo env
│ └── k8s/ # K8s manifests (if needed)
│
├── /orchestrate
│ ├── agents/
│ │ ├── codegen-agent/
│ │ │ ├── agent.yaml # agent definition
│ │ │ └── src/ # orchestration logic
│ │ └── deploy-agent/
│ │ ├── agent.yaml
│ │ └── src/
│ └── tests/
│
├── /governance
│ ├── policies/ # policy-as-code YAMLs
│ ├── lineage-examples/ # lineage registration files
│ └── monitoring/ # drift/bias checks
│
├── /data
│ ├── schemas/ # JSONSchema/Avro
│ ├── sample/ # synthetic datasets
│ └── catalog/ # watsonx.data metadata
│
├── /models
│ ├── prompts/ # prompt templates
│ ├── fine-tuning/ # fine-tuning scripts
│ └── registry.yaml # governance metadata
│
├── /assistant
│ ├── before-after/ # before vs AI-generated code
│ ├── src/ # code assistant outputs
│ └── tests/ # unit & integration tests
│
├── /ci
│ ├── pipelines/ # CI/CD workflows
│ └── scripts/ # helper scripts
│
└── /tests
├── e2e/ # full demo flow tests
├── integration/
└── performance/