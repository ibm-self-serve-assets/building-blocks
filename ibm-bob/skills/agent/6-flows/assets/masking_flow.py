"""
masking_flow.py — Sensitive data masking across all node types.

Demonstrates:
- aflow.mask_property() with MaskingPolicy and InputPolicy
- Masking flow.input fields
- Masking flow.private (nested objects)
- Masking script node outputs
- Masking tool node outputs
- Masking userflow form fields (with real-time MASK_WHILE_TYPING)
- private_schema for sensitive intermediate state

MaskingPolicy values:
  MASK_ALL     — replace entire value
  MASK_FIRST4  — mask first 4 characters
  MASK_LAST4   — mask last 4 characters

InputPolicy values:
  MASK_WHILE_TYPING — mask in real-time as user types
"""

from typing import List
from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.masking_utils import InputPolicy, MaskingPolicy
from ibm_watsonx_orchestrate.flow_builder.types import UserFieldKind, ForeachPolicy
from ibm_watsonx_orchestrate.flow_builder.data_map import DataMap, Assignment


# ── Schemas ───────────────────────────────────────────────────────────────────

class UserInput(BaseModel):
    username: str = Field(description="User's username")
    ssn:      str = Field(description="Social Security Number (SENSITIVE)")

class Credentials(BaseModel):
    auth_token: str = Field(description="Authentication token (SENSITIVE)")

class PrivateData(BaseModel):
    user_id:     str         = Field(default="")
    credentials: Credentials = Field(default_factory=Credentials)

class ProcessedUser(BaseModel):
    user_id:          str       = Field(description="Generated user ID")
    username:         str       = Field(description="Username")
    masked_ssn:       str       = Field(description="Masked SSN")
    processing_notes: List[str] = Field(description="Processing notes")


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="masking_demo_flow",
    display_name="Masking Demo Flow",
    description="Demonstrates masking of sensitive data across all node types.",
    input_schema=UserInput,
    output_schema=ProcessedUser,
    private_schema=PrivateData
)
def build_masking_demo_flow(aflow: Flow) -> Flow:

    # ── Script: initialise private state ─────────────────────────────────────
    class ScriptOutput(BaseModel):
        masked_ssn: str = Field(description="Masked SSN for display")

    init_script = aflow.script(
        name="process_data",
        display_name="Process User Data",
        output_schema=ScriptOutput,
        script="""
flow.private.user_id                  = f"USR-{hash(flow.input.username) % 10000}"
flow.private.credentials.auth_token   = "tok_" + flow.input.username[:4]
self.output.masked_ssn                = flow.input.ssn
"""
    )

    # ── User flow: display masked fields ─────────────────────────────────────
    user_flow = aflow.userflow()

    ssn_display = user_flow.field(
        direction="output",
        name="display_ssn",
        display_name="SSN (masked)",
        kind=UserFieldKind.Text,
        text="SSN: {flow.input.ssn}"
    )
    token_display = user_flow.field(
        direction="output",
        name="display_token",
        display_name="Auth Token (masked)",
        kind=UserFieldKind.Text,
        text="Token: {flow.private.credentials.auth_token}"
    )
    user_flow.edge(START, ssn_display)
    user_flow.edge(ssn_display, token_display)
    user_flow.edge(token_display, END)

    # ── Final script: prepare output ─────────────────────────────────────────
    output_script = aflow.script(
        name="prepare_output",
        display_name="Prepare Output",
        script="""
self.output.user_id          = flow.private.user_id
self.output.username         = flow.input.username
self.output.masked_ssn       = flow.process_data.output.masked_ssn
self.output.processing_notes = ["Processed successfully", "Sensitive fields masked"]
"""
    )

    # ── Wire flow ─────────────────────────────────────────────────────────────
    aflow.edge(START,       init_script)
    aflow.edge(init_script, user_flow)
    aflow.edge(user_flow,   output_script)
    aflow.edge(output_script, END)

    # ── Masking configuration ─────────────────────────────────────────────────

    # 1. Mask flow input field — SSN fully hidden
    aflow.mask_property(
        "flow.input.ssn",
        masking_policy=MaskingPolicy.MASK_ALL
    )

    # 2. Mask nested private variable — show last chars only
    aflow.mask_property(
        "flow.private.credentials.auth_token",
        masking_policy=MaskingPolicy.MASK_FIRST4
    )

    # 3. Mask script node output
    aflow.mask_property(
        f"flow.{init_script.spec.name}.output.masked_ssn",
        masking_policy=MaskingPolicy.MASK_FIRST4
    )

    # 4. Mask userflow display field (output — shown in chat)
    aflow.mask_property(
        "flow.userflow_1.display_ssn.output",
        masking_policy=MaskingPolicy.MASK_ALL
    )

    # 5. Mask a form input field with real-time masking while the user types
    # (example — if a form field for password was present)
    # aflow.mask_property(
    #     "flow.userflow_2.ApplicationForm.output.password",
    #     masking_policy=MaskingPolicy.MASK_ALL,
    #     input_policy=InputPolicy.MASK_WHILE_TYPING
    # )

    return aflow
