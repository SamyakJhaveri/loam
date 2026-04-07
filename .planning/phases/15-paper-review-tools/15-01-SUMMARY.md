---
phase: 15-paper-review-tools
plan: 01
subsystem: paper
tags: [latex, statistics, fisher-test, mcnemar, anonymization, cost-analysis]

# Dependency graph
requires:
  - phase: 14-paper-tex-integration
    provides: "Complete paper.tex with all sections wired"
provides:
  - "Paper with 6 review panel fixes (FIX-2a, FIX-2b, FIX-3, SF-1, SF-3, SF-6)"
  - "Appendix E: Translation Prompt Template"
  - "Appendix F: Evaluation Cost Summary table"
affects: [17-paper-integration, 18-cross-model-verification]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Provenance comments linking LaTeX values to JSON source fields"]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex
    - docs/paper/latex/appendices.tex

key-decisions:
  - "SF-1 cost data placed in appendix table per D-04 (not inline in S5.5)"
  - "FIX-2b: Report omp_target McNemar pair rather than exclude from Bonferroni family"
  - "FIX-2a: Fisher test scoped to all directions (n=192) with scope clarification vs Cochran-Armitage"

patterns-established:
  - "Review panel fix pattern: verify against source data, apply, cross-check acceptance criteria"

requirements-completed: []

# Metrics
duration: 4min
completed: 2026-04-07
---

# Phase 15 Plan 01: Paper Review Panel Fixes Summary

**Applied 6 SC26 review panel fixes: Fisher exact test (S6.4), omp_target McNemar (S6.5), prompt template appendix, cost data appendix table, unbalanced design clarification, absolute self-repair figures**

## Performance

- **Duration:** 4 min
- **Started:** 2026-04-07T06:58:37Z
- **Completed:** 2026-04-07T07:02:17Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Moved SF-1 API cost data from inline paragraph in paper.tex S5.5 to dedicated appendix table in appendices.tex (Evaluation Cost Summary with \label{sec:appendix-cost}), per D-04 decision
- Verified all 5 remaining fixes (FIX-2a, FIX-2b, SF-3, SF-6) from commit 1f835bb are present and correct with values matching source data files
- Verified Appendix E (Translation Prompt Template) system message matches llm_evaluate.py lines 629-637 exactly; anonymization details match lines 578-589
- Confirmed \pending{} macros preserved (22 instances, D-03), augmentation claim language unsoftened (D-02), no excluded items touched (D-06)

## Task Commits

Each task was committed atomically:

1. **Task 1: Apply statistical and editorial fixes to paper.tex (FIX-2a, FIX-2b, SF-1, SF-3, SF-6)** - `a826c5b` (feat)
2. **Task 2: Add translation prompt template as Appendix E (FIX-3)** - verification only, no changes needed (content already correct from 1f835bb)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - Replaced inline cost paragraph with forward-reference to appendix
- `docs/paper/latex/appendices.tex` - Added Evaluation Cost Summary section with cost table ($145.37, 120.6M tokens, 7 days, $0.13/task)

## Decisions Made
- **SF-1 cost data placement (D-04):** Plan specified moving cost data to appendix table rather than keeping inline. Commit 1f835bb had left it inline; this plan execution corrected it by adding the appendix table and replacing inline content with a forward-reference.
- **FIX-2b approach:** Reported the omp_target McNemar pair (h=-1.37, p=0.0625, corrected p=0.25) alongside the other 3 pairs rather than excluding it from the Bonferroni family, per R3-STATS recommendation.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] SF-1 cost data was inline instead of in appendix table**
- **Found during:** Task 1 verification
- **Issue:** Commit 1f835bb placed cost data as inline paragraph in paper.tex line 663 rather than as appendix table per D-04 decision
- **Fix:** Added \section{Evaluation Cost Summary} with \label{sec:appendix-cost} and 4-row table to appendices.tex; replaced inline paragraph in paper.tex with forward-reference sentence
- **Files modified:** docs/paper/latex/paper.tex, docs/paper/latex/appendices.tex
- **Verification:** grep confirms 145.37 in appendices.tex, appendix-cost ref in paper.tex, no "4{,}600 API requests" inline
- **Committed in:** a826c5b

---

**Total deviations:** 1 auto-fixed (1 bug fix)
**Impact on plan:** SF-1 fix was partially applied; correction aligns implementation with D-04 specification. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 6 review panel fixes are now applied and verified
- Paper.tex ready for Phase 15 Plan 02 (additional review items if any)
- All statistical values traced to source data files (statistical_analysis.json, token_analysis.json)

## Self-Check: PASSED

- docs/paper/latex/paper.tex: FOUND
- docs/paper/latex/appendices.tex: FOUND
- 15-01-SUMMARY.md: FOUND
- commit a826c5b: FOUND

---
*Phase: 15-paper-review-tools*
*Completed: 2026-04-07*
