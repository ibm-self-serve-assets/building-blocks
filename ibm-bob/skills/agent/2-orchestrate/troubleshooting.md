# Troubleshooting Guide

## Agent Issues

### Agent Not Responding

**Symptoms:**
- Agent doesn't respond to messages
- Timeout errors
- No output generated

**Diagnosis:**
```bash
# Check agent status
orchestrate agents describe -a agent_name --env live

# View agent logs
orchestrate agents logs -a agent_name --env live --tail 50

# Test agent directly
orchestrate agents test -a agent_name --message "test message"
```

**Common Causes:**
1. **Model unavailable**: Check model status and connection
2. **Tool errors**: Verify all tools are accessible
3. **Memory issues**: Check conversation history size
4. **Rate limiting**: Check API rate limits

**Solutions:**
```bash
# Restart agent
orchestrate agents restart -a agent_name --env live

# Clear conversation history
orchestrate agents clear-history -a agent_name

# Check model connection
orchestrate models test -m model_name --env live

# Verify tool availability
orchestrate tools list --env live
```

### Agent Gives Incorrect Responses

**Symptoms:**
- Agent provides wrong information
- Agent doesn't follow instructions
- Agent uses wrong tools

**Diagnosis:**
```bash
# Review agent configuration
orchestrate agents export -a agent_name --env live

# Check instruction clarity
cat agents/agent_name.yaml | grep -A 20 "instructions:"

# Review conversation history
orchestrate agents history -a agent_name --limit 10
```

**Solutions:**
1. **Improve instructions**: Make instructions more specific and clear
2. **Add examples**: Include few-shot examples in instructions
3. **Refine description**: Ensure agent description matches capabilities
4. **Update model**: Try different model or adjust temperature

```yaml
# Better instructions example
instructions: |
  You are a billing specialist. Follow these rules:
  1. Always verify customer identity before processing payments
  2. Use process_payment tool for all payment operations
  3. Provide itemized breakdowns for all charges
  4. Never discuss technical issues - route to technical_agent
```

### Collaborator Not Being Called

**Symptoms:**
- Supervisor doesn't delegate to collaborators
- Wrong collaborator selected
- Collaborator ignored

**Diagnosis:**
```bash
# Check collaborator configuration
orchestrate agents describe -a supervisor_agent --env live

# Review delegation logs
orchestrate agents logs -a supervisor_agent --filter "collaborator"
```

**Solutions:**
1. **Improve collaborator descriptions**: Make descriptions more specific
2. **Add routing instructions**: Explicitly state when to use each collaborator
3. **Test delegation**: Use test messages that should trigger delegation

```python
# Better collaborator descriptions
billing_agent = Agent(
    name="billing_specialist",
    description="""
    ONLY handles: billing inquiries, payment processing, invoices,
    refunds, account charges, subscription management.
    
    CANNOT handle: technical issues, product questions, account setup.
    
    Use when user mentions: payment, bill, invoice, charge, refund,
    subscription, pricing.
    """
)
```

## Workflow Issues

### Workflow Fails to Start

**Symptoms:**
- Workflow doesn't execute
- Import errors
- Validation failures

**Diagnosis:**
```bash
# Validate workflow syntax
python -m py_compile workflow.py

# Check workflow import
orchestrate tools import -k flow -f workflow.py --dry-run

# View import errors
orchestrate tools import -k flow -f workflow.py --verbose
```

**Common Causes:**
1. **Syntax errors**: Python syntax issues
2. **Import errors**: Missing dependencies
3. **Schema errors**: Invalid input/output schemas
4. **Decorator errors**: Incorrect @flow usage

**Solutions:**
```bash
# Fix syntax errors
python -m pylint workflow.py

# Install dependencies
pip install -r requirements.txt

# Validate schemas
python -c "from workflow import build_flow; print(build_flow.__annotations__)"

# Re-import workflow
orchestrate tools import -k flow -f workflow.py --force
```

### Workflow Hangs or Times Out

**Symptoms:**
- Workflow never completes
- Timeout errors
- Stuck in specific node

**Diagnosis:**
```bash
# Check workflow status
orchestrate flows status -n workflow_name

# View execution logs
orchestrate flows logs -n workflow_name --instance-id <id>

# Check node execution
orchestrate flows describe -n workflow_name
```

**Common Causes:**
1. **Infinite loops**: Loop without exit condition
2. **Blocking operations**: Long-running synchronous calls
3. **Deadlocks**: Circular dependencies
4. **Resource exhaustion**: Memory or connection limits

**Solutions:**
```python
# Add timeout to loop
@flow(name="safe_loop")
def build_safe_loop(aflow: Flow) -> Flow:
    loop_node = aflow.loop(
        evaluator="flow.state.counter < 100",  # Add limit
        max_iterations=100  # Hard limit
    )
    return aflow

# Add timeout to agent calls
agent_node = aflow.agent(
    name="agent",
    agent="my_agent",
    timeout=30  # 30 second timeout
)

# Use async operations
async_tool = aflow.tool(
    "async_operation",
    async_mode=True
)
```

### Branch Not Taking Expected Path

**Symptoms:**
- Wrong branch executed
- Branch condition not evaluated
- Unexpected flow path

**Diagnosis:**
```bash
# Check branch evaluator
orchestrate flows describe -n workflow_name | grep -A 5 "branch"

# View state at branch point
orchestrate flows logs -n workflow_name --filter "branch"

# Test evaluator
python -c "from workflow import evaluator; print(evaluator({'state': {'value': 10}}))"
```

**Solutions:**
```python
# Use explicit boolean evaluator
branch = aflow.branch(
    evaluator="flow.state.approved == true"  # Explicit boolean
)

# Add logging before branch
log_state = aflow.tool("log_current_state")
aflow.edge(previous_node, log_state)
aflow.edge(log_state, branch)

# Test all branch paths
branch.case(True, success_path)
branch.case(False, failure_path)
branch.default(error_handler)  # Add default case
```

## MCP Integration Issues

### MCP Server Not Found

**Symptoms:**
- "Toolkit not found" errors
- Tools not available
- Import failures

**Diagnosis:**
```bash
# List available toolkits
orchestrate tools list --kind mcp

# Check MCP server status
orchestrate tools describe --mcp toolkit_name

# Test MCP connection
orchestrate tools test --mcp toolkit_name
```

**Solutions:**
```bash
# Re-import MCP toolkit
orchestrate tools import --mcp toolkit_name

# Check MCP server configuration
cat mcp-servers/toolkit_name/config.json

# Verify server is running
ps aux | grep mcp-server

# Restart MCP server
orchestrate tools restart --mcp toolkit_name
```

### MCP Tool Execution Fails

**Symptoms:**
- Tool returns errors
- Timeout on tool calls
- Invalid responses

**Diagnosis:**
```bash
# Test tool directly
orchestrate tools execute --mcp toolkit_name:tool_name --args '{"param": "value"}'

# View tool logs
orchestrate tools logs --mcp toolkit_name

# Check tool schema
orchestrate tools describe --mcp toolkit_name:tool_name
```

**Common Causes:**
1. **Wrong tool name format**: Must use `toolkit:tool` format
2. **Invalid arguments**: Arguments don't match schema
3. **Server errors**: MCP server internal errors
4. **Connection issues**: Network or authentication problems

**Solutions:**
```python
# Always use toolkit:tool format
agent = Agent(
    name="mcp_agent",
    tools=["database-tools:query_database"]  # Correct format
)

# Validate arguments match schema
tool_args = {
    "query": "SELECT * FROM users",
    "params": []
}

# Add error handling
try:
    result = orchestrate.tools.execute(
        "database-tools:query_database",
        args=tool_args
    )
except Exception as e:
    print(f"Tool execution failed: {e}")
```

### Remote MCP Server Connection Issues

**Symptoms:**
- Cannot connect to remote server
- Authentication failures
- Timeout errors

**Diagnosis:**
```bash
# Test connection
curl -X POST https://remote-mcp-server.com/health

# Check authentication
orchestrate connections test -a mcp_connection

# View connection logs
orchestrate connections logs -a mcp_connection
```

**Solutions:**
```bash
# Reconfigure connection
orchestrate connections configure \
    -a mcp_connection \
    --env live \
    --type team

# Update credentials
orchestrate connections set-credentials \
    -a mcp_connection \
    --env live \
    -e "API_KEY=$NEW_API_KEY"

# Test with verbose logging
orchestrate tools import --mcp toolkit_name --verbose
```

## AI Gateway Issues

### Model Not Available

**Symptoms:**
- "Model not found" errors
- Cannot create agents with model
- Model list doesn't show model

**Diagnosis:**
```bash
# List available models
orchestrate models list --env live

# Check model configuration
orchestrate models describe -m model_name --env live

# Test model
orchestrate models test -m model_name --env live
```

**Solutions:**
```bash
# Re-import model
orchestrate models add -f models/model_name.yaml --env live

# Verify connection
orchestrate connections test -a model_connection --env live

# Check model policy
orchestrate models policies list --env live
```

### Model API Errors

**Symptoms:**
- 401 Unauthorized
- 429 Rate limit exceeded
- 500 Server errors

**Diagnosis:**
```bash
# Check connection credentials
orchestrate connections describe -a connection_name --env live

# View API logs
orchestrate models logs -m model_name --env live

# Test with different model
orchestrate models test -m backup_model --env live
```

**Solutions:**
```bash
# Update credentials
orchestrate connections set-credentials \
    -a openai \
    --env live \
    -e "OPENAI_API_KEY=$NEW_KEY"

# Add rate limiting
cat > model-policy.yaml <<EOF
spec_version: v1
kind: model_policy
name: rate_limited_policy
models:
  - model_name
config:
  rate_limit: 10  # requests per second
  retry_attempts: 3
  retry_delay: 1000  # milliseconds
EOF

orchestrate models policies add -f model-policy.yaml --env live

# Use fallback model
cat > model-policy.yaml <<EOF
spec_version: v1
kind: model_policy
name: fallback_policy
models:
  - primary_model
  - backup_model
strategy: fallback
EOF
```

### Model Policy Not Working

**Symptoms:**
- Load balancing not distributing
- Fallback not triggering
- Policy not applied

**Diagnosis:**
```bash
# Check policy configuration
orchestrate models policies describe -p policy_name --env live

# View policy logs
orchestrate models policies logs -p policy_name --env live

# Test policy behavior
orchestrate models test -m model_name --policy policy_name
```

**Solutions:**
```bash
# Verify policy syntax
orchestrate models policies validate -f policy.yaml

# Re-apply policy
orchestrate models policies add -f policy.yaml --force --env live

# Check model assignment
orchestrate models describe -m model_name --env live | grep policy
```

## A2A Protocol Issues

### External Agent Not Responding

**Symptoms:**
- External agent doesn't respond
- Connection timeout
- Authentication failures

**Diagnosis:**
```bash
# Test external agent endpoint
curl -X POST https://external-agent.com/a2a/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Check agent configuration
orchestrate agents describe -a external_agent --env live

# View connection logs
orchestrate agents logs -a external_agent --filter "external"
```

**Solutions:**
```python
# Verify A2A configuration
external_agent = ExternalAgent(
    kind=AgentKind.EXTERNAL,
    name="external_agent",
    provider="external_chat/A2A/0.3.0",  # Use v0.3.0
    api_url="https://external-agent.com/a2a",
    auth_scheme=ExternalAgentAuthScheme.BEARER_TOKEN,
    auth_config={"token": "${EXTERNAL_AGENT_TOKEN}"}
)

# Test authentication
orchestrate connections test -a external_agent_connection

# Update endpoint
orchestrate agents update -a external_agent \
    --api-url "https://new-endpoint.com/a2a"
```

### A2A Version Mismatch

**Symptoms:**
- Protocol errors
- Incompatible message format
- Handshake failures

**Diagnosis:**
```bash
# Check A2A version
curl https://external-agent.com/a2a/version

# View protocol logs
orchestrate agents logs -a external_agent --filter "protocol"
```

**Solutions:**
```python
# Use correct A2A version (0.3.0)
external_agent = ExternalAgent(
    provider="external_chat/A2A/0.3.0",  # Not 0.2.1
    # ... rest of config
)

# Update external agent to support 0.3.0
# See A2A 0.3.0 specification for changes
```

## Performance Issues

### Slow Agent Responses

**Symptoms:**
- Long response times
- Timeout warnings
- Poor user experience

**Diagnosis:**
```bash
# Measure response time
time orchestrate agents test -a agent_name --message "test"

# Check model latency
orchestrate models benchmark -m model_name

# View performance metrics
orchestrate agents metrics -a agent_name --env live
```

**Solutions:**
```python
# Use faster model
agent = Agent(
    name="fast_agent",
    model="gpt-3.5-turbo",  # Faster than gpt-4
    # ... rest of config
)

# Reduce context size
agent = Agent(
    name="optimized_agent",
    max_history=5,  # Limit conversation history
    # ... rest of config
)

# Use streaming
agent = Agent(
    name="streaming_agent",
    stream=True,  # Enable streaming responses
    # ... rest of config
)

# Cache common responses
agent = Agent(
    name="cached_agent",
    cache_enabled=True,
    # ... rest of config
)
```

### High Resource Usage

**Symptoms:**
- High memory consumption
- CPU spikes
- Connection pool exhaustion

**Diagnosis:**
```bash
# Check resource usage
orchestrate system metrics --env live

# View active connections
orchestrate connections status --env live

# Check workflow instances
orchestrate flows list --status running
```

**Solutions:**
```bash
# Limit concurrent workflows
orchestrate config set max_concurrent_flows 10

# Increase connection pool
orchestrate connections configure \
    -a connection_name \
    --pool-size 20

# Clean up old instances
orchestrate flows cleanup --older-than 7d

# Optimize memory usage
orchestrate config set max_memory_per_agent 512M
```

## Deployment Issues

### Import Failures

**Symptoms:**
- Cannot import agents/workflows
- Validation errors
- Dependency issues

**Diagnosis:**
```bash
# Validate before import
orchestrate agents validate -f agent.yaml
orchestrate tools validate -f workflow.py

# Check dependencies
orchestrate agents dependencies -f agent.yaml

# View detailed errors
orchestrate agents import -f agent.yaml --verbose
```

**Solutions:**
```bash
# Fix validation errors
orchestrate agents validate -f agent.yaml --fix

# Install dependencies
pip install -r requirements.txt

# Force import
orchestrate agents import -f agent.yaml --force --env live
```

### Environment Sync Issues

**Symptoms:**
- Draft and live out of sync
- Missing resources in live
- Configuration drift

**Diagnosis:**
```bash
# Compare environments
orchestrate agents list --env draft > draft.txt
orchestrate agents list --env live > live.txt
diff draft.txt live.txt

# Check specific resource
orchestrate agents describe -a agent_name --env draft
orchestrate agents describe -a agent_name --env live
```

**Solutions:**
```bash
# Sync specific agent
orchestrate agents export -a agent_name --env draft
orchestrate agents import -f agent_name.yaml --env live

# Sync all agents
./deploy-orchestration.sh

# Verify sync
orchestrate agents list --env live
```

## Getting Help

### Enable Debug Logging
```bash
# Set debug mode
export WXO_DEBUG=true

# Run command with verbose output
orchestrate agents import -f agent.yaml --verbose --debug

# View full logs
orchestrate logs --level debug --tail 100
```

### Collect Diagnostic Information
```bash
#!/bin/bash
# collect-diagnostics.sh

echo "=== System Info ===" > diagnostics.txt
orchestrate version >> diagnostics.txt

echo "\n=== Agents ===" >> diagnostics.txt
orchestrate agents list --env live >> diagnostics.txt

echo "\n=== Workflows ===" >> diagnostics.txt
orchestrate tools list --kind flow --env live >> diagnostics.txt

echo "\n=== Models ===" >> diagnostics.txt
orchestrate models list --env live >> diagnostics.txt

echo "\n=== Connections ===" >> diagnostics.txt
orchestrate connections list --env live >> diagnostics.txt

echo "\n=== Recent Logs ===" >> diagnostics.txt
orchestrate logs --tail 50 >> diagnostics.txt

echo "Diagnostics saved to diagnostics.txt"
```

### Contact Support
- Include diagnostic information
- Provide error messages and logs
- Describe steps to reproduce
- Share relevant configuration files (redact secrets)