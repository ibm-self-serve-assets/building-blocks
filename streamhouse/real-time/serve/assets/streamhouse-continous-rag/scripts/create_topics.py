#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

from confluent_kafka.admin import AdminClient, NewTopic

from app.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create FactoryPulse Kafka topics")
    parser.add_argument(
        "--profile",
        choices=["local", "flink"],
        default="local",
        help=(
            "local creates every topic for the Python indexing demo. "
            "flink leaves Flink-owned embedding topics to the SQL DDL."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    if not settings.kafka_ready:
        print("Confluent Cloud credentials are not configured. Copy .env.example to .env and fill Kafka settings.")
        return 2

    admin = AdminClient(
        {
            "bootstrap.servers": settings.confluent_bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": settings.confluent_kafka_api_key,
            "sasl.password": settings.confluent_kafka_api_secret,
        }
    )

    base_topics = [
        settings.topic_machine_telemetry,
        settings.topic_production_events,
        settings.topic_quality_events,
        settings.topic_maintenance_events,
        settings.topic_factory_state,
        settings.topic_factory_exceptions,
        settings.topic_knowledge_raw,
        settings.topic_query_requests,
    ]
    flink_owned = [settings.topic_knowledge_embeddings, settings.topic_query_embeddings]
    topic_names = base_topics + (flink_owned if args.profile == "local" else [])

    topics = [
        NewTopic(
            name,
            num_partitions=3,
            replication_factor=-1,
            config={"cleanup.policy": "compact" if "embeddings" in name else "delete"},
        )
        for name in topic_names
    ]

    futures = admin.create_topics(topics)
    for name, future in futures.items():
        try:
            future.result()
            print(f"created: {name}")
        except Exception as exc:
            text = str(exc)
            if "TOPIC_ALREADY_EXISTS" in text or "already exists" in text.lower():
                print(f"exists:  {name}")
            else:
                print(f"error:   {name}: {exc}")
    if args.profile == "flink":
        print("Flink profile: create rag.knowledge.embeddings and rag.query.embeddings with infra/flink/continuous_rag.sql")
    return 0


if __name__ == "__main__":
    sys.exit(main())
