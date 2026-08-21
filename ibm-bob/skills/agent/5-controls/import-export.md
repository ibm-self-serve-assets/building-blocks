# Domain 5 — Controls: Import / Export

> **ADK version**: 2.15.0

Use YAML files to version-control controls, deploy across environments, and manage multiple controls at once.

---

## Export a control

```bash
orchestrate controls export --name <control-name> --output <path.yaml>
```

```bash
# Export the pii_DA control from the live env
orchestrate controls export -n pii_DA -o ./controls/pii_DA.yaml
```

The output is a **valid import file** — you can edit it and re-import.

---

## Import controls

```bash
orchestrate controls import --file <path>
```

```bash
orchestrate controls import -f ./controls/pii-filter.yaml
orchestrate controls import -f ./controls/all-agent-controls.yaml
```

- Accepts **YAML** or **JSON**
- Creates new controls; updating existing ones is not guaranteed — use unique names per env
- Agent/tool/model bindings are resolved by **display name** at import time

---

## YAML file schema

Each file defines **one control** using the standard `spec_version: v1` envelope:

```yaml
spec_version: v1
kind: control
control:
  artifact_name: PII Filter             # display name from 'orchestrate controls list-types'
  name: pii_filter_guard               # internal name — snake_case, must be unique
  display_name: PII Filter Guard       # optional, defaults to name
  description: Redacts PII on my-agent # optional
  hooks:                               # required — at least one
    - agent_pre_invoke
    - agent_post_invoke
  priority: 50                         # optional, default 100 (lower = runs first)
  config:                              # artifact-specific config
    detect_ssn: true
    detect_email: true
    detect_phone: true
    detect_credit_card: true
    detect_bank_account: true
    default_mask_strategy: redact
    redaction_text: "[REDACTED]"
    log_detections: true
  agent_names:                         # bind by agent display_name
    - my-agent
  # tool_names:
  #   - my-tool
  # model_names:
  #   - my-model
```

### YAML field reference

| Field | Required | Description |
|---|---|---|
| `spec_version` | ✅ | Always `v1` |
| `kind` | ✅ | Always `control` |
| `control.artifact_name` | ✅ | Display name from `orchestrate controls list-types` (e.g. `"Content Guardrails"`, `"PII Filter"`) |
| `control.name` | ✅ | Unique internal name — use `snake_case` |
| `control.display_name` | ❌ | Human-readable label, defaults to `name` |
| `control.description` | ❌ | Descriptive text |
| `control.hooks` | ✅ | List of hook names — at least one required |
| `control.priority` | ❌ | Integer, default `100` — lower runs first |
| `control.config` | ❌ | Artifact-specific config key/value map |
| `control.agent_names` | ❌ | List of agent display names to bind |
| `control.tool_names` | ❌ | List of tool names to bind |
| `control.model_names` | ❌ | List of model names to bind |

> **One file = one control.** To deploy multiple controls, import each file separately or loop:
> ```bash
> for f in ./controls/*.yaml; do orchestrate controls import -f "$f"; done
> ```

---

## Ready-made resource files

The [`resources/`](resources/) folder contains production-ready templates:

| File | Controls inside | Target asset |
|---|---|---|
| [`pii-filter.yaml`](resources/pii-filter.yaml) | PII Filter | Agent |
| [`content-guardrails.yaml`](resources/content-guardrails.yaml) | Guardrails (full) + SecretsDetection + RegexPattern | Agent |
| [`sql-sanitizer.yaml`](resources/sql-sanitizer.yaml) | SQLSanitizer + RateLimiterPlugin | Tool |
| [`model-resilience.yaml`](resources/model-resilience.yaml) | Fallback + Retry | Model |

Import any of them:
```bash
orchestrate controls import -f .bob/skills/agent/5-controls/resources/pii-filter.yaml
orchestrate controls import -f .bob/skills/agent/5-controls/resources/content-guardrails.yaml
```

---

## Deployment script

Use [`resources/apply-controls.sh`](resources/apply-controls.sh) to apply all resource files in the correct order:

```bash
bash .bob/skills/agent/5-controls/resources/apply-controls.sh <agent-name> <tool-name> <model-name>

# Example
bash .bob/skills/agent/5-controls/resources/apply-controls.sh "test_DA" "my-db-tool" "gpt-4o"
```

---

## Export → version control → deploy workflow

```bash
# 1. Export all current controls (do this once per env)
orchestrate controls list | awk 'NR>3 {print $2}' | while read name; do
  orchestrate controls export -n "$name" -o "./controls/${name}.yaml"
done

# 2. Commit to git
git add controls/
git commit -m "chore: export controls snapshot"

# 3. Deploy to another env
orchestrate env activate staging
for f in ./controls/*.yaml; do
  orchestrate controls import -f "$f"
done
orchestrate controls list
```

---

## Re-import gotchas

| Behaviour | Detail |
|---|---|
| Name collision | If a control with the same name already exists, import may fail — remove first or use a unique name |
| Agent name resolution | Agents are matched by display name — ensure the target env has agents with matching display names |
| Model names | Model bindings use the model name string exactly as registered |
| Missing hooks | YAML without `hooks` key will fail with `422` — always include at least one hook |
