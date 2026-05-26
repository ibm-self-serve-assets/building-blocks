"""
Metrics processing and display utilities.

This module provides helpers for processing and visualizing evaluation metrics.
"""

import pandas as pd
from typing import Optional, List, Dict, Any
from IPython.display import display


def format_metrics_dataframe(
    eval_result,
    include_fields: Optional[List[str]] = None
) -> pd.DataFrame:
    """Format evaluation results as a pandas DataFrame.

    Args:
        eval_result: Evaluation result object from evaluator.get_result().
        include_fields: Additional fields to include (e.g., input_text, generated_text).

    Returns:
        Formatted DataFrame with metrics.

    Example:
        ```python
        eval_result = evaluator.get_result()
        df = format_metrics_dataframe(
            eval_result,
            include_fields=["input_text", "generated_text"]
        )
        ```
    """
    df = eval_result.to_df()

    if include_fields:
        # This would need to be combined with input data
        # Implementation depends on how eval_result stores this
        pass

    return df


def display_metrics(
    eval_result,
    node_name: Optional[str] = None,
    include_fields: Optional[List[str]] = None
) -> None:
    """Display evaluation metrics in Jupyter notebook.

    Args:
        eval_result: Evaluation result object from evaluator.get_result().
        node_name: Optional node name to filter metrics.
        include_fields: Additional fields to include in display.

    Example:
        ```python
        eval_result = evaluator.get_result()
        display_metrics(eval_result, node_name="Generation Node")
        ```
    """
    if node_name:
        metrics = eval_result.get_aggregated_metrics_results(node_name=node_name)
        print(f"\n=== Metrics for {node_name} ===")
        display(metrics)
    else:
        df = format_metrics_dataframe(eval_result, include_fields)
        display(df)


def get_metric_summary(eval_result) -> Dict[str, Any]:
    """Get a summary of all metrics.

    Args:
        eval_result: Evaluation result object.

    Returns:
        Dictionary with metric summaries.

    Example:
        ```python
        summary = get_metric_summary(eval_result)
        print(f"Average faithfulness: {summary['faithfulness']['mean']}")
        ```
    """
    df = eval_result.to_df()

    summary = {}
    for col in df.select_dtypes(include=['number']).columns:
        summary[col] = {
            'mean': df[col].mean(),
            'min': df[col].min(),
            'max': df[col].max(),
            'std': df[col].std()
        }

    return summary


def compare_experiments(
    eval_results: List,
    experiment_names: List[str]
) -> pd.DataFrame:
    """Compare metrics across multiple experiments.

    Args:
        eval_results: List of evaluation result objects.
        experiment_names: Names for each experiment.

    Returns:
        DataFrame comparing metrics across experiments.

    Example:
        ```python
        comparison = compare_experiments(
            [result1, result2, result3],
            ["Baseline", "Improved", "Final"]
        )
        ```
    """
    dfs = []
    for name, result in zip(experiment_names, eval_results):
        df = result.to_df()
        df['experiment'] = name
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined.pivot_table(
        index='experiment',
        values=[col for col in combined.columns if col not in ['experiment', 'interaction_id']],
        aggfunc='mean'
    )
