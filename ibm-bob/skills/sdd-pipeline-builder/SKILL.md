---
name: sdd-pipeline-builder
description: Use when the user wants to create a new UFC insight pipeline from a GitHub issue or specification. Generates a spec.md, then builds the complete backend service, unit tests, registers it in the API, and opens a PR.
---

# SDD Pipeline Builder

Full workflow reference: `docs/SDD_FINAL_WORKFLOW.md`
Pipeline standards reference: `.bob/skills/pipeline-standards/SKILL.md`

**On activation** — also activate the pipeline-standards skill immediately:
```
use_skill("pipeline-standards")
```

**Working directory** — restrict all file reads/writes/searches here unless a step names another path:
```
backend/insights-engine-api/app/src/services/fight_insight_services/
```

---

## Step 0 — Determine specification source

Before parsing anything, identify how the spec was provided:

**If the user gave a GitHub issue NUMBER** (e.g. "issue #42", "from GitHub issue #7"):

Fetch the issue using this exact `curl` command (the PAT is read from the `.env` file):

```bash
curl -s \
  -H "Authorization: token $(grep '^GITHUB_PAT=' .env | cut -d'=' -f2)" \
  -H "Accept: application/vnd.github.v3+json" \
  "$(grep '^GITHUB_API_URL=' .env | cut -d'=' -f2)/repos/ibm-build-lab/ufc-insight-engine/issues/{NUMBER}"
```

**Do NOT** attempt `gh` CLI, do NOT use `.bob/mcp.json` (it no longer exists), do NOT ask the user for credentials.
The token is always in `.env` → `GITHUB_PAT`.  The API base URL is in `.env` → `GITHUB_API_URL`.

Parse all 10 sections from the `body` field of the JSON response.

**If the user pasted the issue content directly:**
- Parse all 10 sections inline from the pasted text

---

## Phase 1 — Spec Generation

### Step 1 — Get the specification

Accept one of:
- A GitHub issue number — fetch using `curl` as described in Step 0 above
- The full GitHub issue text pasted by the user directly

The issue must follow the 10-section template in `docs/SDD_FINAL_WORKFLOW.md §Step 1`. Parse every section. Note any gaps — they become clarifying questions in Step 2.

---

### Step 2 — Ask clarifying questions

Use `ask_followup_question` for every unclear or missing piece. Do NOT proceed until all are answered. Cover at minimum:

| Item | Default if not specified |
|---|---|
| Insight type name (appears in `InsightType` enum) | — required |
| Pipeline slug (snake_case → `{slug}_service.py`) | — required |
| Stat thresholds and columns (if stat-based) | none |
| Which prestige ranks apply (1–7) | all 7 |
| Active-fighter filtering per group | no |
| Scoring: base score, prestige penalty, threshold penalty | 100, 5, 3 |
| At least one heading example sentence | — required |
| Edge cases (min fights, tie handling, etc.) | MIN_FIGHTS=5 |

---

### Step 3 — Generate spec.md

**Location** (inside working directory):
```
sdd/{slug}_service/spec.md
```

Target length: **200–250 lines**. Use `write_file`. Structure:

```markdown
# {Insight Name} Pipeline Specification

## Metadata
- Pipeline slug: {slug}_service.py
- Insight type string: "{slug}"
- Category: [Stat-based / Streak-based / Comparative / Other]
- GitHub Issue: #{number}

## Configuration Constants
### Stat Thresholds          ← include only if stat-based
### Insight Generation Rules ← MIN_FIGHTS_FOR_INSIGHT, MIN_STREAK_LENGTH, TOP_N_RANKINGS
### Insight Scoring Rules    ← BASE_INSIGHT_SCORE, PRESTIGE_PENALTY, THRESHOLD_PENALTY, INSIGHT_TYPE

## Prestige Ranking Strategy
← Which of ranks 1–7 apply and whether active-fighter filtering is used per rank

## Core Functions
← Name + one-line description for each function to be implemented

## Heading Generation
### LLM System Prompt        ← exact text
### LLM User Prompt Template ← exact text with all VARIABLES listed
### Deterministic Fallback   ← exact f-string template

## Evidence Objects
### Facts object             ← all required keys + pipeline-specific keys
### pipeline_evidence list   ← ordered entries (Score, Prestige Rank, Rank, then pipeline-specific)

## Edge Cases
← Bullet list of every edge case and how it is handled

## Acceptance Criteria
← Copied from docs/SDD_FINAL_WORKFLOW.md §Acceptance Criteria, annotated for this pipeline

## Compliance Checklist
- [ ] Prestige Ranking System
- [ ] Scoring System
- [ ] LLM Heading Generation (3 functions)
- [ ] pipeline_evidence order correct
- [ ] Facts Object complete
- [ ] Unit tests: all 5 required tests pass
- [ ] InsightType enum updated
- [ ] Both service_map dicts updated
```

Present spec to user. **Wait for explicit approval** before continuing to Phase 2.

---

## Phase 2 — Pipeline Development

### Step 4 — Generate pipeline service

**Location** (inside working directory):
```
sdd/{slug}_service/{slug}_service.py
```

Follow **all** standards in `.bob/skills/pipeline-standards/SKILL.md`. Summary of mandatory structure:

```
1. Imports + logging setup
2. init_environment() shim
3. UPPER_SNAKE_CASE constants (STAT_THRESHOLDS, MIN_*, BASE_INSIGHT_SCORE, etc.)
4. Core metric/calculation functions
5. get_top_{metric}_for_group() + find_fighter_ranking() — use ranking_cache
6. calculate_insight_score() — delegates to utils.calculate_base_insight_score()
7. _build_llm_system_and_user() — pre-compute ALL phrasing, return (system, user)
8. generate_insight_heading_deterministic() — pure string fallback, no LLM
9. generate_insight_heading() — calls utils.call_wx_model_with_fallback()
10. _build_facts_object() — returns complete facts dict
11. generate_insights(fighter_data, fight_id, config) — main entry point
```

Key rules (full detail in pipeline-standards):
- `import utils` — NOT `experimental.utils`
- No variables outside functions (constants excepted)
- `pipeline_evidence` order: `{"Insight Score": …}` → `{"Prestige Rank": …}` → `{"Rank": …}` → pipeline-specific
- Prestige Rank **required** in both `facts` dict and `pipeline_evidence`
- LLM params: `decoding_method="greedy"`, `max_new_tokens=200`, `temperature=0.3`, `repetition_penalty=1.05`

Read these gold-standard references with `read_file` as needed:
- `backend/insights-engine-api/app/src/services/fight_insight_services/betting_service.py`
- `backend/insights-engine-api/app/src/services/fight_insight_services/consecutive_insight_service.py`
- `backend/insights-engine-api/app/src/services/fight_insight_services/win_streak_service.py`

Present code to user. **Wait for explicit approval** before continuing.

---

### Step 5 — Generate unit test

**Location** (inside working directory):
```
sdd/{slug}_service/{slug}_unit_test.py
```

Use the path-setup block verbatim — do not modify:

```python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../../..'))
sys.path.insert(0, project_root)
backend_path = os.path.join(project_root, 'backend')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
services_path = os.path.join(project_root, 'backend', 'insights-engine-api', 'app', 'src', 'services')
sys.path.insert(0, services_path)
```

Imports: `import backend.utils as utils` and `from PostgresService import PostgresService`.
Data loading: `utils.load_fighter_data(postgres_service)` — never read a CSV.

**9 required tests** (must all be present):

**Core 5 (structural baseline):**
1. `test_no_variables_outside_functions` — asserts no mutable names at module level
2. `test_has_generate_insights_function` — asserts `generate_insights` exists and is callable
3. `test_generate_insights_with_fighter_data` — runs the pipeline end-to-end, validates required top-level keys
4. `test_utils_file` — asserts `"import utils"` in source (not `experimental.utils`)
5. `test_insight_format` — validates `insight_id` prefix, `insight_type` enum value, required keys

**Extended 4 (coverage expansion — from PR #426):**
6. `test_pipeline_evidence_order` — runs `generate_insights`, asserts `pipeline_evidence[0]` key == `"Insight Score"`, `[1]` == `"Prestige Rank"`, `[2]` == `"Rank"`
7. `test_qualification_rule` — mocks the leaderboard builder (`get_top_*_for_group`) with a stub DataFrame; asserts fighters present in the DF qualify with correct rank, and fighters absent return `None`
8. `test_deterministic_headings` — calls `generate_insight_heading_deterministic()` directly with mock inputs; asserts a non-empty string is returned containing the fighter name and key stat value
9. `test_calculate_insight_score` — calls `calculate_insight_score()` for each prestige rank (1–6) and asserts the result equals `BASE_INSIGHT_SCORE - (prestige_rank * PRESTIGE_PENALTY) - (threshold_index * THRESHOLD_PENALTY)`

> **Note**: `test_qualification_rule` and `test_deterministic_headings` are pipeline-specific — function names in the mock patches must match the actual function names in the generated service (e.g. `get_top_distribution_for_group`, `compute_metric_pct`). Adapt the stub DataFrame columns to the pipeline's leaderboard schema.

---

### Step 6 — Run tests

Run from project root:
```bash
python3 backend/insights-engine-api/app/src/services/fight_insight_services/unit_tests/{slug}_unit_test.py
```

All 9 required tests must pass. Fix any failures before continuing.

---

### Step 7 — Register in API

Two files outside the working directory. Use `apply_diff` for both.

#### 7a. Add `InsightType` enum entry

File: `backend/insights-engine-api/app/src/model/FightInsightDataModel.py`

```python
{SlugTitle} = "{slug}"   # e.g.  Momentum_Shift = "momentum_shift"
```

Insert in alphabetical/categorical order inside the `InsightType` enum.

#### 7b. Add import + both service_map entries

File: `backend/insights-engine-api/app/route/fight_insight/routes.py`

1. Add import at the top with the other service imports:
```python
import app.src.services.fight_insight_services.{slug}_service as {slug}_insight_service
```

2. Add to the `/generate` service_map (~line 120):
```python
InsightType.{SlugTitle}: {slug}_insight_service,
```

3. Add to the `/generate-matchup-maker` service_map (~line 307) — same entry.

> ⚠️ **Both** `service_map` dicts must be updated. Missing one silently breaks the matchup route.

---

### Step 8 — Restructure into final directory layout

The final on-disk layout for the pipeline is:

```
fight_insight_services/
├── {slug}/
│   ├── __init__.py                ← required for Python package import
│   ├── {slug}_service.py          ← production service
│   ├── {slug}_unit_test.py        ← production unit test
│   └── sdd/
│       ├── spec.md                ← specification
│       └── {slug}_service_dev.py  ← dev/scratch copy
```

There is **no** top-level `{slug}_service.py` copy. The API imports directly from the subfolder.

Run these shell commands to build that layout:

```bash
BASE=backend/insights-engine-api/app/src/services/fight_insight_services

# Create the slug package directory
mkdir -p $BASE/{slug}/sdd
touch $BASE/{slug}/__init__.py

# Promote production files from the sdd staging area
cp $BASE/sdd/{slug}_service/{slug}_service.py   $BASE/{slug}/{slug}_service.py
cp $BASE/sdd/{slug}_service/{slug}_unit_test.py $BASE/{slug}/{slug}_unit_test.py

# Copy spec + dev copy into slug/sdd/
cp $BASE/sdd/{slug}_service/spec.md              $BASE/{slug}/sdd/spec.md
cp $BASE/sdd/{slug}_service/{slug}_service.py    $BASE/{slug}/sdd/{slug}_service_dev.py

# Remove the old flat sdd/{slug}_service/ staging directory
rm -rf $BASE/sdd/{slug}_service/
```

After building the directory, update two things in the promoted unit test (`{slug}/{slug}_unit_test.py`):

1. `SERVICE_FILE` must point to the service file **in the same folder**:
   ```python
   SERVICE_FILE = os.path.join(os.path.dirname(__file__), "{slug}_service.py")
   ```
2. The `sys.path` parent insert must add `fight_insight_services/` (the `..` from `{slug}/`):
   ```python
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
   ```

Update the `routes.py` import to use the package path (Step 7b already does this):
```python
import app.src.services.fight_insight_services.{slug}.{slug}_service as {slug}_insight_service
```

---

### Step 9 — Commit and create PR

#### Prerequisites (one-time setup)

`gh` CLI must be installed and authenticated against `github.ibm.com`.

```bash
# Install gh CLI (macOS)
brew install gh

# Authenticate — two things happen here:
#   1. git push/pull uses SSH (your ~/.ssh key, no password)
#   2. gh API calls (pr create, issue view, etc.) use the token you paste
#
# When prompted: GitHub Enterprise Server → hostname: github.ibm.com
#                → SSH (for git operations)
#                → Paste an authentication token
gh auth login --hostname github.ibm.com --git-protocol ssh

# Verify
gh auth status
```

**Important:** `--git-protocol ssh` controls how `git push/pull` works — it uses your SSH key.
`gh pr create` always calls the GitHub REST API and **always requires a token** — SSH keys are not valid API credentials. This is a GitHub platform constraint, not a `gh` limitation.

The token must have **`pull_requests:write`** scope on the `ibm-build-lab` org.
It is stored in the macOS keychain by `gh` — it never appears in any committed file.

---

#### 9a — Stage and commit (7 files only)

Stage only the 7 pipeline deliverable files — nothing else:

```bash
git add \
  backend/insights-engine-api/app/src/services/fight_insight_services/{slug}/ \
  backend/insights-engine-api/app/route/fight_insight/routes.py \
  backend/insights-engine-api/app/src/model/FightInsightDataModel.py

git commit -m "feat: Add {slug} pipeline via SDD (issue #{number})

- {slug}/{slug}_service.py: [one-line description]
- {slug}/{slug}_unit_test.py: 9/9 tests pass
- {slug}/sdd/spec.md: pipeline specification
- InsightType.{SlugTitle} added to FightInsightDataModel
- Both service_map dicts updated in routes.py (/generate + /generate-matchup-maker)"
```

The 7 staged files are:
- `{slug}/__init__.py`
- `{slug}/{slug}_service.py`
- `{slug}/{slug}_unit_test.py`
- `{slug}/sdd/spec.md`
- `{slug}/sdd/{slug}_service_dev.py`
- `routes.py`
- `FightInsightDataModel.py`

> ⚠️ If Vault Radar blocks the commit, a secret leaked into a staged file.
> Run `git status` to identify it, remove it, re-stage and retry.

#### 9b — Push branch

```bash
git push origin $(git branch --show-current)
```

#### 9c — Create PR with `gh`

```bash
SLUG="{slug}"      # replace with the actual slug
NUMBER="{number}"  # replace with the issue number

gh pr create \
  --repo ibm-build-lab/ufc-insight-engine \
  --base main \
  --title "feat: Add ${SLUG} pipeline via SDD (issue #${NUMBER})" \
  --body "## Summary
Adds the \`${SLUG}\` insight pipeline (closes #${NUMBER}).

### Changes
- \`${SLUG}/${SLUG}_service.py\` — production service
- \`${SLUG}/${SLUG}_unit_test.py\` — 9/9 tests pass against live DB + watsonx
- \`${SLUG}/sdd/spec.md\` — pipeline specification
- \`InsightType\` registered in enum and both service_maps in routes.py

### Testing
All 9 unit tests pass: test_calculate_insight_score, test_deterministic_headings,
test_generate_insights_with_fighter_data, test_has_generate_insights_function,
test_insight_format, test_no_variables_outside_functions, test_pipeline_evidence_order,
test_qualification_rule, test_utils_file"
```

`gh` prints the PR URL on success. If the token lacks `pull_requests:write`, fall back to the browser:
```bash
open "https://github.ibm.com/ibm-build-lab/ufc-insight-engine/compare/main...$(git branch --show-current)?expand=1"
```

---

## Critical rules

1. Working directory is `fight_insight_services/`. Only Steps 7, 8, and 9 touch files outside it.
2. NEVER produce placeholder code — every function must be complete and runnable.
3. NEVER assume — use `ask_followup_question` for anything ambiguous.
4. ALWAYS wait for user approval after Step 3 (spec) and Step 4 (code).
5. ALWAYS update **both** `service_map` dicts in `routes.py` — use the package import path `fight_insight_services.{slug}.{slug}_service`.
6. Follow every standard in `.bob/skills/pipeline-standards/SKILL.md` — no exceptions.
7. NEVER commit `.bob/mcp.json` — PAT lives in `.env` (gitignored).
8. A PR commit must contain exactly 7 files: the 5 pipeline files in `{slug}/`, plus `routes.py` and `FightInsightDataModel.py`. No SDD tooling, docs, or scaffolding files.
