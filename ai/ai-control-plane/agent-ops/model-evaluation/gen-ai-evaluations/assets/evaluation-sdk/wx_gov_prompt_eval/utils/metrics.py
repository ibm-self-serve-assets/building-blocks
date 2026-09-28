"""
Metrics extraction and visualization utilities.

This module provides functions for extracting, formatting, and visualizing
evaluation metrics from Watson OpenScale.
"""

from typing import Dict, List, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt


def extract_metrics(
    wos_client,
    monitor_instance_id: str,
    project_id: Optional[str] = None,
    space_id: Optional[str] = None
) -> pd.DataFrame:
    """
    Extract metrics from a Watson OpenScale monitor instance.

    Args:
        wos_client: Watson OpenScale API client
        monitor_instance_id: ID of the monitor instance
        project_id: Project ID (for development subscriptions)
        space_id: Space ID (for production subscriptions)

    Returns:
        DataFrame containing the metrics

    Example:
        >>> metrics_df = extract_metrics(
        ...     wos_client=wos_client,
        ...     monitor_instance_id="monitor-123",
        ...     project_id="project-456"
        ... )
    """
    if project_id:
        result = wos_client.monitor_instances.show_metrics(
            monitor_instance_id=monitor_instance_id,
            project_id=project_id
        )
    elif space_id:
        result = wos_client.monitor_instances.show_metrics(
            monitor_instance_id=monitor_instance_id,
            space_id=space_id
        )
    else:
        raise ValueError("Either project_id or space_id must be provided")

    # The result is displayed as HTML in notebooks, but we can also get the data
    # For now, return a simple confirmation
    return result


def extract_record_level_metrics(
    wos_client,
    dataset_id: str
) -> pd.DataFrame:
    """
    Extract record-level metrics from a dataset.

    Args:
        wos_client: Watson OpenScale API client
        dataset_id: ID of the generative AI quality dataset

    Returns:
        DataFrame containing record-level metrics

    Example:
        >>> records_df = extract_record_level_metrics(
        ...     wos_client=wos_client,
        ...     dataset_id="dataset-123"
        ... )
    """
    result = wos_client.data_sets.get_list_of_records(
        data_set_id=dataset_id
    ).result

    # Extract records into a list of dictionaries
    table_data = []
    for record in result["records"]:
        entity_values = record["entity"]["values"]
        metadata = record["metadata"]
        flat_record = {**entity_values, **metadata}
        table_data.append(flat_record)

    # Create DataFrame
    df = pd.DataFrame(table_data)
    return df


def format_metrics_table(metrics_df: pd.DataFrame) -> str:
    """
    Format metrics DataFrame as a readable table.

    Args:
        metrics_df: DataFrame containing metrics

    Returns:
        Formatted string representation of the metrics table

    Example:
        >>> table_str = format_metrics_table(metrics_df)
        >>> print(table_str)
    """
    return metrics_df.to_string(index=False)


def plot_metrics(
    metrics_df: pd.DataFrame,
    metric_columns: List[str],
    record_id_column: str = "id",
    title: str = "Metrics by Record",
    figsize: Tuple[int, int] = (12, 6)
) -> None:
    """
    Plot metrics against record IDs.

    Args:
        metrics_df: DataFrame containing metrics
        metric_columns: List of metric column names to plot
        record_id_column: Column name for record IDs
        title: Plot title
        figsize: Figure size as (width, height)

    Example:
        >>> plot_metrics(
        ...     metrics_df=df,
        ...     metric_columns=["faithfulness", "answer_relevance"],
        ...     title="Quality Metrics by Record"
        ... )
    """
    # Extract record IDs (last 5 characters for readability)
    x = [str(rid)[-5:] for rid in metrics_df[record_id_column]]

    # Create subplots for each metric
    num_metrics = len(metric_columns)
    fig, axes = plt.subplots(num_metrics, 1, figsize=figsize)

    if num_metrics == 1:
        axes = [axes]

    for i, metric in enumerate(metric_columns):
        if metric in metrics_df.columns:
            y = metrics_df[metric]
            axes[i].scatter(x, y, marker='o')
            axes[i].set_xlabel('Record ID (last 5 characters)')
            axes[i].set_ylabel(metric.replace('_', ' ').title())
            axes[i].set_title(f'{metric.replace("_", " ").title()} vs Record ID')
            axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def get_source_attributions(
    wos_client,
    subscription_id: str,
    record_id: str,
    project_id: Optional[str] = None,
    space_id: Optional[str] = None
) -> Dict:
    """
    Get source attributions for a specific record.

    Source attributions show which parts of the context contributed to
    generating the answer.

    Args:
        wos_client: Watson OpenScale API client
        subscription_id: Subscription ID
        record_id: Record ID to get attributions for
        project_id: Project ID (for development subscriptions)
        space_id: Space ID (for production subscriptions)

    Returns:
        Dictionary containing attribution information

    Example:
        >>> attributions = get_source_attributions(
        ...     wos_client=wos_client,
        ...     subscription_id="sub-123",
        ...     record_id="rec-456",
        ...     project_id="project-789"
        ... )
    """
    if project_id:
        result = wos_client.subscriptions.get_attributions(
            subscription_id=subscription_id,
            record_id=record_id,
            project_id=project_id
        ).result
    elif space_id:
        result = wos_client.subscriptions.get_attributions(
            subscription_id=subscription_id,
            record_id=record_id,
            space_id=space_id
        ).result
    else:
        raise ValueError("Either project_id or space_id must be provided")

    return result._to_dict()


def display_attributions(attributions: Dict) -> None:
    """
    Display source attributions in a readable format.

    Args:
        attributions: Attribution dictionary from get_source_attributions

    Example:
        >>> display_attributions(attributions)
    """
    if "entity" in attributions and "attributions" in attributions["entity"]:
        for i, attribution in enumerate(attributions["entity"]["attributions"], 1):
            print(f"\n=== Attribution {i} ===")
            print(f"Sentence: {attribution.get('sentence', 'N/A')}")
            print(f"Score: {attribution.get('score', 'N/A')}")
            if "sources" in attribution:
                print("Sources:")
                for j, source in enumerate(attribution["sources"], 1):
                    print(f"  {j}. {source}")
    else:
        print("No attributions found")
