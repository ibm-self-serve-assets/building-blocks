# Domain 5 — Controls: Troubleshooting

> **ADK version**: 2.15.0 · Error codes and fixes from live testing

---

## Error: `422 Unprocessable Entity` on `controls import` (wrong YAML schema)

**Symptom**: YAML import fails immediately with a validation error.

**Causes and fixes**:

| Wrong field | Correct field | Location |
|---|---|---|
| `artifact: pii_filter` | `artifact_name: PII Filter` | inside `control:` block |
| `agents:` | `agent_names:` | inside `control:` block |
| `tools:` | `tool_names:` | inside `control:` block |
| `models:` | `model_names:` | inside `control:` block |
| No `spec_version`/`kind` wrapper | must have `spec_version: v1` + `kind: control` + `control:` | top level |

**Correct minimal YAML structure**:
```yaml
spec_version: v1
kind: control
control:
  artifact_name: PII Filter    # use display name from list-types
  name: my_pii_control         # snake_case
  hooks:
    - agent_pre_invoke
  agent_names:
    - my-agent
```

---

## Error: `422 Unprocessable Entity` on `controls create`

**Symptom**:
```
Error: 422 Unprocessable Entity
```

**Causes and fixes**:

| Cause | Fix |
|---|---|
| Missing `--hook` | Always add at least one `--hook agent_pre_invoke` or `--hook tool_pre_invoke` |
| Invalid config JSON | Validate with `python3 -c "import json,sys; json.loads(sys.argv[1])" '<your-json>'` |
| Required config field missing | Check artifact schema: `orchestrate controls get-type -n <artifact> -v` |
| `SecretsDetection` missing `block_on_detection` | It is a **required** field — add `"block_on_detection": false` to config |

---

## Control created but `count` shows 0 (unbound control)

**Symptom**: `controls create` succeeds, `controls list` shows the control, but `controls count` shows 0 for the asset type.

**Cause**: No `--agent`, `--tool`, or `--model` flag was provided.

**Fix**:
```bash
# Check existing binding
orchestrate controls get-details -n my-control -v
# Look at: "agent_ids", "tool_ids", "model_ids" — if all empty, control is unbound

# Bind to an agent
orchestrate controls update \
  --name my-control \
  --agent "MyAgent" \
  --hook agent_pre_invoke   # must re-specify hooks on update
```

---

## `orchestrate` resolves to version 2.8.0 instead of 2.15.0

**Symptom**:
```bash
orchestrate --version
# ADK Version: 2.8.0    ← wrong
```

**Cause**: The system PATH resolves the old system-installed binary before the venv binary.

**Fix**:
```bash
# Activate the venv first
source /path/to/venv/bin/activate

# Verify
which orchestrate
# Should show: /path/to/venv/bin/orchestrate

orchestrate --version | head -1
# ADK Version: 2.15.0
```

**Permanent fix** — add to your shell profile:
```bash
echo "source /Users/dheerajarremsetty/Desktop/scratch-pad/Merge-Skills/venv/bin/activate" >> ~/.zshrc
```

---

## `--type` flag not found on `get-type`

**Symptom**:
```
Error: No such option: --type
```

**Fix**: The flag is `--name` / `-n`, not `--type`:
```bash
# Wrong
orchestrate controls get-type --type pii_filter

# Correct
orchestrate controls get-type --name pii_filter -v
orchestrate controls get-type -n "PII Filter" -v
```

---

## `--agent` not working — control shows 0 agents

**Symptom**: `--agent "MyAgent"` does not bind the control, or returns an error.

**Cause**: `--agent` takes the **display_name**, not the internal `name` or agent `id`.

**Fix**:
```bash
# Find the correct display name
orchestrate agents list -v | grep '"display_name"'

# Use the exact display_name value
orchestrate controls create \
  --artifact pii_filter \
  --name my-control \
  --hook agent_pre_invoke \
  --config '{"detect_email":true,"default_mask_strategy":"redact"}' \
  --agent "test_DA"   # ← use display_name, not "test_DA_2160PL" (internal name)
```

---

## `controls update` removes existing agent bindings

**Symptom**: After running `controls update --agent "NewAgent"`, the original agent binding is gone.

**Cause**: `--agent` in `update` **replaces** all bindings — it does not append.

**Fix**: Re-specify all agents you want to keep:
```bash
orchestrate controls update \
  --name my-control \
  --agent "OriginalAgent" \
  --agent "NewAgent"     # both specified = both kept
```

---

## `controls update` resets hooks

**Same as above**: `--hook` in update replaces existing hooks. Always re-specify all hooks.

```bash
orchestrate controls update \
  --name my-control \
  --hook agent_pre_invoke \   # was already there
  --hook agent_post_invoke    # newly added
```

---

## Control shows in `list` but has no effect

**Checklist**:
1. Is the control bound? — `get-details -v` → `agent_ids` must be non-empty
2. Is the hook correct? — for agent protection use `agent_pre_invoke` / `agent_post_invoke`
3. Is the config enabling the detections? — all detection flags default to `false`
4. Is the env correct? — `orchestrate env list` to check active env

```bash
# Full diagnostic sequence
orchestrate env list                          # confirm active env
orchestrate controls get-details -n my-control -v  # check config, hooks, agent_ids
orchestrate agents list | grep "MyAgent"      # confirm agent exists in this env
```

---

## Token expired — API calls fail silently

**Symptom**: `controls list-types` or `get-type -v` returns nothing or hangs.

**Fix**:
```bash
orchestrate env activate ibm_cloud   # re-authenticates
orchestrate controls list-types      # retry
```

---

## `controls import` fails with name collision

**Symptom**: Import returns an error about a duplicate name.

**Fix**:
```bash
# Remove the existing control first
orchestrate controls remove -n existing-control-name

# Then re-import
orchestrate controls import -f ./controls/my-control.yaml
```

---

## JSON config string escaping in shell

`--config` takes a raw JSON string. Special characters in shell need escaping.

```bash
# Single-quoted JSON (recommended on zsh/bash)
--config '{"detect_ssn":true,"detect_email":true}'

# Inline with escaped regex (double quotes require backslash escaping)
--config '{"regex_patterns":["\\bDROP\\b","\\bALTER\\b"],"strategy":"block"}'

# Validate before using
python3 -c "
import json, sys
data = json.loads(sys.argv[1])
print('Valid JSON:', json.dumps(data, indent=2))
" '{"detect_ssn":true}'
```

---

## Diagnostic command sequence

Run this to get a complete picture of controls state:

```bash
# 1. Env check
orchestrate env list

# 2. What controls exist
orchestrate controls list
orchestrate controls count

# 3. Inspect a specific control
orchestrate controls get-details -n <name> -v

# 4. Verify artifact type schema
orchestrate controls get-type -n <artifact> -v

# 5. Check agents available to bind
orchestrate agents list -v | python3 -c "
import json,sys
agents = json.load(sys.stdin)['native']
for a in agents:
    print(f'  display_name: {a[\"display_name\"]}  name: {a[\"name\"]}  id: {a[\"id\"]}')
"
```
