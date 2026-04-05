---
phase: 04-methodology-reviewer-defense
plan: 02
subsystem: paper
tags: [latex, methodology, statistics, mcnemar, bonferroni, reproducibility, version-pins]

# Dependency graph
requires:
  - phase: 04-methodology-reviewer-defense
    plan: 01
    provides: Sections 3.2 and 3.4 methodology defense paragraphs (kernel isolation, conjunction verification)
  - phase: 09-objective-quantitative-analysis
    provides: quantitative_findings.json with alpha_corrected=0.0125 across 4 McNemar tests
provides:
  - Rewritten statistical test justification in Section 5.4 with McNemar, Wilson, Cochran-Armitage and rejected alternatives
  - Bonferroni alpha updated from 0.0167 to 0.0125 across all paper locations (6+ occurrences)
  - Reproducibility version pins paragraph in Section 5.5 (commit hash, submodule pin, API dates, data availability)
affects: [11-paper-tex-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [rejected-alternative-justification, version-pin-paragraph, bonferroni-consistency]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex

key-decisions:
  - "Omitted Wilson1927 cite (not in references.bib) -- text says 'Wilson score 95% confidence intervals' without citation"
  - "Used double-blind footnote for repository URL ('Repository URL withheld for double-blind review') since SC26 is double-blind and repo URL contains author name"
  - "Used current HEAD commit hash (c1d8c7b) for ParBench version pin per plan instructions"
  - "Extended (not replaced) methodological notes paragraph with Bonferroni correction explanation sentence"

patterns-established:
  - "Rejected-alternative pattern: each statistical test names the preferred test AND the rejected alternative with reason"
  - "Version pin paragraph: factual 3-sentence block with provenance comment citing git rev-parse and git submodule status"

requirements-completed: [METHOD-02, METHOD-03]

# Metrics
duration: 3min
completed: 2026-04-05
---

# Phase 4 Plan 02: Statistical Test Justification + Reproducibility Pins Summary

**McNemar's exact test rewrite with rejected alternatives for all 3 statistical tests, Bonferroni alpha corrected to 0.0125 across 6+ locations, and reproducibility version pins (commit, submodule, API dates, 1,248 result JSONs) in Section 5.5**

## Performance

- **Duration:** 3 min
- **Started:** 2026-04-05T09:06:52Z
- **Completed:** 2026-04-05T09:10:40Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Rewrote Section 5.4 statistical test sentence: replaced Fisher's exact test with McNemar's exact test, added rejected alternative for each of 3 tests (Wald vs Wilson, unpaired chi-squared vs McNemar, unordered chi-squared vs Cochran-Armitage)
- Updated Bonferroni alpha from 0.0167 (3 tests) to 0.0125 (4 tests including omp_target pair) in all 6+ locations: Section 6.6 prose and source comment, Section 6.8 table cells x3 and source comment, methodological notes extension
- Added reproducibility version pin paragraph in Section 5.5: ParBench commit c1d8c7b, Rodinia submodule 9c10d3ea, Together AI API March-April 2026, 1,248 result JSONs data availability

## Task Commits

Each task was committed atomically:

1. **Task 1: Rewrite statistical test justification + update Bonferroni alpha (METHOD-02)** - `c1d8c7b` (feat)
2. **Task 2: Add reproducibility version pins after hardware table (METHOD-03)** - `379bee0` (feat)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - Statistical test rewrite in Section 5.4, Bonferroni updates in Sections 6.6 and 6.8, reproducibility pins in Section 5.5

## Decisions Made
- Omitted `\cite{Wilson1927}` because `Wilson1927` does not exist in `references.bib`; text describes Wilson score CIs without citation
- Used double-blind footnote for repository URL since SC26 uses double-blind review and the GitHub URL contains the author's name
- Used `c1d8c7b` (current HEAD at execution time) for the ParBench commit pin, per plan instructions
- Extended the existing methodological notes paragraph (did not replace it) with the Bonferroni correction sentence

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Verification Results

Post-edit verification (all PASS):
- `grep -c "Fisher"` = 0 (zero Fisher remnants)
- `grep -c "0.0167"` = 0 (zero old Bonferroni alpha remnants)
- `grep -c "McNemar"` = 11 (correctly named test throughout)
- `grep -c "0.0125"` = 7 (new Bonferroni alpha in all locations)
- `grep -c "9c10d3ea"` = 2 (Rodinia submodule pin)
- `grep -n "orthogonal competencies"` = line 368, Section 3.4 (Plan 01 intact)
- `grep -n "Verification methodology"` = line 314, Section 3.2 (Plan 01 intact)

## Next Phase Readiness
- All four METHOD requirements now complete: METHOD-01 (Plan 01 Task 1), METHOD-02 (Plan 02 Task 1), METHOD-03 (Plan 02 Task 2), METHOD-04 (Plan 01 Task 2)
- Phase 04 methodology defense is complete -- paper Sections 3.2, 3.4, 5.4, 5.5, 6.6, and 6.8 all updated
- Phase 11 (paper TeX integration) can proceed with methodology sections stable

## Self-Check: PASSED

- docs/paper/latex/paper.tex: FOUND
- 04-02-SUMMARY.md: FOUND
- Commit c1d8c7b (Task 1): FOUND
- Commit 379bee0 (Task 2): FOUND
- "McNemar" in paper.tex: 11 occurrences FOUND
- "0.0125" in paper.tex: 7 occurrences FOUND
- Zero "Fisher" in paper.tex: CONFIRMED
- Zero "0.0167" in paper.tex: CONFIRMED
- "9c10d3ea" in paper.tex: FOUND
- "Bonferroni correction divides" in paper.tex: FOUND

---
*Phase: 04-methodology-reviewer-defense*
*Completed: 2026-04-05*
