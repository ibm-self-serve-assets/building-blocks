# Foundation guide

## When to use

First build phase of the QSE Workbench, before any route, table or page exists. Also use when adding or changing an environment variable.

## Inputs you need

- `BUILD_DECISIONS.md` from `../SKILL.md` (for G16).
- [env-vars.md](../references/env-vars.md): every variable with purpose, required, default and sensitivity (copied from SPEC 10.5).
- Node.js >= 22.13.

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| NFR-05 | The backend refuses to start on invalid configuration | Starting the backend without `SECRETS_KEYS` or `ADMIN_PASSWORD` (the two required variables in env-vars.md) exits non-zero with a readable message; a unit test asserts it. (SPEC 11.5 AC-17 and SPEC 12.3 name `SESSION_SECRET`/`ENCRYPTION_KEY`; those names do not exist in `env.ts` or SPEC 10.5. Use `SECRETS_KEYS` and `ADMIN_PASSWORD`.) |

## Steps

1. **Layout** (SPEC 5.3, 13):

   ```text
   backend/   src/{config,controllers,db,integrations,middleware,models,orchestrators,repositories,routes,services,utils}, tests/, demo-data/
   frontend/  src/{components,hooks,layouts,pages,services,stores,styles,test,types}, public/
   deployment/  docker-compose.yml, docker-compose.tls.yml, nginx/
   scripts/   deploy_local.sh, deploy_psh.sh, lib/common.sh
   docs/, .env.example, README.md
   ```

2. **Backend package** (SPEC 2.1). ESM (`"type": "module"`), `engines.node >=22.13`. Dependencies at these resolved versions:

   | Package | Version | | Package | Version |
   |---|---|---|---|---|
   | express | 5.3.0 | | undici | 8.12.4 |
   | zod | 4.6.7 | | pdfkit | 0.20.2 |
   | pino | 10.4.0 | | typescript (dev) | 7.0.2 |
   | helmet | 8.3.0 | | vitest (dev) | 5.1.0 |
   | express-rate-limit | 8.7.3 | | supertest (dev) | 7.3.2 |
   | cors | 2.8.6 | | tsx (dev) | 4.23.15 |
   | cookie-parser | 1.4.7 | | | |

   Scripts: `test`, `dev` (tsx watch), `build` (`tsc -p tsconfig.build.json`), `start`, `typecheck`, `audit`. `tsconfig.json`: target ES2023, `module: NodeNext`, `strict: true`. `tsconfig.build.json` emits to `dist/` with source maps. Database is built-in `node:sqlite` (no npm package).

3. **Frontend package** (SPEC 2.2). Dependencies:

   | Package | Version | | Package | Version |
   |---|---|---|---|---|
   | react, react-dom | 18.3.1 | | react-markdown | 10.1.0 |
   | @carbon/react | 1.120.0 | | remark-gfm | 4.0.1 |
   | @carbon/icons-react | 11.92.0 | | vite (dev) | 8.3.7 |
   | @ibm/plex-sans | 1.1.0 | | @vitejs/plugin-react (dev) | 6.3.0 |
   | @tanstack/react-query | 5.107.1 | | typescript (dev) | 7.0.2 |
   | react-router-dom | 7.18.5 | | sass (dev) | 1.108.1 |
   | zustand | 5.1.0 | | vitest (dev) | 5.1.0 |
   | jsdom (dev) | 31.0.0 | | @testing-library/react (dev) | 16.3.3 |

   Also dev: `@testing-library/jest-dom ^7.0.1`, `@testing-library/user-event ^14.6.8`. Scripts: `test`, `dev`, `build` (`tsc --noEmit && vite build`), `preview`, `typecheck`. Vite: build target `es2022`, no source maps, dev port 5173, proxy `/api` to `VITE_API_PROXY ?? http://127.0.0.1:8080` with `changeOrigin: false`. TS: `jsx: react-jsx`, `moduleResolution: Bundler`, `strict`, `isolatedModules`.

4. **Config module** `backend/src/config/env.ts`:
   - Parse `process.env` with one zod object containing every variable in env-vars.md, with the listed defaults and bounds.
   - Lists (`QSE_CLI_SEARCH_DIRS`, `QSE_CLI_ALLOWED_DIRS`, hosts) use a `list()` helper that splits on commas.
   - `TRUST_PROXY` is an integer >= 0, default 1.
   - `WORKSPACE_ROOT` optional, default `<DATA_DIR>/workspaces`, resolved. `DEMO_DATA_DIR` defaults to `backend/demo-data`.
   - Database path: `<DATA_DIR>/db/workbench.sqlite` in realtime, `<DATA_DIR>/db/workbench-demo.sqlite` in mock (separate files).
   - `NODE_ENV=production` forces secure cookies.
   - On failure print each zod issue (never values of sensitive variables) and `process.exit(1)`.
   - Export one frozen typed config object consumed by the rest of the backend.

5. **STREAM_MODE default (G16):** SPEC says the default is `mock`, in `env.ts` and in compose. Faithful clone: keep `mock`. If BUILD_DECISIONS says "fix": default to `realtime` only if you also require explicit configuration in compose, and say so in the README. Either way, document the consequence: a fresh install shows the demo.

6. **`.env.example`**: every variable, no real values, sensitive ones empty with a generation hint. Never commit a real `.env`.

## Verification (exit gate)

```bash
cd backend  && npm install && npm run typecheck
cd frontend && npm install && npm run typecheck
```

- NFR-05: a unit test calls the config loader with missing secrets and asserts failure (SPEC 11.5 AC-17).
- Another unit test asserts: default `STREAM_MODE` is `mock`, mock and realtime DB files differ, and `NODE_ENV=production` yields secure cookies.
- Every variable in env-vars.md appears in `env.ts` and in `.env.example`.

## Pitfalls

- Using a `sqlite3` npm package. The reference uses `node:sqlite`, which is why Node >= 22.13 is required.
- Reading `.env` files into prompts or logs.
- Making `STREAM_MODE` default to `realtime` silently, which changes documented behaviour (SPEC 10.1).
- Forgetting that Bob address and key are **not** environment variables: they are entered in the UI and stored encrypted.

## Known gaps that apply

- G16: `STREAM_MODE` defaults to `mock`, including in compose. User decision: <fix | keep as built>

## SPEC references

SPEC 2.1, SPEC 2.2, SPEC 5.3, SPEC 10.5, SPEC 11.5 (AC-17). Table: [env-vars.md](../references/env-vars.md).
