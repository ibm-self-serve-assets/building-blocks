# MCP Server Integration

## Critical Documentation-First Principle

⚠️ **MANDATORY**: BEFORE generating ANY MCP-related code, configuration, or CLI commands, you MUST search the watsonx Orchestrate ADK documentation.

```
Use: search_ibm_watsonx_orchestrate_adk
Queries: "MCP toolkit YAML schema", "orchestrate toolkits add", etc.
```

**Why this is critical:**
- Field names must be exact (e.g., `url` NOT `server_url`)
- CLI flags change between versions
- Syntax evolves with ADK updates
- Static examples may be outdated

## ADK Version Compatibility

### Current Version (ADK v1.15.0)
```bash
orchestrate toolkits import -f toolkit.yaml
```

### Future Version (ADK v2.0)
```bash
orchestrate toolkits add -f toolkit.yaml  # "import" renamed to "add"
```

**Always check your version:**
```bash
orchestrate --version
```

## MCP Fundamentals

MCP (Model Context Protocol) allows AI systems to connect to external data sources and tools.

### Two Types of Integration

**Local MCP Toolkits:**
- Run on same machine as watsonx Orchestrate
- Communicate via STDIO (stdin/stdout)
- Use cases: Development, NPM/PyPI packages, file system access

**Remote MCP Toolkits:**
- Hosted on remote servers
- Communicate via SSE or HTTP Streamable
- Use cases: Production, shared services, cloud capabilities

### Important Note

watsonx Orchestrate does NOT use `.bob/mcp.json` or client-side MCP configurations. Those are for MCP clients (Claude Desktop, VSCode, Cursor). In watsonx Orchestrate, use the ADK CLI to import MCP toolkits.

## Importing Local MCP Toolkits

### Command Structure

```bash
orchestrate toolkits add \
    --kind mcp \
    --name <toolkit-name> \
    --description "<description>" \
    --command "<start-command>" \
    --tools "*" \
    --app-id <connection-name>  # Optional
```

### NPM Package Example

```bash
# 1. Create connection for credentials
orchestrate connections add -a tavily

# 2. Configure for both environments
for env in draft live; do
    orchestrate connections configure \
        -a tavily \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a tavily \
        --env $env \
        -e "TAVILY_API_KEY=$TAVILY_API_KEY"
done

# 3. Import toolkit
orchestrate toolkits add \
    --kind mcp \
    --name tavily \
    --description "Search the internet" \
    --command "npx -y tavily-mcp@0.1.3" \
    --tools "*" \
    --app-id tavily
```

### PyPI Package Example

```bash
# Setup connection (same as above)
orchestrate connections add -a tavily
for env in draft live; do
    orchestrate connections configure \
        -a tavily \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a tavily \
        --env $env \
        -e "TAVILY_API_KEY=$TAVILY_API_KEY"
done

# Import from PyPI
orchestrate toolkits add \
    --kind mcp \
    --name tavily \
    --description "Search the internet" \
    --command "pipx run -y mcp-tavily@0.1.10" \
    --tools "*" \
    --app-id tavily
```

### Local Python Server

**Folder Structure:**
```
mcp_server/
├── server.py
└── requirements.txt
```

**Requirements:**
- Place `requirements.txt` at package root
- List all dependencies
- Server script must start MCP server

**Import Command:**
```bash
# Setup connection
orchestrate connections add -a db_tools

for env in draft live; do
    orchestrate connections configure \
        -a db_tools \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a db_tools \
        --env $env \
        -e "DB_PATH=/path/to/database.db"
done

# Import local server
orchestrate toolkits add \
    --kind mcp \
    --name database_tools \
    --description "Database operations" \
    --command "python server.py" \
    --package-root ./mcp_server \
    --language python \
    --tools "*" \
    --app-id db_tools
```

## Importing Remote MCP Toolkits

### YAML Configuration

**CRITICAL**: Use exact field names from documentation.

```yaml
spec_version: v1
kind: mcp
name: remote_toolkit
description: Remote MCP server toolkit
url: https://server.com/mcp  # NOTE: "url" NOT "server_url"
transport: streamable_http   # or "sse"
connections:
  - my_connection  # Optional
tools:
  - "*"  # Import all tools, or list specific ones
```

### Authentication Decision Tree

**URL-Based Authentication** (API key in URL):
```yaml
url: https://server.com/mcp/?apiKey=YOUR_KEY
transport: streamable_http
# No connections field needed
```

**Connection-Based Authentication** (standard headers):
```yaml
url: https://server.com/mcp
transport: streamable_http
connections:
  - my_connection
```

Setup connection:
```bash
orchestrate connections add -a my_connection

for env in draft live; do
    orchestrate connections configure \
        -a my_connection \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a my_connection \
        --env $env \
        -e "API_KEY=value"
done
```

### Import Remote Toolkit

```bash
orchestrate toolkits import -f remote-toolkit.yaml
```

## MCP Tool Naming Convention

⚠️ **CRITICAL RULE**: MCP toolkit tools ALWAYS use format: `toolkit_name:tool_name`

This is NON-NEGOTIABLE. You MUST use the full qualified name.

### How to Find Exact Tool Names

```bash
# 1. Import toolkit first
orchestrate toolkits import -f toolkit.yaml

# 2. List all tools
orchestrate tools list

# 3. Filter by toolkit
orchestrate tools list | grep toolkit_name

# 4. Copy EXACT name (toolkit:tool format)
```

### Agent Configuration

**INCORRECT:**
```yaml
tools:
  - list-issues  # WRONG - missing toolkit prefix
```

**CORRECT:**
```yaml
tools:
  - github:list-issues  # CORRECT - includes toolkit:tool
```

## CLI Command Verification

### Golden Rule

ALWAYS run `--help` before using any orchestrate command for the first time. NEVER assume flags exist.

### Common CLI Mistakes

**Wrong:**
```bash
orchestrate toolkits remove --name toolkit --force
# Error: No such option: --force
```

**Right:**
```bash
orchestrate toolkits remove --name toolkit
```

**Wrong:**
```bash
orchestrate toolkits list --name toolkit
# Error: No such option: --name
```

**Right:**
```bash
orchestrate toolkits list
```

**Wrong:**
```bash
orchestrate agents import agent.yaml
# Error: Got unexpected extra argument
```

**Right:**
```bash
orchestrate agents import -f agent.yaml
```

## Common Pitfalls and Solutions

### Incorrect YAML Field Names

**Mistake:** Using `server_url` instead of `url`

**Symptom:** Error: Both 'url' and 'transport' must be provided together

**Solution:** Always use `url` for remote MCP servers

**Prevention:** Search documentation for YAML schema before creating config

### Missing Toolkit Prefix

**Mistake:** Referencing tools without toolkit prefix

**Symptom:** Error: Failed to find tool. No tools found with the name 'tool_name'

**Solution:** Use `toolkit:tool` format (e.g., `github:list-issues`)

**Prevention:** Always list tools first: `orchestrate tools list`

### Using Non-Existent CLI Flags

**Mistake:** Using flags that don't exist (`--force`, `--format`)

**Symptom:** Error: No such option: --flag_name

**Solution:** Run `--help` to see available options

**Prevention:** Always check: `orchestrate [command] --help`

### Missing File Flag for Imports

**Mistake:** Using positional argument instead of `-f` flag

**Symptom:** Error: Got unexpected extra argument (filename)

**Solution:** Use `-f` flag for file paths

**Prevention:** Remember: file paths always need `-f` flag

## Step-by-Step Verification Workflow

### Phase 1: Preparation

**Step 1: Search Documentation FIRST**
```
Use: search_ibm_watsonx_orchestrate_adk
Query: "MCP toolkit YAML schema" or relevant topic
```

**Step 2: Verify CLI Syntax**
```bash
orchestrate toolkits add --help
```

### Phase 2: Toolkit Import

**Step 3: Import Toolkit**
```bash
orchestrate toolkits add ... OR orchestrate toolkits import -f file.yaml
```

**Step 4: Verify Import**
```bash
orchestrate toolkits list
```

**Step 5: List Tools**
```bash
orchestrate tools list | grep toolkit_name
```
**CRITICAL**: Note exact tool names for agent config

### Phase 3: Agent Creation

**Step 6: Create Agent Configuration**
- Use `toolkit:tool` format
- Use exact names from tools list

**Step 7: Import Agent**
```bash
orchestrate agents import -f agent.yaml
```

## Using MCP Tools in Agents

### Agent Configuration

```yaml
spec_version: v1
kind: agent
name: github_agent
description: Agent that can interact with GitHub
tools:
  - github:list-issues
  - github:create-issue
  - github:search-code
instructions: |
  You can help users manage GitHub repositories.
  Use the available tools to list, create, and search issues.
```

### In Workflows

```python
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END

@flow(name="github_workflow")
def build_workflow(aflow: Flow) -> Flow:
    """Workflow using MCP tools"""
    
    # Use MCP tool in workflow
    list_issues = aflow.tool("github:list-issues")
    
    # Or use agent with MCP tools
    github_agent = aflow.agent(
        name="github",
        agent="github_agent",
        message="List all open issues"
    )
    
    aflow.sequence(START, github_agent, END)
    return aflow
```

## Quick Troubleshooting Guide

### YAML Validation Error
**Message:** Both 'url' and 'transport' must be provided together

**Quick Fixes:**
- Check field name is `url` not `server_url`
- Verify `transport` field is present
- Verify transport value is `sse` or `streamable_http`

### Tool Not Found
**Message:** Failed to find tool. No tools found with the name 'X'

**Quick Fixes:**
```bash
orchestrate tools list | grep toolkit_name
# Copy exact tool name including toolkit prefix
# Update agent config with toolkit:tool format
```

### CLI Flag Error
**Message:** No such option: --flag_name

**Quick Fixes:**
```bash
orchestrate [command] --help
# Check available options
# Remove invalid flag
```

### 401 Unauthorized
**Message:** 401 Unauthorized from MCP server

**Quick Fixes:**
- Check if server uses URL-based auth (query parameters)
- Verify API key is in URL or connection
- Check connection credentials are set for environment

## Complete Example

End-to-end MCP toolkit setup:

```bash
# 1. Search documentation
# Use MCP tool: search_ibm_watsonx_orchestrate_adk
# Query: "MCP toolkit import example"

# 2. Create connection
orchestrate connections add -a github

# 3. Configure for both environments
for env in draft live; do
    orchestrate connections configure \
        -a github \
        --env $env \
        --type team \
        --kind key_value
    
    orchestrate connections set-credentials \
        -a github \
        --env $env \
        -e "GITHUB_TOKEN=$GITHUB_TOKEN"
done

# 4. Create toolkit YAML
cat > github-toolkit.yaml <<EOF
spec_version: v1
kind: mcp
name: github
description: GitHub operations toolkit
url: https://github-mcp.example.com
transport: streamable_http
connections:
  - github
tools:
  - "*"
EOF

# 5. Import toolkit
orchestrate toolkits import -f github-toolkit.yaml

# 6. Verify import
orchestrate toolkits list | grep github

# 7. List tools with exact names
orchestrate tools list | grep github:

# 8. Create agent using tools
cat > github-agent.yaml <<EOF
spec_version: v1
kind: agent
name: github_agent
description: GitHub operations agent
tools:
  - github:list-issues
  - github:create-issue
instructions: Help users manage GitHub repositories.
EOF

# 9. Import agent
orchestrate agents import -f github-agent.yaml

# 10. Test agent
orchestrate agents test github_agent
```

## Best Practices

- **Always search documentation first** before implementation
- **Test in draft environment** before deploying to live
- **Use exact tool names** with `toolkit:tool` format
- **Verify CLI commands** with `--help` before using
- **Set up connections** for both draft and live environments
- **List tools after import** to get exact names
- **Monitor toolkit health** and update regularly
- **Document custom toolkits** for team reference

## Error Recovery Workflow

When encountering ANY error:

1. **Analyze error message** - Extract what failed
2. **Search documentation** - Find correct syntax
3. **Apply fix from docs** - Use exact syntax
4. **Verify fix works** - Confirm error resolved
5. **Document learning** - Note correct approach