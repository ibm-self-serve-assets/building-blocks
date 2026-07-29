# Integration Workflows

This guide covers step-by-step workflows for different integration scenarios.

## Workflow 1: Python Script for API Testing

**Use Case:** Quick testing and prototyping

<Steps>
<Step>
**Verify credentials and test connection**

- Ensure `.env` file has required variables
- Run connection test script
- Confirm token generation works
</Step>

<Step>
**Generate Python integration script**

Create script with:
- Authentication function
- Token management
- Agent invocation function
- Response extraction
- Example usage
- Error handling
</Step>

<Step>
**Test the script**

```bash
python test_agent.py
```

Verify:
- Token generates successfully
- Agent responds correctly
- Response extraction works
- Error handling catches issues
</Step>
</Steps>

**Key Components:**
- `generate_jwt_token()` - Authentication
- `invoke_agent()` - Send message
- `wait_for_completion()` - Poll for response
- `extract_response()` - Get agent's answer

## Workflow 2: Node.js/Express Backend Server

**Use Case:** Production API server

<Steps>
<Step>
**Set up project structure**

```bash
npm init -y
npm install express cors dotenv axios
```

Create files:
- `server.js` - Express server
- `watsonx-client.js` - Integration library
- `test-connection.js` - Connection test
- `.env` - Credentials
</Step>

<Step>
**Generate platform-specific authentication code**

Include:
- Token management with caching
- Automatic token refresh
- Error handling
- Retry logic with exponential backoff
</Step>

<Step>
**Create API endpoints**

Essential routes:
- `GET /api/health` - Health check
- `GET /api/agent/:agentId` - Get agent info
- `POST /api/chat` - Send message to agent
- `POST /api/threads` - Create conversation thread
- `GET /api/skills` - List available skills
</Step>

<Step>
**Add middleware and error handling**

- CORS configuration
- JSON body parsing
- Request logging
- Error handling middleware
- Rate limiting (optional)
</Step>

<Step>
**Test the server**

```bash
npm start
```

Test endpoints:
- Health check: `curl http://localhost:3000/api/health`
- Chat: `curl -X POST http://localhost:3000/api/chat -d '{"agentId":"...", "message":"Hello"}'`
</Step>
</Steps>

## Workflow 3: Full-Stack Web Application

**Use Case:** Complete chat interface

<Steps>
<Step>
**Choose frontend framework**

Options:
- Simple HTML/CSS/JavaScript
- React
- Vue
- Angular
</Step>

<Step>
**Set up backend server**

Follow Workflow 2 to create Express backend
</Step>

<Step>
**Generate frontend UI**

Components needed:
- Chat message display
- Message input form
- Loading states
- Error messages
- Connection status indicator
</Step>

<Step>
**Connect frontend to backend**

- Configure API base URL
- Implement fetch/axios calls
- Handle responses and errors
- Update UI with agent responses
</Step>

<Step>
**Test end-to-end**

Verify:
- Messages send successfully
- Responses display correctly
- Loading states work
- Errors show user-friendly messages
- Conversation history maintained
</Step>
</Steps>

## Workflow 4: Existing Agent Integration

**Use Case:** User has deployed agent and wants to integrate

<Steps>
<Step>
**Collect agent information**

Required:
- Agent ID
- Platform (IBM Cloud/AWS/On-prem)
- Instance ID
- API key
</Step>

<Step>
**Verify platform and credentials**

- Confirm platform matches deployment
- Test credentials with connection script
- Verify agent is accessible
</Step>

<Step>
**Test connection to agent**

```python
# Quick test
response = invoke_agent(host, instance_id, token, agent_id, "Hello")
print(response)
```
</Step>

<Step>
**Generate integration code**

Based on user's needs:
- Python script
- Node.js server
- Web application
- Integration library
</Step>

<Step>
**Test agent interaction**

- Send test messages
- Verify responses
- Check error handling
- Test conversation continuity
</Step>
</Steps>

## Workflow 5: Web App from Scratch

**Use Case:** User wants to create web app from scratch

<Steps>
<Step>
**Gather requirements**

Ask about:
- UI design preferences
- Framework choice (React/Vue/vanilla JS)
- Agent capabilities
- Target users
- Deployment environment
</Step>

<Step>
**Set up credentials**

- Create `.env` file
- Add platform-specific variables
- Test connection
</Step>

<Step>
**Generate full-stack application**

Backend:
- Express server with API routes
- Authentication middleware
- Agent integration
- Error handling

Frontend:
- Chat interface
- Message history
- Loading states
- Error displays
</Step>

<Step>
**Create documentation**

Generate README with:
- Setup instructions
- Environment variables
- Running the app
- API endpoints
- Troubleshooting
</Step>

<Step>
**Test end-to-end**

Complete testing:
- Backend API endpoints
- Frontend UI interactions
- Agent responses
- Error scenarios
- Multi-turn conversations
</Step>
</Steps>

## Workflow 6: Agent Creation + Integration

**Use Case:** User needs to create agent before integration

<Steps>
<Step>
**Use MCP server for agent creation guidance**

Search watsonx-orchestrate-adk-docs for:
- "how to create an agent"
- "agent YAML configuration"
- "deploying agents"
- "agent development workflow"
</Step>

<Step>
**Generate agent configuration files**

Create:
- Agent YAML/JSON configuration
- Tool definitions
- Deployment scripts
</Step>

<Step>
**Guide through deployment process**

- Deploy agent to watsonx Orchestrate
- Verify agent is accessible
- Get agent ID
</Step>

<Step>
**Proceed with integration workflow**

Once agent is deployed:
- Set up credentials
- Test connection
- Generate integration code
</Step>
</Steps>

## Code Generation Best Practices

### Always Include

1. **Comprehensive error handling**
   - Connection errors
   - Authentication failures
   - Timeout handling
   - Invalid responses

2. **Token management**
   - Caching (tokens valid 2 hours)
   - Automatic refresh
   - Expiration tracking

3. **Logging**
   - Request/response logging
   - Error logging
   - Performance metrics

4. **Input validation**
   - Agent ID format
   - Message length limits
   - Parameter types

5. **Documentation**
   - Setup instructions
   - API endpoint docs
   - Example usage
   - Troubleshooting guide

### Platform-Specific Considerations

**IBM Cloud:**
- Use IAM token generation
- Region-specific URLs
- Standard OAuth flow

**AWS:**
- Use JWT token generation
- No region prefix in hostname
- Different auth endpoint

**On-Premises:**
- Use Zen API key
- Custom hostname/port
- Namespace configuration

## Testing Strategy

### Connection Testing
```python
# Always test before building
def test_connection():
    token = generate_token(api_key)
    skills = list_skills(host, instance_id, token)
    print(f"✓ Connected - Found {len(skills)} skills")
```

### Integration Testing
```python
# Test complete flow
def test_integration():
    # 1. Generate token
    token = generate_token(api_key)
    
    # 2. Invoke agent
    result = invoke_agent(host, instance_id, token, agent_id, "Test message")
    
    # 3. Wait for response
    run_details = wait_for_completion(host, instance_id, token, result['run_id'])
    
    # 4. Extract response
    response = extract_response(run_details)
    
    assert response, "Response should not be empty"
    print(f"✓ Integration test passed: {response}")
```

### Error Scenario Testing
```python
# Test error handling
def test_error_scenarios():
    # Test invalid agent ID
    # Test expired token
    # Test network timeout
    # Test malformed response
```

## Common Integration Patterns

### Simple Agent Execution
```python
response = execute_agent_run(
    base_url=base_url,
    instance_id=instance_id,
    token=token,
    agent_id=agent_id,
    message="Hello, how can you help me?"
)
```

### Conversation with Thread
```python
# First message - creates thread
response1 = execute_agent_run(..., message="What's the weather?")
thread_id = response1['thread_id']

# Follow-up - uses same thread
response2 = execute_agent_run(..., message="What about tomorrow?", thread_id=thread_id)
```

### Streaming Response
```python
# Start streaming run
response = execute_agent_run(..., message="Tell me a story", stream=True)
run_id = response['id']

# Stream events
for event in stream_run_events(base_url, instance_id, token, run_id):
    if event.get('event') == 'run.step.delta':
        print(event.get('data', {}).get('content', ''), end='', flush=True)
```

### Context-Aware Execution
```python
response = execute_agent_run(
    ...,
    message="What's my account status?",
    context={
        "user_email": "john@example.com",
        "user_name": "John Doe",
        "account_id": "ACC123456"
    }
)
```

## Next Steps

After completing integration:
1. Review `troubleshooting.md` for common issues
2. Check `code-examples.md` for complete implementations
3. Test thoroughly before production deployment
4. Monitor performance and error rates
5. Implement logging and monitoring