# Troubleshooting Guide for WXO Domain Agent Builder

This guide helps you resolve common issues when building and deploying watsonx Orchestrate agents using the domain agent template.

## Table of Contents

1. [Environment Setup Issues](#environment-setup-issues)
2. [Tool Import Problems](#tool-import-problems)
3. [Knowledge Base Issues](#knowledge-base-issues)
4. [Agent Deployment Failures](#agent-deployment-failures)
5. [Runtime Errors](#runtime-errors)
6. [MCP Server Issues](#mcp-server-issues)
7. [Common Error Messages](#common-error-messages)

---

## Environment Setup Issues

### Problem: WXO_API_KEY not set

**Symptoms:**
```
Error: WXO_API_KEY environment variable is not set
```

**Solution:**
```bash
export WXO_API_KEY="your-api-key-here"
```

Or add to your `.env` file:
```
WXO_API_KEY=your-api-key-here
```

### Problem: Virtual environment not activated

**Symptoms:**
- `orchestrate` command not found
- Import errors for `ibm_watsonx_orchestrate`

**Solution:**
```bash
cd ~/src/wxo-adk
source .venv/bin/activate
orchestrate env activate wxo-uv-env
```

### Problem: Wrong Python version

**Symptoms:**
```
Error: Python 3.11+ required
```

**Solution:**
Check your Python version and use pyenv or conda to switch:
```bash
python --version
pyenv install 3.11.0
pyenv local 3.11.0
```

---

## Tool Import Problems

### Problem: Missing @tool decorator

**Symptoms:**
```
Error: Function is not recognized as a tool
```

**Solution:**
Ensure all tool functions have the `@tool` decorator:
```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def my_tool_function(param: str) -> dict:
    """Tool description"""
    return {"result": "value"}
```

### Problem: Tool already exists

**Symptoms:**
```
Error: Tool with name 'tool_name' already exists
```

**Solution:**
Remove the old tool first:
```bash
orchestrate tools remove -n tool_name
orchestrate tools import -k python -f tools/tool_name.py
```

### Problem: Import fails with syntax error

**Symptoms:**
```
SyntaxError: invalid syntax
```

**Solution:**
1. Check Python syntax in your tool file
2. Ensure proper indentation
3. Verify all imports are correct
4. Test the file independently:
```bash
python tools/your_tool.py
```

### Problem: Type hints missing or incorrect

**Symptoms:**
```
Error: Type annotations required for tool parameters
```

**Solution:**
Add proper type hints to all parameters and return values:
```python
from typing import Optional, List, Dict, Any

@tool
def my_tool(
    required_param: str,
    optional_param: Optional[int] = None
) -> Dict[str, Any]:
    """Tool with proper type hints"""
    return {"status": "success"}
```

---

## Knowledge Base Issues

### Problem: Knowledge base import fails

**Symptoms:**
```
Error: Failed to import knowledge base
```

**Solution:**
1. Verify YAML syntax:
```bash
python -c "import yaml; yaml.safe_load(open('knowledge_bases/your_kb.yaml'))"
```

2. Check file paths in the YAML are correct
3. Ensure embedding model is specified:
```yaml
embedding_model:
  model_id: ibm/slate-125m-english-rtrvr-v2
```

### Problem: Documents not found

**Symptoms:**
```
Error: Document file not found: data/file.csv
```

**Solution:**
1. Verify file exists: `ls -la data/`
2. Check file path in knowledge base YAML
3. Use absolute or relative paths correctly

### Problem: Embedding model not available

**Symptoms:**
```
Error: Embedding model not found
```

**Solution:**
Use one of the supported models:
- `ibm/slate-125m-english-rtrvr-v2` (recommended)
- `ibm/slate-30m-english-rtrvr-v2`

---

## Agent Deployment Failures

### Problem: Agent deployment fails

**Symptoms:**
```
Error: Failed to deploy agent
```

**Solution:**
1. Verify agent was imported first:
```bash
orchestrate agents list
```

2. Check agent name matches:
```bash
orchestrate agents deploy -n exact_agent_name
```

3. Ensure all tools and knowledge bases are imported

### Problem: Agent not showing in UI

**Symptoms:**
- Agent deployed successfully but not visible in WXO UI

**Solution:**
1. Wait 1-2 minutes for propagation
2. Refresh the browser
3. Check agent status:
```bash
orchestrate agents list
```

### Problem: Tools not available in agent

**Symptoms:**
- Agent deployed but tools don't work

**Solution:**
1. Re-import tools
2. Re-import agent configuration
3. **Deploy agent again** (critical step):
```bash
orchestrate agents deploy -n agent_name
```

---

## Runtime Errors

### Problem: Tool execution fails

**Symptoms:**
```
Error: Tool execution failed
```

**Solution:**
1. Check tool logs for specific error
2. Verify data files exist and are accessible
3. Test tool function independently:
```python
from tools.your_tool import your_function
result = your_function(test_param="value")
print(result)
```

### Problem: Tool data not returning expected results

**Symptoms:**
- Tool returns empty results or wrong data

**Solution:**
WXO tools run in isolated cloud environments and cannot access local files. Data must be embedded directly in tool code as Python dicts:
```python
# ✅ CORRECT: Embed data directly in tool
PATIENT_DATA = [
    {"patient_id": "PAT001", "name": "Sarah Johnson", "care_level": "Outpatient"},
    {"patient_id": "PAT002", "name": "Michael Chen", "care_level": "ICU"},
]

@tool
def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """Get patient by ID."""
    patient = next((p for p in PATIENT_DATA if p["patient_id"] == patient_id), None)
    if not patient:
        return {"error": f"Patient {patient_id} not found"}
    return patient
```

**Never** use `os.path`, `open()`, `csv.DictReader`, or `pd.read_csv` in deployed WXO tools — they will fail.

---

## MCP Server Issues

### Problem: MCP server not responding

**Symptoms:**
- `SearchIbmWatsonxOrchestrateAdk` tool not working
- `list_tools` command fails

**Solution:**
1. Check MCP server status in Bob settings
2. Restart MCP servers
3. Verify MCP configuration in `.bob/mcp.json`

### Problem: Cannot find WXO documentation

**Symptoms:**
- MCP search returns no results

**Solution:**
1. Use more specific search terms
2. Try alternative phrasings
3. Check MCP server logs for errors

---

## Common Error Messages

### "ibm-watsonx-orchestrate should not be in requirements.txt"

**Cause:** The WXO SDK is provided by the platform

**Solution:** Remove `ibm-watsonx-orchestrate` from requirements.txt

### "Tool decorator not found"

**Cause:** Missing import statement

**Solution:**
```python
from ibm_watsonx_orchestrate.agent_builder.tools import tool
```

### "Agent configuration invalid"

**Cause:** YAML syntax error or missing required fields

**Solution:**
1. Validate YAML syntax
2. Ensure all required fields are present:
   - `spec_version`
   - `name`
   - `llm`
   - `instructions`

### "Knowledge base vectorization failed"

**Cause:** Document format not supported or embedding model issue

**Solution:**
1. Use supported formats: CSV, TXT, PDF, DOCX
2. Verify embedding model is correct
3. Check document file size (< 10MB recommended)

---

## Getting Help

If you continue to experience issues:

1. **Check the logs:**
   ```bash
   orchestrate logs
   ```

2. **Verify your setup:**
   ```bash
   orchestrate env list
   orchestrate tools list
   orchestrate agents list
   ```

3. **Use MCP servers:**
   - Search WXO documentation with `SearchIbmWatsonxOrchestrateAdk`
   - Check existing tools with `list_tools`

4. **Review documentation:**
   - README.md - Quick start guide
   - TROUBLESHOOTING.md - This troubleshooting guide

5. **Common debugging workflow:**
   ```bash
   # 1. Check environment
   echo $WXO_API_KEY
   which orchestrate
   
   # 2. List current state
   orchestrate tools list
   orchestrate agents list
   orchestrate knowledge-bases list
   
   # 3. Re-import if needed
   orchestrate tools import -k python -f tools/your_tool.py
   orchestrate agents import -f agent_config.yaml
   
   # 4. Deploy
   orchestrate agents deploy -n your_agent_name
   ```

---

## Best Practices to Avoid Issues

1. **Always use type hints** in tool functions
2. **Test tools independently** before importing
3. **Use absolute or proper relative paths** for data files
4. **Deploy agents after any tool changes**
5. **Validate YAML files** before importing
6. **Check MCP documentation** before implementing WXO features
7. **Use the template patterns** - they're tested and proven
8. **Keep tool functions simple** - complex logic should be in separate modules

---

## Quick Reference Commands

```bash
# Environment
export WXO_API_KEY="your-key"
source ~/src/wxo-adk/.venv/bin/activate
orchestrate env activate wxo-uv-env

# Import workflow
orchestrate tools import -k python -f tools/tool_name.py
orchestrate knowledge-bases import -f knowledge_bases/kb_name.yaml
orchestrate agents import -f agent_config.yaml

# Deploy
orchestrate agents deploy -n agent_name

# Troubleshooting
orchestrate tools list
orchestrate agents list
orchestrate logs

# Cleanup
orchestrate tools remove -n tool_name
orchestrate agents remove -n agent_name