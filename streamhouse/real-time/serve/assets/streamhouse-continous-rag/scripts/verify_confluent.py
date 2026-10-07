#!/usr/bin/env python3
"""Verify Confluent Cloud Kafka credentials without printing secrets."""
from __future__ import annotations

import sys

from confluent_kafka.admin import AdminClient

from app.config import get_settings


def main() -> int:
    settings = get_settings()
    if not settings.kafka_ready:
        print("NOT READY: Kafka bootstrap server/API key/API secret are not configured.")
        print("Copy .env.example to .env and populate the CONFLUENT_* Kafka values.")
        return 2

    admin = AdminClient(
        {
            "bootstrap.servers": settings.confluent_bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": settings.confluent_kafka_api_key,
            "sasl.password": settings.confluent_kafka_api_secret,
            "client.id": "factorypulse-config-check",
        }
    )

    try:
        metadata = admin.list_topics(timeout=12)
    except Exception as exc:
        print(f"FAILED: could not connect/authenticate to Confluent Cloud: {exc}")
        return 1

    expected = {
        settings.topic_knowledge_raw,
        settings.topic_knowledge_embeddings,
        settings.topic_factory_state,
        settings.topic_factory_exceptions,
    }
    existing = set(metadata.topics)
    print(f"OK: connected to cluster {metadata.cluster_id or '(cluster id unavailable)'}")
    print(f"Bootstrap: {settings.confluent_bootstrap_servers}")
    print(f"Topics visible: {len(existing)}")
    missing = sorted(expected - existing)
    if missing:
        print("FactoryPulse topics not created yet: " + ", ".join(missing))
        print("Run: python scripts/create_topics.py --profile local")
    else:
        print("FactoryPulse core topics are visible.")
    print("No API secret was printed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
