# Contributing to `real-time-guardrails`

> **For IBM maintainers.** This document describes the dev → BB publish workflow. Partners consuming the SDK don't need to read it.

## Source-of-truth model

The canonical development workspace for this package lives outside this Building Block repo. The copy you see here under `ai-trust/real-time-guardrails/assets/sdk/` is a **published mirror** — kept in sync via a tracked workflow rather than edited in-place.

| Location | Role |
|---|---|
| Dev workspace (not in this repo) | Canonical source. Active development, tests, day-to-day changes happen here. |
| `ai-trust/real-time-guardrails/assets/sdk/` (this folder) | Published mirror that partners consume from this public BB repo. |

**Do not edit files in `assets/sdk/` directly** — any change you make here will be overwritten by the next sync. Edit in the dev workspace, run the tests, then re-publish.

## Sync workflow

The sync is a one-direction rsync from the dev workspace into this folder, with explicit excludes for credentials, caches, and editor cruft.

```bash
SRC=/path/to/dev/real-time-guardrails           # canonical source (not in this repo)
DST=ai-trust/real-time-guardrails/assets/sdk    # this folder

rsync -av --delete \
  --exclude='.env' \
  --exclude='.venv/' --exclude='.venv-*/' \
  --exclude='__pycache__/' --exclude='.pytest_cache/' \
  --exclude='*.egg-info/' --exclude='dist/' --exclude='build/' \
  --exclude='.coverage' --exclude='.coverage.*' --exclude='.DS_Store' \
  --exclude='.mypy_cache/' --exclude='.ruff_cache/' \
  --exclude='inference_engine_cache/' \
  "$SRC/" "$DST/"
```

`--delete` ensures files removed in the dev workspace are also removed from the mirror.

## Pre-sync checklist

Run these in the dev workspace before syncing:

1. **All unit tests pass**: `pytest -m "not integration"` — expect every test green.
2. **Integration tests pass (if you have creds)**: `pytest -m integration` — verifies the synced SDK still talks to watsonx.governance correctly.
3. **Bump version**: edit `src/real_time_guardrails/_version.py` if this sync includes user-visible changes.
4. **Update changelog**: note what changed in this sync near the top of the SDK README under "What's New" or a dedicated `CHANGELOG.md` (whichever exists).
5. **Run the examples once**: at minimum `examples/library_quickstart.py` — confirms the example payloads still produce sensible scores after dependency upgrades.

## Post-sync checklist

After running the rsync into this folder:

1. **Security scan**:
   ```bash
   DST=ai-trust/real-time-guardrails/assets/sdk
   find "$DST" -name '.env' -type f                       # MUST be empty
   find "$DST" -type d \( -name '.venv' -o -name '__pycache__' -o -name '.pytest_cache' \)  # MUST be empty
   grep -rE 'WATSONX_APIKEY=[A-Za-z0-9_-]{20,}' "$DST"    # MUST be empty
   ```
2. **Fresh-install verification** — confirms the synced copy is self-contained:
   ```bash
   cd "$DST"
   python3.12 -m venv .venv-verify
   .venv-verify/bin/pip install -e ".[all]"
   .venv-verify/bin/pytest -m "not integration"          # expect all pass
   rm -rf .venv-verify
   ```
3. **Diff review**:
   ```bash
   cd <root of building-blocks repo>
   git status && git diff --stat ai-trust/real-time-guardrails/assets/sdk
   ```
   Scan for any file you didn't expect — especially anything matching the exclude patterns that snuck in.
4. **Commit + open PR** — never `git push` directly to `main` on this public repo.

## What goes where

| Add new feature to | When |
|---|---|
| `src/real_time_guardrails/` | Core library code — runs in any of the 3 interfaces (lib / REST / MCP) |
| `examples/` | Standalone scripts demonstrating usage patterns. Each example should be runnable as `python examples/<name>.py` |
| `tests/` | Unit tests (mocked SDK) + `@pytest.mark.integration` tests against the real SDK |
| `docs/` | Architecture diagrams, deep-dive markdown — not Sphinx, just markdown for GitHub rendering |
| `README.md` | Top-level usage docs — keep partner-facing language. Don't reference internal IBM systems by name |

## Versioning

Semantic versioning, kept in `src/real_time_guardrails/_version.py`. Bump on every sync that changes behavior partners observe:

- **Patch** (0.1.0 → 0.1.1): bug fixes, internal cleanup, doc fixes
- **Minor** (0.1.0 → 0.2.0): new metrics, new fields, new examples — backward compatible
- **Major** (0.1.0 → 1.0.0): removed fields, renamed APIs, breaking IBM SDK version bumps

The first major-version release should follow a documented production deployment at a partner site. Until then, expect 0.x.

## Reporting issues

Use the parent repo's issue tracker. Tag issues with `building-block:real-time-guardrails` so they're routable to the right maintainer.
