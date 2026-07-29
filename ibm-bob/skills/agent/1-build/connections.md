# watsonx Orchestrate Connections

A connection is the credential/configuration boundary between Orchestrate and an external system. Connections keep secrets out of tool code, OpenAPI specs, MCP server code, and agent YAML.

Use connections for:

- API credentials for Python tools.
- Authentication for OpenAPI tools.
- Environment variables / secure config for MCP toolkits.
- External knowledge providers such as Milvus, Elasticsearch, or custom search.
- SSO/IDP-mediated access for embedded web chat scenarios.
- AI Gateway provider keys via `key_value` connections.

Do **not** hard-code credentials in generated code, YAML specs, OpenAPI specs, shell scripts, browser code, or example docs.

## Connection object shape

A connection has three parts:

1. `app_id`: unique identifier used when binding a connection to tools/agents/knowledge.
2. Environment config: separate `draft` and `live` auth configuration.
3. Credentials: set separately from YAML by CLI/UI.

Team vs member credentials:

| Type | Meaning | Use when |
|---|---|---|
| `team` | Shared credentials configured by a builder/admin. | Service account, shared API key, backend integration. |
| `member` | Each user supplies their own credentials. | Per-user access, user-specific OAuth, delegated operations. |

Draft vs live:

| Environment | Used by |
|---|---|
| `draft` | Builder testing and Manage Agents preview. |
| `live` | Deployed agents and production user access. |

The same `app_id` can use different auth kinds and credential scopes in `draft` vs `live`.

## Naming rules

Use `snake_case` for `app_id` values.

```text
Good: github_api
Good: workday_sso
Good: vendor_risk_api
Bad:  GitHub API
Bad:  github-api
Bad:  app.id
```

Rules:

- Use lowercase letters, numbers, and underscores.
- Keep IDs stable; tools and agents reference them.
- Prefer system/domain names over implementation names.

## Authentication kinds

Common `kind` values:

```text
basic
bearer
api_key
oauth_auth_code_flow
oauth_auth_implicit_flow
oauth_auth_password_flow
oauth_auth_client_credentials_flow
oauth_auth_on_behalf_of_flow
oauth_auth_token_exchange_flow
key_value
kv
```

Practical guidance:

| Kind | Use when | Runtime behavior |
|---|---|---|
| `basic` | Username/password service access. | Supplies username/password or Basic auth header depending on consumer. |
| `bearer` | Static bearer token. | Supplies token or `Authorization: Bearer ...`. |
| `api_key` | Static API key. | Supplies `api_key`; OpenAPI injects `x-api-key`. |
| OAuth flows | Downstream system needs delegated OAuth access. | Orchestrate resolves `access_token`. |
| `oauth_auth_on_behalf_of_flow` | Embedded web chat needs IDP/SSO delegated access. | Uses upstream IDP token exchange on behalf of the user. |
| `key_value` / `kv` | Secure arbitrary config, MCP env vars, AI Gateway provider config. | Supplies named key/value entries. |

Important limits:

- OAuth connections are mainly for agents used through the watsonx Orchestrate integrated web chat UI.
- For embedded web chat on external websites, use supported upstream SSO/IDP patterns.
- AI Gateway supports only `key_value` connections.
- OpenAPI tools do not support `key_value` connections.
- Local MCP toolkits support `key_value` connections.

## Connection YAML

Minimal connection spec:

```yaml
spec_version: v1
kind: connection
app_id: vendor_risk_api
environments:
  draft:
    kind: api_key
    type: team
    server_url: https://api.vendor-risk.example.com
  live:
    kind: api_key
    type: team
    server_url: https://api.vendor-risk.example.com
```

Knowledge provider connection:

```yaml
spec_version: v1
kind: connection
app_id: external_milvus
resource:
  component: knowledge
  category: milvus
environments:
  draft:
    kind: basic
    type: team
    server_url: https://milvus.example.com
  live:
    kind: basic
    type: team
    server_url: https://milvus.example.com
```

Key-value connection for MCP toolkit or AI Gateway:

```yaml
spec_version: v1
kind: connection
app_id: mcp_runtime_config
environments:
  draft:
    kind: key_value
    type: team
  live:
    kind: key_value
    type: team
```

SSO / IDP on-behalf-of connection shape:

```yaml
spec_version: v1
kind: connection
app_id: workday_sso
environments:
  draft:
    kind: oauth_auth_on_behalf_of_flow
    type: member
    sso: true
    server_url: https://example.workday.com/ccx
    idp_config:
      header:
        content-type: application/x-www-form-urlencoded
      body:
        requested_token_use: on_behalf_of
        requested_token_type: urn:ietf:params:oauth:token-type:saml2
    app_config:
      header:
        content-type: application/x-www-form-urlencoded
  live:
    kind: oauth_auth_on_behalf_of_flow
    type: member
    sso: true
    server_url: https://example.workday.com/ccx
    idp_config:
      header:
        content-type: application/x-www-form-urlencoded
      body:
        requested_token_use: on_behalf_of
        requested_token_type: urn:ietf:params:oauth:token-type:saml2
    app_config:
      header:
        content-type: application/x-www-form-urlencoded
```

## Create/import connections

Import from YAML:

```bash
orchestrate connections import -f connections/vendor_risk_api.yaml
```

Create manually with CLI:

```bash
orchestrate connections add -a vendor_risk_api

orchestrate connections configure \
  -a vendor_risk_api \
  --env draft \
  --kind api_key \
  --type team \
  --server-url https://api.vendor-risk.example.com

orchestrate connections configure \
  -a vendor_risk_api \
  --env live \
  --kind api_key \
  --type team \
  --server-url https://api.vendor-risk.example.com
```

Add optional custom config entries:

```bash
orchestrate connections configure \
  -a vendor_risk_api \
  --env draft \
  --kind api_key \
  --type team \
  --server-url https://api.vendor-risk.example.com \
  -e region=us-south \
  -e tenant_id=acme
```

## Set credentials

Credentials should be set separately from YAML.

Basic:

```bash
orchestrate connections set-credentials \
  -a vendor_portal \
  --env draft \
  -u "$VENDOR_USERNAME" \
  -p "$VENDOR_PASSWORD"
```

Bearer:

```bash
orchestrate connections set-credentials \
  -a vendor_portal \
  --env draft \
  --token "$VENDOR_BEARER_TOKEN"
```

API key:

```bash
orchestrate connections set-credentials \
  -a vendor_risk_api \
  --env draft \
  --api-key "$VENDOR_RISK_API_KEY"
```

Key-value:

```bash
orchestrate connections set-credentials \
  -a mcp_runtime_config \
  --env draft \
  -e GITHUB_TOKEN="$GITHUB_TOKEN" \
  -e DEFAULT_ORG="acme"
```

Production guidance:

- Use environment variables, secret managers, or secure prompts; do not paste real secrets into reusable scripts.
- Configure both `draft` and `live` when the asset will be promoted.
- Rotate credentials outside of code and re-run `set-credentials`.

## Bind connections to tools and toolkits

### OpenAPI tools

OpenAPI tools support one connection per server. Use Python tools when you need multiple credentials or non-standard auth behavior.

```bash
orchestrate tools import \
  -k openapi \
  -f openapi/vendor-api.yaml \
  --app-id vendor_risk_api
```

OpenAPI runtime injection:

```text
basic   -> Authorization: Basic {base64(username:password)}
bearer  -> Authorization: Bearer {token}
api_key -> x-api-key: {api_key}
oauth   -> Authorization: Bearer {access_token}
```

### Python tools

Bind one or more connections:

```bash
orchestrate tools import \
  -k python \
  -f tools/vendor_tools.py \
  -a vendor_risk_api \
  -a procurement_api
```

Remap actual Orchestrate `app_id` to the name expected by tool code:

```bash
orchestrate tools import \
  -k python \
  -f tools/vendor_tools.py \
  -a vendor_api=vendor_risk_api
```

Inside the Python tool, use the ADK runtime connections API.

```python
import requests
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_orchestrate.agent_builder.connections import (
    ConnectionType,
    ExpectedCredentials,
)
from ibm_watsonx_orchestrate.run import connections

@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[
        ExpectedCredentials(
            app_id="vendor_api",
            type=ConnectionType.API_KEY_AUTH,
        )
    ],
)
def get_vendor_status(vendor_id: str) -> dict:
    """Retrieve vendor status from the vendor risk API."""
    conn = connections.api_key_auth("vendor_api")
    response = requests.get(
        f"{conn.url}/vendors/{vendor_id}",
        headers={"Authorization": conn.api_key},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

Local connection emulation for Python tool tests:

```bash
export WXO_SECURITY_SCHEMA_vendor_api=api_key_auth
export WXO_CONNECTION_vendor_api_url=https://api.vendor-risk.example.com
export WXO_CONNECTION_vendor_api_api_key="$VENDOR_RISK_API_KEY"

python tools/vendor_tools.py
```

Other local emulation examples:

```bash
# Basic
export WXO_SECURITY_SCHEMA_foo=basic_auth
export WXO_CONNECTION_foo_url=https://api.example.com
export WXO_CONNECTION_foo_username=username
export WXO_CONNECTION_foo_password=password

# Bearer
export WXO_SECURITY_SCHEMA_foo=bearer_token
export WXO_CONNECTION_foo_url=https://api.example.com
export WXO_CONNECTION_foo_token=token
```

### MCP toolkits

Use `key_value` connections to inject secure runtime configuration into local MCP servers.

```bash
orchestrate toolkits add \
  --kind mcp \
  --name github \
  --description "GitHub MCP tools" \
  --package_root ./mcp_server \
  --command "python server.py" \
  --tools "*" \
  --app-id mcp_runtime_config
```

## Bind connections to custom agents

Custom agents use `experimental-connect`.

```bash
orchestrate agents experimental-connect \
  -n custom_agent_name \
  -c openai_api \
  -c crm_api
```

Credential key injection format:

```text
{connection_app_id}_{credential_type}
```

Example:

```bash
orchestrate connections configure \
  --app-id openai_api \
  --environment draft \
  --type team \
  --kind api_key
```

Injected credential key:

```text
openai_api_api_key
```

## Bind connections to knowledge bases

For external knowledge providers, create the connection first and pass it during knowledge base import.

```bash
orchestrate connections add \
  -a external_elasticsearch \
  --component knowledge \
  --category elasticsearch

orchestrate connections configure \
  -a external_elasticsearch \
  --env draft \
  --kind api_key \
  --type team \
  --server-url https://search.example.com

orchestrate connections set-credentials \
  -a external_elasticsearch \
  --env draft \
  --api-key "$ELASTIC_API_KEY"

orchestrate knowledge-bases import \
  -f knowledge/vendor_policy_kb.yaml \
  -a external_elasticsearch
```

Knowledge provider support summary:

| Provider | Supported auth |
|---|---|
| Milvus | Basic |
| Elasticsearch | Basic, API key |
| Custom search | Basic, API key |

## Manage connections

```bash
orchestrate connections list

orchestrate connections import -f connections/vendor_risk_api.yaml

orchestrate connections export \
  -a vendor_risk_api \
  -o connections/vendor_risk_api.exported.yaml

orchestrate connections remove --app-id vendor_risk_api
```

Removing a connection also removes associated configuration. Do not remove a connection before removing or updating dependent tools, toolkits, knowledge bases, or custom agents.

## Deployment order

Connections should be created before dependent tools, toolkits, agents, and knowledge bases.

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# 1. Activate target environment.
orchestrate env activate "$WO_ADK_ENVIRONMENT_NAME" -a "$WO_ADK_API_KEY"

# 2. Import connection configs.
orchestrate connections import -f connections/vendor_risk_api.yaml
orchestrate connections import -f connections/mcp_runtime_config.yaml

# 3. Set credentials from environment variables or secret manager output.
orchestrate connections set-credentials \
  -a vendor_risk_api \
  --env draft \
  --api-key "$VENDOR_RISK_API_KEY"

orchestrate connections set-credentials \
  -a mcp_runtime_config \
  --env draft \
  -e GITHUB_TOKEN="$GITHUB_TOKEN"

# 4. Import dependent tools/toolkits/knowledge.
orchestrate tools import -k python -f tools/vendor_tools.py -a vendor_risk_api
orchestrate toolkits add --kind mcp --name github --package_root ./mcp_server --command "python server.py" --tools "*" --app-id mcp_runtime_config

# 5. Import agents that use the tools.
orchestrate agents import -f agents/vendor_support_agent.yaml
```

## Model guidance

When asked to generate a watsonx Orchestrate asset that calls an external system:

1. Create a connection spec first.
2. Do not place credentials in YAML or code.
3. Add CLI commands to set credentials separately.
4. Bind the connection at tool/toolkit/knowledge import time.
5. For Python tools, declare `expected_credentials` and read credentials with `ibm_watsonx_orchestrate.run.connections`.
6. For embedded web chat SSO use cases, use IDP/SSO connection patterns rather than generic OAuth assumptions.
7. Always document draft/live differences.
8. Include local emulation exports for Python-tool tests when useful.
