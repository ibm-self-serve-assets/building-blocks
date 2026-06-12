---
name: real-time-guardrails
description: Add IBM watsonx.governance-backed runtime safety and quality guardrails to AI/RAG agents. Use when shipping LLM apps to production, designing 4-choke-point Pass/Flag/Block pipelines (input → retrieval → generation → output), picking metric sets from the 28-metric catalog, wiring guardrails into FastAPI / Flask / LangChain / watsonx Orchestrate, authoring custom LLM-as-judge metrics, building compliance audit logs, integrating chat widgets with backend proxies, or tuning per-tenant threshold policies. Covers Python library, REST sidecar, and MCP tool deployment modes.
---

# Real-Time Guardrails

This skill helps developers wire **production-grade safety and quality guardrails** into AI agents using IBM's `real-time-guardrails` package (backed by watsonx.governance). The package ships 28 metrics across safety, RAG-generation, RAG-retrieval, quality, topic, pattern, and tool-call categories, with a 3-state Pass/Flag/Block action model, threshold policy as code, and audit logging.

---

## Mandatory Rules

Read every time. Violating any of these causes silent or costly failures in production.

**RULE 1 — Never paste live credentials into chat.** Guide the user to set `WATSONX_APIKEY` and `WXG_SERVICE_INSTANCE_ID` in a `.env` file (`chmod 600`). Use `read -s` to enter the key without leaving it in shell history. If a user pastes a key into chat, interrupt and tell them to rotate it at IBM Cloud → Manage → Access (IAM) → API keys.

**RULE 2 — `WXG_PROJECT_ID` is optional.** The package runs 25 metrics with just `WATSONX_APIKEY` + `WXG_SERVICE_INSTANCE_ID`. `WXG_PROJECT_ID` unlocks 3 LLM-as-judge metrics (Answer Completeness, Conciseness, Tool Call Relevance). Don't force watsonx.ai on partners who don't want LLM-judge cost.

**RULE 3 — Python 3.11–3.13 only.** The IBM SDK chain doesn't support 3.14 yet. If the user is on 3.14, rebuild their venv with 3.11/3.12/3.13.

**RULE 4 — Install from source with the `[all]` extra; use a dedicated venv.** The package is not on PyPI today — partners install from a building-blocks repo clone via `pip install -e "<repo>/ai-trust/real-time-guardrails/assets/sdk[all]"`. **The quotes are required on zsh** (macOS default) — without them, the shell parses `[all]` as an array subscript, silently produces an empty path, and pip errors with `is not a valid editable requirement`. The bundled `setup.sh` quotes correctly. Without `[metrics,llmaj]` (always part of base install), registry build fails with `ModuleNotFoundError: No module named 'unitxt'`. If the user reports `ResolutionImpossible` during install, their existing venv has stricter pins than the SDK can accept (typically on `pydantic` or `httpx`) — load `reference/setup-and-credentials.md` for the conflict matrix + dry-run recipe.

**RULE 5 — Tool-call payloads use OpenAI ToolSpec format.** `tool_calls: [{"type": "function", "function": {"name": "...", "arguments": "..."}}]`. Flat dicts like `{"name": "...", "parameters": "..."}` are rejected by the SDK.

**RULE 6 — Context field semantics differ.** RAG generation (Faithfulness, Answer/Context Relevance): `context = single string`. RAG retrieval (Hit Rate, Retrieval Precision, Reciprocal Rank): `context = list[str]`, one entry per doc. Wrong shape → MissingFieldError or degenerate scores.

**RULE 7 — Three-state action model.** Pass / Flag / Block. Flag = allow but log for review. Never silently drop the Flag state; surface it in the audit log via `bundle.flagged()`. Defaults: Safety (HIGH_IS_RISK) flag=0.4 block=0.65; RAG/Quality (LOW_IS_RISK) flag=0.3 block=0.1.

**RULE 8 — Threshold precedence (highest wins).** per-call `evaluate(thresholds=)` > constructor `GuardrailsEvaluator(threshold_overrides=)` > YAML config > env vars `GUARDRAILS_THRESHOLD_*` > package default. Per-partner thresholds belong in YAML or env, not hard-coded.

**RULE 9 — Four choke points.** Input safety BEFORE retrieval/model. Retrieval quality AFTER retrieval, BEFORE LLM (skip LLM if HitRate=0). Generation faithfulness AFTER LLM, BEFORE serving. Output safety AFTER LLM, BEFORE serving. Document any skipped choke point with a justification.

**RULE 10 — Never bypass a Block.** Correct responses to Block: (a) refuse, return `result.fallback_message`; (b) regenerate once with adjusted prompt; (c) override threshold per-call with audit-logged justification. NEVER recommend setting thresholds artificially high to bypass.

**RULE 11 — Always emit audit logs.** Use `AuditLogger(path=...)` or `AuditLogger(sink=...)`. For regulated industries (healthcare, finance), use `AuditLogger(include_inputs=False)` — the `input_hash` stays for joinability against a separately-controlled PII store.

**RULE 12 — Latency-aware metric ordering.** Local-Python ~1ms (pattern, readability). Granite Guardian ~200-800ms each (most safety, RAG). LLM-as-judge 1-3s each. Order cheap-first per choke point: safety + pattern → RAG retrieval → RAG generation → LLM-judge quality. For high volume, sample LLM-judge (10% of traffic is a common default).

**RULE 13 — Custom LLM-judge metric authoring.** Simple rubrics (Yes/No, High/Med/Low) → `build_criteria_judge()` from `core.custom_metrics`. Complex judgments needing examples → direct `LLMAsJudgeMetric(prompt_template=...)`. Don't reinvent metrics that exist in the catalog; tune thresholds first. See `reference/custom-metric-authoring.md`.

**RULE 14 — Never expose credentials or the guardrails endpoint to the browser.** `WATSONX_APIKEY` in browser bundles is a leak — bundles are public. Always route: browser → partner backend (session cookie/JWT) → guardrails. Backend holds creds, applies per-tenant policy, writes the audit log, implements fail-open/closed centrally.

**RULE 15 — localStorage is for UX, not audit.** localStorage may hold UI state (last-N visible messages, collapsed/expanded panels) but NEVER compliance-grade audit records. Audit lives server-side. Browsers can't deliver durability, tamper-evidence, or retention policy.

**RULE 16 — Build the evaluator ONCE at startup, share across requests.** Per-request instantiation costs several seconds (registry build + LLMJudge construction) and defeats auto-trigger. Middleware/decorator/callback patterns all assume a long-lived evaluator.

**RULE 17 — One trigger pattern per agent.** Pick middleware OR decorator OR framework callback — don't mix. Reason: single owner = consistent failure modes, audit alignment, threshold policy. Mixing patterns creates gaps where guardrails could be skipped.

**RULE 18 — Enumerate "WILL RUN" vs "WILL BE SKIPPED" up front.** When the partner describes their data shape, immediately list (a) which of the 28 metrics will run, (b) which are skipped and which missing field would unlock them, (c) which are dropped entirely if `WXG_PROJECT_ID` is unset. Then offer three options: supply missing field, author a custom metric, or accept the subset. Use the field availability matrix in `reference/metrics-catalog.md`. **Note:** the 3 LLM-judge metrics ship with opinionated prompts — partners can replace, skip (unset `WXG_PROJECT_ID`), or accept defaults. Be explicit.

**RULE 19 — watsonx Orchestrate (WXO) agents integrate at partner-owned boundaries only.** WXO is IBM-managed: chat HTTP entry, runtime, message routing, LLM call. NEVER recommend inserting middleware on WXO itself or wrapping the WXO runtime. Three legitimate attach points (decision tree in `reference/watsonx-orchestrate-integration.md`):
- Approach 1 — Tool-level wrapping: wrap `@tool()` function bodies. Most flexible. Reference: `examples/wxo_tool_wrapper.py`.
- Approach 2 — Service-layer middleware: FastAPI/Flask middleware on the partner-owned service tools call. Best for RAG-heavy. Reference: `examples/wxo_service_middleware.py`.
- Approach 3 — Frontend BFF: only if partner has a custom UI in front of WXO.
- Production deployments often combine #1 + #3 (defense in depth).

---

## Phased Workflow

### Phase 1 — Setup & verify (~15 min)

**Goal:** working `GuardrailsEvaluator` returning scored results from real watsonx.governance.

**Prerequisite check (ask first):**
- Python 3.11–3.13 available? (`python3 --version`) — RULE 3
- IBM Cloud account with watsonx.governance subscription? — RULE 1
- (Optional) watsonx.ai project for LLM-judge metrics? — RULE 2

**Steps:**

1. **Install:** `pip install real-time-guardrails[all]` — RULE 4
2. **Provision IBM Cloud services** (skip if done):
   - watsonx.governance: IBM Cloud console → Catalog → "watsonx.governance" → Create
   - (Optional) watsonx.ai: https://dataplatform.cloud.ibm.com → Projects → New project → Manage → Services and Integrations → Associate Watson Machine Learning
3. **Set credentials safely** — RULE 1:
   ```bash
   cd <project-root>
   cat > .env <<'EOF'
   WATSONX_APIKEY=
   WXG_SERVICE_INSTANCE_ID=
   WXG_PROJECT_ID=
   EOF
   chmod 600 .env
   read -s -p "API key: " key && printf 'WATSONX_APIKEY=%s\n' "$key" >> .env && unset key
   ```
4. **Sanity check:**
   ```python
   from real_time_guardrails import GuardrailsEvaluator
   ev = GuardrailsEvaluator()
   print("metrics:", ev.list_metrics()["total"])    # 28 (or 25 if no WXG_PROJECT_ID)
   r = ev.evaluate(input_text="My SSN is 123-45-6789", metrics=["PII Detection"])
   print(r["PII Detection"].score, r["PII Detection"].action)
   ```

**Success criteria:** `metrics: 28` (or 25); PII Detection scores 0.6-0.9 with action="Block".

**For credential errors and IBM Cloud UI navigation, load `reference/setup-and-credentials.md`.**

### Phase 2 — Design integration (~30 min)

**Goal:** one decision per choke point — which metrics, which thresholds, which fallback message.

**Steps:**

1. **Map the 4 choke points to the agent** — RULE 9. WHERE in partner's code does query arrive? Where is the retriever call? Where is the LLM call? Skip choke points that don't apply.
2. **Enumerate WILL RUN vs WILL BE SKIPPED** — RULE 18. Look up partner's data shape in the field availability matrix.
3. **Pick metric set per choke point:**

   | Choke point | Recommended |
   |---|---|
   | Input | `categories=["safety", "pattern"]` + `Topic Relevance` if `system_prompt` available |
   | Retrieval | `categories=["rag_retrieval"]` with `context=list[str]` |
   | Generation | `categories=["rag_generation"]` |
   | Output | `metrics=["Output PII Detection", "Output HAP Detection", "Harm", "Profanity", "Social Bias", "Conciseness (LLM Judge)"]` on `generated_text`. **Two patterns at this choke point:** (1) for PII and HAP, use the explicit `Output *` names — the un-prefixed `PII Detection` / `HAP` are wired to the SDK's input-scanning classes. (2) For the other safety metrics (Harm, Profanity, Social Bias, Violence, Jailbreak Detection, Unethical Behavior, Sexual Content, Evasiveness), **same metric name works for input OR output** — the wrapper routes the metric to whichever field the partner populated. See `reference/metrics-catalog.md` "Field routing for single-field safety metrics" for the full rules. |

4. **Decide threshold policy** — RULE 8. Defaults: Safety block=0.65 flag=0.4; RAG block=0.1 flag=0.3. Strict (healthcare/finance/legal): tighten Safety block to 0.5, RAG block to 0.2. Permissive (consumer chat): loosen Safety block to 0.8, RAG block to 0.05.
5. **Write fallback messages** for each Block scenario.
6. **Custom metric needed?** Only if the catalog can't cover a domain-specific concern after tuning. See `reference/custom-metric-authoring.md`.

**Success criteria:** partner has a written (choke point → metrics → thresholds → fallback) row per metric.

**For metric definitions, field requirements, and the field availability matrix, load `reference/metrics-catalog.md`. For per-choke-point code samples, load `reference/integration-patterns.md`.**

### Phase 3 — Implement (~60 min)

**Goal:** working guardrailed agent in the partner's codebase.

**Steps:**

1. **Choose trigger pattern** — RULE 17. Explicit wiring (partner writes per-choke-point calls) OR auto-trigger (HTTP middleware / Python decorator / framework callback). Pick exactly ONE auto-trigger pattern.
   - **If on watsonx Orchestrate (WXO):** RULE 19 — ignore the generic middleware tree. Use the 3-approach decision tree in `reference/watsonx-orchestrate-integration.md`.
2. **For explicit wiring (Python agent):** copy `examples/full_pipeline.py` (`GuardrailedAgent` class). Replace `simulate_retrieve` → partner's vector store; `simulate_model` → partner's LLM client.
3. **For auto-trigger:** pick the reference matching the topology:
   - FastAPI/Flask service → `examples/middleware_fastapi.py` / `examples/middleware_flask.py`
   - Monolithic Python function → `examples/decorator_example.py` (`@guard` decorator)
   - LangChain/LangGraph → `examples/langchain_callback.py` (callback for input + `RunnableLambda` for output — stock callbacks can't block output)
4. **For non-Python agents or shared-service:** REST mode — `real-time-guardrails serve --port 8090`. Request/response shape in `reference/integration-patterns.md`.
5. **For chat-widget frontends:** backend-proxy pattern — RULES 14, 15. Browser → partner backend (session auth) → guardrails. Reference: `examples/frontend_chat_integration.jsx` + `examples/backend_guardrails_proxy.py`. See `reference/frontend-integration.md`.
6. **Wire audit log** — RULE 11:
   ```python
   from real_time_guardrails import AuditLogger
   audit = AuditLogger(path="/var/log/guardrails/audit.jsonl")
   # or: AuditLogger(sink=lambda rec: splunk_client.send(rec))
   ```
   Build evaluator AND logger ONCE at startup — RULE 16.
7. **Handle each action** — RULE 10:
   - Block → return `result.fallback_message` (don't leak metric details — RULE 14)
   - Flag → allow + log to audit (AuditLogger does this)
   - Pass → serve the response

**Success criteria:** every choke point is wired; every decision recorded in audit log; Block returns fallback message; auto-trigger pattern is consistent (no mixing — RULE 17).

**For auto-trigger details (pre/post-hook mechanics, fail-open vs fail-closed, anti-patterns), load `reference/auto-trigger-patterns.md`.**

### Phase 4 — Test & tune (~30 min)

**Goal:** threshold policy validated against a representative workload.

**Steps:**

1. **Run agent against 10-50 sample requests**, capture audit log.
2. **Analyze JSONL:**
   ```bash
   # Block rate per metric
   jq -r '.metrics | to_entries[] | select(.value.action=="Block") | .key' audit.jsonl | sort | uniq -c

   # Flag rate (borderline content)
   jq 'select(.overall_action=="Flag") | {request_id, flagged_metrics, input_hash}' audit.jsonl
   ```
3. **Tune thresholds** — RULE 8. Too many false-positive blocks → loosen. Too few flags → tighten. Persist in YAML or env vars.
4. **Re-run** until action distribution matches partner's tolerance.

**Success criteria:** block rate in partner's target range; zero unexpected `None` scores (verify RULE 5 + RULE 6 compliance).

**For audit log schema, jq query patterns, and dashboard aggregation snippets, load `reference/audit-and-observability.md`.**

### Phase 5 — Deploy & observe (~45 min)

**Goal:** guardrails running in production with observability.

**Steps:**

1. **Deploy** — pick one mode:
   - **Library**: pip-install into agent container. Lowest latency. Python-only.
   - **REST**: Dockerize using the source SDK's Dockerfile (lives in the building-blocks repo at `ai-trust/real-time-guardrails/assets/sdk/Dockerfile`, not bundled with this skill). `real-time-guardrails serve --port 8090`. Co-locate with agent in same VPC.
   - **MCP**: register as MCP tool in agent's config.
2. **Wire audit to log aggregation:**
   ```python
   audit = AuditLogger(sink=lambda rec: splunk_client.send_event("guardrails", rec))
   # or: AuditLogger(sink=lambda rec: elastic_client.index(index="guardrails", document=rec))
   ```
3. **Build partner-facing compliance dashboard.** Reference: `examples/dashboard_skeleton.jsx` (MUI). Reads `/api/audit/recent` from `examples/backend_guardrails_proxy.py`. Polls every 30s; swap to SSE/WebSockets if sub-second latency needed.
4. **Set up production ops dashboards** (separate from compliance UI): block/flag rate per metric, p50/p95 latency per choke point, LLM-judge token spend (if enabled — RULE 12).
5. **Egress check:** outbound HTTPS to `*.ml.cloud.ibm.com` + watsonx.governance service URL. Air-gapped deployments NOT supported.

**Success criteria:** guardrails deployed; audit streaming to partner's log aggregation; dashboards live.

**For deployment modes (library / REST / MCP), Dockerfile, K8s, multi-tenant patterns, and the production checklist, load `reference/deployment.md`.**

---

## Reference Material Map

Load on demand when the conversation enters that topic:

| When user asks about… | Load |
|---|---|
| credential setup, IBM Cloud UI, env var errors | `reference/setup-and-credentials.md` |
| 4-choke-point code samples (lib / REST / Node / MCP) | `reference/integration-patterns.md` |
| full 28-metric catalog, thresholds, field availability matrix, per-partner policy | `reference/metrics-catalog.md` |
| AuditLogger usage, JSONL schema, sink injection, dashboard aggregation | `reference/audit-and-observability.md` |
| Dockerfile, K8s, REST vs MCP trade-offs, multi-tenant, production checklist | `reference/deployment.md` |
| authoring custom LLM-judge metrics, replacing built-in judges | `reference/custom-metric-authoring.md` |
| chat widget topology, anti-patterns, UX per action | `reference/frontend-integration.md` |
| auto-trigger patterns (middleware / decorator / callback), pre/post-hook mechanics, fail-open/closed | `reference/auto-trigger-patterns.md` |
| watsonx Orchestrate integration (Approach 1/2/3), WXO pitfalls | `reference/watsonx-orchestrate-integration.md` |

## Example Code Map

**Prefer ADAPTING these canonical examples rather than recreating from scratch.** Pick the closest match to the partner's topology, copy it, then modify — this prevents drift from working patterns and protects against subtle bugs (build-once evaluator placement, OpenAI tool-spec format, choke-point ordering, audit-log wiring).

Working reference payloads in `examples/`:

| File | Purpose |
|---|---|
| `full_pipeline.py` | `GuardrailedAgent` class — 4-choke-point explicit wiring |
| `middleware_fastapi.py` / `middleware_flask.py` | HTTP middleware auto-trigger |
| `decorator_example.py` | `@guard` decorator auto-trigger |
| `langchain_callback.py` | LangChain callback + `RunnableLambda` |
| `wxo_tool_wrapper.py` | WXO Approach 1 (tool-level wrapping) |
| `wxo_service_middleware.py` | WXO Approach 2 (service-layer middleware) |
| `frontend_chat_integration.jsx` | React chat widget |
| `backend_guardrails_proxy.py` | Flask backend proxy (used by chat widget + dashboard) |
| `dashboard_skeleton.jsx` | MUI compliance dashboard |
| `custom_metric_example.py` | Both LLM-judge authoring styles |
| `audit_log_sample.jsonl` | Sample audit log records |
| `input_safety.json` / `rag_generation.json` / `rag_retrieval.json` / `pattern_keywords.json` / `tool_call.json` | Sample request payloads (REST mode) |

## Asset Map

- `assets/env.example` — env var template with explanations
- `assets/thresholds.example.yaml` — per-metric + category-level threshold config example
