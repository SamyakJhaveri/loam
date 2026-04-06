# Phase 13: Paper.tex Figure & Table Wiring - Context

**Gathered:** 2026-04-06 (updated — original 2026-04-05 context stale after Phase 11 completion)
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire regenerated Phase 8 figures and Phase 3 augmentation figures into paper.tex and appendices.tex by fixing stale references, updating captions, adding missing `\includegraphics` commands, exporting the architecture diagram, cleaning up stale files, and removing deleted survey figure placeholders. Closes integration gaps from Phase 11's appendix restructuring.

</domain>

<decisions>
## Implementation Decisions

### Aug Heatmap Placement
- **D-01:** Add `aug_heatmap.pdf` in **appendices.tex** after the F7 figure block (after line 1221). F7 is now in appendices, so the per-kernel drill-down belongs there too.
- **D-02:** Add a reference in paper.tex's augmentation robustness section (around line 895) as "Appendix Figure~\ref{fig:aug-heatmap}".
- **D-03:** Brief caption: "Per-kernel augmentation status across levels L0--L4 (CUDA-to-OMP, Qwen~3.5). Cell color: pass/fail status."
- **D-04:** Skip `aug_trend.pdf` — F7 (`f7_augmentation_robustness.pdf`) already covers the aggregate trend line.

### F6 Reference & Caption (appendices.tex, NOT paper.tex)
- **D-05:** Update filename: `f6_xsbench_comparison.pdf` → `f6_cross_suite_comparison.pdf` at **appendices.tex:1254**.
- **D-06:** New suite-focused caption at appendices.tex:1255: "Cross-suite pass rate comparison (L0, Qwen~3.5). Per-suite aggregate pass rates with Wilson 95\% CIs across all 5 benchmark suites."
- **D-07:** Rename label: `fig:xsbench` → `fig:cross-suite` at **appendices.tex:1256**.
- **D-08:** Update `\ref{fig:xsbench}` → `\ref{fig:cross-suite}` at **paper.tex:977** (this reference EXISTS — contradicts the old context which claimed zero refs).
- **D-09:** Keep F6 in current appendix location (Appendix D, after pass@k figure).
- **D-10:** Delete old `f6_xsbench_comparison.pdf` and `f6_xsbench_comparison.png` from `docs/paper/latex/figures/`.

### F3 Caption (paper.tex)
- **D-11:** Update F3 caption at **paper.tex:831** from "Triple-panel" to descriptive single-panel caption: "Per-kernel pass/fail heatmap across 6 standard translation directions (29 kernels, L0, Qwen~3.5). Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), blue (VERIFY\_FAIL), pink (EXTRACTION\_FAIL)."

### Architecture Diagram (paper.tex)
- **D-12:** User exports drawio manually (draw.io desktop) → PDF at `docs/paper/latex/figures/parbench_architecture.pdf` **BEFORE** Phase 13 executes.
- **D-13:** Phase 13 unconditionally uncomments `\includegraphics[width=\textwidth]{parbench_architecture.pdf}` at **paper.tex:288**, removes the `\fbox` placeholder at line 289.
- **D-14:** Remove TODO comments at paper.tex lines 5, 284, and the helper comment at line 285.
- **D-15:** Figure 1 caption (line 290) is accurate as-is — no changes needed.

### T2 Table
- **D-16:** Skip T2 table entirely — `tab:direction-rates` already shows per-direction pass rates.
- **D-17:** Delete stale `docs/paper/figures/t2_model_comparison.tex`.

### c1-c4 Companion Figures
- **D-18:** Skip all four companion figures (c1 repair transition matrix, c2 repair rate by direction, c3 transform frequency, c4 selection funnel). Existing tables convey the information. SC26 page budget is tight.

### Appendix Survey Figure Cleanup (appendices.tex)
- **D-19:** Remove all 3 figure blocks with `\fbox` placeholders for deleted images:
  - `api_cooccurrence_network_color_v7.png` (appendices.tex:56-73, figure block at 59-73)
  - `benchmark_api_bipartite_color_readable_v7.png` (appendices.tex:360-378, figure block at 363-378)
  - `quality_tiers.png` (appendices.tex:410-421, figure block at 411-421)
- **D-20:** Update surrounding prose to remove `Figure~\ref{fig:api-network}`, `Figure~\ref{fig:bipartite}`, and `Figure~\ref{fig:quality-tiers}` references that would become undefined. Rephrase to describe the content without referencing a figure.

### Claude's Discretion
- Exact `\begin{figure}` environment sizing for aug_heatmap (`figure` vs `figure*`)
- Whether aug_heatmap needs `\label` for cross-referencing (yes — D-02 uses `\ref{fig:aug-heatmap}`)
- Minor prose adjustments around F6 in paper.tex:977 to match new cross-suite framing
- How to rephrase appendix survey prose after figure removal (keep description, just remove figure cross-references)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper sources (TWO files to modify)
- `docs/paper/latex/paper.tex` — Main paper body (1117 lines as of 2026-04-06). Architecture figure, F3, augmentation section reference.
- `docs/paper/latex/appendices.tex` — Appendix content. F6, F7, aug_heatmap insertion point, survey figure cleanup.

### Figure assets (verified on disk 2026-04-06)
- `docs/paper/latex/figures/aug_heatmap.pdf` — Per-kernel augmentation heatmap (37KB, generated 2026-04-04)
- `docs/paper/latex/figures/f6_cross_suite_comparison.pdf` — Cross-suite comparison bar chart (22KB, generated 2026-04-05)
- `docs/paper/latex/figures/f3_kernel_model_heatmap.pdf` — 29-kernel × 6-direction heatmap (55KB, generated 2026-04-05)
- `docs/paper/latex/figures/f7_augmentation_robustness.pdf` — Augmentation trend line (14KB, generated 2026-04-05)
- `docs/paper/figures/parbench_architecture.drawio` — Source for architecture diagram (user exports to PDF before execution)

### Files to delete
- `docs/paper/latex/figures/f6_xsbench_comparison.pdf` — Old F6 (replaced by f6_cross_suite_comparison.pdf)
- `docs/paper/latex/figures/f6_xsbench_comparison.png` — Old F6 PNG
- `docs/paper/figures/t2_model_comparison.tex` — Stale T2 table

### Prior phase decisions
- `.planning/phases/08-figure-regeneration/08-CONTEXT.md` — Figure redesign decisions (D-05 F3 single-panel, D-06 F6 cross-suite, D-11 manual drawio export)
- `.planning/phases/03-augmentation-analysis-story/03-CONTEXT.md` — Augmentation narrative framing (D-09 two figures: heatmap + trend)

</canonical_refs>

<code_context>
## Existing Code Insights

### Lines requiring changes (paper.tex — 1117 lines as of 2026-04-06)
- Line 5: TODO comment about drawio export — remove
- Line 284: TODO comment about drawio export — remove
- Line 285: Helper comment (`% Once the PDF exists, uncomment...`) — remove
- Line 288: Commented-out `\includegraphics{parbench_architecture.pdf}` — uncomment
- Line 289: `\fbox` placeholder — remove
- Line 831: F3 caption with "Triple-panel" — update to single-panel descriptive caption
- Line ~895: Insert reference to aug_heatmap: "Appendix Figure~\ref{fig:aug-heatmap}"
- Line 977: `\ref{fig:xsbench}` → `\ref{fig:cross-suite}`

### Lines requiring changes (appendices.tex)
- Lines 56-73: api_cooccurrence figure block — remove block, update prose at line 51
- Lines 360-378: bipartite figure block — remove block, update prose at line 357
- Lines 410-421: quality_tiers figure block — remove block (prose at 406 doesn't need ref update)
- Line 1218: F7 figure (no changes needed — reference point for aug_heatmap insertion)
- After line 1221: Insert new `\begin{figure}` block for aug_heatmap
- Line 1254: `f6_xsbench_comparison.pdf` → `f6_cross_suite_comparison.pdf`
- Line 1255: F6 caption — rewrite for cross-suite
- Line 1256: `\label{fig:xsbench}` → `\label{fig:cross-suite}`

### References in appendices.tex to update after figure removal
- Line 51: "Figure~\ref{fig:api-network}" — rephrase to remove figure reference
- Line 357: "Figure~\ref{fig:bipartite}" — rephrase to remove figure reference
- `fig:quality-tiers` label is only in the figure block itself (no `\ref{}` in prose) — clean removal

### graphicspath
- paper.tex line 24: `\graphicspath{{figures/}{../../analysis/visualizations/}}` — figures/ relative to `docs/paper/latex/`
- appendices.tex uses same graphicspath (it's `\input` from paper.tex)

### Implementation notes
- F7 at appendices.tex:1216 uses `\begin{figure}[htbp]` (single-column). Aug_heatmap should match this style.
- The architecture figure uses `figure*` (full-width, line 286). Uncommenting the `\includegraphics` requires the exported PDF to exist BEFORE compilation.
- The drawio file exists in TWO locations: `docs/paper/figures/` AND `docs/paper/latex/figures/` (identical). The `\graphicspath` resolves from `docs/paper/latex/figures/`, so the exported PDF must go there.

</code_context>

<specifics>
## Specific Ideas

- F6 caption should be suite-focused: "Cross-suite pass rate comparison..."
- F3 caption should list all 5 status colors explicitly for readers
- Aug heatmap caption should be brief (2 lines max) — the figure is self-explanatory
- Architecture diagram export is a manual user step — Phase 13 just handles the LaTeX side
- Survey figure removal should preserve the descriptive prose, just remove figure references
- User will export drawio to PDF before Phase 13 execution begins

</specifics>

<deferred>
## Deferred Ideas

- c1-c4 companion figures (repair matrix, repair rate, transform frequency, selection funnel) — could be added to supplementary material in a future revision
- `aug_trend.pdf` — redundant with F7 for now; could replace F7 if Phase 3's version is preferred later
- XSBench-specific comparison figure — the argument is well-covered in Section 4.3 text
- Survey visualization images (api_cooccurrence, bipartite) exist in `analysis/visualizations/take in paper/` — could be restored if appendix page budget allows in camera-ready
- `quality_tiers.png` — would need regeneration from scratch if ever restored

</deferred>

---

*Phase: 13-paper-figure-table-wiring*
*Context gathered: 2026-04-06 (updated)*
