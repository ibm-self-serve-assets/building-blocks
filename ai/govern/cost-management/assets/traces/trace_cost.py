"""Tokens and dollars for watsonx Orchestrate conversations, from platform traces.

Reads exported trace JSON files, or fetches traces from the active (or --env) orchestrate environment through
GET /v1/agentops-v3/observations with the time window the API requires. Prices generations with a YAML price
table (USD per 1M tokens) and attributes them to the agent that made them. With --eval-run it joins the traces
to an Agent Ops run (thread ids from <case>.metadata.json, is_success from summary_metrics.csv).

Usage:
  python trace_cost.py traces/*.json
  python trace_cost.py --trace-id <id> [--trace-id <id> ...] [--env <name>] [--since 4h] [--save traces/]
  python trace_cost.py --from-search traces.txt [--limit 20] [--save traces/]        # ids from a saved `traces search` table
  python trace_cost.py --eval-run results/evaluate_v2/<timestamp>/ [--save traces/] [--csv cost.csv]
  options: --prices prices.yaml  --price <model>=<in>,<out>  --from/--to ISO-8601  --rate 4  --json out.json

Observed on ADK 2.18.0 / IBM Cloud SaaS (2026-10): the observations endpoint needs fromStartTime/toStartTime at
most 4 hours apart and allows a few calls per minute; `orchestrate observability traces export` does not send the
window and fails. The bearer token is read from ~/.cache/orchestrate/credentials.yaml and never printed.
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pip install pyyaml")

HERE = Path(__file__).resolve().parent
DEFAULT_PRICES = next((p for p in (HERE / "prices.yaml", HERE.parent / "assets" / "prices.yaml") if p.exists()), None)
TRACE_ID = re.compile(r"\b[0-9a-f]{32}\b")


# ----------------------------------------------------------------------------- args

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("files", nargs="*", help="exported trace JSON files ({'data': [...]} or a list of observations)")
    p.add_argument("--trace-id", action="append", default=[], help="fetch this trace (repeatable)")
    p.add_argument("--from-search", help="file with the output of `orchestrate observability traces search`; every trace id in it is fetched")
    p.add_argument("--eval-run", help="Agent Ops run folder: joins traces to cases by thread id and brings is_success")
    p.add_argument("--limit", type=int, help="fetch at most this many traces")
    p.add_argument("--env", help="orchestrate environment name (default: the active one)")
    p.add_argument("--since", default="4h", help="fetch window ending now: 30m, 2h, 4h (API maximum 4h)")
    p.add_argument("--from", dest="from_", help="fetch window start, ISO 8601 (overrides --since)")
    p.add_argument("--to", help="fetch window end, ISO 8601 (default: start + 4h, capped at now)")
    p.add_argument("--rate", type=float, default=4.0, help="API calls per minute (default 4)")
    p.add_argument("--save", help="directory to save fetched traces as <trace id>.json")
    p.add_argument("--prices", default=str(DEFAULT_PRICES) if DEFAULT_PRICES else None, help="price table YAML (USD per 1M tokens)")
    p.add_argument("--price", action="append", default=[], metavar="MODEL=IN,OUT", help="override or add a price, per 1M tokens")
    p.add_argument("--csv", help="write one row per trace (and per case with --eval-run)")
    p.add_argument("--json", help="write the full summary as JSON")
    return p.parse_args()


# ----------------------------------------------------------------------------- orchestrate credentials

def orchestrate_target(env: str | None) -> tuple[str, str, str]:
    cfg = yaml.safe_load(open(os.path.expanduser("~/.config/orchestrate/config.yaml")))
    env = env or (cfg.get("context") or {}).get("active_environment")
    if not env:
        sys.exit("no active orchestrate environment; run `orchestrate env activate <name>` or pass --env")
    url = (cfg.get("environments") or {}).get(env, {}).get("wxo_url")
    creds = yaml.safe_load(open(os.path.expanduser("~/.cache/orchestrate/credentials.yaml")))
    token = ((creds.get("auth") or {}).get(env) or {}).get("wxo_mcsp_token")
    if not (url and token):
        sys.exit(f"environment '{env}' has no cached url/token; run `orchestrate env activate {env}`")
    return env, url.rstrip("/"), token


class Api:
    def __init__(self, env: str | None, rate: float):
        self.env, self.base, self._token = orchestrate_target(env)
        self.min_gap = 60.0 / max(rate, 0.1)
        self._last = 0.0

    def get(self, path: str, params: dict) -> dict:
        wait = self.min_gap - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        url = f"{self.base}{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self._token}", "Accept": "application/json"})
        self._last = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            if e.code == 401:
                sys.exit(f"401 from the instance: the cached token for '{self.env}' expired; run `orchestrate env activate {self.env} --api-key ...`")
            if e.code == 429:
                time.sleep(self.min_gap * 2)
                return self.get(path, params)
            sys.exit(f"HTTP {e.code} on {path}: {body}")

    def observations(self, trace_id: str, start: datetime, end: datetime) -> list[dict]:
        out, cursor = [], None
        while True:
            params = {"traceId": trace_id, "fromStartTime": iso(start), "toStartTime": iso(end), "limit": 500}
            if cursor:
                params["cursor"] = cursor
            d = self.get("/v1/agentops-v3/observations", params)
            out.extend(d.get("data") or [])
            cursor = (d.get("meta") or {}).get("cursor")
            if not cursor:
                return out

    def traces_for_session(self, session_id: str, start: datetime, end: datetime) -> list[dict]:
        d = self.get("/v1/agentops-v3/traces", {"sessionId": session_id, "fromTimestamp": iso(start), "toTimestamp": iso(end), "limit": 50})
        return d.get("data") or []


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def window(args: argparse.Namespace) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if args.from_:
        start = datetime.fromisoformat(args.from_.replace("Z", "+00:00")).astimezone(timezone.utc)
        end = datetime.fromisoformat(args.to.replace("Z", "+00:00")).astimezone(timezone.utc) if args.to else min(now, start + timedelta(hours=4))
    else:
        m = re.fullmatch(r"(\d+)\s*([mhd])", args.since.strip())
        if not m:
            sys.exit("--since takes 30m, 2h or 4h")
        n, unit = int(m.group(1)), m.group(2)
        delta = timedelta(minutes=n) if unit == "m" else timedelta(hours=n) if unit == "h" else timedelta(days=n)
        start, end = now - delta, now
    if end - start > timedelta(hours=4, minutes=1):
        sys.exit("the observations API accepts windows of at most 4 hours; narrow --since or pass --from/--to around the trace")
    return start, end


# ----------------------------------------------------------------------------- prices

def load_prices(path: str | None, overrides: list[str]) -> tuple[dict[str, tuple[float, float]], dict]:
    table: dict[str, tuple[float, float]] = {}
    meta = {"source": None, "as_of": None}
    if path and Path(path).exists():
        d = yaml.safe_load(open(path)) or {}
        meta = {"source": d.get("source"), "as_of": d.get("as_of")}
        per = float(d.get("per_tokens") or 1_000_000)
        for model, p in (d.get("models") or {}).items():
            table[str(model)] = (float(p["input"]) / per, float(p["output"]) / per)
    for o in overrides:
        model, _, prices = o.partition("=")
        i, _, out = prices.partition(",")
        table[model.strip()] = (float(i) / 1_000_000, float(out) / 1_000_000)
    return table, meta


def price_for(model: str | None, table: dict[str, tuple[float, float]]) -> tuple[float, float] | None:
    if not model:
        return None
    candidates = [model]
    parts = model.split("/")
    if len(parts) >= 3:
        candidates.append("/".join(parts[1:]))     # drop the provider prefix: watsonx/openai/x -> openai/x
    candidates.append(parts[-1])                   # bare model name
    by_tail = {k.split("/")[-1]: v for k, v in table.items()}
    for c in candidates:
        if c in table:
            return table[c]
    tail = parts[-1]
    if tail in by_tail:
        return by_tail[tail]
    return None


# ----------------------------------------------------------------------------- trace analysis

def attrs(o: dict) -> dict:
    return ((o.get("metadata") or {}).get("attributes") or {})


def tokens(o: dict) -> tuple[int, int]:
    u = o.get("usage") or o.get("usageDetails") or {}
    i = u.get("input") or o.get("promptTokens") or o.get("inputTokens") or 0
    out = u.get("output") or o.get("completionTokens") or o.get("outputTokens") or 0
    return int(i or 0), int(out or 0)


def agent_of(o: dict, by_id: dict[str, dict]) -> str:
    """Nearest ancestor that names a collaborator, else the agent on the root span."""
    cur, hops = o, 0
    while cur and hops < 30:
        a = attrs(cur)
        if a.get("collaborator.name"):
            return str(a["collaborator.name"])
        if a.get("agent.name"):
            return str(a["agent.name"])
        cur = by_id.get(cur.get("parentObservationId") or "")
        hops += 1
    return "(unknown agent)"


def analyze(observations: list[dict], prices: dict[str, tuple[float, float]]) -> dict:
    by_id = {o["id"]: o for o in observations if o.get("id")}
    gens = [o for o in observations if o.get("type") == "GENERATION"]
    roots = [o for o in observations if not o.get("parentObservationId")]
    starts = [o.get("startTime") for o in observations if o.get("startTime")]
    ends = [o.get("endTime") for o in observations if o.get("endTime")]
    session = next((attrs(o).get("langfuse.session.id") or attrs(o).get("thread_id") for o in observations if attrs(o).get("langfuse.session.id") or attrs(o).get("thread_id")), None)
    per_model: dict[str, dict] = defaultdict(lambda: {"generations": 0, "input": 0, "output": 0, "cost": 0.0, "priced": True})
    per_agent: dict[str, dict] = defaultdict(lambda: {"generations": 0, "input": 0, "output": 0, "cost": 0.0})
    total_in = total_out = 0
    cost = 0.0
    unpriced: set[str] = set()
    for g in gens:
        i, out = tokens(g)
        model = g.get("model") or attrs(g).get("llm.model_name") or "(no model)"
        agent = agent_of(g, by_id)
        p = price_for(model, prices)
        c = (i * p[0] + out * p[1]) if p else 0.0
        if not p:
            unpriced.add(model)
            per_model[model]["priced"] = False
        for bucket in (per_model[model], per_agent[agent]):
            bucket["generations"] += 1
            bucket["input"] += i
            bucket["output"] += out
            bucket["cost"] += c
        total_in += i
        total_out += out
        cost += c
    start, end = (min(starts) if starts else None), (max(ends) if ends else None)
    duration = None
    if start and end:
        duration = round((parse_ts(end) - parse_ts(start)).total_seconds(), 1)
    return {
        "trace_id": next((o.get("traceId") for o in observations if o.get("traceId")), None),
        "root": roots[0].get("name") if roots else None,
        "session_id": session,
        "start": start, "duration_s": duration,
        "observations": len(observations), "generations": len(gens),
        "input_tokens": total_in, "output_tokens": total_out,
        "cost_usd": None if unpriced else round(cost, 6),
        "cost_priced_part_usd": round(cost, 6),
        "unpriced_models": sorted(unpriced),
        "per_model": dict(per_model), "per_agent": dict(per_agent),
    }


def parse_ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


# ----------------------------------------------------------------------------- inputs

def load_file(path: str) -> list[dict]:
    d = json.load(open(path))
    if isinstance(d, dict):
        return d.get("data") or d.get("observations") or []
    return d


def ids_from_search(path: str) -> list[str]:
    seen, out = set(), []
    for tid in TRACE_ID.findall(open(path, encoding="utf-8", errors="replace").read()):
        if tid not in seen:
            seen.add(tid)
            out.append(tid)
    return out


def eval_run_cases(run_dir: str) -> tuple[dict[str, str], dict[str, dict]]:
    """thread id -> case name, and case name -> summary_metrics row."""
    threads: dict[str, str] = {}
    for mf in glob.glob(os.path.join(run_dir, "*.metadata.json")):
        case = os.path.basename(mf).replace(".metadata.json", "")
        tid = (json.load(open(mf)) or {}).get("thread_id")
        if tid:
            threads[tid] = case
    rows: dict[str, dict] = {}
    sm = os.path.join(run_dir, "summary_metrics.csv")
    if os.path.exists(sm):
        for r in csv.DictReader(open(sm, encoding="utf-8")):
            rows[r.get("dataset_name", "")] = r
    if not threads:
        sys.exit(f"no <case>.metadata.json with thread_id under {run_dir}")
    return threads, rows


# ----------------------------------------------------------------------------- main

def main() -> None:
    args = parse_args()
    prices, price_meta = load_prices(args.prices, args.price)
    results: list[dict] = []
    case_of_trace: dict[str, str] = {}
    sm_rows: dict[str, dict] = {}

    for f in args.files:
        results.append(analyze(load_file(f), prices) | {"source": f})

    wanted: list[str] = list(args.trace_id)
    if args.from_search:
        wanted += ids_from_search(args.from_search)

    api: Api | None = None
    if wanted or args.eval_run:
        api = Api(args.env, args.rate)
        start, end = window(args)
        if args.eval_run:
            threads, sm_rows = eval_run_cases(args.eval_run)
            print(f"eval run {args.eval_run}: {len(threads)} cases; looking up traces by thread id in {iso(start)} .. {iso(end)}")
            for thread, case in threads.items():
                for t in api.traces_for_session(thread, start, end):
                    case_of_trace[t["id"]] = case
                    wanted.append(t["id"])
            missing = sorted(set(threads.values()) - set(case_of_trace.values()))
            if missing:
                print(f"no trace found in the window for: {', '.join(missing)} (traces older than the window need --from/--to)")
        seen: set[str] = set()
        wanted = [t for t in wanted if not (t in seen or seen.add(t))]
        if args.limit:
            wanted = wanted[: args.limit]
        if args.save:
            Path(args.save).mkdir(parents=True, exist_ok=True)
        for n, tid in enumerate(wanted, 1):
            print(f"fetching {n}/{len(wanted)} {tid}", file=sys.stderr)
            obs = api.observations(tid, start, end)
            if args.save:
                Path(args.save, f"{tid}.json").write_text(json.dumps({"data": obs, "meta": {"cursor": None}}))
            r = analyze(obs, prices) | {"source": "api"}
            r["trace_id"] = r["trace_id"] or tid
            results.append(r)

    if not results:
        sys.exit("nothing to analyze: pass files, --trace-id, --from-search or --eval-run")

    for r in results:
        r["case"] = case_of_trace.get(r["trace_id"] or "")
        row = sm_rows.get(r["case"] or "")
        r["is_success"] = (row.get("is_success") == "True") if row else None

    report(results, price_meta, bool(args.eval_run))
    if args.csv:
        write_csv(results, args.csv)
        print(f"\nCSV: {args.csv}")
    if args.json:
        Path(args.json).write_text(json.dumps({"prices": price_meta, "traces": results}, indent=2, default=str))
        print(f"JSON: {args.json}")


def fmt_cost(r: dict) -> str:
    return f"{r['cost_usd']:.4f}" if r["cost_usd"] is not None else f"~{r['cost_priced_part_usd']:.4f}+?"


def report(results: list[dict], price_meta: dict, eval_mode: bool) -> None:
    label = f"prices: {price_meta.get('source') or 'overrides only'} (as of {price_meta.get('as_of') or 'n/a'}), USD, model-inference list price"
    print(f"\n{len(results)} trace(s) · {label}\n")
    head = f"{'case' if eval_mode else 'trace':34} {'result':7} {'start (UTC)':20} {'dur s':>6} {'gens':>4} {'input':>7} {'output':>6} {'$':>9}  agents"
    print(head)
    for r in sorted(results, key=lambda x: x.get("start") or ""):
        name = (r.get("case") or r.get("trace_id") or r.get("source") or "")[:34]
        res = {True: "pass", False: "FAIL", None: "-"}[r.get("is_success")]
        start = (r.get("start") or "")[:19].replace("T", " ")
        names = list(r["per_agent"])
        prefix = os.path.commonprefix(names) if len(names) > 1 else ""
        prefix = prefix[: prefix.rfind("_") + 1] if "_" in prefix else ""   # strip a shared project prefix such as agentops_d1_
        agents = ", ".join(a[len(prefix):] or a for a in names)
        print(f"{name:34} {res:7} {start:20} {str(r['duration_s'] or ''):>6} {r['generations']:>4} {r['input_tokens']:>7} {r['output_tokens']:>6} {fmt_cost(r):>9}  {agents}")

    per_model: dict[str, dict] = defaultdict(lambda: {"generations": 0, "input": 0, "output": 0, "cost": 0.0, "priced": True})
    per_agent: dict[str, dict] = defaultdict(lambda: {"generations": 0, "input": 0, "output": 0, "cost": 0.0})
    for r in results:
        for m, s in r["per_model"].items():
            for k in ("generations", "input", "output", "cost"):
                per_model[m][k] += s[k]
            per_model[m]["priced"] &= s["priced"]
        for a, s in r["per_agent"].items():
            for k in ("generations", "input", "output", "cost"):
                per_agent[a][k] += s[k]

    print(f"\n{'model':44} {'gens':>5} {'input':>8} {'output':>7} {'$':>9}")
    for m, s in sorted(per_model.items(), key=lambda kv: -kv[1]["input"]):
        dollars = f"{s['cost']:.4f}" if s["priced"] else "unpriced"
        print(f"{m:44} {s['generations']:>5} {s['input']:>8} {s['output']:>7} {dollars:>9}")
    print(f"\n{'agent':44} {'gens':>5} {'input':>8} {'output':>7} {'$':>9}")
    for a, s in sorted(per_agent.items(), key=lambda kv: -kv[1]["input"]):
        print(f"{a:44} {s['generations']:>5} {s['input']:>8} {s['output']:>7} {s['cost']:>9.4f}")

    tin = sum(r["input_tokens"] for r in results)
    tout = sum(r["output_tokens"] for r in results)
    priced = [r for r in results if r["cost_usd"] is not None]
    tcost = sum(r["cost_usd"] for r in priced)
    print(f"\nTotal: {tin + tout} tokens ({tin} in / {tout} out) · ${tcost:.4f} across {len(priced)} fully priced trace(s)")
    if results:
        print(f"Average per conversation: {round((tin + tout) / len(results))} tokens · ${tcost / max(1, len(priced)):.4f}")
    unpriced = sorted({m for r in results for m in r["unpriced_models"]})
    if unpriced:
        print(f"Unpriced models (tokens counted, dollars not): {', '.join(unpriced)} — add them to the price table or pass --price")
    if eval_mode:
        successes = sum(1 for r in results if r.get("is_success"))
        if successes:
            print(f"$ per successful journey: ${tcost / successes:.4f} ({successes} successes of {len(results)} traced cases)")
        else:
            print("$ per successful journey: n/a (no successful cases among the traced ones)")


def write_csv(results: list[dict], path: str) -> None:
    fields = ["trace_id", "case", "is_success", "session_id", "start", "duration_s", "generations", "input_tokens", "output_tokens", "cost_usd", "models", "agents", "unpriced_models"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in results:
            w.writerow({**{k: r.get(k) for k in fields if k not in ("models", "agents", "unpriced_models")},
                        "models": ";".join(r["per_model"]), "agents": ";".join(r["per_agent"]), "unpriced_models": ";".join(r["unpriced_models"])})


if __name__ == "__main__":
    main()
