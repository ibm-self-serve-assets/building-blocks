# Building Block of Agents

## Overview

Welcome to the **Building Block of Agents**.  

This framework provides ready-to-use accelerators that make it easier to operationalize AI and GenAI use cases.

Each accelerator addresses a critical capability required to build, integrate, and scale AI-driven applications. These accelerators are designed to integrate seamlessly with enterprise systems, reducing time-to-value for AI projects. By standardizing agent creation, orchestration, and governance, the framework ensures scalability, trust, and efficiency across diverse workloads.

The Building Block of Agents includes:

- **Agent Builder** – to create and deploy agents  
- **AI Gateway** – to connect third-party and IBM models  
- **Multi-Agent Orchestration** – to coordinate agents, tools, and humans  

---

Here’s how the accelerators fit under the **Building Block of Agents**:

<img width="612" height="408" alt="Agents" src="https://github.com/user-attachments/assets/e89318a5-dc3c-4afb-b092-295fe21e0188" />

- **Agent Builder**  
- **AI Gateway**  
- **Multi-Agent Orchestration**

---

## Accelerators

### Agent Builder

The IBM watsonx Orchestrate Agent Development Kit (ADK) provides everything you need to build and deploy agents:

- Packaged as a **Python library** and **CLI tool**.  
- Enables you to configure agents that run on the **watsonx Orchestrate platform**.  
- Supports integrating agents and tools built on **other frameworks**.  
- Offers a **Developer Edition** for local builds and rapid iteration, allowing you to test and refine agents in isolation.  
- Once validated, agents can be seamlessly shared and deployed into a **production instance of watsonx Orchestrate** for team-wide use.  

---

### AI Gateway

The **AI Gateway** allows you to register and connect models from multiple providers in one central place.

- Supports external LLMs such as **OpenAI, Anthropic, Ollama, and watsonx.ai**.  
- Lets developers assign the most suitable model per agent without modifying code.  
- Provides a **unified integration layer** so every agent can flexibly use IBM and third-party models.  
- Simplifies governance and ensures **consistent model access management**.  

---

### Multi-Agent Orchestration

The **multi-agent orchestration engine** powers collaboration across:

- **AI agents**  
- **Business tools** (Salesforce, Workday, Microsoft Outlook, Slack, etc.)  
- **Human experts**  

Key capabilities:

- Powered by **fine-tuned LLMs** like **IBM Granite**.  
- Automates **complex workflows** by intelligently routing requests.  
- Centralizes interactions via a **single chat interface**.  
- Enables **proactive and autonomous collaboration** between AI and business processes.  
- Boosts productivity by cutting through complexity and keeping work moving efficiently.  

---

## Use Cases

- **Agent Builder** → Build an HR assistant that automates leave approvals using Workday APIs.  
- **AI Gateway** → Register both **watsonx.ai Granite models** and **OpenAI GPT** in one place, letting agents dynamically select the best LLM.  
- **Multi-Agent Orchestration** → Automate a **sales pipeline workflow** where Salesforce data, Outlook meetings, and Slack updates are coordinated across teams.  

---

## Getting Started

Clone this repository:

```bash
git clone https://github.com/your-org/building-block-agents.git
cd building-block-agents
```

Review the accelerators inside the repo:

- `agent-builder/`  
- `ai-gateway/`  
- `multi-agent-orchestration/`  

Follow the documentation in each folder to integrate the accelerator into your application.

---

## Contributing

We welcome contributions! Please fork this repo, create a feature branch, and open a pull request with your changes.

---

## License

This project is licensed under the [Apache 2.0 License](LICENSE).

