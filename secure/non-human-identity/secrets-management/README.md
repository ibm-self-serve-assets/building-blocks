# 💻 IBM Secrets Management Building Blocks

---

## 📑 Table of Contents

- [Overview](#overview)
- [Objective](#objective)
- [Best Practices](#best-practices)
- [Enterprise Architecture Overview](#enterprise-architecture-overview)
- [Demo Recording Best Practices](#demo-recording-best-practices)
- [Folder Structure](#folder-structure-for-code-development)
- [Related Resources](#related-resources)

---

## 🔗 Navigation

**Secure Building Blocks:**
- [← Back to Non-Human Identity](../README.md)
- [← Back to Secure](../../README.md)
- [Quantum-Safe →](../../quantum-safe/README.md)

**Other Categories:**
- [Build & Deploy](../../../build-and-deploy/Iaas/README.md)
- [Optimize](../../../optimize/finops/README.md)

---

## Overview

Best Practices for IBM Secrets Management Building Blocks Development using HashiCorp Vault.

## Objective

Develop a **demo building block for IBM Secrets Management** that demonstrates:

- **Automated Secret Detection**: Scan codebases for hardcoded secrets (API keys, passwords, tokens, cloud credentials, private keys) using AI-assisted analysis.
- **Vault Migration**: Securely migrate detected secrets into HashiCorp Vault KV stores with proper path conventions and access policies.
- **Code Remediation**: Automatically replace hardcoded values with dynamic Vault SDK references, eliminating secret exposure from source code.
- **Agentic AI** using **IBM Bob** and the Vault MCP server for end-to-end automated detection, migration, and code refactoring workflows.

The demo highlights the **integration of IBM AI tooling with HashiCorp Vault** and the security posture improvements delivered by removing hardcoded secrets from codebases.

---

## Best Practices

### 1. Secret Detection
- Scan all file types: source code, configuration files, CI/CD pipelines, infrastructure-as-code, and Dockerfiles.
- Use regex patterns and entropy analysis to identify API keys, database credentials, private keys, OAuth secrets, and cloud provider credentials.
- Distinguish real secrets from placeholder values (e.g. `"your-api-key-here"`, `"changeme"`) to minimise false positives.
- Always scan git history — secrets committed and later deleted are still exposed.

### 2. Vault Path Conventions
- Use a consistent hierarchical path structure:
  ```
  secret/[project]/[environment]/[service]/[secret-name]
  ```
  Examples:
  ```
  secret/myapp/production/database/password
  secret/myapp/production/api/stripe-key
  secret/myapp/staging/aws/access-key-id
  ```
- Separate secrets by environment (`production`, `staging`, `development`) to enforce least-privilege access.

### 3. Access Control
- Create per-environment Vault policies — grant read-only by default, limit write access to CI/CD and admin roles.
- Prefer dynamic secrets and short-lived credentials over long-lived static keys where Vault supports it.
- Use AppRole auth for CI/CD pipelines; use cloud provider identity (AWS IAM, Azure MSI, GCP SA) for cloud-hosted workloads.

### 4. Code Remediation
- Preserve existing variable names when replacing hardcoded values to minimise downstream code changes.
- Initialise the Vault client once at application startup; cache secrets in memory with a TTL — never cache to disk.
- Always fail fast if Vault is unreachable at startup rather than silently falling back to insecure defaults.
- Add `.env`, `*.pem`, `*.key`, and `secrets.*` patterns to `.gitignore`.

### 5. Rotation and Hygiene
- Rotate **all** migrated secrets immediately after migration.
- Establish a rotation schedule: 30–90 days for most secrets; automated rotation for database credentials and cloud keys where possible.
- Enable Vault audit logging and monitor for unusual access patterns or failed authentication attempts.

---

## Enterprise Architecture Overview

### Logical Components

- **HashiCorp Vault**: Central secrets store with KV v2, Transit encryption, and audit logging.
- **IBM Bob (Vault Secret Migrator skill)**: Agentic AI workflow for scanning, migrating, and remediating secrets.
- **Vault MCP Server**: Provides Bob with direct Vault API access via `mcp__vault__*` tools.
- **Application Code**: Updated to retrieve secrets dynamically via Vault SDKs (Python `hvac`, Node.js `node-vault`, etc.).
- **CI/CD Pipelines**: Authenticated to Vault via AppRole; secrets injected at runtime, not stored in pipeline config.

### Data & Control Flow

1. Bob scans the codebase with regex patterns to identify hardcoded secrets.
2. Findings are presented to the developer with severity classification and proposed Vault paths.
3. Developer reviews and approves the migration plan.
4. Bob writes each secret to Vault via `mcp__vault__write_secret` and verifies storage.
5. Bob replaces hardcoded values in source code with Vault SDK calls using `apply_diff`.
6. Validation scan confirms zero remaining hardcoded secrets; linters and tests are run.
7. `SECURITY_REPORT.md` and `VAULT_MIGRATION_GUIDE.md` are generated as audit artefacts.

---

### Demo Recording Best Practices

- Record both **screen and voice narration** for clarity.
- Keep demo **under 10 minutes**, with optional 60–90 second highlights.
- Include clear **callouts** for secret detection findings, Vault migration steps, and code remediation changes.

---

## Folder Structure for Code Development

```plaintext
secrets-management/
│
├── bob-modes/                         # Custom Bob modes for secrets management
│   └── base-modes/                    # Importable mode zip and install guide
│
├── bob-skills/                        # Bob skills for Vault integration
│   └── vault-secret-migrator/         # Skill: scan, migrate, and remediate secrets
│       └── skills/
│           └── vault-secret-migrator/
│               ├── SKILL.md           # Skill entry point
│               ├── 1_workflow.md      # 7-phase workflow
│               ├── 2_best_practices.md
│               ├── 3_secret_detection_patterns.md
│               ├── 4_tool_usage.md
│               └── 5_examples.md
```

---

## 📚 Related Resources

### Secure Building Blocks
- [Non-Human Identity](../README.md) - IBM Security Verify integration
- [Quantum-Safe](../../quantum-safe/README.md) - IBM Guardium Crypto Manager

### Build & Deploy Building Blocks
- [Infrastructure as a Service (IaaS)](../../../build-and-deploy/Iaas/README.md) - Terraform-based infrastructure
  - [Ansible Deployment](../../../build-and-deploy/Iaas/assets/deploy-bob-anisble/README.md) - Automated deployment with Ansible
  - [Retail Application](../../../build-and-deploy/Iaas/assets/retailapp/README.md) - Sample retail app deployment
- [iPaaS](../../../build-and-deploy/ipaas/README.md) - Integration workflows
- [Code Modernisation](../../../build-and-deploy/code-modernisation/README.md) - Middleware modernization

### Optimize Building Blocks
- [Automated Resilience](../../../optimize/automated-resilience-and-compliance/README.md) - IBM Concert insights
- [FinOps](../../../optimize/finops/README.md) - Cost optimization with IBM Turbonomic
- [Automated Resource Management](../../../optimize/automated-resource-mgmt/README.md) - IBM Turbonomic

---

**[⬆ Back to Top](#-ibm-secrets-management-building-blocks)**
