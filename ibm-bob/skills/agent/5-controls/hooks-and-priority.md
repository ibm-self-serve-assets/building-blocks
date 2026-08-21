# Domain 5 — Controls: Hooks and Priority

> **ADK version**: 2.15.0

---

## Available hooks

| Hook | Asset type | Fires when... |
|---|---|---|
| `agent_pre_invoke` | agent | **Before** the LLM processes the user message |
| `agent_post_invoke` | agent | **After** the LLM generates its response, before delivery to user |
| `tool_pre_invoke` | tool | **Before** the tool function executes |
| `tool_post_invoke` | tool | **After** the tool returns its result to the LLM |
| `prompt_pre_fetch` | agent | Before a system prompt template is retrieved |
| `prompt_post_fetch` | agent | After a system prompt template is retrieved |

---

## Execution flow diagram

```
User message
     │
     ▼
[agent_pre_invoke controls]  ← Runs in priority order (lowest first)
     │
     ▼
   LLM processes input
     │
     ├──── calls tool ────▶ [tool_pre_invoke controls]
     │                              │
     │                         tool executes
     │                              │
     │                      [tool_post_invoke controls]
     │                              │
     ◀──── tool result ────────────-┘
     │
     ▼
   LLM generates response
     │
     ▼
[agent_post_invoke controls] ← Runs in priority order (lowest first)
     │
     ▼
 User sees response
```

---

## Priority rules

- **Lower number = runs first** (default 100)
- Controls with the **same priority** run in insertion order
- **Priority 1** is the highest — use for blocking controls (guardrails, jailbreak)
- **Priority 50-90** — redaction and masking
- **Priority 100** (default) — logging and monitoring
- **Priority 200+** — non-critical / informational

### Recommended priority assignments

| Use case | Recommended priority |
|---|---|
| Jailbreak / content safety blocking | 1–10 |
| Secrets detection (block mode) | 5–15 |
| PII masking (redact) | 20–50 |
| Regex pattern filtering | 30–60 |
| Output length enforcement | 80–100 |
| Rate limiting | 100 |
| Audit logging only | 100–200 |

---

## Hook selection guide

### "I want to screen what the user sends"
```
hook: agent_pre_invoke
```
Examples: jailbreak detection, PII masking of input, secrets detection on user message.

### "I want to screen what the agent replies"
```
hook: agent_post_invoke
```
Examples: PII masking of output, output length guard, content safety on agent response.

### "I want full double-guard (both directions)"
```
hook: agent_pre_invoke
hook: agent_post_invoke
```
Use: most safety and privacy controls should run on both.

### "I want to protect tool inputs (arguments from LLM)"
```
hook: tool_pre_invoke
```
Examples: SQL sanitizer on a database tool, rate limiter before tool executes.

### "I want to sanitize what a tool returns to the LLM"
```
hook: tool_post_invoke
```
Examples: secrets detection on tool output, output length guard on large tool results.

### "I want to intercept prompt template fetching"
```
hook: prompt_pre_fetch   # before the template is retrieved
hook: prompt_post_fetch  # after the template is retrieved
```
Less common; useful for prompt injection protection in RAG scenarios.

---

## Multi-control ordering example

This shows how three controls on the same agent interact at `agent_pre_invoke`:

```
agent_pre_invoke hook on "test_DA"
  │
  ├── [priority=1]   jailbreak-guard     (Guardrails, blocks if jailbreak detected)
  │
  ├── [priority=10]  secrets-blocker     (SecretsDetection, blocks if API key found)
  │
  ├── [priority=50]  pii-redactor        (pii_filter, redacts email/SSN/phone)
  │
  └── [priority=100] audit-logger        (pii_filter with log_detections only)
```

If `jailbreak-guard` **blocks**, controls 2–4 do not execute.

---

## Updating hooks on existing controls

`--hook` in `update` **replaces** all existing hooks — it does not append.

```bash
# Add agent_post_invoke to a control that only had agent_pre_invoke
orchestrate controls update \
  --name my-pii-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke   # must re-specify pre_invoke too
```

---

## Viewing hooks on a control

```bash
# Summary view
orchestrate controls list

# Full hook list + config
orchestrate controls get-details -n my-pii-guard -v
```

The `hooks` field in JSON output:
```json
{
  "hooks": [
    "agent_pre_invoke",
    "agent_post_invoke"
  ]
}
```

---

## Common mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Creating without `--hook` | `422 Unprocessable Entity` | Always include at least one `--hook` |
| Setting only `agent_post_invoke` | Input not protected | Add `agent_pre_invoke` too |
| Low priority on a redact-only control | Blocker runs after redactor (wasted cycles) | Blockers should always have lower priority numbers than redactors |
| Using `tool_pre_invoke` on agent artifact | Silently mis-bound or ignored | Check artifact `asset_type` with `get-type -v` |
