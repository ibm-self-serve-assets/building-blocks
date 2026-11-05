# Deployment and Operations — Requirement Spec

## 1. Overview

This spec defines how Factory Pulse is run, packaged, deployed, configured, secured, observed and backed up. Basis: `README.md`, `.env.example`, `deploy/` (Dockerfile, `deploy-local.*`, `deploy-ce.sh`, `deploy-confluent.*`), `scripts/` (`start.*`, `deploy.py`, `backup.*`, e2e/SSE tests), `infra/terraform/`, `server/app.py` and `docs/architecture.md`.

Deployment modes:
1. **Local dev** — `scripts/start.sh|.cmd|.py` or `cd frontend && npm install && npm run dev` (UI :5173, API :4000).
2. **Single container (podman/Docker)** — multi-stage `deploy/Dockerfile` (node:22-alpine build → python:3.11-slim); serves API + compiled UI on port 8080 inside the container (README: http://localhost:4000 via `deploy-local.sh` mapping).
3. **IBM Cloud Code Engine** — `deploy/deploy-ce.sh` builds image, pushes to IBM Container Registry, turns `.env` into a Code Engine secret, runs app with `--min-scale 1 --max-scale 1 --cpu 1 --memory 2G`.
4. **One-click Confluent Terraform** — `deploy/deploy-confluent.*` / `python scripts/deploy.py {up|plan|retry|status|destroy|run}`.

## 2. Stakeholders

| Stakeholder | Interest |
|---|---|
| Platform / DevOps engineer | Reproducible builds, deploys, rollback/teardown |
| Solutions Architect / Demo Presenter | One-command start, quick cloud provisioning, safe teardown |
| Security reviewer | Secret handling, unauthenticated backend exposure |
| Confluent / IBM Cloud account owner | Billing awareness, permissions, quotas |
| Maintainer | Backups, health checks, tests |

## 3. Functional Requirements

| ID | Priority | Requirement |
|---|---|---|
| FR-401 | Must | The product SHALL start locally in simulation mode with `cp .env.example .env` followed by the documented dev commands, requiring only Node.js 20+ (and Python 3.11+ for the backend) and no cloud credentials. |
| FR-402 | Must | `scripts/start.sh`, `scripts/start.cmd` and `scripts/start.py` SHALL start backend (port 4000) and frontend dev server (port 5173) together. |
| FR-403 | Must | The Flask backend SHALL serve the compiled frontend (`frontend/dist`) and API from one process, return JSON 404 for unknown `/api/*` paths and SPA `index.html` fallback otherwise; if the frontend is not built it SHALL respond 404 "Frontend not built. Run `npm run build` first." |
| FR-404 | Must | `deploy/Dockerfile` SHALL build the frontend, install `deploy/requirements.txt`, expose 8080, default `STREAM_MODE=mock`, accept `VITE_GOOGLE_MAPS_API_KEY`/`VITE_GOOGLE_MAPS_MAP_ID` build args, and include a HEALTHCHECK against `/api/health` (30 s interval, 5 s timeout). |
| FR-405 | Must | `deploy/deploy-local.sh|.cmd` SHALL build and run the container with podman and support subcommands `logs` (follow) and `down` (stop and remove). |
| FR-406 | Should | `deploy/deploy-ce.sh` SHALL validate required `.env` variables (`KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_API_KEY`, `KAFKA_API_SECRET`), log in to IBM Cloud (default region `eu-de`), ensure registry secret, create/replace the app secret from non-empty `.env` values excluding `PORT` and `API_KEY`, and deploy with port 8080, min/max scale 1, 1 vCPU, 2 GB. |
| FR-407 | Should | `deploy/deploy-ce.sh delete` SHALL remove the Code Engine application. |
| FR-408 | Should | `python scripts/deploy.py up` SHALL prompt for Confluent Cloud API key and secret, show the billable plan, require confirmation, run Terraform to provision environment, Kafka Standard cluster (AWS, default `us-east-2`), service accounts, API keys, ACLs, topics, Schema Registry subjects, Flink pool + 4 CTAS statements, Tableflow and RTCE, then write a permission-restricted `.env` and start the local UI. |
| FR-409 | Should | `deploy.py plan` SHALL show the plan without applying; `status` SHALL print outputs; `retry` SHALL re-run apply; `run` SHALL start the app only. |
| FR-410 | Must | `deploy.py destroy` SHALL require the user to type `DESTROY` (unless `--yes`) and tear down cloud resources; documentation SHALL state closing the app does not stop charges. |
| FR-411 | Must | The Cloud API key/secret SHALL NOT be written to `.env` or a tfvars file; only generated resource secrets are written to the local ignored `.env` (and necessarily to Terraform state). |
| FR-412 | Should | Terraform SHALL expose feature toggles `enable_flink`, `enable_tableflow`, `enable_rtce` (default true), `flink_max_cfu` (default 5), `deployment_name` (default `factory-pulse-demo`) and `region`. |
| FR-413 | Must | Configuration SHALL be via environment variables documented in `.env.example`: `PORT`, `SIM_INTERVAL_MS`, `STREAM_MODE`, Kafka/Schema Registry credentials, `KAFKA_AUTO_CREATE_TOPICS`, `KAFKA_CONSUME_DERIVED`, `KAFKA_RISK_TOPIC`, `KAFKA_KPI_TOPIC`, `ACTION_WEBHOOK_URL`/`TOKEN`, `RTCE_MCP_ENDPOINT`/`RTCE_MCP_BASIC_TOKEN`, `VITE_GOOGLE_MAPS_API_KEY`/`MAP_ID` (plus `KAFKA_CONSUME_SOURCE`, topic overrides used in code). |
| FR-414 | Must | `.env` SHALL be git-ignored; `.env.example` SHALL contain only placeholders. Secrets SHALL never use the `VITE_` prefix. |
| FR-415 | Must | `GET /api/health` SHALL return `{ok, server, time, stream, mcpConfigured, googleMapsConfigured}` for liveness/readiness and Kafka transport observability. |
| FR-416 | Should | The server SHALL log publish and source-merge errors to stdout without crashing, and expose transport counters (`sent`, `failed`, `lastError`, `lastAck`) via `/api/stream`. |
| FR-417 | Should | `scripts/backup.sh|.ps1` SHALL create a timestamped copy (`backups/backup_<YYYYMMDD_HHMMSS>/`) of the listed source, docs, deploy, scripts and test files, skipping missing files and writing `MANIFEST.txt` with OK/SKIP counts. |
| FR-418 | Should | The project SHALL provide automated checks: `npm test` (Node simulation tests), `npm run build`, `npm run check`, Python deploy tests (`tests/test_deploy.py`) and e2e/SSE scripts in `scripts/`. |
| FR-419 | Must | Documentation SHALL state the backend has no authentication and MUST NOT be exposed publicly, listing required hardening (OIDC, RBAC, command allow-list, MCP argument validation, CSRF, rate limits, audit, CORS allow-list, approvals) before shared deployment. |
| FR-420 | Should | The Google Maps key SHALL be a browser key restricted by HTTP referrer; absence SHALL degrade to the SVG map. |
| FR-421 | Could | Graceful shutdown SHALL stop the simulation thread and disconnect Kafka. |
| FR-422 | Won't | This release WILL NOT provide HA, autoscaling (>1 instance, since state is in-memory per process), managed secrets rotation, or CI/CD pipelines. |

## 4. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-401 | Startup | Backend ready (`/api/health` 200) ≤ 10 s after process start in mock mode; container build ≤ 10 min on a networked machine. |
| NFR-402 | Footprint | Container runs within 1 vCPU / 2 GB; image based on `python:3.11-slim`. |
| NFR-403 | Security — secrets | 0 secrets in image layers, git history or browser bundle; Code Engine secrets injected only as env vars; `.env` permission-restricted by `deploy.py`. |
| NFR-404 | Security — exposure | Public exposure of the unauthenticated API is prohibited; webhook and MCP endpoints must be HTTPS. |
| NFR-405 | Observability | `/api/health` responds ≤ 200 ms in mock mode; Docker healthcheck interval 30 s; transport state changes are broadcast as SSE `cloud` events within one tick. |
| NFR-406 | Recoverability | Backup script completes ≤ 30 s for the listed files and reports files OK/skipped; Terraform state is retained locally for audit after destroy. |
| NFR-407 | Portability | Works on Windows (`.cmd`, `.ps1`), macOS and Linux (`.sh`); container tooling podman (Docker-compatible Dockerfile). |
| NFR-408 | Cost safety | Billable provisioning requires explicit confirmation; destroy requires typed `DESTROY`; Flink capped at 5 CFU by default. |
| NFR-409 | Repeatability | `deploy.py plan` followed by `up` yields the same resources; `retry` is idempotent for partially applied states. |
| NFR-410 | Configurability | All behaviour toggles (mode, intervals, consumers, webhook, MCP) are env-driven with no code change; defaults documented. |
| NFR-411 | Verification honesty | Docs state that Terraform apply and Vite production build were not verified in the authoring environment until proven. |

## 5. Acceptance Criteria

**FR-401**
- *Given* Node 20+ and Python 3.11+ and no cloud accounts, *When* the user follows the README quick start, *Then* http://localhost:5173 loads and `/api/health` at :4000 returns `stream.status:"mock"`.

**FR-402**
- *Given* a clean checkout, *When* `scripts/start.sh` runs, *Then* both servers are listening on ports 4000 and 5173 and stop together on interrupt.

**FR-403**
- *Given* `frontend/dist` exists, *When* `GET /` and `GET /some/spa/route` are requested, *Then* `index.html` is returned; `GET /api/nope` returns JSON 404 `{"error":"Not found"}`.
- *Given* no `dist`, *When* `GET /` is requested, *Then* 404 "Frontend not built…".

**FR-404**
- *Given* `podman build -f deploy/Dockerfile .`, *When* it completes, *Then* the image exposes 8080, `STREAM_MODE=mock`, and `docker inspect` shows a HEALTHCHECK; *And* `/api/health` returns 200 inside the container.

**FR-405**
- *Given* `./deploy/deploy-local.sh`, *When* run, *Then* the app is reachable at http://localhost:4000; `logs` follows output; `down` removes the container.

**FR-406**
- *Given* `.env` lacks `KAFKA_API_SECRET`, *When* `deploy-ce.sh` runs, *Then* it prints "Missing required variable in .env: KAFKA_API_SECRET" and exits non-zero without deploying.
- *Given* a valid `.env` and `ibmcloud` login, *When* run, *Then* the secret excludes `PORT` and `API_KEY` and the app runs with min=max=1 scale, 1 CPU, 2G.

**FR-407**
- *Given* a deployed app, *When* `deploy-ce.sh delete` runs, *Then* the Code Engine application no longer exists.

**FR-408**
- *Given* valid Cloud API credentials and an eligible account, *When* `python scripts/deploy.py up` runs and the user confirms the plan, *Then* resources are created, `.env` is updated with `STREAM_MODE=kafka` credentials, and the UI starts.
- *Given* the user declines confirmation, *Then* nothing is applied.

**FR-409**
- *Given* `deploy.py plan`, *When* run, *Then* no resources are created and the plan is displayed; `status` prints Terraform outputs.

**FR-410**
- *Given* `deploy.py destroy`, *When* the user types anything other than `DESTROY`, *Then* no teardown occurs; typing `DESTROY` destroys the resources and prints "Cloud teardown completed…".

**FR-411**
- *Given* a completed `up`, *When* `.env` and any tfvars are inspected, *Then* the Cloud API key/secret are absent.

**FR-412**
- *Given* `enable_flink=false`, *When* planned, *Then* no Flink pool/statements are created.

**FR-413**
- *Given* `.env.example`, *When* compared with variables read in `server/`, *Then* each documented variable has a comment/default and every code-read variable is documented.

**FR-414**
- *Given* `git status`, *When* `.env` exists, *Then* it is ignored; *And* `.env.example` secret fields are empty.

**FR-415**
- *Given* the running server, *When* `GET /api/health`, *Then* HTTP 200 with the listed keys.

**FR-416**
- *Given* a publish exception, *When* it occurs, *Then* "Publish error: …" is printed and the loop continues; `/api/stream.failed` reflects errors.

**FR-417**
- *Given* the workspace root, *When* `bash scripts/backup.sh` runs, *Then* `backups/backup_<timestamp>/` contains the files with the same relative paths, a `MANIFEST.txt` lists `[OK]`/`[SKIP]`, and missing files are skipped without aborting.

**FR-418**
- *Given* dependencies installed, *When* `npm run check` runs, *Then* tests and build complete with exit code 0.

**FR-419**
- *Given* `docs/architecture.md`, *When* read, *Then* the security section lists the hardening prerequisites and the prohibition on connecting to PLCs.

**FR-420**
- *Given* no Maps key, *When* `/api/health` is read, *Then* `googleMapsConfigured:false` and the SVG map is used.

**FR-421**
- *Given* the server receives a normal exit from `python app.py`, *When* it terminates, *Then* the shutdown event is set and Kafka disconnects.

**FR-422**
- *Given* Code Engine settings, *When* inspected, *Then* `MAX_SCALE` defaults to 1 and docs note state is per instance.

## 6. Out of Scope

- Kubernetes/Helm manifests, multi-region HA, blue/green deployment.
- CI/CD pipelines and automated image scanning.
- Managed secret stores (Vault, IBM Secrets Manager) and rotation.
- Production TLS termination/WAF, OIDC/RBAC (documented prerequisites only).
- Central log aggregation/metrics/tracing stack (only health endpoint, stdout and SSE status exist).
- Cost optimization beyond the default Flink CFU cap.

## 7. Open Questions

| # | Question | Owner |
|---|---|---|
| 1 | `README.md` says the container is reachable at :4000 while the Dockerfile exposes 8080; confirm the host port mapping in `deploy-local.sh`. | DevOps / TBD |
| 2 | Terraform default region is `us-east-2` but Code Engine default region is `eu-de`; is this cross-region split intentional? | DevOps / TBD |
| 3 | Repository contains committed Terraform state/backups under `infra/terraform` — should these be git-ignored and purged? | Security reviewer / TBD |
| 4 | Backup script manifest lists files that may not exist (e.g. `docs/cloud-setup.md`); should it be directory-based? | Maintainer / TBD |
| 5 | Observability: do we need structured logs/metrics beyond `/api/health`? | DevOps / TBD |
| 6 | Should Code Engine deployments add a minimal auth proxy given the unauthenticated API? | Security reviewer / TBD |
| 7 | Server-side configuration for demo credentials (`VITE_DEMO_USER/PASS`) is baked at build time — acceptable for shared deployments? | Product / TBD |
