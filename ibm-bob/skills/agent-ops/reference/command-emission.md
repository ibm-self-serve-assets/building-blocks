# Canonical Command Emission Format

**TRIGGER:** Load when Bob is about to emit any bash block, asks "how should I format this", or when user asks about what Bob may execute vs forbidden, why every block starts with `source "$VENV_ACTIVATE"`, or how to handle credentials safely.

---

## Why this file exists

This skill is **terminal-first**. Bob writes the command; the user runs it. RULE 2 of the skill forbids Bob from executing mutating commands. This file is the practical contract for how Bob fulfills that rule.

---

## Canonical block format

**Required elements:**

1. **Bold lead-in line on its own line**, then a blank line, then the code fence.
   Format: `**Run this in your terminal** — <one-line purpose>:`
2. Fenced bash block opened with three backticks and the word `bash`.
3. Inline `#` comments for every non-obvious flag inside the block.
4. Lead with `source "$VENV_ACTIVATE" && \` when the command calls `orchestrate ...` or `python ...`. User's venv does NOT persist across turns; activation is per-command.
5. **Trailing instruction** below the block: tell user what to paste back ("last 20 lines", "the path printed at the end", "the error stack if it fails", "y/n if it completes").

### Template
````
**Run this in your terminal** — <one-line purpose>:

```bash
# <inline comment per non-obvious flag>
source "$VENV_ACTIVATE" && \
orchestrate <command> <subcommand> \
  --flag-1 value-1 \
  --flag-2 value-2
```

When it finishes, paste <last 20 lines | the output path | y/n> back so I can <diagnose | proceed | summarize>.
````

---

## Reference examples

### Example: `dev_ed_server_start_with_langfuse`
**Purpose:** start the Developer Edition server with the local Langfuse stack.

````
**Run this in your terminal** — start the WXO Developer Edition server with local Langfuse (first run pulls Docker images, can take ~7 minutes):

```bash
# -e .env sources your DevEd credentials (WO_DEVELOPER_EDITION_SOURCE, WO_INSTANCE, WO_API_KEY)
# -l starts the bundled Langfuse stack at http://localhost:3010
source "$VENV_ACTIVATE" && \
orchestrate server start -e .env -l
```

When the server is up (you'll see `Server started on http://localhost:4321`), paste y/n back and I'll continue.
````

### Example: `evaluate_with_explicit_token`
**Purpose:** run `evaluate` with explicit token in `config.yaml`, avoiding the gateway-provider auto-resolution gap on older ADK versions.

````
**Run this in your terminal** — generate config.yaml with explicit token, then run the evaluation:

```bash
# Extract local mcsp token from credentials cache, write it into config.yaml.
# The token only exists inside this shell session — never sent to chat.
source "$VENV_ACTIVATE" && \
TOKEN=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.cache/orchestrate/credentials.yaml')))['auth']['local']['wxo_mcsp_token'])") && \
cat > config.yaml <<EOF
auth_config:
  url: http://localhost:4321
  tenant_name: local
  token: ${TOKEN}
provider_config:
  provider: gateway
  model_id: meta-llama/llama-3-3-70b-instruct
EOF
echo "Wrote config.yaml with token redacted: $(grep token config.yaml | sed 's/token: .*/token: <REDACTED>/')" && \
orchestrate evaluations evaluate \
  --test-paths benchmarks/ \
  --tools-path agent/tools \
  --output-dir eval_results/$(date +%Y%m%d-%H%M%S) \
  --config ./config.yaml
```

When it finishes, paste the last 20 lines of output (or the path printed at the end) so I can diagnose.
````

### Example: `env_activate_cloud`
**Purpose:** activate a SaaS cloud environment after adding it.

````
**Run this in your terminal** — add and activate the SaaS cloud env (replace `<NAME>`, `<URL>`, and `<TYPE>` per the matrix):

```bash
# --type mcsp_v2 for api.<region>.watson-orchestrate.ibm.com (Dallas, Frankfurt, Tokyo)
# --type ibm_iam for api.<region>.watson-orchestrate.cloud.ibm.com (IBM Cloud)
source "$VENV_ACTIVATE" && \
orchestrate env add -n <NAME> -u <URL> --type <TYPE> --activate
```

Paste the success line (or error if it fails) so I can confirm.
````

### Example: `traces_search_with_window`
**Purpose:** search traces within a time window (RULE 6 — window mandatory).

````
**Run this in your terminal** — search recent traces:

```bash
# --start-time and --end-time are both required by the CLI.
# Format MUST be %Y-%m-%dT%H:%M:%S — no `Z` suffix, no microseconds.
# (CLI accepts %Y-%m-%d, %Y-%m-%dT%H:%M:%S, or %Y-%m-%d %H:%M:%S only.)
# On ADK >= 2.6.0 you can use --last 1h instead and skip the explicit window.
source "$VENV_ACTIVATE" && \
orchestrate observability traces search \
  --start-time "$(date -u -v-1H +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --limit 20
```

Paste the trace IDs (just the list) and I'll pick one to export.
````

### Example: `curl_authed_endpoint` (RULE 5 reference)
**Purpose:** generic pattern for hitting any auth'd HTTP endpoint (e.g., Langfuse REST, ad-hoc WXO endpoints) without leaking the bearer token. Every secret reference must interpolate via shell `$()` from the source-of-truth file, never appear in chat.

````
**Run this in your terminal** — call an auth'd HTTP endpoint (token read locally; never sent to chat):

```bash
# Replace <ENV> and <ENDPOINT> with your env name and the API path.
TOKEN=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.cache/orchestrate/credentials.yaml')))['auth']['<ENV>']['wxo_mcsp_token'])") && \
INSTANCE=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.config/orchestrate/config.yaml')))['environments']['<ENV>']['url'])") && \
curl -sS \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Accept: application/json" \
  "${INSTANCE}<ENDPOINT>" | python3 -m json.tool
```

Paste the response (or the HTTP status if it fails) so I can interpret it.
````

---

## Anti-patterns

| Banned | Reason |
|---|---|
| Manually-pasted JWTs, API keys, or instance UUIDs in any emitted block | Violates RULE 5. Use shell `$()` interpolation from `credentials.yaml`. |
| `sudo` anywhere in an emitted command | WXO eval commands do not need root. If a path-permissions issue appears, surface it for the user to resolve. |
| `&&` chains longer than ~5 commands in one block | Hard to debug, hard to retry. Split into separate blocks the user runs in sequence. |
| `>` redirection into ambiguous paths (e.g., `> output.json` without a directory) | Pollutes user's cwd. Always emit `--output-dir <path>` or fully-qualified path. |
| Emitting `orchestrate ...` without `source "$VENV_ACTIVATE" && \` | Violates RULE 4. The venv does NOT persist across turns. |
| Emitting `--with-langfuse` and `--with-ibm-telemetry` in the same `server start` | Violates RULE 8. Mutually exclusive. Emit two separate `server start` blocks if both needed. |

---

## What Bob may execute (read-only)

**Allowed:**
- `lsof -ti :4321` / `:3010` / `:8080`
- `orchestrate env list`
- `orchestrate agents list`
- `pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework`
- `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`
- file reads via Read tool
- `orchestrate observability traces search ... --limit <=10` (low-limit probe)

**Forbidden (must emit for user):**
- `orchestrate server start ...`
- `orchestrate env activate ...`
- `orchestrate env add ...`
- `orchestrate evaluations evaluate ...`
- `orchestrate evaluations quick-eval ...`
- `orchestrate evaluations record ...`
- `orchestrate evaluations generate ...`
- `orchestrate evaluations red-teaming plan ...`
- `orchestrate evaluations red-teaming run ...`
- `pip install ...`
- Any `git` command that writes

---

## Handling user output

**Principle 1:** Do NOT ask the user to paste full traces, full result files, or multi-megabyte JSON into chat. Ask for the smallest signal you need: last 20 lines, the error stack, the output path, or a y/n.

**Principle 2:** When the user pastes a path (e.g., `eval_results/20260512-...`), use the Read tool on relevant files inside that path. Do NOT ask the user to `cat` them.

**Principle 3:** For large result files (`results.json`, exported traces), read with `head`/`grep`/limited offsets — never load the full file when a summary or specific section will do.
