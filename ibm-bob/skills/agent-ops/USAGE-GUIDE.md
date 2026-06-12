# Agent Ops Skill — Usage Guide

This guide is for the **person installing and invoking the skill**. For internal mechanics and detailed reference materials, see `SKILL.md` and `reference/`. For the full prerequisites checklist (software, credentials, hardware, network, troubleshooting), see `assets/PREREQUISITES.md`.

## Quick start

### 1. Install the skill into your Bob workspace

```bash
cp -r agent-ops ~/your-repo/.bob/skills/
```

Bob auto-discovers skills in `.bob/skills/`. No additional registration needed.

### 2. Install the WXO ADK with the agentops extra

**Fastest path — run the bundled setup script:**

```bash
bash .bob/skills/agent-ops/setup.sh
```

This creates a Python 3.12 venv at `~/agent-ops-venv`, installs `ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0` (which pulls eval-fw 1.4+), installs `uv` for the docs MCP, and prints the next-step guidance. Override the venv location with `VENV_DIR=/path/to/venv bash setup.sh`.

**Manual path** (if you want to use an existing venv or customize the install):

```bash
# Python 3.12 required (3.11 may work; 3.13+ not yet supported)
python3.12 -m venv ~/agent-ops-venv
source ~/agent-ops-venv/bin/activate

# Install ADK with the agentops extra (pulls eval-fw 1.4+)
pip install "ibm-watsonx-orchestrate[agentops]>=2.6.0,<3.0.0"

# Install uv for the docs MCP server
pip install uv
```

### 3. Export `$VENV_ACTIVATE` (mandatory)

Bob's emitted commands all start with `source "$VENV_ACTIVATE" && \`. Set this once in your shell rc:

```bash
echo 'export VENV_ACTIVATE=$HOME/agent-ops-venv/bin/activate' >> ~/.zshrc
source ~/.zshrc
```

### 4. Set up credentials

Drop a `.env` into your agent's project root (used by DevEd for image pulls):

```
WO_DEVELOPER_EDITION_SOURCE=orchestrate
WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<your-instance-id>
WO_API_KEY=<your-WXO-SaaS-API-key>
```

For RAG benchmarks AND red-teaming (anything that calls watsonx-backed judges), export in the shell:

```bash
export WATSONX_APIKEY=<IBM Cloud IAM API key>
export WATSONX_PROJECT_ID=<watsonx project ID>     # OR
export WATSONX_SPACE_ID=<WML-bound deployment space ID>
```

For cost/latency analysis (Langfuse), you'll fetch these from the Langfuse UI after first server start (`http://localhost:3010`, user `orchestrate@ibm.com`):

```bash
export LANGFUSE_BASE_URL=http://localhost:3010
export LANGFUSE_PUBLIC_KEY=pk-lf-...
export LANGFUSE_SECRET_KEY=sk-lf-...
```

See `assets/PREREQUISITES.md` for IBM Cloud UI navigation and full credential matrix.

### 5. Start your Docker runtime

Rancher Desktop, Docker Desktop, or Colima — anything that provides a `docker` CLI. The DevEd Lima VM needs ~16 GB free RAM and ~50 GB disk for the bootstrap image pull.

### 6. (Optional) Configure the docs MCP server

The skill ships a `mcp.json` at `assets/mcp.json` that registers the WXO docs MCP server. To wire it into Bob, copy or symlink it into your project root:

```bash
cp .bob/skills/agent-ops/assets/mcp.json ./mcp.json
# or symlink: ln -s .bob/skills/agent-ops/assets/mcp.json ./mcp.json
```

This gives Bob live access to the ADK docs via `search_ibm_watsonx_orchestrate_adk` and `query_docs_filesystem_ibm_watsonx_orchestrate_adk`.

### 7. Invoke the skill in Bob

Open your agent's project root in Bob and describe what you want. Bob auto-detects this skill and runs the 3-question interview.

**Example invocations:**

- *"I want to evaluate my pawsitive-grooming-agent before I deploy it to SaaS"*
- *"My benchmark scenarios are failing — Journey Success is 0 on 3 of 8. Help me figure out why"*
- *"Run red-teaming on my native portfolio-advisor agent. Focus on prompt leakage and instruction override"*
- *"Set up Langfuse and show me cost per scenario for the last eval run"*
- *"Search runtime traces from the last hour for agent foo"*

Bob will:
1. Post the prereq notice + 3 questions (target env / intent / current state)
2. Present a MODULE PLAN showing which modules will run, in what order
3. Run read-only diagnostics for the first module (`lsof`, `pip show`, etc.)
4. Emit copy-paste bash blocks for everything else
5. Ask you to paste back small signals (last 20 lines, output path, y/n) — never full traces

---

## What "Bob will run" vs "Bob will emit"

| Bob runs automatically (read-only) | Bob emits for you to run |
|---|---|
| `lsof -ti :4321 / :3010 / :8080` | `orchestrate server start ...` |
| `orchestrate env list` | `orchestrate env activate ...` |
| `orchestrate agents list` | `orchestrate env add ...` |
| `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework` | `orchestrate evaluations evaluate ...` |
| `python3 -c "from dotenv import find_dotenv; ..."` | `orchestrate evaluations quick-eval ...` |
| File reads via Bob's Read tool | `orchestrate evaluations record ...` |
| `orchestrate observability traces search ... --limit ≤10` (probe) | `orchestrate evaluations generate ...` |
| | `orchestrate evaluations red-teaming plan/run ...` |
| | Any `pip install ...` |
| | Any `git` write |

This boundary is enforced by RULE 2 in `SKILL.md`. The terminal-emitting stance prevents Bob from leaking credentials, mutating shared state, or surprise-installing packages.

---

## First-time gotchas

1. **Ancestor `.env` pollution.** `dotenv.load_dotenv()` walks UP the directory tree until it finds a `.env`. A stale `.env` in `~/src/.env` silently overrides your project's. Bob runs `find_dotenv()` as a pre-flight check; if the printed path is outside your project, move the ancestor `.env` aside.
2. **Lima VM in degraded state.** If `docker --context ibm-watsonx-orchestrate ps` returns `EOF`, the WXO ADK's bundled Lima VM is stuck. Bob's recovery recipe: stop server → `mv ~/.lima/ibm-watsonx-orchestrate ~/.lima/ibm-watsonx-orchestrate.bak-$(date +%Y-%m-%d)` → restart server (ADK creates a fresh VM, ~10 min first run).
3. **`-l` and `-i` are mutually exclusive.** You can run the server with Langfuse OR IBM Telemetry, never both. Pick one per session.
4. **`-a all` silently produces 0 red-teaming attacks.** Run `red-teaming list` first to see the EXACT attack names, then pass a comma-separated list (e.g., `"Instruction Override,Jailbreaking,Crescendo Attack"`).
5. **`analyze` does NOT take `--output-dir`.** The report writes alongside `--data-path`.
6. **Cost shows as $0 in Langfuse.** Two possible causes: (a) the model isn't registered with pricing — Langfuse ships 161 model definitions but `groq/openai/gpt-oss-120b` and watsonx-served models are NOT pre-registered; or (b) token usage isn't being propagated to Langfuse observations. The skill walks you through inspecting a single trace's `promptTokens` / `completionTokens` to disambiguate.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `400 Bad Request from iam.cloud.ibm.com/identity/token` | Ancestor `.env` pollution overriding `WO_INSTANCE` | Run `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`. Move ancestor `.env` aside. |
| `RuntimeError: WO_API_KEY must be specified for SaaS or IBM IAM auth` | `auth_config.url` in `config.yaml` is a cloud URL but the active env is local | Confirm `config.yaml.auth_config.url` matches the active env's URL |
| `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}` | Active env's instance UUID doesn't match the API key | Ask user which instance their key belongs to; activate matching env or `env add` new one |
| `model_not_supported` / 404 on judge model from watsonx | `model_id` in `config.yaml` isn't supported by your watsonx project/space | Set `model_id: meta-llama/llama-3-3-70b-instruct` (commonly available); list supported models in watsonx.ai console |
| RAG judges 403/401: 'invalid bedrock API key' | Default judge `bedrock/openai.gpt-oss-120b-1:0` needs Bedrock creds | Use `provider: gateway` in `config.yaml` + export `WATSONX_APIKEY` + `WATSONX_PROJECT_ID` or `WATSONX_SPACE_ID`. The gateway routes via watsonx. |
| `space_id ... is not associated with a WML instance` | Watsonx space exists but isn't bound to a Machine Learning service | Either bind in IBM Cloud → Resource list → WML service → Manage → Add to space, OR use `WATSONX_PROJECT_ID` instead (projects are usually pre-bound) |
| `apikey must be specified` from eval framework | `WATSONX_APIKEY` env var not exported | `export WATSONX_APIKEY=...` (re-export per shell session) |
| Langfuse `port 3010` connection refused | Server wasn't started with `-l` | Restart with `orchestrate server start -e .env -l`. Remember `-l` and `-i` are mutually exclusive. |
| `session_id=None` in `results.json` | LLM-simulator infrastructure crash (non-deterministic) | Re-run the failing scenario; if persistent across 3 runs, check provider config + active env |
| `red-teaming plan` produces 0 attacks despite `-a` | `-a all` was passed OR attack name misspelled/wrong case | Run `red-teaming list` first; use EXACT case-sensitive names, comma-separated |
| `red-teaming run` errors mid-batch with `FileNotFoundError: ... instruction_override.messages.json` | RAG-seed benchmarks (those using `conversational_search`) trigger an eval-fw 1.4.9 bug for `Instruction Override` variants | Either exclude RAG seed scenarios when running `plan` (`-d` to tool-only benchmarks) or exclude `Instruction Override` from `-a` when RAG seeds are present |
| `docker.sock` returns EOF on ibm-watsonx-orchestrate context | Pre-existing Lima VM from older ADK in degraded state | Stop server, move `~/.lima/ibm-watsonx-orchestrate/` aside (`.bak/` suffix), restart server (creates fresh VM) |

For deeper troubleshooting, Bob loads the relevant module reference file. The full troubleshooting table is also in `assets/PREREQUISITES.md`.

---

## What "complete" looks like

After running a full workflow, you should have:

- [ ] WXO ADK 2.6+ and eval-framework 1.4+ installed in a Python 3.12 venv
- [ ] `$VENV_ACTIVATE` set in your shell rc
- [ ] `.env` in agent root with `WO_DEVELOPER_EDITION_SOURCE`, `WO_INSTANCE`, `WO_API_KEY` (DevEd) OR cloud env activated via `orchestrate env add` (SaaS)
- [ ] `WATSONX_APIKEY` + `WATSONX_PROJECT_ID`/`SPACE_ID` exported (for RAG benchmarks + red-teaming)
- [ ] Server started with `-l` (Langfuse) or `-i` (IBM Telemetry), with Langfuse keys exported if using `-l`
- [ ] Agent imported into the active env (tools → KBs → agent)
- [ ] Benchmark JSON(s) under `benchmarks/`, validated by `quick-eval`
- [ ] Full `evaluate --with-langfuse` run, with `summary_metrics.csv` interpreted
- [ ] (Optional) `red-teaming plan` + `run` results, with severity-rated findings
- [ ] (Optional) Langfuse model pricing registered for cost analysis; 5-layer report delivered

---

## Updating the skill

```bash
cd <bob-skills-source>
git pull
cp -r agent-ops ~/your-repo/.bob/skills/   # overwrite
```

Bob picks up the updated skill on next invocation. No restart needed.
