---
phase: 11-paper-tex-integration
plan: 03
subsystem: paper-tex
tags: [latex, sc26-review, power-analysis, case-studies, discussion-rewrite]

# Dependency graph
requires:
  - phase: 11-paper-tex-integration
    provides: "Plan 01 float migration + Plan 02 narrative verification"
  - phase: 12-sc26-review-fixes
    provides: "Corrected paper.tex with factual accuracy fixes"
provides:
  - "paper.tex S4-S7 updated with all 10 SC26 review items addressed"
  - "MDES power analysis (34.1pp) as honest statistical limitation"
  - "Three VERIFY_FAIL case studies with data-validated failure mechanisms"
  - "S7 Discussion rewritten from 7 subsections to 3 (27% line reduction)"
  - "Threats to Validity updated with power caveats and single-model acknowledgment"
affects: [11-04-PLAN]

# Tech tracking
tech-stack:
  added: []
  patterns: ["P-code traceability comments (% P0-6, % P1-8, etc.) for SC26 review audit trail"]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex

key-decisions:
  - "Case study mechanisms validated against actual result JSONs, not pre-written plan text: cfd=type-system mapping error (not reduction scope), hotspot=thread mapping + missing launch syntax, gaussian=conditional compilation mismatch (not shared memory)"
  - "S7 Implications (S7.7) folded into S7.1 and S7.2 rather than kept as separate subsection, per D-14/D-15 redundancy reduction"
  - "Threats updated from 'two-model' to 'single-model' to reflect current Qwen-only state with pending GPT-4.1 mini"
  - "HeCBench commit hash 22785cd added alongside existing Rodinia 9c10d3ea in version-pinning paragraph"

patterns-established:
  - "SC26 P-code traceability: every new paragraph has % P{X}-{Y}: comment linking to review item"
  - "Data-validated case studies: every failure mechanism claim cross-checked against result JSON before writing"

requirements-completed: [TEX-04, TEX-05, TEX-06, TEX-07]

# Metrics
duration: 6min
completed: 2026-04-06
---

# Phase 11 Plan 03: SC26 Review Items + S7 Discussion Rewrite Summary

**Addressed all 10 SC26 review items (3 full + 7 brief) across S4-S7: MDES 34.1pp power analysis, 3 data-validated VERIFY_FAIL case studies, spectrum reframe, HPC tier grounding, and S7 merged from 7 to 3 subsections with updated Threats to Validity**

## Performance

- **Duration:** 6 min
- **Started:** 2026-04-06T07:32:17Z
- **Completed:** 2026-04-06T07:38:59Z
- **Tasks:** 2/2
- **Files modified:** 1

## Accomplishments
- Implemented 3 full-treatment SC26 review items: P0-6 (MDES power analysis at 34.1pp), P1-8 (3 VERIFY_FAIL case studies), P1-15 (S7 merge from 7 to 3 subsections)
- Implemented 7 brief-treatment SC26 review items: P0-7 (HeCBench commit hash), P1-9 (syntax-vs-reasoning spectrum reframe), P1-11 (HPC tier grounding), P1-14 (XSBench 0% honest acknowledgment), P1-16 (softened Cochran-Armitage), P1-17 (exact eval commands), P1-19 (McNemar power caveat)
- Validated case study failure mechanisms against actual result JSON data (3 files inspected): cfd type-system mapping error, hotspot thread mapping error, gaussian conditional compilation mismatch
- S7 Discussion reduced from 108 lines to 79 lines (27% reduction) while preserving all 8 key claims from original

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement SC26 review items in S4, S5, S6** - `7f5bcd9` (feat)
2. **Task 2: Rewrite S7 Discussion — merge 7 to 3 subsections** - `e047804` (feat)

## Files Created/Modified
- `docs/paper/latex/paper.tex` - S4-S7 updated: MDES power analysis in S6.5, HeCBench hash + eval commands in S5, 3 case studies + spectrum reframe + HPC tier grounding + XSBench 0% in S6, McNemar caveat in S6.6, S7 merged to 3 subsections with updated Threats

## Decisions Made
- Case study mechanisms adjusted from plan pre-written text to match actual result JSON data. Plan described CFD as "reduction scope error" but result JSON shows OpenCL `clBuildProgram` JIT failure from `float3` type redefinition (type-system mapping error). Plan described gaussian as "shared memory synchronization" but result JSON shows `#ifdef TIMING` guards removing verification output (conditional compilation mismatch). These corrections ensure paper claims are data-faithful.
- S7.7 (Implications for HPC Community) was not kept as a separate subsection. Key points were folded into S7.1 (framework extensibility, tractable vs intractable kernels) and S7.2 (targeted interventions, augmentation as standard practice) per D-14/D-15 guidance.
- Threats to Validity "Two-model evaluation" updated to "Single-model evaluation" with \pending{} for GPT-4.1 mini to honestly reflect current state.
- HeCBench commit hash (22785cd) placed in the same version-pinning paragraph as Rodinia (9c10d3ea) for consistency.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected case study failure mechanisms to match actual data**
- **Found during:** Task 1 (P1-8 case study writing)
- **Issue:** Plan pre-wrote CFD case study as "reduction scope error" and gaussian as "shared memory synchronization," but actual result JSONs show different failure mechanisms
- **Fix:** Validated each case study against actual result JSON files; rewrote CFD as type-system mapping error (float3 redefinition), gaussian as conditional compilation mismatch (#ifdef TIMING)
- **Files modified:** docs/paper/latex/paper.tex
- **Verification:** All 3 result JSONs inspected; case study text matches actual error_message and translated_files content
- **Committed in:** 7f5bcd9 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - data accuracy)
**Impact on plan:** Essential for scientific accuracy. Paper claims now match actual data rather than hypothesized mechanisms.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all new text is sourced from paper_data.json, statistical_analysis.json, error_taxonomy.json, and validated result JSONs with provenance comments. Existing \tbd{} and \pending{} macros for GPT-4.1 mini data are pre-existing and out of scope for this plan.

## Next Phase Readiness
- Sections 4-7 now complete with all SC26 review items addressed
- S7 Discussion restructured for reduced redundancy and better flow
- All provenance comments in place for Plan 11-04 cross-section audit
- paper.tex ready for final consistency check (Plan 11-04) and compilation

## Self-Check: PASSED

- Modified file exists: docs/paper/latex/paper.tex (FOUND)
- Task 1 commit 7f5bcd9 verified in git log (FOUND)
- Task 2 commit e047804 verified in git log (FOUND)
- SUMMARY.md exists at expected path (FOUND)

---
*Phase: 11-paper-tex-integration*
*Completed: 2026-04-06*
