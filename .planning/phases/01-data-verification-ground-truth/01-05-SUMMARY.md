---
phase: 01-data-verification-ground-truth
plan: 05
subsystem: analysis
tags: [paper_data, statistical_analysis, figures, regeneration, scope_filter]

# Dependency graph
requires:
  - phase: 01-01
    provides: Verified paper numerical claims
  - phase: 01-02
    provides: Verified spec/manifest counts
  - phase: 01-03
    provides: Verified Section 6 numbers
  - phase: 01-04
    provides: Verified augmentation/self-repair data
provides:
  - Freshly regenerated paper_data.json (480 Rodinia primary tasks, 36.2% pass rate)
  - Freshly regenerated statistical_analysis.json
  - Freshly regenerated selfrepair_analysis.json
  - All 10 paper figure PDFs regenerated (F2-F7, C1-C4)
  - Suite filter on generate_paper_data.py for scope control
affects: [phase-02, phase-03, phase-04, phase-05]

# Tech tracking
tech-stack:
  added: []
  patterns: [suite-filter-flag for analysis scope control]

key-files:
  created: []
  modified:
    - results/analysis/paper_data.json
    - results/analysis/statistical_analysis.json
    - results/analysis/selfrepair_analysis.json
    - scripts/analysis/generate_paper_data.py
    - scripts/analysis/test_generate_paper_data.py
    - docs/paper/figures/ (10 PDFs + PNGs)

key-decisions:
  - "Added --suite filter to generate_paper_data.py to scope primary campaign to Rodinia (480 tasks) after discovering 230 new non-Rodinia results would change pass rate from 36.2% to 38.3%"
  - "Updated test expectations: pass@k campaign 288 tasks (Rodinia-only) vs previous 426 (all-suite)"

patterns-established:
  - "Suite filtering: always pass --suite rodinia when regenerating paper_data.json for the frozen 480-task primary campaign"

requirements-completed: [VERIFY-06]

# Metrics
duration: 8min
completed: 2026-04-03
---

# Phase 1 Plan 5: Analysis Regeneration Summary

**Regenerated all analysis files and 10 paper figures with new --suite rodinia scope filter; pass rate 36.2% confirmed matching Wave 1 verified value**

## Performance

- **Duration:** 8 min
- **Started:** 2026-04-03T22:53:13Z
- **Completed:** 2026-04-03T23:01:19Z
- **Tasks:** 1
- **Files modified:** 20

## Accomplishments
- Added `--suite` filter flag to `generate_paper_data.py` to control analysis scope (critical: 230 new non-Rodinia results would have changed pass rate from 36.2% to 38.3%)
- Regenerated paper_data.json: 480 tasks, 174 PASS, 36.2% [32.1%, 40.6%] -- matches Wave 1 verified values exactly
- Regenerated statistical_analysis.json (1136 records), selfrepair_analysis.json (1248 records)
- Regenerated all 10 paper figure PDFs and PNGs (F2-F7, C1-C4, T2)
- Updated tests: 59 total tests pass (29 paper_data + 13 statistical + 17 taxonomy)

## Task Commits

Each task was committed atomically:

1. **Task 1: Pre-check scope filter, regenerate all analysis files + figures, validate** - `57a34d8` (feat)

## Files Created/Modified
- `scripts/analysis/generate_paper_data.py` - Added --suite filter flag for scope control
- `scripts/analysis/test_generate_paper_data.py` - Updated pass@k expected values for Rodinia-only scope (288 vs 426)
- `results/analysis/paper_data.json` - Freshly regenerated (480 tasks, 36.2% pass rate)
- `results/analysis/statistical_analysis.json` - Freshly regenerated from 1136 records
- `results/analysis/selfrepair_analysis.json` - Freshly regenerated from 1248 records
- `docs/paper/figures/*.pdf` - 10 figure PDFs regenerated (F2-F7, C1-C4)
- `docs/paper/figures/*.png` - Companion PNG files for figures

## Decisions Made

1. **Added --suite filter to generate_paper_data.py**: The script had no suite filtering and would process all 1248 result files (710 primary after KNOWN_FAIL exclusion). With 230 new non-Rodinia results from tmux runs, the overall pass rate would shift from 36.2% to 38.3%. Adding `--suite rodinia` preserves the frozen 480-task primary campaign scope for paper data integrity.

2. **Updated pass@k test expectations**: With the Rodinia suite filter, pass@k campaign is 288 tasks (down from 426 all-suite). Updated 3 test assertions: passk_campaign count (288 vs 426), pass@1 macro avg (0.153 vs 0.197), pass@3 macro avg (0.229 vs 0.275).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added --suite flag to generate_paper_data.py**
- **Found during:** Task 1 (scope pre-check)
- **Issue:** Script had no suite filter. With 230 new non-Rodinia result files (hecbench, xsbench, rsbench, mixbench), running the script would produce 710 primary tasks at 38.3% pass rate instead of the verified 480 tasks at 36.2%
- **Fix:** Added `--suite` CLI argument that filters records by source_spec prefix. Records `suite_filter` in output JSON.
- **Files modified:** scripts/analysis/generate_paper_data.py
- **Verification:** Regenerated with `--suite rodinia` produces 480 tasks, 174 PASS, 0.3625 pass rate
- **Committed in:** 57a34d8

**2. [Rule 1 - Bug] Updated stale test expectations for pass@k campaign**
- **Found during:** Task 1 (test suite run after regeneration)
- **Issue:** 3 tests expected 426 pass@k tasks (all-suite count), but Rodinia-only scope produces 288. Test assertions for pass@1 and pass@3 macro averages also changed.
- **Fix:** Updated test_campaign_totals (426->288), test_passk_estimates (0.197->0.153, 0.275->0.229), test_passk_total_samples (426->288)
- **Files modified:** scripts/analysis/test_generate_paper_data.py
- **Verification:** All 29 tests pass
- **Committed in:** 57a34d8

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug fix)
**Impact on plan:** Both auto-fixes necessary for correctness. The suite filter is essential infrastructure for the frozen primary campaign scope. No scope creep.

## Issues Encountered
None beyond the scope filter issue (documented as deviation above).

## User Setup Required
None - no external service configuration required.

## Known Stubs
None -- all data is live, no placeholder values.

## Next Phase Readiness
- All analysis files freshly regenerated -- downstream phases (2-5) can consume current data
- paper_data.json scope locked to Rodinia via --suite flag
- Cochran-Armitage: z=-0.17, p=0.87 (augmentation null result confirmed)
- Self-repair: 90 repaired, 5 regressions, 84 first-attempt PASS (confirmed)
- All 10 paper figures ready for LaTeX inclusion

## Self-Check: PASSED

All artifacts verified:
- results/analysis/paper_data.json: FOUND
- results/analysis/statistical_analysis.json: FOUND
- results/analysis/selfrepair_analysis.json: FOUND
- docs/paper/figures/f2_repo_vs_kernel.pdf: FOUND
- docs/paper/figures/f7_augmentation_robustness.pdf: FOUND
- Commit 57a34d8: FOUND

---
*Phase: 01-data-verification-ground-truth*
*Completed: 2026-04-03*
