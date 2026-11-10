# Digital twin guide

## When to use

After `frontend-ui.md`, before or together with the Workspace page in `feature-pages.md`. Use whenever the Pipeline digital twin is created, restyled, tested or debugged (including a blank render).

## Inputs you need

- [twin-spec.md](../references/twin-spec.md): SPEC 3.4 verbatim.
- Types from `frontend/src/types/api.ts` (`Execution`, `BobConnection`, `Repository`, `QseConfig`).
- Step definitions: `backend/src/orchestrators/steps.ts` (9 steps).
- `BUILD_DECISIONS.md` (G2, G3, G4).

## Requirements covered

| ID | Requirement | Acceptance test |
|---|---|---|
| FR-12 | The system shall show a live pipeline diagram derived only from real step events and connection status | With no execution, every step node is idle/pending; with steps `[completed, running, pending...]`, nodes show exactly those states; the component makes no API call (AC-14). |

## Steps

### The rules (do not skip)

1. **Pure view.** `PipelineTwin` receives data the page already has. It makes **no** API call and holds no server state.
2. **No invented progress.** Never show a percentage, ETA, animation of progress or any state that no step event or connection status reported. Headless Bob exposes no percentage; say so in the footer note.
3. **Placeholders are labelled.** When `execution` is null or has no steps, render the placeholder step list (`DEFAULT_STEPS`) with every node pending/idle. Do not imply a run exists.
4. **External node health comes only from stored status** (below), never from guesses.
5. **DEMO honesty.** When `execution.mock` or `streamMode === 'mock'`, append " DEMO: this twin replays a recorded run." to the footer note and use the "recorded" QSE detail.
6. **Must not crash the Workspace page.** There is no ErrorBoundary in the app (G4). A throw inside the twin blanks the whole page. Defend against undefined `bob`, `repo`, `qse`, unknown step keys and empty step arrays; the test suite must include these.
7. **Colours via `--twin-*`, never `--cds-*`** (G3): `--cds-*` are undefined unless the theme class is applied; an undefined SVG fill is black and an undefined stroke is none, which blanked the first version.

### Component API (`frontend/src/components/PipelineTwin.tsx`)

```ts
interface PipelineTwinProps {
  execution: Execution | null;
  bob?: BobConnection;
  repo?: Repository;
  qse?: QseConfig;
  streamMode?: 'mock' | 'realtime';
}
export function buildExternals(...): ExternalNode[]  // also exported, unit-tested
```

Mounted by `WorkspacePage` inside `Card title="Pipeline digital twin"` (between "Execution controls" and "Execution monitor").

### Geometry

`STEP_W=108`, `STEP_H=76`, `GAP=24`, `PAD=12`, `EXT_Y=16`, `EXT_H=60`, `STEP_Y=150`. `viewBox = 0 0 {PAD*2 + n*STEP_W + (n-1)*GAP} 252` (n=9 -> width 1188; n=8 -> 1056). SVG has `width: 100%`, `min-width: 1000px`; wrapper `.twin { overflow-x: auto }`.

### Layout

- A row of step nodes: rect 108x76, 4 px left status bar, two title lines, a state line, optional duration, and the source label `backend` / `headless-bob` beneath.
- Arrows between consecutive steps; an arrow turns green once the upstream step is completed (`.twin-flow--done`).
- Three external nodes above the row, each centred over the step(s) it links to, with dashed connectors (`.twin-link`); a connector turns blue and thick (`.twin-link--live`) while a linked step is running.

| External node | `data-testid` | Width | Linked steps | Tone rule |
|---|---|---|---|---|
| Git repository | `twin-ext-git` | 112 | `prepare_repo` | cloned -> ok; failed -> error; else idle |
| QSE CLI | `twin-ext-qse` | 112 | `validate_qse` | valid -> ok; invalid -> error; else idle |
| Headless Bob | `twin-ext-bob` | 172 | `submit_prompt`, `bob_processing` | connected -> ok; auth_failed/connection_failed -> error; else idle |

### Status mapping

Step tone: pending -> idle, running -> active, completed -> ok, failed -> error, skipped -> warn, cancelled -> warn. Test ids: wrapper `pipeline-twin`; steps `twin-step-<key>`.

### Labels

`SHORT` provides two-line labels for 8 keys: `validate_config`, `prepare_repo`, `validate_qse`, `prepare_context`, `submit_prompt`, `bob_processing`, `retrieve_results`, `generate_report`. Any other key (notably `completed`) falls back to splitting the backend label in half and truncating each half to 16 characters.

### Colour variables (defined on `.twin`)

| Variable | Value | Variable | Value |
|---|---|---|---|
| `--twin-layer` | `#262626` | `--twin-success` | `#42be65` |
| `--twin-border` | `#6f6f6f` | `--twin-info` | `#4589ff` |
| `--twin-text` | `#f4f4f4` | `--twin-error` | `#fa4d56` |
| `--twin-text-2` | `#c6c6c6` | `--twin-warning` | `#f1c21b` |

CSS classes: `.twin`, `.twin-svg`, `.twin-rect`, `.twin-bar`, `.twin-title` (12 px / 600), `.twin-sub` (10 px), `.twin-src` (10 px), `.twin-state` (11 px), `.twin-flow` (`--done`), `.twin-link` (`--live`), `.twin-arrowhead`, `.twin-node--ok|active|error|warn`, `.twin-note`. Rect fill `--twin-layer`, stroke `--twin-border`. Styles go at the end of `frontend/src/styles/index.scss`. No CSS animations.

### Accessibility

SVG has `role="img"`, a `<title>`, and an `aria-label` summarising every step and each external node's state.

### Footer note

"Now: <running step label>. " (only when a step is running) + "Built only from real step events and connection status; no percentage is shown because Headless Bob does not report one." + (mock only) " DEMO: this twin replays a recorded run."

### G2 inconsistency (Partial)

The backend defines **9** steps (ending with `completed`); the placeholder `DEFAULT_STEPS` has **8** (no `completed`). With a real execution the twin renders `execution.steps` (9 nodes) and `completed` uses the fallback label split ("Execution", "completed"). Faithful clone: keep 8 placeholders and the fallback. Fix: add a ninth placeholder and a `SHORT` entry for `completed`.

## Verification (exit gate)

```bash
cd frontend && npm run typecheck && npm test && npm run build
```

Five tests in `PipelineTwin.test.tsx` (AC-14):

1. Renders all steps pending with no execution.
2. Reflects real step statuses.
3. Shows the demo notice only for recorded runs.
4. `buildExternals` derives external health from connection status.
5. Marks everything idle when nothing is configured.

FR-12 statement: the test for rule 2 must assert there is no `%` text and no node state beyond what the input provided. Add a regression test that renders with `bob`, `repo`, `qse` undefined and an unknown step key and does not throw (rule 6).

Visual check on `/workspace`: dark nodes on `#161616`, light text, coloured status bars; if you see black shapes or nothing, `--twin-*` is not defined on `.twin`.

## Pitfalls

- Using `var(--cds-*)` in the SVG (blank render).
- Calling APIs or computing progress inside the component.
- Hard-coding 8 or 9 nodes; derive `n` from `execution.steps`.
- Forgetting `min-width` / horizontal scroll, which squashes labels on narrow screens.
- Letting a missing prop throw (no ErrorBoundary).

## Known gaps that apply

- G2: placeholder 8 steps vs backend 9; `SHORT` lacks `completed`. User decision: <fix | keep as built>
- G3: `--cds-*` variables undefined. User decision: <fix | keep as built>
- G4: no ErrorBoundary (the twin must not crash the page). User decision: <fix | keep as built>

## SPEC references

SPEC 3.1.4, SPEC 3.4, SPEC 4.5 (steps), SPEC 4.6 (monitoring). Detail: [twin-spec.md](../references/twin-spec.md).
