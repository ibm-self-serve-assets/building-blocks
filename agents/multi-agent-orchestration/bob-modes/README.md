# 🚀 Multi-Agent Orchestration Bob Modes - Setup Guide

This directory contains custom Bob modes for building multi-agent orchestration systems with watsonx Orchestrate. Follow the instructions below to import and use these modes in your Bob projects.

## 📦 Available Modes

### Base Mode
- **multi-agent-orchestration-base-mode** - Foundation mode for building production-grade AI agents, MCP servers, and multi-agent workflows

### Custom Modes
- **agent-model-gateway-bob-mode** - Comprehensive mode for integrating third-party LLM models into watsonx Orchestrate via the AI Gateway

---

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes. You can directly add any multi-agent orchestration mode.

### 📁 Add Mode Configuration

1. **Download and extract** the desired mode's `.zip` file from the `base-modes/` or `custom-modes/` folder
2. **Open your project** in Bob UI
3. **Navigate** to the project workspace (file explorer)
4. **Copy the `.bob` folder** from the extracted mode:

```
.bob/
├── custom_modes.yaml
└── rules/
    └── [mode-name]/
        └── [mode rules files]
```

5. **Paste** the `.bob/` directory into your project root
6. The structure should look like:

```
your-project/
├── .bob/
│   ├── custom_modes.yaml
│   └── rules/
│       └── [mode-name]/
└── [your project files]
```

---

### ▶️ Start Using the Mode

- Refresh or reload the Bob UI (if required)
- Navigate to **Modes / Custom Modes section**
- Select the multi-agent orchestration mode you installed
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

1. **Download and extract** the desired mode's `.zip` file
2. **Open** `.bob/custom_modes.yaml` in the Bob UI editor
3. **Add** the new multi-agent orchestration mode at the end of the file

#### Example:

```yaml
# Existing custom modes
- slug: existing-mode-1
  name: Existing Mode 1
  # ... existing configuration ...

- slug: existing-mode-2
  name: Existing Mode 2
  # ... existing configuration ...

# Add new multi-agent orchestration mode
- slug: multi-agent-orchestration
  name: 🤖 Multi-Agent Orchestration
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
    └── [new-multi-agent-mode]/
```

👉 Do **not modify or delete existing rule folders**

---

### ✅ Verify in Bob UI

After completing the setup:

- Go to **Modes / Custom Modes**
- Confirm:
  - Existing modes are still available
  - New multi-agent orchestration mode appears
- Open the mode and ensure no configuration errors are shown

---

## 🧠 Best Practices

- Always **append**, never overwrite `custom_modes.yaml`
- Keep each mode isolated under its own rules folder
- Validate YAML formatting carefully (indentation matters)
- Reload the UI if changes are not reflected immediately
- Review each mode's specific README for prerequisites and usage instructions

---

## 📚 Mode-Specific Documentation

Each mode has its own detailed README with specific instructions:

- **Multi-Agent Orchestration Base Mode**: See `multiagent-orchestration-bob-modes/base-modes/README.md`
  - Prerequisites: watsonx Orchestrate ADK, Python 3.10+, MCP SDK
  - Builds production-grade AI agents and MCP servers
  - Supports watsonx Orchestrate agent development
  - Includes MCP server development capabilities
  
- **Agent Model Gateway Mode**: See `multiagent-orchestration-bob-modes/custom-modes/agent-model-gateway-bob-mode/README.md`
  - Prerequisites: Bob, watsonx Orchestrate access, third-party LLM API keys
  - Integrates external models (OpenAI, Anthropic, Google) into watsonx Orchestrate

---

## 🎯 Outcome

After completing these steps:

- Your chosen multi-agent orchestration mode will be available in Bob UI
- Existing modes (if any) will continue to function without disruption
- You can start building agents, MCP servers, and orchestration systems using the imported mode
- Follow the mode-specific README for detailed usage instructions

---

## 💡 Quick Start Tips

1. **Start with base mode** if you're new to multi-agent orchestration
2. **Choose agent-model-gateway-bob-mode** for integrating third-party LLM models
3. **Read mode-specific READMEs** before starting your first project
4. **Install prerequisites** (ADK, MCP SDK) before using the modes
5. **Enable auto-approve** in Bob UI for smoother workflows (except for questions)

---

## 🆘 Need Help?

- Check the mode-specific README files for detailed instructions
- Review the example projects included in each mode
- Ensure all prerequisites are installed before starting
- Verify your API keys and credentials are correctly configured
- Visit the watsonx Orchestrate documentation at https://developer.watson-orchestrate.ibm.com/