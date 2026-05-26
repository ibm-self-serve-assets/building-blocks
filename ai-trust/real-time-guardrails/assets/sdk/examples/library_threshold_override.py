"""Demonstrate the 5 threshold-override layers and their precedence.

Precedence (highest wins): per-call > constructor > YAML config > env var > default.
"""

from __future__ import annotations

import os
from pathlib import Path

from real_time_guardrails import GuardrailsEvaluator


def show_pii_threshold(label: str, ev: GuardrailsEvaluator, **eval_kwargs: object) -> None:
    bundle = ev.evaluate(
        input_text="My SSN is 123-45-6789",
        metrics=["PII Detection"],
        **eval_kwargs,  # type: ignore[arg-type]
    )
    r = bundle["PII Detection"]
    print(f"  {label:<45} threshold={r.threshold}  score={r.score}  action={r.action}")


def main() -> None:
    # Layer 5 — package default (Safety = 0.65)
    print("\n--- Layer 5: package default ---")
    ev = GuardrailsEvaluator()
    show_pii_threshold("default", ev)

    # Layer 4 — env var
    print("\n--- Layer 4: env var override (0.3) ---")
    os.environ["GUARDRAILS_THRESHOLD_PII_DETECTION"] = "0.3"
    ev_env = GuardrailsEvaluator()
    show_pii_threshold("GUARDRAILS_THRESHOLD_PII_DETECTION=0.3", ev_env)
    del os.environ["GUARDRAILS_THRESHOLD_PII_DETECTION"]

    # Layer 3 — YAML config file
    print("\n--- Layer 3: YAML config file (0.4) ---")
    config_path = Path("/tmp/example_thresholds.yaml")
    config_path.write_text('metrics:\n  "PII Detection": 0.4\n')
    ev_cfg = GuardrailsEvaluator(config_path=config_path)
    show_pii_threshold(f"config_path={config_path}", ev_cfg)
    config_path.unlink()

    # Layer 2 — constructor override
    print("\n--- Layer 2: constructor override (0.5) ---")
    ev_ctor = GuardrailsEvaluator(threshold_overrides={"PII Detection": 0.5})
    show_pii_threshold("threshold_overrides={'PII Detection': 0.5}", ev_ctor)

    # Layer 1 — per-call override beats constructor
    print("\n--- Layer 1: per-call override (0.9, beats constructor 0.5) ---")
    show_pii_threshold(
        "thresholds={'PII Detection': 0.9}", ev_ctor, thresholds={"PII Detection": 0.9}
    )

    # Inspect what /api/metrics-style payload would show
    print("\n--- list_metrics(): default vs. effective ---")
    payload = ev_ctor.list_metrics()
    pii = next(m for m in payload["metrics"] if m["name"] == "PII Detection")
    print(f"  default_threshold   = {pii['default_threshold']}")
    print(f"  effective_threshold = {pii['effective_threshold']}")


if __name__ == "__main__":
    main()
