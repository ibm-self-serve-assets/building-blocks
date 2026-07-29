# Deployment Safety Rules

Critical rules for deployment automation and script generation to ensure safe, correct, and user-controlled deployment processes.

## Critical Deployment Rules

### Rule 1: Never Execute Deployment Commands Without Permission (HIGHEST PRIORITY)

**NEVER execute deployment commands (import, deploy, configure, delete) directly without explicit user permission. Always create deployment scripts instead.**

**Why:** Users need to review and control when assets are deployed to their environments. Direct execution can cause unexpected changes or conflicts.

**Correct approach:** Create deployment scripts and inform user how to run them

**Wrong approach:** Running orchestrate commands directly during implementation

### Rule 2: Always Query MCP Docs for CLI Commands (HIGHEST PRIORITY)

**Before creating deployment scripts, ALWAYS search the watsonx-orchestrate-adk-docs MCP server for the correct CLI command syntax, flags, and parameters.**

**Why:** CLI commands and syntax can change between ADK versions. MCP docs provide the most up-to-date and accurate command reference.

**MCP queries to use:**
- "orchestrate tools import syntax"
- "orchestrate agents import command"
- "orchestrate knowledge import parameters"
- "orchestrate connections configure flags"

**Verification:** Use `execute_command` with --help flag to verify syntax if needed

### Rule 3: Validate Folder Structure and Paths (HIGHEST PRIORITY)

**Always validate the project folder structure and provide correct relative paths in deployment scripts. Ensure scripts can find all asset files.**

**Validation steps:**
1. Use `list_files` to verify project structure
2. Confirm agents/ folder contains agent YAML files
3. Confirm tools/ folder contains Python tool files
4. Confirm knowledge/ folder exists if knowledge bases are used
5. Confirm connections/ folder exists if connections are used

**Path considerations:**
- Script location (typically scripts/ folder)
- Project root location
- Asset file locations (agents/, tools/, etc.)
- Working directory when script executes

**Solution:** Add directory change command at start of script:
```bash
cd "$(dirname "$0")/.."  # Change to project root
```

### Rule 4: Test CLI Commands with --help (HIGH PRIORITY)

**When uncertain about CLI command syntax, use `execute_command` with --help flag to verify the correct usage before adding to deployment scripts.**

**Examples:**
```bash
orchestrate tools import --help
orchestrate agents import --help
orchestrate connections configure --help
```

## Deployment Script Workflow

<Steps>
<Step>
**Search MCP Docs for CLI Commands**

Query watsonx-orchestrate-adk-docs MCP server:
- "orchestrate tools import command syntax"
- "orchestrate agents import parameters"
- "orchestrate knowledge import flags"
- "CLI deployment automation"

Purpose: Get exact, up-to-date command syntax and parameters
</Step>

<Step>
**Validate Project Structure**

Use `list_files` to verify folder structure:
- ✓ agents/ folder exists with YAML files
- ✓ tools/ folder exists with Python files
- ✓ knowledge/ folder exists if needed
- ✓ connections/ folder exists if needed
- ✓ scripts/ folder exists for deployment scripts
</Step>

<Step>
**Determine Correct Paths**

Considerations:
- Script will be in scripts/ folder
- Assets are in sibling folders (agents/, tools/, etc.)
- Need to change to project root before running commands

Solution:
- Bash: `cd "$(dirname "$0")/.."`
- Python: `os.chdir(os.path.dirname(os.path.dirname(__file__)))`
</Step>

<Step>
**Create Deployment Script**

Requirements:
- Change to project root directory first
- Use exact CLI syntax from MCP docs
- Use correct relative paths to assets
- Include all required flags and parameters
- Add error handling (set -e for bash)
- Include clear progress messages
- Make script executable (chmod +x)

Template:
```bash
#!/bin/bash
set -e  # Exit on error

# Change to project root
cd "$(dirname "$0")/.."

echo "Deploying assets..."

# Import tools
orchestrate tools import -k python -f tools/tool_name.py -p .

# Import agents  
orchestrate agents import -f agents/agent_name.yaml

# Verify
orchestrate tools list
orchestrate agents list

echo "Deployment complete!"
```
</Step>

<Step>
**Create Rollback Script**

Purpose: Enable safe removal of deployed assets

Template:
```bash
#!/bin/bash
set -e

cd "$(dirname "$0")/.."

echo "Rolling back deployment..."

orchestrate agents delete --name agent_name --force
orchestrate tools delete --name tool_name --force

echo "Rollback complete!"
```
</Step>

<Step>
**Inform User**

Message template:
"I've created deployment scripts in the scripts/ folder:
- deploy.sh: Deploys all assets to your active environment
- rollback.sh: Removes deployed assets if needed

To deploy:
1. Review the scripts to ensure they match your environment
2. Run: cd project_name && ./scripts/deploy.sh

The script will import all assets to your currently active environment."

**NEVER execute deployment commands directly**
</Step>
</Steps>

## Common CLI Command Patterns

### Import Python Tool
```bash
orchestrate tools import -k python -f tools/tool_name.py -p .
```

**Flags:**
- `-k`: Kind of tool (python, openapi, langflow)
- `-f`: File path to tool (relative to current directory)
- `-p`: Package root directory (. for current directory)
- `-r`: Requirements file (optional)
- `-a`: App ID for connection (optional)

### Import Agent
```bash
orchestrate agents import -f agents/agent_name.yaml
```

**Flags:**
- `-f`: File path to agent specification YAML

### Import Knowledge Base
```bash
orchestrate knowledge import -f knowledge/kb_spec.yaml
```

**Flags:**
- `-f`: File path to knowledge base specification

### Configure Connection
```bash
orchestrate connections configure -a app_id --env draft -t team -k basic
```

**Flags:**
- `-a`: Application ID
- `--env`: Environment (draft or live)
- `-t`: Type (team or personal)
- `-k`: Kind (basic, oauth, key_value, etc.)

### Set Connection Credentials
```bash
orchestrate connections set-credentials -a app_id --env draft -e "KEY=value"
```

**Flags:**
- `-a`: Application ID
- `--env`: Environment (draft or live)
- `-e`: Environment variable (KEY=value format)

### Deploy Agent to Live
```bash
orchestrate agents deploy --name agent_name
```

**Flags:**
- `--name`: Agent name to deploy from draft to live

### Generate Webchat Embed
```bash
orchestrate channels webchat embed --agent-name agent_name
```

**Flags:**
- `--agent-name`: Agent name for webchat integration

### Delete Agent
```bash
orchestrate agents delete --name agent_name --force
```

**Flags:**
- `--name`: Agent name to delete
- `--force`: Skip confirmation prompt

### Delete Tool
```bash
orchestrate tools delete --name tool_name --force
```

**Flags:**
- `--name`: Tool name to delete
- `--force`: Skip confirmation prompt

## Path Resolution Guide

### Script in scripts/ Folder

Project structure:
```
project_root/
├── agents/
│   └── agent.yaml
├── tools/
│   └── tool.py
└── scripts/
    └── deploy.sh  # Script location
```

Solution:
1. Add: `cd "$(dirname "$0")/.."`
2. Now in project_root/
3. Use: agents/agent.yaml, tools/tool.py

### Script in Project Root

Project structure:
```
project_root/
├── agents/
│   └── agent.yaml
├── tools/
│   └── tool.py
└── deploy.sh  # Script location
```

Solution:
1. Already in project_root/
2. Use: agents/agent.yaml, tools/tool.py

## Error Prevention

### Wrong Command Syntax
- **Symptom:** Command not found or invalid option errors
- **Cause:** Using outdated or incorrect CLI syntax
- **Prevention:** Always search MCP docs for current syntax
- **Fix:** Query MCP docs and update script with correct syntax

### Incorrect Paths
- **Symptom:** File not found errors during deployment
- **Cause:** Wrong relative paths or missing directory change
- **Prevention:** Validate structure and add cd command to script
- **Fix:** Add `cd "$(dirname "$0")/.."` and verify paths

### Missing Package Root
- **Symptom:** Python module import errors for tools
- **Cause:** Missing -p flag when importing Python tools
- **Prevention:** Always include -p . flag for Python tools
- **Fix:** Add -p . to orchestrate tools import command

### Executing Without Permission
- **Symptom:** User surprised by deployed assets
- **Cause:** Running deployment commands directly
- **Prevention:** Always create scripts, never execute directly
- **Fix:** Create deployment script and inform user

## Best Practices

1. Search MCP docs before every deployment script creation
2. Validate folder structure with `list_files`
3. Test CLI commands with --help when uncertain
4. Add clear progress messages to scripts
5. Include error handling (set -e for bash)
6. Create both deploy and rollback scripts
7. Document deployment process in README.md
8. **Never execute deployment commands directly**
9. Always inform user how to run deployment scripts