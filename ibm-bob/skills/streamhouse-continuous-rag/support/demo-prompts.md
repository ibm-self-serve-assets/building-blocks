# Demo prompts and talking points

## Primary demonstration

Ask before the machine is resolved:

> Why is CNC-03 showing high vibration and what should the technician inspect first?

Talking point: live operational state and continuously indexed maintenance knowledge are separate streams that become useful together at answer time.

Then click **Resolve + Learn**, which publishes the synthetic WO-11023 resolution as a new knowledge event.

Ask:

> What changed after WO-11023 was resolved?

Talking point: the new work-order resolution becomes retrievable without a nightly corpus rebuild.

## Additional prompts

- What does our current knowledge say about CNC-03 vibration?
- What should we inspect when vibration and dimensional drift rise together?
- Which previous maintenance event is most similar to the current CNC-03 condition?
- What evidence supports the recommended maintenance action?

## One-line Streamhouse explanation

> Streamhouse makes the changing state of the business continuously available; Continuous RAG applies the same idea to the knowledge AI retrieves.

## What not to claim

- Do not call the demo hash embedding a production semantic model.
- Do not claim Tableflow is the interactive RAG vector-search layer.
- Do not claim Kafka replaces the systems of record.
- Do not imply that a generated recommendation is an autonomous safety decision; keep a human/operator approval step in the manufacturing story.
