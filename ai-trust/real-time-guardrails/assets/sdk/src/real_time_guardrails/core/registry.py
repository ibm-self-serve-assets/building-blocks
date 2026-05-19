from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Iterable, Iterator, Mapping

from .exceptions import (
    MissingFieldError,
    UnknownCategoryError,
    UnknownMetricError,
)
from .results import Category
from .thresholds import ThresholdSpec


@dataclass(frozen=True)
class MetricEntry:
    """One row of the metric catalog.

    ``required_fields`` are *all* required; ``accepts_fields`` is an "any of"
    set (when non-empty, at least one of those fields must be supplied). The
    typical use of ``accepts_fields`` is safety metrics that accept either
    ``input_text`` or ``generated_text``.
    """

    name: str
    metric: Any  # An instantiated ibm_watsonx_gov metric object
    category: Category
    column_name: str
    threshold_spec: ThresholdSpec
    required_fields: FrozenSet[str]
    description: str
    accepts_fields: FrozenSet[str] = frozenset()


class MetricRegistry:
    """Holds the 28 MetricEntry rows and provides lookup + filtering."""

    def __init__(self, entries: Iterable[MetricEntry]) -> None:
        self._by_name: dict[str, MetricEntry] = {}
        for entry in entries:
            if entry.name in self._by_name:
                raise ValueError(f"Duplicate metric name in registry: {entry.name!r}")
            self._by_name[entry.name] = entry

    # ----- read-only access -----

    def __iter__(self) -> Iterator[MetricEntry]:
        return iter(self._by_name.values())

    def __len__(self) -> int:
        return len(self._by_name)

    def __contains__(self, name: object) -> bool:
        return name in self._by_name

    @property
    def names(self) -> list[str]:
        return list(self._by_name.keys())

    @property
    def categories(self) -> set[Category]:
        return {entry.category for entry in self._by_name.values()}

    def get(self, name: str) -> MetricEntry:
        try:
            return self._by_name[name]
        except KeyError as exc:
            raise UnknownMetricError(name, self._by_name.keys()) from exc

    def filter_by_name(self, names: Iterable[str]) -> list[MetricEntry]:
        return [self.get(name) for name in names]

    def filter_by_category(self, categories: Iterable[str]) -> list[MetricEntry]:
        valid = self.categories
        selected: list[MetricEntry] = []
        for cat in categories:
            if cat not in valid:
                raise UnknownCategoryError(cat, valid)
            selected.extend(e for e in self._by_name.values() if e.category == cat)
        return selected

    def auto_select(self, available_fields: set[str]) -> list[MetricEntry]:
        """Pick every metric whose ``required_fields`` are satisfied and (if
        ``accepts_fields`` is non-empty) at least one accepts field is present.
        """
        return [
            e
            for e in self._by_name.values()
            if self._satisfied(e, available_fields)
        ]

    def validate_required(
        self, entries: Iterable[MetricEntry], available_fields: set[str]
    ) -> None:
        """Raise :class:`MissingFieldError` for any unsatisfied requirement.

        - Each field in ``required_fields`` must be present.
        - If ``accepts_fields`` is non-empty, at least one of those fields must
          be present; the error message lists the acceptable fields.
        """
        for entry in entries:
            for field in entry.required_fields:
                if field not in available_fields:
                    raise MissingFieldError(entry.name, field)
            if entry.accepts_fields and not (entry.accepts_fields & available_fields):
                accepted = " or ".join(repr(f) for f in sorted(entry.accepts_fields))
                raise MissingFieldError(entry.name, f"at least one of {accepted}")

    @staticmethod
    def _satisfied(entry: MetricEntry, available_fields: set[str]) -> bool:
        if not entry.required_fields.issubset(available_fields):
            return False
        if entry.accepts_fields and not (entry.accepts_fields & available_fields):
            return False
        return True


def known_categories() -> tuple[Category, ...]:
    return (
        "safety",
        "rag_generation",
        "rag_retrieval",
        "quality",
        "topic",
        "pattern",
        "tool_call",
    )
