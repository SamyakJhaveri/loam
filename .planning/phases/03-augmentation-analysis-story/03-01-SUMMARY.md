---
phase: 03-augmentation-analysis-story
plan: 01
subsystem: analysis
tags: [augmentation, matrix, wilson-ci, pattern-classification, eval-results]

# Dependency graph
requires:
  - phase: 02-benchmark-characterization-data
    provides: "benchmark_characterization.py monolithic script pattern"
provides:
  - "augmentation_per_kernel_matrix.json: 26-kernel cuda-to-omp L0-L4 matrix with pattern classification"
  - "augmentation_per_kernel_matrix.md: human-readable summary with tables"
  - "augmentation_analysis.py: reusable augmentation analysis script"
  - "test_augmentation_analysis.py: 10 validation tests for matrix structure and patterns"
affects: [03-augmentation-analysis-story, paper-tex-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Wilson CI inline re-implementation (no scipy dependency for analysis scripts)", "Pattern classification: stable_pass/stable_fail/degradation/improvement/other"]

key-files:
  created:
    - scripts/analysis/augmentation_analysis.py
    - scripts/analysis/test_augmentation_analysis.py
    - results/analysis/augmentation_per_kernel_matrix.json
    - results/analysis/augmentation_per_kernel_matrix.md
  modified: []

key-decisions:
  - "Wilson CI re-implemented inline to avoid scipy import complexity in analysis scripts"
  - "stable_fail requires ALL levels to be the same non-PASS status; mixed non-PASS is 'other' (myocyte)"
  - "Direction derived from source_spec/target_spec JSON fields, not filename parsing (more reliable)"
  - "omp_target filtered via _extract_api() checking suffix before omp to avoid substring collision"

patterns-established:
  - "Pattern classification: 5-category system (stable_pass, stable_fail, degradation, improvement, other)"
  - "Secondary matrix: per-direction aggregates with Wilson CIs for all 8 translation directions"

requirements-completed: [AUG-01, AUG-02]

# Metrics
duration: 3min
completed: 2026-04-04
---

# Phase 3 Plan 1: Augmentation Analysis Matrix Summary

**Per-kernel augmentation matrix with 26 cuda-to-omp kernels across L0-L4, pattern classification (11 stable, 5 fail, 5 degradation, 4 improvement, 1 other), Wilson CIs, and 8-direction secondary matrix**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-04T18:52:17Z
- **Completed:** 2026-04-04T18:55:38Z
- **Tasks:** 1
- **Files created:** 4

## Accomplishments
- Built augmentation_analysis.py (458 lines) that reads raw Qwen eval result JSONs and produces the complete per-kernel x per-level status matrix
- Pattern classification identifies 5 degradation kernels (backprop, hotspot3d, lavamd, lud, scan) and 4 improvement kernels (bptree, mixbench, nn, streamcluster) as motivating examples for AUG-02
- Wilson 95% CIs computed for all aggregate pass rates (L0: 61.5% [42.5%, 77.6%])
- Secondary matrix covers all 8 translation directions with per-direction per-level aggregates
- 10 tests independently validate matrix structure, kernel counts, raw data matching, and pattern classification

## Task Commits

Each task was committed atomically:

1. **Task 1: Create test scaffold and augmentation analysis script** - `d84b30e` (feat)

## Files Created/Modified
- `scripts/analysis/augmentation_analysis.py` - Complete augmentation matrix computation from raw eval result JSONs (458 lines)
- `scripts/analysis/test_augmentation_analysis.py` - 10 validation tests for matrix structure, kernel count, status values, and pattern classification (196 lines)
- `results/analysis/augmentation_per_kernel_matrix.json` - Primary and secondary augmentation matrices with aggregates and pattern summary
- `results/analysis/augmentation_per_kernel_matrix.md` - Markdown summary with per-kernel table, pattern summary, aggregate pass rates, exceptions, and secondary directions

## Decisions Made
- Wilson CI re-implemented inline using Abramowitz-Stegun approximation for the inverse normal CDF, avoiding scipy dependency while maintaining accuracy within 4.5e-4 of exact values
- stable_fail classification requires all levels to have the same non-PASS status (e.g., all BUILD_FAIL); myocyte (mix of BUILD_FAIL and VERIFY_FAIL) correctly classified as "other" per research document expectations
- API extraction from spec names checks for "omp_target" suffix before "omp" to prevent substring collision
- Result JSON source_spec/target_spec fields used as authoritative source for direction determination, not filename parsing

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- augmentation_per_kernel_matrix.json is ready for Plan 02 (figure generation) and Plan 03 (LASSI positioning)
- Pattern summary data directly feeds into augmentation story narrative for paper.tex
- Backprop degradation root cause documented in exceptions list

## Self-Check: PASSED

All 4 created files verified on disk. Commit d84b30e verified in git log.

---
*Phase: 03-augmentation-analysis-story*
*Completed: 2026-04-04*
