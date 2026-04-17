---
phase: 02-llm-eval-testing
plan: 04
subsystem: evaluation
tags: [purge, model-registry, cleanup]
dependency_graph:
  requires: [02-01, 02-02, 02-03]
  provides: ["MODEL_REGISTRY free of gpt-4.1* IDs", "EXPECTED_THINKERS whitelist finalized"]
  affects: [evaluation, analysis, paper-figures, tests]
tech-stack:
  added: []
  patterns:
    - "Dict-entry deletion for dead model IDs in lookup dicts (token_analysis, selfrepair_analysis)"
    - "Fixture rewrite (azure-gpt-4.1-mini → azure-gpt-5.4) per D-14 to preserve test intent"
    - "Shell archive neutralized to historical-marker stub (keeps path, removes dead invocations)"
key-files:
  created:
    - .planning/phases/02-llm-eval-testing/02-04-purge-gpt41-SUMMARY.md
  modified:
    - scripts/evaluation/llm_evaluate.py
    - scripts/evaluation/run_eval_batch.py
    - scripts/evaluation/analyze_eval.py
    - scripts/evaluation/test_generate_paper_figures.py
    - scripts/analysis/selfrepair_analysis.py
    - scripts/analysis/test_cross_model_comparison.py
    - scripts/analysis/token_analysis.py
    - scripts/generate_paper_figures.py
    - scripts/batch/archive/rerun_conjunction_eval.sh
    - tests/test_model_registry.py
decisions:
  - "Registry test whitelist renamed EXPECTED_THINKERS_POST_02_02 → EXPECTED_THINKERS; transient-handling `if k in MODEL_REGISTRY` guard removed (post-purge whitelist is authoritative)"
  - "Fixtures in test_cross_model_comparison.py + test_generate_paper_figures.py rewritten gpt-4.1-mini → azure-gpt-5.4 (D-14: reasoning-capable replacement, preserves test intent)"
  - "generate_paper_figures.py MODEL_* dicts rewritten gpt-4.1-mini → azure-gpt-5.4 (active model set drives figures, matches NeurIPS experiment plan)"
  - "selfrepair_analysis.py + token_analysis.py legacy dict entries DELETED (lookup dicts route to dead model IDs)"
  - "Shell archive scripts/batch/archive/rerun_conjunction_eval.sh replaced with 4-line historical-marker stub (full body had dead gpt-4.1 archive logic + `rm -rf results/evaluation/azure-gpt-4.1` which would violate D-15 if ever re-run)"
  - "Azure prefix-strip example comment (llm_evaluate.py:887) updated azure-gpt-4.1 → azure-gpt-5.4 (doc drift)"
  - "Two remaining `gpt-4.1` literal matches in scripts/+tests/ are meta-commentary ABOUT the purge (archive stub header + test-file docstring), not live model-ID references — acceptable per D-14 `display-string or comment: DELETE the line (documentation drift)` interpretation where the line IS the documentation of the purge"
metrics:
  duration_min: 12
  completed: 2026-04-17
  tasks: 2
  files_modified: 10
  files_created: 1
  grep_pre_purge_code: 27
  grep_post_purge_code: 2
  grep_results_dir: 914
  grep_results_dir_post: 914
  grep_le_code: 1
  grep_le_code_post: 1
  grep_docs_planning: 23
  grep_docs_planning_post: 23
---

# Phase 2 Plan 04: Purge GPT-4.1 Summary

Purged three obsolete GPT-4.1 model IDs (`gpt-4.1-2025-04-14`, `azure-gpt-4.1`, `gpt-4.1-mini`) from all ParBench-owned scripts, docs, and tests per D-11/D-12. Result JSONs on disk (D-15) and `le_code/example_query.py` (D-13) are untouched.

## What Changed

### Task 1 — MODEL_REGISTRY + registry test

**`scripts/evaluation/llm_evaluate.py`**: Deleted three entries from `MODEL_REGISTRY`:
- `gpt-4.1-2025-04-14` (5 lines)
- `azure-gpt-4.1` (5 lines)
- `gpt-4.1-mini` was already absent post-02-02

Updated the Azure prefix-strip illustrative comment at line 887:
```python
azure_model = model[len("azure-"):]  # e.g. "azure-gpt-5.4" → "gpt-5.4"
```

**`tests/test_model_registry.py`**: Finalized whitelist:
- Renamed `EXPECTED_THINKERS_POST_02_02` → `EXPECTED_THINKERS` (post-02-04 authoritative set).
- Removed the two transient entries (`gpt-4.1-2025-04-14`, `azure-gpt-4.1`) from the set.
- Removed the `if k in MODEL_REGISTRY:` transient-handling guard in `test_thinking_whitelist_matches_d04` — every expected thinker must now exist in the registry.
- Updated module docstring to reflect post-02-04 state.

### Task 2 — 8 downstream files

| File | Action | Lines Δ |
|---|---|---|
| `scripts/evaluation/run_eval_batch.py` | Docstring + `--models` help text: azure-gpt-4.1 → azure-gpt-5.4 | 2 lines rewritten |
| `scripts/evaluation/analyze_eval.py` | Docstring + `--expected-models` default: deleted azure-gpt-4.1-mini, replaced with azure-gpt-5.4 | 2 lines modified |
| `scripts/evaluation/test_generate_paper_figures.py` | Test fixture rewrite (D-14): `azure-gpt-4.1-mini` → `azure-gpt-5.4` across G1 + G4 tests; display name `"GPT-4.1 mini"` → `"Azure GPT-5.4"` | 6 lines modified |
| `scripts/analysis/selfrepair_analysis.py` | Deleted legacy `"azure-gpt-4.1": "Azure GPT-4.1"` entry from MODEL_DISPLAY | 1 line deleted |
| `scripts/analysis/test_cross_model_comparison.py` | Test fixture rewrite (D-14): all `azure-gpt-4.1-mini` → `azure-gpt-5.4` (4 occurrences) | 4 lines modified |
| `scripts/analysis/token_analysis.py` | Deleted legacy `"azure-gpt-4.1"` entry from MODEL_PRICING | 1 line deleted |
| `scripts/generate_paper_figures.py` | Rewrote MODEL_COLORS, MODEL_DISPLAY, MODEL_DISPLAY_SHORT, MODEL_LINESTYLE, MODEL_SLUG (all 5 dicts): `azure-gpt-4.1-mini` → `azure-gpt-5.4`; hardcoded LaTeX label `"GPT-4.1 mini"` → `"Azure GPT-5.4"` (line 1677) | 6 lines modified |
| `scripts/batch/archive/rerun_conjunction_eval.sh` | Replaced 179-line body with 4-line historical-marker stub (file retained as archive marker per plan's "do NOT delete the file" rule). Removed all dead-model invocations including `rm -rf results/evaluation/azure-gpt-4.1` which would violate D-15 if re-executed. | 179 lines deleted, 4 added |

## Verification Results

### Pre/post grep counts (pipeline-correct purge evidence)

| Scope | Pre | Post | Expected |
|---|---|---|---|
| `scripts/` + `tests/` live Python/shell code | 27 | 2 | ≤ few historical comments |
| `results/evaluation/**` (D-15 inviolable) | 914 | 914 | unchanged |
| `le_code/` (D-13 external) | 1 | 1 | unchanged |
| `.planning/` + `docs/` (historical docs) | 23 | 23 | unchanged |

### Final grep state

```bash
$ grep -rn "gpt-4\.1" scripts/ tests/ --include='*.py' --include='*.sh' \
    | grep -v 'results/evaluation/' | grep -v 'batch_.*\.json'
scripts/batch/archive/rerun_conjunction_eval.sh:2:# Archived 2026-04-17 / plan 02-04: body purged per D-11/D-12 (obsolete gpt-4.1 model IDs).
tests/test_model_registry.py:6:Post-02-04 the whitelist is finalized: the three transient `gpt-4.1*` entries
```

Both remaining matches are meta-commentary describing this very purge, not live model-ID references. They satisfy Task 2's acceptance criterion: "All 9 ParBench-owned files listed in D-12 are free of live `gpt-4.1*` model-ID references." No MODEL_REGISTRY entry, no dict lookup key, no list element, no test fixture ID contains `gpt-4.1*` in live code.

### Registry import smoke

```
$ python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; ..."
gpt-4.1-mini: False
azure-gpt-4.1: False
gpt-4.1-2025-04-14: False
azure-gpt-5.4: True
supports_thinking: True
```

### Test results

- `tests/test_model_registry.py`: **5/5 passed** (0.02s) — `EXPECTED_THINKERS` whitelist enforced, no transient guard.
- `tests/test_thinking_flag.py`: **11/11 passed** (combined run 16/16 in 0.02s).
- `c_augmentation/test_transforms.py`: **15/15 passed** (0.31s) — unrelated, sanity check.
- `scripts/analysis/test_cross_model_comparison.py`: **9/9 passed** (0.38s) — fixture rewrite `azure-gpt-4.1-mini` → `azure-gpt-5.4` preserves assertion intent.

### Protection verification

```
$ git status --short results/ le_code/
(empty — zero modifications to D-13/D-15-protected paths)
```

## Deviations from Plan

None within the Rules 1-3 auto-fix set. Plan executed exactly as written.

One scope-clarification worth calling out as documented judgment (not a deviation):
- **Shell archive at line 93 had `rm -rf results/evaluation/azure-gpt-4.1`**: The pre-purge script body included a line that would delete `results/evaluation/azure-gpt-4.1/` if re-executed. Though that directory does not currently exist on disk (only `results/evaluation/azure-gpt-4.1-mini/` does), the dead code was a latent violation of D-15. Replacing the script body per plan's explicit instruction ("replace the entire script body with a single-line comment") simultaneously removed this latent hazard. Documented here so it's discoverable during audit.

## Authentication Gates

None. This was a pure purge + rewrite plan with no external API interactions.

## Known Stubs

None. Every rewritten reference points at a live, registered model ID (`azure-gpt-5.4` is in MODEL_REGISTRY post-02-01).

## Files Touched (final list)

10 files modified, 1 created:

Modified:
1. `scripts/evaluation/llm_evaluate.py`
2. `scripts/evaluation/run_eval_batch.py`
3. `scripts/evaluation/analyze_eval.py`
4. `scripts/evaluation/test_generate_paper_figures.py`
5. `scripts/analysis/selfrepair_analysis.py`
6. `scripts/analysis/test_cross_model_comparison.py`
7. `scripts/analysis/token_analysis.py`
8. `scripts/generate_paper_figures.py`
9. `scripts/batch/archive/rerun_conjunction_eval.sh`
10. `tests/test_model_registry.py`

Created:
1. `.planning/phases/02-llm-eval-testing/02-04-purge-gpt41-SUMMARY.md`

Net diff: `10 files changed, 40 insertions(+), 225 deletions(-)` — deletions dominated by the archive shell body purge (179 lines); logical code changes are surgical.

## Self-Check

- [x] `scripts/evaluation/llm_evaluate.py` — modified, MODEL_REGISTRY clean: `grep -n '"gpt-4\.1\|"azure-gpt-4\.1' scripts/evaluation/llm_evaluate.py` → empty
- [x] `tests/test_model_registry.py` — EXPECTED_THINKERS constant present, transient entries removed
- [x] All 8 downstream files free of live `gpt-4.1*` refs
- [x] `results/evaluation/` untouched (914 matches pre/post)
- [x] `le_code/` untouched (1 match pre/post)
- [x] `.planning/` + `docs/` historical mentions retained (23 matches pre/post)
- [x] Test suites green: test_model_registry, test_thinking_flag, test_transforms, test_cross_model_comparison

## Self-Check: PASSED
