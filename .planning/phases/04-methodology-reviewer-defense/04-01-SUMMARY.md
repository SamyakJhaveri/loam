---
phase: 04-methodology-reviewer-defense
plan: 01
subsystem: paper
tags: [latex, methodology, reviewer-defense, kernel-isolation, verification]

# Dependency graph
requires:
  - phase: 09-objective-quantitative-analysis
    provides: quantitative_findings.json with all-suite BUILD_FAIL and VERIFY_FAIL counts
  - phase: 02-benchmark-characterization-data
    provides: sloc_analysis.json with kernels_above_pareval_threshold
provides:
  - Kernel isolation defense paragraph in Section 3.4 with three-layer evidence
  - Conjunction verification defense paragraph in Section 3.2 with named VERIFY_FAIL example
affects: [04-02, 11-paper-tex-integration]

# Tech tracking
tech-stack:
  added: []
  patterns: [provenance-comment-per-number, analytical-framing-not-rebuttal]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex

key-decisions:
  - "Used LaTeX non-breaking spaces (~) for all number-of-N patterns to prevent line breaks mid-statistic"
  - "Placed provenance comments as LaTeX % comments immediately above the paragraph they annotate"
  - "Used 'orthogonal competencies' as the conceptual anchor per D-02, with analytical framing throughout"
  - "Selected gaussian OpenCL-to-CUDA as VERIFY_FAIL example per 04-RESEARCH.md verification"

patterns-established:
  - "Provenance comments cite quantitative_findings.json field paths for all new methodology numbers"
  - "Analytical framing: 'We isolate X because Y' not 'One might argue X, but Y'"

requirements-completed: [METHOD-01, METHOD-04]

# Metrics
duration: 2min
completed: 2026-04-05
---

# Phase 4 Plan 01: Methodology Defense Paragraphs Summary

**Kernel isolation defense (3-layer evidence) and conjunction verification defense (gaussian VERIFY_FAIL example) inserted into paper.tex Sections 3.4 and 3.2**

## Performance

- **Duration:** 2 min
- **Started:** 2026-04-05T09:00:51Z
- **Completed:** 2026-04-05T09:03:17Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Inserted kernel isolation rationale paragraph at top of Section 3.4 with three-layer evidence: XSBench 0% vs ParBench 64.2%, 31/35 SLoC threshold, 33.9% BUILD_FAIL rate
- Inserted conjunction verification defense paragraph at end of Section 3.2 with named gaussian VERIFY_FAIL example, 7.3% rate (51/700), and compilation-only alternative cite
- All new numbers have LaTeX provenance comments citing quantitative_findings.json and sloc_analysis.json field paths

## Task Commits

Each task was committed atomically:

1. **Task 1: Write kernel isolation defense paragraph at top of Section 3.4** - `945268a` (feat)
2. **Task 2: Write conjunction verification defense paragraph at end of Section 3.2** - `f89b5da` (feat)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - Added kernel isolation defense paragraph (Section 3.4, before existing "Kernel-centric methodology" paragraph) and conjunction verification defense paragraph (Section 3.2, after failure classification paragraph)

## Decisions Made
- Used LaTeX non-breaking spaces (`~`) for all number-of-N patterns (e.g., `51~of~700`, `31~of~35`) to prevent awkward line breaks mid-statistic
- Placed provenance comments as LaTeX `%` comments immediately above the paragraph they annotate, with explicit field paths (e.g., `campaign_1.failure_taxonomy.status_counts.BUILD_FAIL = 237/700 = 33.9%`)
- Used analytical framing throughout ("We isolate...because..." not "One might argue...")
- Selected gaussian (OpenCL-to-CUDA, L0) as the VERIFY_FAIL example because it demonstrates all three layers: compiles, runs with exit_code=0, produces partial output but missing expected "Total:" summary, and all 3 self-repair attempts fail identically

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Plan 04-02 (statistical test justification and reproducibility pins) can proceed -- these modify different sections (5.4 and 5.5) than what was touched here
- Sections 3.2 and 3.4 now have reviewer-defense paragraphs that preempt the two most likely SC-level methodology objections

## Self-Check: PASSED

- docs/paper/latex/paper.tex: FOUND
- 04-01-SUMMARY.md: FOUND
- Commit 945268a (Task 1): FOUND
- Commit f89b5da (Task 2): FOUND
- "orthogonal competencies" in paper.tex: FOUND
- "Verification methodology" in paper.tex: FOUND

---
*Phase: 04-methodology-reviewer-defense*
*Completed: 2026-04-05*
