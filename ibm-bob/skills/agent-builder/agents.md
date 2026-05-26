# watsonx Orchestrate Agents 
In-depth guide for authoring, importing, deploying and testing watsonx Orchestrate agents with the ADK CLI and REST APIs.

## Recommended project layout

```text
orchestrate-project/
├── agents/          # Agent specifications: YAML, JSON, or Python
├── tools/           # Python tools and tool packages
├── knowledge/       # Knowledge base specs and source documents
├── flows/           # Agentic workflow definitions
├── connections/     # Connection notes/specs; credentials are configured separately
├── scripts/         # Deployment, rollback, smoke tests
├── docs/            # Optional design notes and runbooks
└── tests/           # Optional tests and validation fixtures
```

Rules for generated paths:

- Assume commands run from the project root unless a script explicitly `cd`s there.
- Keep agent specs in `agents/`.
- Keep tool code in `tools/` and toolkit packages in their own subfolders.
- Keep deploy/rollback scripts in `scripts/` and make them executable.

## Agent kinds

| Kind | Use when |
|---|---|
| `native` | The agent is built and managed directly in watsonx Orchestrate. |
| `external` | The agent is hosted outside Orchestrate and exposed through `external_chat` or A2A. |
| `assistant` | The collaborator is a watsonx Assistant. |

## Naming and model references

Use `snake_case` everywhere: agent names, tool names, toolkit names, collaborator names, knowledge base names, folders, Python files, and YAML specs.

```text
Good agent:  contract_risk_review_agent
Good tool:   get_order_status
Good file:   customer_support_agent.yaml
Bad:         myAgent1
Bad:         Helper Agent
Bad:         order-tools.py
```

Rules:

- Use lowercase letters, numbers, and underscores.
- Avoid spaces, hyphens, special characters, and generic names like `helper`.
- Keep names short and domain-specific.
- Treat `description` as routing metadata for supervisor/collaborator selection.
- Use full model paths in `llm`, usually `provider/model-name` or the provider-qualified path required by the target environment.

## Native agent YAML example

Use this as the canonical native-agent shape. Prefer adapting this one example rather than generating multiple competing examples.

```yaml
spec_version: v1
kind: native
name: contract_review_agent
llm: groq/openai/gpt-oss-120b
style: default
hide_reasoning: false
memory_enabled: false

description: |
  Reviews contract language, identifies risk, and routes specialized legal,
  procurement, or compliance questions to collaborator agents.

instructions: |
  You help users review contracts.
  Use tools when facts must come from systems of record.
  Use the knowledge base for policy or playbook questions.
  Route specialist questions to collaborators when they are a better fit.
  Do not invent contract terms or policy requirements.

collaborators:
  - legal_policy_agent
  - procurement_agent

tools:
  - contract_tools:extract_clauses
  - contract_tools:score_risk
  - get_vendor_record

knowledge_base:
  - contract_playbook_kb

restrictions: editable
```

## External agent YAML example

Use an external agent when the runtime is hosted outside Orchestrate. Use `external_chat` for OpenAI-style chat-completion endpoints. Use the supported A2A provider string when integrating A2A-compatible agents.

```yaml
spec_version: v1
kind: external
name: research_agent
title: Research Agent
nickname: research_agent
provider: external_chat
# For A2A, use the supported provider string, for example:
# provider: external_chat/A2A/0.3.0
description: |
  Searches and summarizes research-heavy topics from an externally hosted agent.
tags:
  - research
api_url: "https://example.com/chat/completions"
auth_scheme: BEARER_TOKEN # BEARER_TOKEN | API_KEY | NONE
auth_config:
  token: "${RESEARCH_AGENT_TOKEN}"
chat_params:
  stream: true
config:
  hidden: false
  enable_cot: false
```

## Agent style selection

| Style | YAML value | Use when | Behavior |
|---|---|---|---|
| Default | `default` | Simple or lightly sequential work | Tool-centric; model chooses tools and decides when to respond. |
| ReAct | `react` | Ambiguous, evolving, research-like work | Iterative Think → Act → Observe loop. |
| Planner | `planner` | Transparent, structured, multi-step workflows | Builds a task/tool plan first, then executes step by step and can replan. |

Default is usually the safest baseline. Upgrade to `react` when the path is not known up front. Use `planner` when the user or workflow needs explicit sequencing and transparency.

## Instruction contract

Instructions are the primary control surface for native agents. A strong instruction block should usually specify:

1. Role and expertise.
2. Primary responsibilities.
3. Tool usage rules.
4. Collaborator routing logic, if multi-agent.
5. Knowledge base usage rules, if grounded retrieval is required.
6. Output format requirements.
7. Error handling and uncertainty behavior.

Model-facing rules:

- Write operational instructions, not vague persona prompts.
- State when to use each tool.
- State when not to use a tool.
- State when to route to a collaborator.
- State what to do when no collaborator fits.
- For grounded answers, tell the agent to say when the knowledge base does not contain the answer.
- Never instruct the agent to invent data that should come from a system of record.

## Optional native-agent fields

Avoid generating a separate YAML example for each optional feature. Add only the fields needed by the use case.

| Field | Use when | Notes |
|---|---|---|
| `guidelines` | Deterministic behavior should fire when a condition is met. | Use sparingly; keep conditions concrete. |
| `context_access_enabled` | Runtime context variables are required. | Required when the agent needs passed user, tenant, session, or channel context. |
| `context_variables` | The agent needs named context fields. | Built-ins include `wxo_email_id`, `wxo_user_name`, `wxo_tenant_id`, `wxo_thread_id`, `wxo_run_id`. Do not use the reserved `wxo_` prefix for custom variables. |
| `chat_with_docs` | Users should upload session-scoped documents during chat. | Use when uploaded files are the source of truth for a session. Configure citation behavior and an explicit `idk_message`. |
| `structured_output` | The response must match a schema. | Prefer for workflows consumed by another system. |
| `memory_enabled` | Agent should retain conversation memory where supported. | Default false unless the scenario requires it. |
| `hide_reasoning` | Reasoning/steps should be hidden from users. | Keep false for debugging, true for production UX when appropriate. |
| `restrictions` | Control editability. | Use environment/team convention. |

Context-variable rules:

- Reference variables in instructions, descriptions, or guidelines with `{variable_name}`.
- Built-in context variables use the `wxo_` prefix.
- Custom context variables must not use the reserved `wxo_` prefix.
- Use underscores, not hyphens.

## Multi-agent design

Use collaborators for real domain specialization, not as generic helpers.

Rules:

- Create specialist collaborator agents before the parent/orchestrator agent.
- Parent/orchestrator agents route and synthesize; they should not duplicate specialist work.
- Each specialist should have one focused responsibility and a routing-oriented `description`.
- Parent instructions must specify when to route, when not to route, and what to do when no collaborator fits.
- Provide routing scenarios in prose inside the parent instructions when ambiguity is likely.
- Keep collaborator count low; too many specialists creates routing ambiguity.

Recommended build/import order:

1. Write/import tools and toolkits.
2. Write/import knowledge bases.
3. Write/import specialist collaborator agents.
4. Write/import parent/orchestrator agents.
5. Test in draft.
6. Deploy to live only after draft validation.

## CLI: import, create, deploy, manage

Import from YAML, JSON, Python, or exported ZIP:

```bash
orchestrate agents import -f agents/contract_review_agent.yaml
orchestrate agents import -f contract_review_agent.zip
```

Import with a connection, typically for external agents:

```bash
orchestrate agents import \
  -f agents/research_agent.yaml \
  --app-id research_agent_connection
```

List, export, update, and remove:

```bash
orchestrate agents list -v
orchestrate agents list --kind native -v
orchestrate agents export -n contract_review_agent -k native -o contract_review_agent.zip
orchestrate agents export -n contract_review_agent -k native --agent-only -o agents/contract_review_agent.yaml
orchestrate agents import -f agents/contract_review_agent.yaml
orchestrate agents remove --name contract_review_agent --kind native
```

Deploy / undeploy live agents:

```bash
orchestrate agents deploy --name contract_review_agent
orchestrate agents undeploy --name contract_review_agent
```

Test in chat from CLI:

```bash
orchestrate chat ask --agent-name contract_review_agent
orchestrate chat ask --agent-name contract_review_agent "Review this vendor agreement for risk."
```

Generate embedded web chat snippet for a live/deployed agent:

```bash
orchestrate channels webchat embed --agent-name contract_review_agent
```

## Deployment script pattern

Use a script so agent, tool, toolkit, and knowledge-base order stays deterministic.

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Activating Orchestrate environment..."
orchestrate env activate "$WO_ADK_ENVIRONMENT_NAME" -a "$WXO_API_KEY"

echo "Importing tools and toolkits..."
orchestrate tools import -k python -f tools/contract_tools.py -p .
orchestrate toolkits add \
  --kind mcp \
  --name contract_tools \
  --description "Contract analysis tools" \
  --package_root ./tools/contract_mcp_server \
  --command "python server.py" \
  --tools "*"

echo "Importing knowledge bases..."
orchestrate knowledge-bases import -f knowledge/contract_playbook_kb.yaml

echo "Importing collaborator agents..."
orchestrate agents import -f agents/legal_policy_agent.yaml
orchestrate agents import -f agents/procurement_agent.yaml

echo "Importing parent agent..."
orchestrate agents import -f agents/contract_review_agent.yaml

echo "Validating assets..."
orchestrate tools list -v
orchestrate knowledge-bases list
orchestrate agents list -v
```

Rollback pattern:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Removing deployed assets..."
orchestrate agents remove --name contract_review_agent --kind native
orchestrate agents remove --name legal_policy_agent --kind native
orchestrate agents remove --name procurement_agent --kind native
orchestrate toolkits remove -n contract_tools
orchestrate tools remove -n get_vendor_record
orchestrate knowledge-bases remove --name contract_playbook_kb
```

## Draft vs live

Agents operate in draft or live state.

| State | Use for | Notes |
|---|---|---|
| Draft | Development and testing | Validate in the builder UI and CLI before promotion. |
| Live | End-user access | Required for REST API and embedded web chat integrations. |

Guidance:

1. Test draft agents in the Orchestrate UI and with `orchestrate chat ask` before deployment.
2. Deploy to live only after tools, connections, knowledge bases, and collaborators are validated.
3. Use `orchestrate agents deploy --name agent_name` to promote draft to live.
4. Use `orchestrate agents undeploy --name agent_name` to remove live availability.

## REST API access pattern

Use REST APIs for application-driven interactions with deployed/live agents. Browser UIs should not call Orchestrate directly. Route calls through a server-side backend.

Backend responsibilities:

- Enforce app-level authorization.
- Store private keys and API keys securely.
- Perform IBM IAM token exchange server-side.
- Cache token expiry and refresh before expiry.
- Hide agent IDs, environment IDs, tenant details, and secrets from browser code.
- Add logging for request IDs, run IDs, thread IDs, response status, and parsing failures.

Development can use `.env`; production should use a secrets manager such as HashiCorp Vault or the platform-standard equivalent.

## REST endpoints for agents and runs

| Method | Endpoint | Use |
|---|---|---|
| `GET` | `/v1/orchestrate/agents` | List available agents for picker/admin UI. |
| `GET` | `/v1/orchestrate/agents/{agent_id}` | Inspect a specific agent. |
| `GET` | `/v1/orchestrate/agents/{agent_id}/environment` | List environments for an agent. |
| `POST` | `/v1/orchestrate/runs` | Create a non-streaming agent run. |
| `GET` | `/v1/orchestrate/runs` | List run metadata. |
| `GET` | `/v1/orchestrate/runs/{run_id}` | Fetch/poll one run. |
| `GET` | `/v1/orchestrate/runs/{run_id}/events` | Inspect streamed or async events. |
| `POST` | `/v1/orchestrate/runs/stream` | Stream incremental agent output. |
| `POST` | `/v1/orchestrate/runs/cancel/{run_id}` | Cancel a run when the UX supports abort. |

Important:

- REST payloads require the agent ID, not the agent name.
- Passing an agent name where the API expects `agent_id` can produce confusing backend/database errors.
- Pass the correct `environment_id` for the deployed/live agent environment.

## IAM token exchange

```bash
export WXO_API_KEY="..."

TOKEN=$(curl -sS -X POST "https://iam.cloud.ibm.com/identity/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=urn:ibm:params:oauth:grant-type:apikey" \
  -d "apikey=${WXO_API_KEY}" | jq -r '.access_token')
```

List environments for an agent:

```bash
curl --request GET \
  --url "https://${WXO_INSTANCE_URL}/v1/orchestrate/agents/${AGENT_ID}/environment" \
  --header "Authorization: Bearer ${TOKEN}" \
  --header "Accept: application/json"
```

Node/Express-style token cache:

```javascript
import axios from 'axios';

let cachedToken = null;
let cachedExpiryMs = 0;

export async function getIamToken() {
  const now = Date.now();
  if (cachedToken && now < cachedExpiryMs - 60_000) return cachedToken;

  const body = new URLSearchParams({
    grant_type: 'urn:ibm:params:oauth:grant-type:apikey',
    apikey: process.env.WXO_API_KEY,
  });

  const response = await axios.post(
    process.env.WXO_AUTH_URL ?? 'https://iam.cloud.ibm.com/identity/token',
    body,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );

  cachedToken = response.data.access_token;
  cachedExpiryMs = Date.now() + (response.data.expires_in ?? 3600) * 1000;
  return cachedToken;
}
```

## Non-streaming agent run

Use non-streaming calls for batch-style UX or when polling is acceptable.

```javascript
import axios from 'axios';
import { getIamToken } from './auth.js';

export async function runAgent(messageText) {
  const token = await getIamToken();

  const createResponse = await axios.post(
    `${process.env.WXO_INSTANCE_URL}/v1/orchestrate/runs`,
    {
      message: {
        role: 'user',
        content: [{ response_type: 'text', text: messageText }],
      },
      agent_id: process.env.AGENT_ID,
      environment_id: process.env.AGENT_ENVIRONMENT_ID,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    }
  );

  return pollForCompletion(createResponse.data.run_id, token);
}

async function pollForCompletion(runId, token) {
  for (let i = 0; i < 60; i++) {
    const response = await axios.get(
      `${process.env.WXO_INSTANCE_URL}/v1/orchestrate/runs/${runId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );

    if (response.data.status === 'completed') return parseAgentResponse(response.data);
    if (response.data.status === 'failed') throw new Error(`Run failed: ${runId}`);

    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  throw new Error(`Run timeout: ${runId}`);
}

function parseAgentResponse(completedRun) {
  const content = completedRun?.result?.data?.message?.content;
  const finalResponse = Array.isArray(content) ? content[0]?.text ?? null : null;
  const stepHistory = completedRun?.result?.data?.message?.step_history ?? [];

  return { finalResponse, stepHistory, fullResponse: completedRun };
}
```

Response parsing paths:

```text
Final response: result.data.message.content[0].text
Step history:   result.data.message.step_history
Metadata:       run_id, thread_id, status
```

## Streaming agent run

Use streaming when the UX should render partial tokens, incremental steps, or live progress for long-running calls.

```javascript
import axios from 'axios';
import { getIamToken } from './auth.js';

export async function streamAgent(messageText, onEvent) {
  const token = await getIamToken();

  const response = await axios.post(
    `${process.env.WXO_INSTANCE_URL}/v1/orchestrate/runs/stream`,
    {
      message: {
        role: 'user',
        content: [{ response_type: 'text', text: messageText }],
      },
      agent_id: process.env.AGENT_ID,
      environment_id: process.env.AGENT_ENVIRONMENT_ID,
    },
    {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      responseType: 'stream',
    }
  );

  response.data.on('data', chunk => {
    for (const line of chunk.toString().split('\n')) {
      if (!line.trim()) continue;
      try {
        onEvent(JSON.parse(line));
      } catch {
        // Ignore partial or non-JSON stream fragments.
      }
    }
  });
}
```
