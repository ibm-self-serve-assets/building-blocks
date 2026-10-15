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
  "run_id": "uuid",
  "thread_id": "uuid",
  "task_id": "uuid",
  "message_id": "uuid"
}
```
⚠️ **NO AGENT RESPONSE TEXT HERE!**

⚠️ **The run identifier field is `run_id` — NOT `id`.** This is the most common key-name mistake:

```python
# ❌ Wrong — "id" does not exist in the POST response, returns None
run_id = response.json().get("id")

# ✅ Correct
run_id = response.json()["run_id"]
```

A `None` run_id causes an immediate error before polling even starts.

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

### Issue #4: Hostname Configuration

**Problem:** Hardcoding a hostname instead of deriving it from the service URL causes
connection errors or 401s because IBM Cloud and AWS use different hostnames.

**Error (AWS — region prefix):** `[Errno 8] nodename nor servname provided`

**Error (IBM Cloud — wrong host):** `401 — kid is not found in the customer's token`

**Wrong:**
```python
# ❌ Region prefix never works for AWS
host = f"{region}.dl.watson-orchestrate.ibm.com"

# ❌ AWS host used for an IBM Cloud instance
host = "api.dl.watson-orchestrate.ibm.com"
```

**Correct:**
```python
# ✅ Always derive host from service URL
from urllib.parse import urlparse
host = urlparse(service_url).netloc
# IBM Cloud example: api.us-south.watson-orchestrate.cloud.ibm.com
# AWS example:       api.dl.watson-orchestrate.ibm.com
```

**Platform-Specific Hostnames:**
- **AWS:** `api.dl.watson-orchestrate.ibm.com` (fixed, no region prefix)
- **IBM Cloud:** `api.<region>.watson-orchestrate.cloud.ibm.com` (region-specific — derive from service URL)
- **On-Premises:** Custom hostname from your deployment

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
    url = f"https://{host}/instances/{instance_id}/v1/orchestrate/runs/{run_id}"
    headers = {"Authorization": f"Bearer {token}"}
    wait_time = 0.5
    max_wait_time = 8
    start_time = time.time()  # initialise before the loop

    while time.time() - start_time < max_wait:
        response = requests.get(url, headers=headers)
        run_details = response.json()
        status = run_details.get('status')

        if status == 'completed':
            return run_details
        elif status in ('failed', 'cancelled'):
            raise RuntimeError(f"Run {status}: {run_details.get('last_error')}")

        time.sleep(wait_time)
        wait_time = min(wait_time * 2, max_wait_time)

    raise TimeoutError(f"Run did not complete within {max_wait} seconds")
```

### Issue #6: Token/Key Type Mismatch (WXO-PROXY-10080E)

**Problem:** Using an IBM Cloud IAM key with the AWS/MCSP token endpoint, or vice versa.
The WXO proxy validates token signatures using platform-specific public keys (`kid`).
If the key type doesn't match the endpoint, the proxy cannot find the public key to verify the token.

**Errors:**
- `401 — "kid is not found in the customer's token"` — IBM Cloud IAM token sent to wrong proxy
- `400/401 — "ApiKey is not valid"` — IBM Cloud IAM key sent to `iam.platform.saas.ibm.com`

**How to identify your key type:**

```bash
# Test IBM Cloud IAM endpoint
curl -s -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=YOUR_KEY" \
  | python3 -m json.tool
# → "access_token" present: IBM Cloud IAM key → use ibm_cloud platform

# Test AWS/MCSP endpoint
curl -s -X POST "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token" \
  -H "Content-Type: application/json" \
  -d '{"apikey": "YOUR_KEY"}' \
  | python3 -m json.tool
# → "token" present: WXO MCSP key → use aws platform
```

**Root cause for IBM Cloud users:**

> The WXO Settings → API details → **"Generate API key"** button on IBM Cloud redirects
> to `cloud.ibm.com/iam/apikeys`. This is **correct and expected**.
> The key produced there is an IBM Cloud IAM key and **must** be exchanged at
> `iam.cloud.ibm.com/identity/token`, NOT at `iam.platform.saas.ibm.com`.

**Fix:**

Always derive the token endpoint from the service URL — never hardcode it:

```python
from urllib.parse import urlparse

def get_token_endpoint(service_url: str) -> tuple[str, str]:
    """Return (token_endpoint, platform) derived from service URL."""
    host = urlparse(service_url).netloc
    if "watson-orchestrate.cloud.ibm.com" in host:
        return "https://iam.cloud.ibm.com/identity/token", "ibm_cloud"
    elif "dl.watson-orchestrate.ibm.com" in host:
        # Use MCSP V2 — active standard for all current AWS regions
        return "https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token", "aws"
    return None, "onprem"
```

---

### Issue #7: AWS MCSP V1 vs V2 Migration (WXO-PROXY-10080E on AWS)

**Problem:** AWS tenants that migrated to MCSP V2 reject tokens minted by the MCSP V1 endpoint.
The WXO proxy's JWKS trust store only holds V2 public keys — a V1 token's `kid` is not found.

**Error:** `401 — "kid is not found in the customer's token"` (same error code as Issue #6
but caused by a different root: V1 key used against a V2-migrated AWS tenant, not a platform mismatch)

**MCSP V1 vs V2 comparison:**

| | MCSP V1 (Legacy) | MCSP V2 (Current) |
|---|---|---|
| Host | `iam.platform.saas.ibm.com` | `account-iam.platform.saas.ibm.com` |
| Path | `/siusermgr/api/1.0/apikeys/token` | `/api/2.0/apikeys/token` |
| Regions | Unmigrated only | `us-east-1`, `eu-central-1`, `ap-south-1`, `ap-southeast-1` |
| Payload | `{"apikey": "..."}` | `{"apikey": "..."}` (same) |
| Token field | `token` | `token` (same) |

**How to identify MCSP V2 keys:** They start with `k1:usr_...`

**Wrong (V1 — will fail on migrated AWS tenants):**
```python
# ❌ MCSP V1 — legacy, rejected by migrated AWS instances
token_url = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
```

**Correct (V2 — use for all current AWS regions):**
```python
# ✅ MCSP V2 — active standard for all current AWS regions
token_url = "https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token"
payload   = {"apikey": api_key}   # same payload as V1
# response["token"] is the bearer token
```

**Full AWS token function:**
```python
import json, http.client, ssl

def get_aws_token(api_key: str) -> str:
    """Get AWS MCSP V2 token. Falls back to V1 if V2 rejects the key."""
    ctx = ssl.create_default_context()
    for host, path in [
        ("account-iam.platform.saas.ibm.com", "/api/2.0/apikeys/token"),   # V2 first
        ("iam.platform.saas.ibm.com", "/siusermgr/api/1.0/apikeys/token"), # V1 fallback
    ]:
        conn = http.client.HTTPSConnection(host, context=ctx)
        conn.request("POST", path, json.dumps({"apikey": api_key}),
                     {"Content-Type": "application/json"})
        res  = conn.getresponse()
        data = json.loads(res.read())
        conn.close()
        if res.status == 200:
            return data["token"]
    raise RuntimeError("AWS token generation failed on both MCSP V2 and V1 endpoints")
```

---

## Quick Diagnostic Checklist

When integration fails, check these in order:

1. ✓ Is message formatted as `{"role": "user", "content": "text"}`?
2. ✓ Are you reading `run_id` (not `id`) from the POST response?
3. ✓ Are you polling GET /v1/orchestrate/runs/{run_id} after POST?
4. ✓ Are you extracting from `result.data.message.content[0].text`?
5. ✓ Is hostname derived from `WXO_SERVICE_URL` (not hardcoded)?
6. ✓ Is the token endpoint correct for your platform (IBM Cloud ≠ AWS)?
7. ✓ Does path include `/instances/{instance_id}`?
8. ✓ Is token still valid (not expired)?
9. ✓ Is agent ID correct and accessible?

## Complete Working Flow

```python
from urllib.parse import urlparse

# 0. Derive config from service URL
service_url = "https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<id>"
parsed      = urlparse(service_url)
host        = parsed.netloc
instance_id = parsed.path.split("/instances/")[1].split("/")[0]
# IBM Cloud → iam.cloud.ibm.com ; AWS → iam.platform.saas.ibm.com
token_endpoint, platform = get_token_endpoint(service_url)

# 1. Generate token (platform-specific)
token = generate_token(api_key, token_endpoint, platform)

# 2. Invoke agent with CORRECT message format
payload = {
    "agent_id": "your-agent-id",
    "message": {
        "role": "user",
        "content": "Your question here"
    }
}
response = requests.post(
    f"https://{host}/instances/{instance_id}/v1/orchestrate/runs",
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