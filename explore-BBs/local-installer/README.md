# building-blocks-installer

Local companion MCP server for the **IBM Building Blocks Explorer** Bob mode.
The Explorer's remote catalog server is the brain (discovery, skills, modes,
download URLs); this tiny local server is the hands — it installs the chosen
Bob skills and modes into the current workspace, because Bob builds do not
reliably provide a shell tool.

**Scoped by design — this is not a shell:**

- Four fixed operations, no command execution:
  `install_skill`, `install_bob_mode`, `render_diagram`, `verify_install`
- Downloads only from the official repo
  (`raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/`)
- Writes only inside the workspace it is launched in
  (`.bob/` for installs, `*.png` at the root for diagrams)

## How it ships

A CI-built wheel is committed under `dist/`. The Explorer mode's `mcp.json`
launches it with `uvx`, pinning the wheel by commit-SHA raw URL so partners
always run exactly the reviewed bytes:

```json
"building-blocks-installer": {
  "command": "uvx",
  "args": [
    "--from",
    "building-blocks-installer @ https://raw.githubusercontent.com/ibm-self-serve-assets/building-blocks/<COMMIT_SHA>/explore-BBs/local-installer/dist/building_blocks_installer-0.1.2-py3-none-any.whl",
    "building-blocks-installer"
  ]
}
```

Partner prerequisites: **Bob + [uv](https://docs.astral.sh/uv/)**. Nothing
else — uv provisions its own Python if the machine has none.

## Development

```bash
uv build                          # build the wheel into dist/
uv run building-blocks-installer  # run the stdio server from source
```
