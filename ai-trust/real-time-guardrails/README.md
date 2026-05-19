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

## What's New

📦 **Production SDK now available** alongside the tutorial scripts. Pip-installable Python package with library, REST, and MCP interfaces — 28 metrics, 3-state action model, built-in audit logging, drop-in 4-choke-point pipeline class. See [`assets/sdk/`](assets/sdk/).

---

## What's Inside

### [Assets](assets/)

Two complementary paths — pick the one that matches your needs:

#### 📦 [`assets/sdk/`](assets/sdk/) — Production SDK (recommended for deployment)

The full pip-installable `real-time-guardrails` Python package. Ships:

- **28 metrics** across safety / RAG / quality / topic / pattern / tool-call categories
- **Three interfaces**: library (in-process), REST server, MCP server
- **`GuardrailedAgent` class** wrapping the full 4-choke-point pattern (input → retrieval → generation → output)
- **`AuditLogger`** for JSONL compliance trails
- **Threshold overrides** at 5 layers (per-call > constructor > YAML > env var > default)
- **180+ unit tests** + integration tests against real watsonx.governance

Start here for: production deployment, multi-tenant guardrail policies, REST/MCP integration with non-Python agents.

```bash
cd assets/sdk
pip install -e ".[all]"
python examples/library_quickstart.py
```

See [`assets/sdk/README.md`](assets/sdk/README.md) for the full integration guide (with architecture diagram + per-language examples).

#### 📘 [`assets/` (numbered scripts)](assets/) — Tutorial templates

Four numbered Python scripts (`01_…` through `04_…`) that show how to use the watsonx.governance SDK directly — minimal abstractions, copy-modify-deploy. Start here if you want to:

- Learn the gov SDK from scratch
- Ship a simple input/output safety filter in <30 minutes
- Adapt a known-good pattern (e.g. `04_guardrail_pipeline.py`) to your own data

### [Bob Modes](bob-modes/)

Real-Time Guardrails Bob mode — guides developers through the full lifecycle: setup → integrate → test → deploy. Activate it in IBM Bob and Bob becomes a guardrails-aware assistant that knows the metric catalog, threshold policies, fallback patterns, and integration code for the 4 choke points.

---

## Getting Started

**For partners deploying guardrails in production:**
1. Read the top of [`assets/sdk/README.md`](assets/sdk/README.md) — install + IBM Cloud requirements
2. Set up `.env` with `WATSONX_APIKEY` + `WXG_SERVICE_INSTANCE_ID` (and optionally `WXG_PROJECT_ID` for LLM-judge metrics)
3. Run `python assets/sdk/examples/library_quickstart.py` to verify
4. Integrate using the 4-choke-point pattern shown in the README's "Integrating with your RAG agent" section

**For developers learning the gov SDK:**
1. Review the numbered scripts in [`assets/`](assets/) — start with `01_content_safety_guardrails.py`
2. Follow the setup instructions in [`assets/README.md`](assets/README.md)

**For Bob users:**
1. Activate the Real-Time Guardrails mode (see [`bob-modes/`](bob-modes/))
2. Ask Bob to help you integrate guardrails into your agent
