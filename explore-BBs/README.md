# Building Blocks Explorer - Bob Mode

A custom Bob mode that **guides you to the right IBM Technology Building Blocks and Bob modes for your use case**. It doesn't build your project itself — its job is to understand what you're trying to do, recommend the right pieces, and hand you off to a builder Bob mode that does the actual implementation.

**How the hand-off works:** when this mode recommends another Bob mode (e.g., `domain-agent-builder`), the recommended mode is **merged into the same `.bob/` folder**. You stay in one workspace and switch to the builder mode via Bob's mode picker. The downloaded mode's MCP servers are merged into the same `mcp.json` file.

## What it does

When activated, Bob acts as a discovery and recommendation guide that:
- Walks you through a 5-step discovery flow (Discover → Clarify → Design & Recommend → Confirm → Hand-off)
- Lists and searches building blocks across 3 capabilities: AI, Data, and Automation
- Fetches documentation and READMEs in real time via MCP
- Browses code, configs, and reference implementations
- Recommends the right combination of building blocks and **builder Bob mode(s)** for your use case
- Merges the recommended builder mode into this workspace so you can switch to it and start building

## SDLC workflow (5 steps, internal)

1. **Discover** — understand your business problem
2. **Clarify** — targeted questions to fill in design gaps
3. **Design & Recommend** — generate a Mermaid architecture diagram with Building Block annotations
4. **Confirm** — write `use_case_summary.md` + `architecture_diagram.png` and ask for approval
5. **Hand-off** — merge the recommended builder Bob Mode(s) into this `.bob/` folder so the builder mode can take over the actual implementation

You can stop at any step.

## File layout

### Initial state (just BB-explorer)

```
your-project/
├── .bob/
│   ├── custom_modes.yaml          # Single entry: building-blocks slug
│   ├── rules-building-blocks/
│   │   └── 2_sdlc_workflow.xml
│   └── mcp.json                   # MCP config (Building Blocks server)
└── README.md
```

### After downloading another Bob mode (e.g., `domain-agent-builder`)

```
your-project/
├── .bob/
│   ├── custom_modes.yaml             # Both mode entries, appended
│   ├── rules-building-blocks/
│   ├── rules-domain-agent-builder/   # ← copied from downloaded mode
│   ├── portfolio-advisor-agent/      # ← copied template asset
│   └── mcp.json                      # ← merged: existing + downloaded mode's MCPs
├── use_case_summary.md
├── architecture_diagram.png
└── ...
```

The downloaded mode also ships its own MCP config (newer modes use `mcp.json`; older ones use the hidden `.mcp.json`). Both files (existing + downloaded) are merged into a single `mcp.json` containing all MCP servers — Bob then sees every server it needs.

Reload Bob (or your IDE) after the merge — the new mode appears in the picker.

## MCP server

This mode connects to the Building Blocks MCP server deployed on IBM Code Engine:

- **URL**: `https://building-blocks-mcp.23rbzktsxcbt.us-south.codeengine.appdomain.cloud/mcp`
- **Transport**: Streamable HTTP (via `mcp-proxy`)
- **Auth**: None (read-only, public data)

Configured in `.bob/mcp.json` (non-hidden so Bob detects it). After merging another mode, that file holds all MCP servers needed by all installed modes.

## Setup

1. Copy this folder to your project root, or open it directly as your workspace:
   ```bash
   cp -R building-blocks-explorer my-project
   cd my-project
   ```

2. Select **🧱 IBM Building Blocks Explorer** in Bob's mode picker.

3. Start exploring:
   - "I want to build an insurance claims assistant agent"
   - "What building blocks are available?"
   - "Show me the Vector Search documentation"
   - "What Bob Modes can I install?"

When Bob downloads another mode, it'll appear in the picker after a reload.
