---
name: leak-to-lease
description: >-
  Guides approved MySQL credential remediation using the seven lease-mcp tools
  and HashiCorp Vault. Use when asked to quarantine a leaked database password,
  migrate an application to Vault database leases, rotate its compromised
  administrator credential, or verify rejection of the old credential.
  Requires a configured lease-mcp backend and explicit operator approval.
metadata:
  author: "Aadhav Manimurugan (https://github.com/aadhavibm)"
  version: "0.1.0"
---

# Leak to Lease

Guide the operator through a scoped credential-remediation workflow. This skill
contains instructions, not a Vault server, database, or MCP implementation.
Its external backend is [Leak to Lease](https://github.com/aadhavibm/leak-to-lease).
Read [setup](references/setup.md) if prerequisites or tools are missing.

## Safety and scope

- Never request, read, print, echo, or log credential values. Do not open leaked
  source lines, private environment files, token files, or raw scanner reports
  with an agent read tool. Use approved paths, line numbers and fingerprints.
- Do not put credentials in tool arguments or shell commands. Let the backend
  read the selected source value and perform authentication by reference.
- Instructions are not an access-control boundary. Confirm the operator's OS,
  Vault and database permissions and approved source root.
- Discovery approval is not change approval. Obtain approval before source,
  Vault or database changes, and obtain separate approval immediately before
  administrator rotation. Confirm the recovery plan and affected consumers.
- Do not reset, reseed, recreate, or stop existing resources to make a check
  pass. Use only separately approved disposable resources for demonstrations.
- On a failure, report safe metadata and stop dependent changes. Do not retry
  quarantine or rotation blindly, or restore the leaked password automatically.
- This prototype supports the backend's MySQL workflow. It does not discover
  every consumer, erase Git history, or automatically integrate arbitrary apps.

## 1. Intake and preflight

Establish the approved application/repository, environment and change owner:

1. A fresh finding's source path and one-based line number, without reading its
   value. Refresh stale scanner metadata instead of guessing line numbers.
2. The MySQL endpoint/account/schema used by the MCP server's credential proof,
   and the MySQL address reachable by Vault's database plugin. Those addresses
   may differ across host and container networks.
3. The Vault endpoint, database mount, connection name, application roles,
   reviewed grants, TTLs and application authentication method.
4. The affected consumers, application checks, change approvals and recovery
   plan. Do not silently substitute localhost or default accounts.

Verify that these exact tools are attached:

`quarantine_secret`, `enable_db_engine`, `configure_mysql_connection`,
`create_dynamic_role`, `rotate_root`, `lookup_lease`, `prove_dead`.

If any are missing, follow setup and stop remediation. Do not simulate calls.
If all are attached, do not reinstall dependencies unnecessarily.

## 2. Establish the scanner baseline

Use the approved scanner on the approved scope, with matched values suppressed.
Record the scanner's actual identity and exit result. The backend gate uses
`0` for no findings, `1` for findings, and `2` for scan/configuration errors.
Configured Radar must not silently fall back to the local parser.

A local-parser result is not a Vault Radar result. The bundled replay retains
intentional fake values in its tracked starting sources; agree on the private
replay-copy scope rather than disabling the gate or claiming those sources
were permanently sanitized.

## 3. Quarantine, then verify the exact baseline

After change approval, call `quarantine_secret` with the approved `source_path`,
`line_number`, and `mount_path="secret"`. Reference resolution currently requires
that fixed KV mount. If an approved fingerprint is compatible with the backend's
`sha256:<64 hex>` format, pass it as `expected_fingerprint`; do not reinterpret
another scanner's hash.

Require `QUARANTINED_AND_SANITIZED`. Retain the quarantine ID, fingerprint and
safe locations. The placeholder is not application migration.

- A stale fingerprint, unsupported literal, linked/non-owned source or busy
  source is a blocker, not permission to bypass validation.
- `QUARANTINED_NOT_SANITIZED` means storage succeeded but replacement failed.
  Keep its safe recovery reference and stop; do not overwrite intervening edits
  or quarantine the same value again.
- Pause external writers. Advisory locking does not control every other editor.

Call `prove_dead` with that reference and the original approved proof endpoint,
schema and username. Require `ACCEPTED` / `ERROR_CREDENTIAL_STILL_ACTIVE`
**before rotation**. An already rejected or inconclusive baseline does not
demonstrate remediation by this workflow.

## 4. Configure leases and migrate consumers

1. Call `enable_db_engine` for the approved database mount. Review an existing
   mount before changing its connection configuration.
2. Call `configure_mysql_connection` with the quarantine ID and reviewed
   connection settings. Preserve literal `{{username}}` and `{{password}}`
   template markers. Do not insert credentials. Require `CONFIGURED`.
3. Call `create_dynamic_role` for each approved role, using the same connection
   name as `db_name` and the same database mount. Require `ROLE_ACTIVE`.
4. Review the defaults: DML grants cover `petclinic.*`, not separate per-service
   tables; role defaults are `1h` and `24h` maximum. Supply reviewed SQL/TTLs for
   another scope. Default root-rotation SQL targets both `%` and `localhost`;
   confirm those accounts or supply reviewed rotation statements.
5. Migrate each consumer using its actual Vault integration and private,
   role-scoped authentication. Do not give application processes setup/admin
   tokens. Schema seeding is a separately approved administrative operation.
6. Verify real database-backed application work, not only a health response or
   cached data. Spring PetClinic's degraded owner response can retain owner
   data with `visitsUnavailable=true`; that is not a healthy Visits check.

When an approved lease ID is available as safe metadata, use `lookup_lease` and
require `ACTIVE` with positive remaining TTL. Do not read a credential-issuing
endpoint merely to obtain an ID. Do not invent a successful lease check.

For ongoing operation, test actual pool rollover beyond maximum TTL and
recovery after Vault returns. Already-borrowed transactions and cached reads
are not forcibly cancelled by lease expiry. Other applications require their
own integration and acceptance tests.

## 5. Rotate, prove rejection, and recheck

Do not rotate until migration and application checks pass. An emergency change
of order requires explicit approval for that altered risk.

1. Obtain administrator-rotation approval for the specific connection/mount.
2. Call `rotate_root` once; require `ROOT_ROTATED`.
3. Call `prove_dead` for each reference at its original proof endpoint/account.
   Require `REJECTED`, `connection_rejected=true`, `error_code="1045"`, and
   `CREDENTIAL_PROVEN_DEAD`. Other connection failures are inconclusive.
4. Recheck uncached application work and the same approved scanner scope.
   A clean scan does not prove database rejection; rejection at one endpoint
   does not establish rejection at every other account or database.

## 6. Handoff

Report changed locations, safe references, roles/mount/connection, actual
scanner and test results, application work, and each proof's outcome.
Separate passed, failed, inconclusive, skipped and untested stages.

State completion only for the approved scope when migration, rotation,
rejection, application checks and the final scan all pass. Retain quarantine
data under the owner's retention policy. Stop only owned temporary resources
after verification; stopping a dev Vault destroys its ephemeral state.
