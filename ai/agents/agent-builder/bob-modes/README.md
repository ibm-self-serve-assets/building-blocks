# Bob Modes for Agent Builder

Custom IBM Bob mode configurations for building, testing, and integrating AI agents using **IBM watsonx Orchestrate** and the **Agentic Development Kit (ADK)**.

---

## Overview

These Bob modes provide specialized personas and tailored tool permissions for agent development workflows:

- **Agent Builder Base Mode**: Foundation mode for building and testing autonomous agents with the watsonx Orchestrate ADK.
- **Domain Agent Builder**: Build domain-specific agents (healthcare, retail, finance, HR, IT) with custom tools and RAG knowledge bases.
- **Voice Agent Builder**: Configure and deploy voice-enabled agents with STT/TTS channels (phone, WhatsApp, SMS, Slack).
- **Agent REST Integration**: Connect agents to external enterprise systems and web applications via REST APIs.

---

## Included Modes

| Mode | Location | Type | Description |
|---|---|---|---|
| `agent-builder-base-mode` | [`base-modes/agent-builder-base-mode.zip`](base-modes/agent-builder-base-mode.zip) | Base Mode | Core agent building, ADK commands, and prompt authoring |
| `domain-agent-builder` | [`custom-modes/domain-agent-builder.zip`](custom-modes/domain-agent-builder.zip) | Custom Mode | Domain-specific agents with custom tools and knowledge bases |
| `voice-agent-builder` | [`custom-modes/voice-agent-builder.zip`](custom-modes/voice-agent-builder.zip) | Custom Mode | Voice agent setup with telephony and audio channel pipelines |
| `agent-rest-integration` | [`custom-modes/agent-rest-integration.zip`](custom-modes/agent-rest-integration.zip) | Custom Mode | Application integration via watsonx Orchestrate REST APIs |

---

## Installing Bob Modes

### For New Projects

1. Download and extract the desired mode `.zip` file from `base-modes/` or `custom-modes/`.
2. Copy the `.bob/` folder into your project root:
   ```text
   your-project/
   ├── .bob/
   │   ├── custom_modes.yaml
   │   └── rules/
   │       └── [mode-name]/
   └── [project files]
   ```
3. Restart or reload IBM Bob and select the mode in the **Modes / Custom Modes** selector.

### For Existing Projects

If your project already contains `.bob/custom_modes.yaml`:

1. **Do not overwrite** existing `custom_modes.yaml` files.
2. Open your `.bob/custom_modes.yaml` and append the new mode entries from the extracted mode.
3. Copy the extracted rule folder into `.bob/rules/<mode-name>/`.
4. Reload IBM Bob to activate.

---

## Prerequisites

- IBM Bob IDE / Extension installed
- Python 3.10+ with `uv` or `pip`
- IBM watsonx Orchestrate instance and API credentials
