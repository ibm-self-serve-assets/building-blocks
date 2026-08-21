# 🧱 IBM Building Blocks Explorer

A **Bob mode** that takes you from a business use case to a build-ready
workspace. Describe what you want to build — the Explorer finds the right
IBM Technology Building Blocks, designs the solution with you, and installs
the matching **Bob skills** and **Bob modes** into your workspace so you can
start building immediately.

```
explore-BBs/
├── building-blocks-explorer.zip   # the Bob mode — download this
├── mcp-server/                    # source of the hosted catalog service
├── bb-catalog/                    # the catalog: blocks, skills, docs (auto-synced)
└── local-installer/               # source of the local install helper
```

## Install the Bob mode

**Prerequisites:** Bob, plus [uv](https://docs.astral.sh/uv/) for the local
install helper (`curl -LsSf https://astral.sh/uv/install.sh | sh` or
`brew install uv`). Nothing else — no Python, git, or Node required.

1. Download [building-blocks-explorer.zip](building-blocks-explorer.zip) and unzip it.
2. Open the resulting `building-blocks-explorer/` folder as your workspace in Bob.
3. Select **🧱 IBM Building Blocks Explorer** from Bob's mode picker.

Try:

- *"Are there any Bob skills related to real-time data streaming?"*
- *"I want help with access management and secrets for a client — can you help?"*
- *"A retail client wants an in-store assistant that answers product and
  policy questions from their documents — what should we build this with?"*

## How it works

The mode connects to two MCP servers (pre-configured, nothing to set up):

- **building-blocks** — the hosted catalog service: building blocks, Bob
  skills, Bob modes, and documentation, always current (the catalog in
  [`bb-catalog/`](bb-catalog/) updates automatically as teams ship assets).
  Server source: [`mcp-server/`](mcp-server/).
- **building-blocks-installer** — a small local helper that installs your
  chosen skills and modes into the workspace. Deliberately scoped: it only
  downloads from this repository and only writes inside your workspace.
  Source: [`local-installer/`](local-installer/).

With your approval, recommended skills land in `.bob/skills/` (several work
side by side) and builder modes merge into your workspace — reload Bob and
everything is active.

## Troubleshooting

- **Catalog tools unavailable** — check Bob's MCP panel shows
  `building-blocks` as Connected; fully restart Bob if not.
- **Installer unavailable** — usually a missing `uv`; install it and reload
  Bob. Until then the Explorer guides you through manual installs.
- **First launch is slow** — the install helper downloads and caches on
  first use; subsequent launches are instant.
