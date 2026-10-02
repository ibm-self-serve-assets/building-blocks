# Module: Observability (traces)

**TRIGGER:** the user wants to see what happened in a conversation (handoffs, tool calls, arguments, model, tokens, latency), search or export traces, use the traces Python API or REST API, link a chat run to its trace, or asks where the dashboards are.

Cost in dollars (Langfuse) is not in this module; route to the Cost Management building block.

Authoritative docs: https://developer.watson-orchestrate.ibm.com/traces/overview.md, `traces/traces_with_cli.md`, `traces/traces_with_python.md`.

---

## Where traces come from

| Target | Availability |
|---|---|
| SaaS | on by default; the traces API needs an identity with admin privileges on the instance |
| Developer Edition | only when the server was started with `--with-ibm-telemetry` / `-i` (not together with `-l`) |
| Product UI | **Agentic Control Plane** → observability (trace details per conversation), agent analytics, and the FinOps view (token consumption; preview) |

A trace is the span tree of one request: the orchestrator run, each `chat_with_collaborator_*` handoff, each tool call with input and output, and each model generation with `model` and `usage` (tokens). *Observed on SaaS:* the tree is complete about 15 seconds after the run finishes; search windows are limited to 4 hours; observation lookups are rate limited to a few per minute.

---

## Inputs

- Target environment (Q1) activated.
- A time window, and ideally a `session_id`, `user_id`, or a `trace_id`. The runs API stream (`POST /v1/orchestrate/runs?stream=true`) carries the `trace_id` on the `message.created` event, so an application can store it per conversation.

## Read-only diagnostics

1. `orchestrate env list` — the right environment is active.
2. Low-limit probe: `orchestrate observability traces search --last 1h --limit 5`. Empty on DevEd → the server is running without `-i`. Empty on SaaS → no traffic in the window, or the identity lacks admin rights (403).

---

## CLI

### `traces_search`

```bash
# --last replaces --start-time/--end-time; keep windows <= 4h on SaaS.
# --user-id / --session-id narrow the search; the agent-name / span-count filters are deprecated and ignored.
source "$VENV_ACTIVATE" && \
orchestrate observability traces search \
  --last 1h \
  --limit 20 \
  --sort-field start_time --sort-direction desc
```

Explicit window (format `%Y-%m-%dT%H:%M:%S`, `%Y-%m-%d %H:%M:%S`, or `%Y-%m-%d`):

```bash
source "$VENV_ACTIVATE" && \
orchestrate observability traces search \
  --start-time "$(date -u -v-2H +%Y-%m-%dT%H:%M:%S)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%S)" \
  --session-id "<session id>" \
  --limit 50
```

### `traces_export`

```bash
# One trace, all observations, pretty JSON (default) to a file.
source "$VENV_ACTIVATE" && \
orchestrate observability traces export \
  --trace-id <32-hex trace id> \
  --output traces/<trace id>.json
```

*Observed on ADK 2.18.0 against IBM Cloud SaaS:* this command (and the Python `fetch_trace_observations`) fails with `400 VALIDATION_ERROR: fromStartTime is required` because the observations endpoint now demands a time window of at most 4 hours. Until the CLI sends one, use the REST call below or `trace_cost.py --trace-id <id> --save traces/` from the `cost-management` skill, which fetches with the window and prices the generations.

Bob then reads the file and summarizes: the root span, the handoff sequence, each tool call with arguments and result, each generation's model and token usage, the slowest spans, and any error spans.

---

## Python

```python
# traces_report.py — search the last hour, export the slowest trace, list generations with tokens.
from datetime import datetime, timedelta, timezone
from ibm_watsonx_orchestrate.cli.commands.observability.traces.traces_controller import TracesController
from ibm_watsonx_orchestrate.client.observability.traces.traces_client import TraceFilters, TraceSort

controller = TracesController()                       # uses the active environment
end = datetime.now(timezone.utc)
filters = TraceFilters(start_time=end - timedelta(hours=1), end_time=end)   # add session_ids=[...] or user_ids=[...]
search = controller.search_traces(filters=filters, sort=TraceSort(field="start_time", direction="desc"))

if search.traceSummaries:
    slowest = max(search.traceSummaries, key=lambda t: t.durationMs or 0)
    obs, _ = controller.export_trace_to_json(slowest.traceId, output_file=f"trace_{slowest.traceId[:8]}.json")
    for o in obs.observations or []:
        if o.type == "GENERATION":
            print(o.name, o.model, o.usage)
```

Run with `source "$VENV_ACTIVATE" && python3 traces_report.py`. Models: `Observation` (`id`, `traceId`, `type`, `name`, `startTime`, `endTime`, `model`, `input`, `output`, `metadata`, `usage`), `TraceSummary` (`traceId`, `durationMs`, `agentNames`, `sessionIds`, `userIds`), `TraceSearchResponse`, `ObservationsExportResponse`.

---

## REST

The CLI and Python wrap `GET /v1/agentops-v3/traces` and `GET /v1/agentops-v3/observations` on the instance. Call them with the bearer token from the token cache, read inside the shell (RULE 5):

```bash
# Observations for one trace. Replace <ENV> with the environment name and <TRACE_ID> with the id.
TOKEN=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.cache/orchestrate/credentials.yaml')))['auth']['<ENV>']['wxo_mcsp_token'])") && \
INSTANCE=$(python3 -c "import yaml,os; print(yaml.safe_load(open(os.path.expanduser('~/.config/orchestrate/config.yaml')))['environments']['<ENV>']['wxo_url'])") && \
curl -sS -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" \
  "${INSTANCE}/v1/agentops-v3/observations?traceId=<TRACE_ID>&fromStartTime=$(date -u -v-4H +%Y-%m-%dT%H:%M:%SZ)&toStartTime=$(date -u +%Y-%m-%dT%H:%M:%SZ)&limit=200" \
  | python3 -m json.tool | head -80
```

*Observed on SaaS:* `fromStartTime`/`toStartTime` are required and may span at most 4 hours; calls are limited to about four per minute. The response is `{"data": [observation, ...], "meta": {"cursor": ...}}`; a generation has `type: GENERATION`, `name: WatsonxChatModel.chat`, `model` without the provider prefix (`openai/gpt-oss-120b`), `usage {input, output, total}`, `latency`, and `metadata.attributes["langfuse.session.id"]` = the conversation thread id. The agent that made a generation is the nearest ancestor span carrying `agent.id` / `agent.name` (collaborators appear under `collaborator` spans). Cache what you fetch. Traces by conversation: `GET /v1/agentops-v3/traces?sessionId=<thread id>&fromTimestamp=…&toTimestamp=…`.

---

## Reading a trace (what Bob reports)

1. **Journey:** root span → handoffs in order → tools called by each collaborator. Compare with the expected journey from the test case; a missing handoff or tool is a routing or instruction problem.
2. **Arguments and results:** the exact tool input and output; this is where "the agent approved politely with a reference number" turns out to be a letter generated without the AML result.
3. **Model and tokens per generation:** which model each agent used and the input/output tokens; large input counts on later turns are context growth.
4. **Latency:** the slowest spans; tool latency versus model latency.
5. **Errors:** spans with error status, retries, fallbacks.

Token totals per run are also available without traces: the runs API returns `usage.model_usage[]` on `message.completed`.

---

## Done when

- Trace ids found for the conversation in question (or a clear statement that none exist and why).
- The trace exported and summarized: journey, arguments, model and tokens, slowest spans, errors.
- A next step named: fix the test case or agent (`module-analyze.md`), add a runtime control (`agent-controls` skill), or quantify cost (Cost Management).
