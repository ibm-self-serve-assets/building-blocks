"""
parallel_flow.py — Parallel and conditional-parallel execution patterns.

Demonstrates:
- aflow.parallel() for unconditional concurrent branches
- aflow.parallel_conditions() for conditional concurrent branches
- private_schema to share state across branches
- Multi-phase flow with sequential phases between parallel blocks

Flow:  START
         → init_state (script)
         → phase1_parallel (conditional: design + arch, or skip)
         → phase2_parallel (unconditional: squad1 + squad2 + squad3)
         → qa_work (script)
         → finalize (script)
         → END
"""

from typing import List
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END


# ── Schemas ───────────────────────────────────────────────────────────────────

class FlowInput(BaseModel):
    feature_name:  str  = Field(description="Feature to deliver")
    design_needed: bool = Field(default=True, description="Whether design work is needed")
    arch_needed:   bool = Field(default=True, description="Whether architecture work is needed")

class FlowOutput(BaseModel):
    status:           str       = Field(description="Final delivery status")
    phases_completed: List[str] = Field(description="Completed phase names")

class PrivateState(BaseModel):
    design_needed:    bool      = Field(default=False)
    arch_needed:      bool      = Field(default=False)
    phases_completed: List[str] = Field(default_factory=list)


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="feature_delivery_workflow",
    display_name="Feature Delivery Workflow",
    description="Multi-phase delivery using conditional and unconditional parallel execution.",
    input_schema=FlowInput,
    output_schema=FlowOutput,
    private_schema=PrivateState
)
def build_feature_delivery_flow(aflow: Flow) -> Flow:

    # ── Phase 0: Initialize private state ────────────────────────────────────
    init = aflow.script(
        name="init_state",
        display_name="Initialise State",
        script="""
flow.private.design_needed    = flow.input.design_needed
flow.private.arch_needed      = flow.input.arch_needed
flow.private.phases_completed = []
"""
    )

    # ── Phase 1: Conditional parallel (Design & Architecture) ────────────────
    phase1 = aflow.parallel_conditions(
        name="parallel_phase1",
        display_name="Phase 1 — Design & Architecture"
    )

    design_work = phase1.script(
        name="design_work",
        script="""
flow.private.phases_completed.append("Design")
"""
    )
    arch_work = phase1.script(
        name="architecture_work",
        script="""
flow.private.phases_completed.append("Architecture")
"""
    )
    phase1_skip = phase1.script(
        name="phase1_skip",
        script="pass  # Nothing required this phase"
    )

    phase1.condition(expression="flow.private.design_needed is True", to_node=design_work)
    phase1.condition(expression="flow.private.arch_needed is True",   to_node=arch_work)
    phase1.condition(default=True,                                     to_node=phase1_skip)

    phase1.sequence(design_work,  END)
    phase1.sequence(arch_work,    END)
    phase1.sequence(phase1_skip,  END)

    # ── Phase 2: Unconditional parallel (Development squads) ─────────────────
    phase2 = aflow.parallel(
        name="parallel_phase2",
        display_name="Phase 2 — Development"
    )

    squad1 = phase2.script(name="squad1_work", script="flow.private.phases_completed.append('Squad 1 Dev')")
    squad2 = phase2.script(name="squad2_work", script="flow.private.phases_completed.append('Squad 2 Dev')")
    squad3 = phase2.script(name="squad3_work", script="flow.private.phases_completed.append('Squad 3 Dev')")

    phase2.sequence(START, squad1, END)
    phase2.sequence(START, squad2, END)
    phase2.sequence(START, squad3, END)

    # ── Phase 3: Sequential QA ────────────────────────────────────────────────
    qa = aflow.script(
        name="qa_work",
        script="flow.private.phases_completed.append('QA')"
    )

    finalize = aflow.script(
        name="finalize",
        script="""
self.output.status           = "Feature delivery completed successfully"
self.output.phases_completed = flow.private.phases_completed
"""
    )

    # ── Wire phases together ──────────────────────────────────────────────────
    aflow.edge(START, init)
    aflow.edge(init,   phase1)
    aflow.edge(phase1, phase2)
    aflow.edge(phase2, qa)
    aflow.edge(qa,     finalize)
    aflow.edge(finalize, END)

    return aflow
