# Real-Time Guardrails — Bob Skill

A Bob skill that guides developers through adding **production-grade runtime safety and quality guardrails** to AI/RAG agents using IBM's `real-time-guardrails` package (backed by watsonx.governance).

## What this skill does

When a developer says they want to add guardrails to an LLM app, this skill drives them end-to-end through:

1. **Setup** — IBM Cloud provisioning, credentials wired safely (no key-leaks)
2. **Design** — 4-choke-point pattern (input → retrieval → generation → output), metric set per choke point, threshold policy, fallback messages
3. **Implement** — explicit wiring or auto-trigger (middleware / decorator / framework callback), with reference impls for FastAPI, Flask, LangChain, watsonx Orchestrate
4. **Test & tune** — sample-workload tuning, jq queries against the audit log
5. **Deploy & observe** — library / REST / MCP modes, Splunk/ELK audit sinks, compliance dashboards

## When to use this skill

- Adding safety and quality enforcement to an AI agent before shipping to production
- Wiring guardrails into FastAPI / Flask / LangChain / LangGraph / watsonx Orchestrate
- Picking the right metric set from the 28-metric catalog for a partner's data shape
- Authoring custom LLM-as-judge metrics when the catalog doesn't cover a domain-specific concern
- Building compliance audit logs and partner-facing compliance dashboards
- Integrating chat widgets with a backend proxy (without leaking `WATSONX_APIKEY` to the browser)
- Tuning per-tenant threshold policies (5-layer override model)
- Diagnosing why a metric scored unexpectedly

## When NOT to use this skill — see instead

- **Pre-deployment evaluation of a watsonx Orchestrate agent** (benchmarks, simulated users, red-teaming) → use the **agent-ops** skill. Real-Time Guardrails is for *runtime* enforcement; Agent Ops is for *build-time* validation of WXO agents.
- **Build-time evaluation of GenAI quality (RAG faithfulness, HAP/PII screening, agentic tool-call accuracy) on a dataset** → use the **build-time-gen-ai-evals** skill. Both skills share the same underlying `ibm-watsonx-gov` SDK and the same custom LLM-as-judge authoring patterns — only the lifecycle stage differs. Real-Time Guardrails enforces decisions per-request at runtime; build-time-gen-ai-evals scores a dataset before deploy.

| Skill | Lifecycle stage | Trigger |
|---|---|---|
| **real-time-guardrails** (this one) | Runtime (per-request) | Production traffic |
| agent-ops | Build-time (pre-deploy) | WXO agent ready for validation |
| build-time-gen-ai-evals | Build-time (pre-deploy) | Dataset of inputs/outputs/traces |

## Prerequisites

- IBM Cloud account with watsonx.governance subscription (always required)
- (Optional) watsonx.ai project with Watson Machine Learning associated — only needed for the 3 LLM-as-judge metrics
- Python 3.11–3.13 (3.14 not yet supported by the IBM SDK chain)
- Outbound HTTPS to `*.ml.cloud.ibm.com` and your watsonx.governance regional endpoint (air-gapped not supported)

See `USAGE-GUIDE.md` for full installation and first-run instructions.

## What's in this skill

```
real-time-guardrails/
├── SKILL.md                     # Bob loads this on every invocation
├── README.md                    # this file (partner-facing overview)
├── USAGE-GUIDE.md               # install + first-run walkthrough
├── setup.sh                     # one-command venv + clone + dep pre-flight + install
├── reference/                   # detailed knowledge, Bob loads on demand
│   ├── setup-and-credentials.md
│   ├── integration-patterns.md
│   ├── metrics-catalog.md
│   ├── audit-and-observability.md
│   ├── deployment.md
│   ├── custom-metric-authoring.md
│   ├── frontend-integration.md
│   ├── auto-trigger-patterns.md
│   └── watsonx-orchestrate-integration.md
├── examples/                    # working reference payloads
│   ├── full_pipeline.py         (GuardrailedAgent — 4 choke points wired)
│   ├── middleware_fastapi.py / middleware_flask.py
│   ├── decorator_example.py
│   ├── langchain_callback.py
│   ├── wxo_tool_wrapper.py / wxo_service_middleware.py
│   ├── frontend_chat_integration.jsx
│   ├── backend_guardrails_proxy.py
│   ├── dashboard_skeleton.jsx
│   ├── custom_metric_example.py
│   ├── audit_log_sample.jsonl
│   └── *.json   (sample REST request payloads per choke point)
└── assets/
    ├── env.example              (env var template)
    └── thresholds.example.yaml  (per-metric + category threshold config)
```

## Installing this skill

Drop the `real-time-guardrails/` folder into your Bob skill directory (typically `.bob/skills/`):

```bash
cp -r real-time-guardrails ~/path/to/your/repo/.bob/skills/
```

Then ask Bob something like:
- *"I need to add safety guardrails to my RAG agent before going to production"*
- *"My LangChain chatbot needs PII detection and HAP screening on outputs"*
- *"How do I add guardrails to a watsonx Orchestrate agent that uses 3 tools?"*

Bob will load this skill and drive the workflow.

## Source

This skill is derived from the [Real-Time Guardrails Bob mode](https://github.com/ibm-self-serve-assets/building-blocks/tree/main/ai-trust/real-time-guardrails) in the IBM Building Blocks portfolio. The underlying Python package is `real-time-guardrails` (built on top of `ibm-watsonx-gov`).
