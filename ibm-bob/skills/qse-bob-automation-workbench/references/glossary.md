# Glossary

Written from `SPEC.md` content only.

| Term | Meaning |
|---|---|
| Workbench | The QSE Automation Workbench web application described by `SPEC.md`. It orchestrates; it does not analyse code itself (SPEC 1.1). |
| Bob / Headless Bob | The external agent service that receives one prompt, runs the QSE CLI and returns output and files. Reached over REST threads (`rest-threads`) or ACP 0.2.0 (`acp`). The browser never calls it; the backend does (SPEC 4.1, 6.4). |
| QSE | IBM Quantum Safe Explorer. The CLI scanner run by Headless Bob. The workbench only locates it, runs the version check and verifies Bob can reach the same path (SPEC 4.3). |
| CBOM | Cryptography Bill of Materials. One of the JSON result files the QSE CLI writes (`quantum_safe_cryptography_analysis_cbom.json`). The workbench does **not** parse it (SPEC 4.7, gap G10). |
| ACP | Agent Communication Protocol, version 0.2.0. Alternative Bob adapter with `supportsFiles=false`, so no report file or artifacts (SPEC 6.4, G18). |
| `STREAM_MODE` | `mock` or `realtime`. Default is `mock` (SPEC 4, 10.1, G16). |
| mock | A replay of one recorded real run from `backend/demo-data/recorded-run.json`. No GitHub, QSE CLI or Headless Bob call occurs. Every record has `mock=true` and is labelled DEMO (SPEC 4.5, FR-08). |
| realtime | The live chain: GitHub clone, QSE CLI validation, Headless Bob execution. |
| Execution | One pipeline run of 9 steps for one repository and one prompt (SPEC 4.5). |
| Step source | `backend` for the workbench's own steps; `headless-bob` for `bob_processing`. |
| Report source | `headless-bob-file`, `headless-bob-output` or `unavailable`. Never fabricated (FR-07, SPEC 4.7). |
| Execution strategy | `shared-volume` (containers; `PathMapper` translates paths) or `colocated` (host processes; identity mapping) (SPEC 5.4). |
| PathMapper | Translates workbench paths into the paths Bob sees, longest-prefix match; a path outside every mount is "not reachable from Bob" (SPEC 5.4). |
| Pipeline digital twin | The SVG diagram on the Workspace page built only from real step events and connection status (SPEC 3.4, FR-12). |
| Heavy route | A route with an extra rate limit of `max(10, floor(RATE_LIMIT_MAX/6))` per window (SPEC 6.2). |
| Status labels | **Implemented**, **Partial**, **Mocked**, **Planned**: see the legend at the top of `SPEC.md`. |
