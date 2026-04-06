---
phase: 13-paper-figure-table-wiring
plan: 02
subsystem: paper
tags: [latex, appendices.tex, figure-wiring, file-cleanup, survey-placeholders]

# Dependency graph
requires:
  - phase: 13-paper-figure-table-wiring
    plan: 01
    provides: "paper.tex figure wiring edits (F6 cross-ref, aug_heatmap ref, architecture diagram)"
provides:
  - "aug_heatmap figure block wired into appendices.tex after F7"
  - "F6 updated to cross-suite comparison (new filename, caption, label)"
  - "Three survey placeholder figure blocks removed (api-network, bipartite, quality-tiers)"
  - "Orphaned figure references updated in prose"
  - "Stale files deleted (old F6 PDF/PNG, T2 table)"
affects: [paper-compilation, appendix-figure-numbering]

# Tech tracking
tech-stack:
  added: []
  patterns: [bottom-to-top-editing]

# Key files
key-files:
  modified:
    - docs/paper/latex/appendices.tex
  deleted:
    - docs/paper/figures/f6_xsbench_comparison.pdf
    - docs/paper/figures/f6_xsbench_comparison.png
    - docs/paper/figures/t2_model_comparison.tex

# Decisions
decisions:
  - "Edited appendices.tex bottom-to-top (5 edit groups) to prevent line-number drift"
  - "Deleted files via canonical git paths (docs/paper/figures/) not symlink paths (docs/paper/latex/figures/)"

# Metrics
metrics:
  duration: "2min"
  completed: "2026-04-06"
  tasks: 2
  files: 4
---

# Phase 13 Plan 02: Appendices Figure Wiring & Stale File Cleanup Summary

Appendices.tex updated with aug_heatmap figure block after F7, F6 cross-suite comparison replacement, three survey placeholder figure blocks removed, and three stale files deleted from disk.

## What Was Done

### Task 1: Apply all appendices.tex figure wiring edits (bottom-to-top)
**Commit:** `016a99f`

Applied 5 edit groups to `docs/paper/latex/appendices.tex` in bottom-to-top order:

1. **Edit Group 1 (F6 update, D-05/D-06/D-07):** Changed `f6_xsbench_comparison.pdf` to `f6_cross_suite_comparison.pdf`, updated caption to describe cross-suite pass rate comparison with Wilson 95% CIs, changed label from `fig:xsbench` to `fig:cross-suite`.

2. **Edit Group 2 (aug_heatmap insertion, D-01/D-03):** Inserted new figure block after F7's `\end{figure}` with `aug_heatmap.pdf`, caption describing per-kernel augmentation status across levels L0--L4, and `fig:aug-heatmap` label.

3. **Edit Group 3 (quality_tiers removal, D-19):** Removed 12-line placeholder figure block including TODO comment, fbox placeholder, caption, and `fig:quality-tiers` label.

4. **Edit Group 4 (bipartite removal, D-19/D-20):** Updated prose to replace `Figure~\ref{fig:bipartite} visualizes this heterogeneity as a bipartite network` with `This heterogeneity forms a bipartite network structure linking benchmarks to their supported APIs`. Removed 19-line placeholder figure block.

5. **Edit Group 5 (api-network removal, D-19/D-20):** Updated prose to remove `in Figure~\ref{fig:api-network}` from sentence. Removed 18-line placeholder figure block.

Net change: -45 lines (58 deleted, 13 added).

### Task 2: Delete stale files from disk
**Commit:** `6d64d68`

Deleted 3 files:
- `docs/paper/figures/f6_xsbench_comparison.pdf` (old F6, replaced by cross-suite version)
- `docs/paper/figures/f6_xsbench_comparison.png` (old F6 PNG variant)
- `docs/paper/figures/t2_model_comparison.tex` (stale standalone T2 table)

Confirmed replacements still present: `f6_cross_suite_comparison.pdf` and `aug_heatmap.pdf`.

## Verification Results

### Positive checks (all present, exactly 1 each)
- `aug_heatmap`: 1 match (line 1173)
- `fig:aug-heatmap`: 1 match
- `f6_cross_suite_comparison`: 1 match (line 1209)
- `fig:cross-suite`: 1 match (line 1211)

### Negative checks (all removed, 0 each)
- `f6_xsbench`: 0
- `fig:xsbench`: 0
- `fig:api-network`: 0
- `fig:bipartite`: 0
- `fig:quality-tiers`: 0
- `quality_tiers`: 0
- `fbox.*Missing`: 0

### Stale reference sweep (paper.tex + appendices.tex)
Zero matches for: `fig:xsbench`, `fig:api-network`, `fig:bipartite`, `fig:quality-tiers`, `f6_xsbench`, `Triple-panel`, `quality_tiers`, `api_cooccurrence_network`, `benchmark_api_bipartite`, `t2_model_comparison`, `fbox.*Missing`.

### File existence checks
- `f6_xsbench_comparison.pdf`: deleted
- `f6_xsbench_comparison.png`: deleted
- `t2_model_comparison.tex`: deleted
- `f6_cross_suite_comparison.pdf`: present (replacement)
- `aug_heatmap.pdf`: present

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Git staging used canonical paths instead of symlink paths**
- **Found during:** Task 2
- **Issue:** `docs/paper/latex/figures/` is a symlink to `../figures`, so git tracks files under `docs/paper/figures/`. Initial `git add` with latex/figures paths failed with "beyond a symbolic link" error.
- **Fix:** Used canonical git-tracked paths (`docs/paper/figures/`) for staging.
- **Files modified:** Same 3 files, different paths for git.
- **Commit:** 6d64d68

## Known Stubs

None. All figure blocks reference actual PDF files confirmed present on disk.

## Self-Check: PASSED

- FOUND: docs/paper/latex/appendices.tex
- FOUND: .planning/phases/13-paper-figure-table-wiring/13-02-SUMMARY.md
- CONFIRMED DELETED: f6_xsbench_comparison.pdf
- CONFIRMED DELETED: f6_xsbench_comparison.png
- CONFIRMED DELETED: t2_model_comparison.tex
- FOUND commit: 016a99f (Task 1)
- FOUND commit: 6d64d68 (Task 2)
