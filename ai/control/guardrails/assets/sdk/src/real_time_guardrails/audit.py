"""JSONL audit logger for guardrail decisions.

For compliance use cases: every guardrail decision is appended as a single
JSON object to either a file or a pluggable sink callable (Splunk, ELK,
stdout, etc.).

Example::

    from real_time_guardrails import AuditLogger, GuardrailsEvaluator

    ev = GuardrailsEvaluator()
    audit = AuditLogger(path="audit.jsonl")

    bundle = ev.evaluate(input_text="...", metrics=["PII Detection"])
    audit.record(bundle, input_payload={"input_text": "..."}, request_id="req-42")
    audit.close()

The default sink writes one JSON line per record to ``path``. Inject a
``sink=callable`` to forward records elsewhere instead — useful for
streaming to managed log services without touching disk.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
from pathlib import Path
from typing import Any, Callable, Mapping

from .core.results import GuardrailAction, ResultBundle


Sink = Callable[[dict[str, Any]], None]


def _now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _hash_input(payload: Mapping[str, Any]) -> str:
    """Stable short hash of the input payload — for joining audit records to source data."""
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


class AuditLogger:
    """Append-only JSONL audit trail of guardrail decisions.

    Parameters
    ----------
    path : str | Path | None
        File path for JSONL output. Required unless ``sink`` is provided.
        File is opened in append mode and flushed after every record so
        decisions are durable even if the process crashes.
    sink : Callable[[dict], None] | None
        Optional callable that receives each record. When supplied, replaces
        the default file sink — useful for forwarding to Splunk, ELK, stdout,
        or test fixtures. Either ``path`` or ``sink`` must be set.
    include_inputs : bool
        When True (default), include the raw input payload in each record.
        Disable for compliance regimes that forbid persisting user content;
        the per-input hash is still recorded so records remain joinable.
    """

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        sink: Sink | None = None,
        include_inputs: bool = True,
    ) -> None:
        if path is None and sink is None:
            raise ValueError("AuditLogger requires either path= or sink=")
        self._path: Path | None = Path(path) if path is not None else None
        self._sink: Sink | None = sink
        self._include_inputs = include_inputs
        self._file = None
        if self._path is not None and self._sink is None:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._file = open(self._path, "a", encoding="utf-8")

    def record(
        self,
        bundle: ResultBundle,
        input_payload: Mapping[str, Any] | None = None,
        *,
        request_id: str = "",
        actor: str = "",
    ) -> dict[str, Any]:
        """Append one record covering all metrics in ``bundle``. Returns the record dict."""
        payload = dict(input_payload or {})
        record: dict[str, Any] = {
            "timestamp": _now_iso(),
            "request_id": request_id,
            "actor": actor,
            "record_id": bundle.record_id,
            "input_hash": _hash_input(payload),
            "overall_action": bundle.overall_action(),
            "blocked_metrics": [r.metric for r in bundle.failed()],
            "flagged_metrics": [r.metric for r in bundle.flagged()],
            "metrics": {
                name: {
                    "score": r.score,
                    "action": r.action,
                    "threshold": r.threshold,
                    "flag_threshold": r.flag_threshold,
                    "category": r.category,
                }
                for name, r in bundle.results.items()
            },
        }
        if self._include_inputs:
            record["input"] = payload
        self._emit(record)
        return record

    def close(self) -> None:
        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None

    def __enter__(self) -> "AuditLogger":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ----- internals -----

    def _emit(self, record: dict[str, Any]) -> None:
        if self._sink is not None:
            self._sink(record)
            return
        assert self._file is not None
        self._file.write(json.dumps(record, default=str) + "\n")
        self._file.flush()


def overall_action_priority(actions: list[GuardrailAction]) -> GuardrailAction:
    """Helper: return the most severe action from a list (Block > Flag > Pass)."""
    if "Block" in actions:
        return "Block"
    if "Flag" in actions:
        return "Flag"
    return "Pass"
