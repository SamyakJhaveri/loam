---
phase: 16-gpt-data-analysis
plan: 03
subsystem: analysis
tags: [cross-model, chi-squared, cohens-h, gpt-4.1-mini, qwen, statistical-comparison]

# Dependency graph
requires:
  - phase: 16-01
    provides: paper_data.json (Qwen) and paper_data_gpt41mini.json (GPT) primary campaign data
  - phase: 16-02
    provides: T3b schema gate validation confirming matching field names and 7 common directions
provides:
  - cross_model_comparison.json with chi-squared, Cohen's h, per-direction, per-kernel matrix
  - cross_model_comparison.py reusable script for regeneration
affects: [16-04-PLAN, 17-paper-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [scipy.stats.chi2_contingency for 2x2 contingency, Cohen's h with arcsine transform, four-way kernel agreement matrix]

key-files:
  created:
    - scripts/analysis/cross_model_comparison.py
    - scripts/analysis/test_cross_model_comparison.py
    - results/analysis/cross_model_comparison.json
  modified: []

key-decisions:
  - "Kernel passes for a model if pass > 0 in by_kernel (any-passing threshold)"
  - "Chi-squared uses overall totals (710 Qwen vs 551 GPT) not common-direction-only"

patterns-established:
  - "Four-way kernel agreement: both_pass, both_fail, qwen_only_pass, gpt_only_pass"
  - "Cohen's h thresholds: <0.2 negligible, <0.5 small, <0.8 medium, >=0.8 large"

requirements-completed: [T4]

# Metrics
duration: 2min
completed: 2026-04-07
---

# Phase 16 Plan 03: Cross-Model Statistical Comparison Summary

**Chi-squared test (p=0.0009) and Cohen's h effect sizes for Qwen vs GPT across 7 directions and 31 kernels with four-way agreement matrix**

## Performance

- **Duration:** 2 min 11 sec
- **Started:** 2026-04-07T19:47:05Z
- **Completed:** 2026-04-07T19:49:16Z
- **Tasks:** 1/1
- **Files modified:** 3

## Accomplishments
- Created cross_model_comparison.py (274 lines) with TDD: 9 tests RED then GREEN
- Chi-squared test: chi2=10.97, p=0.000926 -- statistically significant difference between models
- Cohen's h = 0.19 (negligible effect size) -- despite significance, practical difference is small
- Per-kernel agreement: 13 both_pass, 5 both_fail, 11 qwen_only_pass, 2 gpt_only_pass out of 31 common kernels
- Per-direction analysis reveals cuda-to-omp_target as largest divergence (h=0.86, large effect: Qwen 17.5% vs GPT 0.0%)

## Task Commits

Each task was committed atomically:

1. **Task 1 (TDD RED): Failing tests for cross_model_comparison.py** - `301ed81` (test)
2. **Task 1 (TDD GREEN): Implement cross_model_comparison.py + produce JSON** - `2c4085a` (feat)

## Files Created/Modified
- `scripts/analysis/cross_model_comparison.py` - Cross-model statistical comparison script (274 lines)
- `scripts/analysis/test_cross_model_comparison.py` - TDD test suite (9 tests covering cohens_h, classify_effect_size, build_comparison)
- `results/analysis/cross_model_comparison.json` - Statistical comparison output for Section 6.9

## Decisions Made
- Kernel "passes" if pass > 0 in by_kernel (simplest threshold capturing whether a model can translate a kernel at all)
- Chi-squared test uses overall primary campaign totals (Qwen 710, GPT 551) rather than restricting to common-direction-only counts, because the overall comparison is the headline statistic
- Cohen's h threshold categories follow standard conventions: negligible (<0.2), small (<0.5), medium (<0.8), large (>=0.8)

## Deviations from Plan

None - plan executed exactly as written.

## Key Statistical Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-squared chi2 | 10.9704 | Significant at alpha=0.05 |
| Chi-squared p-value | 0.000926 | Reject null hypothesis of equal rates |
| Cohen's h (overall) | 0.1926 | Negligible practical effect size |
| Common directions | 7 | GPT missing omp_target-to-cuda |
| Both-pass kernels | 13/31 | 42% agreement on passing kernels |
| Qwen-only-pass | 11/31 | 35% kernels only Qwen can translate |
| GPT-only-pass | 2/31 | 6% kernels only GPT can translate |

### Per-Direction Effect Sizes

| Direction | Qwen Rate | GPT Rate | Cohen's h | Effect |
|-----------|-----------|----------|-----------|--------|
| cuda-to-omp | 64.2% | 40.0% | 0.4887 | small |
| cuda-to-omp_target | 17.5% | 0.0% | 0.8632 | large |
| cuda-to-opencl | 20.0% | 30.0% | -0.2320 | small |
| omp-to-cuda | 52.5% | 17.9% | 0.7482 | medium |
| omp-to-opencl | 27.8% | 33.3% | -0.1206 | negligible |
| opencl-to-cuda | 6.0% | 3.7% | 0.1078 | negligible |
| opencl-to-omp | 38.9% | 41.1% | -0.0453 | negligible |

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- cross_model_comparison.json is the HARD GATE artifact for Phase 17B (Section 6.9)
- All data needed for Section 6.9 narrative is now available: chi-squared significance, effect sizes, per-kernel agreement
- Plan 04 (figure regeneration) can proceed with all dual-model data artifacts in place
- Key narrative: statistically significant but negligible practical effect -- models differ more in direction-specific strengths than overall capability

## Self-Check: PASSED

All 3 artifact files verified present on disk. Both task commits verified in git log.

---
*Phase: 16-gpt-data-analysis*
*Completed: 2026-04-07*
