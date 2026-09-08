# Bob Modes for Multi-Agent Orchestration

Custom IBM Bob mode configurations for orchestrating multi-agent systems, designing agent flows, and integrating Model Context Protocol (MCP) servers on **IBM watsonx Orchestrate**.

---

## Overview

These Bob modes provide specialized assistance for designing and executing distributed multi-agent systems:

- **Multi-Agent Orchestration Base Mode**: Foundation mode for defining coordinator agents, task delegation strategies, shared context, and agent-to-agent (A2A) communication.
- **Agent Model Gateway Mode**: Configure agent routing through the watsonx.ai AI Gateway for load balancing, multi-model fallback, and rate limiting.

---

## Included Modes

| Mode | Location | Type | Description |
|---|---|---|---|
| `multi-agent-orchestration-base-mode` | [`base-modes/multi-agent-orchestration-base-mode.zip`](base-modes/multi-agent-orchestration-base-mode.zip) | Base Mode | Multi-agent coordination, A2A routing, and MCP server configuration |
| `agent-model-gateway-bob-mode` | [`custom-modes/agent-model-gateway-bob-mode.zip`](custom-modes/agent-model-gateway-bob-mode.zip) | Custom Mode | watsonx.ai Model Gateway integration and multi-agent routing policies |

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
2. Open your `.bob/custom_modes.yaml` and append the new mode configuration.
3. Copy the extracted rule folder into `.bob/rules/<mode-name>/`.
4. Reload IBM Bob to activate.

---

## Prerequisites

- IBM Bob IDE / Extension installed
- Python 3.10+ / Node.js (for MCP servers)
- IBM watsonx Orchestrate instance credentials
