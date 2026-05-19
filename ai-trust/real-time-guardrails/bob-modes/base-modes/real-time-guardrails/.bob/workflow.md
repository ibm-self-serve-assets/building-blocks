# Real-Time Guardrails — Developer Workflow

This is the canonical phased walkthrough Bob uses to drive a developer from "I want guardrails on my AI agent" to "guardrails are deployed and observable in production."

Each phase has a clear **goal**, **prerequisite check**, **ordered steps with commands**, **success criteria**, and **common failures + remedies**.

---

## Phase 1 — Setup & Verify (~15 min)

**Goal:** Working `GuardrailsEvaluator` instance that returns scored results from real watsonx.governance.

### Prerequisite check (Bob asks first)

- [ ] Python 3.11–3.13 available? (`python3 --version`) — RULE 3
- [ ] IBM Cloud account with watsonx.governance subscription? — RULE 1
- [ ] (Optional) watsonx.ai project for LLM-as-judge metrics? — RULE 2

### Steps

1. **Install the package**
   ```bash
   pip install real-time-guardrails[all]      # the [all] extra is mandatory — RULE 4
   # or for development:
   git clone https://github.com/ibm-self-serve-assets/building-blocks
   cd building-blocks/ai-trust/real-time-guardrails/assets/sdk
   pip install -e ".[all]"
   ```

2. **Provision IBM Cloud services** (skip if already done)
   - watsonx.governance: IBM Cloud console → Catalog → search "watsonx.governance" → Create
   - watsonx.ai (optional): https://dataplatform.cloud.ibm.com → Projects → New project
   - For LLM-judge metrics specifically: in the watsonx.ai project, **Manage** → **Services and Integrations** → Associate **Watson Machine Learning**

3. **Set credentials safely** — RULE 1
   ```bash
   cd <your-project-root>
   cat > .env <<'EOF'
   WATSONX_APIKEY=     # paste with read -s next
   WXG_SERVICE_INSTANCE_ID=
   WXG_PROJECT_ID=     # optional
   EOF
   chmod 600 .env
   # Avoid pasting the key into chat or shell history:
   read -s -p "API key: " key && printf 'WATSONX_APIKEY=%s\n' "$key" >> .env && unset key
   ```

4. **Run sanity check**
   ```python
   from real_time_guardrails import GuardrailsEvaluator
   ev = GuardrailsEvaluator()
   print("metrics:", ev.list_metrics()["total"])    # 28 (or 25 if no WXG_PROJECT_ID)
   r = ev.evaluate(input_text="My SSN is 123-45-6789", metrics=["PII Detection"])
   print(r["PII Detection"].score, r["PII Detection"].action)
   ```

### Success criteria

- `metrics: 28` (or 25 without WXG_PROJECT_ID) — RULE 2
- PII Detection score in the 0.6–0.9 range with action="Block"

### Common failures

| Error | Cause | Fix |
|---|---|---|
| `ConfigError: Missing required environment variable(s): WATSONX_APIKEY` | env var not exported in this shell | `source .env` or use `set -a; source .env; set +a` |
| `ModuleNotFoundError: No module named 'unitxt'` | missing extras | `pip install real-time-guardrails[all]` — RULE 4 |
| `EvaluatorInitError: Failed to initialize ibm_watsonx_gov MetricsEvaluator` | API key invalid, lacks permissions, or service instance ID wrong | re-check IDs in IBM Cloud → Resource list → Instance → GUID |
| `project_id ... is not associated with a WML instance` | watsonx.ai project missing WML association | in the project, Manage → Services and Integrations → Associate Service → Watson Machine Learning |

---

## Phase 2 — Design integration (~30 min)

**Goal:** A decision per choke point — which metrics, which thresholds, which fallback message.

### Prerequisite check

- [ ] Partner has a clear picture of their agent architecture (input → retrieval → LLM → output)?
- [ ] Partner has stated their compliance posture (strict vs permissive)?

### Steps

1. **Map the 4 choke points to the agent** — RULE 9
   - Input choke point: WHERE in the partner's code does the user query first arrive?
   - Retrieval: AFTER the vector store call, BEFORE the LLM call.
   - Generation: AFTER the LLM call.
   - Output: BEFORE serving the response to the user.

   If any choke point doesn't apply (e.g. non-RAG agent has no retrieval), skip it.

2. **Pick the metric set per choke point** — see `rules-real-time-guardrails/2_integration_patterns.xml`

   | Choke point | Recommended metrics |
   |---|---|
   | Input | `categories=["safety", "pattern"]` + optionally `Topic Relevance` if `system_prompt` available |
   | Retrieval | `categories=["rag_retrieval"]` (with `context=list[str]`) |
   | Generation | `categories=["rag_generation"]` |
   | Output | `metrics=["PII Detection", "HAP (Hate, Abuse, Profanity)", "Conciseness (LLM Judge)"]` (run on `generated_text`) |

3. **Decide threshold policy** — RULE 8
   - Start with defaults (Safety block=0.65 flag=0.4; RAG block=0.1 flag=0.3).
   - If compliance-strict (healthcare/finance/legal): tighten Safety block to 0.5, RAG block to 0.2.
   - If user-experience-permissive (consumer chat): loosen Safety block to 0.8, RAG block to 0.05.

4. **Write fallback messages** for each Block scenario (Bob can suggest based on the partner's domain)

5. **Custom metric needed?** — If the 28-metric catalog doesn't cover the partner's domain-specific concern (e.g. "does this answer cite the correct internal policy?"), author a custom LLM-as-judge metric. See `rules-real-time-guardrails/6_custom_metric_authoring.xml` for the decision tree (rubric-style vs prompt_template) and `reference-payloads/custom_metric_example.py` for the working pattern. Tune thresholds on existing metrics first — only author custom when tuning isn't enough.

### Success criteria

- Partner has a written list of (choke point → metrics → thresholds → fallback) — one row per metric.
- Any custom metrics are authored and registered in the evaluator's MetricRegistry.

---

## Phase 3 — Implement (~60 min)

**Goal:** Working `GuardrailedAgent` (or equivalent) in the partner's codebase.

### Prerequisite check

- [ ] Phase 2 decisions documented?
- [ ] Partner has chosen an interface: library (in-process) / REST (separate service) / MCP (agentic tool)?

### Steps

1. **Choose your trigger pattern** — RULE 17
   - **Explicit wiring** (Python `GuardrailedAgent` or per-choke-point inline calls): partner has full control; agent code calls evaluator at each stage.
   - **Auto-trigger** (HTTP middleware / Python decorator / framework callback): guardrails fire on every request without per-handler wiring. Pick exactly ONE pattern.
   - Decision tree: `rules-real-time-guardrails/8_auto_trigger_patterns.xml`. Polyglot HTTP → middleware. Monolithic Python → decorator. LangChain/LangGraph → framework callback. Microservice mesh → middleware at gateway.

2. **For explicit wiring (Python agent): use the `GuardrailedAgent` template**

   Copy `.bob/reference-payloads/full_pipeline.py` into the partner's repo. Replace:
   - `simulate_retrieve` → partner's vector store call
   - `simulate_model` → partner's LLM client call

3. **For auto-trigger: pick the reference impl matching your topology**
   - FastAPI/Flask service → `reference-payloads/middleware_fastapi.py` or `middleware_flask.py`
   - Monolithic Python function → `reference-payloads/decorator_example.py` (the `@guard` decorator)
   - LangChain / LangGraph chain → `reference-payloads/langchain_callback.py` (callback for input, RunnableLambda for output)
   - Heads-up: stock LangChain callbacks are observational and can't replace outputs. Output blocking must use `RunnableLambda` wrapping. See 8_auto_trigger_patterns.xml.

4. **For non-Python agents or shared-service deployment: use the REST interface**

   Deploy the package: `real-time-guardrails serve --port 8090` (or Dockerize). Agent makes HTTP calls at each choke point:
   ```javascript
   await fetch(`${GUARD}/api/evaluate`, {
     method: "POST",
     headers: {"Content-Type": "application/json"},
     body: JSON.stringify({
       input_text: userQuery,
       categories: ["safety", "pattern"],
       params: {keywords: partnerBlockList},
     }),
   });
   ```

5. **For chat-widget frontends: use the backend-proxy pattern** — RULES 14, 15
   - Browser calls partner's backend (cookie/JWT auth) — NOT the guardrails service directly.
   - Backend proxies to guardrails, writes audit log, returns sanitized result.
   - Reference: `reference-payloads/frontend_chat_integration.jsx` (React) + `reference-payloads/backend_guardrails_proxy.py` (Flask backend).
   - See 7_frontend_integration.xml for topology + anti-patterns.

6. **Wire the audit log** — RULE 11
   ```python
   from real_time_guardrails import AuditLogger
   audit = AuditLogger(path="/var/log/guardrails/audit.jsonl")
   # or for streaming: AuditLogger(sink=lambda rec: splunk_client.send(rec))
   ```
   Build the evaluator (and logger) ONCE at startup — RULE 16.

7. **Handle each action** — RULE 10
   - Block → return result.fallback_message (don't leak metric details — RULE 14)
   - Flag → allow but log to audit (already done by AuditLogger)
   - Pass → serve the response

### Success criteria

- The partner's agent calls all chosen choke points.
- Every decision is recorded in the audit log.
- Block-action responses return the appropriate fallback message.
- Auto-trigger pattern is consistent across the agent (RULE 17 — no mixing).

---

## Phase 4 — Test & tune (~30 min)

**Goal:** Threshold policy validated against a representative workload.

### Prerequisite check

- [ ] Partner has 10–50 sample requests representing typical traffic?

### Steps

1. **Run the agent against the sample workload** and capture the audit log.

2. **Analyze the JSONL audit trail**
   ```bash
   # Count actions per metric
   jq -r '.metrics | to_entries[] | "\(.key) \(.value.action)"' audit.jsonl | sort | uniq -c

   # Find borderline (Flag) cases
   jq 'select(.overall_action == "Flag") | {request_id, flagged_metrics, input_hash}' audit.jsonl

   # Find blocks
   jq 'select(.overall_action == "Block") | {request_id, blocked_metrics}' audit.jsonl
   ```

3. **Tune thresholds** — RULE 8
   - Too many false-positive blocks? Loosen the block threshold for that metric.
   - Too few flags catching borderline content? Tighten the flag threshold.
   - Persist tuned values in a YAML config (or env vars for deployment).

4. **Re-run** until the action distribution matches the partner's tolerance.

### Success criteria

- Block rate on the sample workload is in the partner's target range.
- Audit log shows zero unexpected scores (no metric returning `None` unintentionally — RULE 5 / RULE 6).

---

## Phase 5 — Deploy & observe (~45 min)

**Goal:** Guardrails running in production with observability.

### Prerequisite check

- [ ] Partner's agent is ready to deploy with guardrails wired?
- [ ] Partner has a log aggregation system (Splunk, ELK, CloudWatch, etc.)?

### Steps

1. **Deploy** — pick one:
   - **Library mode**: pip-install into the agent's container. No separate service.
   - **REST mode**: Dockerize using `assets/sdk/Dockerfile`. Co-locate with agent (same VPC). `real-time-guardrails serve --port 8090`.
   - **MCP mode**: register as an MCP tool in the agent's MCP config.

2. **Wire audit log to log aggregation**
   ```python
   import splunk_sdk
   audit = AuditLogger(sink=lambda rec: splunk_sdk.send_event("guardrails", rec))
   ```
   Or for ELK: `AuditLogger(sink=lambda rec: elastic_client.index(index="guardrails", document=rec))`.

3. **Build a partner-facing compliance dashboard**
   - Reference: `reference-payloads/dashboard_skeleton.jsx` — MUI-based React component that reads from `/api/audit/recent` (provided by `backend_guardrails_proxy.py`).
   - What it shows: summary stacked bar (Pass/Flag/Block counts), per-metric average score + action counts, expandable history table with per-metric breakdown per decision.
   - Aggregation snippets (build your own if you don't want MUI): see `<dashboard_starter>` in 4_audit_and_observability.xml.
   - Polls every 30 s by default; swap to SSE/WebSockets if you need sub-second latency.

4. **Set up production dashboards** (separate from the partner-facing compliance dashboard above)
   - Block rate per metric (time-series)
   - Flag rate per metric (time-series)
   - p50/p95 latency per choke point
   - Token spend on LLM-judge metrics (if used) — RULE 12

4. **Monitor egress** — RULE: partners deploying in restricted environments need outbound HTTPS to `*.ml.cloud.ibm.com` + the watsonx.governance service URL. Air-gapped deployments are not supported.

### Success criteria

- Guardrails service deployed.
- Audit log streaming to partner's log aggregation.
- Dashboards built and showing live data.

---

## Quick reference

| Need | File |
|---|---|
| Mandatory rules (17 total) | `.bob/custom_modes.yaml` → `customInstructions` |
| Workflow phases | this file |
| Setup details + IBM Cloud UI navigation | `.bob/rules-real-time-guardrails/1_setup_and_credentials.xml` |
| Integration code per choke point | `.bob/rules-real-time-guardrails/2_integration_patterns.xml` |
| Metric catalog + threshold mechanics | `.bob/rules-real-time-guardrails/3_metric_catalog_and_thresholds.xml` |
| Audit log usage + dashboard aggregation | `.bob/rules-real-time-guardrails/4_audit_and_observability.xml` |
| Deployment + scaling | `.bob/rules-real-time-guardrails/5_deployment.xml` |
| Authoring custom LLM-judge metrics | `.bob/rules-real-time-guardrails/6_custom_metric_authoring.xml` |
| Frontend chat-widget integration + anti-patterns | `.bob/rules-real-time-guardrails/7_frontend_integration.xml` |
| Auto-trigger patterns (middleware/decorator/callback) | `.bob/rules-real-time-guardrails/8_auto_trigger_patterns.xml` |
| Working code samples (JSON + Python + JSX) | `.bob/reference-payloads/` |
