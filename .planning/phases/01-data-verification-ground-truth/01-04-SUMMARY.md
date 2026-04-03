---
phase: 01-data-verification-ground-truth
plan: 04
subsystem: paper-verification
tags: [latex, statistics, mcnemar, bonferroni, cochran-armitage, pass-at-k, direction-analysis]

# Dependency graph
requires:
  - phase: none
    provides: paper_data.json with by_direction, passk_campaign, direction_asymmetry sections
provides:
  - Verified S6.6-S6.8 + S7 Discussion with 38 source comments and 1 inline fix
  - All direction rates, pass@k, statistical tests, and discussion claims confirmed against paper_data.json
affects: [01-05, paper-final-review]

# Tech tracking
tech-stack:
  added: []
  patterns: [source-comment-traceability]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex

key-decisions:
  - "Fixed OpenCL/OMP gap from 17.4 to 17.3 pp (exact: 17.333... rounds down at 1dp)"
  - "Confirmed Bonferroni alpha=0.0167 (0.05/3 for 3 McNemar tests) is correct for paper scope, despite statistical_analysis.json using 0.0125 (4 tests incl. omp_target)"
  - "All S7 Discussion data claims trace back to S6 tables with zero new unverified claims"

patterns-established:
  - "Source comment pattern: % src: paper_data.json > section > field: exact values with rounding notes"

requirements-completed: [VERIFY-01]

# Metrics
duration: 3min
completed: 2026-04-03
---

# Phase 01 Plan 04: Verify S6.6-S6.8 + S7 Discussion Summary

**Verified direction rates, pass@k, McNemar/Bonferroni stats, and Discussion consistency with 38 source comments and 1 rounding fix (17.4->17.3 pp)**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-03T22:00:14Z
- **Completed:** 2026-04-03T22:04:09Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Verified tab:direction-rates (6 rows, task sum 80+80+75+75+85+85=480, all L0 and all-levels rates match paper_data.json)
- Verified McNemar values: p=0.625/0.688/0.727, n=16/17/15, h=0.26/0.31/0.27 (all match paper_data.json direction_asymmetry with correct rounding)
- Verified tab:pass-at-k: 103 hard fail + 0 noisy + 17 always pass + 22 partial = 142, percentages 72.5%/15.5%/12.0% all confirmed
- Verified Bonferroni alpha=0.0167 = 0.05/3 (3 McNemar tests, correct for primary 3-direction scope)
- Verified tab:stats-summary internal consistency with S6.5 (Cochran-Armitage) and S6.6 (McNemar)
- Verified S7 Discussion: all numerical claims trace to S6 tables, zero new unverified data claims found
- Fixed one rounding error: OpenCL/OMP gap 17.4->17.3 pp (exact: (35/75-22/75)*100=17.333... rounds to 17.3 at 1dp)
- Added 38 source comments with paper_data.json cross-references across S6.6-S6.8 and S7

## Task Commits

Each task was committed atomically:

1. **Task 1: Verify direction rates, pass@k, stats summary, and S7 Discussion** - `c6a41c6` (feat)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - S6.6-S6.8 and S7 verified with 38 source comments; 1 rounding fix (17.4->17.3 pp)

## Decisions Made
- Fixed OpenCL/OMP gap from 17.4 to 17.3 pp: exact computation (35/75 - 22/75)*100 = 17.333... rounds to 17.3, not 17.4
- Confirmed Bonferroni alpha=0.0167 is correct for paper's 3-direction scope, even though statistical_analysis.json uses 0.0125 (4 tests including omp_target). The paper excludes omp_target from primary analysis.
- Augmentation L3 rate: paper says 56.3%, actual is 9/16=56.25%. Both round to 56.3% at 1dp -- no fix needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed OpenCL/OMP direction gap rounding error**
- **Found during:** Task 1 (S7 Discussion verification, Step 4)
- **Issue:** Paper claimed "17.4 points for OpenCL/OpenMP" but exact computation (35/75 - 22/75)*100 = 17.333... rounds to 17.3 at 1dp
- **Fix:** Changed "17.4" to "17.3" in the Direction Asymmetry discussion paragraph
- **Files modified:** docs/paper/latex/paper.tex
- **Verification:** python3 -c "print(round((35/75-22/75)*100, 1))" outputs 17.3
- **Committed in:** c6a41c6

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Minor rounding correction for statistical accuracy. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all data in S6.6-S6.8 and S7 is verified against paper_data.json.

## Next Phase Readiness
- S6.6-S6.8 and S7 fully verified with source traceability
- Plan 01-05 can proceed to verify any remaining sections
- All statistical test values confirmed exact for SC peer review

---
*Phase: 01-data-verification-ground-truth*
*Completed: 2026-04-03*
