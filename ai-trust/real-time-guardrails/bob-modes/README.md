# Real-Time Guardrails — Bob Modes

AI-assisted modes for IBM Bob that guide developers through integrating real-time guardrails into their AI applications.

## What's a Bob Mode?

A Bob Mode is a packaged expertise file (`.bob/` folder) that turns IBM Bob into a domain-specific expert. When activated, Bob loads the mode's mandatory rules, follows its workflow phases, and references its working examples — so partners get expert-level guidance for the domain without anyone manually writing prompts.

## Base Modes

### 🛡️ [Real-Time Guardrails](base-modes/real-time-guardrails/)

End-to-end developer guide for adding `real-time-guardrails` to an AI/RAG agent. Bob walks the developer through **5 phases**:

1. **Setup & Verify** — provision IBM Cloud services, set credentials safely, run sanity check
2. **Design integration** — map the 4-choke-point pattern (4 points at which you can apply guardrails) to the agent, pick metric sets and thresholds per choke point
3. **Implement** — wire `GuardrailedAgent` or REST calls; add audit logging
4. **Test & tune** — run sample workload, analyze JSONL audit trail, tune thresholds
5. **Deploy & observe** — Dockerize, wire to log aggregation, build dashboards

The mode enforces **18 mandatory rules** covering credential hygiene, the 3-state Pass/Flag/Block action model, threshold precedence, the 4 choke points, OpenAI tool-call format, latency-aware metric ordering, compliance audit logging, custom-metric authoring, backend-proxy mandates, and auto-trigger pattern selection.

#### What's inside `base-modes/real-time-guardrails/.bob/`

| File | Purpose |
|---|---|
| `custom_modes.yaml` | Mode identity + **18 mandatory rules** (always in Bob's context) |
| `workflow.md` | 5-phase walkthrough with exact commands per phase |
| `rules-real-time-guardrails/1_setup_and_credentials.xml` | Env vars, IBM Cloud provisioning, common errors |
| `rules-real-time-guardrails/2_integration_patterns.xml` | 4 choke points + Python/REST/MCP integration code |
| `rules-real-time-guardrails/3_metric_catalog_and_thresholds.xml` | Full 28-metric catalog + 5-layer threshold override mechanics |
| `rules-real-time-guardrails/4_audit_and_observability.xml` | AuditLogger usage, JSONL schema, Splunk/ELK sinks, dashboard aggregation snippets |
| `rules-real-time-guardrails/5_deployment.xml` | Dockerfile, REST vs MCP, scaling, multi-tenant patterns |
| `rules-real-time-guardrails/6_custom_metric_authoring.xml` | When + how to author custom LLM-judge metrics (prompt_template vs criteria+Option) |
| `rules-real-time-guardrails/7_frontend_integration.xml` | Chat-widget pattern, backend proxy, Block/Flag/Pass UX, anti-patterns |
| `rules-real-time-guardrails/8_auto_trigger_patterns.xml` | Middleware / decorator / framework callback decision tree + pre/post hook mechanics |
| `reference-payloads/*.json` + `*.yaml` + `.jsonl` | Working request payloads + sample audit log |
| `reference-payloads/full_pipeline.py` | End-to-end `GuardrailedAgent` class |
| `reference-payloads/custom_metric_example.py` | Both LLM-judge authoring styles, side by side |
| `reference-payloads/frontend_chat_integration.jsx` + `backend_guardrails_proxy.py` | Production React chat widget + Flask backend proxy with audit-serving endpoint |
| `reference-payloads/dashboard_skeleton.jsx` | MUI compliance dashboard reading the audit log |
| `reference-payloads/middleware_fastapi.py` + `middleware_flask.py` | Auto-trigger via HTTP middleware |
| `reference-payloads/decorator_example.py` | Auto-trigger via `@guard` Python decorator |
| `reference-payloads/langchain_callback.py` | Auto-trigger for LangChain chains (callback + RunnableLambda) |

## How to activate the mode in Bob

Clone the `.bob/` folder into your project:

```bash
cd <your-project-root>
cp -r .../building-blocks/ai-trust/real-time-guardrails/bob-modes/base-modes/real-time-guardrails/.bob .
```

Open Bob, select the **🛡️ Real-Time Guardrails** mode from the mode selector. Bob is now guardrails-aware and will guide you through the 5-phase workflow.
