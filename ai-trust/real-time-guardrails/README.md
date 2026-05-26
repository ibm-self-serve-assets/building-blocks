# Real-Time Guardrails

Enforce safety boundaries and operational constraints to keep your AI applications within desired behavior in production.

---

## Key Highlights

- Real-time detection across **28 reference-free metrics** in 7 categories — safety, RAG generation, RAG retrieval, output quality, topic alignment, pattern matching, and tool-call validation
- Three-state **Pass / Flag / Block** action model with built-in fallback messages and audit logging
- Library, REST API, and MCP server — pick the interface that fits your agent
- Threshold policy as code (per-call, constructor, YAML config, env vars) for multi-tenant deployments
- API-based validation of user queries, retrieved context, generated answers, and tool calls

## Solves For

- Lack of risk management for AI
- Lack of real-time protections against adversarial attacks
- Identifying potentially harmful content in prompts and outputs
- Compliance pattern: allow-but-route-for-review (Flag) for borderline content
- Multi-tenant guardrail policies (different partners, different thresholds)

---

## What's Inside

### 🛡️ [Bob Mode](bob-modes/) — start here

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
cp -r .../building-blocks/ai-trust/real-time-guardrails/bob-modes/base-modes/real-time-guardrails/.bob .
```

Open Bob, select the **🛡️ Real-Time Guardrails** mode, and ask Bob to help you integrate guardrails into your agent. Full details in [`bob-modes/README.md`](bob-modes/README.md).

---

### 📦 [Assets](assets/) — what Bob is built on top of

The same code Bob uses, available standalone if you want to integrate without the mode.

#### [`assets/sdk/`](assets/sdk/) — Production SDK

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

#### [`assets/` (numbered scripts)](assets/) — Tutorial templates

Four numbered Python scripts (`01_…` through `04_…`) that show how to use the watsonx.governance SDK directly — minimal abstractions, copy-modify-deploy. Start here if you want to learn the gov SDK from scratch, ship a simple input/output safety filter in <30 minutes, or adapt a known-good pattern (e.g. `04_guardrail_pipeline.py`) to your own data.

---

## Getting Started

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


