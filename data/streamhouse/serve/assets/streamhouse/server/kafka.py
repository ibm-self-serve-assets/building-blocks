# Optional Confluent Kafka transport. Local demo runs in mock mode without any cloud credentials.
# When STREAM_MODE=kafka and the confluent_kafka package is available, real Schema Registry governed
# publishing is attempted; otherwise the transport reports configuration_required.
import time
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).isoformat()


class ConfluentTransport:
    def __init__(self, env=None):
        import os as _os
        self.env = env or _os.environ
        self.mode = "kafka" if self.env.get("STREAM_MODE") == "kafka" else "mock"
        self.status = "disconnected"
        self.sent = 0
        self.failed = 0
        self.last_error = None
        self.last_ack = None
        self.producer = None
        self.registry = None
        self.ids = {}
        self.consumer = None
        self.source_consumer = None
        self.on_derived = None
        self.on_source = None

    def info(self):
        return {
            "mode": self.mode, "status": self.status, "sent": self.sent, "failed": self.failed,
            "lastError": self.last_error, "lastAck": self.last_ack,
            "topics": list(_value_schemas().keys()), "derivedConnected": self.consumer is not None,
            "sourceConnected": self.source_consumer is not None,
        }

    def connect(self):
        if self.mode != "kafka":
            self.status = "mock"
            return
        e = self.env
        mandatory = ["KAFKA_BOOTSTRAP_SERVERS", "KAFKA_API_KEY", "KAFKA_API_SECRET",
                     "SCHEMA_REGISTRY_URL", "SCHEMA_REGISTRY_API_KEY", "SCHEMA_REGISTRY_API_SECRET"]
        missing = [k for k in mandatory if not e.get(k)]
        if missing:
            self.status = "configuration_required"
            self.last_error = "Missing: " + ", ".join(missing)
            return
        try:
            from confluent_kafka import Producer  # type: ignore
            from confluent_kafka.schema_registry import SchemaRegistryClient, Schema  # type: ignore
        except Exception as exc:  # pragma: no cover - cloud-only optional dependency
            self.status = "configuration_required"
            self.last_error = f"confluent_kafka not installed: {exc}"
            return
        self.status = "connecting"
        try:
            conf = {"bootstrap.servers": e["KAFKA_BOOTSTRAP_SERVERS"], "security.protocol": "SASL_SSL",
                    "sasl.mechanism": "PLAIN", "sasl.username": e["KAFKA_API_KEY"],
                    "sasl.password": e["KAFKA_API_SECRET"]}
            self.producer = Producer(conf)
            self.registry = SchemaRegistryClient({"url": e["SCHEMA_REGISTRY_URL"],
                                                  "basic.auth.user.info": f"{e['SCHEMA_REGISTRY_API_KEY']}:{e['SCHEMA_REGISTRY_API_SECRET']}"})
            if e.get("KAFKA_AUTO_CREATE_TOPICS") == "true":
                from confluent_kafka.admin import AdminClient, NewTopic  # type: ignore
                admin = AdminClient(conf)
                topics = [NewTopic(t, num_partitions=3, replication_factor=3) for t in _value_schemas().keys()]
                fs = admin.create_topics(topics)
                for topic, f in fs.items():
                    try:
                        f.result()
                    except Exception:
                        pass
            for topic, schema in _value_schemas().items():
                key_schema = Schema(json.dumps(_key_schema()), "JSON")
                value_schema = Schema(json.dumps(schema), "JSON")
                key_id = self.registry.register_schema(f"{topic}-key", key_schema)
                value_id = self.registry.register_schema(f"{topic}-value", value_schema)
                self.ids[topic] = {"key": key_id, "value": value_id}
            self.status = "connected"
            self.last_error = None
            if e.get("KAFKA_CONSUME_DERIVED") == "true":
                self._connect_derived()
            if e.get("KAFKA_CONSUME_SOURCE") == "true":
                self._connect_source()
        except Exception as exc:
            self.status = "error"
            self.last_error = str(exc)
            self.disconnect()

    def _connect_derived(self):
        from confluent_kafka import Consumer  # type: ignore
        from confluent_kafka.schema_registry.json_schema import JSONDeserializer  # type: ignore
        e = self.env
        conf = {"bootstrap.servers": e["KAFKA_BOOTSTRAP_SERVERS"], "security.protocol": "SASL_SSL",
                "sasl.mechanism": "PLAIN", "sasl.username": e["KAFKA_API_KEY"],
                "sasl.password": e["KAFKA_API_SECRET"], "group.id": f"factory-pulse-output-{int(time.time()*1000)}",
                "auto.offset.reset": "latest"}
        self.consumer = Consumer(conf)
        topics = [e.get("KAFKA_RISK_TOPIC") or "factory-risk-signals", e.get("KAFKA_KPI_TOPIC") or "factory-shift-kpis"]
        self.consumer.subscribe(topics)

        def poll_loop():
            while self.consumer is not None:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    continue
                try:
                    value = json.loads(msg.value().decode("utf-8")) if msg.value() else None
                    if self.on_derived:
                        self.on_derived({"topic": msg.topic(), "value": value, "timestamp": now()})
                except Exception as exc:
                    self.last_error = f"Decode {msg.topic()}: {exc}"

        import threading as _threading
        _threading.Thread(target=poll_loop, daemon=True).start()

    def publish(self, batch):
        if self.status != "connected" or not self.producer or not batch:
            return
        try:
            by_topic = {}
            for item in batch:
                ids = self.ids.get(item["topic"])
                if not ids:
                    continue
                by_topic.setdefault(item["topic"], []).append(
                    {"key": json.dumps(item["key"]), "value": json.dumps(item["value"]), "timestamp": str(int(time.time() * 1000))}
                )
            for topic, messages in by_topic.items():
                for m in messages:
                    self.producer.produce(topic, key=m["key"], value=m["value"])
            self.producer.poll(0)
            self.sent += len(batch)
            self.last_ack = now()
            self.last_error = None
        except Exception as exc:
            self.failed += len(batch)
            self.status = "error"
            self.last_error = str(exc)

    def _connect_source(self):
        """Subscribe to the three source topics and forward raw messages to on_source."""
        from confluent_kafka import Consumer  # type: ignore
        e = self.env
        conf = {
            "bootstrap.servers": e["KAFKA_BOOTSTRAP_SERVERS"], "security.protocol": "SASL_SSL",
            "sasl.mechanism": "PLAIN", "sasl.username": e["KAFKA_API_KEY"],
            "sasl.password": e["KAFKA_API_SECRET"],
            "group.id": f"factory-pulse-source-{int(time.time() * 1000)}",
            "auto.offset.reset": "latest",
        }
        self.source_consumer = Consumer(conf)
        topics = [
            e.get("KAFKA_TELEMETRY_TOPIC") or "factory-iot-telemetry",
            e.get("KAFKA_STATE_TOPIC") or "factory-asset-state",
            e.get("KAFKA_EVENTS_TOPIC") or "factory-maintenance-events",
        ]
        self.source_consumer.subscribe(topics)

        def poll_loop():
            while self.source_consumer is not None:
                msg = self.source_consumer.poll(1.0)
                if msg is None or msg.error():
                    continue
                try:
                    value = json.loads(msg.value().decode("utf-8")) if msg.value() else None
                    if value and self.on_source:
                        self.on_source({"topic": msg.topic(), "value": value, "timestamp": now()})
                except Exception as exc:
                    self.last_error = f"Source decode {msg.topic()}: {exc}"

        import threading as _threading
        _threading.Thread(target=poll_loop, daemon=True).start()

    def disconnect(self):
        try:
            if self.consumer is not None:
                self.consumer.close()
        except Exception:
            pass
        try:
            if self.source_consumer is not None:
                self.source_consumer.close()
        except Exception:
            pass
        try:
            if self.producer is not None:
                self.producer.flush(5)
        except Exception:
            pass
        self.consumer = None
        self.source_consumer = None
        self.producer = None
        if self.status == "connected":
            self.status = "disconnected"


def _value_schemas():
    from schemas import VALUE_SCHEMAS
    return VALUE_SCHEMAS


def _key_schema():
    from schemas import KEY_SCHEMA
    return KEY_SCHEMA


import json  # noqa: E402
