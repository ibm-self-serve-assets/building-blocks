# Building Blocks Explorer — Catalog MCP Server

Remote MCP server backing the **Building Blocks Explorer** Bob mode. The
catalog is loaded live from markdown files in this repository — adding or
changing a block or skill never requires a server redeploy.

## Tools (14)

| Tool | Description |
|------|-------------|
| `list_building_blocks` | List/filter building blocks by group, capability, or tag |
| `search_building_blocks` | Ranked keyword search across blocks and docs |
| `get_building_block` | Full details about a building block (metadata + README) |
| `get_building_block_readme` | README for a block or sub-component |
| `list_docs_pages` | Documentation pages from the docs site |
| `get_docs_page` | Raw markdown content of a docs page |
| `list_assets` | Browse code files and configs within a building block |
| `get_asset_file` | Content of a specific code/config file |
| `list_bob_modes` | Bob Modes discovered across building blocks |
| `get_bob_mode_info` | README and details for a specific Bob Mode |
| `download_bob_mode` | Direct download URL for a Bob Mode ZIP |
| `list_skills` | Bob skills, with owning blocks and capability |
| `get_skill` | Full "use when…" description for one skill |
| `download_skill` | Download URL + layout-aware install instructions |

## How the catalog works

The catalog lives at [`explore-BBs/bb-catalog/`](../bb-catalog/):

```
bb-catalog/
├── capabilities.md         # top-level capabilities (ai, data, automation)
├── groups.md               # groups within each capability
├── docs-pages.md           # docs site nav
├── blocks/                 # one file per building block
├── skills/                 # one file per Bob skill (GENERATED — see below)
└── skill-archives/         # generated zips for skills without one upstream
```

Block files are authored by hand. **Skill files are generated** by
[`bb-catalog/scripts/sync_skills.py`](../bb-catalog/scripts/), which scans
the repository for skills, reconciles duplicates by content, and runs
automatically in CI — see `bb-catalog/skills-inventory.md` for the current
inventory and any items needing attention.

The server fetches these files live from `raw.githubusercontent.com` with a
5-minute TTL cache, falling back to a stale cache and then to a bundled
snapshot if GitHub is unreachable. To force a refresh sooner, POST to
`/admin/reload-data`.

## Layout

```
mcp-server/
├── pyproject.toml              # deps pinned exactly (see uv.lock)
├── Dockerfile
├── scripts/
│   ├── validate_data.py        # catalog cross-reference validator
│   └── smoke_test.py           # exercises all 14 tools + fallback path
└── src/building_blocks_mcp_remote/
    ├── server.py               # FastMCP entry, /health, /admin/reload-data
    ├── data_loader.py          # catalog fetch, schemas, cache, fallback
    ├── github_client.py        # GitHub auth (App or PAT), API budgets, cache
    ├── rate_limit.py           # per-IP rate limiting middleware
    ├── fallback_registry.json  # bundled last-known-good catalog snapshot
    └── tools/                  # the 14 tools (discover, details, docs,
                                # assets, bob_modes, skills)
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GH_APP_ID` / `GH_APP_INSTALLATION_ID` / `GH_APP_PRIVATE_KEY` | No | — | GitHub App auth (preferred for production; PEM raw or base64) |
| `GITHUB_TOKEN` | Recommended | — | PAT fallback (60 → 5,000 req/hr; zero scopes suffice — public data only) |
| `PORT` | No | 9248 | HTTP port |
| `BB_RATE_LIMIT_PER_MIN` | No | 60 | Per-IP rate limit (`/health` exempt) |
| `BB_ADMIN_TOKEN` | No | — | Shared secret for `POST /admin/reload-data` (`X-Admin-Token` header) |
| `BB_CATALOG_LOCAL_PATH` | No | — | Read the catalog from a local directory (dev mode; bypasses cache) |

## Local development

```bash
cd mcp-server
uv sync

# Option A: live-fetch from GitHub
export GITHUB_TOKEN="ghp_..."
uv run building-blocks-mcp-remote-marketplace

# Option B: local catalog (fast iteration on catalog edits)
export BB_CATALOG_LOCAL_PATH="/path/to/building-blocks/explore-BBs/bb-catalog"
uv run building-blocks-mcp-remote-marketplace

# Verify everything
BB_CATALOG_LOCAL_PATH=/path/to/explore-BBs/bb-catalog uv run python scripts/smoke_test.py
curl http://localhost:9248/health
```

## Deploy to IBM Code Engine

Runs as Code Engine app `building-blocks-explorer-mcp` (separate from the
legacy v1 app, which stays untouched for existing users).

```bash
ibmcloud ce secret create --name bb-marketplace-secrets \
  --from-literal GITHUB_TOKEN=<pat> --from-literal BB_ADMIN_TOKEN=<random>

ibmcloud ce app create --name building-blocks-explorer-mcp \
  --build-source . --port 9248 --min-scale 0 --max-scale 3 \
  --env-from-secret bb-marketplace-secrets

# Redeploy after server-code changes:
ibmcloud ce app update --name building-blocks-explorer-mcp --build-source .

# Force a catalog refresh after a merge (optional; TTL is 5 min):
curl -X POST https://<app-url>/admin/reload-data -H "X-Admin-Token: <BB_ADMIN_TOKEN>"
```

Catalog and skills content changes **never** need a redeploy — only changes
under `mcp-server/` do.

## Adding a new building block

1. Author `bb-catalog/blocks/<slug>.md` (see existing files for the schema).
2. Add the block's docs page entry to `bb-catalog/docs-pages.md`.
3. Run `bb-catalog/scripts/validate_catalog.py` — fix any errors.
4. PR / push to this repo. Live within 5 minutes of merge.

New **skills** need no catalog work at all: ship the skill under your
block's `bob-skills/` (or `ibm-bob/skills/`) and the sync workflow catalogs
it automatically.

## License

Apache 2.0
