#!/usr/bin/env python3
"""
FactoryPulse Streamhouse — Continuous Demo Simulator
=====================================================
Streams realistic data to ALL six Confluent Cloud topics continuously,
demonstrating the full Streamhouse architecture:

  factory.machine.telemetry   ← PLC/sensor readings (every 3 s)
  factory.production.events   ← MES production progress (every 10 s)
  factory.quality.events      ← Inspection results (every 15 s)
  factory.maintenance.events  ← CMMS work order status changes
  factory.state               ← Correlated factory state (every 5 s)
  factory.exceptions          ← Exception-to-action events
  rag.knowledge.raw           ← New knowledge at story milestones

Story arc (auto-advances on a timeline):
  Phase 0:  Healthy production         (0–60 s)
  Phase 1:  Early vibration onset      (60–120 s)
  Phase 2:  Degradation — warning      (120–180 s)
  Phase 3:  Critical — production risk (180–240 s)
  Phase 4:  Maintenance in progress    (240–300 s)
  Phase 5:  Resolved + knowledge event (300–360 s)
  Phase 6:  Back to healthy + learning (360+ s, loops)

Usage:
    # From repo root (app must NOT be running — this is a standalone script)
    source .venv/bin/activate
    python scripts/stream_demo.py

    # Quiet mode (suppress per-event lines)
    python scripts/stream_demo.py --quiet

    # Single pass, no loop
    python scripts/stream_demo.py --no-loop

    # Custom tick interval (default 3 s)
    python scripts/stream_demo.py --tick 2
"""
from __future__ import annotations

import argparse
import math
import random
import sys
import time
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Bootstrap path so imports resolve when running from repo root
# ---------------------------------------------------------------------------
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import get_settings
from app.models import (
    FactoryException,
    FactoryState,
    KnowledgeDocument,
    MachineTelemetry,
    MaintenanceEvent,
    ProductionEvent,
    QualityEvent,
)
from app.services.kafka import KafkaGateway


# ---------------------------------------------------------------------------
# Story phases — each defines the machine/production state for that window
# ---------------------------------------------------------------------------
PHASES: list[dict] = [
    # ── Phase 0: Healthy ────────────────────────────────────────────────────
    {
        "name": "healthy",
        "duration_s": 60,
        "vibration_base": 2.1, "vibration_noise": 0.15,
        "temperature_base": 61.5, "temperature_noise": 0.5,
        "cycle_base": 42.0, "cycle_noise": 0.8,
        "defect_rate": 1.2, "defect_noise": 0.3,
        "load_pct": 68.0,
        "lube_flow_ok": True,
        "machine_health": "healthy",
        "production_risk": "low", "quality_risk": "low", "overall_risk": "low",
        "root_signal": "Normal operation — all systems nominal",
        "recommendation": "Continue monitoring standard interval",
        "bore_offset": 0.0, "bore_noise": 0.002,
    },
    # ── Phase 1: Early onset ─────────────────────────────────────────────────
    {
        "name": "early_onset",
        "duration_s": 60,
        "vibration_base": 3.1, "vibration_noise": 0.25,
        "temperature_base": 62.8, "temperature_noise": 0.6,
        "cycle_base": 44.5, "cycle_noise": 1.0,
        "defect_rate": 1.6, "defect_noise": 0.4,
        "load_pct": 71.0,
        "lube_flow_ok": True,
        "machine_health": "healthy",
        "production_risk": "low", "quality_risk": "low", "overall_risk": "low",
        "root_signal": "Vibration slowly rising on CNC-03 spindle — within monitor threshold",
        "recommendation": "Schedule tool-holder inspection at next planned stop",
        "bore_offset": 0.003, "bore_noise": 0.003,
    },
    # ── Phase 2: Degradation — warning ──────────────────────────────────────
    {
        "name": "degradation",
        "duration_s": 60,
        "vibration_base": 4.2, "vibration_noise": 0.3,
        "temperature_base": 64.7, "temperature_noise": 0.8,
        "cycle_base": 51.0, "cycle_noise": 1.5,
        "defect_rate": 2.8, "defect_noise": 0.6,
        "load_pct": 76.0,
        "lube_flow_ok": True,
        "machine_health": "warning",
        "production_risk": "medium", "quality_risk": "medium", "overall_risk": "medium",
        "root_signal": "Vibration 4.2 mm/s — above warning threshold; cycle time +21 % vs baseline",
        "recommendation": "Inspect tool-holder balance and spindle condition at next safe stop within 4 hours",
        "bore_offset": 0.009, "bore_noise": 0.005,
    },
    # ── Phase 3: Critical ────────────────────────────────────────────────────
    {
        "name": "critical",
        "duration_s": 60,
        "vibration_base": 5.8, "vibration_noise": 0.35,
        "temperature_base": 68.2, "temperature_noise": 1.0,
        "cycle_base": 63.0, "cycle_noise": 2.0,
        "defect_rate": 8.2, "defect_noise": 1.0,
        "load_pct": 84.0,
        "lube_flow_ok": True,
        "machine_health": "critical",
        "production_risk": "critical", "quality_risk": "high", "overall_risk": "critical",
        "root_signal": "CRITICAL: vibration 5.8 mm/s correlated with +50 % cycle time and 8.2 % defect rate",
        "recommendation": "Immediate safe stop — inspect spindle tool-holder before continuing production",
        "bore_offset": 0.019, "bore_noise": 0.006,
    },
    # ── Phase 4: Maintenance in progress ────────────────────────────────────
    {
        "name": "maintenance",
        "duration_s": 60,
        "vibration_base": 0.0, "vibration_noise": 0.0,
        "temperature_base": 55.0, "temperature_noise": 0.2,
        "cycle_base": 0.0, "cycle_noise": 0.0,
        "defect_rate": 0.0, "defect_noise": 0.0,
        "load_pct": 0.0,
        "lube_flow_ok": True,
        "machine_health": "warning",
        "production_risk": "high", "quality_risk": "low", "overall_risk": "medium",
        "root_signal": "CNC-03 stopped for maintenance — TECH-409 inspecting spindle and tool-holder",
        "recommendation": "Hold production on LINE-01 — estimated return to service 45 min",
        "bore_offset": 0.0, "bore_noise": 0.0,
    },
    # ── Phase 5: Resolved ────────────────────────────────────────────────────
    {
        "name": "resolved",
        "duration_s": 60,
        "vibration_base": 2.1, "vibration_noise": 0.12,
        "temperature_base": 62.2, "temperature_noise": 0.4,
        "cycle_base": 43.0, "cycle_noise": 0.6,
        "defect_rate": 1.1, "defect_noise": 0.2,
        "load_pct": 69.0,
        "lube_flow_ok": True,
        "machine_health": "healthy",
        "production_risk": "medium", "quality_risk": "low", "overall_risk": "low",
        "root_signal": "CNC-03 returned to service — tool-holder replaced (WO-11023), vibration nominal",
        "recommendation": "Monitor first 50 parts after recalibration — enhanced inspection interval",
        "bore_offset": 0.001, "bore_noise": 0.002,
    },
]

# ---------------------------------------------------------------------------
# Knowledge documents injected at specific story milestones
# ---------------------------------------------------------------------------
MILESTONE_KNOWLEDGE: dict[str, KnowledgeDocument] = {
    "degradation": KnowledgeDocument(
        document_id="shift-handover-vibration-alert",
        title="Shift Handover Note — CNC-03 Vibration Alert",
        text=(
            "Shift handover note — Day shift to Afternoon shift, LINE-01.\n"
            "Supervisor: M. Alvarez. Written by: Operator T. Singh.\n\n"
            "CNC-03 has been showing a gradual vibration increase since approximately 09:15. "
            "Current reading 4.2 mm/s RMS against a 2.5 mm/s normal operating band. "
            "Cycle time has increased from 42 s to approximately 51 s. "
            "Defect rate is at 2.8 % — above the 2 % monitor threshold but below the 5 % hold threshold. "
            "We have not yet stopped the machine — the shift supervisor has authorised continuation "
            "to the next scheduled break (14:30) when a tool-holder inspection will be performed.\n\n"
            "Parts produced since anomaly onset (part serial GA-4471-2310 onwards): "
            "8 parts held for enhanced dimensional inspection. Quality technician L. Ferreira has been notified.\n\n"
            "Recommended action for afternoon shift: inspect tool-holder balance and runout first "
            "per MFG-DOC-CNC-002 before any bearing work. WO-11023 has been opened in MES."
        ),
        source="shift-handover",
        asset_id="CNC-03",
        metadata={"shift": "Day", "supervisor": "M. Alvarez", "work_order": "WO-11023"},
    ),
    "critical": KnowledgeDocument(
        document_id="quality-alert-ga4471",
        title="Quality Alert — GA-4471 Bore Diameter Out of Tolerance",
        text=(
            "Quality Alert — issued by Quality Technician L. Ferreira, LINE-01.\n"
            "Time: 13:22. Asset: CNC-03.\n\n"
            "Dimensional inspection of Gear Assembly GA-4471 bore has confirmed out-of-tolerance results "
            "on 6 consecutive parts. Bore diameter measured 0.018–0.022 mm oversized against "
            "+0.010 / -0.000 mm tolerance. Surface finish Ra measured at 2.1 µm against Ra ≤ 1.6 µm acceptance.\n\n"
            "Parts on quality hold: serial GA-4471-2318 to GA-4471-2323 (6 parts confirmed reject). "
            "Additional parts from serial GA-4471-2310 (8 parts) under enhanced inspection.\n\n"
            "Root cause investigation underway — spindle vibration at 5.8 mm/s strongly suggests "
            "tool-holder imbalance or spindle bearing issue. Maintenance TECH-409 has been called. "
            "Machine stopped at 13:28 per SOP MFG-SOP-LINE01-007 Tier 3 procedure.\n\n"
            "Rework path for oversized bores: GA-RW-0441 rework order authorised — "
            "bore can be re-machined to next oversize class if material is sufficient."
        ),
        source="quality-alert",
        asset_id="CNC-03",
        metadata={"alert_type": "dimensional", "parts_on_hold": "14", "work_order": "WO-11023"},
    ),
    "resolved": KnowledgeDocument(
        document_id="wo-11023-resolution",
        title="WO-11023 CNC-03 Tool-holder Imbalance Resolution",
        text=(
            "Work order WO-11023 — CNC-03, LINE-01. "
            "Technician: A. Reyes (Tech ID: TECH-409). Shift: Day shift, Supervisor: M. Alvarez.\n\n"
            "Symptom: CNC-03 spindle vibration reached 5.8 mm/s RMS during Gear Assembly production. "
            "Cycle time increased to 63 s (baseline 42 s). Defect rate rose to 8.2 % — dimensional "
            "deviation on bore diameter GA-4471, parts oversized by 0.015–0.025 mm. "
            "Projected output dropped to 870 units against 1,000-unit shift target.\n\n"
            "Diagnostic: Tool-holder inspection per MFG-DOC-CNC-002. "
            "Runout at 50 mm gauge length: 0.0094 mm TIR (limit 0.003 mm). "
            "Balance class G6.3 found — LINE-01 requires G2.5 at 25,000 RPM. "
            "Root cause confirmed: tool-holder imbalance (serial T-07-291, incorrectly returned to rack).\n"
            "Spindle bearing checked: no damage — cleared.\n\n"
            "Corrective action: replaced tool holder T-07-291 with SANDVIK-390.140-4032 (G2.5, serial T-07-308). "
            "Applied torque spec 45 Nm (OEM retention knob spec). "
            "Spindle warm-up cycle completed (1,000 / 5,000 / 12,000 RPM, 10 min each).\n\n"
            "Verification: vibration 2.1 mm/s, cycle time 42 s, defect rate 1.1 %, "
            "bore diameter within ±0.010 mm on 3 consecutive test parts.\n\n"
            "Lessons: when vibration + dimensional drift appear together, inspect tool-holder first. "
            "This resolved in 45 min vs 3.5 h for a full bearing replacement."
        ),
        source="maintenance-work-order",
        asset_id="CNC-03",
        metadata={"work_order": "WO-11023", "technician": "TECH-409", "torque_spec_nm": "45"},
    ),
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _jitter(base: float, noise: float) -> float:
    """Gaussian jitter around a base value."""
    return round(base + random.gauss(0, noise), 3) if noise > 0 else base


def _part_serial(tick: int) -> str:
    return f"GA-4471-{2300 + tick}"


def _produced(tick: int, cycle_s: float) -> int:
    """Estimate parts produced given elapsed ticks and current cycle time."""
    elapsed_hours = (tick * 3) / 3600
    return min(1000, int(elapsed_hours * 3600 / max(cycle_s, 1)))


def _efficiency(cycle_s: float) -> float:
    return round(min(100.0, (42.0 / max(cycle_s, 1)) * 100), 1)


def pub(kafka: KafkaGateway, topic: str, model, key: str, quiet: bool) -> None:
    kafka.produce(topic, model.model_dump(), key=key)
    if not quiet:
        ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
        name = model.__class__.__name__
        print(f"  [{ts}] -> {topic:<38} {name}")


# ---------------------------------------------------------------------------
# Main simulation loop
# ---------------------------------------------------------------------------

def run_phase(
    phase: dict,
    kafka: KafkaGateway,
    settings,
    tick_interval: int,
    quiet: bool,
    global_tick: int,
    milestone_fired: set[str],
) -> tuple[int, set[str]]:
    """Run one phase, streaming all topic types throughout."""
    phase_name = phase["name"]
    phase_ticks = phase["duration_s"] // tick_interval
    print(f"\n{'='*60}")
    print(f"  PHASE: {phase_name.upper().replace('_',' ')}")
    print(f"  vibration base={phase['vibration_base']} mm/s  "
          f"defect={phase['defect_rate']}%  health={phase['machine_health']}")
    print(f"{'='*60}")

    # Fire milestone knowledge at phase start (once per story cycle)
    if phase_name in MILESTONE_KNOWLEDGE and phase_name not in milestone_fired:
        doc = MILESTONE_KNOWLEDGE[phase_name]
        # Re-stamp updated_at so freshness is real
        doc = doc.model_copy(update={"updated_at": datetime.now(timezone.utc).isoformat()})
        pub(kafka, settings.topic_knowledge_raw, doc, doc.document_id, quiet)
        kafka.flush(5)
        milestone_fired.add(phase_name)
        print(f"  ★ Knowledge event streamed: {doc.title}")

    # Phase inner tick loop
    for i in range(phase_ticks):
        vib = _jitter(phase["vibration_base"], phase["vibration_noise"])
        temp = _jitter(phase["temperature_base"], phase["temperature_noise"])
        cycle = _jitter(phase["cycle_base"], phase["cycle_noise"]) if phase["cycle_base"] > 0 else 0.0
        defect = round(max(0.0, _jitter(phase["defect_rate"], phase["defect_noise"])), 2)
        produced = _produced(global_tick, cycle if cycle > 0 else 42)
        projected = min(1000, int(produced + ((1000 - produced) * 42 / max(cycle, 1)) * 0.5))
        bore = round(10.0 + phase["bore_offset"] + _jitter(0, phase["bore_noise"]), 4)
        bore_result = "pass" if abs(bore - 10.0) <= 0.010 else ("hold" if abs(bore - 10.0) <= 0.018 else "fail")

        # ── factory.machine.telemetry (every tick) ──────────────────────────
        telemetry = MachineTelemetry(
            machine_id="CNC-03", line_id="LINE-01",
            spindle_speed_rpm=12000.0 if phase["machine_health"] != "warning" else 11800.0,
            vibration_mm_s=vib, temperature_c=temp,
            load_pct=_jitter(phase["load_pct"], 2.0),
            coolant_pressure_bar=_jitter(4.2, 0.1),
            lube_flow_ok=phase["lube_flow_ok"],
        )
        pub(kafka, settings.topic_machine_telemetry, telemetry, telemetry.machine_id, quiet)

        # ── factory.state (every tick) ──────────────────────────────────────
        factory_state = FactoryState(
            machine_id="CNC-03", line_id="LINE-01",
            vibration_mm_s=vib, temperature_c=temp,
            cycle_time_sec=cycle if cycle > 0 else 42.0,
            defect_rate_pct=defect,
            produced_units=produced, projected_units=projected,
            machine_health=phase["machine_health"],
            production_risk=phase["production_risk"],
            quality_risk=phase["quality_risk"],
            overall_risk=phase["overall_risk"],
            root_signal=phase["root_signal"],
            recommendation=phase["recommendation"],
        )
        pub(kafka, settings.topic_factory_state, factory_state, factory_state.machine_id, quiet)

        # ── factory.production.events (every 3rd tick ~10 s) ────────────────
        if global_tick % 3 == 0:
            prod_event = ProductionEvent(
                line_id="LINE-01", machine_id="CNC-03",
                produced_units=produced, target_units=1000, projected_units=projected,
                cycle_time_sec=cycle if cycle > 0 else 42.0,
                scrap_units=int(produced * defect / 100),
                efficiency_pct=_efficiency(cycle if cycle > 0 else 42.0),
            )
            pub(kafka, settings.topic_production_events, prod_event, prod_event.machine_id, quiet)

        # ── factory.quality.events (every 5th tick ~15 s) ───────────────────
        if global_tick % 5 == 0 and phase["machine_health"] != "warning" or phase["defect_rate"] > 3:
            quality_event = QualityEvent(
                machine_id="CNC-03", line_id="LINE-01",
                part_serial=_part_serial(global_tick),
                result=bore_result,
                defect_rate_pct=defect,
                bore_diameter_mm=bore,
                surface_finish_ra=_jitter(1.4 + phase["bore_offset"] * 5, 0.1),
                notes=f"vibration {vib} mm/s at inspection" if vib > 3.5 else "",
            )
            pub(kafka, settings.topic_quality_events, quality_event, quality_event.machine_id, quiet)

        # ── factory.exceptions for critical/degradation ──────────────────────
        if i == 0 and phase["overall_risk"] in ("medium", "critical"):
            exc = FactoryException(
                severity="critical" if phase["overall_risk"] == "critical" else "warning",
                machine_id="CNC-03", line_id="LINE-01",
                title=f"CNC-03 — {phase['root_signal'][:60]}",
                description=(
                    f"Vibration: {phase['vibration_base']} mm/s  "
                    f"Cycle time: {phase['cycle_base']} s  "
                    f"Defect rate: {phase['defect_rate']}%"
                ),
                recommended_action=phase["recommendation"],
            )
            pub(kafka, settings.topic_factory_exceptions, exc, exc.machine_id, quiet)

        # ── factory.maintenance.events at maintenance phase ──────────────────
        if phase_name == "maintenance":
            if i == 0:
                maint = MaintenanceEvent(
                    work_order="WO-11023", machine_id="CNC-03", line_id="LINE-01",
                    event_type="in_progress", technician_id="TECH-409",
                    title="WO-11023 — CNC-03 spindle inspection in progress",
                    description="TECH-409 performing tool-holder and spindle bearing inspection per MFG-DOC-CNC-002",
                    priority="critical",
                )
                pub(kafka, settings.topic_maintenance_events, maint, maint.work_order, quiet)
        elif phase_name == "resolved" and i == 0:
            maint = MaintenanceEvent(
                work_order="WO-11023", machine_id="CNC-03", line_id="LINE-01",
                event_type="resolved", technician_id="TECH-409",
                title="WO-11023 — RESOLVED: tool-holder replaced, CNC-03 returned to service",
                description="Root cause: out-of-spec tool holder T-07-291. Replaced with SANDVIK G2.5. Torque spec 45 Nm.",
                priority="critical",
            )
            pub(kafka, settings.topic_maintenance_events, maint, maint.work_order, quiet)

        kafka.flush(2)
        global_tick += 1
        time.sleep(tick_interval)

    return global_tick, milestone_fired


def main() -> None:
    parser = argparse.ArgumentParser(description="FactoryPulse continuous Streamhouse demo simulator")
    parser.add_argument("--tick", type=int, default=3, help="Seconds between telemetry events (default: 3)")
    parser.add_argument("--quiet", action="store_true", help="Suppress per-event output")
    parser.add_argument("--no-loop", action="store_true", help="Run the story arc once then exit")
    args = parser.parse_args()

    settings = get_settings()
    kafka = KafkaGateway(settings)
    if not settings.kafka_ready:
        raise SystemExit("Confluent Cloud credentials not configured — check .env")

    sep = "=" * 60
    print(sep)
    print("  FactoryPulse -- Continuous Streamhouse Demo Simulator")
    print(sep)
    print(f"  bootstrap : {settings.confluent_bootstrap_servers}")
    print(f"  tick      : {args.tick} s   loop: {not args.no_loop}")
    print("  topics    : machine.telemetry | production.events |")
    print("              quality.events | maintenance.events |")
    print("              factory.state | factory.exceptions |")
    print("              rag.knowledge.raw")
    print()
    print("  Open http://localhost:8080 and watch all tabs update live.")
    print("  Press Ctrl+C to stop.\n")

    global_tick = 0
    loop_count = 0

    try:
        while True:
            loop_count += 1
            milestone_fired: set[str] = set()
            print(f"\n{sep}")
            print(f"  Story loop #{loop_count} -- {len(PHASES)} phases x {sum(p['duration_s'] for p in PHASES)} s")
            print(sep)
            for phase in PHASES:
                global_tick, milestone_fired = run_phase(
                    phase, kafka, settings, args.tick, args.quiet, global_tick, milestone_fired
                )
            if args.no_loop:
                break
            print(f"\n  Loop #{loop_count} complete. Restarting story arc in 10 s…")
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
    finally:
        kafka.close()
        print(f"Total ticks streamed: {global_tick}")


if __name__ == "__main__":
    main()
