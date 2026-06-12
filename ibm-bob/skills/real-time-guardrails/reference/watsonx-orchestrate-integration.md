# watsonx Orchestrate (WXO) Integration

**TRIGGER:** Load when partner says "I'm using watsonx Orchestrate", "I have a WXO agent", or mentions `@tool()` decorators, the `orchestrate` CLI, or watsonx Agent Builder. Also load when partner asks "how do I add guardrails to a managed agent platform" or describes a WXO-specific topology.

---

## WXO topology

### IBM-managed (partner CANNOT attach guardrails here)
- The chat HTTP endpoint that receives user messages
- The WXO runtime that orchestrates tool calls and conversation memory
- The LLM invocation (model selection, prompting, response generation)
- Message routing between user, agent, and tools

### Partner-owned (guardrails attach HERE)
- The Python files containing `@tool()` decorated functions (in `agents/tools/`)
- Any external services those tools call (FastAPI/Flask retrieval servers, REST APIs, databases via wrapper services)
- Any custom frontend (BFF) that sits in front of WXO's chat API (uncommon — most partners use WXO's built-in UI)

---

## Anti-patterns (CRITICAL)

### Trying to wrap the WXO runtime
**BAD:** inserting middleware on WXO's HTTP endpoint, modifying WXO's source code, registering a "global guardrails callback" with WXO.

**WHY:** WXO is a managed service. The runtime is not partner code. There's no public hook for runtime-level interception.

**CORRECT:** attach guardrails at partner-owned boundaries (tools, external services, or frontend BFF). Use the decision tree below.

### Confusing WXO with watsonx Assistant
**NOTE:** watsonx Orchestrate ≠ watsonx Assistant. Patterns documented here apply to Orchestrate (`@tool()` decorators, agent YAML files, `orchestrate` CLI). Assistant is a different product with different integration patterns.

---

## DECISION tree — pick approach 1, 2, or 3

Bob MUST run through this BEFORE recommending. Different topologies need different integration points.

**Q1:** Does the agent have a custom frontend (BFF) in front of WXO?
- **Yes** → **Approach 3 (frontend BFF)**. Use pattern in `reference/frontend-integration.md` + `examples/backend_guardrails_proxy.py`. BFF sees the original user message AND the final agent response — best for production customer UX. Often combined with #1 for defense in depth.
- **No (uses WXO's built-in chat UI/CLI)** → continue.

**Q2:** Does most of the agent's "work" happen in ONE retrieval or external service the partner owns?
- **Yes** → **Approach 2 (service-layer middleware)**. Attach FastAPI/Flask middleware on that service. Reference: `examples/wxo_service_middleware.py`. Best for RAG-heavy agents where bulk of safety/quality concerns live in retrieval.
- **No (tools call multiple services, or do work inline)** → continue.

**Q3:** Does the agent use diverse tools (DB queries, calculations, email, multiple APIs)?
- **Yes** → **Approach 1 (tool-level wrapping)**. Wrap each `@tool()` function body. Reference: `examples/wxo_tool_wrapper.py`. Most comprehensive. Each tool can have own policy.
- **No (single retrieval tool, or simple tool set)** → **Approach 1 (default for WXO)**. Tool wrapping works for any tool count; more work as count grows.

### Combinations

- **Defense in depth: 1+3.** Tool wrapping (in-depth coverage of agent behavior) + frontend BFF (end-to-end coverage of user-facing UX). Avoid double-blocking by having BFF skip metrics already enforced at tool layer.
- **RAG + UX: 2+3.** Service middleware (retrieval quality) + frontend BFF (final output safety).

---

## Approach 1 — Tool-level wrapping

**Where:** inside the body of each `@tool()` decorated function in `agents/tools/*.py`.

**Reference:** `examples/wxo_tool_wrapper.py`.

### Pros
- 100% partner-owned code — no infrastructure changes
- Per-tool policy granularity (different metrics for retrieval vs email vs DB)
- Audit log centralized in one Python module
- Push with `orchestrate tools import -k python -f tool_file.py` — fast iteration

### Cons
- Scales linearly with tool count (each tool needs wrapping)
- Partner has to remember to wrap new tools as added
- Only sees what the tool sees — can't observe WXO's between-tool reasoning

### Choke point mapping
- **Input:** top of tool function body. Field: tool's query arg → `input_text`.
- **Retrieval:** after tool's retrieval call, before formatting return value. Field: retrieved docs → `context` (list[str]).
- **Output:** right before the `return`. Field: formatted text agent will see → `generated_text`.
- **Generation faithfulness CAVEAT:** LLM lives inside WXO. Partner can check faithfulness of tool's output against retrieved context (tool wrote summary of docs that should be faithful), but CANNOT check faithfulness of WXO's final answer against tool's output.

### Field shape translation
| WXO concept | Our SDK field |
|---|---|
| query arg of tool | `input_text` |
| tool's str return value | `generated_text` |
| retrieved docs (if RAG) | `context` (str for generation; list[str] for retrieval-quality) |

**NOTE:** WXO tools always take and return strings. Map these to our SDK fields explicitly per tool.

### Build evaluator
**Where:** module-level (RULE 16). NOT per-tool-call.
```python
# Top of agents/tools/your_tools.py
from real_time_guardrails import GuardrailsEvaluator, AuditLogger
_ev = GuardrailsEvaluator()                            # built once at import
_audit = AuditLogger(path="/var/log/wxo_audit.jsonl")  # or sink=...
```

---

## Approach 2 — Service-layer middleware

**Where:** FastAPI/Flask middleware on the partner-owned service tools call (NOT on WXO itself).

**Reference:** `examples/wxo_service_middleware.py`. Related: `examples/middleware_fastapi.py` / `examples/middleware_flask.py` for underlying FastAPI/Flask mechanics.

### Pros
- Single attachment point catches every caller (not just tool-mediated)
- One middleware function covers all of the service's endpoints
- Useful when service has multiple consumers (other apps calling `/retrieve` in addition to the WXO agent)

### Cons
- Only sees the tool's call to THIS service — if agent has tools that call other services or do work inline, those are uncovered
- The "input" middleware sees is the tool's request body — NOT necessarily user's original message (tool may have rewritten the query)
- Requires rebuilding the service container + updating deployment manifests

### Field shape translation
| Source | Our SDK field |
|---|---|
| request body's `query` field | `input_text` (may be user's original OR tool-rewritten — document partner's tool behavior so Bob can decide which safety metrics make sense) |
| service's response text or formatted result | `generated_text` |
| if service returns retrieved docs in response | `context` (list[str]) — run RAG retrieval guardrails BEFORE returning to tool |

### Retrieval-specific note
For RAG retrieval services: after service computes results but BEFORE returning to tool, run `rag_retrieval` metrics on `input_text=query, context=[doc.text for doc in results]`. If HitRate=0, middleware can return a "no relevant info" response instead of letting tool serve noise to the agent.

### Block response shape
On a Block, middleware must return a JSON body that the tool can still parse. Reference payload returns:
```json
{"results": [], "guardrail_action": "Block", "guardrail_reason": "..."}
```
with HTTP 200. Tool sees `results: []` and naturally serves its existing "no relevant information found" path to the agent — no changes needed in `@tool()` code. If tool ALSO inspects `guardrail_action`, it can surface a more specific message; not required.

**TELL PARTNERS UP FRONT:** middleware does NOT break tool code on Block; it just makes tool's empty-results path fire.

### Deployment targets
**Code Engine (common for WXO partners):**
```bash
ibmcloud ce app create --name retrieval-with-guardrails \
  --image <your-image> \
  --env WATSONX_APIKEY=... \
  --env WXG_SERVICE_INSTANCE_ID=... \
  --env WXG_PROJECT_ID=...
```
**Audit log note:** Code Engine has ephemeral filesystem. Use `AuditLogger(sink=...)` writing to IBM Cloud Logs / Splunk / ELK rather than `path=...`.

**Kubernetes:** existing pattern in `reference/deployment.md`. Secrets via K8s Secret manifest; ConfigMap for non-secret config.

---

## Approach 3 — Frontend BFF

**Where:** backend-for-frontend service in front of WXO's chat API. Partner's frontend talks to BFF; BFF talks to WXO and runs guardrails on the way in/out.

**Reference:** `examples/frontend_chat_integration.jsx`, `examples/backend_guardrails_proxy.py`, `reference/frontend-integration.md`.

### When applicable
ONLY when partner has a custom frontend in front of WXO. If partner uses WXO's built-in chat UI/CLI, this approach doesn't apply — point them at Approach 1 or 2.

### Pros
- Sees ORIGINAL user message + final agent response — best end-to-end coverage
- Works for any WXO agent regardless of tool composition
- Controls customer-facing UX (fallback messages, flag badges) directly

### Cons
- Requires partner to build a BFF (extra infrastructure)
- Doesn't see retrieval quality unless BFF observes tool calls (hard)
- Can't catch issues that happen mid-agent between tool calls

---

## Testing workflow

WXO is a managed service — partners can't run it locally. Each approach has a different test strategy.

### Approach 1
1. Develop wrapped `@tool()` function in `agents/tools/your_tool.py`
2. Unit-test wrapper logic locally with mocked `GuardrailsEvaluator` (use `unittest.mock` to stub `evaluate()` responses for known-good and known-bad inputs)
3. Push to WXO: `orchestrate tools import -k python -f your_tool.py`
4. End-to-end test: `orchestrate agents chat --name <agent>` and try scenarios that should be blocked / flagged / passed
5. Inspect audit log for evidence wrappers fired correctly

### Approach 2
1. Standard FastAPI test client (or Flask equivalent) — see `examples/middleware_fastapi.py`
2. Runs entirely locally — no WXO interaction needed for unit testing middleware
3. For end-to-end: push updated service container to Code Engine/K8s, then `orchestrate agents chat` to confirm tool calls go through middleware correctly

### Approach 3
Same as `reference/frontend-integration.md`'s testing — local Flask test client for BFF, then browser-driven E2E.

---

## WXO-specific pitfalls

| Pitfall | Description |
|---|---|
| **`ibm_watsonx_orchestrate` SDK required** | The `@tool()` decorator comes from `ibm_watsonx_orchestrate.agent_builder.tools` (NOT a generic Python decorator). Install the SDK in the same Python environment as the tool wrappers. |
| **Tool function signatures matter** | WXO inspects function signature to expose tool to agent. When wrapping a tool, preserve original signature (parameters, type hints, docstring) — these become the tool's API surface in the agent's reasoning. |
| **Re-pushing tools requires explicit command** | Editing a tool file locally does NOT auto-push to WXO. Re-run `orchestrate tools import -k python -f <file>` for every change. Document in workflow. |
| **Environment secrets management** | Tools run on Code Engine or K8s (depending on WXO platform deployment). Inject `WATSONX_APIKEY` etc. into THAT runtime, NOT into WXO itself. Code Engine: `ibmcloud ce app update --env`. K8s: Secret manifest. |
| **Audit log destination on managed runtime** | Tools running on Code Engine have ephemeral filesystems — local file audit logs vanish on container restart. Use `AuditLogger(sink=...)` writing to IBM Cloud Logs / Splunk / ELK, OR mount a persistent volume. |
