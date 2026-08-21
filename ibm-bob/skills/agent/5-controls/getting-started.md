# Domain 5 — Controls: Getting Started

> **ADK version**: 2.15.0 · **Verified live against**: `ibm_cloud` env

Controls let you attach **policy artifacts** to agents, tools, and models — enforcing safety,
privacy, rate limits, and model resilience without changing agent code.

---

## 🔀 Three paths into controls

When a user mentions controls, guardrails, PII filtering, or content safety, first identify which path applies:

---

### 🛤️ Path A — Building a new agent: Controls Recommendation Engine

The agent build (Domain 1) is complete. **Before presenting final deliverables**, run the Controls Recommendation Engine — do not ask a generic yes/no question. Instead, analyse what was built and make specific recommendations.

---

#### Step 1 — Analyse what was built

Look at the agent's purpose, instructions, tools, and data to answer these questions:

| Signal | Controls to consider |
|---|---|
| Agent is **user-facing / public-facing** | `Content Guardrails` (jailbreak + HAP + harm) — always |
| Agent handles **employee data, HR, finance, health** | `PII Filter` (SSN, email, phone, DOB, bank, medical) |
| Agent handles **code, configs, or developer workflows** | `Secrets Detector` (AWS keys, JWTs, private keys) |
| Agent calls **database tools** | `SQL Sanitizer` on the tool |
| Agent calls **external APIs at high volume** | `Rate Limiter` on the tool |
| Agent **generates long outputs** (reports, code, docs) | `Output Length Guard` |
| Agent uses **custom terminology / confidential project names** | `Regex Pattern` (redact internal codes) |
| Agent relies on **a specific model** in production | `Fallback` or `Retry` model controls |

---

#### Step 2 — Present recommendations to the user

Format your recommendation like this:

```
Based on the agent I just built, here are the policy controls I recommend:

✅ Content Guardrails [RECOMMENDED]
   Blocks jailbreak attempts, harmful content, and hate/abuse/profanity.
   Why: All user-facing agents should have this as a baseline.

✅ PII Filter [RECOMMENDED]
   Redacts email addresses and phone numbers from inputs and outputs.
   Why: [reason specific to this agent's purpose]

⚪ Secrets Detector [OPTIONAL]
   Detects and redacts AWS keys, JWTs, and private key blocks.
   Why: Only needed if users might paste credentials into this agent.

⚪ Output Length Guard [OPTIONAL]
   Truncates responses over 5000 characters.
   Why: Consider this if the agent generates long structured outputs.

Would you like me to add any of these? You can say:
- "Add all recommended" → I'll generate all ✅ controls
- "Add content guardrails and PII filter" → I'll generate specific ones
- "Skip for now" → I'll wrap up the agent files as-is
```

---

#### Step 3 — Generate controls (if user says yes)

> ⚠️ **Controls are NEVER embedded in the agent YAML.** The agent YAML `plugins` field is a separate built-in plugin system. Controls are always **standalone resources** imported via `orchestrate controls import` and bound to agents by display name.

For each control the user selects, generate a separate YAML file using the correct schema:

```yaml
spec_version: v1
kind: control
control:
  artifact_name: Content Guardrails    # display name from list-types
  name: <agent_name>_content_guardrails
  hooks:
    - agent_pre_invoke
    - agent_post_invoke
  priority: 1
  config:
    enabled:
      jailbreak: true
      hap: true
      harm: true
    block_message: Content blocked by guardrails controls
  agent_names:
    - <agent display_name>             # must match agent's display_name exactly
```

Add the import commands to `deploy.sh`:
```bash
# Import controls (run after agent import)
orchestrate controls import -f controls/content_guardrails.yaml
orchestrate controls import -f controls/pii_filter.yaml
```

And verify with:
```bash
orchestrate controls list --agent "<agent-display-name>"
orchestrate controls count
```

---

### 🛤️ Path B — Controls only (no agent building)

The user wants to **create and push controls directly** to an existing WXO instance, without building a new agent.

**What to do:**

1. Run the discovery questionnaire (below)
2. Generate the CLI commands and/or import YAML files
3. Instruct the user to run them — do not execute directly

**Jump to**: [Discovery questionnaire](#discovery-questionnaire) → [cli-reference.md](cli-reference.md) → [recipes.md](recipes.md)

---

### 🛤️ Path C — Agent already exists, add controls to it

The user has an **existing agent already deployed in WXO** and wants to add, update, or remove controls on it.

**What to do:**

1. Ask for the agent name:
   > *"What is the display name of the agent in WXO? (Run `orchestrate agents list` if unsure)"*
2. Check what controls already exist:
   ```bash
   orchestrate controls list --agent "<agent-display-name>"
   orchestrate controls count
   ```
3. Run the discovery questionnaire (below) for the new controls needed
4. Generate `orchestrate controls create` commands or import YAML files
5. If updating an existing control: use `orchestrate controls update` (replace semantics — re-specify all hooks/agents)

**Jump to**: [Discovery questionnaire](#discovery-questionnaire) → [cli-reference.md](cli-reference.md) → [troubleshooting.md](troubleshooting.md)

---

## Discovery questionnaire

Ask these questions before writing any control:

```
1. What asset are you protecting?
   a) An agent (input / output guardrails, PII, regex, secrets, output-length)
   b) A tool (guardrails, output-length, secrets, SQL sanitizer, rate limiter)
   c) A model (fallback, load-balance, retry)

2. What is the risk you want to mitigate?
   a) Harmful / unsafe content (jailbreak, HAP, violence, sexual, bias)
   b) PII leakage (SSN, email, phone, credit-card, bank account…)
   c) Secret / credential exposure (AWS keys, JWTs, private keys…)
   d) Runaway output length (cost, context-window overflow)
   e) SQL injection through tool inputs
   f) Tool call rate spikes
   g) Model availability (rate limits / provider outages)

3. Block or redact?
   — Block: reject the call with an error message
   — Redact: let it through but replace matched content with [REDACTED]

4. When does the control fire?
   — Before the LLM sees the input  → agent_pre_invoke
   — After the LLM generates output → agent_post_invoke
   — Both (double-guard)
   — Before a tool runs             → tool_pre_invoke
   — After a tool returns           → tool_post_invoke
   — Before a prompt is fetched     → prompt_pre_fetch
   — After a prompt is fetched      → prompt_post_fetch

5. Which agent / tool / model should it apply to?
   (Provide the display name shown in 'orchestrate agents list')

6. Priority? (lower = runs first; default 100)
   Use priority 1-10 for blocking controls, 50-90 for redaction, 100+ for logging.
```

---

## Minimal viable control — 3 commands

```bash
# 1. See what artifact types are available
orchestrate controls list-types

# 2. Create a PII filter on your agent
orchestrate controls create \
  --artifact "PII Filter" \
  --name my_pii_control \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --config '{"detect_email":true,"detect_phone":true,"default_mask_strategy":"redact"}' \
  --agent "my-agent"

# 3. Verify it applied
orchestrate controls list
orchestrate controls count
```

**Or import from a YAML file** (recommended for version control):
```bash
orchestrate controls import --file pii-filter.yaml
```

---

## Asset-type capability matrix

| Artifact | Agent | Tool | Model |
|---|---|---|---|
| `Content Guardrails` | ✅ | ✅ | ❌ |
| `PII Filter` | ✅ | ❌ | ❌ |
| `Secrets Detector` | ✅ | ✅ | ❌ |
| `Regex Pattern` | ✅ | ❌ | ❌ |
| `Output Length Guard` | ✅ | ✅ | ❌ |
| `SQLSanitizer` | ❌ | ✅ | ❌ |
| `Rate Limiter` | ❌ | ✅ | ❌ |
| `Fallback` | ❌ | ❌ | ✅ |
| `Load Balance` | ❌ | ❌ | ✅ |
| `Retry` | ❌ | ❌ | ✅ |

> Use the **Display Name** column from `orchestrate controls list-types` as the `--artifact` value.
> Internal names (e.g. `pii_filter`, `Guardrails`) also work.

---

## Hook selection cheat-sheet

| Goal | Hook(s) |
|---|---|
| Screen user input before LLM sees it | `agent_pre_invoke` |
| Screen LLM output before user sees it | `agent_post_invoke` |
| Full double-guard (both directions) | `agent_pre_invoke` + `agent_post_invoke` |
| Sanitize arguments before tool executes | `tool_pre_invoke` |
| Sanitize tool results before LLM sees them | `tool_post_invoke` |
| Intercept system-prompt fetch | `prompt_pre_fetch` / `prompt_post_fetch` |

---

## Naming conventions

```
<agent-shortname>_<artifact-shortname>

Examples:
  pii_filter_guard           # PII filter on an agent
  billing_sql_sanitizer      # SQL sanitizer on a billing tool
  gpt4_fallback              # Fallback policy on GPT-4 model
```

> Use `snake_case` — IBM's non-negotiable naming standard for all WXO assets.

---

## Common pitfalls before you start

| Pitfall | Fix |
|---|---|
| `--agent` takes **display_name**, not agent ID | Run `orchestrate agents list` to confirm the display name |
| Creating without `--agent`/`--tool`/`--model` | Control is created but **unbound** — `count` shows 0 |
| `orchestrate` resolves to system 2.8.0 binary | Activate venv: `source venv/bin/activate` |
| `422 Unprocessable Entity` on create | Add `--hook` — at least one hook is required |
| YAML uses `artifact:` instead of `artifact_name:` | Import YAML must use `artifact_name:` inside the `control:` block |
| YAML uses `agents:` instead of `agent_names:` | Import YAML must use `agent_names:`, `tool_names:`, `model_names:` |

---

## Next steps

- **[cli-reference.md](cli-reference.md)** — every flag for all 10 commands
- **[artifact-types.md](artifact-types.md)** — full config schemas with defaults
- **[hooks-and-priority.md](hooks-and-priority.md)** — execution order deep-dive
- **[recipes.md](recipes.md)** — copy-paste patterns for common scenarios
- **[import-export.md](import-export.md)** — YAML file format + bulk deployment
- **[troubleshooting.md](troubleshooting.md)** — error codes and fixes
