# Module: Langfuse (dollars with the least custom code)

**TRIGGER:** the user wants Langfuse connected to the instance, asks why Langfuse shows $0, how to price watsonx models in Langfuse, how to attribute cost by use case or version, or how to read cost per session.

Authoritative docs: https://developer.watson-orchestrate.ibm.com/llm/observability.md (integration), https://langfuse.com/docs (models and pricing, API).

---

## Ownership gate (RULE 3)

```bash
source "$VENV_ACTIVATE" && \
orchestrate settings observability langfuse get
```

- Output shows an active integration → **someone already exports this instance's traces.** If that is not the user's project, stop here: configuring would redirect the whole instance. Use platform traces (`module-sources.md`) or ask the owner for read access to their project.
- No integration and the user owns the instance → continue.

Availability: SaaS Trial, Essentials, and Standard (non-isolated) on IBM Cloud; commercial on AWS; Developer Edition via `server start -l`.

---

## 1. Connect the instance

Hosted Langfuse (Langfuse Cloud or self-hosted). Keys come from the Langfuse project settings; the user exports them, Bob never types them:

```bash
# --url is the OTLP endpoint of the Langfuse host; --health-uri the host itself; the public key goes in --config-json
source "$VENV_ACTIVATE" && \
orchestrate settings observability langfuse configure \
  --url "${LANGFUSE_HOST}/api/public/otel" \
  --api-key "${LANGFUSE_SECRET_KEY}" \
  --health-uri "${LANGFUSE_HOST}" \
  --config-json "{\"public_key\": \"${LANGFUSE_PUBLIC_KEY}\"}" && \
orchestrate settings observability langfuse get
```

File form (`--config-file langfuse.yaml`): `spec_version: v1`, `kind: langfuse`, `project_id`, `api_key`, `url`, `host_health_uri`, `config_json: {public_key: ...}`, `mask_pii: true`. `mask_pii: true` is the right default for production traffic. `orchestrate settings observability langfuse remove` disconnects.

Developer Edition: `orchestrate server start -e .env -l` (local Langfuse at `http://localhost:3010`, user `orchestrate@ibm.com`, password printed on first start; `-l` and `-i` are exclusive). `orchestrate evaluations evaluate … --with-langfuse` additionally stores evaluation metrics in Langfuse.

Verify: run one conversation, then open the Langfuse project → Traces; the trace appears within a minute with `GENERATION` observations and token usage.

---

## 2. Price the models

Langfuse computes cost only for models it has a price for; watsonx-served model names (`openai/gpt-oss-120b`, `ibm/granite-4-h-small`, …) are not in its built-in list, so cost shows as 0 until you add them. Prices apply to generations ingested **after** registration.

```bash
# per-million prices from assets/prices.yaml or the provider's list; the pattern must match the model name Langfuse receives
export LANGFUSE_HOST=... LANGFUSE_PUBLIC_KEY=... LANGFUSE_SECRET_KEY=...   # the user exports these
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/langfuse_cost_report.py \
  --register-model gpt-oss-120b \
  --match-pattern "(?i)^((watsonx|groq|bedrock)[./])?(openai[./])?gpt-oss-120b.*$" \
  --input-price-per-million 0.159 --output-price-per-million 0.636
```

Repeat per model the agents use (`llm:` in the agent YAMLs). The same can be done in the Langfuse UI (Settings → Models). Verify with one new conversation: the trace's total cost is now > 0.

---

## 3. Read cost

```bash
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/langfuse_cost_report.py --since 2h
source "$VENV_ACTIVATE" && python3 .bob/skills/cost-management/scripts/langfuse_cost_report.py --since 24h --session <thread id>
```

Per session (one session = one conversation; an evaluation run yields one session per case), per model, totals, and the models still unpriced. For the five-layer analysis, continue in `module-report.md`.

Langfuse UI: Dashboard (cost over time, by model), Traces (per conversation), Sessions (per thread). Finance-facing views can be built from the Metrics API (dimensions model, trace name, tags, environment; measures total cost and tokens).

---

## 4. Attribution by use case, version, and tenant

Langfuse aggregates by **session**, **tags**, **trace name**, **user id**, and **environment**. The platform sets the session id to the conversation thread; everything else is set by the application that calls the agent:

- one agent (and one trace name) per use case keeps attribution trivial;
- for shared agents, the calling application adds `tags` such as `use_case:<name>` and `version:<v>` (and a `user_id` per tenant) through the runs API metadata where supported, or by posting a **score** on the trace afterwards (`POST /api/public/scores`, `dataType: CATEGORICAL`), which is also how a human review label gets attached;
- Developer Edition evaluation runs with `--with-langfuse` arrive already grouped per test case.

---

## Common failures (curated)

| Symptom | Cause | Fix |
|---|---|---|
| `langfuse get` shows a project the user does not recognize | another team configured the instance | stop (RULE 3); use platform traces or ask the owner |
| Traces appear but cost is 0 | model not priced, or priced after the traces were ingested | register the model; look at new traces |
| No traces arrive after `configure` | wrong OTLP URL (`/api/public/otel`), wrong host region, or plan not eligible | check `--url`/`--health-uri`, region (`cloud.langfuse.com` vs `us.`/`eu.`), plan |
| `langfuse_cost_report.py` → 401 | keys from another project or environment | re-export the project's keys |
| Script errors mentioning deprecated endpoints | old `langfuse` SDK | `pip install -U langfuse` |
| 429 from Langfuse Cloud | free-tier rate limit | smaller windows; the script pages at 50; wait a minute |
| Numbers differ from the Control Plane | Langfuse counts what was exported after `configure`; the Control Plane counts everything | compare equal windows after the integration date |

---

## Done when

- Integration verified (`langfuse get` + a new trace in the project) **or** the ownership gate stopped it, with the platform-traces path offered instead.
- Every model the agents use is priced; a fresh trace shows cost > 0.
- Attribution plan agreed (per-use-case agents, tags, scores) and the first cost read-out produced.
