# Secrets Management Skills

Secrets Management building blocks enable secure non-human identity (NHI) lifecycle governance, automated secret detection, and safe migration to HashiCorp Vault.

## 📦 Available Assets & Skills

### `vault-secret-migrator.zip`

A comprehensive skill and automation package for HashiCorp Vault secret migration, providing capabilities for:

- **Secret Detection & Scanning**: Scanning codebases for hardcoded API keys, tokens, database credentials, and secrets.
- **Vault Migration**: Securely migrating detected secrets to HashiCorp Vault KV secret engines.
- **Dynamic Code Refactoring**: Replacing hardcoded credentials with dynamic Vault SDK and environment variable calls.
- **Auditing & Remediation**: Generating comprehensive secret remediation reports and audit logs.

## 🚀 Installation and Setup

### Step 1: Extract the Skill to Bob Workspace
Extract the `vault-secret-migrator.zip` archive into your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the package
unzip /path/to/automation/secure/non-human-identity-and-secret-management/secrets-management/bob-skills/vault-secret-migrator.zip
```

### Step 2: Verify Installation
Check that the skill files are present:

```bash
ls -la .bob/skills/
```

### Step 3: Activate in Bob
1. Open Bob and select your preferred mode.
2. Ensure the **Skills** option is enabled.
3. The Secrets Management capabilities will be active and ready to assist.
