from __future__ import annotations

import os
import socket
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="FactoryPulse Streamhouse", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    port: int = Field(default=8080, alias="PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    confluent_enabled: bool = Field(default=True, alias="CONFLUENT_ENABLED")
    confluent_bootstrap_servers: str = Field(default="", alias="CONFLUENT_BOOTSTRAP_SERVERS")
    confluent_kafka_api_key: str = Field(default="", alias="CONFLUENT_KAFKA_API_KEY")
    confluent_kafka_api_secret: str = Field(default="", alias="CONFLUENT_KAFKA_API_SECRET")
    confluent_schema_registry_url: str = Field(default="", alias="CONFLUENT_SCHEMA_REGISTRY_URL")
    confluent_schema_registry_api_key: str = Field(default="", alias="CONFLUENT_SCHEMA_REGISTRY_API_KEY")
    confluent_schema_registry_api_secret: str = Field(default="", alias="CONFLUENT_SCHEMA_REGISTRY_API_SECRET")
    serialization_mode: str = Field(default="plain-json", alias="SERIALIZATION_MODE")

    rag_pipeline_mode: str = Field(default="local", alias="RAG_PIPELINE_MODE")
    rag_top_k: int = Field(default=4, alias="RAG_TOP_K")
    rag_chunk_size: int = Field(default=850, alias="RAG_CHUNK_SIZE")
    rag_chunk_overlap: int = Field(default=120, alias="RAG_CHUNK_OVERLAP")
    rag_embedding_dim: int = Field(default=384, alias="RAG_EMBEDDING_DIM")

    llm_provider: str = Field(default="none", alias="LLM_PROVIDER")
    watsonx_api_key: str = Field(default="", alias="WATSONX_API_KEY")
    watsonx_project_id: str = Field(default="", alias="WATSONX_PROJECT_ID")
    watsonx_model_id: str = Field(default="", alias="WATSONX_MODEL_ID")
    watsonx_url: str = Field(default="https://us-south.ml.cloud.ibm.com", alias="WATSONX_URL")
    watsonx_api_version: str = Field(default="2023-05-29", alias="WATSONX_API_VERSION")

    topic_machine_telemetry: str = Field(default="factory.machine.telemetry", alias="TOPIC_MACHINE_TELEMETRY")
    topic_production_events: str = Field(default="factory.production.events", alias="TOPIC_PRODUCTION_EVENTS")
    topic_quality_events: str = Field(default="factory.quality.events", alias="TOPIC_QUALITY_EVENTS")
    topic_maintenance_events: str = Field(default="factory.maintenance.events", alias="TOPIC_MAINTENANCE_EVENTS")
    topic_factory_state: str = Field(default="factory.state", alias="TOPIC_FACTORY_STATE")
    topic_factory_exceptions: str = Field(default="factory.exceptions", alias="TOPIC_FACTORY_EXCEPTIONS")
    topic_knowledge_raw: str = Field(default="rag.knowledge.raw", alias="TOPIC_KNOWLEDGE_RAW")
    topic_knowledge_embeddings: str = Field(default="rag.knowledge.embeddings", alias="TOPIC_KNOWLEDGE_EMBEDDINGS")
    topic_query_requests: str = Field(default="rag.query.requests", alias="TOPIC_QUERY_REQUESTS")
    topic_query_embeddings: str = Field(default="rag.query.embeddings", alias="TOPIC_QUERY_EMBEDDINGS")
    # Flink-owned intermediate topic (STANDARD clusters only)
    topic_machine_metrics: str = Field(default="factory.machine.metrics", alias="TOPIC_MACHINE_METRICS")

    # Security
    demo_api_key: str = Field(default="", alias="DEMO_API_KEY")

    # Tableflow
    tableflow_enabled: bool = Field(default=False, alias="TABLEFLOW_ENABLED")
    tableflow_topics: list[str] = Field(
        default_factory=lambda: ["factory.state", "factory.exceptions"],
        alias="TABLEFLOW_TOPICS",
    )

    instance_id: str = Field(
        default_factory=lambda: os.getenv("CE_APP")
        or f"{socket.gethostname()}-{os.getpid()}",
        alias="INSTANCE_ID",
    )

    @property
    def kafka_ready(self) -> bool:
        return bool(
            self.confluent_enabled
            and self.confluent_bootstrap_servers
            and self.confluent_kafka_api_key
            and self.confluent_kafka_api_secret
        )

    @property
    def schema_registry_ready(self) -> bool:
        return bool(
            self.confluent_schema_registry_url
            and self.confluent_schema_registry_api_key
            and self.confluent_schema_registry_api_secret
        )

    @property
    def watsonx_ready(self) -> bool:
        return bool(
            self.llm_provider.lower() == "watsonx"
            and self.watsonx_api_key
            and self.watsonx_project_id
            and self.watsonx_model_id
        )

    @property
    def effective_serialization_mode(self) -> str:
        """Return the effective serialization mode.

        SERIALIZATION_MODE in .env is always authoritative.
        Auto-promotion to 'schema-registry-json' only happens when
        SERIALIZATION_MODE is not set at all (falls back to the default 'plain-json'
        AND the env var is absent).  An explicit SERIALIZATION_MODE=plain-json in
        .env always wins and opts out of Schema Registry, even when SR credentials
        are present.
        """
        # If the operator explicitly set SERIALIZATION_MODE, honour it exactly.
        if os.getenv("SERIALIZATION_MODE") is not None:
            return self.serialization_mode
        # No explicit override — auto-promote when SR credentials are available.
        if self.schema_registry_ready:
            return "schema-registry-json"
        return self.serialization_mode

    def safe_summary(self) -> dict[str, object]:
        return {
            "app_env": self.app_env,
            "kafka_configured": self.kafka_ready,
            "schema_registry_configured": self.schema_registry_ready,
            "serialization_mode": self.serialization_mode,
            "effective_serialization_mode": self.effective_serialization_mode,
            "rag_pipeline_mode": self.rag_pipeline_mode,
            "llm_provider": self.llm_provider,
            "watsonx_configured": self.watsonx_ready,
            "tableflow_enabled": self.tableflow_enabled,
            "api_key_required": bool(self.demo_api_key),
            "instance_id": self.instance_id,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()
