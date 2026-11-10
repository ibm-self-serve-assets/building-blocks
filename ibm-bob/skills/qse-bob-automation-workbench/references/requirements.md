# Requirements and business context

> Extracted verbatim from `SPEC.md` (sections 1.1-1.6). Do not edit here; edit SPEC.md and re-extract.

## 1.1 Purpose

QSE Automation Workbench is a web application that lets an authenticated user orchestrate a **quantum-safe cryptography assessment** of a GitHub repository. The workbench does not perform the analysis itself. It prepares the inputs, hands a single prompt to an external agent (**Headless Bob**), which runs the **IBM Quantum Safe Explorer (QSE) CLI**, then retrieves and presents the resulting report.

## 1.2 Business objectives

| # | Objective | Realised by |
|---|---|---|
| O1 | Give a user one place to connect Headless Bob, clone a repository, validate the QSE CLI and start an assessment | Pages `/bob`, `/repository`, `/qse`, `/workspace` |
| O2 | Make the assessment observable in real time without inventing progress | SSE stream, step list, log viewer, Pipeline digital twin |
| O3 | Preserve results so they can be reviewed and exported later | SQLite persistence, `/history`, `/reports`, Markdown/PDF/JSON download |
| O4 | Keep credentials and untrusted repository content safe | AES-256-GCM secret box, SSRF guard, shell-free exec, redaction, CSRF |
| O5 | Allow a safe demonstration with no external dependencies | `STREAM_MODE=mock` replay of one recorded real run |

## 1.3 Capabilities

| Capability | Status |
|---|---|
| Local username/password sign-in with server-side sessions | Implemented |
| Configure and test a Headless Bob connection (`rest-threads` or `acp` adapter) | Implemented (realtime). Mocked (mock). |
| Validate and clone a GitHub repository (public, or private with a token) | Implemented (realtime). Mocked (mock). |
| Discover, configure and validate the QSE CLI | Implemented (realtime). Mocked (mock). |
| Submit one prompt, run the 9-step pipeline, stream events and logs | Implemented (realtime). Mocked (mock). |
| Cancel a running execution | Implemented |
| Persist execution history; search, filter, sort, paginate | Implemented |
| Build a Markdown report from Headless Bob's output; split it into sections | Implemented |
| Download report as Markdown, PDF or JSON; download retrieved artifacts | Implemented |
| Rotate the encryption key for stored secrets | Implemented (admin only) |
| Change own password | Implemented |
| Pipeline digital twin diagram | Implemented (added to the workspace page) |
| Multi-user management (create, delete, change role) | **Planned**: only the bootstrap admin exists; no API or UI |
| Structured crypto-risk scoring, CBOM rendering, risk categorisation | **Planned**: the backend never synthesises findings |
| Data retention / cleanup of old executions | **Planned** |
| Database other than SQLite | **Planned** (docs mention Postgres as a future adapter) |
| SSO / OIDC / MFA | **Planned** |

## 1.4 Functional requirements

| ID | Requirement | Status |
|---|---|---|
| FR-01 | The system shall require authentication for every `/api` route except `POST /api/auth/login`. | Implemented |
| FR-02 | The system shall store the Bob API key and repository tokens only in encrypted form and never return them. | Implemented |
| FR-03 | The system shall refuse to start an execution unless Bob is connected, the repository is cloned, the QSE CLI is validated and reachable from Bob, and a prompt is provided. | Implemented |
| FR-04 | The system shall run at most `MAX_CONCURRENT_EXECUTIONS` executions at once and queue the rest. | Implemented |
| FR-05 | The system shall stream execution state and logs over SSE and support resume via `Last-Event-ID` / `?after=`. | Implemented |
| FR-06 | The system shall persist every execution, its steps, logs, report and artifact metadata. | Implemented |
| FR-07 | The system shall present the report source honestly: `headless-bob-file`, `headless-bob-output` or `unavailable`. | Implemented |
| FR-08 | The system shall label all recorded-replay data as DEMO in the UI and in exports. | Implemented |
| FR-09 | The system shall allow the user to cancel an active execution. | Implemented |
| FR-10 | The system shall mark executions that were active at restart as failed. | Implemented |
| FR-11 | The system shall let an administrator re-encrypt stored secrets with the active key. | Implemented |
| FR-12 | The system shall show a live pipeline diagram derived only from real step events and connection status. | Implemented |

## 1.5 Non-functional requirements

| ID | Requirement | Status |
|---|---|---|
| NFR-01 | Secrets never appear in logs, API responses, URLs or browser storage. | Implemented (redaction, secret box) |
| NFR-02 | All outbound HTTP to Bob is SSRF-guarded; redirects are not followed. | Implemented |
| NFR-03 | No child process is started through a shell; repository content is never executed. | Implemented |
| NFR-04 | The service shall shut down gracefully on SIGTERM/SIGINT (hard stop after 25 s). | Implemented |
| NFR-05 | The backend shall refuse to start on invalid configuration. | Implemented |
| NFR-06 | The UI shall use IBM Carbon (g100 dark) and IBM Plex typography. | Implemented, with the token caveat in [3.1.4](#314-known-token-caveat) |
| NFR-07 | The system shall be single-node. | By design (SQLite, in-memory SSE bus, in-process queue) |
| NFR-08 | Performance targets (latency, throughput) | **Not specified in code**; none are claimed here |

## 1.6 Out of scope (explicitly not built)

Multi-tenant isolation, per-user repositories (the repository list is global), horizontal scaling, queue persistence across restarts, QSE-phase-level progress (Headless Bob exposes none), and any analysis logic inside the workbench.

---
