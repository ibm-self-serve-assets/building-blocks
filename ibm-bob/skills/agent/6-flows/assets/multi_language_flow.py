"""
multi_language_flow.py — Multi-language support for user activity nodes.

Demonstrates:
- aflow.target_locales() to specify supported languages
- aflow.source_locale() to set the source language
- aflow.translation_enabled() to enable/disable translation
- form() with translatable labels, placeholders, and instructions
- CLI workflow: import → export translations CSV → add translations → re-import

What gets translated:
  ✅ Field labels, display names, help text, placeholder text
  ✅ Form instructions, button labels, choice option labels, error messages

What does NOT get translated:
  ❌ User input, dynamic variable content, tool outputs
  ❌ Flow expressions, variable names, tool/flow names

Translation CLI workflow:
  1. orchestrate tools import -k flow -f multi_language_flow.py
  2. orchestrate tools export -k flow customer_feedback_form --translation translations.csv
  3. Add translations to translations.csv
  4. orchestrate tools import -k flow -f multi_language_flow.py --translation translations.csv

Supported locales: en, fr, es, de, it, ja, ko, zh-CN, zh-TW, pt-BR
"""

from pydantic import BaseModel, Field
from ibm_watsonx_orchestrate.flow_builder.flows import Flow, flow, START, END
from ibm_watsonx_orchestrate.flow_builder.types import UserFieldKind


# ── Schema ────────────────────────────────────────────────────────────────────

class FeedbackOutput(BaseModel):
    customer_name: str = Field(description="Submitted customer name")
    feedback:      str = Field(description="Submitted feedback text")
    rating:        str = Field(description="Submitted rating value")


# ── Flow ──────────────────────────────────────────────────────────────────────

@flow(
    name="customer_feedback_form",
    display_name="Customer Feedback",
    description="Collect customer feedback in multiple languages.",
    output_schema=FeedbackOutput
)
def build_feedback_flow(aflow: Flow = None) -> Flow:

    user_flow = aflow.userflow()

    form = user_flow.form(
        name="feedback_form",
        display_name="Customer Feedback",                   # ← translated
        instructions="Please share your experience.",       # ← translated
        submit_button_label="Submit Feedback",             # ← translated
        cancel_button_label="Cancel"                       # ← translated
    )

    # All labels, help text, and placeholders are translatable
    form.text_input_field(
        name="customer_name",
        label="Your Name",                                  # ← translated
        required=True,
        placeholder_text="Enter your full name",            # ← translated
        help_text="We need your name to follow up."         # ← translated
    )

    form.text_input_field(
        name="feedback",
        label="Your Feedback",                              # ← translated
        required=True,
        single_line=False,
        placeholder_text="Tell us about your experience",   # ← translated
    )

    form.single_choice_input_field(
        name="rating",
        label="Overall Rating",                             # ← translated
        required=True,
        # Choice option labels are also translatable
        choices=None   # would normally use a DataMap with choices
    )

    user_flow.edge(START, form)
    user_flow.edge(form, END)

    # ── Configure multi-language support ──────────────────────────────────────
    aflow.source_locale("en")                               # source is English
    aflow.target_locales(["fr", "es", "de", "ja", "ko"])   # translate to 5 languages
    aflow.translation_enabled(True)                        # enabled by default

    aflow.sequence(START, user_flow, END)
    return aflow
