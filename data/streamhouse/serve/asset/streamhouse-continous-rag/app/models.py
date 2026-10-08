from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class KnowledgeDocument(BaseModel):
    document_id: str = Field(
        default_factory=lambda: str(uuid4()),
        max_length=128,
        pattern=r"^[A-Za-z0-9\-_\.]+$",
    )
    title: str = Field(min_length=1, max_length=256)
    text: str = Field(min_length=1, max_length=50_000)
    source: Literal[
        "operator-upload",
        "demo-knowledge",
        "maintenance-work-order",
        "api-upload",
        "shift-handover",
        "quality-alert",
        "test",
    ] = "operator-upload"
    asset_id: str | None = Field(default=None, max_length=64, pattern=r"^[A-Za-z0-9\-]+$")
    updated_at: str = Field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = Field(default_factory=dict)


class KnowledgeChunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    text: str
    source: str
    asset_id: str | None = None
    updated_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float]
    embedding_model: str


class RagQuestion(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=10)


class RagEvidence(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    text: str
    source: str
    asset_id: str | None = None
    score: float
    updated_at: str


class RagAnswer(BaseModel):
    answer: str
    evidence: list[RagEvidence]
    retrieval_mode: str
    generation_mode: str
    latency_ms: int


class FactoryState(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    line_id: str = "LINE-01"
    machine_id: str = "CNC-03"
    product: str = "Gear Assembly"
    vibration_mm_s: float = 2.1
    temperature_c: float = 61.5
    cycle_time_sec: float = 42.0
    defect_rate_pct: float = 1.2
    produced_units: int = 620
    target_units: int = 1000
    projected_units: int = 1010
    machine_health: Literal["healthy", "warning", "critical"] = "healthy"
    production_risk: Literal["low", "medium", "high", "critical"] = "low"
    quality_risk: Literal["low", "medium", "high", "critical"] = "low"
    overall_risk: Literal["low", "medium", "high", "critical"] = "low"
    root_signal: str = "Normal operation"
    recommendation: str = "Continue monitoring"


class FactoryException(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    severity: Literal["info", "warning", "high", "critical"]
    machine_id: str
    line_id: str
    title: str
    description: str
    recommended_action: str


class MachineTelemetry(BaseModel):
    """Raw sensor reading published to factory.machine.telemetry."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    machine_id: str = "CNC-03"
    line_id: str = "LINE-01"
    spindle_speed_rpm: float = 12000.0
    vibration_mm_s: float = 2.1
    temperature_c: float = 61.5
    load_pct: float = 68.0
    coolant_pressure_bar: float = 4.2
    lube_flow_ok: bool = True


class ProductionEvent(BaseModel):
    """MES production progress event — factory.production.events."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    line_id: str = "LINE-01"
    machine_id: str = "CNC-03"
    product: str = "Gear Assembly GA-4471"
    shift: str = "Day"
    produced_units: int = 0
    target_units: int = 1000
    projected_units: int = 1000
    cycle_time_sec: float = 42.0
    scrap_units: int = 0
    efficiency_pct: float = 100.0


class QualityEvent(BaseModel):
    """Inspection result — factory.quality.events."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    machine_id: str = "CNC-03"
    line_id: str = "LINE-01"
    part_serial: str = ""
    inspection_type: str = "dimensional"
    result: Literal["pass", "fail", "hold"] = "pass"
    defect_rate_pct: float = 1.2
    bore_diameter_mm: float = 10.000
    bore_tolerance_mm: float = 0.010
    surface_finish_ra: float = 1.4
    notes: str = ""


class MaintenanceEvent(BaseModel):
    """CMMS maintenance status — factory.maintenance.events."""
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    ts: str = Field(default_factory=utc_now_iso)
    work_order: str = ""
    machine_id: str = "CNC-03"
    line_id: str = "LINE-01"
    event_type: Literal["opened", "in_progress", "resolved", "pm_due"] = "opened"
    technician_id: str = ""
    title: str = ""
    description: str = ""
    priority: Literal["low", "medium", "high", "critical"] = "medium"


class HealthStatus(BaseModel):
    status: str
    kafka: str
    rag_pipeline: str
    indexed_chunks: int
    latest_state_at: str | None
