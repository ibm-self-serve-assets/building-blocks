---
groups:
  - id: agents
    name: Agents
    capability: ai
    description: Build, orchestrate, and deploy autonomous AI agents with the watsonx Orchestrate ADK and multi-agent patterns
  - id: control
    name: Control
    capability: ai
    description: Visibility and control across the AI lifecycle — Agent Ops (evaluate and observe), Guardrails (runtime enforcement), Cost Management, and Compliance, powered by watsonx.governance and watsonx Orchestrate
  - id: engineering
    name: Engineering
    capability: ai
    description: Bob-powered development layer across the software lifecycle — agentic SDLC, code modernization, headless Bob, and integration as code
  - id: streamhouse
    name: Streamhouse
    capability: data
    description: Data in motion on the Streamhouse — real-time streaming ingestion, stream transformation, governance, and serving live operational state so applications and agents act on current information
  - id: pipelines
    name: Pipelines
    capability: data
    description: Prepare, transform, move, and index structured and unstructured data for analytics, RAG, search, and AI applications
  - id: lakehouse
    name: Lakehouse
    capability: data
    description: Data at rest on the open lakehouse — metadata enrichment and data quality, data observability, zero-copy interoperability across engines, and serverless vector retrieval
  - id: operate
    name: Operate
    capability: automation
    description: Provision, configure, and schedule the infrastructure and workloads behind hybrid applications — Infrastructure as Code, configuration automation, workload orchestration, and asset management
  - id: secure
    name: Secure
    capability: automation
    description: Non-human identity and secrets management, application risk and continuous compliance, and quantum-safe cryptographic readiness
  - id: optimize
    name: Optimize
    capability: automation
    description: Observability, application performance, technology financial management and FinOps, and network health across hybrid cloud
---

# Groups

9 groups across the 3 core capabilities. Each building block belongs to exactly one group.
Group ids mirror the section folders of the docs site (`mkdocs.yml` nav in
[building-blocks-docs](https://github.com/ibm-self-serve-assets/building-blocks-docs)) and the
second-level folders of this repository (`ai/`, `data/`, `automation/`).
