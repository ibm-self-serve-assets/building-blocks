---
name: agent-builder
description: Build and deploy multi-agent systems with tools (MCP servers) using watsonx Orchestrate's Agent Development Kit (ADK), CLI and REST API
---

## IBM watsonx Orchestrate
IBM watsonx Orchestrate (WxO) supports building, orchestrating, deploying and governing AI agents. The watsonx Orchestrate [Agent Development Kit (ADK)](https://developer.watson-orchestrate.ibm.com) gives developers a pro-code path for creating agents, tools, knowledge bases, and integrations using a Python library, CLI and REST APIs. Together, watsonx Orchestrate and the ADK let teams move from local development and testing to deployment in watsonx Orchestrate, while also connecting external agents, APIs, and frameworks into a governed enterprise agent ecosystem.

## Getting Started
Even if you'll connect to Orchestrate via the REST API, you'll need to use the ADK when building, deploying, and testing your agents. Start by installing the `ibm-watsonx-orchestrate` Python library, which also installs the `orchestrate` executable.

Execute the following script to install `ibm-watsonx-orchestrate` into a virtual python environment called `ai-agent-builder`

```bash
# Make the script executable (first time only)
chmod +x run-adk.sh
bash run-adk.sh
```

### Using the orchestrate CLI executable
The best way to learn about the `orchestrate` executable's latest capabilities is to run the help command:

```bash
orchestrate --help
```

### Activate your Orchestrate environment
To work with agents, tools and connections, your Orchestrate environment must first be activated.  Check your local .env for the required variables.

```bash
# always ensure an environment is active
orchestrate env list 

# Create a new environment if needed.  
orchestrate env add --name WO_ADK_ENVIRONMENT_NAME --url WO_INSTANCE_URL

# Activate environment if needed. Always pass the WXO_API_KEY to ensure non-blocking activation.
orchestrate env activate ORCHESTRATE_ENVIRONMENT_NAME -a WXO_API_KEY
```

## Required Reading

The following documents provide detailed, task-focused guidance for designing, building, deploying, and integrating watsonx Orchestrate agents and their supporting assets.

- [Building and deploying agents](agents.md)  
  Defines native and external agent patterns, YAML structure, agent styles, collaborator routing, deployment order, draft/live promotion, REST API access, and agent runtime debugging.

- [Building and deploying tools and toolkits](tools_and_toolkits.md)  
  Covers Python tools, OpenAPI tools, MCP toolkits, Python toolkits, import/update/remove commands, naming conventions, packaging structure, and how tools are attached to agents.

- [Building and deploying knowledge bases](knowledgebases.md)  
  Explains built-in and external knowledge bases, document ingestion, vector index configuration, external search provider patterns, import/status/export/remove commands, and how agents reference knowledge bases.

- [Configuring connections](connections.md)  
  Covers app IDs, draft/live credentials, connection configuration, credential binding, and how connections are associated with tools, toolkits, knowledge bases, and external agents.

- [Embedding chat in applications](embedded_chat.md)  
  Explains how to expose deployed agents through embedded web chat, generate embed code, use context variables, handle events, secure backend-issued tokens, customize the UI, and decide when to use embedded chat versus REST APIs.
