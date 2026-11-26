# Leak to Lease

An approval-gated MySQL credential-remediation workflow for Bob using an
external `lease-mcp` backend.

**Author:** Aadhav Manimurugan (https://github.com/aadhavibm).

## Prerequisites

- Bob with skill support and seven attached `lease-mcp` tools.
- The [public backend](https://github.com/aadhavibm/leak-to-lease), installed
  separately, plus operator-approved Vault/MySQL access.
- Fresh scanner metadata, known consumers and an application recovery plan.

See [setup](references/setup.md). Installing this skill does not install its
backend or grant infrastructure permissions.

## Example requests

- "Quarantine this approved MySQL finding by reference and establish a baseline."
- "Guide migration to Vault database leases before administrator rotation."
- "Verify the old credential is rejected; do not treat an unreachable DB as dead."

Begin with [SKILL.md](SKILL.md). The workflow stops for missing tools, missing
approvals, a mismatched baseline, failed migration or an inconclusive proof.

## Boundaries

This is a prototype workflow, not a general scanner or automatic application
migration tool. It does not erase historical copies or guarantee that an agent
with unrelated permissions cannot read a secret.

The existing collection Vault skill is separate and is not replaced.
This contribution contains instructions only; it does not bundle or relicense
the external backend. That repository has viewing-only terms and retains its
upstream PetClinic licenses. Maintainer acceptance of that external dependency
and individual author credit remains a review item.

The backend is published at the public URL above. Use the pinned revision in
setup, and distinguish backend checks from Bob workflow validation when
reporting results. Publication does not change the backend's viewing-only terms.
