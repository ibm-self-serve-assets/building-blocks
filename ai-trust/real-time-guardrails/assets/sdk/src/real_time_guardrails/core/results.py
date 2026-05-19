from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Iterator, Literal, Mapping


Category = Literal[
    "safety",
    "rag_generation",
    "rag_retrieval",
    "quality",
    "topic",
    "pattern",
    "tool_call",
]

GuardrailAction = Literal["Pass", "Flag", "Block", "---"]
"""Three-state action model (plus non-actionable sentinel).

- ``Pass`` — score is below the flag/block thresholds; allow through.
- ``Flag`` — score is between flag and block thresholds; allow but mark for
  human review. Useful for borderline compliance cases.
- ``Block`` — score is at/above (HIGH_IS_RISK) or at/below (LOW_IS_RISK) the
  block threshold; refuse the request/response.
- ``"---"`` — metric is non-actionable (e.g. ``Unsuccessful Requests``); the
  score is reported but no action is taken.
"""


@dataclass(frozen=True)
class GuardrailResult:
    metric: str
    category: Category
    score: float | None
    passed: bool | None
    action: GuardrailAction
    column: str | None
    threshold: float
    """The *block* threshold currently in force."""
    flag_threshold: float | None = None
    """The *flag* threshold currently in force (``None`` if this metric has no
    flag state — e.g. pattern metrics or non-actionable metrics)."""
    fallback_message: str | None = None
    """Optional user-facing message populated when ``action == "Block"``. Set
    via per-call ``fallback_messages={metric_name: ...}`` or the category default."""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ResultBundle:
    record_id: str
    metrics_evaluated: list[str]
    results: dict[str, GuardrailResult] = field(default_factory=dict)

    def __getitem__(self, name: str) -> GuardrailResult:
        return self.results[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __contains__(self, name: object) -> bool:
        return name in self.results

    def failed(self) -> list[GuardrailResult]:
        """Results where ``action == "Block"`` — these blocked the request/response."""
        return [r for r in self.results.values() if r.action == "Block"]

    def flagged(self) -> list[GuardrailResult]:
        """Results where ``action == "Flag"`` — borderline; log for human review but allow through."""
        return [r for r in self.results.values() if r.action == "Flag"]

    def passed_all(self) -> bool:
        """True when no metric returned ``Block``. Flag-state metrics still count as passing."""
        return not self.failed()

    def overall_action(self) -> GuardrailAction:
        """Aggregate action across all metrics, prioritised Block > Flag > Pass.

        ``"---"`` (non-actionable) is treated as Pass for aggregation purposes.
        """
        actions = {r.action for r in self.results.values()}
        if "Block" in actions:
            return "Block"
        if "Flag" in actions:
            return "Flag"
        return "Pass"

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "metrics_evaluated": list(self.metrics_evaluated),
            "results": {name: r.to_dict() for name, r in self.results.items()},
        }

    @classmethod
    def from_mapping(
        cls,
        record_id: str,
        results: Mapping[str, GuardrailResult],
    ) -> "ResultBundle":
        return cls(
            record_id=record_id,
            metrics_evaluated=list(results.keys()),
            results=dict(results),
        )
