# rag_only

Two scenarios for a KB-bound agent — no transactional tools, just
knowledge-base lookup. Used to measure **Faithfulness**, **Answer
Relevancy**, and the related RAG metrics in isolation.

## Files

- `scenario_01_policy_lookup.json` — Asks a multi-condition policy question;
  text_checks include alternative phrasings of the expected concept.
- `scenario_02_compliance_question.json` — Asks for a structured list
  (data classifications) with required keywords for compliance terms.

## Adapt to your agent

1. Change `agent` to your KB-bound agent's name.
2. Replace `search_policy_knowledge_base` /
   `search_compliance_knowledge_base` with the names of your agent's
   actual KB lookup tools (see the agent's `knowledge_base:` section).
3. Replace the `keywords` list with terms that should appear in the
   correct answer for YOUR KB content (case-insensitive substring match).
4. No `args` / `arg_matching` for `conversational_search` goals — the
   framework does NOT validate the search query; it validates that a KB
   was consulted and that the answer contains the keywords.

RAG metric interpretation: see
[`../../reference/module-analyze.md`](../../reference/module-analyze.md).
