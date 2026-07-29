# Troubleshooting Guide

Common integration issues and their solutions.

## Quick Diagnostic Checklist

When integration fails, check these in order:

1. ✓ Is message formatted as `{"role": "user", "content": "text"}`?
2. ✓ Are you polling GET /v1/orchestrate/runs/{run_id} after POST?
3. ✓ Are you extracting from `result.data.message.content[0].text`?
4. ✓ Is hostname `api.dl.watson-orchestrate.ibm.com` (no region)?
5. ✓ Does path include `/instances/{instance_id}`?
6. ✓ Is JWT token still valid (not expired)?
7. ✓ Is agent ID correct and accessible?

## Authentication Issues

### Invalid API Key (401 Unauthorized)

**Symptoms:**
- 401 Unauthorized error
- "Invalid API key" message
- Token generation fails

**Diagnosis:**
1. Verify API key is copied correctly (no extra spaces)
2. Check if API key has expired
3. Confirm API key is for the correct platform
4. Verify API key has necessary permissions

**Solutions:**
- Regenerate API key from platform console
- Ensure `.env` file has correct variable names
- Check for hidden characters in API key
- Verify API key is not revoked

**Debug Code:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('WATSONX_API_KEY')

print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:10] if api_key else 'None'}...")
print(f"Has whitespace: {api_key != api_key.strip() if api_key else 'N/A'}")
```

### Token Expired (401 After Initial Success)

**Symptoms:**
- 401 error after initial success
- "Token expired" message
- Intermittent authentication failures

**Diagnosis:**
1. Check token expiration time (2 hours)
2. Verify token refresh logic is implemented
3. Check system clock synchronization

**Solutions:**
- Implement automatic token refresh
- Add token expiration buffer (refresh 5 min before expiry)
- Cache tokens with expiration tracking
- Synchronize system time with NTP

**Token Manager Example:**
```python
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.token = None
        self.expiry = None
    
    def is_expired(self):
        if not self.expiry:
            return True
        # Refresh 5 minutes before actual expiry
        buffer = timedelta(minutes=5)
        return datetime.now() >= (self.expiry - buffer)
    
    def get_token(self):
        if self.is_expired():
            self.refresh_token()
        return self.token
```

### Wrong Platform Configuration

**Symptoms:**
- Connection test fails
- "Host not found" errors
- Incorrect URL format errors

**Diagnosis:**
1. Verify `WATSONX_PLATFORM` environment variable
2. Check service URL format
3. Confirm region/endpoint is correct

**Solutions:**
- Ask user to confirm platform (IBM Cloud/AWS/On-prem)
- Validate URL format matches platform
- Provide platform detection helper
- Show example URLs for each platform

**Platform Detection:**
```python
def detect_platform_from_url(url):
    """Detect platform from service URL"""
    if 'watson-orchestrate.ibm.com' in url:
        if 'api.' in url:
            return 'ibm_cloud'
        elif '.dl.' in url:
            return 'aws'
    return 'unknown'
```

## Connection Issues

### Network Timeout

**Symptoms:**
- Connection timeout errors
- No response from server
- Hanging requests

**Diagnosis:**
1. Check network connectivity
2. Verify firewall rules
3. Test DNS resolution
4. Check proxy settings

**Solutions:**
- Implement connection timeout (30 seconds)
- Add retry logic with exponential backoff
- Check corporate firewall/proxy
- Verify VPN connection if required

**Connectivity Test:**
```python
import socket

def test_connectivity(host, port=443, timeout=10):
    """Test if host is reachable"""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as e:
        print(f"Connection failed: {e}")
        return False
```

**Retry with Backoff:**
```python
def retry_with_backoff(func, max_retries=3):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
            time.sleep(wait_time)
```

### SSL Certificate Error

**Symptoms:**
- SSL certificate verification failed
- Certificate errors
- HTTPS connection issues

**Diagnosis:**
1. Check system time is correct
2. Verify SSL certificates are up to date
3. Check for corporate SSL inspection

**Solutions:**
- Update system SSL certificates
- Synchronize system time
- Configure corporate CA certificates
- For development only: disable SSL verification (not recommended for production)

### Rate Limiting (429 Too Many Requests)

**Symptoms:**
- 429 Too Many Requests error
- "Rate limit exceeded" message
- Requests failing after many successes

**Diagnosis:**
1. Check request frequency
2. Review rate limit headers
3. Identify request patterns

**Solutions:**
- Implement request throttling
- Add exponential backoff on 429 errors
- Cache responses when possible
- Batch requests if supported

**Rate Limiter:**
```python
import time
from functools import wraps

def rate_limit(calls_per_second=10):
    """Rate limiting decorator"""
    min_interval = 1.0 / calls_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limit(calls_per_second=5)
def call_api():
    # Your API call here
    pass
```

## Agent Issues

### Agent Not Found (404)

**Symptoms:**
- 404 Not Found error
- "Agent does not exist" message
- Empty response when fetching agent

**Diagnosis:**
1. Verify agent ID is correct
2. Check if agent is deployed
3. Confirm instance ID matches
4. Verify user has access to agent

**Solutions:**
- List all available agents to find correct ID
- Verify agent deployment status
- Check user permissions
- Confirm instance ID in `.env` file

### Agent Response Error

**Symptoms:**
- Agent returns error response
- Unexpected response format
- Missing expected fields

**Diagnosis:**
1. Check request payload format
2. Verify required parameters
3. Review agent configuration
4. Check skill availability

**Solutions:**
- Validate request payload against API schema
- Include all required parameters
- Test agent in watsonx Orchestrate UI first
- Check agent logs for errors

## Code Issues

### Environment Variables Not Loaded

**Symptoms:**
- "Environment variable not found" errors
- None values for credentials
- KeyError for env variables

**Diagnosis:**
1. Check if `.env` file exists
2. Verify `.env` file location
3. Confirm variable names match
4. Check if dotenv is loaded

**Solutions:**
- Ensure `.env` file is in project root
- Use python-dotenv or similar library
- Verify variable names (case-sensitive)
- Check `.env` file format (no quotes needed)

**Proper Loading:**
```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Validate required variables
required_vars = ['WATSONX_API_KEY', 'WATSONX_INSTANCE_ID']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {missing_vars}")
```

### JSON Parsing Error

**Symptoms:**
- JSON decode errors
- "Expecting value" errors
- Invalid JSON response

**Diagnosis:**
1. Check response content type
2. Verify response is not empty
3. Check for HTML error pages
4. Review response status code

**Solutions:**
- Check response status before parsing
- Handle empty responses
- Log raw response for debugging
- Validate content-type header

**Safe Parsing:**
```python
import json

def safe_json_parse(response_data):
    """Safely parse JSON response"""
    try:
        if not response_data:
            return None
        return json.loads(response_data)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        print(f"Raw response: {response_data[:200]}")
        return None
```

## Error Code Reference

| Code | Meaning | Common Causes | Solution |
|------|---------|---------------|----------|
| 400 | Bad Request | Wrong endpoint, invalid payload | Check URL and payload format |
| 401 | Unauthorized | Invalid/expired token | Regenerate token |
| 403 | Forbidden | Insufficient permissions | Check user permissions |
| 404 | Not Found | Wrong agent ID or endpoint | Verify IDs and URLs |
| 422 | Unprocessable Entity | Invalid message format | Use `{"role": "user", "content": "text"}` |
| 429 | Too Many Requests | Rate limit exceeded | Implement throttling |
| 500 | Internal Server Error | Server-side issue | Retry with backoff |
| 503 | Service Unavailable | Service down | Check service status, retry later |

## Debugging Workflow

<Steps>
<Step>
**Enable detailed logging**

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```
</Step>

<Step>
**Test authentication independently**

```python
token = generate_token(api_key)
print(f"Token: {token[:20]}...")
print(f"Token length: {len(token)}")
```
</Step>

<Step>
**Test API connectivity**

```python
skills = list_skills(host, instance_id, token)
print(f"Found {len(skills)} skills")
```
</Step>

<Step>
**Test agent invocation**

```python
result = invoke_agent(host, instance_id, token, agent_id, "Test")
print(f"Run ID: {result['run_id']}")
```
</Step>

<Step>
**Test response retrieval**

```python
run_details = get_run_details(host, instance_id, token, run_id)
print(f"Status: {run_details['status']}")
print(f"Response: {extract_response(run_details)}")
```
</Step>
</Steps>

## Getting Additional Help

If issues persist after troubleshooting:

1. **Check Official API Documentation:**
   https://developer.ibm.com/apis/catalog/watsonorchestrate--custom-assistants/Introduction

2. **Review Critical Patterns:**
   See `critical-patterns.md` for the 5 most common failures

3. **Verify API Reference:**
   See `api-reference.md` for correct endpoints and formats

4. **Check Code Examples:**
   See `code-examples.md` for complete working implementations

5. **Enable Debug Logging:**
   Add detailed logging to identify exact failure point

6. **Test with curl:**
   Isolate whether issue is in code or API
   ```bash
   curl -X POST "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token" \
     -H "Content-Type: application/json" \
     -d '{"apikey": "your_key"}'