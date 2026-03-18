# 🚀 Agent Gateway Bob Modes - Setup Guide

This directory contains custom Bob modes for integrating third-party LLM models into watsonx Orchestrate via the AI Gateway. Follow the instructions below to import and use these modes in your Bob projects.

## 📦 Available Modes

### Base Mode
- **agent-model-gateway-bob-mode** - Comprehensive mode for integrating third-party LLM models (OpenAI, Anthropic, Google, Azure, AWS Bedrock, and more) into watsonx Orchestrate

💡 **Tip:** If you're viewing this on GitHub, you can download the .zip file directly by clicking the link in the main [Agent Gateway README](../../README.md).

---

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes. You can directly add the agent gateway mode.

### 📁 Add Mode Configuration

1. **Download and extract** the mode's `.zip` file from the `base-modes/` folder
2. **Open your project** in Bob UI
3. **Navigate** to the project workspace (file explorer)
4. **Copy the `.bob` folder** from the extracted mode:

```
.bob/
├── custom_modes.yaml
└── rules/
    └── agent-gateway/
        └── [mode rules files]
```

5. **Paste** the `.bob/` directory into your project root
6. The structure should look like:

```
your-project/
├── .bob/
│   ├── custom_modes.yaml
│   └── rules/
│       └── agent-gateway/
└── [your project files]
```

---

### ▶️ Start Using the Mode

- Refresh or reload the Bob UI (if required)
- Navigate to **Modes / Custom Modes section**
- Select the agent gateway mode you installed
- Start using it in your workflows

---

## 🔁 For Existing Projects

If your project already has custom modes configured, follow these steps carefully to avoid breaking existing setups.

---

### ⚠️ Do Not Overwrite Existing Configuration

- Do **not replace** the existing `.bob/custom_modes.yaml`
- This file may already contain active modes used by your project

---

### ✏️ Append New Mode Configuration

1. **Download and extract** the mode's `.zip` file
2. **Open** `.bob/custom_modes.yaml` in the Bob UI editor
3. **Add** the agent gateway mode at the end of the file

#### Example:

```yaml
# Existing custom modes
- slug: existing-mode-1
  name: Existing Mode 1
  # ... existing configuration ...

- slug: existing-mode-2
  name: Existing Mode 2
  # ... existing configuration ...

# Add agent gateway mode
- slug: agent-gateway
  name: 🌉 Agent Model Gateway
  # ... new mode configuration ...
```

---

### 📂 Maintain Rules Folder Structure

1. **Navigate** to `.bob/rules/`
2. **Add** the new rules folder from the extracted mode
3. **Ensure** the final structure looks like:

```
.bob/
├── custom_modes.yaml
└── rules/
    ├── existing-mode-1/
    ├── existing-mode-2/
    └── agent-gateway/
```

👉 Do **not modify or delete existing rule folders**

---

### ✅ Verify in Bob UI

After completing the setup:

- Go to **Modes / Custom Modes**
- Confirm:
  - Existing modes are still available
  - Agent gateway mode appears
- Open the mode and ensure no configuration errors are shown

---

## 🧠 Best Practices

- Always **append**, never overwrite `custom_modes.yaml`
- Keep each mode isolated under its own rules folder
- Validate YAML formatting carefully (indentation matters)
- Reload the UI if changes are not reflected immediately
- Review the mode-specific documentation for prerequisites and usage instructions

---

## 📚 What This Mode Does

The **Agent Model Gateway** mode provides:

### Interactive Model Integration
- Streamlined workflow for integrating external LLM models
- Documentation-driven approach ensuring best practices
- Step-by-step guidance for secure credential management

### Multi-Provider Support
- **OpenAI** - GPT-4, GPT-3.5, and other OpenAI models
- **Anthropic** - Claude 3.7 Sonnet and other Claude models
- **Google** - Gemini 2.5 Pro and other Gemini models
- **Azure OpenAI** - Azure-hosted OpenAI models
- **AWS Bedrock** - Amazon's managed foundation models
- **IBM watsonx.ai** - IBM's enterprise AI models
- And many more providers

### Enterprise-Grade Features
- Secure credential storage in watsonx connections
- Model configuration via YAML specifications
- Validation and testing workflows
- Production-ready integrations

---

## 🔧 Prerequisites

Before using this mode, ensure you have:

### Required
- **IBM Bob** - Latest version
- **watsonx Orchestrate ADK**: `pip install ibm-watsonx-orchestrate`
- **Python 3.x**
- **watsonx Orchestrate environment** with access
- **API keys** for the LLM providers you want to integrate

### Recommended
- Familiarity with watsonx Orchestrate CLI commands
- Understanding of YAML configuration files
- Access to provider documentation for API key generation

---

## 🎯 What You Can Build

With this mode, you can:

### Model Integration
- Connect OpenAI GPT models to watsonx Orchestrate
- Integrate Anthropic Claude for safe, reliable AI
- Add Google Gemini for advanced reasoning tasks
- Configure Azure OpenAI with deployment-specific settings
- Set up AWS Bedrock models with IAM roles
- Use IBM watsonx.ai models alongside external providers

### Advanced Gateway Features
- Configure load balancing across multiple models
- Set up failover and retry policies
- Implement model routing strategies
- Monitor model performance and costs
- Manage credentials securely

### Enterprise Workflows
- Build multi-model agent systems
- Create cost-optimized routing policies
- Implement compliance-aware model selection
- Set up regional model deployments

---

## 💡 Quick Start Tips

1. **Gather API keys first** - Have your provider API keys ready before starting
2. **Start with one provider** - Test with a single model before adding more
3. **Follow the workflow** - Bob will guide you through each step
4. **Test thoroughly** - Validate each integration before moving to production
5. **Review documentation** - Check provider-specific requirements and limits

---

## 📖 Usage Examples

### Integrating OpenAI Models
```
"Help me integrate OpenAI GPT-4 into watsonx Orchestrate"
"Set up OpenAI connection with my API key"
"Create a model configuration for GPT-3.5-turbo"
```

### Integrating Anthropic Claude
```
"Integrate Anthropic Claude 3.7 Sonnet"
"Configure Claude with my Anthropic API key"
"Set up Claude for safe, reliable AI responses"
```

### Integrating Google Gemini
```
"Add Google Gemini 2.5 Pro to my gateway"
"Configure Gemini for advanced reasoning tasks"
"Set up Google AI Studio connection"
```

### Advanced Configuration
```
"Set up load balancing between GPT-4 and Claude"
"Create a failover policy for model reliability"
"Configure retry logic for API timeouts"
```

---

## 🎯 Outcome

After completing these steps:

- Agent gateway mode will be available in Bob UI
- Existing modes (if any) will continue to function without disruption
- You can start integrating third-party LLM models into watsonx Orchestrate
- Bob will guide you through secure, production-ready model integrations

---

## 🆘 Need Help?

- Review the [Model Gateway Guide](../../assets/model-gateway-guide/) for detailed integration examples
- Check provider documentation for API key generation and requirements
- Ensure all prerequisites are installed before starting
- Verify your watsonx Orchestrate environment is properly configured
- Test connections and credentials before deploying to production

---

## 📚 Additional Resources

- [IBM AI Gateway Tutorial](https://developer.ibm.com/tutorials/ai-agents-llms-watsonx-orchestrate-ai-gateway/)
- [Multi-Model Orchestration Demo](https://medium.com/@IBMDeveloper/extend-your-ai-agents-with-external-llms-using-watsonx-orchestrate-and-ai-gateway-1cfaa9c0e304)
- [watsonx Orchestrate ADK Documentation](https://developer.watson-orchestrate.ibm.com/)
- [Supported LLM Providers](https://developer.watson-orchestrate.ibm.com/llm/managing_llm#supported-providers)