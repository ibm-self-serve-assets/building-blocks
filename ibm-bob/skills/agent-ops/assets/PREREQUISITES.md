# Agent Ops — prerequisites

What needs to be in place before invoking the skill. Validated with ADK 2.18.0 / evaluation framework 1.5.2 against an IBM Cloud SaaS instance; Developer Edition notes come from the ADK documentation.

## 1. Software

| Component | Version | Purpose | Install |
|---|---|---|---|
| [Bob](https://bob.ibm.com) | current | runs the skill | bob.ibm.com |
| Python | **3.12** | venv for the ADK | `pyenv install 3.12` or system Python |
| WXO ADK with the `[agentops]` extra | `>= 2.18.0, < 3.0.0` (pulls evaluation framework `1.5.x`) | the CLI Bob emits commands for | `pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"` |
| Docker runtime | recent | **Developer Edition only** | Docker Desktop, Rancher Desktop, or Colima |

Why the floor: 2.18 / 1.5 is the combination the field notes in `SKILL.md` were observed on (handoff goals, `max_user_turns`, `RubricEvaluation` via `operator_configs`, `traces search --last`, the `analyze`/`text_match` quirk). Earlier releases behave differently in ways this skill no longer documents.

## 2. Credentials

### 2a. SaaS

- The **instance URL** (WXO UI → Settings → API details), for example `https://api.<region>.watson-orchestrate.cloud.ibm.com/instances/<id>` (IBM Cloud) or `https://api.<region>.watson-orchestrate.ibm.com/instances/<id>` (AWS).
- An **API key** with access to that instance: an IBM Cloud IAM key (user or service ID with the WO User role on the instance) or an MCSP key for AWS-hosted instances.
- Keep the key in a file with mode 600 (for example `~/.wxo-key.json` containing `{"apikey": "..."}`) and read it with `$(...)` when activating. Tokens expire after about two hours.

```bash
orchestrate env add --name <env> --url <instance url>            # --type ibm_iam | mcsp | cpd only if inference fails
orchestrate env activate <env> --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
export WO_API_KEY="$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"   # lets long runs refresh their token
```

On SaaS the evaluation framework's judge and simulated user run through the instance's model gateway; no watsonx.ai key is needed for the default models.

### 2b. Developer Edition

`<project>/.env`, passed with `-e` on every `server start`:

```
WO_DEVELOPER_EDITION_SOURCE=orchestrate
WO_INSTANCE=https://api.<region>.watson-orchestrate.ibm.com/instances/<id>   # any instance you can authenticate to; used for image pulls and model access
WO_API_KEY=<key for that instance>
```

Optional, when you want the local gateway to use watsonx.ai models directly: `WATSONX_APIKEY` and `WATSONX_SPACE_ID` (a space bound to a watsonx.ai Runtime instance) or `WATSONX_PROJECT_ID`. Then `orchestrate env activate local`.

### 2c. Not needed for this skill

Langfuse keys (cost analysis lives in the Cost Management building block), AWS Bedrock or Groq keys (the default judge model is served through the WXO gateway).

## 3. Network egress

| Host | Purpose |
|---|---|
| `api.<region>.watson-orchestrate.cloud.ibm.com` / `api.<region>.watson-orchestrate.ibm.com` | your instance |
| `iam.cloud.ibm.com` | IBM Cloud token exchange (IBM Cloud instances) |
| `developer.watson-orchestrate.ibm.com` | ADK docs MCP server |
| `registry.dl.watson-orchestrate.ibm.com`, `docker.io`, `quay.io` | Developer Edition image pulls |
| `*.ml.cloud.ibm.com` | watsonx.ai, only if you point the local gateway at it |

## 4. Hardware (Developer Edition only)

About 16 GB of RAM free for Docker and 50 GB of disk; the first `server start` pulls images for about 10 minutes, later starts take under a minute.

## 5. The agent you want to evaluate

- **Native WXO agents** for the full capability set; red-teaming is native-only. External agents can still be run through `evaluate` (only Text Match and Journey Success apply).
- **Python `@tool` functions** with type hints and docstrings for `quick-eval`, `generate`, and `analyze --mode enhanced` (`--tools-path` points at the folder).
- **Names.** Every agent's `display_name` should equal its `name`; test cases reference agents and tools by `name`.
- **Layout** (any layout works; this is the one the examples use):
  ```
  <project>/
  ├── agents/            # one YAML per agent, collaborators listed by name
  ├── tools/             # Python modules with @tool functions
  ├── knowledge_bases/   # optional
  └── evaluations/       # test cases, configs, attacks, results
  ```
- **Import order:** tools → knowledge bases → collaborators → orchestrator. Agents are usable right after import; no deploy step is needed for evaluation on SaaS or DevEd.

## 6. Shell environment

```bash
export VENV_ACTIVATE=/path/to/venv/bin/activate     # mandatory; every emitted command sources it
export WO_API_KEY="$(...)"                           # optional; token refresh during long SaaS runs
```

## 7. Quick install summary

```bash
python3.12 -m venv ~/agent-ops-venv && source ~/agent-ops-venv/bin/activate
echo 'export VENV_ACTIVATE=$HOME/agent-ops-venv/bin/activate' >> ~/.zshrc
pip install "ibm-watsonx-orchestrate[agentops]>=2.18.0,<3.0.0"
orchestrate env add --name <env> --url <instance url>
orchestrate env activate <env> --api-key "$(python3 -c 'import json,os;print(json.load(open(os.path.expanduser("~/.wxo-key.json")))["apikey"])')"
orchestrate agents list            # confirm your agent is there; check for name collisions on shared instances
# open the project in Bob → "Evaluate this agent"
```

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `401` / `Unauthorized` from the framework mid-run | SaaS token expired | Re-activate the environment; export `WO_API_KEY` for refresh |
| `Scope not found: Scope{scopeType='SERVICE', scopeId='<uuid>'}` | the API key is not for the activated instance | Confirm which instance the key belongs to; activate that environment or `env add` it |
| `400 Bad Request` from `iam.cloud.ibm.com/identity/token` | a `.env` in an ancestor folder overrides `WO_INSTANCE`/`WO_API_KEY` | `python3 -c "from dotenv import find_dotenv; print(repr(find_dotenv()))"`; move the file aside |
| Agent not found by the framework | wrong active environment, or the name in the test case differs from `orchestrate agents list` | Fix the environment or the `agent` field |
| Many `Tool with ID '<uuid>' not found` warnings in `agents list`, then `KeyError` before any case runs | orphaned tool references on a long-lived tenant | Remove dead references (`agents update`) or evaluate on a clean instance |
| Simulated user chats for 20 turns | default `max_user_turns` | Set `max_user_turns: 3` and end the story with "reply END and nothing else" |
| `quick-eval` lists schema mismatches for `chat_with_collaborator_*` | handoffs are reported as tool calls | Noise on multi-agent systems; read the other rows |
| `analyze` raises a validation error on `text_match` | framework 1.5.2 writes a number; `analyze` expects the enum string | Normalize a copy of the run folder (recipe in `reference/module-analyze.md`) |
| `red-teaming plan` produced goals unrelated to the policy | planner output quality | Review every file; hand-author the success goal |
| DevEd: `docker --context ibm-watsonx-orchestrate ps` returns `EOF` | degraded Lima VM | `orchestrate server stop`, move `~/.lima/ibm-watsonx-orchestrate` aside, start again |
| DevEd: traces search returns nothing | server started without `-i` | Restart with `orchestrate server start -e .env -i` |
