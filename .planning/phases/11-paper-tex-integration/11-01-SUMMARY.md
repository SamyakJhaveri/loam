---
phase: 11-paper-tex-integration
plan: 01
subsystem: paper-tex
tags: [latex, ieee, appendix, float-migration, page-reduction]

# Dependency graph
requires:
  - phase: 12-sc26-review-fixes
    provides: "Corrected paper.tex with factual accuracy fixes"
provides:
  - "paper.tex with 7 main-text floats and ref pointers to appendix"
  - "appendices.tex Appendix D with 17 migrated floats plus full per-kernel table"
  - "Condensed per-kernel table (top-5 + bottom-5) in main text"
  - "Inline methodology key facts in Section 5 prose"
affects: [11-02-PLAN, 11-03-PLAN, 11-04-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns: ["appendix-float-migration with ref-pointer traceability"]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex
    - docs/paper/latex/appendices.tex

key-decisions:
  - "Top-5 hardest kernels selected as gaussian/heartwall/myocyte/rsbench/xsbench (all 0%) rather than including tied kernels"
  - "Suite-summary inline facts placed in S4 (Benchmark Curation) where the table was originally located rather than S5"
  - "Used 35 unique kernels (corpus size) not 31 (eval count) in suite-summary inline text for consistency with existing paper usage"

patterns-established:
  - "Float-to-appendix migration: comment marker + ref pointer sentence at removal site"
  - "Appendix D organized by original section with section-comment separators"

requirements-completed: [TEX-05, D-01, D-02, D-03, D-04, D-05, D-07]

# Metrics
duration: 6min
completed: 2026-04-06
---

# Phase 11 Plan 01: Float Migration Summary

**Migrated 17 floats from paper.tex to appendices.tex Appendix D, condensed per-kernel table to top-5/bottom-5, and inlined methodology key facts into S5 prose -- reducing main text from 24 floats to 7**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-06T07:05:51Z
- **Completed:** 2026-04-06T07:11:48Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- Migrated 17 floats from paper.tex to new Appendix D in appendices.tex, preserving all labels unchanged
- Created condensed 10-row per-kernel table (top-5 easiest + top-5 hardest) with full 31-row version in appendix
- Inlined essential methodology facts (GPU model RTX 4070/sm_89, CUDA 12.3, GCC 12.4, Qwen 3.5 397B, 5 suites/35 kernels/96 specs) into Section 5 prose with provenance comments
- All 35 cross-references in paper.tex resolve to labels in either paper.tex or appendices.tex (verified)
- Zero duplicate labels across both files (109 unique labels verified)

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Appendix D and migrate 17 floats** - `b41af18` (feat)
2. **Task 2: Condense per-kernel table to top-5 + bottom-5** - `007d451` (feat)
3. **Task 3: Inline methodology key facts into S5 prose** - `7f3e898` (feat)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - Main text reduced from 24 to 7 floats; ref pointers inserted; condensed per-kernel table; inline S5 key facts
- `docs/paper/latex/appendices.tex` - New Appendix D section with 18 floats (17 migrated + 1 full per-kernel table)

## Decisions Made
- Top-5 hardest kernels: Selected gaussian, heartwall, myocyte, rsbench, xsbench (all at 0.0% pass rate). Five additional kernels also at 0% (convolution1d, dwt2d) were not included to keep the table at exactly 5+5 rows; they have smaller sample sizes (n=10 vs n=30).
- Suite-summary inline text placed in S4 (Benchmark Curation) rather than S5 because that is where tab:suite-summary was originally located and where the ref pointer was inserted.
- Used "35 unique kernels" (corpus size) rather than "31 evaluated kernels" in the suite-summary inline text for consistency with existing paper terminology; the distinction between corpus and evaluation set is explained in S6.3.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all data is sourced from paper_data.json with provenance comments. No \tbd{} markers were introduced by this plan (existing \tbd{} markers for GPT-4.1 mini data are pre-existing and out of scope).

## Next Phase Readiness
- paper.tex now has 7 main-text floats, ready for prose-compression work in subsequent plans
- All ref pointers in place for cross-reference integrity
- Appendix D structure established for any additional float migrations
- Condensed per-kernel table references full appendix version for reviewer access

## Self-Check: PASSED

- All 2 modified files exist on disk
- All 3 task commits verified in git log (b41af18, 007d451, 7f3e898)
- SUMMARY.md exists at expected path

---
*Phase: 11-paper-tex-integration*
*Completed: 2026-04-06*
