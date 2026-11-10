# Spec audit guide

## When to use

Final phase of the rebuild (phase 11), and any time someone asks "is this a faithful recreation?". The audit is read-only: it reports, it does not fix.

## Inputs you need

- The rebuilt project root with `BUILD_DECISIONS.md`.
- `../references/SPEC.md` (sections 3.3, 3.4, 6.2, 7, 10.5, 13) and [gap-register.md](../references/gap-register.md).
- Ability to run the project's quality-gate commands (see `testing.md`).

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| (audit of FR-01..FR-12, NFR-01..NFR-08) | Each has recorded evidence | Section C of the report lists every ID with evidence (command output or file path) or FAIL. |

## Steps

Produce a report `AUDIT_REPORT.md` (the only file this guide may create) with the sections below. Each check is `PASS`, `FAIL` or `N/A (reason)`, with evidence.

### A. Structural checks (script them)

1. **Routes:** extract every method and path from SPEC 6.2 and from the project's `routes/index.ts`. Every SPEC row must exist with the same role (`any|op|adm`) and success status; list extras separately.
2. **Env vars:** every variable in SPEC 10.5 (backend runtime table) is parsed in `backend/src/config/env.ts` and listed in `.env.example`; defaults match.
3. **Tables:** all 11 tables exist (`users`, `sessions`, `bob_connection`, `repositories`, `qse_config`, `executions`, `execution_steps`, `execution_logs`, `reports`, `artifacts`, `prompt_history`); `bob_connection` and `qse_config` have `CHECK (id = 1)`; no FK on `executions.repository_id`.
4. **Pages:** all 11 routes in SPEC 3.3.0 render without error: `/login`, `/`, `/bob`, `/repository`, `/qse`, `/workspace`, `/workspace/:executionId`, `/history`, `/reports`, `/reports/:executionId`, `/settings`, plus `*` redirect to `/`. Check ids and copy against SPEC 3.3.x.
5. **Traceability:** every file path in the SPEC 13 matrix exists in the new project (or is recorded as intentionally different in `BUILD_DECISIONS.md`).

### B. Behavioural checks

6. **Digital twin (SPEC 3.4):** component exists with the listed props; makes no API call; no percentage text; placeholder when `execution` is null; external node tone rules; `--twin-*` variables defined on `.twin` and no `var(--cds-` inside the SVG; footer note text; DEMO addendum only in mock; the 5 tests plus a no-throw test pass. Note G2 outcome.
7. **Observability:** `x-request-id` on responses and in the error envelope; `/healthz` body; `/readyz` keys `database`, `workspace`, `accepting`; logs redact a test token; SIGTERM leaves within 25 s.
8. **Settings:** `GET /api/settings` has the documented fields and no filesystem paths; `POST /api/admin/rotate-secrets` is admin-only and returns `{activeKeyId, bobApiKeyReencrypted, repositoryTokensReencrypted}`; password change returns 204 and revokes all sessions; Settings page has the three password inputs with the documented validation and the admin-only rotation modal.
9. **Mock integrity:** in mock mode every row has `mock=true`, DEMO labels and `-DEMO` filenames; in realtime no demo data is ever served; separate DB files.
10. **Honesty rules:** report `source` is one of the three values; `unavailable` has no fabricated body; no progress percentage anywhere; no performance claim anywhere (NFR-08).
11. **Status labels:** documentation in the new project uses Implemented / Partial / Mocked / Planned, and nothing Partial or Planned is described as Implemented; no mocked behaviour is described as a real integration.

### C. Requirement evidence

12. A table for FR-01..FR-12 and NFR-01..NFR-08: owner guide, evidence, PASS/FAIL. Use the owner table in `../SKILL.md`.

### D. Process checks

13. `BUILD_DECISIONS.md` has a decision for every G1..G21 and the build mode.
14. The feature coverage matrix in `BUILD_DECISIONS.md` has every row ticked with evidence.
15. The go/no-go list in `production-readiness.md` was reviewed (look for a recorded note).
16. Quality gate commands pass for both packages (run them; record exit codes).
17. No `.env` file, secret, token or real customer repository name is committed (search tracked files; do not print values).

### E. Output format

```markdown
# Audit report
Mode: faithful clone | clone + fixes        Date: <ISO date>

## Summary
| Area | PASS | FAIL | N/A |
...
## Checks
| # | Check | Result | Evidence |
...
## Requirements
| ID | Owner guide | Result | Evidence |
...
## Deviations
| # | Where | Expected (SPEC section) | Found | Severity (blocker/major/minor) | Related gap |
...
```

Severity guide: **blocker** = security control missing, secret leakage, demo data served in realtime, fabricated results; **major** = missing route/page/table/env var, failing gate; **minor** = copy or styling differences, documented gaps kept as built.

## Verification (exit gate)

- The report exists and has all five sections with no empty cells.
- Every FAIL has a deviation row; there are zero blockers for sign-off.
- The audit changed no application file (`git status` shows only `AUDIT_REPORT.md` as new).

## Pitfalls

- "Fixing" while auditing. Report only.
- Treating an intentionally kept gap (recorded in `BUILD_DECISIONS.md`) as a FAIL; mark it as a minor deviation with the gap id.
- Trusting a green test run without checking AC-06, AC-07 and AC-18, which the reference never tested.
- Printing secrets while searching for them.

## Known gaps that apply

- G1..G21: every gap must have a recorded decision; this guide checks the record, it does not decide. See [gap-register.md](../references/gap-register.md). User decision: <fix | keep as built> (per gap, in `BUILD_DECISIONS.md`)

## SPEC references

SPEC 3.3, SPEC 3.4, SPEC 6.2, SPEC 7, SPEC 10.5, SPEC 11.5, SPEC 12, SPEC 13, SPEC 14, SPEC 15.
