from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Callable

from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.serialization import MessageField, SerializationContext

from app.config import Settings

LOGGER = logging.getLogger(__name__)
SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"

_PROBE_CACHE_TTL = 10.0  # seconds between live broker checks


class KafkaGateway:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._producer: Producer | None = None
        self._schema_registry_client = None
        self._serializers: dict[str, Any] = {}
        self._deserializer = None
        self._threads: list[threading.Thread] = []
        self._stop = threading.Event()
        self._probe_cache: dict[str, Any] | None = None
        self._probe_cache_ts: float = 0.0
        self._probe_lock = threading.Lock()

        if not settings.kafka_ready:
            LOGGER.warning("Confluent Cloud is not configured; Kafka operations are disabled.")
            return

        self._producer = Producer(self._kafka_common_config())
        self._configure_schema_registry_if_requested()

    def _kafka_common_config(self) -> dict[str, Any]:
        return {
            "bootstrap.servers": self.settings.confluent_bootstrap_servers,
            "security.protocol": "SASL_SSL",
            "sasl.mechanisms": "PLAIN",
            "sasl.username": self.settings.confluent_kafka_api_key,
            "sasl.password": self.settings.confluent_kafka_api_secret,
            "client.id": f"factorypulse-{self.settings.instance_id}",
        }

    def _configure_schema_registry_if_requested(self) -> None:
        if self.settings.effective_serialization_mode != "schema-registry-json":
            return
        if not self.settings.schema_registry_ready:
            raise RuntimeError(
                "SERIALIZATION_MODE=schema-registry-json requires Schema Registry URL/key/secret."
            )
        from confluent_kafka.schema_registry import SchemaRegistryClient
        from confluent_kafka.schema_registry.json_schema import JSONDeserializer

        self._schema_registry_client = SchemaRegistryClient(
            {
                "url": self.settings.confluent_schema_registry_url,
                "basic.auth.user.info": (
                    f"{self.settings.confluent_schema_registry_api_key}:"
                    f"{self.settings.confluent_schema_registry_api_secret}"
                ),
            }
        )
        self._deserializer = JSONDeserializer(
            schema_str=None,
            schema_registry_client=self._schema_registry_client,
        )

    def _schema_path_for_topic(self, topic: str) -> Path:
        mapping = {
            self.settings.topic_knowledge_raw: "knowledge_raw.json",
            self.settings.topic_knowledge_embeddings: "knowledge_embedding.json",
            self.settings.topic_factory_state: "factory_state.json",
            self.settings.topic_factory_exceptions: "factory_exception.json",
            self.settings.topic_query_requests: "query_request.json",
            self.settings.topic_query_embeddings: "query_embedding.json",
        }
        return SCHEMA_DIR / mapping.get(topic, "generic_event.json")

    def _encode(self, topic: str, value: dict[str, Any]) -> bytes:
        if self.settings.effective_serialization_mode != "schema-registry-json":
            return json.dumps(value, separators=(",", ":"), default=str).encode("utf-8")

        from confluent_kafka.schema_registry.json_schema import JSONSerializer

        serializer = self._serializers.get(topic)
        if serializer is None:
            schema_str = self._schema_path_for_topic(topic).read_text(encoding="utf-8")
            serializer = JSONSerializer(
                schema_str=schema_str,
                schema_registry_client=self._schema_registry_client,
                conf={"auto.register.schemas": True},
            )
            self._serializers[topic] = serializer
        return serializer(value, SerializationContext(topic, MessageField.VALUE))

    def _decode(self, topic: str, payload: bytes | None) -> dict[str, Any] | None:
        if payload is None:
            return None
        if self.settings.effective_serialization_mode != "schema-registry-json":
            return json.loads(payload.decode("utf-8"))
        return self._deserializer(payload, SerializationContext(topic, MessageField.VALUE))

    def produce(self, topic: str, value: dict[str, Any], key: str | None = None) -> None:
        if not self._producer:
            raise RuntimeError("Confluent Cloud is not configured.")
        encoded = self._encode(topic, value)
        self._producer.produce(
            topic=topic,
            key=key.encode("utf-8") if key else None,
            value=encoded,
            on_delivery=self._delivery_report,
        )
        self._producer.poll(0)

    def flush(self, timeout: float = 10.0) -> int:
        if not self._producer:
            return 0
        return self._producer.flush(timeout)

    @staticmethod
    def _delivery_report(err, msg) -> None:
        if err is not None:
            LOGGER.error("Kafka delivery failed: %s", err)

    def start_consumer(
        self,
        topic: str,
        group_id: str,
        handler: Callable[[dict[str, Any]], None],
        *,
        auto_offset_reset: str = "earliest",
    ) -> threading.Thread | None:
        if not self.settings.kafka_ready:
            return None

        config = self._kafka_common_config()
        config.update(
            {
                "group.id": group_id,
                "auto.offset.reset": auto_offset_reset,
                "enable.auto.commit": True,
            }
        )

        def loop() -> None:
            consumer = Consumer(config)
            consumer.subscribe([topic])
            LOGGER.info("Consumer started topic=%s group=%s", topic, group_id)
            try:
                while not self._stop.is_set():
                    msg = consumer.poll(1.0)
                    if msg is None:
                        continue
                    if msg.error():
                        if msg.error().code() != KafkaError._PARTITION_EOF:
                            LOGGER.warning("Kafka consumer error on %s: %s", topic, msg.error())
                        continue
                    try:
                        decoded = self._decode(topic, msg.value())
                        if decoded is not None:
                            handler(decoded)
                    except Exception:
                        LOGGER.exception("Failed processing record from %s", topic)
            finally:
                consumer.close()

        thread = threading.Thread(target=loop, name=f"consumer-{topic}", daemon=True)
        thread.start()
        self._threads.append(thread)
        return thread

    def probe(self) -> dict[str, Any]:
        """Live broker check using the already-authenticated producer connection.

        Reuses the existing SASL_SSL session — no cold TCP+auth overhead.
        Result is cached for ``_PROBE_CACHE_TTL`` seconds.
        """
        with self._probe_lock:
            age = time.monotonic() - self._probe_cache_ts
            if self._probe_cache is not None and age < _PROBE_CACHE_TTL:
                return self._probe_cache

        if not self.settings.kafka_ready or self._producer is None:
            result: dict[str, Any] = {"connected": False, "error": "Kafka credentials not configured"}
            with self._probe_lock:
                self._probe_cache = result
                self._probe_cache_ts = time.monotonic()
            return result

        started = time.monotonic()
        try:
            # list_topics() on the existing producer uses the already-open
            # broker connection — no new SASL handshake needed.
            meta = self._producer.list_topics(timeout=5)
            latency_ms = int((time.monotonic() - started) * 1000)
            fp_topics = [t for t in meta.topics if "factory." in t or "rag." in t]
            result = {
                "connected": True,
                "cluster_id": meta.cluster_id,
                "broker_count": len(meta.brokers),
                "topic_count": len(meta.topics),
                "factorypulse_topics": len(fp_topics),
                "latency_ms": latency_ms,
            }
        except Exception as exc:
            latency_ms = int((time.monotonic() - started) * 1000)
            result = {"connected": False, "error": str(exc), "latency_ms": latency_ms}
            LOGGER.warning("Kafka probe failed: %s", exc)

        with self._probe_lock:
            self._probe_cache = result
            self._probe_cache_ts = time.monotonic()
        return result

    def close(self) -> None:
        self._stop.set()
        self.flush(5)
        for thread in self._threads:
            thread.join(timeout=2)
