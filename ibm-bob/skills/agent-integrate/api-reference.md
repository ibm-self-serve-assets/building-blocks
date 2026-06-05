# API Endpoint & Authentication Reference

⚠️ **READ THIS BEFORE GENERATING ANY CODE** ⚠️

The most common mistake is assuming API patterns without checking documentation. This leads to using wrong API versions, incorrect authentication endpoints, and unnecessary API key parsing.

**ALWAYS reference this guide FIRST.**

## Correct Endpoint Patterns

### Authentication (All Platforms)

**Endpoint:** `https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "apikey": "your_base64_encoded_api_key"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 7200
}
```

**Key Points:**
- Same endpoint for AWS, IBM Cloud, and On-premises
- Returns JWT token valid for 2 hours
- Use token in Authorization header for API calls
- API key is used AS-IS (no decoding or parsing)

### Agent Invocation (Create Run)

**Endpoint:** `https://{host}/instances/{instance_id}/v1/orchestrate/runs`

**Method:** POST

**Headers:**
```
Authorization: Bearer {jwt_token}
Content-Type: application/json
```

**Payload:**
```json
{
  "agent_id": "your_agent_id",
  "message": {
    "role": "user",
    "content": "Your message here"
  }
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "thread_id": "uuid",
  "task_id": "uuid",
  "message_id": "uuid"
}
```

**Key Points:**
- Returns immediately with run metadata
- Actual response requires polling run status
- Host: `api.dl.watson-orchestrate.ibm.com` (for AWS/IBM Cloud)

### Get Run Status and Response

**Endpoint:** `https://{host}/instances/{instance_id}/v1/orchestrate/runs/{run_id}`

**Method:** GET

**Headers:**
```
Authorization: Bearer {jwt_token}
```

**Response:**
```json
{
  "id": "run_id",
  "status": "completed",
  "result": {
    "data": {
      "message": {
        "content": [
          {
            "text": "Agent's response here"
          }
        ]
      }
    }
  }
}
```

**Key Points:**
- Poll this endpoint after agent invocation
- Wait until status is "completed"
- Extract response from `result.data.message.content[0].text`

## URL Structure Breakdown

### Authentication URL
```
https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token
       └─────────┬─────────┘ └────┬────┘ └──────┬──────┘
           Global IBM IAM      Service    API Path
```

**Notes:**
- Global IBM IAM service
- Not instance-specific
- Same for all platforms

### API Operation URL
```
https://api.dl.watson-orchestrate.ibm.com/instances/{instance_id}/v1/orchestrate/runs
       └──────────┬──────────┘ └────────┬────────┘ └┬┘ └────┬────┘ └─┬─┘
              Hostname          Instance Prefix    Ver Service  Resource
```

**Notes:**
- Instance-specific operations
- Always includes `/instances/{id}` prefix
- Uses v1 API version
- Host is same for AWS and IBM Cloud

## Common Endpoint Failures

### ❌ Failure #1: Using v2 Endpoints (They Don't Exist)

**Wrong:**
```python
auth_url = f"{service_url}/v2/api_keys/token"
run_url = f"{service_url}/v2/agents/{agent_id}/runs"
```

**Error:** 400 Bad Request - Endpoints not found

**Correct:**
```python
auth_url = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
run_url = f"https://{host}/instances/{instance_id}/v1/orchestrate/runs"
```

### ❌ Failure #2: Wrong Authentication Endpoint

**Wrong:**
```python
# Auth endpoint is NOT instance-specific
auth_url = f"{service_url}/v2/api_keys/token"
auth_url = f"https://{host}/instances/{instance_id}/api_keys/token"
```

**Error:** 400 Bad Request

**Correct:**
```python
# Global IBM IAM endpoint - ALWAYS the same
auth_url = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
```

### ❌ Failure #3: API Key Parsing

**Wrong:**
```python
# Don't decode or parse the API key
decoded_key = base64.b64decode(api_key).decode('utf-8')
username, apikey, client_id = decoded_key.split(':')
payload = {"username": username, "api_key": apikey, "client_id": client_id}
```

**Error:** "Invalid API key format" or authentication failure

**Correct:**
```python
# Use API key as-is
payload = {"apikey": api_key}
```

## Implementation Checklist

Before writing ANY integration code:

1. ✓ Have you read the "Complete Working Flow" section?
2. ✓ Are you using the correct authentication endpoint?
   - Correct: `iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token`
   - Wrong: Any endpoint containing your instance URL or `/v2/`
3. ✓ Are you using v1 orchestrate endpoints?
   - Correct: `/v1/orchestrate/runs`
   - Wrong: `/v2/agents/{id}/runs` or `/api/v2/`
4. ✓ Are you using the API key as-is?
   - Correct: `{"apikey": api_key}`
   - Wrong: Decoding, parsing, or splitting the API key
5. ✓ Does your URL include `/instances/{instance_id}`?
   - Correct: `https://{host}/instances/{id}/v1/orchestrate/runs`
   - Wrong: `https://{host}/v1/orchestrate/runs` (missing instance prefix)
6. ✓ Are you using the correct hostname?
   - Correct: `api.dl.watson-orchestrate.ibm.com`
   - Wrong: `us-east-1.dl.watson-orchestrate.ibm.com` (region prefix)

## Platform-Specific Hostnames

| Platform | Hostname |
|----------|----------|
| AWS | `api.dl.watson-orchestrate.ibm.com` |
| IBM Cloud | `api.dl.watson-orchestrate.ibm.com` |
| On-Premises | Custom hostname from deployment |

**Important:** No region prefix for AWS/IBM Cloud!

## Quick Reference Card

### Authentication
```
Endpoint: https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token
Payload:  {"apikey": "your_key"}
Returns:  {"token": "jwt", "expires_in": 7200}
```

### Agent Invocation
```
Endpoint: https://api.dl.watson-orchestrate.ibm.com/instances/{id}/v1/orchestrate/runs
Payload:  {"agent_id": "id", "message": {"role": "user", "content": "text"}}
Returns:  {"run_id": "uuid", "thread_id": "uuid"}
```

### Run Status
```
Endpoint: https://api.dl.watson-orchestrate.ibm.com/instances/{id}/v1/orchestrate/runs/{run_id}
Returns:  {"status": "completed", "result": {"data": {"message": {"content": [{"text": "response"}]}}}}
```

## Key Rules

✅ **DO:**
- Use v1, not v2
- Use IBM IAM for auth, not instance URL
- Use API key as-is, no parsing
- Include `/instances/{id}` prefix
- Reference this guide first, assume nothing

❌ **DON'T:**
- Assume v2 API exists
- Use instance URL for authentication
- Decode or parse API keys
- Forget `/instances/{id}` prefix
- Use region-based hostnames for AWS

## Debugging 400/404 Errors

**Symptoms:**
- 400 Bad Request
- "Endpoint not found"
- "Invalid request"

**Likely Causes:**
1. Using v2 endpoints instead of v1
2. Wrong authentication endpoint
3. Missing `/instances/{id}` prefix
4. Incorrect payload format

**Solution:**
Compare your URLs to the examples in this guide. Use exact URLs from "Quick Reference Card" section.

## Additional Resources

**Official API Documentation:**
https://developer.ibm.com/apis/catalog/watsonorchestrate--custom-assistants/Introduction

This resource provides:
- Complete endpoint documentation
- Interactive API testing
- Detailed parameter descriptions
- Request/response examples
- Error code explanations