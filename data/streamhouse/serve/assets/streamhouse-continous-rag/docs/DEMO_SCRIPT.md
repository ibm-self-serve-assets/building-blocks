# 8–10 minute demo script

## 1. Set the story (45 seconds)

"We are not demonstrating Kafka as a message pipe. We are showing a Streamhouse where operational state and enterprise knowledge are continuously updated on the same event backbone."

Open **Overview** and click **Baseline**.

Call out:
- CNC-03 is healthy.
- projected production is above target.
- quality is normal.

## 2. Degradation begins (60 seconds)

Click **Degrade**.

Explain that machine vibration is rising and the current state now combines condition, production, and quality indicators.

## 3. Business exception (60 seconds)

Click **Critical**.

Call out:
- vibration 5.8 mm/s,
- cycle time increased,
- defect rate increased,
- projected output drops to 870/1000.

Message: "No single source system owns this combined answer. The Streamhouse continuously represents what the factory knows now."

## 4. Continuous RAG (2 minutes)

Click **Seed knowledge** if you have not already done so.

Open **Continuous RAG** and ask:

`Why is CNC-03 showing high vibration and what should the technician inspect first?`

Show the evidence cards. Explain that the answer is grounded in current work orders and SOP content rather than general model memory.

## 5. The continuous-learning moment (2 minutes)

Return to Overview and click **Resolve + Learn**.

This publishes synthetic WO-11023 closure knowledge saying tool-holder imbalance was found and corrected.

Wait a few seconds, return to Continuous RAG and ask:

`What changed after WO-11023 was resolved?`

Call out that the new work-order resolution can now be retrieved **without a nightly index rebuild**.

Key line:

> Traditional RAG answers from what the index knew when it was last refreshed. Continuous RAG can answer from what the enterprise knows now.

## 6. Explain the Streamhouse (90 seconds)

Open **Streamhouse**.

Explain:
- Kafka = durable shared event backbone.
- Flink = two jobs working in concert:
  - **Operational pipeline** (`infra/flink/factory_operations.sql`) — aggregates telemetry into windows, detects threshold breaches and emits `factory.exceptions`, then joins telemetry + quality + production to derive `factory.state`. This is the "join · detect" role in the architecture diagram.
  - **Continuous RAG pipeline** (`infra/flink/continuous_rag.sql`) — chunks new knowledge with `ML_RECURSIVE_TEXT_SPLITTER` and embeds it with `AI_EMBEDDING` so retrieval stays fresh without a batch rebuild.
  - *In a demo without a Flink compute pool, the Python demo step buttons (`Baseline / Degrade / Critical / Resolve`) act as a shortcut and produce `factory.state` and `factory.exceptions` directly. The Flink SQL produces the same events in a full STANDARD cluster deployment.*
- Schema Registry = data contracts enforced at every topic boundary; automatically activated when SR credentials are present.
- Tableflow = the analytical/historical path into Iceberg/Delta.
- RAG = one operational consumer of that continuously changing enterprise state.

## 7. Close (30 seconds)

"The value is not just lower latency. It is reducing the gap between a business change, the enterprise's shared understanding of that change, and the action an operator or AI assistant can take."
