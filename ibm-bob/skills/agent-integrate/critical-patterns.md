# Critical Integration Patterns

⚠️ **MUST READ BEFORE CODING** ⚠️

These patterns are based on real-world debugging of failed integrations. Following these patterns prevents the most common integration failures.

## The 5 Critical Issues

### Issue #1: Message Format (MOST COMMON ERROR)

**Problem:** API expects message as an OBJECT with role and content, NOT a string.

**Error:** 422 Unprocessable Entity - "Input should be a valid dictionary"

**Wrong:**
```python
# ❌ This will fail
payload = {
    "agent_id": agent_id,
    "message": "Hello, how can you help me?"  # String - WRONG!
}
```

**Correct:**
```python
# ✅ Always use this format
payload = {
    "agent_id": agent_id,
    "message": {
        "role": "user",      # Required: must be "user"
        "content": message   # Required: the actual message text
    }
}
```

### Issue #2: Asynchronous Processing (Missing Response)

**Problem:** The initial POST returns immediately with metadata only. The actual agent response is NOT included. You must poll for the response.

**What you get from POST:**
```json
{
  "thread_id": "uuid",
  "run_id": "uuid",
  "task_id": "uuid",
  "message_id": "uuid"
}
```
⚠️ **NO AGENT RESPONSE TEXT HERE!**

**Correct Workflow:**

<Steps>
<Step>
POST /v1/orchestrate/runs → Get run_id
</Step>

<Step>
Wait 2-3 seconds for agent processing
</Step>

<Step>
GET /v1/orchestrate/runs/{run_id} → Get actual response
</Step>
</Steps>

**Complete Code:**
```python
# Step 1: Invoke agent
response = requests.post(url, json=payload, headers=headers)
run_id = response.json()['run_id']

# Step 2: Wait for processing
time.sleep(2)

# Step 3: Get response
status_url = f"{base_url}/v1/orchestrate/runs/{run_id}"
run_details = requests.get(status_url, headers=headers).json()

# Step 4: Extract response
response_text = run_details['result']['data']['message']['content'][0]['text']
```

### Issue #3: Response Extraction (Deeply Nested)

**Problem:** Agent response is deeply nested in the structure. Many developers look in the wrong place.

**Extraction Path:**
```
run_details → result → data → message → content[0] → text
```

**Complete Structure:**
```json
{
  "id": "run-uuid",
  "status": "completed",
  "result": {
    "data": {
      "message": {
        "content": [
          {
            "text": "THE ACTUAL RESPONSE HERE",
            "response_type": "text"
          }
        ]
      }
    }
  }
}
```

**Safe Extraction Code:**
```python
def extract_agent_response(run_details):
    """Safely extract agent response from nested structure"""
    try:
        result = run_details['result']
        data = result['data']
        message = data['message']
        content = message['content']
        text = content[0]['text']
        return text
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Failed to extract response: {e}")
```

### Issue #4: Hostname Configuration (DNS Errors)

**Problem:** Region-based hostnames don't work for AWS platform.

**Error:** `[Errno 8] nodename nor servname provided, or not known`

**Wrong:**
```python
# ❌ Region-based hostname doesn't exist
host = f"{region}.dl.watson-orchestrate.ibm.com"
# Results in: us-east-1.dl.watson-orchestrate.ibm.com (DNS fails)
```

**Correct:**
```python
# ✅ Use api.dl for AWS and IBM Cloud
host = "api.dl.watson-orchestrate.ibm.com"  # No region prefix
```

**Platform-Specific Hostnames:**
- **AWS:** `api.dl.watson-orchestrate.ibm.com`
- **IBM Cloud:** `api.dl.watson-orchestrate.ibm.com`
- **On-Premises:** Custom hostname from deployment

### Issue #5: Polling Strategy (Production-Ready)

**Problem:** Using fixed `sleep(2)` works for testing but isn't production-ready.

**Production Polling with Status Checks:**
```python
def wait_for_run_completion(host, instance_id, token, run_id, max_wait=30):
    """Poll run status until completed or timeout"""
    url = f"https://{host}/instances/{instance_id}/v1/orchestrate/runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    poll_interval = 1
    
    while time.time() - start_time < max_wait:
        response = requests.get(url, headers=headers)
        run_details = response.json()
        status = run_details.get('status')
        
        if status == 'completed':
            return run_details
        elif status == 'failed':
            raise RuntimeError(f"Run failed: {run_details.get('last_error')}")
        elif status == 'cancelled':
            raise RuntimeError("Run was cancelled")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Run did not complete within {max_wait} seconds")
```

**Exponential Backoff (More Efficient):**
```python
def wait_with_backoff(host, instance_id, token, run_id, max_wait=30):
    """Poll with exponential backoff: 0.5s, 1s, 2s, 4s, 8s"""
    wait_time = 0.5
    max_wait_time = 8
    
    while time.time() - start_time < max_wait:
        # Check status...
        if status == 'completed':
            return run_details
        
        time.sleep(wait_time)
        wait_time = min(wait_time * 2, max_wait_time)
```

## Quick Diagnostic Checklist

When integration fails, check these in order:

1. ✓ Is message formatted as `{"role": "user", "content": "text"}`?
2. ✓ Are you polling GET /v1/orchestrate/runs/{run_id} after POST?
3. ✓ Are you extracting from `result.data.message.content[0].text`?
4. ✓ Is hostname `api.dl.watson-orchestrate.ibm.com` (no region)?
5. ✓ Does path include `/instances/{instance_id}`?
6. ✓ Is JWT token still valid (not expired)?
7. ✓ Is agent ID correct and accessible?

## Complete Working Flow

```python
# 1. Generate JWT token
token = generate_jwt_token(api_key)

# 2. Invoke agent with CORRECT message format
payload = {
    "agent_id": "your-agent-id",
    "message": {
        "role": "user",
        "content": "Your question here"
    }
}
response = requests.post(
    f"https://api.dl.watson-orchestrate.ibm.com/instances/{instance_id}/v1/orchestrate/runs",
    json=payload,
    headers={"Authorization": f"Bearer {token}"}
)
run_id = response.json()['run_id']

# 3. Poll for completion
run_details = wait_for_run_completion(host, instance_id, token, run_id)

# 4. Extract response from nested structure
agent_response = run_details['result']['data']['message']['content'][0]['text']

print(agent_response)
```

## Production Best Practices

### Token Caching
```python
class TokenManager:
    def __init__(self):
        self.token = None
        self.expiry = None
    
    def get_token(self, api_key):
        # Check if token exists and is still valid (with 5-minute buffer)
        if self.token and self.expiry:
            if datetime.now() < self.expiry - timedelta(minutes=5):
                return self.token
        
        # Generate new token
        self.token = generate_jwt_token(api_key)
        self.expiry = datetime.now() + timedelta(seconds=7200)
        return self.token
```

### Retry Logic
```python
def invoke_with_retry(host, instance_id, token, agent_id, message, max_retries=3):
    """Invoke agent with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            return invoke_agent(host, instance_id, token, agent_id, message)
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)
```

### Comprehensive Error Handling
```python
def safe_agent_execution(host, instance_id, token, agent_id, message):
    """Execute agent with comprehensive error handling"""
    try:
        result = invoke_agent(host, instance_id, token, agent_id, message)
        run_id = result['run_id']
        run_details = wait_for_run_completion(host, instance_id, token, run_id)
        return extract_agent_response(run_details)
    except requests.exceptions.ConnectionError:
        return "Error: Unable to connect to watsonx Orchestrate API"
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return "Error: Authentication failed. Check your API key."
        elif e.response.status_code == 404:
            return "Error: Agent not found. Check your agent ID."
        elif e.response.status_code == 422:
            return "Error: Invalid request format. Check message structure."
    except TimeoutError:
        return "Error: Agent processing timed out. Try again later."
```

## Timing Metrics

Typical end-to-end timing:
- Token Generation: ~500ms
- Agent Invocation: ~200ms
- Agent Processing: 1-3 seconds
- Status Retrieval: ~200ms
- **Total:** 2-4 seconds

Plan your timeouts accordingly.