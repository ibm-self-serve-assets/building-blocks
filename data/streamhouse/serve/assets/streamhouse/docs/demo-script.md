# Live demo — "The machine that warned us first"

**Audience:** manufacturing CIO / COO, plant reliability leads, real-time data architects, data & AI owners.

**Business outcome:** avoid unplanned production stoppages through current, governed, shareable manufacturing context without replacing existing systems.

**Persona:** Maya Chen, fictional VP of Operations responsible for six US factory locations.

### Act 1 — Find the signal (minutes 0–4)

**Say:** “Maya does not lack dashboards. She lacks *a current operational picture* across plants. SCADA, MES and ERP tell different parts of the story, and batch data arrives too late for agents to act.”

- Open **Command center**. Show six plants, OEE, per-factory health and events per second.
- Select Detroit and open **Digital twin**. Explain that the animated six-station robotic floor is visually simulated, not connected to real physical robots.
- Select **Bearing wear** at 85–90% and click **Inject scenario**. Sensor vibration rises, the selected robot turns red, output/OEE decreases and a fault event appears after a few telemetry ticks.

### Act 2 — Trace the event through Streamhouse (minutes 4–9)

**Say:** “A robot event is not another silo. It’s a governed asset signal entering the production data backbone.”

- Open **Streamhouse** and move left-to-right: **Capture** (IoT), **Stream** (Kafka), **Transform** (Flink), **Govern** (schema/lineage), **Serve** (RTCE & Tableflow).
- If cloud mode is on, show `stream.sent` in `/api/health` or Kafka Messages to verify producer acknowledgements.
- Open **Flink SQL**: first inspect source schemas, then show condition-based `factory-risk-signals` SQL and tumbling 1-minute factory metrics. Only claim these are executing when you deployed them and observe real derived output.
- Open **Actions** and distinguish Confluent's built-in Topic Actions (deduplication, masking, transform) from an enterprise maintenance workflow.

### Act 3 — Context and response (minutes 9–13)

**Say:** “GenAI doesn’t fix stale information. Real-time context gives the AI the equipment state, sensor trend and priority *now*.”

- Open **AI context / MCP**. Ask “Which robot needs maintenance right now?” The built-in answer is intentionally labeled local demo rules.
- If RTCE is enabled, press **Discover remote MCP tools**, select an appropriate table discovery/query tool, and invoke it. Discuss how watsonx Orchestrate/agents can use the same MCP interface with proper authentication.
- Explain the second serving lane: Tableflow materializes schema-bearing Kafka streams to Apache Iceberg, queryable by a compatible lakehouse engine including IBM watsonx.data when integrated.

### Act 4 — Close and prove the change (minutes 13–15)

- Return to **Actions** → **Schedule maintenance** to simulate resolving the fault and resetting the selected factory. Optionally connect an HTTPS action webhook to a ticketing process; disclose whether it is really configured.
- Close with: “No rip and replace: existing operational investments stay where they are. Streamhouse adds production-grade streaming, governed transformations, live context for agents and open Iceberg history.”

## Challenge questions

**Is the 3D twin real?** No. Its visual geometry, robot movement and sensor values are simulations synchronized by a Python Flask backend. The Kafka transport can be live to a real cloud cluster.

**Is there a real Confluent cluster?** Only when `STREAM_MODE=kafka`, `stream.status=connected`, and acknowledged writes are increasing. The package ships with placeholders, not credentials.

**Does your chatbot call an LLM?** The default panel is explicitly rule-based. The separate RTCE MCP explorer uses the real MCP API after configuring credentials. Bring your own agent/model for LLM reasoning.

**Does maintenance work on Maximo?** By default no, it's a simulated command. An opt-in HTTPS webhook is provided as the integration point; implementing an IBM Maximo service request/work order requires mapping, auth, validation and approval.

**Can Tableflow publish into watsonx.data?** Tableflow publishes Iceberg. The external catalog/storage route and watsonx.data Iceberg catalog integration must be configured in the actual customer environment; it is not an automatic connection in this repo.

**Are Flink Actions the same as operational Actions?** No. Flink Topic Actions are ready-made Flink transformations; business workflow dispatch is a distinct downstream action.
