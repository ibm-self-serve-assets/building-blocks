#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from app.config import get_settings
from app.models import KnowledgeDocument
from app.services.kafka import KafkaGateway

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    settings = get_settings()
    kafka = KafkaGateway(settings)
    if not settings.kafka_ready:
        raise SystemExit("Confluent Cloud credentials are not configured.")

    for path in sorted((ROOT / "demo_knowledge").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        document = KnowledgeDocument(
            document_id=f"demo-{path.stem}",
            title=title,
            text=text,
            source="demo-knowledge",
            asset_id="CNC-03" if "CNC-03" in text else None,
            metadata={"filename": path.name, "demo": True},
        )
        kafka.produce(settings.topic_knowledge_raw, document.model_dump(), key=document.document_id)
        print(f"published {document.document_id}: {title}")

    kafka.flush(10)
    kafka.close()


if __name__ == "__main__":
    main()
