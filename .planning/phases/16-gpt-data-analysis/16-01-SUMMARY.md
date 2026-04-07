---
phase: 16-gpt-data-analysis
plan: 01
subsystem: analysis
tags: [gpt-4.1-mini, eval-summary, paper-data, error-taxonomy, dual-model]

# Dependency graph
requires:
  - phase: 15.5-pre-work
    provides: GPT-4.1 mini evaluation results in results/evaluation/azure-gpt-4.1-mini/
provides:
  - eval_summary.json refreshed with both azure-gpt-4.1-mini and together-qwen-3.5-397b-a17b
  - paper_data_gpt41mini.json with GPT primary campaign statistics (29.2% pass rate)
  - error_taxonomy.json with dual-model per_model breakdown
affects: [16-02-PLAN, 16-03-PLAN, 16-04-PLAN, 17-paper-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [dynamic model name derivation from results_dir.name in generate_paper_data.py]

key-files:
  created:
    - results/analysis/paper_data_gpt41mini.json
  modified:
    - results/evaluation/eval_summary.json
    - results/evaluation/eval_summary.md
    - results/analysis/error_taxonomy.json
    - results/analysis/error_taxonomy.md
    - scripts/analysis/generate_paper_data.py

key-decisions:
  - "Fixed hardcoded model name in generate_paper_data.py to derive from results_dir.name"

patterns-established:
  - "generate_paper_data.py model field is now dynamic, supporting any model directory name"

requirements-completed: [T1, T2, T3]

# Metrics
duration: 2min
completed: 2026-04-07
---

# Phase 16 Plan 01: GPT Data Artifact Generation Summary

**Generated three dual-model analysis artifacts: eval_summary.json (1951 tasks, 2 models), paper_data_gpt41mini.json (551 primary tasks, 29.2% pass rate), and error_taxonomy.json (2145 results, both models in per_model)**

## Performance

- **Duration:** 2 min 21 sec
- **Started:** 2026-04-07T19:39:34Z
- **Completed:** 2026-04-07T19:41:55Z
- **Tasks:** 3/3
- **Files modified:** 6

## Accomplishments
- Refreshed eval_summary.json with both azure-gpt-4.1-mini (815 tasks, 27.2% pass) and together-qwen-3.5-397b-a17b (1136 tasks, 31.3% pass)
- Generated paper_data_gpt41mini.json with full primary campaign statistics: 551 tasks, 29.2% pass rate, 7 directions, 31 kernels, Wilson CIs, Cochran-Armitage trend test
- Refreshed error_taxonomy.json with both models in per_model dict: GPT total=897, Qwen total=1248, 1567 classified failures

## Task Commits

Each task was committed atomically:

1. **Task 1: Refresh eval_summary.json with both models** - `0a9e631` (feat)
2. **Task 2: Generate paper_data_gpt41mini.json** - `6c35a22` (feat)
3. **Task 3: Refresh error_taxonomy.json with both models** - `e83792a` (feat)

## Files Created/Modified
- `results/evaluation/eval_summary.json` - Dual-model evaluation summary (1951 records)
- `results/evaluation/eval_summary.md` - Human-readable summary markdown
- `results/analysis/paper_data_gpt41mini.json` - GPT-4.1 mini primary campaign data for paper tables
- `results/analysis/error_taxonomy.json` - Combined dual-model error taxonomy (2145 results)
- `results/analysis/error_taxonomy.md` - Human-readable error taxonomy markdown
- `scripts/analysis/generate_paper_data.py` - Fixed hardcoded model name to use results_dir.name

## Decisions Made
- Fixed hardcoded model name bug in generate_paper_data.py: was always "together-qwen-3.5-397b-a17b" regardless of --results-dir. Changed to derive from results_dir.name for correctness.
- Regenerated Qwen paper_data.json to use the same dynamic model derivation (no data change, only metadata field).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed hardcoded model name in generate_paper_data.py**
- **Found during:** Task 2 (Generate paper_data_gpt41mini.json)
- **Issue:** Line 1222 of generate_paper_data.py had `"model": "together-qwen-3.5-397b-a17b"` hardcoded, causing GPT output to have wrong model field
- **Fix:** Changed to `"model": results_dir.name` to derive model name from the results directory
- **Files modified:** scripts/analysis/generate_paper_data.py
- **Verification:** paper_data_gpt41mini.json now has model="azure-gpt-4.1-mini"; Qwen paper_data.json still has model="together-qwen-3.5-397b-a17b"
- **Committed in:** 6c35a22 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** Essential bug fix for correctness. Without this, the model field would be wrong in paper_data_gpt41mini.json, which would propagate to cross_model_comparison.py (Plan 03) and paper tables.

## Key Metrics

| Model | Total Tasks | PASS | Pass Rate |
|-------|------------|------|-----------|
| azure-gpt-4.1-mini | 815 | 222 | 27.2% |
| together-qwen-3.5-397b-a17b | 1136 | 356 | 31.3% |

GPT primary campaign (L0, non-sample): 551 tasks, 161 PASS, 29.2% pass rate [25.6%, 33.1% Wilson CI]

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All three prerequisite artifacts for Plan 02 (table/section generation), Plan 03 (cross-model comparison), and Plan 04 (figure regeneration) are now available
- paper_data_gpt41mini.json ready for cross_model_comparison.py consumption
- error_taxonomy.json has both models for comparative error analysis
- eval_summary.json has both models for aggregate reporting

## Self-Check: PASSED

All 5 artifact files verified present on disk. All 3 task commits verified in git log.

---
*Phase: 16-gpt-data-analysis*
*Completed: 2026-04-07*
