"""Tutorial 04: End-to-End Guardrail Pipeline with real-time-guardrails

Brings everything together: the 4 choke points (input → retrieval → generation
→ output) wired into a single GuardrailedAgent class with built-in audit
logging. Replace simulate_retrieve() and simulate_model() with your real
vector store and LLM client to ship to production.

  ┌──────────────────────────────────────────────────────────────────────────┐
  │ user query                                                               │
  │   → INPUT guardrail (safety)                          Block? → refuse    │
  │   → retrieve docs                                                         │
  │   → RETRIEVAL guardrail (HitRate, Precision, RR)      Block? → "no info" │
  │   → call LLM                                                              │
  │   → GENERATION guardrail (Faithfulness, AnswerRel)    Block? → regenerate│
  │   → OUTPUT guardrail (output PII, HAP)                Block? → scrub     │
  │   → return final response                                                 │
  │   Every decision recorded to JSONL audit log.                             │
  └──────────────────────────────────────────────────────────────────────────┘

The GuardrailedAgent class lives in `sdk/examples/full_pipeline.py` — this
tutorial imports it directly so you can see the end-to-end shape, then
swap in your real retriever + LLM.

Prerequisites
-------------
1. `pip install -e ./sdk[all]`
2. `cp ./sdk/.env.example ./.env` and fill in credentials
3. Run: `python 04_guardrail_pipeline.py`
4. Inspect /tmp/guardrail_pipeline_audit.jsonl after for the audit trail.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from dotenv import load_dotenv

from real_time_guardrails import AuditLogger, GuardrailsEvaluator


load_dotenv()

# Import the GuardrailedAgent class from the SDK examples folder.
# In production, copy that file into your codebase and adapt the
# retrieve/model callbacks to your real implementations.
sys.path.insert(0, str(Path(__file__).parent / "sdk" / "examples"))
from full_pipeline import GuardrailedAgent  # noqa: E402


# ── Replace these two with your real retriever + LLM ───────────────────

def my_retriever(query: str) -> list[str]:
    """Stand-in vector store. Returns docs based on keyword match."""
    docs_db = {
        "password": [
            "To reset your password, go to Settings > Security > Reset Password.",
            "Password complexity: 12+ chars, mixed case, symbol required.",
            "Account lockout after 5 failed login attempts.",
        ],
        "return": [
            "Return policy: electronics within 30 days with original receipt.",
            "15% restocking fee on opened items.",
            "Refunds processed within 5–7 business days to original payment method.",
        ],
    }
    for key, docs in docs_db.items():
        if key in query.lower():
            return docs
    return ["No matching docs found."]


def my_llm(query: str, context: str) -> str:
    """Stand-in LLM. Replace with your real watsonx.ai / OpenAI / etc. call."""
    if "password" in query.lower():
        return (
            "To reset your password, go to Settings > Security > Reset Password, "
            "enter your current password, then choose a new one meeting the "
            "complexity rules (12+ chars, mixed case, symbol)."
        )
    if "return" in query.lower():
        return f"Based on the policy: {context[:120]}..."
    return "I don't have specific information about that."


# ── Build the pipeline ─────────────────────────────────────────────────

ev = GuardrailsEvaluator()
audit = AuditLogger(path="/tmp/guardrail_pipeline_audit.jsonl")
agent = GuardrailedAgent(
    ev,
    audit=audit,
    retrieve_callback=my_retriever,
    model_callback=my_llm,
)


# ── Demo: three scenarios exercising different choke points ────────────

SCENARIOS = [
    ("safe-query",     "How do I reset my password?"),
    ("pii-in-input",   "My SSN is 123-45-6789 — please update my password"),
    ("off-topic-rag",  "What's the weather in Tokyo?"),
]


def main() -> None:
    print("=" * 70)
    print(f"GUARDRAIL PIPELINE — {ev.list_metrics()['total']} metrics available")
    print(f"Audit log: {audit._path if hasattr(audit, '_path') else 'JSONL'}")
    print("=" * 70)
    for request_id, query in SCENARIOS:
        print(f"\n─ {request_id}: {query!r}")
        result = agent.process_request(query, request_id=request_id)
        print(f"  overall action: {result.overall_action}")
        print(f"  final response: {result.final_response[:120]}")

    # Show the last audit line so the partner sees the JSONL shape
    print("\n" + "─" * 70)
    print("Last audit-log line (JSONL):")
    audit.close()
    last = Path("/tmp/guardrail_pipeline_audit.jsonl").read_text().strip().splitlines()[-1]
    print(json.dumps(json.loads(last), indent=2)[:600] + "...")


if __name__ == "__main__":
    sys.exit(main())
