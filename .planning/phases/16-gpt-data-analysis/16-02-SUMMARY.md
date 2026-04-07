---
phase: 16-gpt-data-analysis
plan: 02
subsystem: analysis
tags: [gpt-4.1-mini, t2-table, schema-gate, generate-paper-figures, dual-model]

# Dependency graph
requires:
  - phase: 16-01
    provides: paper_data_gpt41mini.json and eval_summary.json with GPT data
provides:
  - generate_t2_model_table() computes GPT row dynamically from records
  - T3b schema gate validated -- paper_data_gpt41mini.json matches paper_data.json schema
  - F3 heatmap stale 'data pending' annotation removed
affects: [16-03-PLAN, 16-04-PLAN, 17-paper-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [dynamic GPT row computation mirroring Qwen row pattern in T2 table]

key-files:
  created: []
  modified:
    - scripts/generate_paper_figures.py

key-decisions:
  - "GPT row in T2 table uses same dynamic filter pattern as Qwen (filter by model substring)"

patterns-established:
  - "T2 model table rows computed dynamically from records, never hardcoded"

requirements-completed: [T3b, T5-prep]

# Metrics
duration: 1min
completed: 2026-04-07
---

# Phase 16 Plan 02: T2 Table Fix and Schema Gate Summary

**Fixed GPT 'pending' hardcoding in generate_t2_model_table() with dynamic computation, removed stale F3 annotation, and validated T3b schema gate (7 common directions, matching field names)**

## Performance

- **Duration:** 1 min 17 sec
- **Started:** 2026-04-07T19:44:03Z
- **Completed:** 2026-04-07T19:45:20Z
- **Tasks:** 2/2
- **Files modified:** 1

## Accomplishments
- Replaced hardcoded GPT "pending" row in generate_t2_model_table() with dynamic computation that mirrors the Qwen row logic (filter by model substring, compute per-direction pass/total stats)
- Removed stale "GPT-4.1 mini: data pending" annotation from F3 kernel-model heatmap
- Validated T3b schema gate: paper_data_gpt41mini.json and paper_data.json share 7 common directions, matching pass_rate/ci_lower/ci_upper/by_status field names

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix generate_t2_model_table() to compute GPT stats dynamically** - `3bbca1f` (fix)
2. **Task 2: Schema gate -- validate paper_data_gpt41mini.json (T3b)** - validation-only, no commit needed

## Files Created/Modified
- `scripts/generate_paper_figures.py` - Replaced hardcoded GPT pending row with dynamic computation; removed stale F3 data pending annotation; added GPT verbose output

## Decisions Made
- GPT row uses same dynamic filter pattern as Qwen: `[r for r in std_records if "gpt" in r["model"].lower()]`
- F3 heatmap annotation removed entirely (GPT data now included in heatmap rendering)

## Deviations from Plan

None - plan executed exactly as written.

## Schema Gate Results (T3b)

| Check | Result |
|-------|--------|
| GPT pass_rate is float | 0.2922 |
| GPT total > 0 | 551 |
| GPT pass > 0 | 161 |
| ci_lower/ci_upper present | Yes |
| by_status present | Yes (BUILD_FAIL, PASS, VERIFY_FAIL, RUN_FAIL) |
| Common directions | 7 (all 6 standard + cuda-to-omp_target) |
| GPT-only directions | None |
| Qwen-only directions | omp_target-to-cuda |
| Both have by_kernel | Yes (31 kernels each) |
| Field name match | pass_rate in all by_direction entries |

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- generate_paper_figures.py ready for Plan 04 `--figure all` regeneration (T2 table will have real GPT data)
- paper_data_gpt41mini.json schema validated for Plan 03 cross_model_comparison.py consumption
- Both paper_data files share matching field names and structure for identical processing

## Self-Check: PASSED

All files verified present on disk. Task 1 commit (3bbca1f) verified in git log. Task 2 was validation-only (no commit).

---
*Phase: 16-gpt-data-analysis*
*Completed: 2026-04-07*
