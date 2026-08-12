# Vault Secret Migrator — Tool Usage Guide

Reference for using Bob's tools correctly within this skill.

---

## Tool Priority Order

| Priority | Tool | When to use |
|----------|------|-------------|
| 1 | `grep` | Initial secret detection — run multiple regex patterns across the codebase |
| 2 | `read_file` | Get full file context after grep identifies matches |
| 3 | `mcp__vault__write_secret` / `mcp__vault__read_secret` | Push secrets to Vault and verify each write |
| 4 | `apply_diff` | Surgically replace hardcoded values with Vault SDK calls |
| 5 | `insert_content` | Add Vault client initialisation code and imports |
| 6 | `write_file` | Create `SECURITY_REPORT.md` and `VAULT_MIGRATION_GUIDE.md` |
| 7 | `execute_command` | Run linters, tests, and validation checks |

---

## `grep` — Secret Scanning

```python
# AWS credentials
grep(
  pattern="(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
  path=".",
  include="*.{py,js,ts,java,go,rb,yml,yaml,json}"
)

# Database connection strings
grep(
  pattern="postgres(?:ql)?://[a-zA-Z0-9_-]+:[^@\\s]+@[a-zA-Z0-9.-]+(?::\\d+)?/[a-zA-Z0-9_-]+",
  path=".",
  include="*.{py,js,ts,java,go,rb,php,yml,yaml,json,env}"
)

# Generic passwords
grep(
  pattern="(?i)(password|passwd|pwd)[\\s]*[=:]\\s*['\"]([^'\"]{8,})['\"]",
  path=".",
  include="*.{py,js,ts,java,go,rb,php,yml,yaml,json,env}"
)
```

**Best practices:**
- Use `include` to scope to relevant file types — avoids scanning binaries and lockfiles.
- Run separate `grep` calls per secret category (API keys, passwords, cloud creds, private keys).
- Follow each `grep` with `read_file` on matching files to validate context.

**Common pitfalls:**
- Too-broad regex → high false positive rate. Start narrow, widen if needed.
- Forgetting `include` → slow scans over `node_modules/`, `.git/`, `venv/`.

---

## `mcp__vault__write_secret` — Store Secrets

```python
# Write a database password
mcp__vault__write_secret(
  mount="secret",
  path="myapp/production/database/credentials",
  key="password",
  value="actualSecretPassword123"
)

# Write an API key
mcp__vault__write_secret(
  mount="secret",
  path="myapp/production/api/stripe",
  key="secret_key",
  value="sk_live_51H8x9..."
)
```

**Best practices:**
- Always test connectivity first with `mcp__vault__list_mounts()`.
- Follow every write with a `mcp__vault__read_secret` verification call.
- Log the Vault path (not the value) for the audit report.

**Path convention:**
```
[mount]/[project]/[environment]/[service]/[secret-name]
secret/myapp/production/api/stripe-key
```

---

## `mcp__vault__read_secret` — Verify Storage

```python
mcp__vault__read_secret(
  mount="secret",
  path="myapp/production/database/credentials"
)
```

Use immediately after each write to confirm the secret was stored correctly.

---

## `apply_diff` — Replace Hardcoded Secrets

Always `read_file` first to get exact content before diffing.

**Python (hvac):**
```python
# Before
STRIPE_KEY = "sk_live_51H8x9..."

# After
import hvac, os
vault_client = hvac.Client(
    url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
    token=os.environ["VAULT_TOKEN"]
)
stripe_secret = vault_client.secrets.kv.v2.read_secret_version(
    path="myapp/production/api/stripe"
)["data"]["data"]
STRIPE_KEY = stripe_secret["secret_key"]
```

**JavaScript (node-vault):**
```javascript
// Before
const API_KEY = "sk_live_abc123";

// After
const vault = require("node-vault")({
  endpoint: process.env.VAULT_ADDR || "http://localhost:8200",
  token: process.env.VAULT_TOKEN
});
const secret = await vault.read("secret/data/myapp/production/api/stripe");
const API_KEY = secret.data.data.secret_key;
```

**Best practices:**
- Preserve variable names — minimises downstream code changes.
- Group related changes (imports + initialisation + replacements) in one `apply_diff` call.
- Add a comment above each Vault call: `# Retrieved from Vault: secret/myapp/production/...`

---

## `insert_content` — Add Vault Initialisation

Use to insert imports and client setup at the top of a file without modifying existing lines.

```python
# Insert at line 1 — Python Vault client setup
import hvac
import os

vault_client = hvac.Client(
    url=os.environ.get("VAULT_ADDR", "http://localhost:8200"),
    token=os.environ["VAULT_TOKEN"]
)
if not vault_client.is_authenticated():
    raise SystemExit("Cannot authenticate with Vault")
```

---

## `ask_followup_question` — Get User Confirmation

Use after presenting scan results, before making any changes.

```python
ask_followup_question(
  question="I found 15 hardcoded secrets across 8 files. Review the findings above. Should I proceed with migrating these secrets to Vault?",
  suggestion_a="Yes, migrate all secrets to Vault and update the code",
  suggestion_b="Yes, but exclude test files from migration",
  suggestion_c="No, let me review the findings first",
  suggestion_d="Only migrate critical and high severity secrets"
)
```

Also use `ask_followup_question` when:
- A detected secret is ambiguous (placeholder vs real value).
- Choosing between Vault path structures.
- Confirming the environment (`production` / `staging` / `development`).

---

## `write_file` — Documentation

```python
write_file(
  path="SECURITY_REPORT.md",
  content="""
# Security Report

## Summary
- X secrets migrated to Vault
- Y files updated
- 0 hardcoded secrets remaining

## Secrets Migrated
| Secret | File | Vault Path |
|--------|------|-----------|
| STRIPE_KEY | src/config.py | secret/myapp/production/api/stripe |

## Recommendations
- Rotate all migrated secrets immediately
- Enable Vault audit logging
- Establish 90-day rotation schedule
"""
)
```

---

## `execute_command` — Validation

```bash
# Run linter after changes
execute_command("flake8 src/")

# Run tests
execute_command("pytest tests/")

# Verify no secrets remain (final check)
execute_command("grep -rn 'sk_live_\\|AKIA\\|password.*=' src/ --include='*.py'")
```
