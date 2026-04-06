# Phase 13: Paper.tex Figure & Table Wiring - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire regenerated Phase 8 figures and Phase 3 augmentation figures into paper.tex by fixing stale references, updating captions, adding missing `\includegraphics` commands, exporting the architecture diagram, and cleaning up stale files. Closes 4 integration gaps + 2 E2E flow breaks + P0-3 from SC26 review.

</domain>

<decisions>
## Implementation Decisions

### Aug Figure Placement
- **D-01:** Add `aug_heatmap.pdf` only — skip `aug_trend.pdf` since F7 (`f7_augmentation_robustness.pdf`) already covers the aggregate trend line.
- **D-02:** Place aug_heatmap figure AFTER F7 in Section 7.4 (Augmentation Robustness). Reading order: aggregate trend (F7) → per-kernel drill-down (aug_heatmap).
- **D-03:** Brief caption: "Per-kernel augmentation status across levels L0–L4 (CUDA-to-OMP, Qwen 3.5). Cell color: pass/fail status."

### T2 Table
- **D-04:** Skip T2 table entirely — `tab:direction-rates` (table begins line 1029, label at line 1032) already shows per-direction pass rates with current 5-suite data. T2 content is stale (Rodinia-only, 49/138) and redundant.
- **D-05:** Delete stale `docs/paper/figures/t2_model_comparison.tex` to avoid confusion.

### Architecture Diagram (P0-3)
- **D-06:** User exports drawio manually (draw.io desktop) → place PDF at `docs/paper/latex/figures/parbench_architecture.pdf`.
- **D-07:** Phase 13 uncomments `\includegraphics[width=\textwidth]{parbench_architecture.pdf}` at line 261, removes the `\fbox` placeholder at line 262, and removes the helper comment at line 258 (`% Once the PDF exists, uncomment the \includegraphics...`).
- **D-08:** Figure 1 caption (line 263) is accurate as-is — no changes needed.

### c1-c4 Companion Figures
- **D-09:** Skip all four companion figures (c1 repair transition matrix, c2 repair rate by direction, c3 transform frequency, c4 selection funnel). Existing tables already convey the information. SC26 page budget is tight.

### F6 Reference & Caption
- **D-10:** Update filename: `f6_xsbench_comparison.pdf` → `f6_cross_suite_comparison.pdf` at line 1096.
- **D-11:** New suite-focused caption: "Cross-suite pass rate comparison (L0, Qwen 3.5). Per-suite aggregate pass rates with Wilson 95\% CIs across all 5 benchmark suites."
- **D-12:** Rename label: `fig:xsbench` → `fig:cross-suite` at line 1098. NOTE: grep finds ZERO `\ref{fig:xsbench}` references in paper.tex — the label is currently orphaned (defined but never cited). Only the `\label{}` itself needs renaming; no `\ref{}` updates required. Consider adding a `\ref{fig:cross-suite}` citation in the surrounding prose if the figure is meant to be referenced.
- **D-13:** Keep F6 in current location (after pass@k section, before Statistical Summary).
- **D-14:** Delete old `f6_xsbench_comparison.pdf` and `f6_xsbench_comparison.png` from `docs/paper/latex/figures/`.

### F3 Caption
- **D-15:** Update F3 caption from "Triple-panel" to descriptive single-panel caption: "Per-kernel pass/fail heatmap across 6 standard translation directions (29 kernels, L0, Qwen 3.5). Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), blue (VERIFY\_FAIL), pink (EXTRACTION\_FAIL)."

### Claude's Discretion
- Exact `\begin{figure}` environment sizing for aug_heatmap (`figure` vs `figure*`)
- Whether aug_heatmap needs `\label` for cross-referencing (yes if text references it)
- Minor prose adjustments around F6 to match the new cross-suite framing
- TODO comment cleanup (remove drawio TODO at lines 5, 257, and 258 after uncommenting)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper source
- `docs/paper/latex/paper.tex` — The single file being modified (all wiring changes happen here)

### Figure assets (verified on disk 2026-04-05)
- `docs/paper/latex/figures/aug_heatmap.pdf` — Per-kernel augmentation heatmap (36KB / 37280 bytes, generated 2026-04-04)
- `docs/paper/latex/figures/f6_cross_suite_comparison.pdf` — Cross-suite comparison bar chart (22KB / 22646 bytes, generated 2026-04-05)
- `docs/paper/latex/figures/f3_kernel_model_heatmap.pdf` — 29-kernel × 6-direction heatmap (55KB / 55857 bytes, generated 2026-04-05)
- `docs/paper/latex/figures/f7_augmentation_robustness.pdf` — Augmentation trend line (14KB / 14556 bytes, generated 2026-04-05)
- `docs/paper/figures/parbench_architecture.drawio` — Source for architecture diagram (user exports to PDF)

### Prior phase decisions
- `.planning/phases/08-figure-regeneration/08-CONTEXT.md` — Figure redesign decisions (D-05 F3 single-panel, D-06 F6 cross-suite, D-09 aug figures untouched, D-11 manual drawio export)
- `.planning/phases/03-augmentation-analysis-story/03-CONTEXT.md` — Augmentation narrative framing (D-09 two figures: heatmap + trend)

</canonical_refs>

<code_context>
## Existing Code Insights

### Lines requiring changes (paper.tex)
- Line 5, 257: TODO comments about drawio export — remove after uncommenting
- Line 258: Helper comment (`% Once the PDF exists, uncomment...`) — remove
- Line 261: Commented-out `\includegraphics{parbench_architecture.pdf}` — uncomment
- Line 262: `\fbox` placeholder — remove
- Line 931: F3 caption with "Triple-panel" — update
- Line 1096: `f6_xsbench_comparison.pdf` reference — update filename
- Line 1097: F6 caption — rewrite for cross-suite
- Line 1098: `\label{fig:xsbench}` — rename to `fig:cross-suite`
- After line 1015: Insert new `\begin{figure}` block for aug_heatmap

### References to update
- `\label{fig:xsbench}` at line 1098 → `\label{fig:cross-suite}` (label only — no `\ref{fig:xsbench}` instances exist in paper.tex; label is currently orphaned)

### Files to delete
- `docs/paper/latex/figures/f6_xsbench_comparison.pdf` (old F6)
- `docs/paper/latex/figures/f6_xsbench_comparison.png` (old F6)
- `docs/paper/figures/t2_model_comparison.tex` (stale T2 table)

### Implementation notes
- F7 at line 1010 uses `\begin{figure}[t]` (single-column). If aug_heatmap is placed after F7 as `figure*` (full-width), LaTeX float reordering may push it away from the surrounding text. Consider using single-column `figure` or testing both.
- The drawio file exists in TWO locations: `docs/paper/figures/parbench_architecture.drawio` AND `docs/paper/latex/figures/parbench_architecture.drawio` (identical, 36352 bytes each). The `\graphicspath` resolves from `docs/paper/latex/figures/`, so the exported PDF should go there.
- The architecture figure uses `figure*` (full-width, line 259). Uncommenting the `\includegraphics` requires the exported PDF to exist at `docs/paper/latex/figures/parbench_architecture.pdf` BEFORE compilation.

### graphicspath
- `\graphicspath{{figures/}{../../analysis/visualizations/}}` (line 24) — figures/ relative to `docs/paper/latex/`

</code_context>

<specifics>
## Specific Ideas

- F6 caption should be suite-focused: "Cross-suite pass rate comparison..."
- F3 caption should list all 5 status colors explicitly for readers
- Aug heatmap caption should be brief (2 lines max) — the figure is self-explanatory
- Architecture diagram export is a manual user step — Phase 13 just handles the LaTeX side

</specifics>

<deferred>
## Deferred Ideas

- c1-c4 companion figures (repair matrix, repair rate, transform frequency, selection funnel) — could be added to supplementary material in a future revision
- `aug_trend.pdf` — redundant with F7 for now; could replace F7 if Phase 3's version is preferred later
- XSBench-specific comparison figure — the argument is well-covered in Section 4.3 text; a dedicated figure could strengthen it if page budget allows in camera-ready

</deferred>

---

*Phase: 13-paper-figure-table-wiring*
*Context gathered: 2026-04-05*
