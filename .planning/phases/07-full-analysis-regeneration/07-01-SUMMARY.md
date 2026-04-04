---
phase: 07-full-analysis-regeneration
plan: 01
subsystem: analysis
tags: [eval-summary, paper-data, error-taxonomy, selfrepair, statistical-analysis, wilson-ci]

# Dependency graph
requires:
  - phase: 02-benchmark-characterization-data
    provides: benchmark_characterization.json, sloc_analysis.json (unchanged, not regenerated)
provides:
  - eval_summary.json with 1136-task Qwen aggregate (31.3% pass rate)
  - paper_data_rodinia.json preserving 480-task Rodinia scope for Sections 6.1-6.5
  - paper_data.json with 710 primary tasks across all 5 suites (38.3% pass rate)
  - error_taxonomy.json with 1248 results classified across 12 BUILD_FAIL subcategories
  - selfrepair_analysis.json with 1248 results and 117 full repairs
  - statistical_analysis.json with Wilson CIs for 1136 post-exclusion results
affects: [08-figure-regeneration, 09-objective-quantitative-analysis, 10-qualitative-analysis, 11-paper-tex-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [dual-scope paper_data generation (Rodinia-only + full-dataset)]

key-files:
  created:
    - results/analysis/paper_data_rodinia.json
  modified:
    - results/evaluation/eval_summary.json
    - results/evaluation/eval_summary.md
    - results/analysis/paper_data.json
    - results/analysis/error_taxonomy.json
    - results/analysis/error_taxonomy.md
    - results/analysis/statistical_analysis.json
    - results/analysis/statistical_analysis.md

key-decisions:
  - "paper_data.json scope changed from Rodinia-only to full-dataset (710 primary tasks); Rodinia scope preserved in paper_data_rodinia.json"
  - "selfrepair_analysis output was already current (identical content after regeneration) -- no git diff produced"

patterns-established:
  - "Dual paper_data pattern: paper_data_rodinia.json for Sections 6.1-6.5 (480 primary), paper_data.json for cross-suite (710 primary)"
  - "KNOWN_FAIL exclusion produces 1136 from 1248 disk files (112 excluded involving 6 Rodinia KNOWN_FAIL specs)"

requirements-completed: [REGEN-01, REGEN-02, REGEN-03, REGEN-04, REGEN-05]

# Metrics
duration: 2min
completed: 2026-04-04
---

# Phase 7 Plan 01: Core Analysis Regeneration Summary

**Regenerated 5 analysis outputs (eval summary, dual paper data, error taxonomy, self-repair, statistical) covering complete 1,248-file Qwen dataset across 5 suites**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-04T20:33:56Z
- **Completed:** 2026-04-04T20:36:19Z
- **Tasks:** 2
- **Files modified:** 8 (1 created, 7 modified)

## Accomplishments
- eval_summary.json updated from 907 to 1,136 tasks (31.3% pass rate, 356 PASS)
- paper_data_rodinia.json created to preserve 480-task Rodinia scope (36.2% pass rate) before paper_data.json was overwritten with full-dataset
- paper_data.json now covers 710 primary tasks across all 5 suites (38.3% pass rate)
- error_taxonomy.json covers all 1,248 results with 892 failures classified into 12 BUILD_FAIL, 7 RUN_FAIL, 2 EXTRACTION_FAIL, and 3 VERIFY_FAIL subcategories
- statistical_analysis.json includes Wilson CIs for 7 non-Rodinia kernels (convolution1d, floydwarshall, mixbench, rsbench, scan, xsbench, and more)
- Cross-suite coverage verified: 7 non-Rodinia kernels present in all three analysis outputs (error_taxonomy, selfrepair, statistical)

## Task Commits

Each task was committed atomically:

1. **Task 1: Run eval summary and paper data generation** - `f4b9283` (feat)
2. **Task 2: Run error taxonomy, self-repair, and statistical analysis** - `12ed8c6` (feat)

## Files Created/Modified
- `results/evaluation/eval_summary.json` - Aggregate eval summary: 1136 tasks, 356 PASS (31.3%)
- `results/evaluation/eval_summary.md` - Human-readable eval summary companion
- `results/analysis/paper_data_rodinia.json` - NEW: Rodinia-only 480-task paper data for Sections 6.1-6.5
- `results/analysis/paper_data.json` - Full 710-task cross-suite paper data (was Rodinia-only, now all suites)
- `results/analysis/error_taxonomy.json` - Failure mode taxonomy: 1248 results, 892 failures classified
- `results/analysis/error_taxonomy.md` - Human-readable error taxonomy
- `results/analysis/statistical_analysis.json` - Wilson CIs, Cochran-Armitage, direction asymmetry for 1136 results
- `results/analysis/statistical_analysis.md` - Human-readable statistical analysis

## Decisions Made
- paper_data.json was overwritten from Rodinia-only (480 primary) to full-dataset (710 primary). The Rodinia scope was preserved in the new paper_data_rodinia.json file BEFORE the overwrite, following the plan's critical ordering.
- selfrepair_analysis.json and .md were already current (Apr 3 data was complete at 1248 results). Script re-ran successfully but produced identical output, so no git diff was generated.

## Deviations from Plan

None - plan executed exactly as written.

## Key Data Points (for downstream phases)

| Metric | Value | Source |
|--------|-------|--------|
| Disk result files | 1,248 | find results/evaluation/together-qwen-3.5-397b-a17b/ |
| Post-exclusion tasks | 1,136 | eval_summary.json |
| Rodinia primary tasks | 480 | paper_data_rodinia.json |
| Full primary tasks | 710 | paper_data.json |
| Overall pass rate | 31.3% [28.7%, 34.1%] | statistical_analysis.json |
| Rodinia pass rate | 36.2% [32.1%, 40.6%] | paper_data_rodinia.json |
| Full pass rate | 38.3% [34.8%, 41.9%] | paper_data.json |
| Total failures classified | 892 | error_taxonomy.json |
| Self-repair full repairs | 117 | selfrepair_analysis.json |
| Non-Rodinia kernel count | 7 | All analysis outputs |
| Cochran-Armitage (full) | z=-0.0, p=1.0 | statistical_analysis.json |

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 5 core analysis files regenerated and verified with cross-suite coverage
- Phase 8 (figure regeneration) can proceed using these updated data files
- Phase 9 (objective quantitative analysis) has all data inputs ready
- paper_data_rodinia.json preserves backward compatibility for existing Section 6.1-6.5 references

## Self-Check: PASSED

- All 10 output files exist on disk
- Commit f4b9283 (Task 1) verified in git log
- Commit 12ed8c6 (Task 2) verified in git log
- All REGEN-01 through REGEN-05 verification assertions passed

---
*Phase: 07-full-analysis-regeneration*
*Completed: 2026-04-04*
