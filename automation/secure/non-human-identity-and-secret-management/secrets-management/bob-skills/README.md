# Secrets Management Skills

This directory contains Bob skills for Secrets Management using HashiCorp Vault.

## 🎯 Overview

The `vault-secret-migrator` skill empowers Bob to scan codebases for hardcoded secrets, migrate them securely to HashiCorp Vault, and automatically replace hardcoded values with dynamic Vault SDK references. This skill provides a complete end-to-end remediation workflow covering detection, migration, code refactoring, and documentation.

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `vault-secret-migrator.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/vault-secret-migrator.zip
```

After extraction, you should see a `vault-secret-migrator` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/vault-secret-migrator
```

You should see the skill files including `SKILL.md`, `1_workflow.md`, `2_best_practices.md`, `3_secret_detection_patterns.md`, `4_tool_usage.md`, and `5_examples.md`.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `vault-secret-migrator` skill will be available for use within that mode

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Vault connectivity issues
1. Verify your Vault MCP server is configured in Bob settings
2. Confirm `VAULT_ADDR` is reachable from your machine
3. Check that your Vault token has sufficient permissions (read + write on the target KV mount)
4. Test connectivity by asking Bob: "List the available Vault mounts"
5. Refer to the [Vault MCP server documentation](https://developer.hashicorp.com/vault) for auth configuration

### Skill is active but Bob doesn't detect secrets
1. Be specific in your requests (e.g. "Scan the `src/` directory for hardcoded secrets")
2. Specify the file types or directories to scan
3. Provide context about the project language and framework
4. Ask Bob to explain what patterns it's scanning for

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for architecture and usage context
3. Ask Bob directly — the skill includes comprehensive knowledge of Vault patterns
4. Refer to [HashiCorp Vault documentation](https://developer.hashicorp.com/vault/docs) for API-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Last Updated**: 2025-05-23

---

**Note**: This skill requires HashiCorp Vault with the Vault MCP server configured and accessible. Ensure you have proper Vault access and a valid token before starting a migration.

Made with ❤️ for HashiCorp Vault automation
