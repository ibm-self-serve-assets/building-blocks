from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import Settings, get_settings
from app.models import (
    FactoryException,
    FactoryState,
    HealthStatus,
    KnowledgeDocument,
    RagAnswer,
    RagQuestion,
)
from app.services.kafka import KafkaGateway
from app.services.llm import build_generator
from app.services.rag import RagService
from app.services.state_store import StateStore
from app.services.vector_index import VectorIndex

settings: Settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
LOGGER = logging.getLogger("factorypulse")

store = StateStore()
index = VectorIndex()
kafka = KafkaGateway(settings)
rag = RagService(settings, kafka, index, build_generator(settings))
ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEMO_KNOWLEDGE_DIR = ROOT / "demo_knowledge"

limiter = Limiter(key_func=get_remote_address)
_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


def _verify_api_key(
    request: Request,
    key: str | None = Security(_API_KEY_HEADER),
) -> None:
    expected = settings.demo_api_key
    if not expected:
        return
    if not key or not secrets.compare_digest(key, expected):
        raise HTTPException(
            status_code=403,
            detail="Invalid or missing API key. Provide the configured DEMO_API_KEY via the 'X-API-Key' header.",
        )


def _on_factory_state(payload: dict[str, Any]) -> None:
    try:
        store.set_factory_state(FactoryState.model_validate(payload))
    except Exception:
        LOGGER.exception("Invalid factory state event")


def _on_exception(payload: dict[str, Any]) -> None:
    try:
        store.add_exception(FactoryException.model_validate(payload))
    except Exception:
        LOGGER.exception("Invalid factory exception event")


def _on_document(payload: dict[str, Any]) -> None:
    try:
        store.add_document(KnowledgeDocument.model_validate(payload))
    except Exception:
        LOGGER.exception("Invalid knowledge document event")


@asynccontextmanager
async def lifespan(_: FastAPI):
    if store.factory_state is None:
        store.set_factory_state(FactoryState())

    if settings.kafka_ready:
        # Warm up the broker connection so the first page load shows connected immediately.
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, kafka.probe)

        kafka.start_consumer(
            settings.topic_factory_state,
            f"factorypulse-ui-state-{settings.instance_id}",
            _on_factory_state,
            auto_offset_reset="latest",
        )
        kafka.start_consumer(
            settings.topic_factory_exceptions,
            f"factorypulse-ui-exceptions-{settings.instance_id}",
            _on_exception,
            auto_offset_reset="latest",
        )
        kafka.start_consumer(
            settings.topic_knowledge_raw,
            f"factorypulse-ui-docs-{settings.instance_id}",
            _on_document,
            auto_offset_reset="earliest",
        )
        rag.start()
    else:
        LOGGER.warning("Application started without Kafka credentials. UI-only mode is active.")

    try:
        yield
    finally:
        kafka.close()


app = FastAPI(
    title="FactoryPulse Continuous RAG Streamhouse",
    version="1.0.0",
    description=(
        "Manufacturing demo showing continuous knowledge ingestion, retrieval, and action "
        "on a Confluent Cloud Streamhouse."
    ),
    lifespan=lifespan,
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "connect-src 'self';"
    )
    return response


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health", response_model=HealthStatus)
def health() -> HealthStatus:
    snapshot = store.snapshot()
    latest = snapshot["factory_state"]
    return HealthStatus(
        status="ok",
        kafka="connected/configured" if settings.kafka_ready else "not-configured",
        rag_pipeline=settings.rag_pipeline_mode,
        indexed_chunks=index.count(),
        latest_state_at=latest.get("ts") if latest else None,
    )


@app.get("/api/kafka/probe")
def kafka_probe() -> dict[str, object]:
    """Live broker connectivity check — not a config flag, a real network probe."""
    return kafka.probe()


@app.get("/api/config")
def config() -> dict[str, object]:
    return settings.safe_summary()


@app.get("/api/tableflow/status")
def tableflow_status() -> dict[str, object]:
    """Tableflow materialization status.

    Returns which topics are configured for Tableflow and whether the feature
    is enabled. Tableflow is the analytical/historical path — it is NOT in the
    synchronous RAG retrieval path.
    """
    return {
        "enabled": settings.tableflow_enabled,
        "materialized_topics": settings.tableflow_topics if settings.tableflow_enabled else [],
        "note": (
            "Tableflow materializes factory.state and factory.exceptions as "
            "Iceberg/Delta tables for historical analytics and AI workloads. "
            "It is not in the synchronous RAG latency path."
        ),
    }


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    snapshot = store.snapshot()
    snapshot["indexed_chunks"] = index.count()
    snapshot["config"] = settings.safe_summary()
    return snapshot


@app.get("/api/events/stream")
async def events_stream() -> StreamingResponse:
    async def generator():
        while True:
            snapshot = store.snapshot()
            snapshot["indexed_chunks"] = index.count()
            snapshot["config"] = settings.safe_summary()
            yield f"event: snapshot\ndata: {json.dumps(snapshot, default=str)}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post(
    "/api/knowledge",
    response_model=KnowledgeDocument,
    status_code=202,
    dependencies=[Depends(_verify_api_key)],
)
@limiter.limit("30/minute")
def add_knowledge(request: Request, document: KnowledgeDocument) -> KnowledgeDocument:
    _require_kafka()
    store.add_document(document)
    kafka.produce(
        settings.topic_knowledge_raw,
        document.model_dump(),
        key=document.document_id,
    )
    kafka.flush(5)
    return document


@app.get("/api/knowledge")
def list_knowledge() -> list[dict[str, Any]]:
    return store.snapshot()["documents"]


@app.post(
    "/api/rag/ask",
    response_model=RagAnswer,
    dependencies=[Depends(_verify_api_key)],
)
@limiter.limit("10/minute")
def ask_rag(request: Request, question: RagQuestion) -> RagAnswer:
    _require_kafka()
    try:
        return rag.ask(question)
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        LOGGER.exception("RAG request failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(
    "/api/demo/seed-knowledge",
    dependencies=[Depends(_verify_api_key)],
)
@limiter.limit("5/minute")
def seed_demo_knowledge(request: Request) -> dict[str, Any]:
    _require_kafka()
    seeded = []
    for path in sorted(DEMO_KNOWLEDGE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text.strip() else path.stem
        document = KnowledgeDocument(
            document_id=f"demo-{path.stem}",
            title=title,
            text=text,
            source="demo-knowledge",
            asset_id="CNC-03" if "CNC-03" in text else None,
            metadata={"filename": path.name, "demo": True},
        )
        store.add_document(document)
        kafka.produce(
            settings.topic_knowledge_raw,
            document.model_dump(),
            key=document.document_id,
        )
        seeded.append(document.document_id)
    kafka.flush(10)
    return {"seeded": seeded, "count": len(seeded)}


@app.post(
    "/api/demo/step/{step}",
    dependencies=[Depends(_verify_api_key)],
)
@limiter.limit("30/minute")
def demo_step(request: Request, step: str) -> JSONResponse:
    _require_kafka()
    state, exception, new_knowledge = _build_demo_step(step)
    store.set_factory_state(state)
    kafka.produce(settings.topic_factory_state, state.model_dump(), key=state.machine_id)

    if exception:
        store.add_exception(exception)
        kafka.produce(
            settings.topic_factory_exceptions,
            exception.model_dump(),
            key=exception.machine_id,
        )

    if new_knowledge:
        store.add_document(new_knowledge)
        kafka.produce(
            settings.topic_knowledge_raw,
            new_knowledge.model_dump(),
            key=new_knowledge.document_id,
        )

    kafka.flush(5)
    return JSONResponse(
        {
            "step": step,
            "state": state.model_dump(),
            "exception": exception.model_dump() if exception else None,
            "knowledge_update": new_knowledge.model_dump() if new_knowledge else None,
        }
    )


def _build_demo_step(step: str) -> tuple[FactoryState, FactoryException | None, KnowledgeDocument | None]:
    step = step.lower()
    if step == "baseline":
        return (
            FactoryState(
                vibration_mm_s=2.1,
                temperature_c=61.5,
                cycle_time_sec=42,
                defect_rate_pct=1.2,
                produced_units=620,
                projected_units=1010,
                machine_health="healthy",
                production_risk="low",
                quality_risk="low",
                overall_risk="low",
                root_signal="Normal operation",
                recommendation="Continue monitoring",
            ),
            None,
            None,
        )
    if step == "degrade":
        return (
            FactoryState(
                vibration_mm_s=4.2,
                temperature_c=64.7,
                cycle_time_sec=51,
                defect_rate_pct=2.8,
                produced_units=641,
                projected_units=935,
                machine_health="warning",
                production_risk="medium",
                quality_risk="medium",
                overall_risk="medium",
                root_signal="Vibration trend rising on CNC-03",
                recommendation="Inspect tooling balance during next safe stop",
            ),
            FactoryException(
                severity="warning",
                machine_id="CNC-03",
                line_id="LINE-01",
                title="Machine degradation detected",
                description="Vibration and cycle time are rising together.",
                recommended_action="Check tool-holder balance and spindle condition.",
            ),
            None,
        )
    if step == "critical":
        return (
            FactoryState(
                vibration_mm_s=5.8,
                temperature_c=68.2,
                cycle_time_sec=63,
                defect_rate_pct=8.2,
                produced_units=662,
                projected_units=870,
                machine_health="critical",
                production_risk="critical",
                quality_risk="high",
                overall_risk="critical",
                root_signal="High vibration correlated with slower cycles and dimensional defects",
                recommendation="Stop CNC-03 at next safe opportunity and inspect spindle/tool holder",
            ),
            FactoryException(
                severity="critical",
                machine_id="CNC-03",
                line_id="LINE-01",
                title="Production target and quality at risk",
                description=(
                    "CNC-03 vibration reached 5.8 mm/s while cycle time increased to 63 s and "
                    "defect rate rose to 8.2%. Projected output is 870/1000."
                ),
                recommended_action=(
                    "Inspect spindle bearing, tool-holder balance, and alignment before continuing production."
                ),
            ),
            None,
        )
    if step == "resolved":
        maintenance_note = KnowledgeDocument(
            document_id="wo-11023-resolution",
            title="WO-11023 CNC-03 Tool-holder Imbalance Resolution",
            text=(
                "Work order WO-11023 — CNC-03, LINE-01. "
                "Technician: A. Reyes (Tech ID: TECH-409). Shift: Day shift, Supervisor: M. Alvarez.\n\n"
                "Symptom: CNC-03 spindle vibration reached 5.8 mm/s RMS during Gear Assembly production. "
                "Cycle time increased to 63 s (baseline 42 s). Defect rate rose to 8.2% — dimensional "
                "deviation on bore diameter GA-4471, parts oversized by 0.015–0.025 mm. "
                "Projected output dropped to 870 units against 1,000-unit shift target.\n\n"
                "Diagnostic sequence followed per MFG-DOC-CNC-002:\n"
                "Step 1 — Tool-holder inspection: Runout at 50 mm gauge length measured 0.0094 mm TIR "
                "(acceptance limit 0.003 mm). Balance class G6.3 found on active holder — LINE-01 "
                "specification requires G2.5 at 25,000 RPM. Tool holder (serial T-07-291) was incorrectly "
                "returned to active rack after previous job without balance re-verification. "
                "Root cause confirmed: tool-holder imbalance.\n"
                "Step 2 — Spindle bearing check: Spindle rotated freely, no roughness. "
                "Accelerometer spectrum normal — no bearing damage. Bearing cleared, no replacement needed.\n\n"
                "Corrective action: Replaced tool holder T-07-291 with balanced spare "
                "SANDVIK-390.140-4032 (G2.5, serial T-07-308, Tooling rack T-07). "
                "Applied torque spec 45 Nm per OEM retention knob specification. "
                "Performed spindle warm-up cycle (1,000 / 5,000 / 12,000 RPM, 10 min each).\n\n"
                "Verification: Post-repair vibration 2.1 mm/s RMS — returned to normal operating band. "
                "Cycle time 42 s — at baseline. Defect rate 1.1% — within normal range. "
                "Three consecutive test parts confirmed bore diameter within ±0.010 mm tolerance.\n\n"
                "Recommended inspection interval for CNC-03 tool holders: check balance class and runout "
                "every 200 operating hours or on any tooling change. "
                "When vibration rises together with dimensional drift, inspect tool-holder balance "
                "before opening the spindle — this case required 45 minutes to resolve vs 3.5 hours "
                "for a full bearing replacement (WO-10552 precedent)."
            ),
            source="maintenance-work-order",
            asset_id="CNC-03",
            metadata={"work_order": "WO-11023", "technician": "TECH-409", "resolution": "tool-holder replaced", "torque_spec_nm": "45"},
        )
        return (
            FactoryState(
                vibration_mm_s=2.1,
                temperature_c=62.2,
                cycle_time_sec=43,
                defect_rate_pct=1.1,
                produced_units=701,
                projected_units=982,
                machine_health="healthy",
                production_risk="medium",
                quality_risk="low",
                overall_risk="low",
                root_signal="CNC-03 stabilized after tool-holder replacement",
                recommendation="Monitor first 50 parts after recalibration",
            ),
            FactoryException(
                severity="info",
                machine_id="CNC-03",
                line_id="LINE-01",
                title="CNC-03 returned to stable operation",
                description="Vibration and quality signals normalized after maintenance.",
                recommended_action="Continue enhanced monitoring for the next 50 parts.",
            ),
            maintenance_note,
        )
    raise HTTPException(
        status_code=400,
        detail="Unknown step. Use baseline, degrade, critical, or resolved.",
    )


def _require_kafka() -> None:
    if not settings.kafka_ready:
        raise HTTPException(
            status_code=503,
            detail=(
                "Confluent Cloud is not configured. Set CONFLUENT_BOOTSTRAP_SERVERS, "
                "CONFLUENT_KAFKA_API_KEY and CONFLUENT_KAFKA_API_SECRET."
            ),
        )
