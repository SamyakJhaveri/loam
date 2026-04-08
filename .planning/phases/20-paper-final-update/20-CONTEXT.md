# Phase 20: paper-final-update - Context

**Gathered:** 2026-04-08
**Status:** Ready for replanning

<domain>
## Phase Boundary

Update ALL GPT-4.1-mini numbers in `overleaf.tex`, `appendices.tex`, and `paper.tex` to match Phase 19 analysis outputs. Includes structural updates from `19-STRUCTURAL-CHANGES.md` (13 items: direction table row changes, footnote update, effect-size prose rewrite, per-kernel agreement rewrite, failure taxonomy narrative, abstract/intro/conclusion numbers). Also includes applying methodology text edits (already in working tree for overleaf.tex) to paper.tex. Commit all three files in one paper(20) commit.

**Hard prerequisite (user-confirmed):** User will add valid XSBench GPT result files to `results/evaluation/azure-gpt-4.1-mini/` before Phase 20 executes. Phase 20 plan must start with Task 0: re-run Phase 19 analysis pipeline to refresh all JSON outputs. Paper edits must use the freshly regenerated numbers, NOT the current stale paper_data_gpt41mini.json values.

Phase 20 does NOT run new LLM evaluations. It does NOT add new sections or restructure the paper. It does NOT touch any result JSON files.

</domain>

<decisions>
## Implementation Decisions

### Submission File Priority
- **D-01:** `overleaf.tex` is the SC26 submission artifact (primary). It gets top priority for correctness.
- **D-02:** `paper.tex` must be kept in sync with `overleaf.tex` — apply both the methodology text edits AND the GPT numeric updates to paper.tex.
- **D-03:** `appendices.tex` is shared between both files; update it once.

### Narrative Scope
- **D-04:** Update numbers in-place AND revise interpretive prose where the story was inverted by the new data. Specifically:
  - BUILD_FAIL dominance narrative: old "81.0% of GPT failures" → new "65.0% of GPT failures" (less severe than before)
  - VERIFY_FAIL comparison: old "GPT 5.6% < Qwen 7.2%" → new "GPT 14.2% > Qwen 7.2%" (direction reversed — this is a new finding)
  - Top GPT build failure subcategory: old `missing_target_api` (196 instances) → new `missing_header` (151 instances)
  - Per-kernel agreement: old "13/5/11/2" → new "18/4/6/1" (both-pass jumped from 13 to 18)
  - Effect-size discussion: remove reference to `cuda-to-omp_target h=0.86` (based on invalid Argonne data). New largest effects: `omp_target-to-cuda` (h=1.01) and `omp-to-cuda` (h=0.83).
  - "4 of 7 directions |h| < 0.20" → "1 of 7 directions |h| < 0.20" (only cuda-to-omp at h=0.086)
- **D-05:** Follow `19-STRUCTURAL-CHANGES.md` exactly for all 13 listed items. For any narrative change NOT explicitly listed in that document, Claude uses judgment aligned with D-04 (revise where story inverted).

### XSBench GPT Coverage
- **D-06:** User will find and add valid XSBench GPT result files before Phase 20 executes.
- **D-07:** After XSBench files are added, Phase 20 Task 0 re-runs the full Phase 19 analysis pipeline (all scripts). All paper edit numbers come from the freshly generated JSONs.
- **D-08:** After re-run, if XSBench GPT coverage is still significantly less than Qwen coverage, add a brief qualification sentence in the cross-suite analysis section noting the coverage asymmetry and reason (Argonne machine missing xsbench-src for many directions).

### Unstaged Methodology Edits
- **D-09:** The methodology text edits already in `overleaf.tex` working tree (architecture caption rewrite, spec schema figure-reference update, verify stage conjunction semantics, augmentation section detail expansion) are correct and intentional. DO NOT discard them.
- **D-10:** Fold these methodology edits into the single Phase 20 commit (`paper(20):`). Do not create a separate commit.
- **D-11:** Apply the same methodology text edits to `paper.tex` as part of Phase 20 execution. The executor should diff overleaf.tex vs paper.tex body content and apply the methodology changes.
- **D-12:** Create `20-02-PLAN.md` as the fresh execution plan. `20-01-PLAN.md` is preserved as reference (done markers reflect premature marking; work was not actually committed).

### Validation Gate
- **D-13:** Standard `/validate` (4-wave protocol, ~3 min) is required before the commit. The pre-commit hook enforces `.validation_passed` sentinel.
- **D-14:** After commit: try `pdflatex -interaction=nonstopmode overleaf.tex` and check for errors. Skip silently if pdflatex is not installed.

### Claude's Discretion
- Error taxonomy subcategory counts in failure taxonomy prose: Claude should update these from `error_taxonomy.json` after Phase 19 re-run. The structural changes document lists approximate expected values; always use the freshly generated JSON.
- Wilson CI recalculation for the Aggregate row in Table 3: Claude computes this from the new combined counts.
- Exact per-direction rates for the cross-model direction table: read from freshly generated `cross_model_comparison.json > per_direction` after Phase 19 re-run.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Primary Data Sources (read AFTER Phase 19 re-run, not before)
- `results/analysis/paper_data_gpt41mini.json` — GPT overall stats, by_direction, self_repair, augmentation, passk_campaign. READ AFTER Task 0 re-run.
- `results/analysis/cross_model_comparison.json` — overall chi2/p/h, per_direction, per_kernel_matrix. READ AFTER Task 0 re-run.
- `results/analysis/paper_data.json` — Qwen stats (unchanged, but needed for Aggregate row recalculation)
- `results/analysis/error_taxonomy.json` — failure subcategory counts by model. READ AFTER Task 0 re-run.

### Structural Change Specification
- `.planning/phases/19-gpt-final-data-refresh/19-STRUCTURAL-CHANGES.md` — 13 items with exact paper locations, old text, new text. This is the authoritative change list for paper edits. NOTE: numbers in this document reflect the 6-file XSBench dataset; after Phase 19 re-run with more XSBench files, verify each number against fresh JSONs.
- `.planning/phases/19-gpt-final-data-refresh/19-NUMBERS.md` — Key number summary from Phase 19 (may be stale after XSBench addition; treat as reference, not authoritative).
- `.planning/phases/19-gpt-final-data-refresh/19-01-SUMMARY.md` — Phase 19 execution summary

### Files to Edit
- `docs/paper/latex/overleaf.tex` — PRIMARY submission artifact (SC26). Already has methodology edits in working tree (unstaged). Needs GPT numeric updates.
- `docs/paper/latex/paper.tex` — Secondary sync copy. Needs BOTH methodology text edits AND GPT numeric updates.
- `docs/paper/latex/appendices.tex` — 3 tables: self-repair, augmentation by level, pass@k. Needs GPT column updates.

### Analysis Scripts (Phase 19 re-run)
- `scripts/analysis/generate_paper_data.py` — regenerates paper_data_gpt41mini.json
- `scripts/analysis/cross_model_comparison.py` — regenerates cross_model_comparison.json
- `scripts/analysis/build_error_taxonomy.py` — regenerates error_taxonomy.json
- `scripts/evaluation/analyze_eval.py` — regenerates eval_summary.json
- `scripts/generate_paper_figures.py` — regenerates figures (run with --figure all)

### Prior Phase Context
- `.planning/phases/19-gpt-final-data-refresh/19-CONTEXT.md` — D-03 defines 19-STRUCTURAL-CHANGES.md purpose and minimum contents
- `.planning/phases/17-paper-integration/17-CONTEXT.md` — original paper structure decisions (D-02: direction footnote, D-08: Section 6.9 stats, D-09: per-model figure split)
- `.planning/phases/20-paper-final-update/20-01-PLAN.md` — original plan (reference only; done markers are premature)

</canonical_refs>

<code_context>
## Existing Code Insights

### Working Tree State
- `overleaf.tex` (unstaged): +41 lines/-16 lines. Methodology edits present:
  - Architecture caption: 5-stage numbered description with color-coded stage labels
  - Spec schema text: figure reference updated from "Spec JSON component (blue, bottom-left)" to "stage~1→3 and stage~1→4" notation
  - Verify stage: conjunction semantics added, SKIP behavior documented, Rodinia numeric_comparison example added
  - Augmentation section: 6 transforms expanded with `__global__`/`__kernel__` exclusion rationale, scope clarification (all prompt payload files, not just kernels), indentation reformatted
- `paper.tex`: no working tree changes
- `appendices.tex`: no working tree changes

### Existing Patterns
- `% src: path > key: value` comment convention on all numeric claims — must be updated for every changed number
- `\pending{}` command used for hardware GPU model spec — one intentional use must be preserved
- `\tbd{}` command — should not appear in submission; verify zero occurrences after edits

### Integration Points
- Both `overleaf.tex` and `paper.tex` have identical body content with different preambles — changes to one must be mirrored in the other
- `appendices.tex` is `\input{}`-ted by both files; it does not have its own preamble
- LaTeX environment balance invariant: `overleaf.tex` and `paper.tex` must have `begin == end`; `appendices.tex` expected diff of 1 (known pre-existing)

</code_context>

<specifics>
## Specific Ideas

- When Phase 19 re-run completes, the executor should print ALL new numbers to a new `20-NUMBERS.md` (mirroring `19-NUMBERS.md` format) before applying any paper edits. This gives a paper-audit trail independent of JSON files.
- The spot-check script from the old plan (Task 4) is a good approach: verify 10 specific numbers against source JSONs as a final acceptance gate.
- Do NOT copy overleaf.tex to paper.tex wholesale — the preambles differ. Apply changes surgically using grep+edit.
- For the Aggregate row Wilson CI recalculation: combined pass = 272 + new_gpt_pass, combined total = 710 + new_gpt_total. Recompute using `statsmodels.stats.proportion.proportion_confint(pass, total, alpha=0.05, method='wilson')`.

</specifics>

<deferred>
## Deferred Ideas

- XSBench GPT eval re-run (full campaign) to restore the deleted 32 files — if the files the user finds are only partial, full re-run is post-submission work.
- Page budget compression — deferred to Samyak + Le manual edit (Phase 17 D-05-compress).
- Per-kernel agreement matrix heatmap figure — JSON output only for now.
- Cross-model pass@k comparison (may now be possible if new GPT data covers same subset as Qwen pass@k).

</deferred>

---

*Phase: 20-paper-final-update*
*Context gathered: 2026-04-08*
