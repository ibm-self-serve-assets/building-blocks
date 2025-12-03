# Travel Planner Agent Demo Setup Guide

This comprehensive guide will walk you through building a sophisticated Travel Planner Agent using IBM watsonx Orchestrate. This intelligent agent represents a powerful example of multi-agent orchestration, demonstrating how to create conversational AI systems that can seamlessly integrate multiple external services and data sources to provide comprehensive, personalized assistance.

The Travel Planner Agent we'll build is designed to revolutionize how users approach trip planning by offering:

- **Intelligent Destination Research**: Leveraging advanced web search capabilities to discover attractions, activities, local insights, weather information, and cultural recommendations for any destination worldwide
- **Smart Accommodation Discovery**: Integrating with Airbnb's extensive database to find and recommend suitable places to stay based on user preferences, budget constraints, and travel dates
- **Personalized Travel Recommendations**: Creating customized itineraries that adapt to individual preferences, group dynamics, and specific travel requirements
- **Interactive Planning Experience**: Providing a conversational interface that guides users through the entire planning process with natural, engaging dialogue
- **Comprehensive Information Synthesis**: Combining data from multiple sources to deliver well-rounded, actionable travel advice

This demo showcases the power of modern AI orchestration platforms in creating sophisticated, tool-enabled conversational agents that can handle complex, multi-step workflows while maintaining a natural, user-friendly experience.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Step 2: Watsonx Orchestrate Connection Setup](#step-2-watsonx-orchestrate-connection-setup)
- [Step 3: Travel Planner Agent Creation](#step-3-travel-planner-agent-creation)
- [Step 4: Tool Configuration](#step-4-tool-configuration)

- [Summary](#summary)

## Overview

In this demo, we will create a **Travel Planner Agent** that provides:

- **Destination Research**: Web search capabilities for attractions, activities, and local information
- **Accommodation Search**: Airbnb integration for finding suitable places to stay
- **Personalized Recommendations**: Customized travel plans based on user preferences
- **Interactive Planning**: Conversational interface for trip planning assistance


## Prerequisites

Before starting, ensure you have:

- Access to IBM watsonx Orchestrate instance
- Tavily API account and key
- Basic understanding of agent development concepts
- Text editor for HTML file modification


### .env file variables


| Variable | Section | Example/Default Value | Description |
|----------|---------|----------------------|-------------|
| WXO_SERVICE_URL | Orchestrate service | https://api.{hostname}/instances/{tenant_id} | Watsonx Orchestrate instance base URL  |
| WXO_API_KEY | Orchestrate service | Your API key | API key for service authentication |
| WXO_TOKEN_URL | Orchestrate service | https://iam.cloud.ibm.com/identity/token | IBM Cloud IAM token endpoint |
| AGENT_NAME | AI Agent | Travel_Planner_Agent | Name of the AI agent  |
| AGENT_DESCRIPTION | AI Agent | You are a Personalized Travel Planner Agent... | Agent purpose description |
| AGENT_INSTRUCTIONS | AI Agent | You are a Personalized Travel Planner Agent... | Workflow, rules, interaction style (use \n) |
| AGENT_LLM | AI Agent | watsonx/meta-llama/llama-3-2-90b-vision-instruct | Language model identifier  |
| TOOLKIT_NAME | Toolkit | my_mcp_toolkit | MCP toolkit name  |
| TOOL_NAME_SEARCH | Toolkit | tavily_search | Search tool name |
| TOOL_NAME_EXTRACT | Toolkit | tavily_extract | Extract tool name |
| TOOLKIT_DESCRIPTION | Toolkit | my_mcp_toolkit description | Toolkit description  |
| MCP_URL | Toolkit | MCP URL with API key | MCP server URL  |
| CONNECTION_APP_ID | Connection | connection app id | MCP connection app ID|
| WXO_CONNECTION_API_KEY | Connection | connection api key | Connection API key |
| WXO_CONNECTION_TYPE | Connection | api_key_auth | Connection auth type  |
| WXO_CONNECTION_NAME | Connection | connection name | Connection name|


## Step 2: Watsonx Orchestrate Connection Setup

### 2.1 Create connection

The script provides an automated way to create an WxO connection and related credential using the WXO Orchestration API.
It reads configuration values from environment variables (already covered in the Prerequisites section) and sends a POST request to register a new connection and credential.

### 2.1 Overview

The script defines an clsConnection class responsible for:

1. Loading environment variables using python-dotenv

2. Preparing the connection creation payload

3. Requesting and using an authentication token (via the clsAuth class from wxo_token)

4. Sending a POST request to the WXO Orchestration API

5. Returning the created connection metadata

6. At runtime, it creates an instance of the class, submits the request, and prints the newly created connection ID.

### 2.2 Configure connection Details

Configure your connection using the environment variables defined in your .env file.

Use:

1. `WXO_CONNECTION_NAME` — sets the connection’s display name
2. `WXO_CONNECTION_TYPE` — defines the connection’s authentication type. Here the value will be 'api_key_auth'.
3. `WXO_CONNECTION_API_KEY` — The api key value created during Tavily API Setup step.

## Step 3: Travel Planner Agent Creation
The script provides an automated way to create an AI Agent using the WXO Orchestration API.
It reads configuration values from environment variables (already covered in the Prerequisites section) and sends a POST request to register a new agent.

### 3.1 Overview

The script defines an AIAgentCreator class responsible for:

1. Loading environment variables using python-dotenv

2. Preparing the agent creation payload

3. Requesting and using an authentication token (via the clsAuth class from wxo_token)

4. Sending a POST request to the WXO Orchestration API

5. Returning the created agent’s metadata

6. At runtime, it creates an instance of the class, submits the request, and prints the newly created agent ID.

### 3.2 Configure Agent Details

Configure your agent using the environment variables defined in your .env file.

Use:

1. `AGENT_NAME` — sets the agent’s display name

2. `AGENT_DESCRIPTION` — defines the agent’s purpose and general description

Example, 
```bash
AGENT_NAME="Travel_Planner_Agent"

AGENT_DESCRIPTION="You are a Personalized Travel Planner Agent. You help users plan their trips by searching for attractions, activities, and accommodations. You provide comprehensive travel recommendations with a friendly, interactive approach."

```

### 3.3 Define Agent Behavior

Define and customize the agent’s behavior using the `AGENT_INSTRUCTIONS` variable in your .env file.
Example is as below.

```bash
AGENT_INSTRUCTIONS="You are a Personalized Travel Planner Agent that helps users plan amazing trips. Always greet users with \"Hi! I am your personalized travel planner\" and maintain a warm, helpful, and interactive tone throughout the conversation.\n\nWORKFLOW (MANDATORY SEQUENCE):\n1. Use Tavily_Server_DA_2:tavily-search tool to research the destination city, find top attractions, activities, points of interest, weather information, and local recommendations\n2. Use Airbnb rooms search tool to find available accommodations in the destination area based on user preferences and dates\n   - airbnb-test-mcp-5:airbnb_listing_details: Get detailed information about a specific Airbnb listing. Provide direct links to the user\n   - airbnb-test-mcp-5:airbnb_search: Search for Airbnb listings with various filters and pagination. Provide direct links to the user\n3. Synthesize the information to create comprehensive travel recommendations and suggestions\n\nCRITICAL RULES:\n- ALWAYS introduce yourself as \"Hi! I am your personalized travel planner\" at the start\n- ALWAYS be verbose, friendly, and interactive in your responses\n- ALWAYS ask follow-up questions to better understand user preferences (budget, group size, interests, travel dates)\n- ALWAYS use Tavily_Server_DA_2:tavily-search to research comprehensive information about the destination\n- ALWAYS use Airbnb rooms search to find suitable accommodations\n- ALWAYS provide multiple options and alternatives for both attractions and accommodations\n- ALWAYS suggest next steps and ask courtesy questions like \"Would you like me to find more options?\" or \"Should I look for accommodations in a different area?\"\n- ALWAYS provide practical details (timing, costs, accessibility, booking requirements)\n- ALWAYS format responses with clear sections and bullet points\n- If insufficient information found, suggest alternative approaches or nearby locations\n- Keep the conversation flowing with natural follow-up questions\n\nINTERACTION STYLE:\n- Be enthusiastic about travel and destinations\n- Ask about budget, group size, interests, and travel dates\n- Provide multiple accommodation options with different price ranges\n- Suggest both popular attractions and hidden gems\n- Always end with helpful next steps or questions\n\nExample queries: \"I want to visit Austin, Texas\", \"Plan a weekend trip to San Francisco\", \"Find me things to do in Paris with good weather\""

```

### 3.4 Define LLM model for use
Use variable named `AGENT_LLM` from .env file to use required model.

Example is as below.

```bash
AGENT_LLM="watsonx/meta-llama/llama-3-2-90b-vision-instruct"
```
### 3.5 Usage
Run the script directly to create AI agent on Orchestrate.

```bash
python3 step3_travel_planner_agent_creation.py
```

The output will display agent id as follows.

```bash
Agent created successfully, with id: <generated_agent_id> 
```
# Step 4 – MCP Toolkit Setup & Agent Tool Mapping

## Overview

This step creates the **MCP Toolkit** inside IBM watsonx Orchestrate using your MCP server (e.g., Tavily MCP).  
After creating the toolkit, the script automatically:

1. Fetches the toolkit definition from the server  
2. Extracts the resolved tool list  
3. Locates your Travel Planner Agent by name  
4. Updates the agent’s tool configuration  
5. Attaches all toolkit tools to the agent  

This makes the agent fully capable of calling tools like:

- `tavily-search`  
- `tavily-extract`  
- (any other MCP-exposed tools)

---

## Important Methods (from `MCPToolkitClient`)

| Method | Purpose | HTTP Endpoint |
|--------|---------|---------------|
| `create_mcp_toolkit()` | Creates a new MCP toolkit | `POST /v1/orchestrate/toolkits` |
| `get_toolkit_by_id()` | Fetches toolkit details (including tools) | `GET /v1/orchestrate/toolkits/{id}` |
| `list_agents()` | Returns all agents in the instance | `GET /v1/orchestrate/agents` |
| `filter_agent_by_name()` | Finds agent by its display name | — (local helper) |
| `update_agent_tools()` | Updates the agent’s tool list | `PATCH /v1/orchestrate/agents/{id}` |

These methods together enable toolkit creation and automatic agent-tool mapping.

---

## Required `.env` Variables

Ensure the following variables are set in your `.env`:

```bash
# Watsonx Orchestrate instance
WXO_SERVICE_URL="https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<INSTANCE_ID>"

# Toolkit configuration
TOOLKIT_NAME="Tavily_Server_DA_2"
TOOLKIT_DESCRIPTION="Toolkit exposing Tavily MCP tools"

# MCP details
MCP_URL="https://mcp.tavily.com/mcp/?tavilyApiKey=<YOUR_API_KEY>"
CONNECTION_APP_ID="<connection_id_created_in_step2>"

# Agent to attach tools to
AGENT_NAME="Travel_Planner_Agent"
```

If any required variables are missing, the script stops with:

```
Missing required environment variables
```

---

## How to Run the Script

Run the Step 4 script:

```bash
python3 step4_toolkit_and_agent_tools_setup.py
```

This will:

- Load `.env`
- Authenticate using `clsAuth`
- Create the toolkit
- Fetch the toolkit definition
- Extract tool list
- Find the agent
- Attach the tools to the agent

---

## Expected Output

A successful run prints:

```
Using instance base URL: https://api.us-south.watson-orchestrate.cloud.ibm.com/instances/...

Created toolkit successfully, with id: <toolkit_id>

Toolkit fetched by ID:
{ ... full toolkit metadata JSON ... }

Toolkit tools:
[
  { "id": "tavily-search", ... },
  { "id": "tavily-extract", ... }
]

Required agent found with id: <agent_id>
<Response [200]>
Agent tools updated successfully.
```

If the agent is missing:

```
Agent 'Travel_Planner_Agent' not found. Skipping tool update.
```

If toolkit creation fails:

```
MCPToolkitError occurred:
Message: HTTP 401 error while calling MCP toolkit API.
Status code: 401
Response body: {...}
```

---
## Summary

Congratulations! You have successfully created a comprehensive Travel Planner Agent with the following capabilities:

### What You've Built

- **Intelligent Travel Planning**: Agent that researches destinations and provides recommendations
- **Web Search Integration**: Tavily-powered search for attractions and local information
- **Accommodation Search**: Airbnb integration for finding suitable places to stay
- **Interactive Interface**: Conversational agent with personalized responses
- **External Integration**: Embeddable agent for use in external applications



### Additional Resources

- [IBM watsonx Orchestrate Documentation](https://developer.watson-orchestrate.ibm.com/)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Airbnb MCP Server Documentation](https://github.com/openbnb/mcp-server-airbnb)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers) - Free MCP servers to extend your agent capabilities

---

**Note**: This demo showcases the power of multi-agent orchestration in creating sophisticated, tool-enabled conversational agents. The principles demonstrated here can be applied to various other use cases and domains.
