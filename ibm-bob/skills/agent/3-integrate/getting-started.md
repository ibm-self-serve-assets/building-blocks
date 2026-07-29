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
**Identify deployment platform**

Ask: Where is your watsonx Orchestrate instance deployed?
- IBM Cloud
- AWS
- AWS GovCloud
- On-premises
- "I don't know" (we can help detect it)
</Step>

<Step>
**Check for existing credentials**

Verify you have:
- API key
- Service instance URL or instance ID
- Region (if applicable)
</Step>
</Steps>

## Credential Setup

### Environment File Templates

**IBM Cloud:**
```env
WATSONX_API_KEY=your_ibm_cloud_api_key_here
WATSONX_INSTANCE_ID=your_instance_id_here
WATSONX_REGION=us-south
WATSONX_PLATFORM=ibm_cloud
```

**AWS:**
```env
WATSONX_API_KEY=your_aws_api_key_here
WATSONX_INSTANCE_ID=your_instance_id_here
WATSONX_REGION=us-east-1
WATSONX_PLATFORM=aws
```

**On-Premises:**
```env
WATSONX_USERNAME=your_username_here
WATSONX_API_KEY=your_api_key_here
WATSONX_HOST=your_host_here
WATSONX_PORT=443
WATSONX_NAMESPACE=your_namespace_here
WATSONX_INSTANCE_ID=your_instance_id_here
WATSONX_PLATFORM=onprem
```

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
- Wrong credentials
- Network issues
- Platform mismatch
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
- [ ] Platform identified (IBM Cloud/AWS/On-prem)
- [ ] Credentials obtained (API key, instance ID)
- [ ] `.env` file created with credentials
- [ ] `.env` added to `.gitignore`
- [ ] Connection test passed
- [ ] Integration type selected

## Next Steps

Once setup is complete:
1. Review `critical-patterns.md` for essential implementation patterns
2. Follow workflows in `integration-workflows.md` for your chosen integration type
3. Use `code-examples.md` for complete working code
4. Reference `troubleshooting.md` if issues arise