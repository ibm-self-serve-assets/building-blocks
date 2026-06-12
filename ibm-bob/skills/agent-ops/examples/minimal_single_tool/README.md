# minimal_single_tool

The simplest valid benchmark: one scenario, one tool call, no
dependencies. Use as the few-shot prime when generating new benchmarks
via `orchestrate evaluations generate`, or as a skeleton when authoring
manually.

## Files

- `scenario_01_lookup_user.json` — Single `get_user_by_id` call with strict
  arg matching on `user_id`. The story includes explicit completion criteria
  ("Do NOT end the conversation until...") so the LLM-simulated user does
  not exit early.

## Adapt to your agent

1. Change `agent` to match your `agent_config.yaml`'s `name`.
2. Change `tool_name` (and the matching goal key) to one of your real tools.
3. Change the `args` keys/values to match the tool's actual signature.
4. Adjust `arg_matching` per the strategies in
   [`../../reference/module-benchmarks.md`](../../reference/module-benchmarks.md).
