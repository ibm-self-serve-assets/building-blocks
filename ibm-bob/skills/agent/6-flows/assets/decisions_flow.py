"""
decisions_flow.py — Decision table for insurance rate assessment.

Demonstrates:
- aflow.decisions() with programmatically built rules
- DecisionsRule, DecisionsCondition (equal, less_than, in_range, greater_than_or_equal)
- DecisionsRule.action() for setting output variables
- default_actions fallback when no rule matches
- DecisionTableColumn for UI display names

Rules (evaluated top-to-bottom, first match wins):
  Grade A + loan < 100k        → no insurance required
  Grade A + 100k ≤ loan < 300k → insurance required @ 0.1%
  Grade A + 300k ≤ loan < 600k → insurance required @ 0.3%
  Grade A + loan ≥ 600k        → insurance required @ 0.5%
  Grade B + loan < 100k        → no insurance required
  Grade B + 100k ≤ loan < 300k → insurance required @ 0.25%
  Grade B + 300k ≤ loan < 600k → insurance required @ 0.5%
  Grade B + loan ≥ 600k        → insurance required @ 0.75%
  (no match)                   → assessment_error = "Incorrect data"
"""

from typing import Literal
from pydantic import BaseModel
from ibm_watsonx_orchestrate.flow_builder.flows import (
    END, Flow, flow, START,
    DecisionsNode, DecisionsRule, DecisionsCondition
)
from ibm_watsonx_orchestrate.flow_builder.types import DecisionTableColumn


# ── Schemas ───────────────────────────────────────────────────────────────────

class AssessmentData(BaseModel):
    loan_amount: float
    grade:       Literal["A", "B"]

class Assessment(BaseModel):
    insurance_required: bool        = False
    insurance_rate:     float       = 0.0
    assessment_error:   str | None  = None


# ── Decision table builder ────────────────────────────────────────────────────

def build_insurance_decisions(aflow: Flow) -> DecisionsNode:
    """Build insurance rate decision table programmatically."""

    def make_rules():
        configs = [
            # (grade, condition_fn,             insurance, rate)
            ("A", lambda c: c.less_than(100000),                    False, 0.0),
            ("A", lambda c: c.in_range(100000, 300000, True, False), True, 0.001),
            ("A", lambda c: c.in_range(300000, 600000, True, False), True, 0.003),
            ("A", lambda c: c.greater_than_or_equal(600000),         True, 0.005),
            ("B", lambda c: c.less_than(100000),                    False, 0.0),
            ("B", lambda c: c.in_range(100000, 300000, True, False), True, 0.0025),
            ("B", lambda c: c.in_range(300000, 600000, True, False), True, 0.005),
            ("B", lambda c: c.greater_than_or_equal(600000),         True, 0.0075),
        ]
        rules = []
        for grade, amount_fn, req, rate in configs:
            r = DecisionsRule()
            r.condition("flow.input.grade",       DecisionsCondition().equal(grade))
            r.condition("flow.input.loan_amount",  amount_fn(DecisionsCondition()))
            r.action("flow.output.insurance_required", req)
            if req:
                r.action("flow.output.insurance_rate", rate)
            rules.append(r)
        return rules

    return aflow.decisions(
        name="assess_insurance_rate",
        display_name="Assess Insurance Rate",
        description="Determine insurance requirement and rate based on credit grade and loan amount.",
        rules=make_rules(),
        default_actions={
            "flow.output.assessment_error": "Not assessed. Incorrect data submitted."
        },
        decision_table_columns=[
            DecisionTableColumn(variable="flow.input.grade",                   display_name="Credit Grade"),
            DecisionTableColumn(variable="flow.input.loan_amount",             display_name="Loan Amount"),
            DecisionTableColumn(variable="flow.output.insurance_required",     display_name="Insurance Required"),
            DecisionTableColumn(variable="flow.output.insurance_rate",         display_name="Insurance Rate"),
            DecisionTableColumn(variable="flow.output.assessment_error",       display_name="Assessment Error"),
        ]
    )


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="get_insurance_rate",
    display_name="Insurance Rate Assessment",
    description="Calculate insurance rate based on credit grade and loan amount using a decision table.",
    input_schema=AssessmentData,
    output_schema=Assessment
)
def build_get_insurance_rate(aflow: Flow = None) -> Flow:
    decisions_node = build_insurance_decisions(aflow)
    aflow.sequence(START, decisions_node, END)
    return aflow
