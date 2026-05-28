---
name: deployment-operations
description: Deploy, run, and maintain applications with startup scripts, environment configuration, health monitoring, and operational procedures
---

Deploy and operate applications with automated scripts:

<Steps>
<Step>
Create .env files from .env.example templates
</Step>
<Step>
Use startup scripts in `scripts/` directory to launch services
</Step>
<Step>
Verify health of all services (frontend port 3000, backend port 3001, Vault port 8200)
</Step>
<Step>
Monitor logs for errors and performance issues
</Step>
<Step>
Perform regular backups of configuration and data
</Step>
<Step>
Run maintenance tasks (updates, cleanup, security audits)
</Step>
<Step>
Document operational changes and incidents
</Step>
</Steps>

**Startup Scripts:**
- `scripts/start-frontend.sh` - Starts React on port 3000
- `scripts/start-backend.sh` - Starts Flask on port 3001
- `scripts/start-all.sh` - Starts both with health checks and graceful shutdown

**Health Check:**
```bash
# Backend
curl http://localhost:3001/api/health

# Frontend
curl http://localhost:3000

# Vault
curl http://localhost:8200/v1/sys/health
```

**Common Operations:**
- Start all: `./scripts/start-all.sh`
- Check logs: `tail -f backend.log` or `tail -f frontend.log`
- Stop services: Press Ctrl+C (handled by start-all.sh)
- Rebuild: `cd frontend && npm run build`

**Environment Variables:**
- Frontend: `REACT_APP_API_URL=http://localhost:3001`
- Backend: `FLASK_ENV=development`, `PORT=3001`
- Vault: `VAULT_ADDR=http://localhost:8200`, `VAULT_TOKEN=<token>`