"""
Configuration classes for IBM watsonx.governance Prompt Template Evaluation.

This module provides dataclasses for configuring prompt template evaluation,
including credentials, evaluator settings, and monitor configurations.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


@dataclass
class WatsonxConfig:
    """
    Configuration for IBM watsonx services (OpenScale and Machine Learning).

    This class handles authentication credentials for both Watson OpenScale (WOS)
    and Watson Machine Learning (WML) services.

    Attributes:
        wos_url: Watson OpenScale service URL
        wos_username: Watson OpenScale username
        wos_password: Watson OpenScale password
        wml_url: Watson Machine Learning service URL
        wml_username: Watson Machine Learning username
        wml_password: Watson Machine Learning password
        wml_instance_id: WML instance ID (default: "wml_local")
        wml_version: WML API version (default: "5.0")

    Environment Variables:
        WOS_URL, WOS_USERNAME, WOS_PASSWORD: OpenScale credentials
        WML_URL, WML_USERNAME, WML_PASSWORD: Machine Learning credentials
    """

    wos_url: str = field(default_factory=lambda: os.getenv("WOS_URL", ""))
    wos_username: str = field(default_factory=lambda: os.getenv("WOS_USERNAME", ""))
    wos_password: str = field(default_factory=lambda: os.getenv("WOS_PASSWORD", ""))

    wml_url: str = field(default_factory=lambda: os.getenv("WML_URL", ""))
    wml_username: str = field(default_factory=lambda: os.getenv("WML_USERNAME", ""))
    wml_password: str = field(default_factory=lambda: os.getenv("WML_PASSWORD", ""))
    wml_instance_id: str = "wml_local"
    wml_version: str = "5.0"

    def __post_init__(self):
        """Validate that required credentials are provided."""
        if not all([self.wos_url, self.wos_username, self.wos_password]):
            raise ValueError(
                "Watson OpenScale credentials are required. "
                "Set WOS_URL, WOS_USERNAME, WOS_PASSWORD environment variables "
                "or pass them explicitly."
            )
        if not all([self.wml_url, self.wml_username, self.wml_password]):
            raise ValueError(
                "Watson Machine Learning credentials are required. "
                "Set WML_URL, WML_USERNAME, WML_PASSWORD environment variables "
                "or pass them explicitly."
            )

    def get_wos_credentials(self) -> Dict[str, str]:
        """Get Watson OpenScale credentials dictionary."""
        return {
            "url": self.wos_url,
            "username": self.wos_username,
            "password": self.wos_password
        }

    def get_wml_credentials(self) -> Dict[str, str]:
        """Get Watson Machine Learning credentials dictionary."""
        return {
            "url": self.wml_url,
            "username": self.wml_username,
            "password": self.wml_password,
            "instance_id": self.wml_instance_id,
            "version": self.wml_version
        }


@dataclass
class EvaluatorConfig:
    """
    Configuration for generative AI evaluator (SLM or LLM-as-Judge).

    This class configures the evaluation approach: either using OpenScale's
    built-in smaller models (SLM) or using an external LLM as judge.

    Attributes:
        evaluator_type: Type of evaluator ("slm" for built-in models, "llm" for LLM-as-judge)
        enabled: Whether to use the generative AI evaluator
        evaluator_id: ID of the evaluator integrated system (required for LLM-as-judge)
        model_id: Model ID for LLM-as-judge (e.g., "meta-llama/llama-3-1-8b-instruct")
        evaluator_name: Name for the evaluator integrated system
        evaluator_description: Description for the evaluator

    Example:
        >>> # For SLM (built-in models)
        >>> config = EvaluatorConfig(evaluator_type="slm")

        >>> # For LLM-as-Judge
        >>> config = EvaluatorConfig(
        ...     evaluator_type="llm",
        ...     model_id="meta-llama/llama-3-1-8b-instruct"
        ... )
    """

    evaluator_type: Literal["slm", "llm"] = "slm"
    enabled: bool = True
    evaluator_id: Optional[str] = None
    model_id: str = "meta-llama/llama-3-1-8b-instruct"
    evaluator_name: str = "Generative AI Evaluator"
    evaluator_description: str = "Evaluator for generative AI quality metrics"

    def __post_init__(self):
        """Validate evaluator configuration."""
        if self.evaluator_type == "llm" and self.enabled and not self.evaluator_id:
            # evaluator_id will be created during setup if not provided
            pass

    def is_llm_as_judge(self) -> bool:
        """Check if configured for LLM-as-judge evaluation."""
        return self.evaluator_type == "llm" and self.enabled

    def is_slm(self) -> bool:
        """Check if configured for SLM (built-in) evaluation."""
        return self.evaluator_type == "slm" or not self.enabled


@dataclass
class MonitorConfig:
    """
    Configuration for OpenScale monitor parameters.

    This class configures the monitoring settings for generative AI quality
    and model health metrics.

    Attributes:
        min_sample_size: Minimum sample size for metrics calculation
        faithfulness_enabled: Enable faithfulness metric
        faithfulness_attributions_count: Number of source attributions (SLM only)
        faithfulness_ngrams: N-gram grouping for faithfulness (SLM only)
        answer_relevance_enabled: Enable answer relevance metric
        answer_similarity_enabled: Enable answer similarity metric (LLM-as-judge only)
        rouge_score_enabled: Enable ROUGE score metric
        context_relevance_enabled: Enable context relevance metric
        context_relevance_ngrams: N-gram grouping for context relevance (SLM only)
        retrieval_quality_enabled: Enable retrieval quality metrics
        unsuccessful_requests_enabled: Enable unsuccessful requests detection
        unsuccessful_phrases: List of phrases indicating unsuccessful requests
        pii_enabled: Enable PII detection
        hap_enabled: Enable HAP (Hate, Abuse, Profanity) detection

    Example:
        >>> config = MonitorConfig(
        ...     faithfulness_enabled=True,
        ...     answer_relevance_enabled=True,
        ...     rouge_score_enabled=True
        ... )
    """

    min_sample_size: int = 1

    # Faithfulness configuration
    faithfulness_enabled: bool = True
    faithfulness_attributions_count: int = 3  # SLM only
    faithfulness_ngrams: int = 2  # SLM only

    # Answer relevance
    answer_relevance_enabled: bool = True

    # Answer similarity (LLM-as-judge only)
    answer_similarity_enabled: bool = True

    # ROUGE score
    rouge_score_enabled: bool = True

    # Context relevance
    context_relevance_enabled: bool = True
    context_relevance_ngrams: int = 2  # SLM only

    # Retrieval quality
    retrieval_quality_enabled: bool = True

    # Unsuccessful requests
    unsuccessful_requests_enabled: bool = False
    unsuccessful_phrases: List[str] = field(default_factory=lambda: [
        "i don't know", "i do not know", "i'm not sure", "i am not sure",
        "i'm unsure", "i am unsure", "i'm uncertain", "i am uncertain",
        "i'm not certain", "i am not certain", "i can't fulfill", "i cannot fulfill"
    ])

    # Safety metrics
    pii_enabled: bool = False
    hap_enabled: bool = False

    def to_openscale_config(self, evaluator_config: EvaluatorConfig) -> Dict:
        """
        Convert to OpenScale monitor configuration format.

        Args:
            evaluator_config: The evaluator configuration (SLM or LLM-as-judge)

        Returns:
            Dictionary in OpenScale monitor configuration format
        """
        metrics_config = {}

        # Faithfulness configuration
        if self.faithfulness_enabled:
            faithfulness_config = {}
            # Add SLM-specific parameters only if not using LLM-as-judge
            if evaluator_config.is_slm():
                faithfulness_config["attributions_count"] = self.faithfulness_attributions_count
                faithfulness_config["ngrams"] = self.faithfulness_ngrams
            metrics_config["faithfulness"] = faithfulness_config

        # Answer relevance
        if self.answer_relevance_enabled:
            metrics_config["answer_relevance"] = {}

        # Answer similarity (LLM-as-judge only)
        if self.answer_similarity_enabled and evaluator_config.is_llm_as_judge():
            metrics_config["answer_similarity"] = {}

        # ROUGE score
        if self.rouge_score_enabled:
            metrics_config["rouge_score"] = {}

        # Retrieval quality with context relevance
        if self.retrieval_quality_enabled:
            retrieval_config = {}
            if self.context_relevance_enabled:
                context_config = {}
                # Add SLM-specific parameters only if not using LLM-as-judge
                if evaluator_config.is_slm():
                    context_config["ngrams"] = self.context_relevance_ngrams
                retrieval_config["context_relevance"] = context_config
            metrics_config["retrieval_quality"] = retrieval_config

        # Unsuccessful requests
        if self.unsuccessful_requests_enabled:
            metrics_config["unsuccessful_requests"] = {
                "unsuccessful_phrases": self.unsuccessful_phrases
            }

        # PII detection
        if self.pii_enabled:
            metrics_config["pii"] = {}
            metrics_config["pii_input"] = {}

        # HAP detection
        if self.hap_enabled:
            metrics_config["hap_score"] = {}
            metrics_config["hap_input_score"] = {}

        # Build the full configuration
        config = {
            "generative_ai_quality": {
                "parameters": {
                    "min_sample_size": self.min_sample_size,
                    "metrics_configuration": metrics_config
                }
            }
        }

        # Add evaluator configuration if using LLM-as-judge
        if evaluator_config.is_llm_as_judge() and evaluator_config.evaluator_id:
            config["generative_ai_quality"]["parameters"]["generative_ai_evaluator"] = {
                "enabled": True,
                "evaluator_id": evaluator_config.evaluator_id
            }

        return config
