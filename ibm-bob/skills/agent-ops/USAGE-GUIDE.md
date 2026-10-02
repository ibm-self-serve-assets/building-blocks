# Agent Ops skill — usage guide

For the person installing and invoking the skill. Bob's own instructions are in `SKILL.md` and `reference/`; the prerequisites checklist is `assets/PREREQUISITES.md`.

## 1. Install the skill

```bash
cp -r agent-ops <your-repo>/.bob/skills/
```

Bob discovers skills in `.bob/skills/`. Enable `agent-ops` in the Skills panel if it is not active.

## 2. Install the ADK

Fastest path:

```bash
bash .bob/skills/agent-ops/setup.sh            # creates ~/agent-ops-venv (override with VENV_DIR=...)
```

Manual path:

```bash
python3.12 -m venv ~/agent-ops-venv
source ~/agent-ops-venv/bin/activate
pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"
pip show ibm-watsonx-orchestrate ibm-watsonx-orchestrate-evaluation-framework | grep -E "^(Name|Version)"
```

## 3. Export `$VENV_ACTIVATE`

Every command Bob emits starts with `source "$VENV_ACTIVATE" && \`:

```bash
echo 'export VENV_ACTIVATE=$HOME/agent-ops-venv/bin/activate' >> ~/.zshrc && source ~/.zshrc
```

## 4. Point `orchestrate` at your instance

**SaaS.** Put the API key in a file only you can read and activate the environment from it; the key never appears in a shell history line or in chat:

```bash
echo '{"apikey": "<your IBM Cloud or MCSP API key>"}' > ~/.wxo-key.json && chmod 600 ~/.wxo-key.json
orchestrate env add --name prod-eval --url https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<id>   # --type ibm_iam is inferred for IBM Cloud, mcsp for AWS
orchestrate env activate prod-eval --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
```

SaaS tokens expire after about two hours; re-run the `activate` line when commands start failing with 401. For long evaluation runs also `export WO_API_KEY="$(...same one-liner...)"` so the framework can refresh its token.

**Developer Edition.** A `.env` in the project root:

```
WO_DEVELOPER_EDITION_SOURCE=orchestrate
WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<id>
WO_API_KEY=<key for that instance>
```

then `orchestrate server start -e .env` (add `-i` if you want traces) and `orchestrate env activate local`.

## 5. Import the agent you want to evaluate

Order: tools → knowledge bases → collaborator agents → orchestrator. Check `orchestrate agents list` first if the instance is shared; prefix your names if they could collide.

```bash
orchestrate tools import -k python -f tools/<module>.py
orchestrate knowledge-bases import -f knowledge_bases/<kb>.yaml      # if any
orchestrate agents import -f agents/<collaborator>.yaml              # each collaborator
orchestrate agents import -f agents/<orchestrator>.yaml
```

## 6. (Optional) ADK docs search for Bob

```bash
cp .bob/skills/agent-ops/assets/mcp.json ./mcp.json     # or merge into an existing mcp.json
```

The server is streamable HTTP; nothing to install locally.

## 7. Invoke the skill

Open the agent project in Bob and describe what you want. Bob will:

1. post the one-line prerequisite notice and ask three questions (environment, intent, current state)
2. show a module plan
3. run read-only checks (`orchestrate env list`, `agents list`, `pip show`, …)
4. emit copy-paste blocks for everything else
5. read the result files you point it at and explain them

Example prompts:

- *"Smoke-test `benchmarks/` against `support_agent` with quick-eval"*
- *"Write test cases for the refund flow: happy path, missing order id, out-of-policy refund"*
- *"Run the five cases in `evaluations/testcases_v2/` and tell me what failed and why"*
- *"Score yesterday's run against these rules: never approve when sanctions match; always give a numeric reason for a denial"*
- *"Red-team the orchestrator with crescendo and instruction override; success means it issues an APPROVED letter"*
- *"Search traces from the last hour for session `abc` and export the slowest one"*

## What Bob runs vs. what Bob emits

| Bob runs (read-only) | Bob emits for you |
|---|---|
| `orchestrate env list`, `agents list`, `tools list` | `orchestrate env add / activate`, `server start` |
| `pip show …` | `pip install …` |
| `lsof -ti :4321` (DevEd) | `orchestrate tools / agents / knowledge-bases import` |
| `python3 -c "from dotenv import find_dotenv; …"` | `orchestrate evaluations quick-eval / evaluate / analyze / record / generate` |
| file reads in the project | `orchestrate evaluations red-teaming plan / run` |
| `orchestrate observability traces search --last 1h --limit 5` | `orchestrate observability traces export` and anything that writes files |

## First-time gotchas

1. **The framework evaluates whatever environment is active.** Check `orchestrate env list` before every run; `--env-file` does not switch instances.
2. **Expired SaaS token.** 401s from the framework mean the cached token expired; re-activate the environment.
3. **Ancestor `.env`.** The framework auto-loads the nearest `.env` walking up from the project. A stale one in `~/src/.env` silently overrides your settings; move it aside.
4. **Precision looks low on a multi-agent system.** Handoffs count as tool calls; declare them as goals (see `reference/module-benchmarks.md`).
5. **Routing accuracy is 0.0 although handoffs happened.** Each agent's `display_name` must equal its `name`.
6. **Runs take minutes instead of seconds.** The simulated user chats on after the task; cap `max_user_turns` at 3 and end the story with "reply END".
7. **`analyze` fails validating `text_match`.** Normalize a copy of the run folder first (recipe in `reference/module-analyze.md`).
8. **`red-teaming plan` produced odd goals.** Review every generated file, or hand-author the attack with an explicit success goal.

## What "done" looks like

- [ ] ADK ≥ 2.18 and framework ≥ 1.5 in a Python 3.12 venv; `$VENV_ACTIVATE` exported
- [ ] Environment activated; agent, collaborators, and tools listed under the expected names
- [ ] 5–12 test cases in a folder, each with handoff goals (multi-agent), `max_user_turns`, and an end-of-conversation signal
- [ ] `quick-eval` clean apart from handoff noise
- [ ] `evaluate` run with `summary_metrics.csv` read and each failure attributed (test case / agent / model)
- [ ] Rubric criteria written for the policies that matter and scored
- [ ] Red-team attacks run, with a success rate per attack and remediation applied where needed
- [ ] Traces exported for anything that needed explaining

## Updating the skill

```bash
cd <building-blocks checkout> && git pull
cp -r ibm-bob/skills/agent-ops <your-repo>/.bob/skills/
```
