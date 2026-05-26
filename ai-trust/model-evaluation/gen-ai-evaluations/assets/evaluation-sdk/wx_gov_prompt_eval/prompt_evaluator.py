"""
Main evaluator class for IBM watsonx.governance Prompt Template Assessment.

This module provides the PromptTemplateEvaluator class for creating, configuring,
and evaluating prompt template assets in Watson OpenScale.
"""

from typing import Dict, List, Optional
import pandas as pd
from ibm_aigov_facts_client import DetachedPromptTemplate, PromptTemplate

from wx_gov_prompt_eval.config import (
    WatsonxConfig,
    EvaluatorConfig,
    MonitorConfig
)
from wx_gov_prompt_eval.utils.auth import generate_access_token, get_user_id
from wx_gov_prompt_eval.utils.watsonx_clients import (
    create_wos_client,
    create_wml_client,
    create_facts_client,
    create_generative_ai_evaluator
)
from wx_gov_prompt_eval.utils.metrics import (
    extract_metrics,
    extract_record_level_metrics,
    plot_metrics,
    get_source_attributions,
    display_attributions
)


class PromptTemplateEvaluator:
    """
    Evaluator for IBM watsonx.governance Prompt Template Assets.

    This class provides a comprehensive interface for creating, configuring, and
    evaluating prompt template assets with both SLM (built-in models) and
    LLM-as-Judge approaches.

    Attributes:
        watsonx_config: Configuration for IBM watsonx services
        evaluator_config: Configuration for the evaluation approach (SLM or LLM)
        monitor_config: Configuration for OpenScale monitors
        project_id: CPD project ID (for development subscriptions)
        space_id: CPD space ID (for production subscriptions)
        data_mart_id: OpenScale data mart ID

    Example:
        >>> from wx_gov_prompt_eval import (
        ...     PromptTemplateEvaluator,
        ...     WatsonxConfig,
        ...     EvaluatorConfig,
        ...     MonitorConfig
        ... )
        >>>
        >>> # Configure credentials
        >>> watsonx_config = WatsonxConfig(
        ...     wos_url="https://cpd-instance.example.com",
        ...     wos_username="user@example.com",
        ...     wos_password="password123",
        ...     wml_url="https://cpd-instance.example.com",
        ...     wml_username="user@example.com",
        ...     wml_password="password123"
        ... )
        >>>
        >>> # Configure for LLM-as-Judge
        >>> evaluator_config = EvaluatorConfig(evaluator_type="llm")
        >>>
        >>> # Create evaluator
        >>> evaluator = PromptTemplateEvaluator(
        ...     watsonx_config=watsonx_config,
        ...     evaluator_config=evaluator_config,
        ...     project_id="project-123"
        ... )
        >>>
        >>> # Create prompt template
        >>> prompt_id = evaluator.create_prompt_template(
        ...     name="My RAG Prompt",
        ...     prompt_text="Answer: {retrieved_contexts}\\n\\nQuestion: {user_input}",
        ...     prompt_variables={"retrieved_contexts": "", "user_input": ""},
        ...     model_id="ibm/granite-3-8b-instruct"
        ... )
        >>>
        >>> # Setup monitoring
        >>> subscription_id = evaluator.setup_monitoring(
        ...     prompt_template_id=prompt_id,
        ...     context_fields=["retrieved_contexts"],
        ...     question_field="user_input",
        ...     label_column="ground_truths"
        ... )
        >>>
        >>> # Evaluate with test data
        >>> evaluator.evaluate(test_data_path="test_data.csv")
        >>>
        >>> # Display results
        >>> evaluator.display_metrics()
    """

    def __init__(
        self,
        watsonx_config: WatsonxConfig,
        evaluator_config: Optional[EvaluatorConfig] = None,
        monitor_config: Optional[MonitorConfig] = None,
        project_id: Optional[str] = None,
        space_id: Optional[str] = None,
        data_mart_id: str = "00000000-0000-0000-0000-000000000000"
    ):
        """
        Initialize the PromptTemplateEvaluator.

        Args:
            watsonx_config: Configuration for IBM watsonx services
            evaluator_config: Configuration for evaluation approach (defaults to SLM)
            monitor_config: Configuration for OpenScale monitors (defaults to standard config)
            project_id: CPD project ID (for development subscriptions)
            space_id: CPD space ID (for production subscriptions)
            data_mart_id: OpenScale data mart ID
        """
        self.watsonx_config = watsonx_config
        self.evaluator_config = evaluator_config or EvaluatorConfig()
        self.monitor_config = monitor_config or MonitorConfig()
        self.project_id = project_id
        self.space_id = space_id
        self.data_mart_id = data_mart_id

        # Initialize clients
        self.wos_client = create_wos_client(watsonx_config.get_wos_credentials())
        self.wml_client = create_wml_client(watsonx_config.get_wml_credentials())

        # Generate access token
        self.access_token = generate_access_token(watsonx_config.get_wos_credentials())

        # Storage for created resources
        self.prompt_template_id: Optional[str] = None
        self.subscription_id: Optional[str] = None
        self.mrm_monitor_id: Optional[str] = None
        self.genaiq_monitor_id: Optional[str] = None
        self.genaiq_dataset_id: Optional[str] = None

        # Create LLM evaluator if configured
        if self.evaluator_config.is_llm_as_judge() and not self.evaluator_config.evaluator_id:
            print("Creating generative AI evaluator (LLM-as-Judge)...")
            self.evaluator_config.evaluator_id = create_generative_ai_evaluator(
                wos_client=self.wos_client,
                wos_url=watsonx_config.wos_url,
                access_token=self.access_token,
                model_id=self.evaluator_config.model_id,
                evaluator_name=self.evaluator_config.evaluator_name,
                evaluator_description=self.evaluator_config.evaluator_description
            )
            print(f"✓ Created evaluator with ID: {self.evaluator_config.evaluator_id}")

    def create_prompt_template(
        self,
        name: str,
        prompt_text: str,
        prompt_variables: Dict[str, str],
        model_id: str = "ibm/granite-3-8b-instruct",
        description: str = "",
        task_id: str = "retrieval_augmented_generation",
        input_prefix: str = "",
        output_prefix: str = ""
    ) -> str:
        """
        Create a detached prompt template asset.

        Args:
            name: Name for the prompt template
            prompt_text: The prompt template text with variables
            prompt_variables: Dictionary of prompt variables and their default values
            model_id: Model ID to use
            description: Description for the prompt template
            task_id: Task type ID (default: "retrieval_augmented_generation")
            input_prefix: Input prefix text
            output_prefix: Output prefix text

        Returns:
            Prompt template asset ID

        Example:
            >>> prompt_id = evaluator.create_prompt_template(
            ...     name="RAG Q&A Prompt",
            ...     prompt_text="Answer: {context}\\n\\nQuestion: {question}",
            ...     prompt_variables={"context": "", "question": ""},
            ...     model_id="ibm/granite-3-8b-instruct"
            ... )
        """
        # Create facts client
        container_id = self.project_id or self.space_id
        container_type = "project" if self.project_id else "space"

        facts_client = create_facts_client(
            wos_credentials=self.watsonx_config.get_wos_credentials(),
            container_id=container_id,
            container_type=container_type
        )

        # Create detached information
        detached_information = DetachedPromptTemplate(
            prompt_id=f"detached_prompt_{name}",
            model_id=model_id,
            model_provider="IBM",
            model_name=model_id.split("/")[-1],
            model_url=f"{self.watsonx_config.wml_url}/ml/v1/deployments/text/generation",
            prompt_url="prompt_url",
            prompt_additional_info={}
        )

        # Create prompt template
        prompt_template = PromptTemplate(
            input=prompt_text,
            prompt_variables=prompt_variables,
            input_prefix=input_prefix,
            output_prefix=output_prefix,
        )

        # Create the asset
        print(f"Creating prompt template asset: {name}")
        pta_details = facts_client.assets.create_detached_prompt(
            model_id=model_id,
            task_id=task_id,
            name=name,
            description=description or f"Prompt template for {task_id}",
            prompt_details=prompt_template,
            detached_information=detached_information
        )

        self.prompt_template_id = pta_details.to_dict()["asset_id"]
        print(f"✓ Created prompt template with ID: {self.prompt_template_id}")

        return self.prompt_template_id

    def setup_monitoring(
        self,
        prompt_template_id: Optional[str] = None,
        context_fields: Optional[List[str]] = None,
        question_field: str = "user_input",
        label_column: str = "ground_truths",
        operational_space_id: str = "development",
        problem_type: str = "retrieval_augmented_generation",
        input_data_type: str = "unstructured_text",
        background_mode: bool = False
    ) -> str:
        """
        Setup OpenScale monitoring for the prompt template.

        Args:
            prompt_template_id: ID of the prompt template (uses stored ID if not provided)
            context_fields: List of context field names
            question_field: Name of the question field
            label_column: Name of the ground truth column
            operational_space_id: Operational space ("development", "pre_production", "production")
            problem_type: Problem type (default: "retrieval_augmented_generation")
            input_data_type: Input data type (default: "unstructured_text")
            background_mode: Whether to run setup in background

        Returns:
            Subscription ID

        Example:
            >>> subscription_id = evaluator.setup_monitoring(
            ...     context_fields=["retrieved_contexts"],
            ...     question_field="user_input",
            ...     label_column="ground_truths"
            ... )
        """
        prompt_id = prompt_template_id or self.prompt_template_id
        if not prompt_id:
            raise ValueError("No prompt template ID provided or stored")

        context_fields = context_fields or ["retrieved_contexts"]

        # Build monitor configuration
        monitors = self.monitor_config.to_openscale_config(self.evaluator_config)

        print(f"Setting up OpenScale monitoring for prompt template {prompt_id}")
        print(f"Evaluation mode: {'LLM-as-Judge' if self.evaluator_config.is_llm_as_judge() else 'SLM (built-in models)'}")

        response = self.wos_client.wos.execute_prompt_setup(
            prompt_template_asset_id=prompt_id,
            project_id=self.project_id,
            space_id=self.space_id,
            context_fields=context_fields,
            question_field=question_field,
            label_column=label_column,
            operational_space_id=operational_space_id,
            problem_type=problem_type,
            input_data_type=input_data_type,
            supporting_monitors=monitors,
            background_mode=background_mode
        )

        result = response.result._to_dict()

        if result["status"]["state"] == "FINISHED":
            self.subscription_id = result["subscription_id"]
            print(f"✓ Monitoring setup complete. Subscription ID: {self.subscription_id}")
        else:
            print(f"⚠ Monitoring setup status: {result['status']['state']}")
            self.subscription_id = result.get("subscription_id")

        return self.subscription_id

    def evaluate(
        self,
        test_data_path: str,
        subscription_id: Optional[str] = None,
        background_mode: bool = False
    ) -> Dict:
        """
        Evaluate the prompt template with test data.

        Args:
            test_data_path: Path to test data CSV file
            subscription_id: Subscription ID (uses stored ID if not provided)
            background_mode: Whether to run evaluation in background

        Returns:
            Dictionary with evaluation results

        Example:
            >>> results = evaluator.evaluate("test_data.csv")
        """
        sub_id = subscription_id or self.subscription_id
        if not sub_id:
            raise ValueError("No subscription ID provided or stored")

        # Get MRM monitor instance ID
        if not self.mrm_monitor_id:
            self._get_monitor_instance_ids(sub_id)

        print(f"Running risk evaluation on {test_data_path}")

        # Read test data
        test_data = pd.read_csv(test_data_path, encoding='unicode_escape')

        # Process each row
        results = []
        for index, row in test_data.iterrows():
            row_with_headers = dict(zip(test_data.columns, row))
            temp_path = "temp_input.csv"
            pd.DataFrame([row_with_headers]).to_csv(temp_path, index=False)

            response = self.wos_client.monitor_instances.mrm.evaluate_risk(
                monitor_instance_id=self.mrm_monitor_id,
                test_data_set_name="data.csv",
                test_data_path=temp_path,
                content_type="multipart/form-data",
                body={},
                project_id=self.project_id,
                space_id=self.space_id,
                background_mode=background_mode
            )
            results.append(response)

            if (index + 1) % 10 == 0:
                print(f"  Processed {index + 1}/{len(test_data)} records")

        print(f"✓ Evaluation complete. Processed {len(test_data)} records")

        return {"total_records": len(test_data), "results": results}

    def display_metrics(
        self,
        monitor_type: str = "generative_ai_quality",
        limit: int = 20
    ) -> None:
        """
        Display evaluation metrics.

        Args:
            monitor_type: Type of monitor ("generative_ai_quality" or "mrm")
            limit: Maximum number of records to display

        Example:
            >>> evaluator.display_metrics()
        """
        if not self.subscription_id:
            raise ValueError("No subscription ID available. Run setup_monitoring first.")

        if monitor_type == "generative_ai_quality":
            if not self.genaiq_monitor_id:
                self._get_monitor_instance_ids(self.subscription_id)

            print(f"\n=== Generative AI Quality Metrics ===")
            self.wos_client.monitor_instances.show_metrics(
                monitor_instance_id=self.genaiq_monitor_id,
                project_id=self.project_id,
                space_id=self.space_id,
                limit=limit
            )
        else:
            if not self.mrm_monitor_id:
                self._get_monitor_instance_ids(self.subscription_id)

            print(f"\n=== Model Risk Metrics ===")
            self.wos_client.monitor_instances.show_metrics(
                monitor_instance_id=self.mrm_monitor_id,
                project_id=self.project_id,
                space_id=self.space_id
            )

    def get_record_level_metrics(self) -> pd.DataFrame:
        """
        Get record-level metrics as a DataFrame.

        Returns:
            DataFrame containing record-level metrics

        Example:
            >>> df = evaluator.get_record_level_metrics()
            >>> print(df.head())
        """
        if not self.genaiq_dataset_id:
            self._get_dataset_id()

        df = extract_record_level_metrics(
            wos_client=self.wos_client,
            dataset_id=self.genaiq_dataset_id
        )

        return df

    def plot_metrics(
        self,
        metric_columns: Optional[List[str]] = None,
        figsize=(12, 8)
    ) -> None:
        """
        Plot metrics against record IDs.

        Args:
            metric_columns: List of metric columns to plot (defaults to common metrics)
            figsize: Figure size as (width, height)

        Example:
            >>> evaluator.plot_metrics(
            ...     metric_columns=["faithfulness", "answer_relevance"]
            ... )
        """
        df = self.get_record_level_metrics()

        if metric_columns is None:
            # Default to common metrics
            metric_columns = []
            for col in ["faithfulness", "answer_relevance", "rouge_score"]:
                if col in df.columns:
                    metric_columns.append(col)

        plot_metrics(
            metrics_df=df,
            metric_columns=metric_columns,
            figsize=figsize
        )

    def get_factsheets_url(self) -> str:
        """
        Get the URL to view factsheets for the prompt template.

        Returns:
            Factsheets URL string

        Example:
            >>> url = evaluator.get_factsheets_url()
            >>> print(f"View factsheets at: {url}")
        """
        if not self.prompt_template_id:
            raise ValueError("No prompt template ID available")

        container_id = self.project_id or self.space_id
        container_type = "project_id" if self.project_id else "space_id"

        url = (
            f"{self.watsonx_config.wml_url}/wx/prompt-details/"
            f"{self.prompt_template_id}/factsheet?context=wx&{container_type}={container_id}"
        )

        return url

    def _get_monitor_instance_ids(self, subscription_id: str) -> None:
        """Get monitor instance IDs for MRM and GenAI quality."""
        # Get MRM monitor instance ID
        result = self.wos_client.monitor_instances.list(
            data_mart_id=self.data_mart_id,
            monitor_definition_id="mrm",
            target_target_id=subscription_id,
            project_id=self.project_id,
            space_id=self.space_id
        ).result

        result_json = result._to_dict()
        if result_json["monitor_instances"]:
            self.mrm_monitor_id = result_json["monitor_instances"][0]["metadata"]["id"]

        # Get GenAI quality monitor instance ID
        result = self.wos_client.monitor_instances.list(
            data_mart_id=self.data_mart_id,
            monitor_definition_id="generative_ai_quality",
            target_target_id=subscription_id,
            project_id=self.project_id,
            space_id=self.space_id
        ).result

        result_json = result._to_dict()
        if result_json["monitor_instances"]:
            self.genaiq_monitor_id = result_json["monitor_instances"][0]["metadata"]["id"]

    def _get_dataset_id(self) -> None:
        """Get the generative AI quality dataset ID."""
        result = self.wos_client.data_sets.list(
            target_target_id=self.subscription_id,
            target_target_type="subscription",
            type="gen_ai_quality_metrics"
        ).result

        if result.data_sets:
            self.genaiq_dataset_id = result.data_sets[0].metadata.id
