# Domain 5 — Controls: CLI Reference

> **ADK version**: 2.15.0 · All output verified live against `ibm_cloud` env

---

## Command index

| Command | Purpose |
|---|---|
| [`controls list-types`](#list-types) | Show all available policy artifact types |
| [`controls get-type`](#get-type) | Show schema for a single artifact type |
| [`controls create`](#create) | Bind a policy artifact to agents/tools/models |
| [`controls list`](#list) | Show all controls in the current env |
| [`controls count`](#count) | Count controls by asset type |
| [`controls get-details`](#get-details) | Show full JSON for a single control |
| [`controls update`](#update) | Modify an existing control |
| [`controls remove`](#remove) | Delete a control |
| [`controls export`](#export) | Save a control to YAML |
| [`controls import`](#import) | Load controls from YAML/JSON file |

> **Artifact naming**: `--artifact` accepts both the **display name** (e.g. `"Content Guardrails"`, `"PII Filter"`) and the **internal name** (e.g. `Guardrails`, `pii_filter`). Display names are preferred — they match the YAML `artifact_name` field.

---

## `list-types` {#list-types}

List all available policy artifact types grouped by asset category.

```bash
orchestrate controls list-types
```

**Output (live)**:
```
Agent Policy Artifact Types
┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Display Name        ┃ Name                    ┃ Description                  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Content Guardrails  │ Guardrails              │ Detects sexual content,      │
│ Output Length Guard │ OutputLengthGuardPlugin │ Min/max char/token length    │
│ Regex Pattern       │ RegexPattern            │ Custom regex detect/redact   │
│ Secrets Detector    │ SecretsDetection        │ Credential/secret detection  │
│ PII Filter          │ pii_filter              │ PII detection and masking    │
└─────────────────────┴─────────────────────────┴──────────────────────────────┘
[INFO] - Agent artifacts: 5

Tool Policy Artifact Types: Guardrails, OutputLengthGuardPlugin,
                            RateLimiterPlugin, SQLSanitizer, SecretsDetection

Model Policy Artifact Types: fallback, load_balance, retry_mode
```

---

## `get-type` {#get-type}

Show the full JSON schema for a single artifact type.

```bash
orchestrate controls get-type --name <name-or-display-name> [--verbose]
```

| Flag | Short | Required | Description |
|---|---|---|---|
| `--name` | `-n` | ✅ | Artifact name (`pii_filter`) or display name (`PII Filter`) |
| `--verbose` | `-v` | ❌ | Show full JSON schema |

**Examples**:
```bash
orchestrate controls get-type -n pii_filter -v
orchestrate controls get-type -n "Content Guardrails" -v
orchestrate controls get-type -n SQLSanitizer -v
```

> **Note**: `--type` does NOT exist — the flag is `--name` / `-n`.

---

## `create` {#create}

Create a control by binding a policy artifact to one or more assets.

```bash
orchestrate controls create \
  --artifact <artifact-name>  \   # required
  --name <control-name>       \   # required
  [--display-name <str>]      \
  [--description <str>]       \
  [--hook <hook>]             \   # repeat for multiple hooks
  [--priority <int>]          \   # default: 100
  [--config '<json>']         \
  [--agent <display-name>]    \   # repeat for multiple agents
  [--tool <name>]             \   # repeat for multiple tools
  [--model <name>]                # repeat for multiple models
```

| Flag | Short | Required | Description |
|---|---|---|---|
| `--artifact` | `-a` | ✅ | Artifact name or display name |
| `--name` | `-n` | ✅ | Internal name for this control |
| `--display-name` | | ❌ | Defaults to `--name` if omitted |
| `--description` | `-d` | ❌ | Human-readable description |
| `--hooks` / `--hook` | | ❌* | Execution hook(s) — **at least one required in practice** |
| `--priority` | `-p` | ❌ | Execution order (lower = earlier); default `100` |
| `--config` | | ❌ | JSON string with artifact-specific config |
| `--agent` | | ❌ | Agent display name(s) to bind — repeat flag |
| `--tool` | | ❌ | Tool name(s) to bind — repeat flag |
| `--model` | | ❌ | Model name(s) to bind — repeat flag |

> **⚠️ Critical**: Omitting `--hook` causes `422 Unprocessable Entity`.  
> **⚠️ Critical**: Omitting `--agent`/`--tool`/`--model` creates an **unbound** control (no effect).

**Agent hooks**: `agent_pre_invoke`, `agent_post_invoke`  
**Tool hooks**: `tool_pre_invoke`, `tool_post_invoke`  
**Prompt hooks**: `prompt_pre_fetch`, `prompt_post_fetch`

**Examples**:
```bash
# PII filter — redact SSN + email on agent test_DA
orchestrate controls create \
  --artifact pii_filter \
  --name test-da-pii \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --config '{"detect_ssn":true,"detect_email":true,"default_mask_strategy":"redact","log_detections":true}' \
  --agent "test_DA"

# Content guardrails — block jailbreak + HAP
orchestrate controls create \
  --artifact Guardrails \
  --name my-content-guard \
  --hook agent_pre_invoke \
  --hook agent_post_invoke \
  --priority 1 \
  --config '{"enabled":{"jailbreak":true,"hap":true,"harm":true},"block_message":"Content blocked by policy."}' \
  --agent "test_DA"

# SQL sanitizer on a tool
orchestrate controls create \
  --artifact SQLSanitizer \
  --name sql-guard \
  --hook tool_pre_invoke \
  --config '{"block_on_violation":true,"strip_comments":true,"block_delete_without_where":true}' \
  --tool "my-db-query-tool"

# Rate limiter on a tool
orchestrate controls create \
  --artifact RateLimiterPlugin \
  --name api-rate-limit \
  --hook tool_pre_invoke \
  --config '{"by_tool":30,"by_tenant":3000}' \
  --tool "my-api-tool"

# Model fallback
orchestrate controls create \
  --artifact fallback \
  --name gpt4-fallback \
  --config '{"fallBack":{"strategy":{"mode":"fallback","on_status_codes":[429,500,503]},"targets":[{"provider":"watsonx","override_params":{"model":"ibm/granite-3-8b-instruct"}}]}}' \
  --model "gpt-4o"
```

---

## `list` {#list}

List all controls in the active environment.

```bash
orchestrate controls list [--agent <name>] [--tool <name>] [--model <name>]
```

**Live output example**:
```
Controls
┏━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Name   ┃ Artifact   ┃ Hooks         ┃ Priority ┃ Assets      ┃ ID            ┃
┡━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ pii_DA │ PII Filter │ agent_pre_in… │      100 │ A:1 T:0 M:0 │ 829bcc52-44e… │
│        │            │ agent_post_i… │          │             │               │
└────────┴────────────┴───────────────┴──────────┴─────────────┴───────────────┘
[INFO] - Total controls: 1
```

> Assets column: `A:` = agent count, `T:` = tool count, `M:` = model count.

---

## `count` {#count}

Get a count breakdown by asset type.

```bash
orchestrate controls count
```

**Live output**:
```
Control Counts by Asset Type:
  Agent Controls: 1
  Tool Controls: 0
  Model Controls: 0
  Total Controls: 1
```

> Controls that are **unbound** (no `--agent`/`--tool`/`--model`) still appear in `list` but **do not increment count**.

---

## `get-details` {#get-details}

Show full JSON for a single control including its config, hooks, and bound asset IDs.

```bash
orchestrate controls get-details --name <control-name> [--verbose]
```

| Flag | Short | Required | Description |
|---|---|---|---|
| `--name` | `-n` | ✅ | Control name from `controls list` |
| `--verbose` | `-v` | ❌ | Show full JSON (recommended) |

```bash
orchestrate controls get-details -n pii_DA -v
```

---

## `update` {#update}

Modify any field of an existing control. **All `--agent`/`--hook` flags replace (not append) existing values.**

```bash
orchestrate controls update \
  --name <existing-control-name> \
  [--artifact <new-artifact>]    \
  [--new-name <str>]             \
  [--display-name <str>]         \
  [--description <str>]          \
  [--hook <hook>]                \   # REPLACES all existing hooks
  [--priority <int>]             \
  [--config '<json>']            \
  [--agent <name>]               \   # REPLACES all agent bindings
  [--tool <name>]                \
  [--model <name>]
```

> **⚠️ Replace semantics**: `--agent` replaces the full agent list. To keep existing agents, re-specify them all.

```bash
# Add violence detection to existing guardrail control
orchestrate controls update \
  --name my-content-guard \
  --config '{"enabled":{"jailbreak":true,"hap":true,"harm":true,"violence":true}}' \
  --hook agent_pre_invoke \
  --hook agent_post_invoke

# Rebind a control to a different agent
orchestrate controls update \
  --name test-da-pii \
  --agent "AskOrchestrate"
```

---

## `remove` {#remove}

Delete a control permanently.

```bash
orchestrate controls remove --name <control-name>
```

```bash
orchestrate controls remove -n pii_DA
```

---

## `export` {#export}

Save a control's definition to a YAML file for version control or deployment.

```bash
orchestrate controls export --name <control-name> --output <path>
```

```bash
orchestrate controls export -n pii_DA -o ./controls/pii_DA.yaml
```

---

## `import` {#import}

Load controls from a YAML or JSON file.

```bash
orchestrate controls import --file <path>
```

```bash
orchestrate controls import -f ./controls/pii-filter.yaml
orchestrate controls import -f ./controls/all-controls.yaml
```

See **[import-export.md](import-export.md)** for the full YAML schema.
