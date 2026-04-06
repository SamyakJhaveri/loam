---
phase: 13-paper-figure-table-wiring
plan: 01
subsystem: paper
tags: [latex, paper.tex, figure-wiring, architecture-diagram, cross-references]

# Dependency graph
requires:
  - phase: 11-paper-tex-integration
    provides: "paper.tex with all sections integrated"
provides:
  - "Architecture diagram (Figure 1) wired with PNG includegraphics"
  - "F3 caption updated to match single-panel 29-kernel heatmap"
  - "aug_heatmap appendix cross-reference inserted"
  - "F6 cross-reference updated from fig:xsbench to fig:cross-suite"
  - "All drawio TODO comments removed from paper.tex"
affects: [13-02-PLAN, paper-compilation]

# Tech tracking
tech-stack:
  added: []
  patterns: ["bottom-to-top line editing to prevent drift"]

key-files:
  created: []
  modified:
    - docs/paper/latex/paper.tex

key-decisions:
  - "Used PNG format for architecture diagram instead of PDF (user-approved override; drawio export produced PNG not PDF)"

patterns-established:
  - "Figure wiring edits applied bottom-to-top to prevent line-number drift across multiple edits"

requirements-completed: [AUG-04]

# Metrics
duration: 1min
completed: 2026-04-06
---

# Phase 13 Plan 01: Paper Figure Wiring Summary

**5 figure wiring edits applied to paper.tex: architecture diagram PNG, F3 caption update, aug_heatmap reference, F6 cross-suite label, and drawio TODO removal**

## Performance

- **Duration:** 1 min
- **Started:** 2026-04-06T20:26:11Z
- **Completed:** 2026-04-06T20:27:15Z
- **Tasks:** 2 (1 pre-condition check, 1 multi-edit task)
- **Files modified:** 1

## Accomplishments
- Architecture diagram (Figure 1) now displays exported PNG via `\includegraphics` instead of `\fbox` placeholder
- F3 caption updated from stale "Triple-panel" to "Per-kernel pass/fail heatmap across 6 standard translation directions (29 kernels, L0, Qwen 3.5)"
- Augmentation heatmap appendix reference inserted (`\ref{fig:aug-heatmap}`)
- F6 cross-reference corrected from `fig:xsbench` to `fig:cross-suite`
- Both TODO comments about drawio export removed (top-of-file line 5 and architecture figure block)

## Task Commits

Each task was committed atomically:

1. **Task 1: Pre-condition check** - No commit (verification only, PNG confirmed present)
2. **Task 2: Apply all 5 paper.tex figure wiring edits** - `484c92f` (feat)

**Plan metadata:** [pending final commit]

## Files Created/Modified
- `docs/paper/latex/paper.tex` - 5 figure wiring corrections: architecture includegraphics, F3 caption, aug_heatmap ref, cross-suite ref, TODO removal

## Decisions Made
- Used PNG format (`parbench_architecture.png`) instead of PDF for the architecture diagram. The user confirmed the PNG exists and approved direct use, bypassing the plan's PDF requirement (D-12/D-13 originally specified PDF export from drawio).

## Deviations from Plan

### Auto-fixed Issues

**1. [User Override] Architecture diagram uses PNG instead of PDF**
- **Found during:** Task 1 (pre-condition check)
- **Issue:** Plan required `parbench_architecture.pdf` but user exported as PNG instead
- **Fix:** Used `\includegraphics[width=\textwidth]{parbench_architecture.png}` per user's explicit override instruction
- **Files modified:** docs/paper/latex/paper.tex
- **Verification:** `grep -nP '^\s*\\includegraphics.*parbench_architecture' docs/paper/latex/paper.tex` returns exactly 1 match with `.png`
- **Committed in:** 484c92f

---

**Total deviations:** 1 (user-approved format change from PDF to PNG)
**Impact on plan:** Minimal -- PNG is equally valid for pdflatex compilation. No functional difference.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Known Stubs
None -- all figure references point to existing files or cross-file labels.

## Next Phase Readiness
- paper.tex figure wiring complete for all 5 edits in scope
- Ready for Plan 13-02 (table wiring edits) to proceed
- LaTeX compilation will require the PNG file to be in `docs/paper/latex/figures/` (confirmed present)

---
*Phase: 13-paper-figure-table-wiring*
*Completed: 2026-04-06*
