# Guardrails

Part of **[Control](../)** in the **[AI Control Plane](../../)**.

Evaluation with [Agent Ops](../agent-ops/) tells you how an AI agent behaves before release; **Guardrails** keep it within policy once it is live. Guardrails check requests and responses in production — blocking, masking, flagging, or rerouting before anything reaches users, tools, or downstream systems.

There are two complementary ways to apply guardrails, and you can use them together:

| Approach | Best for | How it works |
|---|---|---|
| **[Agent Controls](#agent-controls--watsonx-orchestrate)** | Agents running on **watsonx Orchestrate** | Reusable policy artifacts — PII filters, content guardrails, secrets detection, rate limits, SQL sanitization, model fallback — attached to agents, tools, and models **as configuration, not code** |
| **[Real-Time Guardrails SDK](#real-time-guardrails-sdk--any-framework)** | Agents and RAG apps on **any framework** | watsonx.governance metrics with **Pass / Flag / Block** thresholds at input, retrieval, generation, and output — as a Python library, REST API, or MCP server, including custom LLM-as-judge checks |

Agent Controls are configured in watsonx Orchestrate, so this folder holds guidance for them rather than code. Everything in [`assets/`](assets/), [`bob-modes/`](bob-modes/), and [`bob-skills/`](bob-skills/) belongs to the Real-Time Guardrails SDK.

---

## Agent Controls — watsonx Orchestrate

**Agent Controls** keep watsonx Orchestrate agents within authorized boundaries once deployed. Powered by the watsonx Orchestrate Controls framework, controls are reusable policy artifacts — PII filters, content guardrails, secrets detection, rate limits, SQL sanitization, and model routing — attached to agents, tools, and models **as configuration, not code**. Policies can be added, changed, or removed without touching the agent's implementation, and the same agent can carry different policies per environment.

A control combines four things: a **policy artifact** (the rule), an **asset** (the agent, tool, or model it protects), an **execution hook** (the pipeline stage where it fires, e.g. `agent_pre_invoke`, `tool_pre_invoke`), and a **priority** (lower numbers run first). If a control blocks, the pipeline halts immediately and nothing downstream runs.

| Layer | Control | What It Enforces |
|---|---|---|
| **Agent** | PII Filter | Detects and masks SSNs, emails, phone numbers, credit cards — redact, partial, hash, tokenize, or remove |
| **Agent** | Content Guardrails | Blocks jailbreaks, hate/abuse/profanity (HAP), violence, sexual content, and bias on input and output |
| **Agent** | Secrets Detector | Catches AWS keys, JWTs, API keys, private key blocks — redact or block |
| **Agent** | Output Length Guard / Regex Pattern | Enforces response size limits; redacts or blocks custom patterns |
| **Tool** | Rate Limiter | Caps tool invocations per minute, per tool and per tenant — stops runaway agent loops |
| **Tool** | SQL Sanitizer | Blocks destructive SQL (DROP, TRUNCATE, unscoped DELETE/UPDATE) and injection comments before execution |
| **Tool** | Guardrails / Secrets / Output Length | Same protections as the agent layer, applied at the tool input/output boundary |
| **Model** | Fallback / Retry | Routes to backup models on errors (429, 5xx) with configurable retries — no agent code change |
| **Model** | Load Balance | Distributes requests across providers using weighted ratios |

**Typical scenarios:** PII compliance for customer-service agents, SQL-injection protection for Text-to-SQL agents, secrets-leakage prevention in finance, and model fallback for high availability.

Agent Controls are watsonx Orchestrate-native. If your agent runs on another framework, or you need custom LLM-as-judge criteria and threshold policy as code, use the [Real-Time Guardrails SDK](#real-time-guardrails-sdk--any-framework) below.

📖 Full control reference, hook diagram, and priority guidance: [Guardrails on the docs site](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/guardrails/#agent-controls-watsonx-orchestrate)

**Bob skill:** a [Bob skill for Agent Controls](https://ibm-self-serve-assets.github.io/building-blocks-docs/ibm-bob/skills/) covers artifact selection, hook assignment, priority layering, and defence-in-depth stacking across agent and tool boundaries.

---

## Real-Time Guardrails SDK — Any Framework

Enforce safety boundaries and operational constraints to keep your AI applications within desired behavior in production.

### Key Highlights

- Real-time detection across **28 reference-free metrics** in 7 categories — safety, RAG generation, RAG retrieval, output quality, topic alignment, pattern matching, and tool-call validation
- Three-state **Pass / Flag / Block** action model with built-in fallback messages and audit logging
- Library, REST API, and MCP server — pick the interface that fits your agent
- Threshold policy as code (per-call, constructor, YAML config, env vars) for multi-tenant deployments
- API-based validation of user queries, retrieved context, generated answers, and tool calls

### Solves For

- Lack of risk management for AI
- Lack of real-time protections against adversarial attacks
- Identifying potentially harmful content in prompts and outputs
- Compliance pattern: allow-but-route-for-review (Flag) for borderline content
- Multi-tenant guardrail policies (different partners, different thresholds)

---

### What's Inside

#### 🛡️ [Bob Mode](bob-modes/) — start here

The fastest way to ship real-time guardrails is to let Bob drive. Activate the **Real-Time Guardrails** Bob mode and Bob becomes a guardrails-aware assistant that knows the metric catalog, threshold policies, the 4-choke-point pattern, fallback UX, and the production integration code.

Bob walks the developer through **5 phases**:

1. **Setup & Verify** — provision IBM Cloud services, set credentials safely, run sanity check
2. **Design integration** — map the 4-choke-point pattern to the agent, pick metric sets and thresholds per choke point
3. **Implement** — wire `GuardrailedAgent` or REST calls; add audit logging
4. **Test & tune** — run sample workload, analyze JSONL audit trail, tune thresholds
5. **Deploy & observe** — Dockerize, wire to log aggregation, build dashboards

Under the hood, the mode enforces **19 mandatory rules** covering credential hygiene, the 3-state Pass/Flag/Block action model, threshold precedence, the 4 choke points, OpenAI tool-call format, latency-aware metric ordering, compliance audit logging, custom-metric authoring, backend-proxy mandates, auto-trigger pattern selection, and watsonx Orchestrate (WXO) partner-boundary integration. It ships with production-ready reference payloads — a full `GuardrailedAgent`, FastAPI/Flask middleware, a LangChain callback, a React chat widget + Flask backend proxy, an MUI compliance dashboard, and WXO tool-wrapper / service-middleware examples.

**Activate it:**

```bash
cd <your-project-root>
cp -r .../building-blocks/ai/control/guardrails/bob-modes/base-modes/real-time-guardrails/.bob .
```

Open Bob, select the **🛡️ Real-Time Guardrails** mode, and ask Bob to help you integrate guardrails into your agent. Full details in [`bob-modes/README.md`](bob-modes/README.md).

---

#### 📦 [Assets](assets/) — what Bob is built on top of

The same code Bob uses, available standalone if you want to integrate without the mode.

##### [`assets/sdk/`](assets/sdk/) — Production SDK

Pip-installable `real-time-guardrails` Python package:

- **28 metrics** across safety / RAG / quality / topic / pattern / tool-call categories
- **Three interfaces**: library (in-process), REST server, MCP server
- **`GuardrailedAgent` class** wrapping the full 4-choke-point pattern (input → retrieval → generation → output)
- **`AuditLogger`** for JSONL compliance trails
- **Threshold overrides** at 5 layers (per-call > constructor > YAML > env var > default)
- **180+ unit tests** + integration tests against real watsonx.governance

```bash
cd assets/sdk
pip install -e ".[all]"
python examples/library_quickstart.py
```

See [`assets/sdk/README.md`](assets/sdk/README.md) for the full integration guide (architecture diagram + per-language examples).

##### [`assets/` (numbered scripts)](assets/) — Tutorial templates

Four numbered Python scripts (`01_…` through `04_…`) that show how to use the watsonx.governance SDK directly — minimal abstractions, copy-modify-deploy. Start here if you want to learn the gov SDK from scratch, ship a simple input/output safety filter in <30 minutes, or adapt a known-good pattern (e.g. `04_guardrail_pipeline.py`) to your own data.

---

### Getting Started

**Recommended path — let Bob drive:**
1. Copy the `.bob/` folder into your project (see [Bob Mode](#️-bob-mode--start-here) above)
2. Activate the **🛡️ Real-Time Guardrails** mode in Bob
3. Ask Bob to help you integrate guardrails — it will walk you through the 5 phases, ask for the right credentials, and generate integration code wired to your agent

**Direct SDK path — integrate yourself:**
1. Read the top of [`assets/sdk/README.md`](assets/sdk/README.md) — install + IBM Cloud requirements
2. Set up `.env` with `WATSONX_APIKEY` + `WXG_SERVICE_INSTANCE_ID` (and optionally `WXG_PROJECT_ID` for LLM-judge metrics)
3. Run `python assets/sdk/examples/library_quickstart.py` to verify
4. Integrate using the 4-choke-point pattern shown in the README's "Integrating with your RAG agent" section

**Learning path — gov SDK from scratch:**
1. Review the numbered scripts in [`assets/`](assets/) — start with `01_content_safety_guardrails.py`
2. Follow the setup instructions in [`assets/README.md`](assets/README.md)

📖 Docs: [Guardrails](https://ibm-self-serve-assets.github.io/building-blocks-docs/ai-core/control/guardrails/)
