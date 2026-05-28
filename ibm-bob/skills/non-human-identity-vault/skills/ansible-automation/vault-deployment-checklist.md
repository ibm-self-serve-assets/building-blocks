# Vault Deployment Checklist

## Pre-Installation
- [ ] Verify OS compatibility (RHEL/CentOS 7+, Ubuntu 18.04+)
- [ ] Check required packages installed (unzip, curl, jq)
- [ ] Verify sufficient disk space in /opt/vault
- [ ] Test network connectivity for binary download
- [ ] Check if Vault is already installed (`which vault`)

## User and Group Setup
- [ ] Create vault user and group
- [ ] Set proper ownership on /opt/vault
- [ ] Verify user permissions

## Installation
- [ ] Download Vault binary (check version)
- [ ] Verify binary checksum
- [ ] Install to /usr/local/bin
- [ ] Set executable permissions (755)
- [ ] Verify installation (`vault version`)

## Configuration
- [ ] Create /etc/vault directory (750 permissions)
- [ ] Create vault.hcl configuration file
- [ ] Configure storage backend (file, consul, etc.)
- [ ] Configure listener (TCP with/without TLS)
- [ ] Set API and cluster addresses
- [ ] Enable UI if needed

## Service Setup
- [ ] Create systemd service file
- [ ] Set proper User and Group in service
- [ ] Enable IPC_LOCK capability
- [ ] Configure security settings (ProtectSystem, PrivateTmp, etc.)
- [ ] Set resource limits (LimitNOFILE, LimitMEMLOCK)
- [ ] Reload systemd daemon
- [ ] Enable service for auto-start
- [ ] Start Vault service

## Firewall Configuration
- [ ] Open port 8200/tcp for API
- [ ] Open port 8201/tcp for cluster (if clustering)
- [ ] Reload firewall rules
- [ ] Test connectivity

## Initialization
- [ ] Initialize Vault (set key shares and threshold)
- [ ] **Securely store** unseal keys (separate locations)
- [ ] **Securely store** root token
- [ ] Never commit keys/tokens to version control

## Unsealing
- [ ] Unseal with required number of keys
- [ ] Verify Vault is unsealed
- [ ] Test API connectivity

## Post-Installation Verification
- [ ] Check service status (`systemctl status vault`)
- [ ] Verify file ownership (vault:vault)
- [ ] Verify file permissions (750 for directories, 640 for configs)
- [ ] Test Vault API (`curl http://localhost:8200/v1/sys/health`)
- [ ] Check logs for errors (`journalctl -u vault`)

## Common Issues
- **Permission denied on /opt/vault/data**: Fix with `chown -R vault:vault /opt/vault`
- **Service won't start**: Check config syntax with `vault server -config=/etc/vault/vault.hcl -test`
- **Port already in use**: Check with `netstat -tlnp | grep 8200`
- **Vault sealed after restart**: This is expected - unseal manually or configure auto-unseal