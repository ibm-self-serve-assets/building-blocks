# Deployment Guide

Complete step-by-step guide for deploying the Automated Hardcoded Secret Detection and Vault Migration solution.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Vault Deployment](#vault-deployment)
3. [Application Setup](#application-setup)
4. [Verification](#verification)
5. [Production Considerations](#production-considerations)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Vault Server:**
- OS: Ubuntu 20.04+, RHEL/CentOS 8+, or Debian 11+
- RAM: 2GB minimum, 4GB recommended
- CPU: 2 cores minimum
- Disk: 20GB minimum
- Network: Port 8200 (API) and 8201 (cluster) accessible

**Application Server:**
- Python 3.9 or higher
- 1GB RAM minimum
- Network access to Vault server

### Software Requirements

**Control Node (where you run Ansible):**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y ansible python3 python3-pip git

# RHEL/CentOS
sudo yum install -y ansible python3 python3-pip git

# macOS
brew install ansible python3 git
```

**Vault Server:**
- Will be installed automatically by Ansible
- Requires sudo/root access

## Vault Deployment

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd Vault32
```

### Step 2: Configure Inventory

Edit the Ansible inventory file:

```bash
cd ansible
vim inventory/hosts.ini
```

**For Remote Deployment:**
```ini
[vault_servers]
vault01 ansible_host=192.168.1.10 ansible_user=ubuntu ansible_ssh_private_key_file=~/.ssh/id_rsa

[vault_servers:vars]
ansible_python_interpreter=/usr/bin/python3
```

**For Local Deployment:**
```ini
[vault_servers]
localhost ansible_connection=local

[vault_servers:vars]
ansible_python_interpreter=/usr/bin/python3
```

### Step 3: Customize Vault Configuration (Optional)

Edit default variables if needed:

```bash
vim roles/vault/defaults/main.yml
```

Key variables:
```yaml
vault_version: "1.15.4"           # Vault version
vault_port: 8200                  # API port
vault_storage_backend: "file"     # Storage backend
vault_tls_disable: true           # TLS (false for production)
vault_ui_enabled: true            # Enable UI
```

### Step 4: Run Deployment

Make the run script executable:
```bash
chmod +x run.sh
```

Execute deployment:
```bash
./run.sh
```

Or run directly with ansible-playbook:
```bash
ansible-playbook -i inventory/hosts.ini site.yml
```

### Step 5: Retrieve Initialization Data

**On the Vault server:**
```bash
sudo cat /etc/vault.d/vault-init.json
```

This file contains:
- `keys`: Unseal keys (5 keys by default)
- `keys_base64`: Base64-encoded unseal keys
- `root_token`: Root token for initial access

**CRITICAL:** Save this data securely and remove the file:
```bash
# Copy the content to a secure location
sudo cp /etc/vault.d/vault-init.json ~/vault-init-backup.json
sudo chmod 600 ~/vault-init-backup.json

# Remove from server
sudo rm /etc/vault.d/vault-init.json
```

### Step 6: Verify Vault Installation

```bash
# Set environment variables
export VAULT_ADDR=http://<vault-server-ip>:8200
export VAULT_TOKEN=<root-token-from-init-file>

# Check status
vault status

# Expected output:
# Sealed: false
# Initialized: true
```

## Application Setup

### Step 1: Navigate to Application Directory

```bash
cd ../secret_scanner_app
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
vim .env
```

Set the following variables:
```bash
VAULT_ADDR=http://<vault-server-ip>:8200
VAULT_TOKEN=<your-vault-token>
DASH_PORT=8050
DASH_DEBUG=True
```

### Step 5: Start Application

**Using the start script:**
```bash
chmod +x start.sh
./start.sh
```

**Or manually:**
```bash
python app.py
```

### Step 6: Access Application

Open your browser and navigate to:
```
http://localhost:8050
```

## Verification

### Test Vault Connection

1. Open the application in your browser
2. Check the connection status banner at the top
3. Should show: "✓ Connected to Vault at http://..."

### Test Secret Scanning

1. Paste sample code with secrets:
```python
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
db_password = "MySecretPassword123!"
```

2. Click "Scan for Secrets"
3. Verify results show:
   - 3 secrets detected
   - Severity levels assigned
   - Secrets stored in Vault
   - Updated code generated

### Verify Vault Storage

```bash
# List secrets
vault kv list scanner/secrets

# Read a secret
vault kv get scanner/secrets/aws_access_key_id_0

# Check Transit encryption
vault read transit/keys/secret-scanner-key
```

## Production Considerations

### 1. Enable TLS

**Update Ansible variables:**
```yaml
# roles/vault/defaults/main.yml
vault_tls_disable: false
vault_tls_cert_file: "/etc/vault.d/tls/vault.crt"
vault_tls_key_file: "/etc/vault.d/tls/vault.key"
```

**Generate certificates:**
```bash
# Self-signed (for testing)
openssl req -x509 -newkey rsa:4096 -keyout vault.key -out vault.crt -days 365 -nodes

# Production: Use Let's Encrypt or your CA
```

### 2. Use Raft Storage for HA

```yaml
# roles/vault/defaults/main.yml
vault_storage_backend: "raft"
```

Configure multiple Vault servers in inventory:
```ini
[vault_servers]
vault01 ansible_host=192.168.1.10
vault02 ansible_host=192.168.1.11
vault03 ansible_host=192.168.1.12
```

### 3. Implement Access Policies

Create application-specific policy:
```bash
vault policy write scanner - <<EOF
path "scanner/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "transit/encrypt/secret-scanner-key" {
  capabilities = ["update"]
}

path "transit/decrypt/secret-scanner-key" {
  capabilities = ["update"]
}
EOF
```

Create token with policy:
```bash
vault token create -policy=scanner -ttl=24h
```

### 4. Enable Audit Logging

```bash
vault audit enable file file_path=/var/log/vault/audit.log
```

### 5. Configure Firewall

**On Vault server:**
```bash
# Ubuntu/Debian
sudo ufw allow 8200/tcp
sudo ufw allow 8201/tcp

# RHEL/CentOS
sudo firewall-cmd --permanent --add-port=8200/tcp
sudo firewall-cmd --permanent --add-port=8201/tcp
sudo firewall-cmd --reload
```

### 6. Setup Monitoring

Monitor key metrics:
- Vault seal status
- Token expiration
- Storage usage
- API response times
- Audit log size

### 7. Backup Strategy

**Vault Data:**
```bash
# For file storage backend
sudo tar -czf vault-backup-$(date +%Y%m%d).tar.gz /opt/vault/data

# For Raft storage
vault operator raft snapshot save backup.snap
```

**Application Data:**
```bash
# Backup environment configuration
cp .env .env.backup
```

### 8. Token Rotation

```bash
# Create periodic token
vault token create -policy=scanner -period=24h

# Revoke old token
vault token revoke <old-token>
```

## Troubleshooting

### Vault Won't Start

**Check logs:**
```bash
sudo journalctl -u vault -f
```

**Common issues:**
- Port already in use: `sudo lsof -i :8200`
- Permission issues: Check `/opt/vault/data` ownership
- Configuration errors: Validate `/etc/vault.d/vault.hcl`

### Vault is Sealed

```bash
# Check seal status
vault status

# Unseal (requires 3 of 5 keys by default)
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

### Application Can't Connect to Vault

**Check connectivity:**
```bash
curl http://<vault-server-ip>:8200/v1/sys/health
```

**Verify environment variables:**
```bash
echo $VAULT_ADDR
echo $VAULT_TOKEN
```

**Test token:**
```bash
vault token lookup
```

### Secrets Not Encrypting

**Check Transit engine:**
```bash
vault secrets list | grep transit
```

**Enable if missing:**
```bash
vault secrets enable transit
```

**Check encryption key:**
```bash
vault read transit/keys/secret-scanner-key
```

**Create if missing:**
```bash
vault write transit/keys/secret-scanner-key type=aes256-gcm96
```

### Application Errors

**Check Python version:**
```bash
python --version  # Should be 3.9+
```

**Verify dependencies:**
```bash
pip list | grep -E "dash|hvac|dotenv"
```

**Run with debug:**
```bash
DASH_DEBUG=True python app.py
```

### Ansible Deployment Fails

**Test connectivity:**
```bash
ansible vault_servers -m ping
```

**Run with verbose output:**
```bash
ansible-playbook -i inventory/hosts.ini site.yml -vvv
```

**Check SSH access:**
```bash
ssh -i ~/.ssh/id_rsa ubuntu@<vault-server-ip>
```

## Security Best Practices

1. **Never commit secrets to version control**
   - Use `.gitignore` for `.env` files
   - Store unseal keys separately

2. **Rotate credentials regularly**
   - Vault tokens: Every 24-48 hours
   - Unseal keys: Annually or after incidents

3. **Use least privilege**
   - Create specific policies for applications
   - Avoid using root token in production

4. **Enable audit logging**
   - Monitor all Vault operations
   - Set up alerts for suspicious activity

5. **Backup regularly**
   - Vault data: Daily
   - Configuration: After changes
   - Test restore procedures

6. **Monitor and alert**
   - Vault seal status
   - Token expiration
   - Failed authentication attempts
   - Storage capacity

7. **Network security**
   - Use TLS in production
   - Restrict network access
   - Use VPN or private networks

8. **Disaster recovery**
   - Document unseal procedure
   - Store keys in separate locations
   - Test recovery regularly

## Next Steps

After successful deployment:

1. **Configure additional secrets engines** as needed
2. **Set up authentication methods** (AppRole, LDAP, etc.)
3. **Implement CI/CD integration** for automated scanning
4. **Train team members** on Vault usage
5. **Establish operational procedures** for maintenance
6. **Set up monitoring and alerting**
7. **Plan for scaling** if needed

## Support Resources

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Ansible Documentation](https://docs.ansible.com)
- [Dash Framework Documentation](https://dash.plotly.com)
- [IBM Carbon Design System](https://carbondesignsystem.com)

---

**For additional help, refer to the main README.md or check the troubleshooting section above.**