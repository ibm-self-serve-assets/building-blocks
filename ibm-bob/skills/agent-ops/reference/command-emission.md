# Command emission

**TRIGGER:** Bob is about to emit a bash block, or the user asks what Bob runs itself, why every block sources the venv, or how credentials are handled.

This skill is terminal-first: Bob writes the command, the user runs it, Bob reads the result files. RULE 2 forbids Bob from executing anything that mutates state, calls an LLM, or takes minutes.

---

## Block format

1. Bold lead-in on its own line: `**Run this in your terminal** — <purpose>:`
2. A fenced `bash` block.
3. An inline `#` comment for every non-obvious flag.
4. First line `source "$VENV_ACTIVATE" && \` whenever `orchestrate` or `python` is called.
5. A trailing line saying what to paste back: the last 20 lines, the output path, or y/n.

````
**Run this in your terminal** — <purpose>:

```bash
# <comment>
source "$VENV_ACTIVATE" && \
orchestrate <command> <subcommand> \
  --flag value
```

When it finishes, paste <the last 20 lines | the output path | y/n> so I can <diagnose | proceed | summarize>.
````

---

## Reference examples

### Activate a SaaS environment from a key file

````
**Run this in your terminal** — activate the environment (the key is read from your file and never shown):

```bash
# ~/.wxo-key.json is {"apikey": "..."} with mode 600
source "$VENV_ACTIVATE" && \
orchestrate env activate <env> --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')" && \
export WO_API_KEY="$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
```

Paste the "is now active" line (or the error).
````

### Import a multi-agent system

````
**Run this in your terminal** — import tools, collaborators, then the orchestrator (order matters):

```bash
source "$VENV_ACTIVATE" && \
orchestrate tools import -k python -f tools/<module>.py && \
orchestrate agents import -f agents/<collaborator_1>.yaml && \
orchestrate agents import -f agents/<collaborator_2>.yaml && \
orchestrate agents import -f agents/<orchestrator>.yaml && \
orchestrate agents list | grep <prefix>
```

Paste the list output so I can confirm the names.
````

### Evaluate with a config file

````
**Run this in your terminal** — run the suite (about a minute for five cases):

```bash
# config: test_paths, output_dir, max_user_turns, judge and simulator models, metrics
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate -c evaluations/eval_config.yaml
```

Paste the "Config and metadata saved to" path; I will read summary_metrics.csv and the transcripts from there.
````

### Search traces

````
**Run this in your terminal** — list traces from the last hour:

```bash
# --last replaces the explicit window; keep windows <= 4h on SaaS
source "$VENV_ACTIVATE" && \
orchestrate observability traces search --last 1h --limit 20
```

Paste the trace ids; I will pick one to export.
````

### Call an authenticated endpoint without exposing the token

````
**Run this in your terminal** — the token is read from the orchestrate cache inside your shell:

```bash
TOKEN=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.cache/orchestrate/credentials.yaml')))['auth']['<ENV>']['wxo_mcsp_token'])") && \
INSTANCE=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.config/orchestrate/config.yaml')))['environments']['<ENV>']['wxo_url'])") && \
curl -sS -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "${INSTANCE}<ENDPOINT>" | python3 -m json.tool | head -60
```

Paste the response (or the HTTP status).
````

---

## Anti-patterns

| Never | Why |
|---|---|
| a pasted API key, token, Langfuse key, or instance id in a block or in chat | RULE 5; read them from files with `$(...)` |
| `sudo` | nothing here needs root |
| `orchestrate agents import` / `tools import` without a prior `list` on a shared instance | RULE 6; `import` updates existing names in place |
| `orchestrate settings observability langfuse configure` on an instance you do not own | one setting per instance; it overwrites the owner's |
| `orchestrate server purge` unless explicitly requested | deletes the VM, agents, and traces |
| `-l` and `-i` on the same `server start` | mutually exclusive |
| `--env-file` to "switch instance" for an evaluation | it does not; activate the environment |
| more than ~5 commands chained with `&&` | hard to retry; split |

---

## What Bob may execute (read-only)

`orchestrate env list`, `orchestrate agents list`, `orchestrate tools list`, `orchestrate models list`, `pip show …`, `lsof -ti :4321`, `python3 -c "from dotenv import find_dotenv; …"`, `orchestrate observability traces search --last 1h --limit 5`, `orchestrate evaluations red-teaming list`, file reads in the project (including run folders the user points at).

## What Bob must emit

`orchestrate env add / activate`, `server start / stop`, any `import` or `update`, `evaluations quick-eval / evaluate / analyze / record / generate`, `red-teaming plan / run`, `observability traces export`, `pip install`, anything that writes outside the project, any git write.

---

## Handling output

- Ask for the smallest signal: the path, the last 20 lines, the error, y/n. Never a full `results.json` or transcript pasted into chat.
- Given a path, read `summary_metrics.csv`, `average_metrics.json`, and the `messages/*.messages.analyze.json` of failed cases with offsets; quote only the failing step.
- Given an exported trace, summarize the span tree; do not echo it.
