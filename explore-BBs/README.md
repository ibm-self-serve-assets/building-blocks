# Building Blocks Explorer — Bob Mode

A custom mode for Bob (IBM's code assistant) that guides you from a business idea to the right IBM Technology Building Blocks, then merges a recommended builder Bob mode into your workspace so you can start implementing.

## Install

1. Download `building-blocks-explorer.zip` from this repo.
2. Unzip it anywhere convenient. You'll get a `building-blocks-explorer/` folder containing a hidden `.bob/` config directory.
3. Open that folder as your workspace in Bob (so Bob picks up `.bob/`).
4. In Bob's mode picker, select **🧱 IBM Building Blocks Explorer**.
5. Start with a prompt like:
   - "I want to build an insurance claims assistant agent"
   - "What building blocks are available?"
   - "What Bob Modes can I install?"

## What this mode does

A 5-step Discover → Clarify → Design → Confirm → Hand-off flow. It uses a remote MCP server to pull the live Building Blocks catalog, READMEs, docs, and sample assets. When you confirm a recommendation, the chosen builder Bob Mode is downloaded and merged into your workspace's `.bob/` folder; after a Bob reload, the new mode is in the picker alongside this one.

For technical details (file layout, MCP server URL, how the merge works), see the README inside the unzipped folder.
