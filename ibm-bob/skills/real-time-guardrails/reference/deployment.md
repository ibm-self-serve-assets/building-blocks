# Deployment

**TRIGGER:** Load at Phase 5 — when user asks about deployment modes (library vs REST vs MCP), Dockerfile/Kubernetes, scaling, network egress, multi-tenant deployment patterns, SDK version upgrades, or asks for a production checklist.

---

## Deployment modes (pick one)

| Mode | When | How | Pros | Cons |
|---|---|---|---|---|
| **library_in_process** | Agent is a Python service and you control its container | Add package to agent's `pyproject.toml` or `requirements.txt`. Build evaluator ONCE at app startup, reuse per request. | Lowest latency (no HTTP hop). Single deployable. | Pinned to Python. Can't share across non-Python services. |
| **rest_sidecar** | Agent is non-Python OR you want to share guardrails across multiple services | `real-time-guardrails serve --port 8090` as a separate container/process. Agent calls `/api/evaluate` over HTTP. | Language-agnostic. Independent scaling. Hot-reload guardrails without redeploying agent. | +5-20ms per request (localhost) or +50-200ms (cross-AZ). Extra deployable. |
| **mcp_tool** | Agent is built on MCP | Register `real-time-guardrails` as MCP server in agent's config. Agent calls `evaluate_*` tools. | Agent-native integration. Natural for any MCP-capable host (chat clients, IDE extensions, agent frameworks). | MCP transport overhead. Doesn't fit non-MCP agents. |

**Best fit by team:**
- Single-language Python agents → **library**
- Polyglot teams, multi-tenant deployments where policy changes more often than agent code → **REST**
- Agentic systems already on MCP → **MCP**

---

## Dockerfile

**Location:** in the building-blocks source repo at `ai-trust/real-time-guardrails/assets/sdk/Dockerfile` — NOT bundled with this skill. Pull from the source repo if you need the canonical Dockerfile.
**Base:** `python:3.11-slim`
**Expose:** 8080
**Cmd:** `real-time-guardrails serve --host 0.0.0.0 --port 8080`

**Build:**
```bash
docker build -t real-time-guardrails:0.1.0 assets/sdk/
```

**Run:**
```bash
docker run -d \
  --name guardrails \
  -p 8090:8080 \
  -e WATSONX_APIKEY="$WATSONX_APIKEY" \
  -e WXG_SERVICE_INSTANCE_ID="$WXG_SERVICE_INSTANCE_ID" \
  -e WXG_PROJECT_ID="$WXG_PROJECT_ID" \
  real-time-guardrails:0.1.0
```

## Kubernetes

**RULE:** mount credentials via Kubernetes Secrets, never bake into the image.

```yaml
envFrom:
  - secretRef:
      name: watsonx-guardrails-creds
```

---

## Scaling

- **Stateless:** the REST server is stateless per request. Horizontal scaling via N replicas is straightforward.
- **Load balancer:** round-robin LB in front of N replicas. Each request independent (no session affinity needed).
- **Bottleneck:** upstream IBM Cloud service, not the package itself. Granite Guardian and watsonx.ai have their own rate limits — check your IBM Cloud plan.
- **Connection pooling:** SDK reuses HTTP connections per evaluator instance. Build one evaluator per worker process, NOT per request.

---

## Network egress

**Required endpoints:**
- watsonx.governance service endpoint (region-specific) — used by Granite Guardian and all SDK-backed metrics
- `*.ml.cloud.ibm.com` (region-specific) — used by watsonx.ai LLM-judge metrics only

**Air-gap:** NOT supported. The SDK cannot run offline.

**Egress proxy:** if your environment requires outbound proxy, set `HTTPS_PROXY` env var before starting the server. The SDK respects standard requests-library proxy env vars.

**VPC co-location:** RECOMMENDED — deploy guardrails service in the same region/VPC as the agent to minimize latency.

---

## Multi-tenant patterns

### Pattern 1 — Single evaluator, per-call policy
**How:** one service, one evaluator instance. Pass `thresholds` + `fallback_messages` per request based on partner_id.

**When:** many partners, similar metric set, different thresholds.

```python
@app.post("/api/evaluate")
def evaluate(request):
    partner = request.headers.get("X-Partner-ID")
    policy = db.get_policy(partner)
    return ev.evaluate(
        **request.json,
        thresholds=policy["block"],
        flag_thresholds=policy["flag"],
        fallback_messages=policy["fallback"],
    )
```

### Pattern 2 — Evaluator per partner
**How:** one service, N evaluators at startup (one per partner with different `threshold_overrides=`).

**When:** few partners, very different policies, want isolation.

### Pattern 3 — Service per partner
**How:** N services, each with its own evaluator + YAML config.

**When:** strict isolation required (separate billing, blast radius).

---

## Upgrades

- **SDK version bumps:** the IBM SDK (`ibm-watsonx-gov`) ships breaking changes between minor versions. When upgrading: re-run integration tests against staging credentials before promoting to prod.
- **Metric catalog changes:** when the SDK adds new metrics (or renames columns), the package needs an update. Maintainer sync workflow in `assets/sdk/CONTRIBUTING.md`.
- **Threshold calibration:** re-calibrate thresholds quarterly against fresh sample data. Granite Guardian model updates can shift score distributions.

---

## Observability basics

Metrics to expose:
- `request_count` (per choke point)
- `p50`, `p95`, `p99` latency (per choke point)
- `block_rate`, `flag_rate` (per metric)
- `upstream_error_rate` (Granite Guardian or watsonx.ai 5xx)
- `llm_judge_token_count` (if `WXG_PROJECT_ID` set, for cost attribution)

---

## Production checklist

- [ ] Credentials in Kubernetes Secrets / equivalent, never in image
- [ ] Outbound HTTPS to required endpoints allowlisted by network policy
- [ ] AuditLogger wired to log aggregation (Splunk/ELK/CloudWatch)
- [ ] Dashboards: block/flag rate, latency, error rate, LLM cost
- [ ] Alerting: block-rate spike, upstream error spike, p95 latency regression
- [ ] Threshold policies version-controlled (YAML files in a repo)
- [ ] Failure mode documented: what happens when guardrails are degraded? (Fail-open vs fail-closed — partner's call)
- [ ] Runbook for credential rotation
