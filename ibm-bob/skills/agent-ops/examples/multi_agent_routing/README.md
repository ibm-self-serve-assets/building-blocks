# multi_agent_routing

Two scenarios that exercise a facilitator + 2 collaborators setup. Each
scenario sends the user to a different collaborator based on intent
(billing vs technical support). Used to measure **Agent Routing F1**.

## Files

- `scenario_01_route_to_billing.json` — Customer mentions "billing" →
  facilitator should route to the billing collaborator → billing agent
  retrieves history.
- `scenario_02_route_to_tech_support.json` — Customer reports a technical
  problem → facilitator should route to the tech support collaborator →
  tech support opens a ticket.

## Adapt to your agent

1. Change `agent` to the name of your facilitator agent.
2. Replace `transfer_to_billing_agent` / `transfer_to_tech_support_agent`
   with your facilitator's actual transfer/handoff tool names.
3. Replace downstream tool names (`get_billing_history`,
   `create_support_ticket`) with the collaborators' real tools.
4. Adjust the stories' intent signals so they unambiguously imply the
   right collaborator — that's what the facilitator's `whenToUse`
   matches against.

If routing F1 fails, see the `Routing F1 below threshold` row in
[`../../reference/module-analyze.md`](../../reference/module-analyze.md).
