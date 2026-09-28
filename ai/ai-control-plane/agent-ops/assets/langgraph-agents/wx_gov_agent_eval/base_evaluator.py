"""
Base evaluator class for wx_gov_agent_eval.

This module provides the base class that all specific evaluators inherit from,
ensuring consistent API and shared functionality.
"""

import os
import pandas as pd
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from ibm_watsonx_gov.evaluators.agentic_evaluator import AgenticEvaluator
from ibm_watsonx_gov.config.agentic_ai_configuration import TracingConfiguration

from .config import WatsonxConfig, EvaluationConfig
from .utils.auth import setup_environment, get_api_credentials
from .utils.metrics import format_metrics_dataframe, display_metrics
from .utils.batch_processing import batch_evaluate


class BaseAgentEvaluator(ABC):
    """Base class for all agent evaluators.

    This class provides common functionality for evaluating LangGraph agents
    using IBM watsonx.governance. Specific evaluators inherit from this class.

    Attributes:
        config: Watsonx configuration.
        eval_config: Evaluation configuration.
        evaluator: Internal AgenticEvaluator instance.
        agent: LangGraph agent being evaluated.

    Example:
        This is an abstract class. Use specific evaluators like:
        - BasicRAGEvaluator
        - ToolCallingEvaluator
        - AdvancedRAGEvaluator
    """

    def __init__(
        self,
        watsonx_config: Optional[WatsonxConfig] = None,
        eval_config: Optional[EvaluationConfig] = None,
        apikey: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """Initialize the base evaluator.

        Args:
            watsonx_config: Watsonx configuration (optional, will use env vars if not provided).
            eval_config: Evaluation configuration (optional, uses defaults if not provided).
            apikey: IBM Cloud API key (optional, alternative to watsonx_config).
            project_id: Watsonx project ID (optional, alternative to watsonx_config).
        """
        # Setup configuration
        if watsonx_config is None:
            if apikey and project_id:
                watsonx_config = WatsonxConfig(apikey=apikey, project_id=project_id)
            else:
                watsonx_config = WatsonxConfig.from_env()

        self.config = watsonx_config
        self.eval_config = eval_config or EvaluationConfig()

        # Setup environment
        setup_environment(
            apikey=self.config.apikey,
            project_id=self.config.project_id
        )

        # Initialize evaluator (subclasses will configure it)
        self.evaluator: Optional[AgenticEvaluator] = None
        self.agent = None

    @abstractmethod
    def build_agent(self, **kwargs) -> Any:
        """Build the LangGraph agent.

        This method must be implemented by subclasses to create their specific agent.

        Args:
            **kwargs: Agent-specific configuration parameters.

        Returns:
            Compiled LangGraph agent.
        """
        pass

    @abstractmethod
    def _setup_evaluator(self) -> AgenticEvaluator:
        """Setup the AgenticEvaluator with metrics specific to this agent type.

        This method must be implemented by subclasses.

        Returns:
            Configured AgenticEvaluator instance.
        """
        pass

    def evaluate_single(
        self,
        input_text: str,
        ground_truth: Optional[str] = None,
        interaction_id: str = "1",
        **kwargs
    ) -> Dict[str, Any]:
        """Evaluate agent on a single input.

        Args:
            input_text: Input question/query.
            ground_truth: Expected answer (optional, needed for some metrics).
            interaction_id: Unique ID for this interaction.
            **kwargs: Additional agent-specific parameters.

        Returns:
            Evaluation results including metrics.

        Example:
            ```python
            result = evaluator.evaluate_single(
                input_text="What is machine learning?",
                ground_truth="Machine learning is...",
                interaction_id="test-1"
            )
            ```
        """
        if self.agent is None:
            raise ValueError("Agent not built. Call build_agent() first.")

        if self.evaluator is None:
            self.evaluator = self._setup_evaluator()

        # Prepare input
        input_data = {
            "input_text": input_text,
            "interaction_id": interaction_id,
            **kwargs
        }

        if ground_truth:
            input_data["ground_truth"] = ground_truth

        # Run evaluation
        self.evaluator.start_run()
        result = self.agent.invoke(input_data)
        self.evaluator.end_run()

        return result

    def evaluate_batch(
        self,
        test_data: pd.DataFrame,
        batch_size: Optional[int] = None,
        parallel: bool = False
    ) -> List[Dict[str, Any]]:
        """Evaluate agent on a batch of test data.

        Args:
            test_data: DataFrame with test data (must include 'input_text' column).
            batch_size: Batch size for processing (uses config default if not provided).
            parallel: Whether to use parallel processing.

        Returns:
            List of evaluation results.

        Example:
            ```python
            test_df = pd.DataFrame({
                "input_text": ["Question 1", "Question 2"],
                "ground_truth": ["Answer 1", "Answer 2"]
            })

            results = evaluator.evaluate_batch(test_df, batch_size=10)
            ```
        """
        if self.agent is None:
            raise ValueError("Agent not built. Call build_agent() first.")

        if self.evaluator is None:
            self.evaluator = self._setup_evaluator()

        batch_size = batch_size or self.eval_config.batch_size

        self.evaluator.start_run()
        results = batch_evaluate(
            agent=self.agent,
            test_data=test_data,
            evaluator=self.evaluator,
            batch_size=batch_size,
            parallel=parallel
        )
        self.evaluator.end_run()

        return results

    def get_results(self) -> Any:
        """Get evaluation results.

        Returns:
            Evaluation results object.

        Example:
            ```python
            eval_result = evaluator.get_results()
            df = eval_result.to_df()
            ```
        """
        if self.evaluator is None:
            raise ValueError("No evaluation has been run yet.")

        return self.evaluator.get_result()

    def get_metrics_dataframe(self) -> pd.DataFrame:
        """Get metrics as a pandas DataFrame.

        Returns:
            DataFrame with all metrics.

        Example:
            ```python
            metrics_df = evaluator.get_metrics_dataframe()
            print(metrics_df.head())
            ```
        """
        result = self.get_results()
        return format_metrics_dataframe(result)

    def display_results(self, node_name: Optional[str] = None) -> None:
        """Display evaluation results.

        Args:
            node_name: Optional node name to filter results.

        Example:
            ```python
            evaluator.display_results()
            # Or for specific node
            evaluator.display_results(node_name="Generation Node")
            ```
        """
        result = self.get_results()
        display_metrics(result, node_name=node_name)

    def get_aggregated_metrics(self, node_name: str) -> Dict[str, Any]:
        """Get aggregated metrics for a specific node.

        Args:
            node_name: Name of the node to get metrics for.

        Returns:
            Dictionary of aggregated metrics.

        Example:
            ```python
            metrics = evaluator.get_aggregated_metrics("Retrieval Node")
            print(f"Average context relevance: {metrics['context_relevance']}")
            ```
        """
        result = self.get_results()
        return result.get_aggregated_metrics_results(node_name=node_name)

    def track_experiment(
        self,
        experiment_name: str,
        use_existing: bool = False
    ) -> str:
        """Enable experiment tracking in watsonx.governance.

        Args:
            experiment_name: Name of the experiment.
            use_existing: Whether to use existing experiment with this name.

        Returns:
            Experiment ID.

        Example:
            ```python
            experiment_id = evaluator.track_experiment(
                "RAG Agent Evaluation",
                use_existing=False
            )
            ```
        """
        if self.evaluator is None:
            self.evaluator = self._setup_evaluator()

        return self.evaluator.track_experiment(
            name=experiment_name,
            use_existing=use_existing
        )
