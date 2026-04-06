# Phase 11: Paper TeX Integration - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Update `docs/paper/latex/paper.tex` so every hardcoded number, table, figure reference, and narrative claim reflects the complete 1,248-task Qwen 3.5 397B dataset. Create an appendix to hold detailed evidence tables/figures, reducing the main text from ~24 pages to ≤10 pages IEEE double-column. Absorb 10 SC26 simulated review items requiring substantive changes. Produce an automated cross-consistency audit script. The paper must be internally consistent and every data claim traceable.

**Critical constraint:** Paper is currently ~24 pages. Must reach ≤10 pages main text. SC26 has no appendix size limit — move detailed evidence there and reference from main.

</domain>

<decisions>
## Implementation Decisions

### Appendix Structure & Float Migration (HIGHEST PRIORITY)
- **D-01:** Create a LaTeX appendix section in paper.tex. Move 17 of 24 floats to appendix. Main text keeps only 7 floats.
- **D-02:** Main text floats (KEEP):
  - `tab:related-work` (S2) — full 10-paper comparison, stays full-width
  - `tab:overall-pass` (S6) — aggregate pass rates, full-width
  - `tab:direction-rates` (S6) — per-direction rates, full-width
  - `tab:per-kernel` (S6) — CONDENSED to top-5 easiest + top-5 hardest kernels (~10 rows). Full 31-row table in appendix.
  - `fig:architecture` (S3) — framework diagram, full-width
  - `fig:failure-taxonomy` (S6) — failure distribution bar/pie
  - `fig:kernel-heatmap` (S6) — 29-kernel × 6-direction heatmap, full-width
- **D-03:** Appendix floats (MOVE — all 17):
  - Tables: `tab:augmentation-levels`, `tab:kernel-pairs`, `tab:api-characteristics`, `tab:suite-summary`, `tab:benchmark-characterization`, `tab:category-distribution`, `tab:model-config`, `tab:hardware`, `tab:repair-transitions`, `tab:self-repair`, `tab:augmentation-rates`, `tab:pass-at-k`, `tab:stats-summary`, full `tab:per-kernel` (31 rows)
  - Figures: `fig:repo-vs-kernel`, `fig:augmentation`, `fig:pass-at-k`, `fig:xsbench`
- **D-04:** Every moved float gets a `\ref` pointer from the main text paragraph where it was previously placed (e.g., "see Appendix Table~\ref{tab:hardware}").
- **D-05:** Methodology tables (model-config, hardware, suite-summary) — all move to appendix. Key facts (GPU model, compiler versions, model name/params) stated inline in Section 5 prose.

### Section Text Preservation
- **D-06:** Section 3 (ParBench Framework, 160 lines) — keep full text, no compression. Architecture is the paper's core contribution.
- **D-07:** Section 4 (Benchmark Curation, 226 lines) — keep full text. Only tables move to appendix; prose narrative stays intact.

### Work Partitioning (4 plans in 3 waves)
- **D-08:** Plan 1 — Appendix structure + float migration: create appendix section, move 17 floats, add `\ref` pointers, inline methodology key facts, condense per-kernel table for main text.
- **D-09:** Plan 2 — Main-text number/claim updates (TEX-01 through TEX-08): update every number, percentage, and CI in Sections 1-8 against `paper_data.json` and `quantitative_findings.json`.
- **D-10:** Plan 3 — SC26 review items: implement full-treatment items (P0-6, P1-8, P1-15) and brief-treatment items (P0-7, P1-9, P1-11, P1-14, P1-16, P1-17, P1-19).
- **D-11:** Plan 4 — Automated cross-consistency audit script (TEX-09): Python script that parses paper.tex for all numbers/percentages, matches against JSON data files, reports mismatches.

### SC26 Review Item Triage
- **D-12:** FULL treatment (substantive work):
  - P0-6: Cochran-Armitage power analysis — compute MDES at 80% power, report limitation honestly
  - P1-8: VERIFY_FAIL case studies — 3 representative examples in main text (wrong reduction scope, race condition, incorrect thread mapping), full table of all VERIFY_FAIL cases in appendix
  - P1-15: S7 redundancy reduction — merge S7.1-S7.5 into 2-3 implication-focused subsections
- **D-13:** BRIEF treatment (1-2 sentence fixes or footnotes):
  - P0-7: Document HeCBench version/commit hash in S5
  - P1-9: Reframe "syntax vs reasoning" as spectrum (1 paragraph rewrite)
  - P1-11: Ground per-kernel tiers in HPC concepts (add explanatory sentence per tier)
  - P1-14: Acknowledge XSBench 0% honestly (1-2 sentences)
  - P1-16: Soften Cochran-Armitage interpretation wording
  - P1-17: Add exact eval campaign commands in S5 (or appendix)
  - P1-19: McNemar power analysis caveat (1 sentence in threats)

### Section 7 Discussion Rewrite
- **D-14:** Merge S7.1-S7.5 into 2-3 subsections focused on IMPLICATIONS (not restating S6 findings). Use freed page budget for deeper analysis.
- **D-15:** Proposed merged structure: (1) Kernel-Centric Translation Implications (merges S7.1 + S7.3), (2) Error Analysis & Actionable Insights (merges S7.2 + S7.4 + S7.5), (3) Threats to Validity (stays as-is, updated with power analysis caveats).
- **D-16:** Threats to Validity STAYS in main text — SC reviewers expect it. Update with P1-16 (Cochran-Armitage interpretation), P1-19 (McNemar power caveat), and sample size limitations.

### Cross-Consistency Audit (TEX-09)
- **D-17:** Automated Python script (not manual grep). Parses paper.tex for numbers/percentages, matches against `quantitative_findings.json` and `paper_data.json`, reports mismatches. Reusable for future edits.
- **D-18:** Leverages Phase 9's `paper_claims` section in quantitative_findings.json for mechanical claim-to-data mapping.

### Claude's Discretion
- Appendix section ordering (by original section order, or grouped by type: tables then figures)
- Exact LaTeX `\appendix` or `\section*{Supplementary Material}` style
- Whether condensed per-kernel table uses tier midrule separators or plain top-5/bottom-5
- P1-17 exact eval commands — in S5 prose or as appendix listing
- How to handle the aug_heatmap figure from Phase 13 (goes in appendix or stays near S6.5)
- Minor prose adjustments when removing table references that no longer point to main text
- Specific VERIFY_FAIL case selection for the 3 main-text examples (must be representative)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper source (primary edit target)
- `docs/paper/latex/paper.tex` — The single file being modified. 1286 lines, 8 sections, 24 current floats.

### Ground truth data files
- `results/analysis/paper_data.json` — Authoritative source for all numerical claims (710 tasks, all 5 suites). Per Phase 12 D-01/D-02.
- `results/analysis/quantitative_findings.json` — 14-dimension quantitative analysis with `paper_claims` section for automated audit. Per Phase 9.
- `results/analysis/quantitative_findings.md` — Paper-ready tables companion.
- `results/analysis/statistical_analysis.json` — Statistical tests (Cochran-Armitage, McNemar, Wilson CIs).
- `results/analysis/selfrepair_analysis.json` — Self-repair rates and attempt analysis.
- `results/analysis/error_taxonomy.json` — Failure taxonomy with subcategories.
- `results/analysis/augmentation_per_kernel_matrix.json` — Per-kernel augmentation data.

### Prior phase context (decisions to carry forward)
- `.planning/phases/12-fix-stale-passk-values/12-CONTEXT.md` — Phase 12 ground truth decisions: paper_data.json (all suites) is THE source. 710 tasks / 38.3%.
- `.planning/phases/12.1-sc26-review-p0-quick-fixes/12.1-CONTEXT.md` — P0 quick fixes already applied. Do NOT re-apply.
- `.planning/phases/09-objective-quantitative-analysis/09-CONTEXT.md` — Two-campaign separation (D-05/D-06), paper_claims mapping (D-22).
- `.planning/phases/13-paper-figure-table-wiring/13-CONTEXT.md` — Figure wiring decisions (aug_heatmap, F6 rename, F3 caption, T2 deletion).
- `.planning/phases/03-augmentation-analysis-story/03-CONTEXT.md` — Augmentation narrative: "mostly null with interesting exceptions" (D-04).
- `.planning/phases/05-introduction-positioning-characterization-table/05-CONTEXT.md` — Introduction decisions: all-suite scope for headlines (D-11), LASSI positioning (D-07/D-08).

### SC26 review items source
- `.planning/ROADMAP.md` — Phase 11 entry lists all 10 absorbed SC26 review items (P0-6, P0-7, P1-8, P1-9, P1-11, P1-14, P1-15, P1-16, P1-17, P1-19) with reviewer attribution.

### Known issues
- `.claude/rules/known-issues.md` — KNOWN_FAIL spec list, eval result schema quirks, timing limitations.

</canonical_refs>

<code_context>
## Existing Code Insights

### Current Paper Structure (paper.tex line numbers)
- S1 Introduction: line 78 (91 lines, 4 subsections)
- S2 Related Work: line 169 (83 lines, 6 subsections)
- S3 ParBench Framework: line 252 (160 lines, 4 subsections)
- S4 Benchmark Curation: line 412 (226 lines, 5 subsections)
- S5 Experimental Setup: line 638 (117 lines, 5 subsections)
- S6 Results: line 755 (381 lines, 8 subsections)
- S7 Discussion: line 1136 (108 lines, 7 subsections)
- S8 Conclusion: line 1244 (42 lines, 2 subsections)

### Float Inventory
- 8 full-width tables (`table*`): related-work, api-characteristics, overall-pass, per-kernel, direction-rates, pass-at-k, stats-summary
- 9 single-column tables: augmentation-levels, kernel-pairs, suite-summary, benchmark-characterization, category-distribution, model-config, hardware, repair-transitions, self-repair, augmentation-rates
- 2 full-width figures (`figure*`): architecture, kernel-heatmap
- 5 single-column figures: repo-vs-kernel, failure-taxonomy, augmentation, pass-at-k, xsbench

### Established Patterns
- Provenance comments: `% src: paper_data.json > field.path = value` (established Phase 1, extended Phase 12)
- `\tbd` macro for pending GPT-4.1 mini values
- `\pending{...}` macro for pending cross-model comparisons
- Wilson CIs formatted as `[lower\%, upper\%]` with 1 decimal place
- `\graphicspath{{figures/}{../../analysis/visualizations/}}` at line 24

### Integration Points
- Phase 13 wiring changes (aug_heatmap insertion, F6 rename, F3 caption) must be coordinated with appendix migration
- Phase 14 (verification backfill) depends on Phase 11 completion for final VERIFICATION.md

</code_context>

<specifics>
## Specific Ideas

- Main text tells the story; appendix proves it. Every moved table/figure gets a `\ref` pointer from main text.
- Per-kernel table condensation: top-5 easiest + top-5 hardest with tier midrule separators, full version in appendix.
- VERIFY_FAIL case studies: pick 3 that represent different failure categories (reduction scope error, race condition, thread mapping error) for maximum reviewer impact.
- S7 rewrite: focus on "so what?" implications for HPC practitioners and LLM developers, not restating pass rates.
- Automated audit script is a lasting artifact — reusable after any future paper edit.

</specifics>

<deferred>
## Deferred Ideas

- Extended VERIFY_FAIL analysis with all cases (beyond 3 main-text examples) — goes in appendix
- Performance/timing analysis with kernel-level profiling — blocked on nvprof/ncu data (out of scope)
- GPT-4.1 mini column additions — blocked on Le's data (use `\tbd` macro)

</deferred>

---

*Phase: 11-paper-tex-integration*
*Context gathered: 2026-04-05*
