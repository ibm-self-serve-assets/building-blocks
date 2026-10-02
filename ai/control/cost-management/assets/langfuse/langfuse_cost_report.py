"""Cost and token report for watsonx Orchestrate agents from Langfuse.

Prerequisite: the watsonx Orchestrate instance exports traces to a Langfuse project you can read
(SaaS: `orchestrate settings observability langfuse configure ...`; Developer Edition: `orchestrate server start -l`).

Environment:
  LANGFUSE_HOST (or LANGFUSE_BASE_URL)   e.g. https://cloud.langfuse.com or http://localhost:3010
  LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY

Usage:
  python langfuse_cost_report.py --since 2h                         # generations started in the last 2 hours
  python langfuse_cost_report.py --since 24h --session <session id> # one conversation / one evaluation case
  python langfuse_cost_report.py --from 2026-10-01T00:00:00Z --to 2026-10-01T06:00:00Z
  python langfuse_cost_report.py --register-model gpt-oss-120b \
      --match-pattern "(?i)^((watsonx|groq|bedrock)[./])?(openai[./])?gpt-oss-120b.*$" \
      --input-price-per-million 0.159 --output-price-per-million 0.636   # then exit

Output: cost and tokens per session and per model, totals, and the models still without a price.
Uses the official Langfuse Python SDK (`pip install -U langfuse`); it tracks Langfuse's API changes
(the original list endpoints are deprecated in favour of v2 and scheduled to stop working in November 2026).
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

try:
    from langfuse import Langfuse
    from langfuse.api.resources.models.types.create_model_request import CreateModelRequest
except ImportError:  # pragma: no cover
    sys.exit("pip install -U langfuse")

PAGE = 50  # Langfuse Cloud free tier allows tens of requests per minute; keep pages moderate


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--since", help="relative window ending now: 30m, 2h, 1d")
    p.add_argument("--from", dest="from_", help="window start, ISO 8601 (UTC if no offset)")
    p.add_argument("--to", help="window end, ISO 8601; default now")
    p.add_argument("--session", help="only this session id")
    p.add_argument("--register-model", metavar="NAME", help="register pricing for a model and exit")
    p.add_argument("--match-pattern", help="regex Langfuse matches against the model name")
    p.add_argument("--input-price-per-million", type=float)
    p.add_argument("--output-price-per-million", type=float)
    return p.parse_args()


def client() -> Langfuse:
    host = os.environ.get("LANGFUSE_HOST") or os.environ.get("LANGFUSE_BASE_URL")
    if not (host and os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY")):
        sys.exit("set LANGFUSE_HOST (or LANGFUSE_BASE_URL), LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY")
    lf = Langfuse(host=host)
    try:
        lf.api.health.health()
    except Exception as exc:  # noqa: BLE001
        sys.exit(f"Langfuse not reachable at {host}: {exc}")
    return lf


def window(args: argparse.Namespace) -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    if args.since:
        m = re.fullmatch(r"(\d+)\s*([mhd])", args.since.strip())
        if not m:
            sys.exit("--since takes 30m, 2h or 1d")
        n, unit = int(m.group(1)), m.group(2)
        start = now - timedelta(minutes=n) if unit == "m" else now - timedelta(hours=n) if unit == "h" else now - timedelta(days=n)
        return start, now
    if args.from_:
        start = datetime.fromisoformat(args.from_.replace("Z", "+00:00"))
        end = datetime.fromisoformat(args.to.replace("Z", "+00:00")) if args.to else now
        return start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    return now - timedelta(hours=2), now


def register_model(lf: Langfuse, args: argparse.Namespace) -> None:
    if not (args.match_pattern and args.input_price_per_million is not None and args.output_price_per_million is not None):
        sys.exit("--register-model needs --match-pattern, --input-price-per-million and --output-price-per-million")
    model = lf.api.models.create(request=CreateModelRequest(
        model_name=args.register_model,
        match_pattern=args.match_pattern,
        unit="TOKENS",
        input_price=args.input_price_per_million / 1_000_000,
        output_price=args.output_price_per_million / 1_000_000,
        tokenizer_id="openai",
        tokenizer_config={"tokenizerModel": "gpt-4o"},
        start_date=None,
    ))
    print(f"registered {model.model_name} (id {model.id}); pricing applies to generations ingested from now on")


def traces_in_window(lf: Langfuse, start: datetime, end: datetime, session: str | None) -> dict[str, dict]:
    """trace id -> {session, name, tags}; observations do not carry the session id themselves."""
    out: dict[str, dict] = {}
    page = 1
    while True:
        resp = lf.api.trace.list(page=page, limit=PAGE, from_timestamp=start, to_timestamp=end, session_id=session)
        for t in resp.data:
            out[t.id] = {"session": t.session_id or "(no session)", "name": t.name, "tags": list(t.tags or [])}
        if page >= (resp.meta.total_pages or 1):
            break
        page += 1
    return out


def generations_in_window(lf: Langfuse, start: datetime, end: datetime) -> list:
    out = []
    page = 1
    while True:
        resp = lf.api.observations.get_many(page=page, limit=PAGE, type="GENERATION", from_start_time=start, to_start_time=end)
        out.extend(resp.data)
        if page >= (resp.meta.total_pages or 1):
            break
        page += 1
    return out


def tokens(obs) -> tuple[int, int, int]:
    d = obs.usage_details or {}
    if d:
        i, o = int(d.get("input", 0) or 0), int(d.get("output", 0) or 0)
        return i, o, int(d.get("total", i + o) or i + o)
    u = obs.usage
    if u:
        i, o = int(getattr(u, "input", 0) or 0), int(getattr(u, "output", 0) or 0)
        return i, o, int(getattr(u, "total", i + o) or i + o)
    return 0, 0, 0


def cost(obs) -> float | None:
    c = obs.cost_details or {}
    if "total" in c and c["total"] is not None:
        return float(c["total"])
    return None


def report(lf: Langfuse, start: datetime, end: datetime, session: str | None) -> None:
    traces = traces_in_window(lf, start, end, session)
    gens = generations_in_window(lf, start, end)
    if session:
        gens = [g for g in gens if g.trace_id in traces]
    if not gens:
        print(f"no generations between {start:%Y-%m-%d %H:%M} and {end:%Y-%m-%d %H:%M} UTC")
        return

    per_session: dict[str, dict] = defaultdict(lambda: {"gens": 0, "in": 0, "out": 0, "total": 0, "cost": 0.0, "priced": 0, "traces": set()})
    per_model: dict[str, dict] = defaultdict(lambda: {"gens": 0, "in": 0, "out": 0, "cost": 0.0, "priced": 0})
    for g in gens:
        meta = traces.get(g.trace_id, {"session": "(trace outside window)"})
        i, o, t = tokens(g)
        c = cost(g)
        model = g.model or "(no model)"
        for bucket in (per_session[meta["session"]], per_model[model]):
            bucket["gens"] += 1
            bucket["in"] += i
            bucket["out"] += o
            if c is not None:
                bucket["cost"] += c
                bucket["priced"] += 1
        per_session[meta["session"]]["total"] += t
        per_session[meta["session"]]["traces"].add(g.trace_id)

    print(f"Window {start:%Y-%m-%d %H:%M} → {end:%Y-%m-%d %H:%M} UTC · {len(traces)} traces · {len(gens)} generations\n")
    print(f"{'session':40} {'traces':>6} {'gens':>5} {'input':>9} {'output':>8} {'cost $':>10}")
    for sid, s in sorted(per_session.items(), key=lambda kv: -(kv[1]['in'] + kv[1]['out'])):
        print(f"{sid[:40]:40} {len(s['traces']):>6} {s['gens']:>5} {s['in']:>9} {s['out']:>8} {s['cost']:>10.4f}")
    print(f"\n{'model':40} {'gens':>5} {'input':>9} {'output':>8} {'cost $':>10} {'priced':>7}")
    for m, s in sorted(per_model.items(), key=lambda kv: -kv[1]['cost']):
        print(f"{m[:40]:40} {s['gens']:>5} {s['in']:>9} {s['out']:>8} {s['cost']:>10.4f} {s['priced']:>3}/{s['gens']}")
    tin, tout = sum(s["in"] for s in per_model.values()), sum(s["out"] for s in per_model.values())
    tcost = sum(s["cost"] for s in per_model.values())
    print(f"\nTotal: {tin + tout} tokens ({tin} in / {tout} out) · ${tcost:.4f}")
    unpriced = [m for m, s in per_model.items() if s["priced"] < s["gens"]]
    if unpriced:
        print(f"Without pricing in Langfuse (cost shows 0): {', '.join(unpriced)} — register them with --register-model")
    if per_session:
        avg = tcost / max(1, len([s for s in per_session if s != '(no session)']))
        print(f"Average per session: ${avg:.4f} — see COST-ANALYSIS.md for the per-turn, pattern, and projection layers")


if __name__ == "__main__":
    a = parse_args()
    lf = client()
    if a.register_model:
        register_model(lf, a)
        sys.exit(0)
    s, e = window(a)
    report(lf, s, e, a.session)
