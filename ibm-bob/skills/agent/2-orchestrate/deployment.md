# Production Deployment Guide

## Pre-Deployment Checklist

Before deploying to production:

- [ ] All agents tested in draft environment
- [ ] All workflows tested with sample data
- [ ] All MCP servers tested and validated
- [ ] All connections configured in both environments
- [ ] All models tested with production credentials
- [ ] Error handling verified for all failure scenarios
- [ ] Performance benchmarks meet requirements
- [ ] Security review completed
- [ ] Documentation updated
- [ ] Rollback plan prepared

## Environment Setup

### Draft Environment
Development and testing environment for iterative changes.

```bash
# Set draft environment
export WXO_ENV=draft

# Verify environment
orchestrate config get-env
# Should show: draft
```

### Live Environment
Production environment for end users.

```bash
# Set live environment
export WXO_ENV=live

# Verify environment
orchestrate config get-env
# Should show: live
```

## Deployment Scripts

### Complete Deployment Script (Bash)

```bash
#!/bin/bash
# deploy-orchestration.sh - Complete deployment automation

set -e  # Exit on error

# Configuration
DRAFT_ENV="draft"
LIVE_ENV="live"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Backup current live environment
backup_live() {
    log_info "Creating backup of live environment..."
    mkdir -p "$BACKUP_DIR"
    
    # Export all agents
    orchestrate agents export --env live --output "$BACKUP_DIR/agents"
    
    # Export all workflows
    orchestrate tools export --env live --kind flow --output "$BACKUP_DIR/workflows"
    
    # Export all models
    orchestrate models export --env live --output "$BACKUP_DIR/models"
    
    # Export all connections
    orchestrate connections export --env live --output "$BACKUP_DIR/connections"
    
    log_info "Backup completed: $BACKUP_DIR"
}

# Deploy connections
deploy_connections() {
    log_info "Deploying connections..."
    
    for conn_file in connections/*.yaml; do
        if [ -f "$conn_file" ]; then
            conn_name=$(basename "$conn_file" .yaml)
            log_info "Deploying connection: $conn_name"
            
            # Add connection
            orchestrate connections add -f "$conn_file" --env live || true
            
            # Configure connection
            orchestrate connections configure \
                -a "$conn_name" \
                --env live \
                --type team \
                --kind key_value
            
            # Set credentials from environment
            if [ -n "${!conn_name^^}_API_KEY" ]; then
                orchestrate connections set-credentials \
                    -a "$conn_name" \
                    --env live \
                    -e "${conn_name^^}_API_KEY=${!conn_name^^}_API_KEY"
            fi
        fi
    done
}

# Deploy models
deploy_models() {
    log_info "Deploying AI Gateway models..."
    
    for model_file in models/*.yaml; do
        if [ -f "$model_file" ]; then
            model_name=$(basename "$model_file" .yaml)
            log_info "Deploying model: $model_name"
            
            orchestrate models add -f "$model_file" --env live
        fi
    done
}

# Deploy MCP toolkits
deploy_mcp_toolkits() {
    log_info "Deploying MCP toolkits..."
    
    for toolkit in mcp-servers/*; do
        if [ -d "$toolkit" ]; then
            toolkit_name=$(basename "$toolkit")
            log_info "Deploying MCP toolkit: $toolkit_name"
            
            orchestrate tools import \
                --mcp "$toolkit_name" \
                --env live
        fi
    done
}

# Deploy agents
deploy_agents() {
    log_info "Deploying agents..."
    
    for agent_file in agents/*.yaml; do
        if [ -f "$agent_file" ]; then
            agent_name=$(basename "$agent_file" .yaml)
            log_info "Deploying agent: $agent_name"
            
            orchestrate agents import \
                -f "$agent_file" \
                --env live
        fi
    done
}

# Deploy workflows
deploy_workflows() {
    log_info "Deploying workflows..."
    
    for workflow_file in workflows/*.py; do
        if [ -f "$workflow_file" ]; then
            workflow_name=$(basename "$workflow_file" .py)
            log_info "Deploying workflow: $workflow_name"
            
            orchestrate tools import \
                -k flow \
                -f "$workflow_file" \
                --env live
        fi
    done
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # List all agents
    log_info "Checking agents..."
    orchestrate agents list --env live
    
    # List all workflows
    log_info "Checking workflows..."
    orchestrate tools list --env live --kind flow
    
    # List all models
    log_info "Checking models..."
    orchestrate models list --env live
    
    # List all connections
    log_info "Checking connections..."
    orchestrate connections list --env live
}

# Rollback to backup
rollback() {
    log_warn "Rolling back to backup: $BACKUP_DIR"
    
    # Restore agents
    for agent_file in "$BACKUP_DIR/agents"/*.yaml; do
        if [ -f "$agent_file" ]; then
            orchestrate agents import -f "$agent_file" --env live
        fi
    done
    
    # Restore workflows
    for workflow_file in "$BACKUP_DIR/workflows"/*.py; do
        if [ -f "$workflow_file" ]; then
            orchestrate tools import -k flow -f "$workflow_file" --env live
        fi
    done
    
    log_info "Rollback completed"
}

# Main deployment flow
main() {
    log_info "Starting deployment to live environment..."
    
    # Backup current state
    backup_live
    
    # Deploy in order
    deploy_connections
    deploy_models
    deploy_mcp_toolkits
    deploy_agents
    deploy_workflows
    
    # Verify
    verify_deployment
    
    log_info "Deployment completed successfully!"
    log_info "Backup location: $BACKUP_DIR"
}

# Handle errors
trap 'log_error "Deployment failed! Run rollback if needed."; exit 1' ERR

# Run deployment
main
```

### Python Deployment Script

```python
#!/usr/bin/env python3
"""
deploy_orchestration.py - Python deployment automation
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class OrchestrateDeployer:
    def __init__(self, env: str = "live"):
        self.env = env
        self.backup_dir = Path(f"backups/{datetime.now():%Y%m%d_%H%M%S}")
        
    def run_command(self, cmd: List[str]) -> Dict:
        """Execute orchestrate CLI command"""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "stdout": e.stdout,
                "stderr": e.stderr,
                "error": str(e)
            }
    
    def backup_environment(self):
        """Backup current live environment"""
        print(f"Creating backup: {self.backup_dir}")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup agents
        agents_dir = self.backup_dir / "agents"
        agents_dir.mkdir(exist_ok=True)
        self.run_command([
            "orchestrate", "agents", "export",
            "--env", self.env,
            "--output", str(agents_dir)
        ])
        
        # Backup workflows
        workflows_dir = self.backup_dir / "workflows"
        workflows_dir.mkdir(exist_ok=True)
        self.run_command([
            "orchestrate", "tools", "export",
            "--env", self.env,
            "--kind", "flow",
            "--output", str(workflows_dir)
        ])
        
        print(f"Backup completed: {self.backup_dir}")
    
    def deploy_connections(self):
        """Deploy all connections"""
        print("Deploying connections...")
        
        connections_dir = Path("connections")
        if not connections_dir.exists():
            print("No connections directory found")
            return
        
        for conn_file in connections_dir.glob("*.yaml"):
            conn_name = conn_file.stem
            print(f"Deploying connection: {conn_name}")
            
            # Add connection
            self.run_command([
                "orchestrate", "connections", "add",
                "-f", str(conn_file),
                "--env", self.env
            ])
            
            # Configure connection
            self.run_command([
                "orchestrate", "connections", "configure",
                "-a", conn_name,
                "--env", self.env,
                "--type", "team",
                "--kind", "key_value"
            ])
            
            # Set credentials from environment
            api_key_var = f"{conn_name.upper()}_API_KEY"
            if api_key_var in os.environ:
                self.run_command([
                    "orchestrate", "connections", "set-credentials",
                    "-a", conn_name,
                    "--env", self.env,
                    "-e", f"{api_key_var}={os.environ[api_key_var]}"
                ])
    
    def deploy_models(self):
        """Deploy AI Gateway models"""
        print("Deploying models...")
        
        models_dir = Path("models")
        if not models_dir.exists():
            print("No models directory found")
            return
        
        for model_file in models_dir.glob("*.yaml"):
            model_name = model_file.stem
            print(f"Deploying model: {model_name}")
            
            self.run_command([
                "orchestrate", "models", "add",
                "-f", str(model_file),
                "--env", self.env
            ])
    
    def deploy_mcp_toolkits(self):
        """Deploy MCP toolkits"""
        print("Deploying MCP toolkits...")
        
        mcp_dir = Path("mcp-servers")
        if not mcp_dir.exists():
            print("No MCP servers directory found")
            return
        
        for toolkit_dir in mcp_dir.iterdir():
            if toolkit_dir.is_dir():
                toolkit_name = toolkit_dir.name
                print(f"Deploying MCP toolkit: {toolkit_name}")
                
                self.run_command([
                    "orchestrate", "tools", "import",
                    "--mcp", toolkit_name,
                    "--env", self.env
                ])
    
    def deploy_agents(self):
        """Deploy agents"""
        print("Deploying agents...")
        
        agents_dir = Path("agents")
        if not agents_dir.exists():
            print("No agents directory found")
            return
        
        for agent_file in agents_dir.glob("*.yaml"):
            agent_name = agent_file.stem
            print(f"Deploying agent: {agent_name}")
            
            self.run_command([
                "orchestrate", "agents", "import",
                "-f", str(agent_file),
                "--env", self.env
            ])
    
    def deploy_workflows(self):
        """Deploy workflows"""
        print("Deploying workflows...")
        
        workflows_dir = Path("workflows")
        if not workflows_dir.exists():
            print("No workflows directory found")
            return
        
        for workflow_file in workflows_dir.glob("*.py"):
            workflow_name = workflow_file.stem
            print(f"Deploying workflow: {workflow_name}")
            
            self.run_command([
                "orchestrate", "tools", "import",
                "-k", "flow",
                "-f", str(workflow_file),
                "--env", self.env
            ])
    
    def verify_deployment(self):
        """Verify deployment"""
        print("Verifying deployment...")
        
        # List agents
        result = self.run_command([
            "orchestrate", "agents", "list",
            "--env", self.env
        ])
        print("Agents:", result["stdout"])
        
        # List workflows
        result = self.run_command([
            "orchestrate", "tools", "list",
            "--env", self.env,
            "--kind", "flow"
        ])
        print("Workflows:", result["stdout"])
    
    def deploy(self):
        """Execute full deployment"""
        print(f"Starting deployment to {self.env} environment...")
        
        try:
            self.backup_environment()
            self.deploy_connections()
            self.deploy_models()
            self.deploy_mcp_toolkits()
            self.deploy_agents()
            self.deploy_workflows()
            self.verify_deployment()
            
            print("Deployment completed successfully!")
            print(f"Backup location: {self.backup_dir}")
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            print(f"Backup available at: {self.backup_dir}")
            sys.exit(1)

if __name__ == "__main__":
    deployer = OrchestrateDeployer(env="live")
    deployer.deploy()
```

## Rollback Procedures

### Quick Rollback

```bash
#!/bin/bash
# rollback.sh - Quick rollback to previous backup

BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "Usage: ./rollback.sh <backup_directory>"
    exit 1
fi

echo "Rolling back to: $BACKUP_DIR"

# Restore agents
for agent_file in "$BACKUP_DIR/agents"/*.yaml; do
    if [ -f "$agent_file" ]; then
        orchestrate agents import -f "$agent_file" --env live
    fi
done

# Restore workflows
for workflow_file in "$BACKUP_DIR/workflows"/*.py; do
    if [ -f "$workflow_file" ]; then
        orchestrate tools import -k flow -f "$workflow_file" --env live
    fi
done

echo "Rollback completed"
```

### Selective Rollback

```bash
# Rollback specific agent
orchestrate agents import -f backups/20260604/agents/my_agent.yaml --env live

# Rollback specific workflow
orchestrate tools import -k flow -f backups/20260604/workflows/my_flow.py --env live

# Rollback specific model
orchestrate models add -f backups/20260604/models/my_model.yaml --env live
```

## Monitoring Setup

### Health Check Script

```bash
#!/bin/bash
# health-check.sh - Monitor deployment health

check_agents() {
    echo "Checking agents..."
    orchestrate agents list --env live | grep -c "name:"
}

check_workflows() {
    echo "Checking workflows..."
    orchestrate tools list --env live --kind flow | grep -c "name:"
}

check_models() {
    echo "Checking models..."
    orchestrate models list --env live | grep -c "name:"
}

check_connections() {
    echo "Checking connections..."
    orchestrate connections list --env live | grep -c "name:"
}

# Run checks
echo "=== Health Check ==="
echo "Agents: $(check_agents)"
echo "Workflows: $(check_workflows)"
echo "Models: $(check_models)"
echo "Connections: $(check_connections)"
```

### Continuous Monitoring

```python
#!/usr/bin/env python3
"""
monitor.py - Continuous health monitoring
"""

import time
import subprocess
from datetime import datetime

def check_health():
    """Check system health"""
    checks = {
        "agents": ["orchestrate", "agents", "list", "--env", "live"],
        "workflows": ["orchestrate", "tools", "list", "--env", "live", "--kind", "flow"],
        "models": ["orchestrate", "models", "list", "--env", "live"]
    }
    
    results = {}
    for name, cmd in checks.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            count = result.stdout.count("name:")
            results[name] = {"status": "healthy", "count": count}
        except subprocess.CalledProcessError as e:
            results[name] = {"status": "error", "error": str(e)}
    
    return results

def main():
    """Monitor continuously"""
    while True:
        timestamp = datetime.now().isoformat()
        health = check_health()
        
        print(f"\n[{timestamp}] Health Check:")
        for component, status in health.items():
            print(f"  {component}: {status}")
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
```

## Production Best Practices

### Deployment Timing
- Deploy during low-traffic periods
- Schedule maintenance windows
- Notify users of planned deployments
- Have rollback plan ready

### Testing Strategy
- Test in draft environment first
- Run integration tests
- Perform load testing
- Validate all connections

### Security Checklist
- [ ] All credentials stored securely
- [ ] No hardcoded secrets in code
- [ ] Connection credentials configured
- [ ] Access controls verified
- [ ] Audit logging enabled

### Documentation
- Document all deployment steps
- Maintain runbook for common issues
- Keep architecture diagrams updated
- Track configuration changes

## Troubleshooting Deployment

### Connection Issues
```bash
# Verify connection
orchestrate connections test -a connection_name --env live

# Reconfigure if needed
orchestrate connections configure -a connection_name --env live --type team

# Reset credentials
orchestrate connections set-credentials -a connection_name --env live
```

### Agent Import Failures
```bash
# Check agent syntax
orchestrate agents validate -f agent.yaml

# View detailed error
orchestrate agents import -f agent.yaml --env live --verbose

# Check dependencies
orchestrate agents describe -a agent_name --env live
```

### Workflow Import Failures
```bash
# Validate workflow
python -m py_compile workflow.py

# Check imports
orchestrate tools import -k flow -f workflow.py --env live --dry-run

# View logs
orchestrate tools logs -n workflow_name --env live