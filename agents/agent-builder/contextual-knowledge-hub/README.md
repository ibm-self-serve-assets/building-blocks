# IBM Product Specialist

## Overview
The **IBM Product Specialist** is an AI-driven asset built using **Watsonx Orchestrate**.  
It acts as an intelligent product expert, leveraging agents to answer questions related to IBM products.  
Currently, it supports three primary IBM products:  
1. **Watsonx Orchestrate**  
2. **Watsonx Assistant**  
3. **Cognos Analytics**  

This project aims to enhance customer support by providing quick, accurate answers related to these IBM products.  
The supervisory agent, **IBM Product Specialist**, intelligently redirects user questions to the appropriate sub-agent.  

---

## Features

- **Centralized Knowledge Base:**  
  The supervisory agent acts as a single entry point for product-related inquiries.

- **Multi-Agent Architecture:**  
  Efficiently divides tasks between specialized agents for each product.

- **Dynamic Information Retrieval:**  
  Uses web crawling to fetch up-to-date information from IBM's official website.  

- **Easy Integration:**  
  Plug-and-play architecture to easily add more product-specific agents.

- **Modular Design:**  
  Supports extending the product catalog with minimal changes.  

---

## Use Cases

- **Customer Support Automation:**  
  Quickly answer customer queries related to IBM products.  

- **Product Information Assistance:**  
  Provide detailed insights, features, pricing, and integration options for IBM tools.  

- **Internal Helpdesk for Enterprises:**  
  Help employees get the latest information about IBM products.  

- **Sales and Marketing Assistance:**  
  Enable product specialists to respond to client questions accurately.  

---

## Architecture
![Orchestrate Assets_2025-05-20_14-13-02](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/e2ad8a7f-b0a4-4303-aa27-101aa51b03b7)

### Working Mechanism
The **IBM Product Specialist** serves as the supervisory agent that directs all incoming user queries to relevant product-specific sub-agents.  
The system comprises the following sub-agents:  
- **Wx_Orchestrate**  
- **Cognos_Analytics**  
- **Wx_Assistant**  

#### Flow
1. **User Query**  
2. **IBM Product Specialist analyzes**  
3. **Decides the best sub-agent**  
4. **Sub-agent retrieves information**  
5. **Response is sent to the user.**  


## Sub Agents and Associated Tools

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

---

### Tools Working Mechanism
- Real-time data gathering via web crawling.  
- Fetches relevant data from IBM websites for accurate answers.  
- The tools utilize APIs and web scraping to gather the latest product information.  

---

## Installation and Setup

### Prerequisites
- Python 3.x  
- Watsonx Orchestrate  ADK

### Adding Cognos Tools
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

### Adding Agents
```bash
orchestrate agents import -f agents/cognos_analytics_agent.yaml
orchestrate agents import -f agents/wxo_agent.yaml
orchestrate agents import -f agents/wx_assistant_agent.yaml
orchestrate agents import -f agents/ibm_product_specialist.yaml
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
5. Verify the master agent setup.
   ![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/31c78cb7-3bc7-423c-bbc0-165dc8ae31d7)


### How to Use
- Once the setup is complete, you can ask questions related to IBM products:
    - Watsonx Orchestrate
    - Watsonx Assistant
    - Cognos Analytics
- The master agent will dynamically choose the appropriate sub-agent to fetch the correct response.
- You can extend the agent setup to support additional IBM products by adding new sub-agents.
- 

---
### In Action
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/34f61627-af29-4cfb-987e-62f64c5230bc)
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/65697f82-a20e-4b0f-9cb9-c29475d99bda)
![image](https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/26ec4ae4-c98b-4850-9a54-505f901bac43)
<img width="869" alt="image" src="https://github.ibm.com/Dheeraj-Arremsetty/wx.orchestrate-Agents-Builder-Library/assets/195534/a6972bb3-baa8-4e97-a9d9-16238cb0b1d8">

