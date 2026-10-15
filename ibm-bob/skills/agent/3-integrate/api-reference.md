# API Endpoint & Authentication Reference

⚠️ **READ THIS BEFORE GENERATING ANY CODE** ⚠️

The most common mistakes are assuming a single auth endpoint for all platforms and hardcoding the IBM Cloud hostname. Both are wrong and will cause 401 errors.

**ALWAYS derive platform, host, and token endpoint from the service URL first.**
See `getting-started.md` → `detect_from_service_url()`.

---

## Authentication

Token endpoint, request format, and response field **differ by platform**. Always determine platform from the service URL before writing auth code.

### IBM Cloud

**Endpoint:** `https://iam.cloud.ibm.com/identity/token`

**Method:** POST

**Headers:**
```
Content-Type: application/x-www-form-urlencoded
```

**Payload:**
```
grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=<your_api_key>
```

**Response:**
```json
{
  "access_token": "<IAM_ACCESS_TOKEN>",
  "expires_in": 3600
}
```

**Token field:** `access_token`

> ⚠️ The IBM Cloud "Generate API key" button in WXO Settings → API details redirects to
> `cloud.ibm.com/iam/apikeys`. This is **expected and correct** for IBM Cloud instances.
> The key produced there works **only** with `iam.cloud.ibm.com`, NOT with `iam.platform.saas.ibm.com`.

---

### AWS

> ⚠️ **AWS has two MCSP versions.** The correct endpoint depends on whether your tenant has
> migrated to MCSP V2. Use the API key format to identify: keys starting with `k1:usr_` are
> MCSP V2 keys. When in doubt, try V2 first — it is the active standard for all current AWS regions.

#### MCSP V2 (Current — migrated regions: us-east-1, eu-central-1, ap-south-1, ap-southeast-1)

**Endpoint:** `https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "apikey": "<your_api_key>"
}
```

**Response:**
```json
{
  "token": "<JWT_ACCESS_TOKEN>",
  "expires_in": 7200
}
```

**Token field:** `token`

#### MCSP V1 (Legacy — unmigrated regions only)

**Endpoint:** `https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token`

Same payload and response shape as V2. If V2 returns 401 `kid is not found`, the tenant may
still be on V1 — try this endpoint as a fallback.

---

### On-Premises

**Endpoint:** `https://<your-host>/icp4d-api/v1/authorize`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Payload:**
```json
{
  "username": "<your_username>",
  "password": "<your_password>"
}
```

**Response:**
```json
{
  "token": "<CPD_TOKEN>"
}
```

**Token field:** `token`

---

### Platform Auth Summary Table

| Platform | Token endpoint | Body format | Token field |
|----------|---------------|-------------|-------------|
| IBM Cloud | `iam.cloud.ibm.com/identity/token` | `application/x-www-form-urlencoded` with `grant_type` + `apikey` | `access_token` |
| AWS (MCSP V2 — current) | `account-iam.platform.saas.ibm.com/api/2.0/apikeys/token` | `application/json` with `apikey` | `token` |
| AWS (MCSP V1 — legacy) | `iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token` | `application/json` with `apikey` | `token` |
| On-premises | `<host>/icp4d-api/v1/authorize` | `application/json` with `username` + `password` | `token` |

---

## Agent Invocation (Create Run)

**Endpoint:** `https://{host}/instances/{instance_id}/v1/orchestrate/runs`

> `{host}` and `{instance_id}` are **always derived from the service URL** — never hardcoded.
> IBM Cloud example host: `api.us-south.watson-orchestrate.cloud.ibm.com`
> AWS example host: `api.dl.watson-orchestrate.ibm.com`

**Method:** POST

**Headers:**
```
Authorization: Bearer {token}
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
- Returns immediately with run metadata — actual response requires polling
- Message must be an object `{"role": "user", "content": "..."}` — NOT a string

---

## Get Run Status and Response

**Endpoint:** `https://{host}/instances/{instance_id}/v1/orchestrate/runs/{run_id}`

**Method:** GET

**Headers:**
```
Authorization: Bearer {token}
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
- Wait until status is `"completed"`
- Extract response from `result.data.message.content[0].text`

---

## Platform-Specific Hostnames

| Platform | Hostname pattern | Example |
|----------|-----------------|---------|
| IBM Cloud | `api.<region>.watson-orchestrate.cloud.ibm.com` | `api.us-south.watson-orchestrate.cloud.ibm.com` |
| AWS | `api.dl.watson-orchestrate.ibm.com` | (no region prefix) |
| On-premises | Custom hostname from your deployment | `cpd-instance.apps.example.com` |

> **Always derive the host from the service URL.** Never hardcode it.
> IBM Cloud instances are region-specific — hardcoding `api.dl` will cause 401/connection errors.

---

## URL Structure Breakdown

### IBM Cloud API Operation URL
```
https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/{id}/v1/orchestrate/runs
        └────────────────┬────────────────┘ └────────┬────────┘ └┬┘ └─────┬─────┘ └─┬─┘
               Region-specific hostname      Instance prefix    Ver  Service   Resource
```

### AWS API Operation URL
```
https://api.dl.watson-orchestrate.ibm.com/instances/{id}/v1/orchestrate/runs
        └──────────┬──────────┘ └────────┬────────┘ └┬┘ └─────┬─────┘ └─┬─┘
            Fixed hostname        Instance prefix    Ver  Service   Resource
```

**Notes for both:**
- Always includes `/instances/{id}` prefix
- Uses v1 API version (v2 does not exist)

---

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
# IBM Cloud
auth_url = "https://iam.cloud.ibm.com/identity/token"
# AWS
auth_url = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
run_url = f"https://{host}/instances/{instance_id}/v1/orchestrate/runs"
```

### ❌ Failure #2: Hardcoding the Wrong Auth Endpoint

**Wrong:**
```python
# Using iam.platform.saas for an IBM Cloud IAM key
auth_url = "https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token"
```

**Error:** 401 — `"kid is not found in the customer's token"` or `"ApiKey is not valid"`

**Correct:**
```python
# Derive from service URL — see detect_from_service_url() in getting-started.md
config = detect_from_service_url(service_url)
auth_url = config["token_endpoint"]
```

### ❌ Failure #3: API Key Parsing

**Wrong:**
```python
# Don't decode or parse the API key
decoded_key = base64.b64decode(api_key).decode('utf-8')
username, apikey, client_id = decoded_key.split(':')
```

**Correct:**
```python
# Use API key as-is
payload = {"apikey": api_key}   # AWS
# or
payload = f"grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey={api_key}"  # IBM Cloud
```

### ❌ Failure #4: Hardcoding IBM Cloud Host as AWS Host

**Wrong:**
```python
# ❌ AWS host used for IBM Cloud instance
host = "api.dl.watson-orchestrate.ibm.com"
```

**Error:** 401 — token `kid` mismatch or connection error

**Correct:**
```python
# ✅ Always derive from service URL
config = detect_from_service_url(service_url)
host = config["host"]   # e.g. api.us-south.watson-orchestrate.cloud.ibm.com
```

---

## Implementation Checklist

Before writing ANY integration code:

1. ✓ Do you have the service URL from WXO Settings → API details?
2. ✓ Have you run `detect_from_service_url()` and confirmed platform + host?
3. ✓ Are you using the correct token endpoint for your platform?
   - IBM Cloud: `iam.cloud.ibm.com/identity/token`
   - AWS: `iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token`
4. ✓ Is host derived from the service URL (not hardcoded)?
5. ✓ Are you using v1 orchestrate endpoints?
   - Correct: `/v1/orchestrate/runs`
   - Wrong: `/v2/agents/{id}/runs`
6. ✓ Is the message formatted as `{"role": "user", "content": "text"}`?
7. ✓ Does path include `/instances/{instance_id}`?

---

## Quick Reference Card

### IBM Cloud Authentication
```
Endpoint: POST https://iam.cloud.ibm.com/identity/token
Headers:  Content-Type: application/x-www-form-urlencoded
Payload:  grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=<key>
Returns:  {"access_token": "...", "expires_in": 3600}
```

### AWS Authentication
```
Endpoint: POST https://iam.platform.saas.ibm.com/siusermgr/api/1.0/apikeys/token
Headers:  Content-Type: application/json
Payload:  {"apikey": "<key>"}
Returns:  {"token": "...", "expires_in": 7200}
```

### Agent Invocation (both platforms)
```
Endpoint: POST https://{host}/instances/{id}/v1/orchestrate/runs
Payload:  {"agent_id": "id", "message": {"role": "user", "content": "text"}}
Returns:  {"run_id": "uuid", "thread_id": "uuid"}
```

### Run Status (both platforms)
```
Endpoint: GET https://{host}/instances/{id}/v1/orchestrate/runs/{run_id}
Returns:  {"status": "completed", "result": {"data": {"message": {"content": [{"text": "response"}]}}}}
```

---

## Key Rules

✅ **DO:**
- Derive host and instance ID from `WXO_SERVICE_URL`
- Use platform-specific token endpoint (IBM Cloud ≠ AWS)
- Use v1, not v2
- Use API key as-is, no parsing
- Include `/instances/{id}` prefix

❌ **DON'T:**
- Hardcode `api.dl.watson-orchestrate.ibm.com` for IBM Cloud instances
- Use `iam.platform.saas.ibm.com` with an IBM Cloud IAM key
- Use `iam.cloud.ibm.com` with a WXO MCSP (AWS) key
- Assume v2 API exists
- Use the IBM Cloud resources page URL as the service URL

---

## Additional Resources

**Official API Documentation:**
https://developer.watson-orchestrate.ibm.com/apis
