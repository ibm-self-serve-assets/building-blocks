# Frontend Integration (Chat Widgets)

**TRIGGER:** Load when partner is building a chat / form / SPA frontend that needs guardrails on user input and agent output, asks about backend proxy patterns, mentions `WATSONX_APIKEY` in browser bundles, asks about localStorage for audit, or asks about UX per Pass/Flag/Block action.

---

## Integration topology — 4 tiers

| Tier | Component | Responsibilities | Must NOT |
|---|---|---|---|
| 1 | **Browser (chat widget)** | Render UI. Generate per-request correlation ID. Show fallback on Block. Show "flagged for review" badges on Flag (if relevant to partner UX). | Hold `WATSONX_APIKEY`. Persist audit to localStorage. Call guardrails REST endpoint directly. |
| 2 | **Partner backend (proxy)** | Authenticate browser session (cookie/JWT). Call guardrails. Write to AuditLogger. Apply per-tenant policy. Implement fail-open/closed. Strip/sanitize before returning. | — |
| 3 | **Guardrails service (REST)** | Run the 28-metric evaluation. Return scored JSON. | — |
| 4 | **IBM Cloud (Granite Guardian + watsonx.ai)** | SaaS-managed by IBM. Partner doesn't operate these. | — |

---

## Why backend proxy is MANDATORY (RULES 14, 15)

1. **`WATSONX_APIKEY` must never reach the browser.** Browser bundle is public; anyone can read it. Direct browser → guardrails-service calls leak IBM Cloud creds even if the service is private.
2. **Audit log lives server-side.** localStorage is not durable, not joinable across users, not compliant with retention regulations, not tamper-evident.
3. **Per-tenant policy lookup is a backend concern.** Browser doesn't know — and shouldn't know — that tenant Acme has different PII thresholds than tenant Globex.
4. **Fail-open vs fail-closed decisions vary per partner.** Backend can fall back to "allow with flag" when guardrails is down; browser can't make that policy call.

---

## Chat widget event-handler pattern

### Input check (on user message submission)
**Handler:** `onSubmit` / `handlePromptSubmit` / form `onSubmit`

**Flow:**
1. Generate `request_id` (UUID) in browser.
2. POST to `YOUR_BACKEND/chat` with `{query, request_id}`.
3. Backend proxies query → guardrails service for INPUT check.
4. If Block: backend returns `{action: "Block", fallback_message: "..."}`.
5. If Pass/Flag: backend calls the agent, then runs OUTPUT check, then returns the response.
6. Frontend renders fallback message on Block; renders agent response (with optional Flag badge) on Pass/Flag.

### Output check (after agent generates)
**Handler:** **backend-side, before returning to browser** — NOT browser-side.

**Reason:** output checks have to look at the LLM's response. The cleanest place is the backend, in the same request cycle that called the agent. Browser-side output checks (like the demo's `instance.on('receive')`) are a leak vector and harder to make idempotent.

---

## Correlation ID propagation

- **Generate:** frontend generates `request_id = crypto.randomUUID()` once per user message.
- **Propagate:** send as header `X-Request-ID` and in the JSON body. Backend reads it, passes to `AuditLogger` via `request_id=`, and echoes back to browser.
- **Use:** frontend can later query audit log by `request_id` if user disputes a refusal.

---

## UX per action (RULE 14)

| Action | UI |
|---|---|
| **Pass** | Show the agent response normally. No badge, no extra UI. |
| **Flag** | Show the agent response. Optionally show a subtle "flagged for review" badge IF partner's policy is to surface borderline content to the user. Many partners hide Flag from end users and only surface it in the compliance dashboard. |
| **Block** | Replace agent response with `fallback_message`. Don't tell user which metric tripped (that's adversarial intel). Optionally provide a "try rephrasing" hint. |

---

## Anti-patterns to call out

### Anti-pattern: direct browser-to-guardrails calls
**BAD:**
```jsx
// API key exposed in browser bundle
const r = await fetch('https://guardrails.example.com/api/evaluate', {
  headers: { 'X-Api-Key': process.env.REACT_APP_API_KEY }
});
```
**GOOD:**
```jsx
// Route through your own backend, session-authenticated
const r = await fetch('/api/chat', {
  credentials: 'include',  // session cookie
  method: 'POST',
  body: JSON.stringify({query, request_id})
});
```

### Anti-pattern: localStorage for audit trail
**BAD:**
```javascript
// Audit data in localStorage — not durable, not compliant
localStorage.setItem('watsonTransactions', JSON.stringify([...prev, decision]));
```
**GOOD:** audit lives server-side via `AuditLogger`. localStorage is fine for UX state (last-N visible messages, panel collapsed/expanded) but NEVER for compliance-grade records.

### Anti-pattern: exposing internal metric names to end users
**BAD:** `"Blocked: PII Detection score 0.87"`
**GOOD:** `"Your request couldn't be processed. Please rephrase your question."` (the `metric.fallback_message`)

**Reason:** telling adversarial users which metric they tripped helps them iterate around it.

---

## Reference files

- `examples/frontend_chat_integration.jsx` — production-grade React chat widget
- `examples/backend_guardrails_proxy.py` — Flask backend proxy (used by both the chat widget and the compliance dashboard)

---

## See also

- `reference/auto-trigger-patterns.md` — middleware vs decorator vs callback decision tree (the backend proxy itself is often middleware-shaped)
- `reference/audit-and-observability.md` — what the dashboard reads from
