"""Factory functions for LLM-as-judge metrics.

These wrap ``ibm_watsonx_gov`` ``LLMAsJudgeMetric`` with prompts copied from the
ai-trust demo. They depend on a ``LLMJudge`` instance which is built once by
the evaluator from :class:`GuardrailsConfig`.

Ported from the ai-trust demo at ``app.py:75-202``. We deliberately skip
``narrative_quality`` (requires ``table_data``) and ``helpfulness`` (subjective,
use-case specific).
"""

from __future__ import annotations

from typing import Any


def build_answer_completeness(judge: Any) -> Any:
    """Returns an LLMAsJudgeMetric that scores how completely the response addresses the input."""
    from ibm_watsonx_gov.entities.criteria import Option  # type: ignore
    from ibm_watsonx_gov.metrics import LLMAsJudgeMetric  # type: ignore

    prompt = (
        "You are an evaluator. Given a user input and a generated response, decide whether the "
        "response completely addresses the user's question.\n\n"
        "Input: {input_text}\n"
        "Response: {generated_text}\n\n"
        "Return one of: complete, partial, incomplete."
    )
    return LLMAsJudgeMetric(
        name="answer_completeness",
        llm_judge=judge,
        prompt_template=prompt,
        input_fields=["input_text", "generated_text"],
        options=[
            Option(name="complete", value=1.0),
            Option(name="partial", value=0.5),
            Option(name="incomplete", value=0.0),
        ],
    )


def build_conciseness(judge: Any) -> Any:
    """Returns an LLMAsJudgeMetric that scores whether the response is concise."""
    from ibm_watsonx_gov.entities.criteria import Option  # type: ignore
    from ibm_watsonx_gov.metrics import LLMAsJudgeMetric  # type: ignore

    prompt = (
        "You are an evaluator. Given a generated response, decide whether the response is "
        "concise and to the point.\n\n"
        "Response: {generated_text}\n\n"
        "Return Yes if concise, No otherwise."
    )
    return LLMAsJudgeMetric(
        name="conciseness",
        llm_judge=judge,
        prompt_template=prompt,
        input_fields=["generated_text"],
        options=[
            Option(name="Yes", value=1.0),
            Option(name="No", value=0.0),
        ],
    )


def build_criteria_judge(
    *,
    name: str,
    display_name: str,
    criteria_description: str,
    options: list[Any],
    judge: Any,
    output_field: str = "generated_text",
) -> Any:
    """Build a custom LLM-as-judge metric using the **criteria + Option** style.

    Use this when your judge is a short rubric (Yes/No, High/Medium/Low) rather
    than a free-form prompt. The SDK constructs the actual prompt internally
    from the criteria description + option names + descriptions.

    Example::

        from ibm_watsonx_gov.entities.criteria import Option
        from real_time_guardrails.core.custom_metrics import build_criteria_judge

        my_helpfulness = build_criteria_judge(
            name="helpfulness",
            display_name="Helpfulness",
            criteria_description="How helpful is the {generated_text}?",
            options=[
                Option(name="High", description="Accurate, actionable, addresses needs.", value=1.0),
                Option(name="Medium", description="Partial — lacks depth.", value=0.5),
                Option(name="Low", description="Vague or unhelpful.", value=0.0),
            ],
            judge=my_llm_judge,
        )

    Compare with :func:`build_answer_completeness` / :func:`build_conciseness`,
    which use the **prompt_template** style for full prompt control.

    Parameters
    ----------
    name : str
        Machine-readable metric name (e.g. ``"helpfulness"``). Appears in the
        SDK result DataFrame as the column name.
    display_name : str
        Human-readable metric name (e.g. ``"Helpfulness"``). Surfaced in
        ``list_metrics()`` and audit logs.
    criteria_description : str
        Short statement of what the LLM is judging. Reference output via the
        ``{generated_text}`` placeholder (or whichever ``output_field`` you pass).
    options : list[Option]
        ``ibm_watsonx_gov.entities.criteria.Option`` instances — each has
        ``name``, ``description``, and ``value`` (the numeric score returned
        when this option is chosen).
    judge : LLMJudge
        Pre-built ``ibm_watsonx_gov.entities.llm_judge.LLMJudge`` instance.
        Typically constructed once at evaluator init from
        :class:`GuardrailsConfig`.
    output_field : str
        Which input field the judge inspects (default ``"generated_text"``).
    """
    from ibm_watsonx_gov.metrics import LLMAsJudgeMetric  # type: ignore

    return LLMAsJudgeMetric(
        name=name,
        display_name=display_name,
        criteria_description=criteria_description,
        options=options,
        output_field=output_field,
        llm_judge=judge,
    )
