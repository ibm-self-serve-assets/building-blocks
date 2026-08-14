---
name: pipeline-standards
description: Use when you need UFC insight pipeline best practices and coding standards — covers required code structure, utils usage, evidence objects, prestige ranking, heading generation, and the compliance checklist. Auto-activates when sdd-pipeline-builder needs the standards, or when the user asks about pipeline coding conventions.
metadata:
  disable-model-invocation: false
---

# UFC Pipeline Coding Standards

This document is the single source of truth for all backend service pipeline code standards.
It is referenced by `.bob/skills/sdd-pipeline-builder/SKILL.md` during code generation.

---

## 1. Required File Structure (in order)

```python
# 1. Imports + warnings suppression + logging setup
import warnings, logging, utils, pandas as pd
from typing import List, Dict, Any, Optional, Tuple
warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 2. Environment shim
def init_environment():
    """Compatibility shim — delegates to utils.init_pipeline_environment()."""
    return utils.init_pipeline_environment()

# 3. UPPER_SNAKE_CASE constants (the ONLY allowed module-level names)
STAT_THRESHOLDS = { ... }       # if stat-based
MIN_FIGHTS_FOR_INSIGHT = 5
TOP_N_RANKINGS = 5
BASE_INSIGHT_SCORE = 100
PRESTIGE_PENALTY = 5
THRESHOLD_PENALTY = 3           # if applicable
INSIGHT_TYPE = "Pipeline Name"

# 4. Core metric/calculation functions
# 5. get_top_{metric}_for_group() + find_fighter_ranking()
# 6. calculate_insight_score()
# 7. _build_llm_system_and_user()
# 8. generate_insight_heading_deterministic()
# 9. generate_insight_heading()
# 10. _build_facts_object()
# 11. generate_insights()       ← always the last function
```

---

## 2. Imports

- Backend services: `import utils` (resolves to `backend/utils.py`)
- Never use `import experimental.utils`
- No variables declared outside functions — only UPPER_SNAKE_CASE constants are permitted at module level

---

## 3. Prestige Ranking System

Seven ranks, 1 = most prestigious:

| Rank | Scope |
|---|---|
| 1 | Among all fighters (UFC history) |
| 2 | Among a gender class |
| 3 | Among active fighters |
| 4 | Among active fighters in gender class |
| 5 | Among a weight class division |
| 6 | Among active fighters in a weight class division |
| 7 | Career class |

- Get groups: `utils.get_standard_ranking_groups()`
- Filter per group: `utils.filter_fighter_data_by_group(fighter_data, group)`
- Select best: `utils.find_best_ranking(all_rankings)` — picks lowest prestige_rank, then lowest rank
- Use `ranking_cache` param in `get_top_*_for_group()` to avoid recomputing the same leaderboard

---

## 4. Scoring

```python
def calculate_insight_score(prestige_rank: int, threshold_index: int) -> int:
    return utils.calculate_base_insight_score(
        prestige_rank=prestige_rank,
        threshold_index=threshold_index,
        base_score=BASE_INSIGHT_SCORE,
        prestige_penalty=PRESTIGE_PENALTY,
        threshold_penalty=THRESHOLD_PENALTY,
    )
```

---

## 5. Heading Generation — Three Mandatory Functions

### `_build_llm_system_and_user()`
- Pre-compute **all** phrasing before passing to LLM: ordinals (`utils.ordinal()`), pronouns (`utils.pronouns()`), rank display (tied vs solo)
- System prompt must enforce: one sentence, no extra text, no rephrasing outside placeholders
- User prompt must list **every** variable and the exact template sentence

### `generate_insight_heading_deterministic()`
- Pure Python f-string — no LLM call, no network dependency
- Must produce a grammatically correct heading on its own
- Always generated first so it is ready as fallback

### `generate_insight_heading()`
```python
def generate_insight_heading(...) -> str:
    fallback = generate_insight_heading_deterministic(...)
    system, user = _build_llm_system_and_user(...)
    prompt = utils.build_llm_prompt_llama3(system=system, user=user)
    return utils.call_wx_model_with_fallback(
        prompt=prompt,
        fallback_heading=fallback,
        model_params={
            "decoding_method": "greedy",
            "max_new_tokens": 200,
            "min_new_tokens": 0,
            "temperature": 0.3,
            "repetition_penalty": 1.05,
        },
    )
```

---

## 6. Evidence Objects

### Facts dict (complete information for downstream use)
```python
facts = {
    "Fighter name": fighter_name,
    "Gender": gender,
    "Statistic": stat_column,               # human-readable stat name
    "Milestone threshold": threshold,        # SEPARATE from Statistic
    "Rank": int(best_ranking["rank"]),
    "Number tied at this rank": int(best_ranking.get("num_tied", 0)),
    "Leader context": group.get("leader_string", ""),
    "Prestige Rank": int(group["prestige_rank"]),   # REQUIRED
    "Insight type": INSIGHT_TYPE,
    # ... pipeline-specific additional keys
}
```

### `pipeline_evidence` list — mandatory order
```python
pipeline_evidence = [
    {"Insight Score": insight_score},    # position 1 — ALWAYS FIRST
    {"Prestige Rank": prestige_rank},    # position 2 — ALWAYS SECOND
    {"Rank": rank},                      # position 3 — ALWAYS THIRD
    {"Statistic": stat_column},          # optional — stat-based pipelines only
    {"Milestone threshold": threshold},  # optional — separate from Statistic
    # pipeline-specific dicts come last
]
```

---

## 7. `generate_insights()` — Main Entry Point

Signature: `generate_insights(fighter_data: pd.DataFrame, fight_id: int, config: Dict) -> List[Dict[str, Any]]`

Internal steps (always in this order):
1. Data preparation (parse `ControlTimeSeconds`, `Event_StartTime`)
2. Identify upcoming fight and both fighters
3. Filter to historical data only (exclude the upcoming fight row)
4. Build `weight_class_map` and `ranking_cache`
5. For each fighter:
   a. Get fight history
   b. Skip if `< MIN_FIGHTS_FOR_INSIGHT`
   c. Determine weight class
   d. Analyze stats, collect insights
6. Return list sorted by insight score descending

---

## 8. Utils Reference

Both `backend/utils.py` and `experimental/utils.py` expose the same API:

| Function | Purpose |
|---|---|
| `utils.init_pipeline_environment()` | Load env vars, watsonx credentials |
| `utils.get_standard_ranking_groups()` | Return all 7 prestige groups |
| `utils.filter_fighter_data_by_group()` | Filter DataFrame by group criteria |
| `utils.find_best_ranking()` | Pick lowest prestige_rank then rank |
| `utils.determine_fighter_weight_class()` | Current weight class of a fighter |
| `utils.calculate_base_insight_score()` | Standardised scoring formula |
| `utils.format_stat_threshold_string()` | "3+ takedowns landed" strings |
| `utils.build_llm_prompt_llama3()` | Format system+user into Llama 3 prompt |
| `utils.call_wx_model_with_fallback()` | Call watsonx.ai with fallback heading |
| `utils.create_ranking_table()` | Standardised ranking table for evidence |
| `utils.expand_consolidated_columns()` | Expand JSON-packed columns in DataFrame |
| `utils.load_fighter_data(postgres_service)` | Load from PostgreSQL (backend only) |
| `utils.ordinal(n)` | 1 → "1st", 2 → "2nd" … |
| `utils.pronouns(gender, plural, capitalize)` | He/She, his/her |
| `utils.features_nl_dictionary()` | Stat column → natural language name |
| `utils.time_to_seconds()` | "MM:SS" → seconds |
| `utils.seconds_to_minutes()` | seconds → "MM:SS" |

---

## 9. Compliance Checklist

Before any pipeline is considered complete, all items must be checked:

- [ ] `import utils` (not `experimental.utils`)
- [ ] No mutable variables outside functions; only UPPER_SNAKE_CASE constants
- [ ] `init_environment()` shim present
- [ ] `utils.get_standard_ranking_groups()` used for prestige groups
- [ ] `utils.find_best_ranking()` used to select best group
- [ ] Prestige Rank in `facts` dict
- [ ] `pipeline_evidence` is a list of dicts with Score → Prestige Rank → Rank first
- [ ] `_build_llm_system_and_user()` pre-computes all phrasing
- [ ] `generate_insight_heading_deterministic()` works without any LLM
- [ ] `generate_insight_heading()` uses `utils.call_wx_model_with_fallback()`
- [ ] LLM params: `greedy / 200 / 0 / 0.3 / 1.05`
- [ ] `_build_facts_object()` includes all required keys
- [ ] `generate_insights()` is the last function in the file
- [ ] Unit tests: all 9 required tests present and passing (core 5 + extended 4)

---

## 10. Gold-Standard Reference Implementations

Read these with `read_file` when you need a concrete example:

- `backend/insights-engine-api/app/src/services/fight_insight_services/betting_service.py`
- `backend/insights-engine-api/app/src/services/fight_insight_services/consecutive_insight_service.py`
- `backend/insights-engine-api/app/src/services/fight_insight_services/win_streak_service.py`
