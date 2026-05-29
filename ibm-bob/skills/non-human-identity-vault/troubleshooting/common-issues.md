# Common Issues Quick Reference

## Frontend Issues

### Hamburger Menu Not Visible
**Solution:**
```scss
.cds--header__menu-toggle {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
}
```
Then rebuild: `cd frontend && rm -rf node_modules/.cache && npm run build`

### CORS Errors
**Solution:**
```python
# Backend
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

### Components Not Rendering
**Check:**
1. Browser console (F12) for errors
2. Import/export statements match
3. Component is properly exported: `export default Component`

## Backend Issues

### Flask Server Won't Start
**Check:**
```bash
# Port in use?
netstat -tlnp | grep 3001
lsof -i :3001

# Kill if needed
kill -9 <PID>

# Virtual environment activated?
source venv/bin/activate
pip install -r requirements.txt
```

### API Returns 500 Error
**Debug:**
```python
# Enable debug mode
export FLASK_DEBUG=1

# Check logs
tail -f logs/app.log

# Test with curl
curl -X POST http://localhost:3001/api/scan \
  -H "Content-Type: application/json" \
  -d '{"code":"test"}'
```

## Vault Issues

### Vault Sealed
**This is expected after restart. Unseal:**
```bash
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

### Permission Denied on /opt/vault/data
**Fix:**
```bash
sudo chown -R vault:vault /opt/vault
sudo chmod 750 /opt/vault
sudo chmod 750 /opt/vault/data
sudo systemctl restart vault
```

### Connection Timeout
**Check:**
```bash
# Vault running?
systemctl status vault

# Port open?
netstat -tlnp | grep 8200

# Firewall?
sudo firewall-cmd --list-ports
sudo firewall-cmd --permanent --add-port=8200/tcp
sudo firewall-cmd --reload
```

## Docker Issues

### Container Won't Start
**Debug:**
```bash
docker logs <container-id>
docker inspect <container-id>
docker ps -a
```

### Image Pull Failed
**Fix:**
```bash
docker login <registry-url>
docker pull <image>:<tag>
```

## OpenShift Issues

### Pod CrashLoopBackOff
**Debug:**
```bash
oc logs <pod-name>
oc logs <pod-name> --previous
oc describe pod <pod-name>
oc get events --sort-by='.lastTimestamp'
```

### ImagePullBackOff
**Fix:**
```bash
# Check image name
oc describe pod <pod-name> | grep Image

# Create pull secret
oc create secret docker-registry <secret-name> \
  --docker-server=<registry> \
  --docker-username=<user> \
  --docker-password=<password>

# Link to service account
oc secrets link default <secret-name> --for=pull
```

## Network Issues

### DNS Resolution Failed
**Check:**
```bash
cat /etc/resolv.conf
nslookup <hostname>
dig <hostname>
ping <hostname>
```

### Firewall Blocking
**Fix:**
```bash
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-port=<port>/tcp
sudo firewall-cmd --reload
```

## Diagnostic Commands

```bash
# System info
cat /etc/os-release
uname -r
free -h
df -h

# Process info
ps aux | grep <process>
top
htop

# Network
netstat -tlnp
ss -tlnp
ip addr show

# Logs
journalctl -xe
journalctl -u <service>
tail -f /var/log/app.log