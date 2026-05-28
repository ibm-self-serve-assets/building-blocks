---
name: ansible-automation
description: Deploy and manage HashiCorp Vault using Ansible automation with proper configuration, permissions, and security setup
---

Deploy HashiCorp Vault using Ansible with proper security configuration:

<Steps>
<Step>
Check if Vault is already installed to avoid reinstallation
</Step>
<Step>
Create vault user and group with proper permissions
</Step>
<Step>
Download and install Vault binary with version verification
</Step>
<Step>
Configure Vault with storage backend and listener settings
</Step>
<Step>
Setup systemd service with security hardening
</Step>
<Step>
Configure firewall rules for port 8200
</Step>
<Step>
Initialize and unseal Vault securely
</Step>
<Step>
Verify installation, permissions, and service status
</Step>
</Steps>

Follow the checklist in `vault-deployment-checklist.md` and use configuration templates in `vault-config-reference.md`.

**Key Security Practices:**
- Always verify ownership (vault:vault) and permissions (750) on /opt/vault
- Store unseal keys and root token securely in separate locations
- Never commit secrets to version control
- Use systemd service with IPC_LOCK capability
- Enable firewall rules for port 8200

**Common Issues:**
- Permission denied: `sudo chown -R vault:vault /opt/vault && sudo chmod 750 /opt/vault/data`
- Service won't start: Check config with `vault server -config=/etc/vault/vault.hcl -test`
- Vault sealed: This is expected after restart - unseal manually or configure auto-unseal