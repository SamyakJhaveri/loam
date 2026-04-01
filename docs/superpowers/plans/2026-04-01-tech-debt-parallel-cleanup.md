# Tech Debt Parallel Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the tech debt identified in the 2026-04-01 scan across 5 analysis scripts (magic numbers, duplicated logic, dead code, nested conditionals) using a parallel 6-agent team with strict TDD and a critic review loop.

**Architecture:** 5 parallel worker agents (one per script) each follow TDD: write failing tests for new utility functions → implement → pass → refactor call sites → re-run all tests. One critic agent reviews each worker's git diff against the tech debt report, issues APPROVE or REQUEST_CHANGES feedback, and the worker iterates until the critic issues APPROVE. Team is created via `/agent-team` skill and `TeamCreate` tool. Each worker uses `ultrathink`.

**Tech Stack:** Python 3.10+, pytest, `scripts/analysis/` + `scripts/evaluation/`, `source env_parbench/bin/activate` before any Python command. No new dependencies.

---

## File Map

| Agent | Modifies | Test File (pre-existing) | Net new |
|-------|---------|--------------------------|---------|
| `worker-build-error` | `scripts/analysis/build_error_taxonomy.py` | `scripts/analysis/test_build_error_taxonomy.py` | 3 new test functions |
| `worker-paper-data` | `scripts/analysis/generate_paper_data.py` | `scripts/analysis/test_generate_paper_data.py` | 4 new test functions |
| `worker-stats` | `scripts/analysis/statistical_analysis.py` | `scripts/analysis/test_statistical_analysis.py` | 6 new test functions |
| `worker-tokens` | `scripts/analysis/token_analysis.py` | `scripts/analysis/test_token_analysis.py` | 5 new test functions |
| `worker-figures` | `scripts/evaluation/generate_paper_figures.py` | `scripts/evaluation/test_generate_paper_figures.py` (CREATE) | 4 new test functions |
| `critic` | reads all diffs | — | — |

---

## Task 1: Pre-Flight Baseline

Run before launching the team. All existing tests must be green before any changes.

- [ ] **Step 1: Activate venv and run the full test suite**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_build_error_taxonomy.py \
       scripts/analysis/test_generate_paper_data.py \
       scripts/analysis/test_statistical_analysis.py \
       scripts/analysis/test_token_analysis.py \
       -v --tb=short 2>&1 | tail -30
```

Expected: All tests PASS. If any fail, stop — do not proceed until baseline is green.

- [ ] **Step 2: Commit baseline sentinel**

```bash
git stash  # should be empty; confirms clean working tree
git status
```

Expected: `nothing to commit, working tree clean`.

---

## Task 2: Launch the Agent Team

Use the `/agent-team` skill (which calls `TeamCreate`) to spawn 6 teammates. Run this task after Task 1 baseline is confirmed green.

- [ ] **Step 1: Invoke `/agent-team` skill to create the team**

Tell Claude Code:

```
/agent-team

Create a team with 6 teammates. All teammates use Opus and ultrathink. Names:
  worker-build-error, worker-paper-data, worker-stats, worker-tokens, worker-figures, critic

The 5 worker teammates work in parallel. The critic reviews each worker's output
after they finish and before they are shut down. Workers iterate on critic feedback
until the critic issues APPROVE. Use bypassPermissions mode.
```

- [ ] **Step 2: Assign tasks to all 5 workers simultaneously**

Send each worker its Task block from Tasks 3–7 below (copy the full block verbatim). Send all 5 in one message to start them in parallel.

---

## Task 3: Worker `worker-build-error` — `build_error_taxonomy.py`

**Full task prompt to send this teammate:**

```
You are working on scripts/analysis/build_error_taxonomy.py.
Use ultrathink for all reasoning. Follow strict TDD.
Activate venv first: source env_parbench/bin/activate

Your job is to fix these tech debt items (no other changes):
1. Extract safe_percentage(n, d) utility and replace 12 call sites
2. Extract _accumulate_category_stats() helper and replace 4 duplicate blocks
3. Extract MAX_EXAMPLES_PER_CATEGORY = 3 constant and replace 4 sites
4. Extract OTHER_BUCKET_REFINEMENT_THRESHOLD = 20 constant and replace 3 sites
5. Remove unused imports (pytest, Counter, defaultdict) from test_build_error_taxonomy.py

Steps:
```

- [ ] **Step 1: Run existing tests to record baseline**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_build_error_taxonomy.py -v --tb=short
```

Record the count: N tests passing.

- [ ] **Step 2: Write failing tests for `safe_percentage` and `_accumulate_category_stats`**

Append to `scripts/analysis/test_build_error_taxonomy.py`:

```python
# --- new tests: safe_percentage ---

def test_safe_percentage_normal():
    from scripts.analysis.build_error_taxonomy import safe_percentage
    assert safe_percentage(10, 20) == 50.0

def test_safe_percentage_zero_denominator():
    from scripts.analysis.build_error_taxonomy import safe_percentage
    assert safe_percentage(5, 0) == 0.0

def test_safe_percentage_full():
    from scripts.analysis.build_error_taxonomy import safe_percentage
    assert safe_percentage(20, 20) == 100.0
```

- [ ] **Step 3: Run new tests — confirm they fail**

```bash
pytest scripts/analysis/test_build_error_taxonomy.py::test_safe_percentage_normal -v
```

Expected: `ImportError` or `AttributeError: module has no attribute 'safe_percentage'`.

- [ ] **Step 4: Add `safe_percentage` to `build_error_taxonomy.py`**

Insert near the top of the file, after imports, before the first function:

```python
def safe_percentage(numerator: int | float, denominator: int | float) -> float:
    """Return numerator/denominator * 100, or 0.0 if denominator is zero."""
    return numerator / denominator * 100 if denominator else 0.0
```

- [ ] **Step 5: Replace all 12 inline percentage expressions**

Find every instance of the pattern `X / Y * 100 if Y > 0 else 0` (and variants like `... if total > 0 else 0`) and replace with `safe_percentage(X, Y)`.

Grep to find all sites before editing:

```bash
grep -n "/ .* \* 100 if" scripts/analysis/build_error_taxonomy.py
```

Edit each one. There should be ~12 replacements.

- [ ] **Step 6: Add module-level constants**

Insert after `safe_percentage`:

```python
MAX_EXAMPLES_PER_CATEGORY: int = 3
OTHER_BUCKET_REFINEMENT_THRESHOLD: float = 20.0
```

Replace every occurrence of the literal `3` used as example limit (4 sites, pattern: `if len(cat_data["examples"]) < 3`) with `MAX_EXAMPLES_PER_CATEGORY`. Replace `> 20` threshold (3 sites, lines ~1089–1105) with `> OTHER_BUCKET_REFINEMENT_THRESHOLD`.

Grep to locate:

```bash
grep -n 'len.*examples.*< 3\|> 20' scripts/analysis/build_error_taxonomy.py
```

- [ ] **Step 7: Remove unused imports from test file**

In `scripts/analysis/test_build_error_taxonomy.py`, remove:

```python
import pytest          # line ~10
from collections import Counter, defaultdict  # line ~11 — remove Counter, defaultdict; keep 'from collections import' only if something else uses it
```

Grep first to confirm nothing else uses them:

```bash
grep -n "pytest\.\|Counter\|defaultdict" scripts/analysis/test_build_error_taxonomy.py
```

If only in the import line, delete the lines.

- [ ] **Step 8: Run full test suite for this file**

```bash
pytest scripts/analysis/test_build_error_taxonomy.py -v --tb=short
```

Expected: All original tests PASS + 3 new `safe_percentage` tests PASS.

- [ ] **Step 9: Signal critic**

Message `critic`: "worker-build-error done. Please review `scripts/analysis/build_error_taxonomy.py` and `scripts/analysis/test_build_error_taxonomy.py`. All tests pass."

Provide the output of `git diff scripts/analysis/build_error_taxonomy.py scripts/analysis/test_build_error_taxonomy.py`.

---

## Task 4: Worker `worker-paper-data` — `generate_paper_data.py`

**Full task prompt to send this teammate:**

```
You are working on scripts/analysis/generate_paper_data.py.
Use ultrathink for all reasoning. Follow strict TDD.
Activate venv first: source env_parbench/bin/activate

Your job is to fix these tech debt items (no other changes):
1. Remove the dead unused variable `multi_attempt` (line ~901)
2. Collapse the duplicate pass@k if/else branches (lines ~1027–1038) into one computation
3. Extract module-level constants: MIN_L0_SAMPLE_SIZE=10, MIN_PASSK_TASK_SAMPLES=3, MIN_BALANCED_KERNELS=20, ALPHA_SIGNIFICANCE=0.05, COHEN_H_SMALL_THRESHOLD=0.20, COHEN_H_MEDIUM_THRESHOLD=0.80, PASSK_K_VALUES=[1,3]
4. Extract _determine_first_attempt_status() and _classify_repair_outcome() from _analyze_self_repair()
```

- [ ] **Step 1: Run existing tests to record baseline**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_generate_paper_data.py -v --tb=short
```

Record the count: N tests passing.

- [ ] **Step 2: Write a failing test that directly calls `_determine_first_attempt_status`**

Append to `scripts/analysis/test_generate_paper_data.py`:

```python
# --- new tests: helper extraction ---

def test_determine_first_attempt_status_pass():
    from scripts.analysis.generate_paper_data import _determine_first_attempt_status
    att = {"status": "PASS", "attempt": 1}
    assert _determine_first_attempt_status(att) == "PASS"

def test_determine_first_attempt_status_build_fail():
    from scripts.analysis.generate_paper_data import _determine_first_attempt_status
    att = {"status": "BUILD_FAIL", "attempt": 1}
    assert _determine_first_attempt_status(att) == "BUILD_FAIL"

def test_constants_exist():
    import scripts.analysis.generate_paper_data as gpd
    assert gpd.MIN_L0_SAMPLE_SIZE == 10
    assert gpd.ALPHA_SIGNIFICANCE == 0.05
    assert gpd.COHEN_H_SMALL_THRESHOLD == 0.20

def test_passk_k_values():
    from scripts.analysis.generate_paper_data import PASSK_K_VALUES
    assert set(PASSK_K_VALUES) == {1, 3}
```

- [ ] **Step 3: Run new tests — confirm they fail**

```bash
pytest scripts/analysis/test_generate_paper_data.py::test_determine_first_attempt_status_pass -v
```

Expected: `ImportError` — `_determine_first_attempt_status` does not exist yet.

- [ ] **Step 4: Add module-level constants**

Insert near top of `generate_paper_data.py`, after existing imports:

```python
MIN_L0_SAMPLE_SIZE: int = 10
MIN_PASSK_TASK_SAMPLES: int = 3
MIN_BALANCED_KERNELS: int = 20
ALPHA_SIGNIFICANCE: float = 0.05
COHEN_H_SMALL_THRESHOLD: float = 0.20
COHEN_H_MEDIUM_THRESHOLD: float = 0.80
PASSK_K_VALUES: list[int] = [1, 3]
```

Replace the corresponding literals in the file body:

```bash
grep -n "< 10\|< 3\|< 20\|0\.05\|0\.20\|0\.80\|\[1, 3\]" scripts/analysis/generate_paper_data.py
```

For each match, replace the literal with the constant name.

- [ ] **Step 5: Remove the dead `multi_attempt` variable**

Find line ~901 inside `_analyze_self_repair`:

```bash
grep -n "multi_attempt" scripts/analysis/generate_paper_data.py
```

Delete the assignment line entirely. It is not used or returned anywhere.

- [ ] **Step 6: Collapse the duplicate pass@k branches**

Find the if/else block around lines 1027–1038 where both branches compute the same formula:

```python
# BEFORE (lines ~1027–1038):
if c >= k_val:
    numerator = math.comb(n - c, k_val)
    denominator = math.comb(n, k_val)
    passk_val = 1.0 - (numerator / denominator) if denominator > 0 else 0.0
else:
    numerator = math.comb(n - c, k_val)
    denominator = math.comb(n, k_val)
    passk_val = 1.0 - (numerator / denominator) if denominator > 0 else 0.0
```

Replace with:

```python
# AFTER: single computation, no branch
numerator = math.comb(n - c, k_val)
denominator = math.comb(n, k_val)
passk_val = 1.0 - (numerator / denominator) if denominator > 0 else 0.0
```

- [ ] **Step 7: Extract `_determine_first_attempt_status`**

Identify the first-attempt status logic inside `_analyze_self_repair` (lines ~835–848). Extract it into a module-level helper. The extracted function should look like:

```python
def _determine_first_attempt_status(first_att: dict) -> str:
    """Return the status string for the first attempt in an eval result."""
    status = first_att.get("status", "")
    if status in ("PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL", "EXTRACTION_FAIL"):
        return status
    return "UNKNOWN"
```

Replace the inline logic in `_analyze_self_repair` with a call to this function. (Read the actual code at that location to ensure the extracted function body matches the real logic — do not guess; use Read tool on lines 835–848.)

- [ ] **Step 8: Run full test suite**

```bash
pytest scripts/analysis/test_generate_paper_data.py -v --tb=short
```

Expected: All original tests PASS + 4 new tests PASS.

- [ ] **Step 9: Signal critic**

Message `critic`: "worker-paper-data done. All tests pass." Provide `git diff scripts/analysis/generate_paper_data.py scripts/analysis/test_generate_paper_data.py`.

---

## Task 5: Worker `worker-stats` — `statistical_analysis.py`

**Full task prompt to send this teammate:**

```
You are working on scripts/analysis/statistical_analysis.py.
Use ultrathink for all reasoning. Follow strict TDD.
Activate venv first: source env_parbench/bin/activate

Your job is to fix these tech debt items (no other changes):
1. Extract is_deterministic(record) and is_stochastic(record) predicates, replace 3 sites each
2. Extract COHENS_H_INTERPRETATION and CRAMERS_V_INTERPRETATIONS as module-level data structures; refactor _interpret_h() and _interpret_v() to use them
3. Define MIN_EXPECTED_CELL_COUNT=5, MCNEMAR_EXACT_THRESHOLD=25, SAMPLE_SIZE_ADEQUACY_THRESHOLD=10 constants
4. Extract _get_direction_pairs(d, directions) helper from the 3-level nested loop in test_direction_asymmetry()
```

- [ ] **Step 1: Run existing tests to record baseline**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_statistical_analysis.py -v --tb=short
```

Record the count: N tests passing.

- [ ] **Step 2: Write failing tests**

Append to `scripts/analysis/test_statistical_analysis.py`:

```python
# --- new tests: predicate extraction ---

def test_is_deterministic_zero():
    from scripts.analysis.statistical_analysis import is_deterministic
    assert is_deterministic({"temperature": 0.0}) is True

def test_is_deterministic_missing_key():
    from scripts.analysis.statistical_analysis import is_deterministic
    assert is_deterministic({}) is True  # missing key → defaults to 0.0

def test_is_stochastic_nonzero():
    from scripts.analysis.statistical_analysis import is_stochastic
    assert is_stochastic({"temperature": 0.7}) is True

def test_is_stochastic_zero():
    from scripts.analysis.statistical_analysis import is_stochastic
    assert is_stochastic({"temperature": 0.0}) is False

def test_constants_exist():
    import scripts.analysis.statistical_analysis as sa
    assert sa.MIN_EXPECTED_CELL_COUNT == 5
    assert sa.MCNEMAR_EXACT_THRESHOLD == 25
    assert sa.SAMPLE_SIZE_ADEQUACY_THRESHOLD == 10

def test_get_direction_pairs_valid():
    from scripts.analysis.statistical_analysis import _get_direction_pairs
    directions = {"cuda-to-omp", "omp-to-cuda", "cuda-to-opencl"}
    pair = _get_direction_pairs("cuda-to-omp", directions)
    assert pair == ("cuda-to-omp", "omp-to-cuda")

def test_get_direction_pairs_no_reverse():
    from scripts.analysis.statistical_analysis import _get_direction_pairs
    directions = {"cuda-to-omp"}
    assert _get_direction_pairs("cuda-to-omp", directions) is None
```

- [ ] **Step 3: Run new tests — confirm they fail**

```bash
pytest scripts/analysis/test_statistical_analysis.py::test_is_deterministic_zero -v
```

Expected: `ImportError` — `is_deterministic` does not exist yet.

- [ ] **Step 4: Add `is_deterministic` / `is_stochastic` to `statistical_analysis.py`**

Insert near the top of the file, after imports:

```python
def is_deterministic(record: dict) -> bool:
    """Return True if this result record used temperature == 0 (greedy decoding)."""
    return (record.get("temperature") or 0.0) == 0.0


def is_stochastic(record: dict) -> bool:
    """Return True if this result record used temperature > 0."""
    return (record.get("temperature") or 0.0) > 0.0
```

Replace all 3 inline occurrences of `(r.get("temperature") or 0) == 0.0` with `is_deterministic(r)` and `> 0` variant with `is_stochastic(r)`.

```bash
grep -n 'get("temperature")' scripts/analysis/statistical_analysis.py
```

- [ ] **Step 5: Add module-level constants**

Insert after the predicate functions:

```python
MIN_EXPECTED_CELL_COUNT: int = 5
MCNEMAR_EXACT_THRESHOLD: int = 25
SAMPLE_SIZE_ADEQUACY_THRESHOLD: int = 10
```

Replace the corresponding magic numbers in the file body. Grep to locate:

```bash
grep -n "< 5\b\|< 25\b\|< 10\b" scripts/analysis/statistical_analysis.py
```

- [ ] **Step 6: Extract effect size interpretation tables**

Read `_interpret_h()` (lines ~563–570) and `_interpret_v()` (lines ~573–584) to capture the actual thresholds. Then insert at module level:

```python
# Cohen's h thresholds (Cohen 1988)
COHENS_H_INTERPRETATION: list[tuple[float, str]] = [
    (0.20, "small"),
    (0.80, "medium"),
    (float("inf"), "large"),
]

# Cramér's V thresholds keyed by df* (Akoglu 2018)
CRAMERS_V_INTERPRETATIONS: dict[int | None, list[tuple[float, str]]] = {
    1: [(0.10, "negligible"), (0.30, "small"), (0.50, "medium"), (float("inf"), "large")],
    2: [(0.07, "negligible"), (0.21, "small"), (0.35, "medium"), (float("inf"), "large")],
    None: [(0.06, "negligible"), (0.17, "small"), (0.29, "medium"), (float("inf"), "large")],
}
```

Rewrite `_interpret_h` to use the table:

```python
def _interpret_h(h: float) -> str:
    abs_h = abs(h)
    for threshold, label in COHENS_H_INTERPRETATION:
        if abs_h < threshold:
            return label
    return "large"
```

Rewrite `_interpret_v` to use the table (read the original function first to ensure correct df* key logic).

- [ ] **Step 7: Extract `_get_direction_pairs`**

Find the nested `for d in directions: if len(parts) == 2: if reverse in directions: if key not in pair_map:` block in `test_direction_asymmetry` (lines ~468–475). Extract:

```python
def _get_direction_pairs(d: str, directions: set[str]) -> tuple[str, str] | None:
    """Return (d, reverse) if both directions exist in the set, else None."""
    parts = d.split("-to-")
    if len(parts) != 2:
        return None
    reverse = f"{parts[1]}-to-{parts[0]}"
    if reverse not in directions:
        return None
    return (d, reverse)
```

Replace the nested block in `test_direction_asymmetry` with:

```python
for d in directions:
    pair = _get_direction_pairs(d, directions)
    if pair is None:
        continue
    key = tuple(sorted(pair))
    if key not in pair_map:
        pair_map[key] = pair
```

- [ ] **Step 8: Run full test suite**

```bash
pytest scripts/analysis/test_statistical_analysis.py -v --tb=short
```

Expected: All original tests PASS + 7 new tests PASS.

- [ ] **Step 9: Signal critic**

Message `critic`: "worker-stats done. All tests pass." Provide `git diff scripts/analysis/statistical_analysis.py scripts/analysis/test_statistical_analysis.py`.

---

## Task 6: Worker `worker-tokens` — `token_analysis.py`

**Full task prompt to send this teammate:**

```
You are working on scripts/analysis/token_analysis.py.
Use ultrathink for all reasoning. Follow strict TDD.
Activate venv first: source env_parbench/bin/activate

Your job is to fix these tech debt items (no other changes):
1. Extract extract_token_lists(results) utility (returns prompt_list, completion_list) — replace 6 sites
2. Extract compute_grouped_stats(records, grouper_fn) — replace 3 identical by-kernel/direction/level blocks
3. Define PRECISION_TOKENS=1, PRECISION_RATE=4, PRECISION_COST_DETAIL=6, PRECISION_CORRELATION=4 constants
4. Define FIELD_PROMPT_TOKENS, FIELD_COMPLETION_TOKENS, FIELD_OVERALL_STATUS, FIELD_SOURCE_SPEC constants
5. Add DEFAULT_TEST_PROMPT_TOKENS=1000, DEFAULT_TEST_COMPLETION_TOKENS=500 constants to the test file
```

- [ ] **Step 1: Run existing tests to record baseline**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_token_analysis.py -v --tb=short
```

- [ ] **Step 2: Write failing tests**

Append to `scripts/analysis/test_token_analysis.py`:

```python
# --- new tests: utility extraction ---

def test_extract_token_lists_basic():
    from scripts.analysis.token_analysis import extract_token_lists
    results = [
        {"prompt_tokens": 100, "completion_tokens": 50},
        {"prompt_tokens": 200, "completion_tokens": 80},
    ]
    prompt, completion = extract_token_lists(results)
    assert prompt == [100, 200]
    assert completion == [50, 80]

def test_extract_token_lists_missing_keys_default_zero():
    from scripts.analysis.token_analysis import extract_token_lists
    results = [{"prompt_tokens": 100}]
    prompt, completion = extract_token_lists(results)
    assert prompt == [100]
    assert completion == [0]

def test_extract_token_lists_empty():
    from scripts.analysis.token_analysis import extract_token_lists
    assert extract_token_lists([]) == ([], [])

def test_precision_constants_exist():
    import scripts.analysis.token_analysis as ta
    assert ta.PRECISION_TOKENS == 1
    assert ta.PRECISION_RATE == 4
    assert ta.PRECISION_COST_DETAIL == 6

def test_field_constants_exist():
    import scripts.analysis.token_analysis as ta
    assert ta.FIELD_PROMPT_TOKENS == "prompt_tokens"
    assert ta.FIELD_OVERALL_STATUS == "overall_status"
```

- [ ] **Step 3: Run new tests — confirm they fail**

```bash
pytest scripts/analysis/test_token_analysis.py::test_extract_token_lists_basic -v
```

Expected: `ImportError`.

- [ ] **Step 4: Add field-name constants and precision constants**

Insert near the top of `token_analysis.py`, after imports:

```python
# Field name constants
FIELD_PROMPT_TOKENS: str = "prompt_tokens"
FIELD_COMPLETION_TOKENS: str = "completion_tokens"
FIELD_OVERALL_STATUS: str = "overall_status"
FIELD_SOURCE_SPEC: str = "source_spec"
FIELD_TARGET_SPEC: str = "target_spec"

# Rounding precision constants
PRECISION_TOKENS: int = 1        # for token count averages
PRECISION_RATE: int = 4          # for pass rates and ratios
PRECISION_COST_DETAIL: int = 6   # for per-task / per-pass costs
PRECISION_CORRELATION: int = 4   # for Spearman correlation
```

Replace every `"prompt_tokens"`, `"completion_tokens"`, `"overall_status"` string literal in the file body with the corresponding constant. Replace `round(..., 1)`, `round(..., 4)`, `round(..., 6)` with the constant names. Grep first:

```bash
grep -n '"prompt_tokens"\|"completion_tokens"\|"overall_status"\|round.*,\s*[146]\b' scripts/analysis/token_analysis.py
```

- [ ] **Step 5: Add `extract_token_lists`**

Insert after the constants:

```python
def extract_token_lists(
    results: list[dict],
) -> tuple[list[int], list[int]]:
    """Return (prompt_token_list, completion_token_list) for a list of result records."""
    return (
        [r.get(FIELD_PROMPT_TOKENS, 0) for r in results],
        [r.get(FIELD_COMPLETION_TOKENS, 0) for r in results],
    )
```

Find all 6 inline token extraction sites and replace with `extract_token_lists(...)`:

```bash
grep -n 'get.*prompt_tokens.*for r in\|get.*completion_tokens.*for r in' scripts/analysis/token_analysis.py
```

- [ ] **Step 6: Add test file constants**

In `test_token_analysis.py`, add at the top (after imports):

```python
DEFAULT_TEST_PROMPT_TOKENS: int = 1000
DEFAULT_TEST_COMPLETION_TOKENS: int = 500
```

Replace any hardcoded `1000` / `500` in the test fixture `_make_result()` with these constants.

- [ ] **Step 7: Run full test suite**

```bash
pytest scripts/analysis/test_token_analysis.py -v --tb=short
```

Expected: All original tests PASS + 5 new tests PASS.

- [ ] **Step 8: Signal critic**

Message `critic`: "worker-tokens done. All tests pass." Provide `git diff scripts/analysis/token_analysis.py scripts/analysis/test_token_analysis.py`.

---

## Task 7: Worker `worker-figures` — `generate_paper_figures.py`

**Full task prompt to send this teammate:**

```
You are working on scripts/evaluation/generate_paper_figures.py.
Use ultrathink for all reasoning. Follow strict TDD.
Activate venv first: source env_parbench/bin/activate

Note: no test file exists yet — you will CREATE scripts/evaluation/test_generate_paper_figures.py.

Your job is to fix these tech debt items (no other changes):
1. Remove unused import: line 34 `import matplotlib.patches as mpatches`
2. Extract aggregate_status_counts(records, group_key) — replace 2 identical aggregation blocks (lines ~984–992, ~1187–1196)
3. Extract create_status_legend(statuses) — replace 4 identical legend creation blocks (lines ~950–956, ~1069–1076, ~1244–1252, ~1338–1343)
4. Define FIGURE_DPI=600, FONT_SIZE_DEFAULT=10, PDF_FONTTYPE=42 constants in setup_rcparams()
5. Move REPO_KERNEL_PAIRS and HECBENCH_FUNNEL_STAGES data inline lists to module-level constants
```

- [ ] **Step 1: Create the test file and write failing tests**

Create `scripts/evaluation/test_generate_paper_figures.py`:

```python
"""Tests for extracted utility functions in generate_paper_figures.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def test_aggregate_status_counts_by_model():
    from scripts.evaluation.generate_paper_figures import aggregate_status_counts
    records = [
        {"model": "claude", "overall_status": "PASS"},
        {"model": "claude", "overall_status": "FAIL"},
        {"model": "gpt", "overall_status": "PASS"},
    ]
    result = aggregate_status_counts(records, "model")
    assert result["claude"]["PASS"] == 1
    assert result["claude"]["FAIL"] == 1
    assert result["gpt"]["PASS"] == 1


def test_aggregate_status_counts_missing_status_defaults_unknown():
    from scripts.evaluation.generate_paper_figures import aggregate_status_counts
    records = [{"model": "m", "overall_status": None}]
    result = aggregate_status_counts(records, "model")
    assert result["m"]["UNKNOWN"] == 1


def test_constants_exist():
    import scripts.evaluation.generate_paper_figures as gpf
    assert gpf.FIGURE_DPI == 600
    assert gpf.PDF_FONTTYPE == 42
    assert isinstance(gpf.REPO_KERNEL_PAIRS, list)
    assert isinstance(gpf.HECBENCH_FUNNEL_STAGES, list)
    assert len(gpf.HECBENCH_FUNNEL_STAGES) == 5


def test_create_status_legend_returns_patches():
    from scripts.evaluation.generate_paper_figures import create_status_legend
    from matplotlib.patches import Patch
    statuses = ["PASS", "BUILD_FAIL"]
    patches = create_status_legend(statuses)
    assert len(patches) == 2
    assert all(isinstance(p, Patch) for p in patches)
```

- [ ] **Step 2: Run new tests — confirm they fail**

```bash
source env_parbench/bin/activate
pytest scripts/evaluation/test_generate_paper_figures.py -v --tb=short
```

Expected: `ImportError` — `aggregate_status_counts`, `create_status_legend` do not exist yet.

- [ ] **Step 3: Remove unused import**

In `generate_paper_figures.py`, find and delete line 34:

```python
import matplotlib.patches as mpatches  # noqa: E402
```

Confirm nothing else references `mpatches`:

```bash
grep -n "mpatches" scripts/evaluation/generate_paper_figures.py
```

Expected: 0 results after deletion.

- [ ] **Step 4: Add module-level constants**

Find `setup_rcparams()` and move the magic values out. Insert at module level near the top (after `OKABE_ITO` or similar constant block):

```python
FIGURE_DPI: int = 600          # IEEE camera-ready resolution
FONT_SIZE_DEFAULT: int = 10
FONT_SIZE_TITLE: int = 11
FONT_SIZE_TICK: int = 9
FONT_SIZE_LEGEND: int = 9
FONT_SIZE_SMALL: int = 8
PDF_FONTTYPE: int = 42         # TrueType (required by ACM/IEEE venues)
```

Replace the hardcoded values inside `setup_rcparams()` with these constants.

Also move the inline data to constants. Read lines ~619–623 and ~708–714 to get the exact values, then add:

```python
REPO_KERNEL_PAIRS: list[tuple[str, int, int]] = [
    ("CUDA–OpenMP", 6, 472),
    ("CUDA–HIP", 3, 633),
    ("CUDA–SYCL", 2, 616),
]

HECBENCH_FUNNEL_STAGES: list[dict] = [
    {"label": "HeCBench kernels total", "count": 506, "exclusion": None},
    {"label": "All 4 API variants\n(CUDA, HIP, SYCL, OMP)", "count": 327, "exclusion": "−179: missing API variants"},
    {"label": "With Makefiles", "count": 325, "exclusion": "−2: no Makefile"},
    {"label": "With self-checking\n(PASS/FAIL/verify patterns)", "count": 242, "exclusion": "−83: no verification"},
    {"label": "Final selected\n(complexity, deps, diversity)", "count": 60, "exclusion": "−182: complexity/deps/diversity"},
]
```

Replace the inline lists at lines ~619–623 and ~708–714 with references to these constants.

**CRITICAL:** Read the actual file at those lines before writing the constants — if the counts differ from the values above, use the values in the file (the file is authoritative).

- [ ] **Step 5: Extract `aggregate_status_counts`**

Read lines ~984–992 and ~1187–1196 to understand the exact aggregation pattern. Then add:

```python
def aggregate_status_counts(
    records: list[dict],
    group_key: str,
) -> dict[str, dict[str, int]]:
    """Aggregate records by group_key field and count by overall_status.

    Returns: {group_value: {status_string: count}}
    """
    from collections import defaultdict
    result: dict[str, dict[str, int]] = {}
    for r in records:
        key = r.get(group_key, "UNKNOWN")
        if key not in result:
            result[key] = defaultdict(int)
        status = r.get("overall_status") or "UNKNOWN"
        result[key][status] += 1
    return result
```

Replace the two aggregation blocks in `generate_f6_taxonomy` and `generate_f8_cross_direction` with calls to this function.

- [ ] **Step 6: Extract `create_status_legend`**

Read the 4 legend blocks to confirm the exact `Patch` constructor arguments. Then add:

```python
def create_status_legend(statuses: list[str]) -> list:
    """Return matplotlib Patch handles for the given status strings.

    Uses STATUS_COLORS and STATUS_ORDER defined in this module.
    """
    from matplotlib.patches import Patch
    return [
        Patch(
            facecolor=STATUS_COLORS[s],
            edgecolor="black",
            linewidth=0.5,
            label=s.replace("_", " "),
        )
        for s in statuses
        if s in STATUS_COLORS
    ]
```

Replace all 4 identical legend creation blocks with calls to `create_status_legend(statuses_in_data)`. Use grep to find all 4:

```bash
grep -n "Patch(facecolor=STATUS_COLORS" scripts/evaluation/generate_paper_figures.py
```

- [ ] **Step 7: Run full test suite**

```bash
pytest scripts/evaluation/test_generate_paper_figures.py -v --tb=short
```

Expected: All 4 new tests PASS.

- [ ] **Step 8: Signal critic**

Message `critic`: "worker-figures done. All tests pass." Provide `git diff scripts/evaluation/generate_paper_figures.py` and the full content of the new `test_generate_paper_figures.py`.

---

## Task 8: Critic Agent Protocol

**Full task prompt for `critic` teammate:**

```
You are the critic agent for a parallel tech debt cleanup. 5 workers will each message you
when done. For each worker, you will review their git diff and test output against the
original tech debt report. Use ultrathink for your reasoning.

For each worker that contacts you, do the following:

REVIEW CRITERIA:
1. Every tech debt item listed for that file is addressed (no skipped items)
2. No behavior changes: utility functions produce identical outputs to the inlined code they replaced
3. All tests referenced in the worker's task pass (run them yourself to confirm)
4. No new magic numbers or strings introduced in the implementation
5. Extracted functions have clear names and a one-line docstring
6. No imports broken (run: python3 -c "import scripts.analysis.<module>" or equivalent)

VERDICT FORMAT:
Issue APPROVE if all criteria are met.
Issue REQUEST_CHANGES with a numbered list of specific required fixes if any criterion fails.
Be precise: cite file:line, describe the exact problem, and state the exact fix required.

DO NOT approve work that:
- Skips any tech debt item from the report
- Changes function signatures or return types of existing public functions
- Breaks any previously passing test
- Introduces a new magic number while removing an old one
- Has utility functions with no docstring

When you issue APPROVE for all 5 workers, message the lead agent: "All 5 workers approved."
```

**Critic review loop protocol (enforced by the lead agent / human orchestrator):**

1. Worker signals critic with `git diff` output.
2. Critic runs the worker's test command (`pytest <file> -v`) to verify tests pass independently.
3. Critic issues APPROVE or REQUEST_CHANGES.
4. If REQUEST_CHANGES: worker reads the feedback, uses ultrathink to plan the correction, applies it, reruns tests, signals critic again.
5. Repeat until APPROVE. Maximum 3 rounds before escalating to human.
6. After APPROVE, worker is shut down.

---

## Task 9: Final Verification and Commit

Run after all 5 workers have received APPROVE from critic.

- [ ] **Step 1: Run the full cross-file test suite**

```bash
source env_parbench/bin/activate
pytest scripts/analysis/test_build_error_taxonomy.py \
       scripts/analysis/test_generate_paper_data.py \
       scripts/analysis/test_statistical_analysis.py \
       scripts/analysis/test_token_analysis.py \
       scripts/evaluation/test_generate_paper_figures.py \
       -v --tb=short 2>&1 | tail -40
```

Expected: All tests PASS (original N + 29 new tests).

- [ ] **Step 2: Import smoke test**

```bash
python3 -c "
import scripts.analysis.build_error_taxonomy
import scripts.analysis.generate_paper_data
import scripts.analysis.statistical_analysis
import scripts.analysis.token_analysis
import scripts.evaluation.generate_paper_figures
print('All imports OK')
"
```

Expected: `All imports OK`.

- [ ] **Step 3: Run /validate**

```
/validate
```

Expected: All 4 waves pass.

- [ ] **Step 4: Commit**

```bash
git add scripts/analysis/build_error_taxonomy.py \
        scripts/analysis/generate_paper_data.py \
        scripts/analysis/statistical_analysis.py \
        scripts/analysis/token_analysis.py \
        scripts/evaluation/generate_paper_figures.py \
        scripts/analysis/test_build_error_taxonomy.py \
        scripts/analysis/test_generate_paper_data.py \
        scripts/analysis/test_statistical_analysis.py \
        scripts/analysis/test_token_analysis.py \
        scripts/evaluation/test_generate_paper_figures.py

git commit -m "$(cat <<'EOF'
refactor: extract utilities and constants across 5 analysis scripts

Tech debt cleanup from 2026-04-01 scan:
- Extract safe_percentage, is_deterministic/is_stochastic, extract_token_lists,
  aggregate_status_counts, create_status_legend as named utility functions
- Define named constants for magic numbers (ALPHA_SIGNIFICANCE, PRECISION_TOKENS,
  MIN_EXPECTED_CELL_COUNT, FIGURE_DPI, MAX_EXAMPLES_PER_CATEGORY, etc.)
- Remove dead code (multi_attempt var, mpatches import, unused pytest/Counter imports)
- Extract _determine_first_attempt_status, _get_direction_pairs helpers
- Collapse duplicate pass@k computation branches
- Add 29 new unit tests for extracted utilities

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Self-Review

**Spec coverage check:**

| Tech Debt Item | Task | Status |
|---------------|------|--------|
| `safe_percentage` (12 sites) | Task 3 | ✓ covered |
| `_accumulate_category_stats` (4 sites) | Task 3 | ✓ covered |
| `MAX_EXAMPLES_PER_CATEGORY`, `OTHER_BUCKET_REFINEMENT_THRESHOLD` | Task 3 | ✓ covered |
| Unused imports in test_build_error_taxonomy.py | Task 3 | ✓ covered |
| `group_and_compute_wilson_ci` | Task 4 | ⚠ simplified to: remove dead `multi_attempt`, collapse pass@k branches, extract `_determine_first_attempt_status` — the grouping helper is higher-risk (3 sites touch core analysis logic); left for follow-up |
| `multi_attempt` dead variable | Task 4 | ✓ covered |
| Pass@k branch collapse | Task 4 | ✓ covered |
| All 7 magic number/constant groups in generate_paper_data.py | Task 4 | ✓ covered |
| `is_deterministic` / `is_stochastic` | Task 5 | ✓ covered |
| Effect size interpretation tables | Task 5 | ✓ covered |
| Statistical threshold constants | Task 5 | ✓ covered |
| `_get_direction_pairs` | Task 5 | ✓ covered |
| `extract_token_lists` | Task 6 | ✓ covered |
| Precision + field-name constants | Task 6 | ✓ covered |
| Test fixture constants | Task 6 | ✓ covered |
| `compute_grouped_stats` | Task 6 | ⚠ deferred — the 3 blocks differ subtly in key extraction (kernel vs direction vs level); aggressive refactor risks regression in a core reporting path. Worker is told about it but it's not in the TDD steps. Add as follow-up task. |
| `mpatches` unused import | Task 7 | ✓ covered |
| `aggregate_status_counts` | Task 7 | ✓ covered |
| `create_status_legend` | Task 7 | ✓ covered |
| Figure constants (DPI, fonts, fonttype) | Task 7 | ✓ covered |
| `REPO_KERNEL_PAIRS`, `HECBENCH_FUNNEL_STAGES` | Task 7 | ✓ covered |

**Deferred (too risky for parallel automated refactor):**
- `group_and_compute_wilson_ci` in `generate_paper_data.py` — touches core analysis; requires manual verification
- `compute_grouped_stats` in `token_analysis.py` — the 3 blocks differ in grouping key; a wrong abstraction silently produces wrong tables
