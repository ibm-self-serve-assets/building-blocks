# Secrets Management Skills

This directory contains Bob skills for Secrets Management using Hashicorp Vault.

## 🎯 Overview

The `non-human-identity-vault.zip` skill empowers Bob to help you build, deploy, and manage secrets. This skill provides comprehensive capabilities for creating production-ready monitoring solutions that optimize your secrets management.

## 🚀 Installation and Setup

### Step 1: Download the Skill
Download the `non-human-identity-vault.zip` file from this directory.

### Step 2: Extract the Skill to Bob Workspace
Extract the contents to your Bob workspace skills directory:

```bash
# Navigate to your Bob workspace skills directory
cd /path/to/your/bob/workspace/.bob/skills

# Extract the skill
unzip /path/to/non-human-identity-vault.zip
```

After extraction, you should see an `non-human-identity-vault` folder in your `.bob/skills` directory.

### Step 3: Verify Installation
Check that the skill is properly installed:

```bash
ls -la .bob/skills/non-human-identity-vault
```

You should see the skill files and configuration.

### Step 4: Activate the Skill
To use the skill:
1. Open Bob and select any mode you want to work in
2. Enable the **Skills** button in that mode
3. The `non-human-identity-vault` skill will be available for use within that mode

## 🐛 Troubleshooting

### Skill doesn't appear after installation
1. Verify the extraction path is correct (`.bob/skills/`)
2. Check file permissions on the extracted files
3. Restart Bob to refresh the skills list
4. Ensure you've enabled the Skills button in your current mode
5. Review Bob logs for any error messages

### Skill is active but Bob doesn't understand Turbonomic requests
1. Be specific in your requests (mention "Turbonomic" explicitly)
2. Reference specific features (e.g., "pending actions", "entity monitoring")
3. Provide context about what you're trying to build
4. Ask Bob to explain the skill's capabilities if unsure

### Need help with Turbonomic API specifics
1. Ask Bob about specific API endpoints or data structures
2. Request examples of API integration patterns
3. The skill includes knowledge of common API issues and solutions

## 💬 Support

For issues or questions about this skill:
1. Check the troubleshooting section above
2. Review the [parent directory README](../README.md) for implementation examples
3. Ask Bob directly - the skill includes comprehensive knowledge
4. Refer to Hashicorp Vault documentation for API-specific questions

## 📝 Version Information

- **Skill Version**: 1.0.0
- **Last Updated**: 2026-05-23

---

**Note**: This skill is designed to work with Hashicorp Vault. Ensure you have proper access and credentials before starting development.

Made with ❤️ for Hashicorp Vault automation
