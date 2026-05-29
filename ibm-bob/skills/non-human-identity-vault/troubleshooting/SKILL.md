---
name: troubleshooting
description: Debug and resolve common issues in applications, Vault, Docker, OpenShift, Nexus, and GPU operators with step-by-step solutions
---

Systematically troubleshoot and resolve issues:

<Steps>
<Step>
Identify the issue category (frontend, backend, Vault, Docker, OpenShift, network)
</Step>
<Step>
Check logs for error messages (browser console, app logs, system logs)
</Step>
<Step>
Gather diagnostic information using appropriate commands
</Step>
<Step>
Apply the documented solution from `common-issues.md`
</Step>
<Step>
Verify the fix resolved the problem
</Step>
<Step>
Document new issues and solutions for future reference
</Step>
</Steps>

**Quick Reference:** See `common-issues.md` for 30+ issues with solutions

**Most Common Issues:**

**Frontend:**
- Hamburger menu not visible → Add CSS visibility rules
- CORS errors → Enable CORS in Flask backend
- Components not rendering → Check browser console for errors

**Backend:**
- Server won't start → Check port 3001 availability
- API 500 errors → Enable debug mode and check logs
- Import errors → Activate virtual environment

**Vault:**
- Sealed after restart → Unseal with 3 keys (expected behavior)
- Permission denied → Fix ownership: `chown -R vault:vault /opt/vault`
- Connection timeout → Check service status and firewall

**Docker:**
- Container won't start → Check logs: `docker logs <container>`
- Image pull failed → Login to registry: `docker login`

**OpenShift:**
- CrashLoopBackOff → Check pod logs: `oc logs <pod>`
- ImagePullBackOff → Create and link pull secret

**Diagnostic Commands:**
```bash
# Logs
journalctl -u <service>
docker logs <container>
oc logs <pod>

# Network
netstat -tlnp | grep <port>
curl http://localhost:<port>

# Process
ps aux | grep <process>
systemctl status <service>