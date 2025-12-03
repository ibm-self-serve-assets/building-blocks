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
- [Step 1: Tavily API Setup](#step-1-tavily-api-setup)
- [Step 2: Watsonx Orchestrate Connection Setup](#step-2-watsonx-orchestrate-connection-setup)
- [Step 3: Travel Planner Agent Creation](#step-3-travel-planner-agent-creation)
- [Step 4: Tool Configuration](#step-4-tool-configuration)
- [Step 5: Agent Testing](#step-5-agent-testing)
- [Step 6: External Integration](#step-6-external-integration)
- [Troubleshooting](#troubleshooting)
- [Summary](#summary)

## Overview

In this demo, we will create a **Travel Planner Agent** that provides:

- **Destination Research**: Web search capabilities for attractions, activities, and local information
- **Accommodation Search**: Airbnb integration for finding suitable places to stay
- **Personalized Recommendations**: Customized travel plans based on user preferences
- **Interactive Planning**: Conversational interface for trip planning assistance

### Architecture

The following diagram illustrates the basic agent and tool flow for the Travel Planner Agent:

![Travel Planner Agent Architecture](./assets/Travel_planner_agent.png)

The agent will utilize three main tools:
1. **Tavily Web Search** - For researching destinations and attractions
2. **Airbnb Search** - For finding available accommodations
3. **Airbnb Listing Details** - For detailed accommodation information

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


## Step 1: Tavily API Setup

### 1.1 Generate Tavily API Key



## Step 2: Watsonx Orchestrate Connection Setup

### 2.1 Access Connections Panel

TBD

## Step 3: Travel Planner Agent Creation

### 3.1 Create New Agent

1. Navigate to **Agent Builder** from the left panel
2. Click **Create Agent**

![Create Agent](./assets/create_agent.png)

### 3.2 Configure Agent Details

Enter the following agent configuration:

**Agent Name**: `Travel_Planner_Agent`

**Description**:
```
You are a Personalized Travel Planner Agent. You help users plan their trips by searching for attractions, activities, and accommodations. You provide comprehensive travel recommendations with a friendly, interactive approach.
```

![Agent Details](./assets/Agent_details.png)

### 3.3 Define Agent Behavior

Configure the agent's behavior with the following detailed instructions:

```
You are a Personalized Travel Planner Agent that helps users plan amazing trips. Always greet users with "Hi! I am your personalized travel planner" and maintain a warm, helpful, and interactive tone throughout the conversation.

WORKFLOW (MANDATORY SEQUENCE):
1. Use Tavily_Server_DA_2:tavily-search tool to research the destination city, find top attractions, activities, points of interest, weather information, and local recommendations
2. Use Airbnb rooms search tool to find available accommodations in the destination area based on user preferences and dates
   - airbnb-test-mcp-5:airbnb_listing_details: Get detailed information about a specific Airbnb listing. Provide direct links to the user
   - airbnb-test-mcp-5:airbnb_search: Search for Airbnb listings with various filters and pagination. Provide direct links to the user
3. Synthesize the information to create comprehensive travel recommendations and suggestions

CRITICAL RULES:
- ALWAYS introduce yourself as "Hi! I am your personalized travel planner" at the start
- ALWAYS be verbose, friendly, and interactive in your responses
- ALWAYS ask follow-up questions to better understand user preferences (budget, group size, interests, travel dates)
- ALWAYS use Tavily_Server_DA_2:tavily-search to research comprehensive information about the destination
- ALWAYS use Airbnb rooms search to find suitable accommodations
- ALWAYS provide multiple options and alternatives for both attractions and accommodations
- ALWAYS suggest next steps and ask courtesy questions like "Would you like me to find more options?" or "Should I look for accommodations in a different area?"
- ALWAYS provide practical details (timing, costs, accessibility, booking requirements)
- ALWAYS format responses with clear sections and bullet points
- If insufficient information found, suggest alternative approaches or nearby locations
- Keep the conversation flowing with natural follow-up questions

INTERACTION STYLE:
- Be enthusiastic about travel and destinations
- Ask about budget, group size, interests, and travel dates
- Provide multiple accommodation options with different price ranges
- Suggest both popular attractions and hidden gems
- Always end with helpful next steps or questions

Example queries: "I want to visit Austin, Texas", "Plan a weekend trip to San Francisco", "Find me things to do in Paris with good weather"
```

## Step 4: Tool Configuration

### 4.1 Configure Tavily Search Tool
TBD

## Step 5: Agent Testing

### 5.1 Test Agent Functionality



## Step 6: External Integration

## Troubleshooting

### Common Issues and Solutions

#### Connection Issues
- **Problem**: Tavily connection fails to establish
- **Solution**: Verify API key is correct and has proper permissions

#### Tool Activation Issues
- **Problem**: Tools not appearing in agent
- **Solution**: Ensure MCP servers are properly connected and tools are activated

#### Agent Response Issues
- **Problem**: Agent not following behavior instructions
- **Solution**: Review and refine the behavior configuration

#### External Integration Issues
- **Problem**: HTML integration not working
- **Solution**: Verify orchestration ID and agent ID are correctly copied

### Getting Help

If you encounter issues not covered in this guide:
1. Check the IBM watsonx Orchestrate documentation
2. Review the agent and tool configuration
3. Test individual components separately
4. Contact support if needed

## Summary

Congratulations! You have successfully created a comprehensive Travel Planner Agent with the following capabilities:

### What You've Built

- **Intelligent Travel Planning**: Agent that researches destinations and provides recommendations
- **Web Search Integration**: Tavily-powered search for attractions and local information
- **Accommodation Search**: Airbnb integration for finding suitable places to stay
- **Interactive Interface**: Conversational agent with personalized responses
- **External Integration**: Embeddable agent for use in external applications

### Next Steps

- **Enhance the Agent**: Add more tools and capabilities
- **Customize Behavior**: Refine the agent's personality and responses
- **Scale Integration**: Deploy to production environments
- **Monitor Performance**: Track agent usage and optimize responses

### Additional Resources

- [IBM watsonx Orchestrate Documentation](https://developer.watson-orchestrate.ibm.com/)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Airbnb MCP Server Documentation](https://github.com/openbnb/mcp-server-airbnb)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers) - Free MCP servers to extend your agent capabilities

---

**Note**: This demo showcases the power of multi-agent orchestration in creating sophisticated, tool-enabled conversational agents. The principles demonstrated here can be applied to various other use cases and domains.