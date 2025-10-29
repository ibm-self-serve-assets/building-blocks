# 🧭 Travel Planner Agent – Building Block Deployment Guide

This guide provides a step-by-step walkthrough for deploying and customizing the **Travel Planner Agent**, built using **IBM watsonx Orchestrate**.  
It demonstrates a multi-agent orchestration system that integrates external services like **Tavily** and **Airbnb** to provide personalized travel planning assistance.

The Travel Planner Agent we'll build is designed to revolutionize how users approach trip planning by offering:

- **Intelligent Destination Research**: Leveraging advanced web search capabilities to discover attractions, activities, local insights, weather information, and cultural recommendations for any destination worldwide
- **Smart Accommodation Discovery**: Integrating with Airbnb's extensive database to find and recommend suitable places to stay based on user preferences, budget constraints, and travel dates
- **Personalized Travel Recommendations**: Creating customized itineraries that adapt to individual preferences, group dynamics, and specific travel requirements
- **Interactive Planning Experience**: Providing a conversational interface that guides users through the entire planning process with natural, engaging dialogue
- **Comprehensive Information Synthesis**: Combining data from multiple sources to deliver well-rounded, actionable travel advice

---

## 📑 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Prerequisites](#prerequisites)
6. [Project Structure](#project-structure)
7. [Developer Guide](#developer-guide)
   - [Step 1: Tavily API Setup](#step-1-tavily-api-setup)
   - [Step 2: Watsonx Orchestrate Connection Setup](#step-2-watsonx-orchestrate-connection-setup)
   - [Step 3: Travel Planner Agent Creation](#step-3-travel-planner-agent-creation)
   - [Step 4: Tool Configuration](#step-4-tool-configuration)
   - [Step 5: Agent Testing](#step-5-agent-testing)
   - [Step 6: External Integration](#step-6-external-integration)
8. [Examples](#examples)
9. [Business Value](#business-value)
10. [Use Cases](#use-cases)
11. [Benefits](#benefits)
12. [Contributing](#contributing)
13. [License](#license)

---

## 🧠 Overview

The **Travel Planner Agent** helps users plan personalized trips through intelligent orchestration of AI tools. It performs destination research, accommodation discovery, and itinerary creation — all through a conversational interface powered by IBM watsonx Orchestrate.

**Core Capabilities:**
- Intelligent destination research using **Tavily API**
- Smart accommodation recommendations via **Airbnb integration**
- Personalized itinerary generation based on user input
- Interactive, natural language trip planning experience

This demo showcases how AI orchestration can combine multiple services into a single, intuitive travel planning assistant.

---

## 🏗️ Architecture

The architecture uses IBM watsonx Orchestrate as the core orchestration layer, connecting to external MCP servers and APIs.

![Travel Planner Agent Architecture](./assets/Travel_planner_agent.png)

**Components:**
1. **Tavily Web Search MCP** – Retrieves attractions, activities, and local insights  
2. **Airbnb Search MCP** – Finds accommodation options based on preferences  
3. **Airbnb Listing Details MCP** – Provides detailed property information  

The agent coordinates these tools in a structured workflow to provide complete, context-aware travel recommendations.

---

## ✨ Features

- **Multi-Tool Integration**: Combines multiple APIs for richer, context-driven responses  
- **Natural Language Interface**: Users interact conversationally  
- **Personalization**: Learns from user preferences (budget, duration, location)  
- **Modular Setup**: Tools can be replaced or extended with new MCP servers  
- **Deployable Anywhere**: Works within IBM watsonx Orchestrate or embedded in web applications  

---

## 🧰 Technology Stack

| Component | Technology | Purpose |
|------------|-------------|----------|
| **Platform** | IBM watsonx Orchestrate | Agent orchestration and workflow management |
| **Integration Layer** | MCP (Model Context Protocol) | Connects external APIs like Tavily and Airbnb |
| **External Services** | Tavily API, Airbnb MCP Server | Destination and accommodation data |
| **Frontend (Optional)** | HTML/JavaScript | Embed the agent in web or demo environments |
| **Authentication** | Key-Value Pair | Secure access to external APIs |
| **Language** | Natural Language Prompts | Enables conversational interaction |

---

## ⚙️ Prerequisites

Before you begin, ensure you have:
- An **IBM watsonx Orchestrate** instance  
- A valid **Tavily API key**  
- Access to **Airbnb MCP Server** (publicly available)  
- Basic understanding of **agent development** concepts  
- A code/text editor (like VS Code) for HTML modification  

---

## 📁 Project Structure

```
Travel_Planner_Agent/
│
├── assets/                     # Screenshots and architecture diagrams
├── travel_planner.html          # HTML for web integration
├── README.md                    # Documentation
├── config/                      # Configuration and setup visuals
│   ├── tavily_setup.png
│   ├── orchestration/
│
└── tools/
    ├── tavily/
    ├── airbnb/
```

---

## 🧑‍💻 Developer Guide

### Step 1: Tavily API Setup
Follow steps to create and configure your **Tavily API key**.  

To configure your Tavily API key, follow these steps:

![Tavily API Key Setup](./assets/Tavily_apikey.png)

1. Navigate to the [Tavily Dashboard](https://tavily.com)
2. Sign up or log in to your account
3. Generate your API key from the dashboard
4. Copy the key and save it securely for later use

> **Important**: Keep your API key secure and never share it publicly.

### Step 2: Watsonx Orchestrate Connection Setup
Set up a new connection under **Connections** in watsonx Orchestrate.  
Authenticate using your Tavily API key and verify both draft and live environments.
Navigate to the **Connections** option in the left sidebar

![Connections Panel](./assets/Connections_wxo.png)

### 2.2 Create New Connection

1. Click **Add Connection** to begin the connection process

![Add Connection](./assets/add_connection.png)

2. Enter connection details:
   - **Connection ID**: `Tavily_MCP`
   - Click **Save and Continue**

![Establishing Connection](./assets/establishing_connection.png)

### 2.3 Configure Authentication

1. Expand the **Authentication type** menu

![Authentication Type Selection](./assets/tavily_authentication_type.png)

2. Select **Key Value Pair**

![Key Value Pair Selection](./assets/tavily_select_kay_value.png)

3. Configure the credentials:
   - **Key name**: `TAVILY_API_KEY`
   - **Value**: Paste your Tavily API key
   - Click **Connect**

![Tavily Credentials Configuration](./assets/tavily_select_kay_value.png)

### 2.4 Test Connection

1. Verify your draft connection shows as **Connected**

![Connection Test](./assets/tavily_connection_test.png)

2. Click **Next** to proceed

### 2.5 Configure Live Environment

1. Repeat the authentication setup for the Live environment
2. Use the same credentials as the draft environment

![Add Live Connection](./assets/tavily_add_connection.png)

3. Click **Add Connection** when complete

![Final Add Connection](./assets/tavily_final_add_connection.png)

### 2.6 Verify Connection Status

1. Confirm both draft and live environments are ready

![Validate Connection](./assets/tavily_validate_connection.png)

2. Click the top menu to return to the main interface

### Step 3: Travel Planner Agent Creation
Use the **Agent Builder** to create a new agent:
- Name: `Travel_Planner_Agent`
- Configure behavior and workflow (as provided in the original guide)
- Include conversational prompts, greeting rules, and tool usage patterns.

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

### Step 4: Tool Configuration
### 4.1 Configure Tavily Search Tool

#### 4.1.1 Add MCP Server

1. Navigate to the **Tools** section within the agent page
2. Click **Add Tool** and select **MCP Server**

![Add Tool to Agent](./assets/agent_add_tool.png)
![Add Tool Options](./assets/agent_add_tool_2.png)
![MCP Server Selection](./assets/agent_add_tool_3.png)

3. Click **Add MCP Server**

![Add MCP Server](./assets/add_mcp.png)

#### 4.1.2 Configure Tavily Server

1. Select your `Tavily_MCP` connection from the list

![Configure Tavily](./assets/configure_travily.png)

2. Enter the command: `npx -y tavily-mcp@0.1.3`
3. Click **Connect**

![Tavily NPX Command](./assets/travily_npx.png)

4. Click **Done** to complete the server setup

![Tavily Done](./assets/Travily_done.png)

#### 4.1.3 Activate Tavily Search Tool

1. Identify the `tavily_search` tool in the available tools list
2. Switch the **Activation toggle** to **On**

![Tavily Search Tool](./assets/tavily_search.png)

3. Click **X** to close the server view

![Close Server View](./assets/close_server.png)

4. Verify the Tavily search tool is now added to your agent tools

![Tavily Edit Details](./assets/tavily_edit_details.png)

5. (Optional) Click the option menu to edit tool details

![Tavily Edit](./assets/taviliy_edit.png)

6. For this demo, we'll keep the default query parameters. Click **Cancel**

![Tavily Edit Save](./assets/tavily_edit_save.png)

**Success**: Tavily web search tool has been successfully added to your Travel Planner Agent.

### 4.2 Configure Airbnb Tools

#### 4.2.1 Add Airbnb MCP Server

1. Click **Add Tool** again

![Airbnb Add Tool](./assets/airbnb_add_tool.png)
![Add Tool Options](./assets/agent_add_tool_2.png)
![MCP Server Selection](./assets/agent_add_tool_3.png)

2. Click **Add MCP Server**

![Add MCP Server](./assets/add_mcp.png)

3. Configure the publicly available Airbnb MCP server:
   - **Server Name**: `Travel-Planner-Airbnb`
   - **Description**: `This is travel planner Airbnb server`
   - **Install command**: `npx -y @openbnb/mcp-server-airbnb --ignore-robots-txt`

![Airbnb Tool Connect](./assets/airbnb_tool_connect.png)

#### 4.2.2 Activate Airbnb Tools

1. Activate the available Airbnb tools from the server

![Airbnb Tools](./assets/airbnb_tools.png)

2. Verify all three tools are now configured in your Travel Planner Agent

![All Three Tools](./assets/airbnb_3_tools.png)

**Success**: Your Travel Planner Agent now has all required tools configured:
- Tavily Web Search
- Airbnb Search
- Airbnb Listing Details

### Step 5: Agent Testing
Open **Preview**, interact with the agent, and validate responses:
- Test greetings and behavior.
- Ensure Tavily and Airbnb tools work correctly.

### 5.1 Test Agent Functionality

1. Navigate to the **Preview** screen
2. Type a test message: `"Hello, how can you help me?"`

![Agent Testing](./assets/Agent_testing.png)

3. Verify the agent responds with the expected greeting and behavior

### 5.2 Validate Tool Integration

Test the agent with sample queries to ensure all tools are working:
- Destination research queries
- Accommodation search requests
- Combined travel planning requests

### Step 6: External Integration
Embed your agent in an external app:
### 6.1 Embed Agent in External Application

To integrate your agent into an external application:

1. Navigate to the **Channels** section within the Travel Planner agent page

![Travel Planner Embedded](./assets/Travel_planner_embeded.png)

2. Copy the **Orchestration ID** and **Agent ID** as shown

![Orchestration ID](./assets/orchestration_id.png)

3. Open the `travel_planner.html` file in a text editor
4. Update the script section with your orchestration and agent IDs

![Orchestration ID HTML](./assets/Orchestration_id_html.png)

### 6.2 Test External Integration

1. Open the HTML file in a web browser
2. Verify the agent is properly embedded and functional

![HTML Ready](./assets/html_ready.png)

### 6.3 Sample Test Scenarios

Test your Travel Planner Agent with these scenarios:

![Test Scenario 1](./assets/t1.png)
![Test Scenario 2](./assets/t2.png)
![Test Scenario 3](./assets/t3.png)
![Test Scenario 4](./assets/t4.png)
![Test Scenario 5](./assets/t5.png)

---

## 🧩 Examples

| Scenario | Example Query | Expected Outcome |
|-----------|----------------|------------------|
| Destination Research | “Plan a weekend trip to Paris” | Suggested attractions, local experiences, and weather |
| Accommodation Search | “Find me Airbnb stays in Goa under ₹5000 per night” | Filtered Airbnb listings |
| Combined Planning | “Plan a 5-day trip to Singapore for 2 adults” | Complete itinerary with hotels and attractions |

Example test screenshots:  
`t1.png`, `t2.png`, `t3.png`, `t4.png`, and `t5.png`.

---

## 💼 Business Value

The **Travel Planner Agent** demonstrates enterprise-grade AI orchestration.  

**Key Business Impacts:**
- Automates multi-source data integration  
- Enables AI-powered customer experience for travel or lifestyle domains  
- Serves as a reusable **building block** for other multi-agent scenarios  
- Highlights IBM watsonx Orchestrate’s potential for rapid automation  

---

## 🌍 Use Cases

- **Travel & Hospitality**: Automated itinerary creation  
- **AI Demonstrations**: Showcasing orchestration capabilities  
- **Customer Assistance**: 24/7 trip-planning conversational agent  
- **Education & Training**: Teaching GenAI orchestration principles  
- **Data Enrichment**: Combining structured (Airbnb) and unstructured (web) data  

---

## 🚀 Benefits

| Category | Description |
|-----------|-------------|
| **Automation** | Streamlines research and booking workflows |
| **Scalability** | Add new MCP servers easily |
| **Flexibility** | Works with both structured and unstructured data |
| **Engagement** | Offers personalized and dynamic responses |
| **Reusability** | Acts as a template for future multi-agent use cases |

---

## 🤝 Contributing

Contributions are welcome!  

To contribute:
1. Fork the repository  
2. Create a branch (`feature/new-tool-support`)  
3. Commit and push your changes  
4. Submit a pull request with a summary of updates  

Please include documentation and testing steps in your PR.

---

## ⚖️ License

This project is licensed under the **Apache 2.0 License**.  
See the [LICENSE](./LICENSE) file for details.

---

## 🧩 Additional Resources

- [IBM watsonx Orchestrate Documentation](https://developer.watson-orchestrate.ibm.com/)
- [Tavily API Documentation](https://docs.tavily.com/)
- [Airbnb MCP Server GitHub](https://github.com/openbnb/mcp-server-airbnb)
- [Model Context Protocol Servers](https://github.com/modelcontextprotocol/servers)

---

**Note:**  
This building block demonstrates how **multi-agent orchestration** can create intelligent, extensible conversational AI solutions that integrate external tools for real-world outcomes.
