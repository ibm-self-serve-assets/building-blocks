# IBM Watsonx Orchestrate AI Gateway: Extending Agents with Third-Party LLMs

IBM **Watsonx Orchestrate** provides a flexible and enterprise-ready framework to build, deploy, and manage AI agents. One of its most powerful features is the **AI Gateway**, which enables organizations to seamlessly connect **third-party Large Language Models (LLMs)** with IBM’s ecosystem.  

With AI Gateway, developers can use a **single orchestration layer** to integrate, manage, and govern models from providers such as OpenAI, Anthropic, Google, AWS Bedrock, Azure OpenAI, Mistral, Ollama, and IBM watsonx.ai. This helps enterprises build **trusted AI workflows** that are secure, scalable, and future-proof.  

--- 

## Why AI Gateway?

The **AI Gateway** serves as a **bridge** between IBM watsonx Orchestrate and external LLM providers, enabling:  

- **Multi-Provider Integration** – 10+ supported providers, including OpenAI, Anthropic, Google Gemini, Azure OpenAI, AWS Bedrock, watsonx.ai, and others  
- **Unified Credential Management** – API keys and tokens stored securely in **Watsonx connections**  
- **Routing Policies** – load balancing, failover, retries, and fallback across multiple LLMs  
- **Enterprise Security** – encrypted credentials, RBAC, and governance controls  
- **Flexible Configurations** – custom endpoints, request timeouts, and provider-specific settings  

[Learn more about supported providers →](https://developer.watson-orchestrate.ibm.com/llm/managing_llm#supported-providers)  

---

## Prerequisites

- Python **3.x**  
- Access to **[Watsonx Orchestrate SaaS](https://cloud.ibm.com/catalog/services/watsonx-orchestrate)**  
- Installed and configured **Watsonx Orchestrate ADK / CLI**  
- API key and model name for third-party LLMs (OpenAI, Anthropic Claude, Google Gemini, etc.)  

Install the ADK:  
```bash
pip install ibm-watsonx-orchestrate
```

Verify installation:  
```bash
orchestrate --version
```

---

## Step-by-Step: Third-Party LLM Integration

This guide covers integration for **OpenAI**, **Anthropic Claude**, and **Google Gemini**, but the same steps apply to all supported providers.  

---

### 1. Integrating OpenAI Models

#### Step 1: Configure Provider Settings  
Create a configuration JSON (excluding API key for security):  

```json
{
  "custom_host": "https://api.openai.com/v1",
  "request_timeout": 500
}
```

#### Step 2: Store API Key Securely  
[Generate OpenAI API key →](https://platform.openai.com/api-keys)  

```bash
orchestrate connections add -a openai_creds
orchestrate connections configure -a openai_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a openai_creds --env draft -e "api_key=sk-xxxx"
```

#### Step 3: Register the OpenAI Model  
```bash
orchestrate models add \
  --name openai/gpt-4 \
  --app-id openai_creds \
  --provider-config '{"custom_host": "https://api.openai.com/v1", "request_timeout": 5000}' \
  --type chat
```

#### Step 4: Verify Integration  
```bash
orchestrate models list
```

---

### 2. Integrating Anthropic Claude Models  

#### Step 1: Create Connection  
[Generate Anthropic API Key →](https://console.anthropic.com/login)  

```bash
orchestrate connections add -a anthropic_creds
orchestrate connections configure -a anthropic_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a anthropic_creds --env draft -e "api_key=YOUR_API_KEY"
```

#### Step 2: Define Model Specification (YAML)  

`config/anthropic-claude.yaml`  

```yaml
spec_version: v1
kind: model
name: anthropic/claude-3-7-sonnet
display_name: Anthropic Claude 3.7 Sonnet
description: Safe, reliable AI assistant from Anthropic
tags: [anthropic, claude]
model_type: chat
provider_config:
  anthropic_version: 2023-06-01
```

#### Step 3: Import Model  
```bash
orchestrate models import --file config/anthropic-claude.yaml --app-id anthropic_creds
```

---

### 3. Integrating Google Gemini Models  

#### Step 1: Create Connection  
[Generate Gemini API Key →](https://aistudio.google.com/)  

```bash
orchestrate connections add -a gemini_creds
orchestrate connections configure -a gemini_creds --env draft -k key_value -t team
orchestrate connections set-credentials -a gemini_creds --env draft -e "api_key=YOUR_API_KEY"
```

#### Step 2: Define Model Specification (YAML)  

`config/google-gemini.yaml`  

```yaml
spec_version: v1
kind: model
name: google/gemini-2.5-pro
display_name: Google Gemini 2.5 Pro
description: Google’s latest GenAI model for advanced reasoning
tags: [google, gemini]
model_type: chat
provider_config: {}
```

#### Step 3: Import Model  
```bash
orchestrate models import --file config/google-gemini.yaml --app-id gemini_creds
```

Navigate to connections from the UI's Agent Manager

<img width="1505" height="885" alt="1" src="https://github.com/user-attachments/assets/2898c5c5-b963-41f3-b913-4227553fb4f1" />

List of imported models

<img width="1508" height="645" alt="2" src="https://github.com/user-attachments/assets/e783bf3b-f7c7-4dc0-87a7-cb961e3ed1a9" />

---

## Validate the Integration

- **List all models**  
```bash
orchestrate models list
```

List of imported models in CLI

<img width="1219" height="405" alt="3" src="https://github.com/user-attachments/assets/4445f2f1-1ebc-41bc-9b3f-792ef9c669eb" />

Test the imported in watsonx orchestrate UI
1. Test the agent’s behavior, verifying that requests are routed to the external model
2. Monitor logs, API responses, latency, error rates
3. If needed, update the model spec (or connection) and re-import / re-add
4. Adjust model policies if you combine multiple models

<img width="1508" height="890" alt="4" src="https://github.com/user-attachments/assets/3b19a8fd-7cde-42e3-a392-33ce26308d17" />

- **Check in Watsonx Orchestrate UI**  
Models appear in the **Model Manager** dropdown.  
Agents can now be assigned third-party LLMs directly.  

---

## Advanced AI Gateway Features

- **Load Balancing & Fallback**  
```bash
orchestrate models policy add \
  --name balanced_gpt \
  --model openai/gpt-4 \
  --model openai/gpt-3.5-turbo \
  --strategy loadbalance \
  --retry-on-code 503 \
  --retry-attempts 3
```

- **Provider-Specific Options**  
  - Azure OpenAI → requires deployment ID, API version  
  - AWS Bedrock → supports IAM roles & regional endpoints  
  - watsonx.ai → integrates via project/space IDs  

[Read: Advanced model policies →](https://developer.watson-orchestrate.ibm.com/llm/model_policies)  

---

## Business Value & Benefits

The AI Gateway enables organizations to:  

1. **Future-Proof AI Strategy** → integrate any leading LLM provider without vendor lock-in  
2. **Enterprise Security** → centralized credential storage, encryption, and RBAC  
3. **Operational Resilience** → load balancing, failover, and fallback across models  
4. **Cost Optimization** → dynamically route requests to the most efficient model  
5. **Productivity Gains** → empower agents with the right LLM for each task  

---

## Example Use Cases  

- **Contact Center Automation** → fallback between Claude (safety) and GPT-4 (creativity)  
- **Knowledge Management** → agents dynamically query OpenAI for summarization and Gemini for reasoning  
- **Financial Services** → regulated workflows using watsonx.ai + external LLMs for contextual insights  
- **Multi-Agent Orchestration** → blend IBM Granite models with external LLMs inside a single workflow  

---

## Next Steps  

- Explore the [IBM AI Gateway Tutorial](https://developer.ibm.com/tutorials/ai-agents-llms-watsonx-orchestrate-ai-gateway/)  
- Try the [Multi-Model Orchestration Demo](https://medium.com/@IBMDeveloper/extend-your-ai-agents-with-external-llms-using-watsonx-orchestrate-and-ai-gateway-1cfaa9c0e304)  
- Build your own agents with **Watsonx Orchestrate ADK** and connect them to external LLMs  

---

## License  
This project is licensed under the **Apache 2.0 License**.  
