# Getting Started with Agent Integration

## Initial Assessment

<Steps>
<Step>
**Determine if agent exists**

- Do you already have a watsonx Orchestrate agent deployed?
- If not, you'll need to create one first using the agent-builder skill
- If yes, proceed with integration setup
</Step>

<Step>
**Collect the Service Instance URL — MANDATORY, no exceptions**

> ⛔ **Do NOT ask the user "what platform are you on?" and proceed from their answer.**
> Even if the user says "I'm on IBM Cloud" or "I'm on AWS", the service URL is still required.
> The URL is the ONLY reliable source for hostname, instance ID, and token endpoint.
> Guessing from a user's description leads to 401 errors. Always collect the URL first.

Ask the user:

> "Please paste your **Service instance URL** from:
> WXO UI → Profile icon (top-right) → **Settings** → **API details** tab → **Service instance URL**"

Example URLs by platform:

| Platform | Example service URL |
|----------|-------------------|
| IBM Cloud | `https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<id>` |
| AWS | `https://api.dl.watson-orchestrate.ibm.com/instances/<id>` |
| On-premises | `https://<custom-host>/orchestrate/<instance>/instances/<id>` |

⚠️ **Never use the URL from the IBM Cloud resources page** (`cloud.ibm.com/resources`).
That URL is for resource management only and does not work for API calls.

From the service URL we automatically derive — no guessing needed:
- ✅ Platform (IBM Cloud / AWS / On-premises)
- ✅ API host for all calls
- ✅ Instance ID
- ✅ Correct token endpoint

Use this helper to derive all config from the URL:

```python
from urllib.parse import urlparse

def detect_from_service_url(service_url: str) -> dict:
    """Derive platform, host, instance ID and token endpoint from service URL."""
    parsed = urlparse(service_url)
    host = parsed.netloc
    parts = [p for p in parsed.path.split("/") if p]
    try:
        instance_id = parts[parts.index("instances") + 1]
    except (ValueError, IndexError):
        raise ValueError(f"Cannot find instance ID in URL: {service_url}")

    if "watson-orchestrate.cloud.ibm.com" in host:
        platform = "ibm_cloud"
        token_endpoint = "https://iam.cloud.ibm.com/identity/token"
        token_field = "access_token"
    elif "dl.watson-orchestrate.ibm.com" in host:
        platform = "aws"
        # MCSP V2 is the active standard for all current AWS regions.
        # V1 (iam.platform.saas.ibm.com) is legacy — only for unmigrated tenants.
        token_endpoint = "https://account-iam.platform.saas.ibm.com/api/2.0/apikeys/token"
        token_field = "token"
    else:
        platform = "onprem"
        token_endpoint = None  # ask user for their CPD IAM URL
        token_field = "token"

    return {
        "host": host,
        "instance_id": instance_id,
        "platform": platform,
        "token_endpoint": token_endpoint,
        "token_field": token_field,
    }
```

**Confirm derived config back to the user before writing any code:**

```
Platform:       ibm_cloud
API Host:       api.us-south.watson-orchestrate.cloud.ibm.com
Instance ID:    da173ff0-e252-4c16-b0db-6d426bdb297f
Token endpoint: https://iam.cloud.ibm.com/identity/token

Does this look correct? (yes / no)
```

Only proceed once the user confirms.
</Step>

<Step>
**Collect API key and Agent ID**

Once the platform is confirmed from the service URL:

- **API key** — from WXO Settings → API details → **Generate API key**
  - On IBM Cloud this redirects to `cloud.ibm.com/iam/apikeys` — this is expected and correct
  - The key produced there must be used with `iam.cloud.ibm.com` (not `iam.platform.saas.ibm.com`)
- **Agent ID** — UUID of the agent to invoke (from WXO UI → Agents, or `orchestrate agents list`)
</Step>
</Steps>

## Credential Setup

### Environment File Templates

**IBM Cloud:**
```env
WXO_API_KEY=your_ibm_cloud_api_key_here
WXO_SERVICE_URL=https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/<instance_id>
WXO_AGENT_ID=your_agent_id_here
```

**AWS:**
```env
WXO_API_KEY=your_aws_api_key_here
WXO_SERVICE_URL=https://api.dl.watson-orchestrate.ibm.com/instances/<instance_id>
WXO_AGENT_ID=your_agent_id_here
```

**On-Premises:**
```env
WXO_USERNAME=your_username_here
WXO_API_KEY=your_api_key_here
WXO_SERVICE_URL=https://<custom-host>/orchestrate/<instance>/instances/<instance_id>
WXO_AGENT_ID=your_agent_id_here
```

> Note: `WXO_SERVICE_URL` replaces the older `WXO_INSTANCE_ID` + `WXO_REGION` pattern.
> Host and instance ID are always derived from the service URL — never hardcode them separately.

### Setup Workflow

<Steps>
<Step>
Create `.env` file in project root
</Step>

<Step>
Add credentials using appropriate template above
</Step>

<Step>
Add `.env` to `.gitignore` to prevent credential exposure
</Step>

<Step>
Verify all required variables are set
</Step>
</Steps>

## Connection Testing

**CRITICAL:** Always test connection before generating integration code.

<Steps>
<Step>
Generate platform-specific test script (Python or shell)
</Step>

<Step>
Run connection test to verify:
- Token generation works
- API connectivity is successful
- Credentials are valid
</Step>

<Step>
If test fails, diagnose:
- Wrong credentials (see `troubleshooting.md` → WXO-PROXY-10080E)
- Wrong platform detected from URL
- Network / SSL issues (see `troubleshooting.md` → TLS Handshake Failure)
- Firewall/proxy blocking
</Step>
</Steps>

## What Integration Type Do You Need?

Choose your integration approach:

- **Python script for API testing** - Quick testing and prototyping
- **Node.js/Express backend server** - Production API server
- **Full-stack web application** - Complete chat interface
- **React/Vue frontend with backend** - Modern web app
- **Integration library/module** - Reusable code library

See `integration-workflows.md` for detailed workflows for each type.

## Quick Start Checklist

- [ ] Agent deployed and accessible
- [ ] Service instance URL obtained from WXO Settings → API details
- [ ] Platform confirmed from service URL (IBM Cloud / AWS / On-premises)
- [ ] API key generated from WXO Settings → API details (not IBM Cloud resources page)
- [ ] Agent ID obtained
- [ ] `.env` file created with `WXO_SERVICE_URL`, `WXO_API_KEY`, `WXO_AGENT_ID`
- [ ] `.env` added to `.gitignore`
- [ ] Connection test passed
- [ ] Integration type selected

## Next Steps

Once setup is complete:
1. Review `critical-patterns.md` for essential implementation patterns
2. Follow workflows in `integration-workflows.md` for your chosen integration type
3. Reference `troubleshooting.md` if issues arise
