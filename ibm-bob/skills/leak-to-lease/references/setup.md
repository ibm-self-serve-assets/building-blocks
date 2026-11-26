# Setup

## Separate components

1. This collection supplies skill instructions.
2. The external [Leak to Lease backend](https://github.com/aadhavibm/leak-to-lease)
   supplies the seven MCP tools and the reference application.
3. The operator supplies approved Vault/MySQL infrastructure and authentication.

Installing a skill is not backend installation or permission to change a DB.
Do not point users to an internal repository or a contributor's workstation.

## Backend source and installation

Review the external repository's terms and README before installing. Its
viewing-only terms are not replaced by the collection's license.

The pinned backend revision for this draft is
`b3fc0e294d032820c6551aa01686c93d9f1e78ed`. The repository is public; do not
substitute another project or revision if its URL is unavailable.

After operator approval, use a new checkout:

```bash
git clone https://github.com/aadhavibm/leak-to-lease.git
cd leak-to-lease
git checkout --detach b3fc0e294d032820c6551aa01686c93d9f1e78ed
python3 -m venv lease-mcp/.venv
lease-mcp/.venv/bin/python -m pip install -e ./lease-mcp
```

Use a new checkout rather than changing an existing working repository. The
backend's build, tests, wheel import and complete replay have separate
verification evidence in its README.

## Private authentication and MCP attachment

Privately configure the backend's `VAULT_ADDR` and `VAULT_TOKEN` in its ignored
backend environment file. Do not ask the operator to paste values into chat.
Use appropriate TLS verification and scoped permissions. Configure
`LEASE_MCP_SOURCE_ROOT` for the explicitly approved source checkout.
The backend validates authentication using `auth/token/lookup-self`; its token
must permit that read as well as the approved operational endpoints.

The backend reads its private environment; Bob does not necessarily forward
every parent variable to an MCP child. Reconnect MCP after configuration changes.
Do not put credentials into a tracked MCP JSON file.

The installed entry point is `lease-mcp`. Make it available on the PATH inherited
by Bob, for example by activating the installed backend environment before
starting Bob. A portable MCP server entry contains no credential values:

```json
{
  "mcpServers": {
    "lease-mcp": {
      "command": "lease-mcp",
      "args": []
    }
  }
}
```

For an IDE that does not inherit that PATH, the operator must configure the
installed executable through Bob's MCP settings. Do not invent a workstation
path or add one to this skill. Confirm all seven actual tools are attached.

## Disposable reference replay

Follow the backend README's tested quick start rather than copying old manual
database-reset instructions. It runs Vault/MySQL containers on a newly selected
local Docker context and the application JARs on the host. MySQL's published
host port is **3307**, while the container's internal port is 3306.

The explicit replay approval covers only that run's new resources. It sanitizes
private source copies, creates service leases, checks real application work,
rotates the administrator credential, verifies error 1045 and rechecks work.
It cleans up its own containers/processes and retains private logs on failure.
Do not run it against an existing application, database or Vault.

## Verification boundaries

- Missing tools or authentication are blockers; do not claim simulated success.
- A local-parser check is not a Vault Radar check. HCP authentication is separate.
- A MySQL 1045 rejection is different from network failure.
- A successful backend replay is not proof that Bob invoked the workflow.
- Timed lease/outage tests require an awake host.
- The source and collection must be publicly available before a fresh public
  download/install can be verified.
