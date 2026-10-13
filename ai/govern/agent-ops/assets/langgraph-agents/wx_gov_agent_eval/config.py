"""
Configuration classes for wx_gov_agent_eval.

This module provides configuration management for watsonx.governance agent evaluation.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class WatsonxConfig:
    """Configuration for IBM watsonx.governance connection.

    Attributes:
        apikey: IBM Cloud API key for watsonx.governance.
        project_id: Watsonx project ID.
        url: Watsonx API URL (default: us-south).
        region: IBM Cloud region (optional).
        service_instance_id: Watsonx.governance service instance ID (optional).

    Example:
        ```python
        config = WatsonxConfig(
            apikey=os.getenv("WATSONX_APIKEY"),
            project_id=os.getenv("WATSONX_PROJECT_ID")
        )
        ```
    """

    apikey: str
    project_id: str
    url: str = "https://us-south.ml.cloud.ibm.com"
    region: Optional[str] = None
    service_instance_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "WatsonxConfig":
        """Create configuration from environment variables.

        Expects:
            - WATSONX_APIKEY
            - WATSONX_PROJECT_ID
            - WATSONX_URL (optional)
            - WATSONX_REGION (optional)
            - WXG_SERVICE_INSTANCE_ID (optional)

        Returns:
            WatsonxConfig instance.

        Raises:
            ValueError: If required environment variables are missing.

        Example:
            ```python
            config = WatsonxConfig.from_env()
            ```
        """
        apikey = os.getenv("WATSONX_APIKEY")
        project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("WXG_PROJECT_ID")

        if not apikey or not project_id:
            raise ValueError(
                "WATSONX_APIKEY and WATSONX_PROJECT_ID (or WXG_PROJECT_ID) environment variables are required"
            )

        return cls(
            apikey=apikey,
            project_id=project_id,
            url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
            region=os.getenv("WATSONX_REGION"),
            service_instance_id=os.getenv("WXG_SERVICE_INSTANCE_ID")
        )


@dataclass
class EvaluationConfig:
    """Configuration for evaluation metrics and behavior.

    Attributes:
        compute_real_time: Whether to compute metrics in real-time during evaluation.
        enable_tracing: Enable experiment tracking in watsonx.governance.
        batch_size: Batch size for batch evaluations (for performance).
        enable_content_safety: Enable content safety metrics (PII, HAP, HARM, etc.).
        enable_cost_metrics: Enable cost and latency tracking.
        custom_metrics: Additional custom metric configurations.

    Example:
        ```python
        eval_config = EvaluationConfig(
            compute_real_time=False,
            enable_tracing=True,
            batch_size=10
        )
        ```
    """

    compute_real_time: bool = False
    enable_tracing: bool = True
    batch_size: int = 10
    enable_content_safety: bool = False
    enable_cost_metrics: bool = True
    custom_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorStoreConfig:
    """Configuration for vector store setup.

    Attributes:
        embedding_model_id: Watsonx embedding model ID.
        chunk_size: Document chunk size for splitting.
        chunk_overlap: Overlap between chunks.
        similarity_threshold: Similarity threshold for retrieval.
        top_k: Number of top documents to retrieve.
        persist_directory: Directory to persist vector store.

    Example:
        ```python
        vs_config = VectorStoreConfig(
            embedding_model_id="ibm/slate-30m-english-rtrvr-v2",
            chunk_size=400,
            top_k=3
        )
        ```
    """

    embedding_model_id: str = "ibm/slate-30m-english-rtrvr-v2"
    chunk_size: int = 400
    chunk_overlap: int = 50
    similarity_threshold: float = 0.1
    top_k: int = 3
    persist_directory: str = "vector_store"


@dataclass
class LLMConfig:
    """Configuration for LLM model used in agents.

    Attributes:
        model_id: Watsonx LLM model ID.
        max_new_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.
        decoding_method: Decoding method (greedy, sample, etc.).
        repetition_penalty: Repetition penalty.
        stop_sequences: Stop sequences for generation.

    Example:
        ```python
        llm_config = LLMConfig(
            model_id="meta-llama/llama-3-3-70b-instruct",
            max_new_tokens=500,
            temperature=0.7
        )
        ```
    """

    model_id: str = "meta-llama/llama-3-3-70b-instruct"
    max_new_tokens: int = 500
    temperature: float = 0.0
    decoding_method: str = "greedy"
    repetition_penalty: float = 1.1
    stop_sequences: list = field(default_factory=lambda: ["."])
