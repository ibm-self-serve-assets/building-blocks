#!/usr/bin/env python3
from __future__ import annotations

import time

from app.config import get_settings
from app.models import FactoryException, FactoryState, KnowledgeDocument
from app.services.kafka import KafkaGateway


def publish(kafka: KafkaGateway, topic: str, model, key: str) -> None:
    kafka.produce(topic, model.model_dump(), key=key)
    kafka.flush(5)


def main() -> None:
    settings = get_settings()
    kafka = KafkaGateway(settings)
    if not settings.kafka_ready:
        raise SystemExit("Confluent Cloud credentials are not configured.")

    stages = [
        ("baseline", FactoryState(vibration_mm_s=2.1, cycle_time_sec=42, defect_rate_pct=1.2, projected_units=1010)),
        (
            "degrade",
            FactoryState(
                vibration_mm_s=4.2, temperature_c=64.7, cycle_time_sec=51, defect_rate_pct=2.8,
                projected_units=935, machine_health="warning", production_risk="medium", quality_risk="medium",
                overall_risk="medium", root_signal="Vibration trend rising on CNC-03",
                recommendation="Inspect tooling balance during next safe stop",
            ),
        ),
        (
            "critical",
            FactoryState(
                vibration_mm_s=5.8, temperature_c=68.2, cycle_time_sec=63, defect_rate_pct=8.2,
                projected_units=870, machine_health="critical", production_risk="critical", quality_risk="high",
                overall_risk="critical", root_signal="High vibration correlated with slower cycles and dimensional defects",
                recommendation="Stop CNC-03 at next safe opportunity and inspect spindle/tool holder",
            ),
        ),
    ]

    for name, stage in stages:
        print(f"publishing stage: {name}")
        publish(kafka, settings.topic_factory_state, stage, stage.machine_id)
        if name != "baseline":
            exc = FactoryException(
                severity="critical" if name == "critical" else "warning",
                machine_id="CNC-03", line_id="LINE-01",
                title="Production target and quality at risk" if name == "critical" else "Machine degradation detected",
                description=stage.root_signal,
                recommended_action=stage.recommendation,
            )
            publish(kafka, settings.topic_factory_exceptions, exc, exc.machine_id)
        time.sleep(6)

    print("publishing maintenance resolution into the continuous knowledge stream")
    doc = KnowledgeDocument(
        document_id="wo-11023-resolution",
        title="WO-11023 CNC-03 Tool-holder Imbalance Resolution",
        text=(
            "CNC-03 was inspected after high vibration, slower cycle time, and dimensional defects. "
            "The technician found tool-holder imbalance. The tool holder was replaced and the machine "
            "was recalibrated. Vibration returned to 2.1 mm/s and dimensional checks returned within tolerance."
        ),
        source="maintenance-work-order",
        asset_id="CNC-03",
        metadata={"work_order": "WO-11023"},
    )
    publish(kafka, settings.topic_knowledge_raw, doc, doc.document_id)

    resolved = FactoryState(
        vibration_mm_s=2.1, temperature_c=62.2, cycle_time_sec=43, defect_rate_pct=1.1,
        projected_units=982, machine_health="healthy", production_risk="medium", quality_risk="low",
        overall_risk="low", root_signal="CNC-03 stabilized after tool-holder replacement",
        recommendation="Monitor first 50 parts after recalibration",
    )
    publish(kafka, settings.topic_factory_state, resolved, resolved.machine_id)
    kafka.close()
    print("done")


if __name__ == "__main__":
    main()
