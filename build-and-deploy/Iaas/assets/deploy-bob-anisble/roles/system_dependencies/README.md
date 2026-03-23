# System Dependencies Role

This Ansible role installs and configures essential system dependencies including:
- Podman
- Java 11
- OpenShift CLI (oc/kubectl)
- Apache JMeter
- Trivy
- HashiCorp Vault

## Vault Configuration

The role automatically:
1. **Installs Vault** - Downloads and installs HashiCorp Vault binary
2. **Configures Vault** - Creates configuration files and directories
3. **Starts Vault Service** - Enables and starts Vault as a systemd service
4. **Initializes Vault** - Initializes Vault with 5 unseal keys (threshold: 3)
5. **Unseals Vault** - Automatically unseals Vault using the first 3 keys

### Vault Configuration Details

- **Storage Backend**: File storage at `/opt/vault/data`
- **Listener**: HTTP on `127.0.0.1:8200` (TLS disabled for local development)
- **UI**: Enabled and accessible at `http://127.0.0.1:8200/ui`
- **Log Level**: Info
- **Unseal Keys**: Saved to `/tmp/vault-keys.json`

### Important Security Notes

⚠️ **CRITICAL**: The Vault unseal keys and root token are saved to `/tmp/vault-keys.json`. This file contains sensitive information and should be:
- Backed up securely to a separate location
- Removed from the server after backing up
- Never committed to version control
- Stored in a secure secrets management system

### Vault Unseal Keys Structure

The `/tmp/vault-keys.json` file contains:
```json
{
  "keys": ["key1", "key2", "key3", "key4", "key5"],
  "keys_base64": ["base64_key1", "base64_key2", ...],
  "root_token": "hvs.xxxxxxxxxxxxx"
}
```

### Manual Vault Operations

#### Check Vault Status
```bash
export VAULT_ADDR='http://127.0.0.1:8200'
vault status
```

#### Manual Unseal (if needed)
```bash
vault operator unseal <unseal_key_1>
vault operator unseal <unseal_key_2>
vault operator unseal <unseal_key_3>
```

#### Login with Root Token
```bash
vault login <root_token>
```

#### Seal Vault
```bash
vault operator seal
```

### Service Management

```bash
# Check service status
sudo systemctl status vault

# Start service
sudo systemctl start vault

# Stop service
sudo systemctl stop vault

# Restart service
sudo systemctl restart vault

# View logs
sudo journalctl -u vault -f
```

## Variables

Default variables can be overridden in `defaults/main.yml`:

```yaml
jmeter_version: "5.6.3"
jmeter_install_dir: "/opt/jmeter"
openshift_cli_version: "4.18.28"
trivy_version: "0.69.3"
vault_version: "1.18.3"
vault_config_dir: "/etc/vault.d"
vault_data_dir: "/opt/vault/data"
vault_log_dir: "/var/log/vault"
vault_address: "http://127.0.0.1:8200"
vault_unseal_keys_file: "/tmp/vault-keys.json"
```

## Usage

Include this role in your playbook:

```yaml
- hosts: all
  roles:
    - system_dependencies
```

## Post-Installation Steps

After running this role:

1. **Backup Vault Keys**: Copy `/tmp/vault-keys.json` to a secure location
2. **Remove Keys from Server**: Delete `/tmp/vault-keys.json` after backing up
3. **Configure Vault**: Set up authentication methods, policies, and secrets
4. **Enable TLS**: For production, configure TLS certificates
5. **Set Up Auto-Unseal**: Consider using cloud KMS for auto-unsealing in production

## Production Considerations

For production deployments:
- Enable TLS/SSL for the Vault listener
- Use a more robust storage backend (Consul, etcd, etc.)
- Implement auto-unseal using cloud KMS (AWS KMS, Azure Key Vault, GCP KMS)
- Set up Vault HA (High Availability) cluster
- Implement proper backup and disaster recovery procedures
- Use Vault's audit logging features
- Follow the principle of least privilege for Vault policies

## Troubleshooting

### Vault Service Won't Start
```bash
# Check logs
sudo journalctl -u vault -n 50

# Verify configuration
vault server -config=/etc/vault.d/vault.hcl -test
```

### Vault is Sealed
```bash
# Check seal status
vault status

# Unseal using keys from backup
vault operator unseal
```

### Permission Issues
```bash
# Ensure correct ownership
sudo chown -R root:root /opt/vault/data
sudo chown -R root:root /etc/vault.d
```

## Made with Bob