# Building Blocks Explorer

A **Bob mode + MCP server pair** that helps users discover and adopt IBM Technology Building Blocks. The Bob mode walks users through a Discover → Clarify → Design → Confirm → Build flow; the MCP server is the backing catalog/code-fetch API.

```
explore-BBs/
├── mcp-server/                  # FastMCP server (deployed to IBM Code Engine)
├── building-blocks-explorer.zip # Bob mode (download + drop into a workspace)
└── README.md                    # you are here
```

## Install the Bob mode

1. Download [building-blocks-explorer.zip](building-blocks-explorer.zip).
2. Unzip it; open the resulting folder as your workspace in Bob.
3. Select **🧱 IBM Building Blocks Explorer** from the mode picker.
4. Try: *"I want to build an insurance claims assistant agent"*.

The mode is pre-wired to the production MCP server on Code Engine — no extra setup needed.

## MCP server

See [mcp-server/README.md](mcp-server/README.md) for tool reference, local-dev setup, and Code Engine deploy/redeploy commands. The server is stateless and the static catalog lives in `mcp-server/src/building_blocks_mcp_remote/registry.py` — update that file whenever a new building block lands upstream.
