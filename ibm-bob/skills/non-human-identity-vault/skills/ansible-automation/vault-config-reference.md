# Vault Configuration Reference

## Service File Template (/etc/systemd/system/vault.service)

```ini
[Unit]
Description=HashiCorp Vault
Documentation=https://www.vaultproject.io/docs/
Requires=network-online.target
After=network-online.target
ConditionFileNotEmpty=/etc/vault/vault.hcl

[Service]
Type=notify
User=vault
Group=vault
ProtectSystem=full
ProtectHome=read-only
PrivateTmp=yes
PrivateDevices=yes
SecureBits=keep-caps
AmbientCapabilities=CAP_IPC_LOCK
CapabilityBoundingSet=CAP_SYSLOG CAP_IPC_LOCK
NoNewPrivileges=yes
ExecStart=/usr/local/bin/vault server -config=/etc/vault/vault.hcl
ExecReload=/bin/kill --signal HUP $MAINPID
KillMode=process
KillSignal=SIGINT
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
LimitNOFILE=65536
LimitMEMLOCK=infinity

[Install]
WantedBy=multi-user.target
```

## Vault Configuration Template (/etc/vault/vault.hcl)

```hcl
storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1  # Set to 0 in production with proper certs
}

api_addr = "http://{{ ansible_default_ipv4.address }}:8200"
cluster_addr = "https://{{ ansible_default_ipv4.address }}:8201"
ui = true
```

## Required Permissions

| Path | Owner | Permissions | Description |
|------|-------|-------------|-------------|
| /opt/vault | vault:vault | 750 | Base directory |
| /opt/vault/data | vault:vault | 750 | Data storage |
| /etc/vault | vault:vault | 750 | Configuration directory |
| /etc/vault/vault.hcl | vault:vault | 640 | Configuration file |
| /usr/local/bin/vault | root:root | 755 | Vault binary |

## Firewall Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 8200 | TCP | API and UI |
| 8201 | TCP | Cluster communication |

## Initialization Commands

```bash
# Initialize Vault
vault operator init -key-shares=5 -key-threshold=3

# Unseal Vault (run 3 times with different keys)
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>

# Check status
vault status

# Login with root token
vault login <root-token>
```

## Verification Commands

```bash
# Check service status
systemctl status vault

# Check if Vault is running
ps aux | grep vault

# Test API
curl http://localhost:8200/v1/sys/health

# Check logs
journalctl -u vault -n 50

# Verify permissions
ls -la /opt/vault
ls -la /opt/vault/data
ls -la /etc/vault
```

## Troubleshooting Commands

```bash
# Test configuration
vault server -config=/etc/vault/vault.hcl -test

# Check port usage
netstat -tlnp | grep 8200

# Fix permissions
sudo chown -R vault:vault /opt/vault
sudo chmod 750 /opt/vault
sudo chmod 750 /opt/vault/data

# Restart service
sudo systemctl daemon-reload
sudo systemctl restart vault