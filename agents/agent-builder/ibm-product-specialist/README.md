# IBM Orchestarte Agentic Product Specialist Demo

This lab guides you through creating a multi-agent workflow using Watsonx Orchestrate to collect and aggregate information from various IBM products. We will set up multiple agents that collaborate in a distributed manner, and use the Watsonx Orchestrate ADK (Automation Development Kit) to orchestrate their interaction.

By the end of this tutorial, you will have a complete setup where a main agent coordinates the execution of various collaborator agents responsible for specific tasks. This allows us to automate the collection, processing, and aggregation of IBM product data using Watsonx Orchestrate’s intelligent automation and multi-agent capabilities.

The **IBM Product Specialist** is an AI-driven asset built using **Watsonx Orchestrate**.  
It acts as an intelligent product expert, leveraging agents to answer questions related to IBM products.  
Currently, it supports three primary IBM products:  
1. **Watsonx Orchestrate**  
2. **Watsonx Assistant**  
3. **Cognos Analytics**  
4. **Watsonx AI**  
5. **Watsonx Code Assistant**  


This project aims to enhance customer support by providing quick, accurate answers related to these IBM products.  
The supervisory agent, **IBM Product Specialist**, intelligently redirects user questions to the appropriate sub-agent.  

---

## Prerequisites

- Access to IBM Watsonx Orchestrate.
- IBM watsonx Agentic Development Kit (ADK).
- Python 3.x

## Architecture
![Orchestrate Assets_2025-05-20_14-13-02](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/e2ad8a7f-b0a4-4303-aa27-101aa51b03b7)

### Working Mechanism
The **IBM Product Specialist** serves as the supervisory agent that directs all incoming user queries to relevant product-specific sub-agents.  
The system comprises the following sub-agents:  
- **Wx_Orchestrate**  
- **Cognos_Analytics**  
- **Wx_Assistant**  
- **Wx_AI**  
- **Wx_Code_Assistant**  

#### Flow
1. **User Query**  
2. **IBM Product Specialist analyzes**  
3. **Decides the best sub-agent**  
4. **Sub-agent retrieves information**  
5. **Response is sent to the user.**  

### Project Structure

```bash

├── agents/                          
│   ├── agent-builder/              
│   │   ├── ibm_product_specialist/ 
│   │   │   ├── agents/ 
│   │   │   │   └── cognos_analytics_agent.yaml 
│   │   │   │   └── ibm_product_specialist.yaml 
│   │   │   │   └── wx_ai_agent.yaml 
│   │   │   │   └── wx_assistant_agent.yaml 
│   │   │   │   └── wx_code_assistant_agent.yaml 
│   │   │   │   └── wxo_agent.yaml
│   │   │   ├── tools/ 
│   │   │   │   └── cognos_analytics/ 
│   │   │   │       └── *.py 
│   │   │   │   └── wx.ai/ 
│   │   │   │       └── *.py 
│   │   │   │   └── wx.assistant/
│   │   │   │       └── *.py
│   │   │   │   └── wx.code_assistant/ 
│   │   │   │       └── *.py 
│   │   │   │   └── wxo/ 
│   │   │   │       └── *.py  
│   │   │   └── README.md  
│   │   └── requirements.txt 
│   ├── AI_Gateway/  
│   │   ├── config/  
│   │   │    ├── anthropic-claude.yaml 
│   │   │    ├── google-genai.yaml
│   │   └── README.md 
│   └── README.md 
├── .gitignore
├── LICENSE
└── requirements.txt
```

## Getting Started

## Sub Agents and Associated Tools

In IBM Watsonx Orchestrate, agents and tools are connected using a structured and modular approach that allows for dynamic task execution. Tools are the functional units (like scripts, APIs, or prebuilt automations), while agents are intelligent entities that use those tools to complete tasks based on goals or inputs.

Here's how the connection between tools and agents works in Watsonx Orchestrate:

1. Conceptual Overview

| Component | Description | Example |
|-----------|-------------|---------|
| Agent     | Orchestrates tasks by invoking tools. | wx_ai_agent |
| Tool      | Performs a specific function like scraping data from watsonx.ai. | get_wxai_info.py |
| Action    | An instruction inside the agent that tells it when and how to use a tool. | Call `get_wxai_info` with URL input |


The watsonx Orchestrate Agents do not contain code — they call tools through defined actions.
Tools are registered and described using the ADK (Agent Development Kit), and they can be reused across agents.
In this case, it fetches and extracts text content from the various IBM watsonx product pages and provides a consolidated information based on the user requests.

## Building the Agents and tools

- Step 1: Define the Agent in YAML
- Step 2: Create the Python Tool
- Step 3: Register the Tool.

### Step 1: Define the Agent in YAML

Create a agent with instruction and attach tools associated with it:e.g: agents/wx_ai_agent.yaml
or 
refer to the already created `tools/` and `agents/` available.

```bash
# agents/wx_ai_agent.yaml

spec_version: v1
style: default
name: Agent_Name
llm: model_id
description: 
  You are IBM Watsonx AI product Specialist and have expert in the product.
  
instructions: 
  Please use below tools to fetch relevant information to answer the questions.
  get_wxai_info - This tool provides high level infomation about Watsonx AI.
  get_wxai_pricing - This tool provides details about the pricing details for Watsonx AI.
  Note-
    - Sometime you may need to use multiple tools to fetch the answer.
    - If question is relevant, then always transfer_to_supervisor.
  Use this information as the context to answer the user’s question, determining whether the question’s statement is correct or incorrect. 
  Format the response in a conversational tone, using a markdown table if the question requires fact validation. Do not expand speciality acronyms.
  
tools:
  - get_wxo_info
  - get_wxai_pricing
```


### Step 2: Create the Python Tool

Create a Python file, e.g., tools/wx.ai/get_wxai_info.py, and define your tool using the @tool decorator.
The python function fetches and extracts text content from the IBM Watsonx AI webpage and return it to the main agent.

### Wx_Orchestrate  
This agent answers questions related to **Watsonx Orchestrate**.  
It uses the following tools to fetch relevant information:  
- `get_wxo_info` - Provides high-level information about Watsonx Orchestrate.  
- `get_wxo_features` - Details about the features of Watsonx Orchestrate.  
- `get_wxo_integration` - Provides integration details for Watsonx Orchestrate.  
- `get_wxo_pricing` - Offers pricing details for Watsonx Orchestrate.  
- `get_wxo_resources` - Lists all resources related to Watsonx Orchestrate.  

---

### Wx_Assistant  
This agent answers questions related to **Watsonx Assistant**.  
It uses the following tools to fetch relevant information:  
- `get_wx_assistant_info` - Provides high-level information about Watsonx Assistant.  
- `get_wx_assistant_features` - Details about the features of Watsonx Assistant.  
- `get_wx_assistant_pricing` - Offers pricing details for Watsonx Assistant.  
- `get_wx_assistant_resources` - Lists all resources related to Watsonx Assistant.  

---

### Cognos_Analytics  
This agent answers questions related to **Cognos Analytics**.  
It uses the following tools to fetch relevant information:  
- `get_cognos_info` - Provides high-level information about Cognos Analytics.  
- `get_cognos_features` - Details about the features of Cognos Analytics.  
- `get_cognos_pricing` - Offers pricing details for Cognos Analytics.  
- `get_cognos_resources` - Lists all resources related to Cognos Analytics.  

### Wx_AI  
This agent answers questions related to **Watsonx AI**.  
It uses the following tools to fetch relevant information:  
- `get_wxai_info` - This tool provides high level infomation about Watsonx AI.
- `get_wxai_agent_development` - This tool provides details about the agent development features for Watsonx AI.
- `get_wxai_knowledge_management` - This tool provides details about the knowledge management feature details for Watsonx AI.
- `get_wxai_model_customization` - This tool provides details about the model customization features for Watsonx AI.
- `get_wxai_rag_development` - This tool provides details about the rag development details for Watsonx AI.
- `get_wxai_model_library` - This tool provides details about all the model resources of Watsonx AI.
- `get_wxai_pricing` - This tool provides details about the pricing details for Watsonx AI.

### Wx_Code_Assistant
This agent answers questions related to **Watsonx Code Assistant**.  
It uses the following tools to fetch relevant information:  
- `get_wxca_info` - This tool provides high level infomation about Watsonx Code Assistant.
- `get_wxca_pricing` - This tool provides details about the pricing details for Watsonx Code Assistant. 

---

### Tools Working Mechanism
- Real-time data gathering via web crawling.  
- Fetches relevant data from IBM websites for accurate answers.  
- The tools utilize APIs and web scraping to gather the latest product information.  

---

## Step 3: Register the Tool

### Install IBM watsonx orchestrate ADK

Install IBM orchestrate ADK
```bash
pip3 install ibm-watsonx-orchestrate 
```
Create an environment in ADK, copy the instance url from the IBM Orchestrate launch page. 
(Ask your instructor for help)

```bash
orchestrate env add -n <ENV_NAME> -u <IBM_ORCHESTRATE_INSTANCE_URL> --iam-url <IAM_URL>
```
Activate the environment
```bash
orchestrate env activate <ENV_NAME> -a <API_KEY>
```

### Adding Cognos Tools

Proceed with the below steps once the environment is activated.

```bash
orchestrate tools import -k python -f tools/cognos_analytics/get_cognos_features.py -r requirements.txt
orchestrate tools import -k python -f tools/cognos_analytics/get_cognos_info.py -r requirements.txt
orchestrate tools import -k python -f tools/cognos_analytics/get_cognos_pricing.py -r requirements.txt
orchestrate tools import -k python -f tools/cognos_analytics/get_cognos_resources.py -r requirements.txt
```

### Adding Wx Assistant Tools
```bash
orchestrate tools import -k python -f tools/wx.assistant/get_wx_assistant_features.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.assistant/get_wx_assistant_info.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.assistant/get_wx_assistant_pricing.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.assistant/get_wx_assistant_resources.py -r requirements.txt
```

### Adding Wx Orchestrate Tools
```bash
orchestrate tools import -k python -f tools/wxo/get_wxo_features.py -r requirements.txt
orchestrate tools import -k python -f tools/wxo/get_wxo_info.py -r requirements.txt
orchestrate tools import -k python -f tools/wxo/get_wxo_integration.py -r requirements.txt
orchestrate tools import -k python -f tools/wxo/get_wxo_pricing.py -r requirements.txt
orchestrate tools import -k python -f tools/wxo/get_wxo_resources.py -r requirements.txt
```

### Adding Wx AI Tools
```bash
orchestrate tools import -k python -f tools/wx.ai/get_wxai_agent_development.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_info.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_knowledge_management.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_model_customization.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_model_library.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_pricing.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.ai/get_wxai_rag_development.py -r requirements.txt
```

### Adding Wx Code Assistant Tools
```bash
orchestrate tools import -k python -f tools/wx.code_assistant/get_wxca_info.py -r requirements.txt
orchestrate tools import -k python -f tools/wx.code_assistant/get_wxca_pricing.py -r requirements.txt
```

### Adding Agents
```bash
orchestrate agents import -f agents/cognos_analytics_agent.yaml
orchestrate agents import -f agents/wxo_agent.yaml
orchestrate agents import -f agents/wx_assistant_agent.yaml
orchestrate agents import -f agents/ibm_product_specialist.yaml
orchestrate agents import -f agents/wx_ai_agent.yaml
orchestrate agents import -f agents/wx_code_assistant_agent.yaml
```

### Starting the Chat Server
```bash
orchestrate chat start
```

### Configuring Agents on UI
1. Open the chat server UI.
2. Navigate to Manage Agents.
3. Select IBM Product Specialist.
4. Click on Add Agents and add the sub-agents:
    - Wx_Orchestrate
    - Wx_Assistant
    - Cognos_Analytics
    - Wx_AI
    - Wx_Code_Assistant
5. Verify the master agent setup.
   ![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/31c78cb7-3bc7-423c-bbc0-165dc8ae31d7)


### How to Use
- Once the setup is complete, you can ask questions related to IBM products:
    - Watsonx Orchestrate
    - Watsonx Assistant
    - Cognos Analytics
    - Watsonx AI
    - Watsonx Code Assistant
- The master agent will dynamically choose the appropriate sub-agent to fetch the correct response.
- You can extend the agent setup to support additional IBM products by adding new sub-agents.
- 

---
### In Action
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/34f61627-af29-4cfb-987e-62f64c5230bc)
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/65697f82-a20e-4b0f-9cb9-c29475d99bda)
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/26ec4ae4-c98b-4850-9a54-505f901bac43)
<img width="869" alt="image" src="https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/a6972bb3-baa8-4e97-a9d9-16238cb0b1d8">

## Conclusion

By following this lab, you’ve created a multi-agent workflow in Watsonx Orchestrate to collect and process data from various IBM product web pages. You’ve learned how to:
- Set up a Main Agent that orchestrates tasks across multiple agents.
- Use Collaborator Agents for scraping, processing, and aggregating data.
- Leverage the Watsonx Orchestrate ADK for seamless automation of multi-agent workflows.

This setup can be adapted to a variety of use cases, such as product comparison engines, market research tools, and e-commerce aggregators. Watsonx Orchestrate’s robust multi-agent support allows you to scale and automate tasks efficiently while maintaining flexibility and control over the workflow.

