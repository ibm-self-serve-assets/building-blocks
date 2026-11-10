# Pipeline digital twin specification

> Extracted verbatim from `SPEC.md` (section 3.4). Do not edit here; edit SPEC.md and re-extract. Paths are relative to the project root.

### 3.4 Pipeline digital twin

Source: `frontend/src/components/PipelineTwin.tsx`; tests: `frontend/src/components/PipelineTwin.test.tsx` (5 tests); styles: `.twin*` at the end of `frontend/src/styles/index.scss`; mounted by `WorkspacePage` inside `Card title="Pipeline digital twin"`.

**Status:** Implemented. A pure view of data the page already has; it makes no API call and never invents progress or a percentage.

**Props (`PipelineTwinProps`):**

| Prop | Type | Meaning |
|---|---|---|
| `execution` | `Execution \| null` | Source of the step list. Empty or null selects the placeholder list. |
| `bob` | `BobConnection?` | Colours and labels the Headless Bob external node |
| `repo` | `Repository?` | Colours and labels the Git external node |
| `qse` | `QseConfig?` | Colours and labels the QSE CLI external node |
| `streamMode` | `'mock' \| 'realtime'?` | Triggers the DEMO note and the "recorded" QSE detail |

Also exported: `buildExternals(...)`.

**Geometry constants:** `STEP_W=108`, `STEP_H=76`, `GAP=24`, `PAD=12`, `EXT_Y=16`, `EXT_H=60`, `STEP_Y=150`. `viewBox = 0 0 {PAD*2 + n*STEP_W + (n-1)*GAP} 252`. For 9 steps width is 1188; for 8, 1056. The SVG has `min-width: 1000px` and `width: 100%`.

**Layout:** a row of step nodes (rect 108×76, 4 px left status bar, two title lines, a state line, optional duration, and the source label `backend` / `headless-bob` beneath). Arrows run between consecutive steps and turn green once the upstream step is completed. Above the row sit three external nodes, each centred over the step(s) it links to with dashed connector lines; a connector turns blue and thick while a linked step is running.

| External node | `data-testid` | Width | Linked steps | Tone rule |
|---|---|---|---|---|
| Git repository | `twin-ext-git` | 112 | `prepare_repo` | cloned → ok; failed → error; else idle |
| QSE CLI | `twin-ext-qse` | 112 | `validate_qse` | valid → ok; invalid → error; else idle |
| Headless Bob | `twin-ext-bob` | 172 | `submit_prompt`, `bob_processing` | connected → ok; auth/connection failed → error; else idle |

**Step tone map:** pending → idle, running → active, completed → ok, failed → error, skipped → warn, cancelled → warn. Step `data-testid` is `twin-step-<key>`; the wrapper is `pipeline-twin`.

**Short labels (`SHORT`)** exist for the 8 keys `validate_config`, `prepare_repo`, `validate_qse`, `prepare_context`, `submit_prompt`, `bob_processing`, `retrieve_results`, `generate_report`. Any other key (notably `completed`) falls back to splitting the backend label in half and truncating each half to 16 characters.

**Colour variables** (defined on `.twin`, because `--cds-*` are undefined, see 3.1.4):

| Variable | Value | Variable | Value |
|---|---|---|---|
| `--twin-layer` | `#262626` | `--twin-success` | `#42be65` |
| `--twin-border` | `#6f6f6f` | `--twin-info` | `#4589ff` |
| `--twin-text` | `#f4f4f4` | `--twin-error` | `#fa4d56` |
| `--twin-text-2` | `#c6c6c6` | `--twin-warning` | `#f1c21b` |

**CSS classes:** `.twin`, `.twin-svg`, `.twin-rect`, `.twin-bar`, `.twin-title`, `.twin-sub`, `.twin-src`, `.twin-state`, `.twin-flow` (`--done`), `.twin-link` (`--live`), `.twin-arrowhead`, `.twin-node--ok|active|error|warn`, `.twin-note`.

**Footer note:** "Now: <running step label>. " (only when a step is running) + "Built only from real step events and connection status; no percentage is shown because Headless Bob does not report one." + " DEMO: this twin replays a recorded run." when `execution.mock` or `streamMode === 'mock'`.

**Known inconsistency (Partial):** the backend defines **9** steps (`backend/src/orchestrators/steps.ts`, ending with `completed`). The twin's placeholder `DEFAULT_STEPS` (shown when no execution exists) has **8** (no `completed`). Once an execution exists the twin renders `execution.steps` (9 nodes) and the `completed` node uses the fallback label split ("Execution", "completed"). Both are cosmetic.

**Tests (5):** renders all steps pending with no execution; reflects real step statuses; shows the demo notice only for recorded runs; `buildExternals` derives external health from connection status; marks everything idle when nothing is configured.
