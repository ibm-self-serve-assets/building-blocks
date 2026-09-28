# AI Compliance

Part of the **[AI Control Plane](../)** building blocks.

AI regulations are multiplying fast and every AI use case may fall under different rules. Without a systematic approach, compliance becomes a bottleneck to deploying AI — or a risk if missed entirely.

---

## Key Highlights

- **Map AI use cases to global regulations** — compliance plans identify which rules apply by use case and region
- **Position reporting** surfaces potential compliance gaps across the enterprise
- **Configurable assessment workflows** streamline the review cycle for use case owners and compliance teams
- **Enforcement tracking** automatically captures agent evaluation metrics as governance evidence and tracks pass/breach results against policy thresholds

## Solves For

- Lack of clear mapping between AI use cases and applicable regulations
- Hidden compliance gaps across the enterprise
- Slow and costly re-assessment every time regulations change
- Slow compliance review delays AI deployment
- Compliance on paper but not in production — approved use cases whose deployed agents drift out of policy

---

## Two Layers: Policy and Proof

| Layer | What It Answers | Evidence |
|---|---|---|
| **Policy — Governance Console (OpenPages)** | Which regulations apply? What are the risks? Who assessed and approved? | Human-generated and periodic: risk assessments, questionnaires, attestations, sign-offs |
| **Proof — Enforcement Tracking** | Is the deployed AI actually behaving within the defined policies? | Machine-generated and continuous: agent evaluation metrics scored as pass/breach against control thresholds |

The two compose into a closed loop: controls are defined and mapped to regulations in the Governance Console, Enforcement Tracking supplies the operational evidence that those controls are holding, and breaches surface back into governance workflows for teams to act on.

## Enforcement Tracking for watsonx Orchestrate

**Enforcement Tracking** connects agent evaluations from watsonx Orchestrate directly to governance controls in watsonx.governance, turning documented policy into continuous, evidence-backed verification.

1. **Connect operational AI to governance controls** — link watsonx Orchestrate to watsonx.governance, then associate each agent with the governance use cases and controls it must satisfy.
2. **Continuously collect evidence of enforcement** — evaluation metrics such as hallucination, helpfulness, and toxicity are captured automatically and stored as governance evidence (on a schedule in production, on demand in development).
3. **Verify controls with automated pass and breach tracking** — collected metrics are checked against business-defined thresholds and each result is recorded as a pass or breach in watsonx.governance.

The evaluation metrics come from [Agent Ops](../agent-ops/) — see that building block for how watsonx Orchestrate agents are evaluated, red-teamed, and observed.

- [Announcement: From governance policies to governance proof with Enforcement Tracking](https://www.ibm.com/new/announcements/from-governance-policies-to-governance-proof-with-enforcement-tracking-for-watsonx-orchestrate)
- [Documentation: Configuring metrics synchronization for watsonx Orchestrate agents](https://www.ibm.com/docs/en/watsonx/saas?topic=console-configuring-metrics-synchronization-watsonx-orchestrate-agents)

---

## What's Inside

### [Assets](assets/)

| Script | What It Does |
|---|---|
| [`01_use_case_inventory.py`](assets/01_use_case_inventory.py) | Create and manage AI use cases in the watsonx governance inventory, add compliance metadata (risk level, regulations, ownership) using the IBM AI Governance Facts Client SDK |
| [`02_governed_tool_management.py`](assets/02_governed_tool_management.py) | Register, list, and manage AI tools in the watsonx governance tool catalog |

Sample data lives in [`assets/sample_data/`](assets/sample_data/); setup instructions are in [`assets/README.md`](assets/README.md).

### Compliance Workflows (OpenPages Governance Console)

For full compliance lifecycle management — regulation mapping, risk assessment, and position reporting — use the **IBM OpenPages Governance Console** integrated with watsonx governance.

| Workflow | What It Does |
|---|---|
| **Regulatory Compliance Management** | Map AI use cases to regulations (EU AI Act, NIST AI RMF), track regulatory changes |
| **Risk Identification & Assessment** | Run risk assessments with configurable questionnaires |
| **Position Reporting** | Dashboard-based visibility into compliance posture across the enterprise |
| **AI Risk Atlas** | Built-in guide to AI risks for planning risk mitigation |

Setup: provision an OpenPages instance with the "Model Risk Governance" solution, integrate it with watsonx governance (API key + fixed URL), load the solution files (questionnaire templates, risk atlas content, sample AI mandates), then create AI use cases in the Governance Console.

- [Integrating watsonx governance with OpenPages](https://www.ibm.com/docs/en/openpages/9.2.0?topic=governance-integrating-watsonxgovernance)
- [Managing risk with Governance Console](https://dataplatform.cloud.ibm.com/docs/content/svc-watsonxgov/wxgov-console.html?context=wx)
- [Creating use cases in Governance Console](https://dataplatform.cloud.ibm.com/docs/content/svc-watsonxgov/wxgov-model-use-cases.html?context=wx)
- [IBM AI Governance Facts Client samples](https://github.com/IBM/ai-governance-factsheet-samples)

---

## Getting Started
1. Follow [`assets/README.md`](assets/README.md) to configure credentials and run the use case inventory script.
2. Register the tools your agents use with the governed tool catalog script.
3. Connect watsonx Orchestrate to watsonx.governance and enable Enforcement Tracking so evaluation results from [Agent Ops](../agent-ops/) flow in as evidence.

📖 Docs: [AI Compliance](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/ai-control-plane/ai-compliance/)
