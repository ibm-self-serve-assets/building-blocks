# 🚀 Agent Builder Bob Modes - Setup Guide

This directory contains custom Bob modes for building agents in watsonx Orchestrate. Follow the instructions below to import and use these modes in your Bob projects.

## 📦 Available Modes

### Base Mode
- **agent-builder-base-mode** - Foundation mode for agent building workflows

### Custom Modes
- **domain-agent-builder** - Build domain-specific agents (healthcare, retail, finance, etc.) with tools and RAG capabilities
- **voice-agent-builder** - Build voice-enabled agents with multi-channel support (phone, WhatsApp, SMS, Slack)

---

## 🆕 For New Projects

When working with a **new project**, there are no existing custom modes. You can directly add any agent builder mode.

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
- Select the agent builder mode you installed
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
3. **Add** the new agent builder mode at the end of the file

#### Example:

```yaml
# Existing custom modes
- slug: existing-mode-1
  name: Existing Mode 1
  # ... existing configuration ...

- slug: existing-mode-2
  name: Existing Mode 2
  # ... existing configuration ...

# Add new agent builder mode
- slug: domain-agent-builder
  name: 🤖 Domain Agent Builder
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
    └── [new-agent-builder-mode]/
```

👉 Do **not modify or delete existing rule folders**

---

### ✅ Verify in Bob UI

After completing the setup:

- Go to **Modes / Custom Modes**
- Confirm:
  - Existing modes are still available
  - New agent builder mode appears
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

- **Domain Agent Builder**: See `agent-builder-bob-modes/custom-modes/domain-agent-builder/README.md`
  - Prerequisites: Bob, uv/uvx, WXO API key
  - Builds tool-augmented agents with RAG for any domain
  
- **Voice Agent Builder**: See `agent-builder-bob-modes/custom-modes/voice-agent-builder/README.md`
  - Prerequisites: Bob, ADK access, channel credentials
  - Builds voice-enabled agents with multi-channel support

---

## 🎯 Outcome

After completing these steps:

- Your chosen agent builder mode will be available in Bob UI
- Existing modes (if any) will continue to function without disruption
- You can start building agents using the imported mode
- Follow the mode-specific README for detailed usage instructions

---

## 💡 Quick Start Tips

1. **Start with base mode** if you're new to agent building
2. **Choose domain-agent-builder** for text-based agents with custom tools
3. **Choose voice-agent-builder** for voice-enabled, multi-channel agents
4. **Read mode-specific READMEs** before starting your first agent build
5. **Enable auto-approve** in Bob UI for smoother workflows (except for questions)

---

## 🆘 Need Help?

- Check the mode-specific README files for detailed instructions
- Review the example agents included in each mode
- Ensure all prerequisites are installed before starting
- Verify your API keys and credentials are correctly configured
