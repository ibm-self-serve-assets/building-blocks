# UI specification

## Design goal

A modern dark enterprise dashboard inspired by the visual language in the supplied Bob screenshots: left-side navigation, strong information hierarchy, muted navy surfaces, thin borders, monospaced metadata, compact status chips, and large operational metrics.

The implementation intentionally uses generic **FactoryPulse** branding rather than reproducing IBM Bob branding.

## Views

### Overview
- live line/machine scope
- projected output
- vibration, cycle time, defect rate
- overall risk
- exception-to-action recommendation
- scenario controls: Baseline, Degrade, Critical, Resolve + Learn

### Continuous RAG
- knowledge freshness / indexed chunk count
- question box with suggested prompts
- grounded response
- explicit retrieval/generation mode
- retrieved evidence cards with similarity score and source

### Knowledge
- publish a new knowledge event
- list knowledge documents observed by the app

### Streamhouse
- visual source → Confluent Cloud → consumer architecture
- five-step business flow

### Live Events
- current event feed showing factory state, exceptions, and knowledge changes

### Settings
- configuration presence only; secrets never displayed

## Frontend implementation

The frontend is dependency-free HTML/CSS/JavaScript under `app/static/`. This avoids a Node toolchain in the deployment container and keeps Code Engine builds fast.

Live updates use Server-Sent Events from `/api/events/stream`.
