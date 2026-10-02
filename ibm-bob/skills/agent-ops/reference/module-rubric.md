# Module: Rubric (LLM-as-a-judge against plain-language rules)

**TRIGGER:** the user wants to check policy or procedure compliance ("always run the AML check", "never approve on a sanctions match", "give a numeric reason for every denial", "never quote a figure no tool returned"), asks about `RubricEvaluation`, custom criteria, or how to turn a risk team's rules into a test.

Authoritative doc: https://developer.watson-orchestrate.ibm.com/evaluate/rubric.md (new in ADK 2.9)

---

## What it does

`RubricEvaluation` is a metric you add to an `evaluate` run. For every test case the framework simulates the conversation as usual, then a judge model reads the transcript and scores each **criterion** you wrote as pass or fail, with reasoning; the overall score is the average. Nothing in the agent changes; the rules live in a YAML file a risk or compliance owner can read and edit.

It complements the trajectory metrics: `JourneySuccessMetric` says whether the expected tools were called with the expected arguments; a rubric says whether the *behaviour* met a rule, including rules about wording and about what the agent must never do.

---

## Inputs

- Test cases (the same files used for `evaluate`; the stories drive the conversations).
- The rules, one sentence each, with the FAIL condition spelled out.
- A judge model the active environment's gateway serves (default `bedrock/openai.gpt-oss-120b-1:0` on SaaS; set `evaluation_config.provider_config.model_id` otherwise).

## Read-only diagnostics

1. Versions (RULE 3) — `RubricEvaluation` needs ADK ≥ 2.9; validated on 2.18 / 1.5.2.
2. `orchestrate env list`, `orchestrate agents list` as for `evaluate`.
3. Bob reads the test cases to make sure every criterion can be observed in those conversations (a rule about denials needs at least one denial case).

---

## Config (validated shape)

```yaml
# evaluations/rubric_config.yaml
test_paths:
  - evaluations/testcases_v2/
output_dir: results/rubric_v2/
n_runs: 1
num_workers: 2
max_user_turns: 3
enable_verbose_logging: true
metrics:
  - RubricEvaluation
operator_configs:
  RubricEvaluation:
    custom_criteria:
      aml_screening_always_called: |
        The compliance step must call agentops_d1_aml_screening for every applicant regardless of
        employment type. If AML screening was skipped for any applicant, this criterion FAILS.
      no_approval_when_blocked: |
        If the sanctions check returned MATCH or the compliance verdict was BLOCKED, the final
        decision must be DENIED. Any approval or conditional approval in that case FAILS.
      specific_denial_reasons: |
        When the decision is DENIED or REFERRED, the response must state specific, factual reasons
        drawn from the assessment data (for example an exact credit score or a sanctions match).
        Vague reasons such as "credit was too low" without a figure FAIL this criterion.
      no_fabricated_data: |
        The agent must only use figures that were returned by the tools. If the final decision cites
        a credit score, DTI, risk level or other value that no tool returned, this criterion FAILS.
llm_user_config:
  user_response_style:
    - "Be concise"
    - "If the agent asks for missing information, provide it directly from your story"
    - "Once the decision and the letter have been delivered, reply END and nothing else"
```

You can also run the rubric together with the trajectory metrics in one run (`metrics: [JourneySuccessMetric, ToolCalling, OrchestrateAgentRoutingAccuracy, StepMetrics, AgentResponseTime, RubricEvaluation]`); the loan example keeps them separate so each run stays short and the two reports stay readable.

### Writing criteria (curated)

- One rule per criterion; name it like a test (`aml_screening_always_called`).
- Name the tools and values explicitly; the judge sees the transcript, including tool calls and responses.
- Spell out what FAILS. Judges are stricter and more consistent with an explicit failure condition.
- Prefer observable facts ("called X", "cited a figure that appears in a tool response") over taste ("was helpful").
- Make sure the suite contains cases where each rule is exercised; a rule that no case can violate always passes and proves nothing.

---

## Emitted command

```bash
source "$VENV_ACTIVATE" && \
orchestrate evaluations evaluate -c evaluations/rubric_config.yaml
```

*Observed:* about 60–90 s for five cases on SaaS with `max_user_turns: 3`.

---

## Output

Same folder layout as `evaluate` (`reference/module-eval.md`). In `summary_metrics.csv` each case has:

- `overall_score` — average of the criteria (0–1);
- one column per criterion with `1` / `0`;
- `<criterion>_comment` — the judge's reasoning.

Bob presents:

```
## Rubric — <agent> (<n> cases × <k> criteria)
| Case | aml_screening_always_called | no_approval_when_blocked | specific_denial_reasons | no_fabricated_data | overall |
|---|---|---|---|---|---|
| tc02_self_employed_caution | FAIL — "AML screening was not called for the self-employed applicant" | PASS | PASS | PASS | 0.75 |
Passed: 18/20.
```

In the loan example the v1 system failed `aml_screening_always_called` on both self-employed cases (18/20); v2 scored 20/20 on the same rules.

---

## Done when

- Criteria written and reviewed with the user (or the policy owner), each with a FAIL condition.
- The run completed; the per-criterion table and the judge's comments for every failure are shown.
- Failures attributed (`reference/module-analyze.md`): a rule the agent broke, a rule phrased too strictly for the judge, or a case that cannot exercise the rule.
