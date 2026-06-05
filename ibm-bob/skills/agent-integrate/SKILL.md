---
name: agent-integrate
description: Integrate watsonx Orchestrate agents into applications using REST APIs. MANDATORY - Review integration guide and critical patterns before generating any code to ensure correct endpoints, authentication, and message formats.
---

# Agent Integration Skill

## 🛑 MANDATORY FIRST STEPS

**Before generating ANY integration code, you MUST:**

1. **Review the integration guide** (critical-patterns.md and api-reference.md)
   - Correct API endpoints (v1, not v2)
   - Proper authentication flow
   - Message format requirements
   - Async processing patterns

2. **Verify these critical patterns:**
   - ✅ Using v1 orchestrate endpoints
   - ✅ Auth endpoint: iam.platform.saas.ibm.com
   - ✅ Message format: `{"role": "user", "content": "text"}`
   - ✅ Polling for run status after invocation
   - ✅ Correct response extraction path

**Why this cannot be skipped:**
- Wrong endpoints cause 404 errors
- Incorrect message format causes failures
- Missing polling means no responses
- These are the most common integration failures

**This applies even if user says "just generate the code" or "keep it simple"**

## What this skill does

Provides comprehensive guidance for integrating watsonx Orchestrate agents into applications via REST APIs. Covers the complete integration lifecycle including authentication, API usage, error handling, and deployment across multiple platforms (IBM Cloud, AWS, On-premises).

## When to use it

Use this skill when you need to:
- Integrate watsonx Orchestrate agents into web or mobile applications
- Generate REST API integration code (Python, Node.js, etc.)
- Set up authentication and credentials for different platforms
- Test API connectivity and troubleshoot integration issues
- Build full-stack applications with watsonx Orchestrate backends
- Migrate integrations between platforms
- Debug common integration failures

## How to work with this skill

<Steps>
<Step>
Start with `getting-started.md` to assess requirements and set up credentials for your platform (IBM Cloud, AWS, or On-premises).
</Step>
<Step>
Review `critical-patterns.md` to understand the 5 most common integration failures and how to avoid them.
</Step>
<Step>
Use `api-reference.md` for correct API endpoints, authentication patterns, and URL structures for your platform.
</Step>
<Step>
Follow `integration-workflows.md` for step-by-step implementation guidance based on your integration type.
</Step>
<Step>
Reference `code-examples.md` and the `resources/` folder for ready-to-use code in Python and Node.js.
</Step>
<Step>
Use `troubleshooting.md` when encountering errors or unexpected behavior.
</Step>
</Steps>

## Supporting files

### Core Workflows
- `getting-started.md` - Initial assessment, credential setup, platform detection, connection testing
- `integration-workflows.md` - Step-by-step workflows for different integration types (Python, Node.js, web apps)
- `critical-patterns.md` - The 5 critical integration issues from real-world debugging (message format, async processing, response extraction, hostname, polling)

### Reference Materials
- `api-reference.md` - Correct API endpoints, authentication methods, URL structures for all platforms
- `troubleshooting.md` - Common errors, debugging workflow, error code reference
- `code-examples.md` - Overview of code examples and usage patterns

### Code Resources
- `resources/` - Ready-to-use integration code
  - `watsonx_client.py` - Complete Python client library with multi-platform support
  - `chat_cli.py` - Interactive CLI chat application
  - `test_connection.py` - Connection test script
  - `server.js` - Node.js Express REST API server
  - `package.json` - Node.js dependencies
  - `README.md` - Setup and usage instructions

## Platform support

This skill covers integration patterns for all watsonx Orchestrate deployment types:

- **IBM Cloud** - IAM token authentication, `api.{region}.watson-orchestrate.cloud.ibm.com` endpoints
- **AWS** - JWT token authentication, `{region}.dl.watson-orchestrate.ibm.com` endpoints
- **On-premises** - JWT token authentication, custom domain endpoints

All code examples automatically detect the platform and use the correct authentication method.

## Critical integration patterns

The skill emphasizes 5 critical patterns that cause most integration failures:

1. **Message Format** - Message must be object with `role` and `content`, not a string
2. **Async Processing** - Agent runs are asynchronous; must poll for completion
3. **Response Extraction** - Navigate nested JSON structure correctly
4. **Hostname Usage** - Use correct host from service URL, don't construct different endpoints
5. **Polling Strategy** - Implement proper polling with timeouts and error handling

See `critical-patterns.md` for detailed explanations and solutions.

## Source mode details

- **Original mode:** 🔗 Agent-Integrate
- **Mode slug:** agent-integrate
- **Tool permissions:** read, edit, command, browser
- **Focus areas:** REST API integration, authentication, error handling, multi-platform support

## Additional notes

This skill is designed for developers integrating watsonx Orchestrate into applications. It assumes basic familiarity with REST APIs and either Python or Node.js.

For building native agents within watsonx Orchestrate (not integrating them), use the `agent-builder` skill instead.

All code examples in the `resources/` folder are production-ready and include:
- Multi-platform support with automatic detection
- Proper error handling
- Token management
- Complete API coverage
- Interactive testing tools