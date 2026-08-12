# Vault Secret Migrator — Workflow

This document defines the 7-phase workflow for the Vault Secret Migrator skill.

---

## Phase 1 — Initialization

**Goal:** Gather context and prepare for scanning.

- Determine scope: entire repo or specific directories.
- Identify programming languages and frameworks in use.
- Check for existing Vault integration or configuration.
- Verify Vault MCP connectivity:
  ```
  mcp__vault__list_mounts()
  ```
- Analyse project structure using `list_files`, `glob`, and `read_file` to identify:
  - Config files: `.env`, `config.*`, `secrets.*`
  - Source code directories
  - Test files (may contain test secrets)
  - CI/CD configuration files

---

## Phase 2 — Comprehensive Secret Detection

**Goal:** Scan the entire codebase for hardcoded secrets.

- Use `grep` with the regex patterns in `3_secret_detection_patterns.md`.
- Scan all relevant file types: `.py`, `.js`, `.ts`, `.java`, `.go`, `.rb`, `.php`, `.yml`, `.yaml`, `.json`, `.env`.
- For each match, use `read_file` to read full context and determine:
  - Variable name and purpose
  - Production code vs test/example
  - Severity: `critical` | `high` | `medium` | `low`
  - File path and line number

**Priority levels:**

| Priority | Secret types |
|----------|-------------|
| Critical | Production DB credentials, cloud root credentials, private keys, production API keys with write access |
| High | Service API keys (Stripe, SendGrid), OAuth secrets, JWT signing keys, encryption keys |
| Medium | Read-only tokens, dev/staging credentials, limited-scope tokens |
| Low | Test credentials, expired keys, placeholder values |

---

## Phase 3 — Report Findings and Get Confirmation

**Goal:** Present all findings and get explicit user approval before any changes.

Report structure:
- **Executive Summary**: total count, breakdown by severity and type, risk assessment.
- **Detailed Findings**: for each secret — file path, line number, type, severity, masked value (`first4****`), proposed Vault path, replacement strategy.
- **Recommendations**: immediate actions, long-term improvements, Vault config suggestions.

Get confirmation with `ask_followup_question` before proceeding.

---

## Phase 4 — Migrate Secrets to Vault

**Goal:** Push all approved secrets to Vault and verify storage.

For each secret:
1. Determine the Vault path: `secret/[project]/[environment]/[service]/[name]`
2. Write to Vault:
   ```
   mcp__vault__write_secret(mount, path, key, value)
   ```
3. Verify write:
   ```
   mcp__vault__read_secret(mount, path)
   ```
4. Record the Vault path for use in code replacement.

Error handling: retry transient failures, log all paths written, maintain rollback capability.

---

## Phase 5 — Replace Hardcoded Secrets with Vault References

**Goal:** Update code to retrieve secrets from Vault dynamically.

Steps:
1. Choose the Vault SDK for the language (see `4_tool_usage.md`).
2. Add Vault client initialisation code using `insert_content`.
3. Replace each hardcoded value with a Vault SDK call using `apply_diff`.
4. Update `.env` / config files; add secrets patterns to `.gitignore`.

Always preserve variable names and maintain existing error handling behaviour.

---

## Phase 6 — Validation

**Goal:** Confirm all changes are correct and no secrets remain.

- Re-scan with `grep` — confirm zero remaining hardcoded secrets.
- Run linters and syntax checkers with `execute_command`.
- Run application tests with `execute_command` to verify Vault integration.

---

## Phase 7 — Documentation

**Goal:** Produce a complete audit trail and onboarding guide.

- `write_file` → `SECURITY_REPORT.md` covering: secrets migrated, before/after posture, Vault paths, access control recommendations.
- `write_file` → `VAULT_MIGRATION_GUIDE.md` covering: setup instructions, authentication, adding new secrets, troubleshooting, team onboarding.
- `apply_diff` → update project `README.md` with a Vault prerequisites section.

---

## Completion Criteria

- [ ] All hardcoded secrets identified and catalogued
- [ ] User reviewed and approved migration plan
- [ ] All secrets successfully pushed to Vault
- [ ] Code updated to retrieve secrets from Vault
- [ ] Application functionality verified
- [ ] No remaining hardcoded secrets in codebase
- [ ] `SECURITY_REPORT.md` created
- [ ] `VAULT_MIGRATION_GUIDE.md` created

---

## Rollback Strategy

- Keep original files in version control before applying changes.
- Document all Vault paths and their code mappings.
- Provide step-by-step revert instructions in `VAULT_MIGRATION_GUIDE.md`.
