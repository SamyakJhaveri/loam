# Phase 17: Paper Integration — Dual-Model Results, Comparison & Differentiation

**Gathered:** 2026-04-07 (updated — gate file corrected, per-model figure handling locked, Phase 16-04 gate added)
**Status:** Ready for planning (pending Phase 16-04 completion)

<domain>
## Phase Boundary

Update `docs/paper/latex/paper.tex` with GPT-4.1 mini data: fill all `\pending{...}` markers and `\tbd` table cells, write the new cross-model comparison section (Section 6.9), add augmentation degradation examples, emphasize prompt anonymization as a key differentiator, and wire per-model figures into the paper body and appendix.

Phase 17 does NOT generate analysis files or figures — those are Phase 16's job. Phase 17 only reads Phase 16 outputs and writes paper.tex / appendices.tex.

**Hard gate — Phase 17 MUST NOT start until ALL of the following exist:**
- `results/analysis/paper_data_gpt41mini.json` ✓ (present)
- `results/analysis/cross_model_comparison.json` ✓ (present)
- `results/analysis/error_taxonomy.json` with `per_model["azure-gpt-4.1-mini"]` ✓ (present)
- `.planning/phases/16-gpt-data-analysis/16-04-SUMMARY.md` ✗ (Phase 16-04 not yet complete — BLOCKER)

**Per-model figures must be committed before Phase 17 starts.** Check that all four `_qwen` and `_gpt` variants of F3, F4, F5, F6 exist in `docs/paper/figures/` and are tracked in git.

</domain>

<decisions>
## Implementation Decisions

### Gate File Correction (UPDATED from original)
- **D-01-gate:** The gate file name was wrong in prior context. `error_taxonomy_gpt41mini.json` does NOT exist and was never generated. The correct gate file is `results/analysis/error_taxonomy.json` (combined dual-model taxonomy with both models in `per_model` dict).
- **D-01-gate-access:** Phase 17 executor reads GPT failure data via `error_taxonomy.json → per_model["azure-gpt-4.1-mini"]`. No separate GPT-only file is needed or should be created.
- **D-01-gate-phase16:** Phase 16-04 must be fully complete (SUMMARY written, per-model figures committed) before Phase 17 starts. This is an additional gate requirement beyond the analysis JSONs.

### omp_target-to-cuda Coverage (unchanged)
- **D-02:** Proceed with **7-direction** cross-model comparison. `omp_target-to-cuda` GPT data has not arrived. Section 6.9, all cross-model prose, and per-direction tables use 7 directions.
- **D-02-upgrade:** If `omp_target-to-cuda` GPT results arrive in `results/evaluation/azure-gpt-4.1-mini/` before Phase 17 execution begins, executor may upgrade to 8 directions. Check once at Phase 17 start; do not check again mid-execution.
- **D-02-footnote:** All cross-model direction tables must include a footnote: "Cross-model comparison covers 7 of 8 evaluated directions; `omp_target-to-cuda` GPT-4.1 mini results were unavailable at submission."

### Marker Counts (confirmed correct)
- **D-03:** Actual `\pending{...}` count: **18**. Line 631 (`\pending{GPU model...}`) stays unfilled — see D-07.
- **D-04:** Actual `\tbd` cell count: **24** across two tables:
  - `tab:overall-pass` (~line 690-691): 9 cells in GPT row + 9 cells in Aggregate row = 18 cells
  - `tab:direction-rates` (~lines 939-944): 6 cells (GPT column per 7 directions; `omp_target-to-cuda` → "—" with footnote)
- **D-04-aggregate:** Aggregate row in `tab:overall-pass` is **sum of counts** (Qwen + GPT), NOT average of pass rates.

### Page Budget (unchanged)
- **D-05:** Add ALL content — no cuts, no deferrals. Tasks 17A, 17A-tbd, 17B, 17C, 17D, 17E execute fully.
- **D-05-compress:** Samyak and Le manually compress to ≤10 pages before April 8 submission. Executor produces complete content, not trimmed content.
- **D-05-appendix-main:** Per-model GPT figures in appendix do NOT count toward the 10-page main body limit.

### Execution Order Within Phase 17 (unchanged)
- **D-06:** Strict Phase 16 gate (see domain boundary). Execution order:
  1. **Wave 1 (one subagent):** 17A + 17A-tbd — fill all `\pending{...}` markers and `\tbd` cells in document order. LaTeX compile check after.
  2. **Wave 2 (sequential):** 17B (Section 6.9), then 17C (augmentation examples), then 17D (anonymization subsection). LaTeX compile checkpoint after each.
  3. **Wave 3:** 17E — wire per-model figures into paper.tex (Qwen) and appendices.tex (GPT), update captions with explicit model names. Final LaTeX compile + page count check.

### Hardware Specs (line 631)
- **D-07:** `\pending{GPU model, CPU model, and OS for the collaborator's evaluation machine.}` stays **as-is**. Add inline TODO comment: `% TODO(samyak): fill when Niranjan/Le provides machine specs`. Do NOT remove the `\pending{}` macro.
- **D-07-count:** Only **17** of the 18 `\pending{...}` markers will be filled. Line 631 is explicitly excluded.

### Section 6.9 Content (unchanged)
- **D-08:** Section 6.9 (Cross-Model Comparison) inserts after Section 6.8. Must contain:
  1. Overall pass rate comparison with actual chi-squared p-value and Wilson 95% CIs (no placeholder stats)
  2. Per-direction side-by-side for 7 common directions; explicit footnote for `omp_target-to-cuda`
  3. Failure taxonomy comparison: BUILD_FAIL dominance pattern (GPT vs Qwen) — use `error_taxonomy.json → per_model` dict
  4. Per-kernel agreement matrix — four-way: both-pass / both-fail / Qwen-only-pass / GPT-only-pass. **Actual numbers from `cross_model_comparison.json`: 13 both-pass, 5 both-fail, 11 Qwen-only-pass, 2 GPT-only-pass (31 common kernels)**
  5. Effect sizes (Cohen's h) overall and per-direction
- **D-08-framing:** Section 6.9 frames two models as demonstrating ParBench's utility, NOT as a model ranking. Both models described as "providers" (provider diversity framing, established in Phase 15).

### Per-Model Figure Handling (NEW — 17E decisions)
- **D-09:** F3, F4, F5, F6 are now split into per-model variants (`_qwen.pdf` and `_gpt.pdf`) by Phase 16-04. The originals (without suffix) are deleted. F7 remains unified dual-model.
- **D-09-main:** Qwen variants go in the **main body** of `paper.tex`:
  - F3: update `\includegraphics` at line ~831 from `f3_kernel_model_heatmap.pdf` → `f3_kernel_model_heatmap_qwen.pdf`
  - F4: update `\includegraphics` at line ~712 from `f4_failure_taxonomy.pdf` → `f4_failure_taxonomy_qwen.pdf`
  - F5: add new `\includegraphics{f5_pass_at_k_by_direction_qwen.pdf}` in the pass@k analysis section
  - F6: add new `\includegraphics{f6_cross_suite_comparison_qwen.pdf}` in the cross-suite section
- **D-09-appendix:** GPT variants go in `docs/paper/latex/appendices.tex`:
  - Add a new section: "GPT-4.1 Mini Figures" containing F3/F4/F5/F6 GPT variants
  - Each GPT figure caption must include "(GPT-4.1 mini)" to distinguish from main body Qwen figures
- **D-09-prose:** All figure citations in paper.tex prose must explicitly name the model. E.g., "Figure 3 (Qwen 3.5 397B) shows..." and "Figure X in Appendix (GPT-4.1 mini) shows..."
- **D-09-captions:** All main body figure captions for F3/F4/F5/F6 must include "(Qwen 3.5 397B)" in the caption text.
- **D-09-line-numbers:** Line numbers for F3/F4 in paper.tex are approximate; executor greps for actual position before editing.

### Claude's Discretion
- Exact prose wording in Section 6.9 and 17C/17D — executor has freedom on sentence-level decisions within the constraints above
- Where exactly in paper.tex to insert F5/F6 Qwen figures — executor decides based on surrounding section content
- How to present the four-way kernel matrix (table vs prose summary) — executor decides based on available space

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 17 Plan
- `.planning/phases/17-paper-integration/PLAN.md` — Full task breakdown 17A through 17E, exact grep positions, verification checklist

### Phase 16 Context & Outputs
- `.planning/phases/16-gpt-data-analysis/16-CONTEXT.md` — Decisions on cross_model_comparison.py design
- `results/analysis/paper_data_gpt41mini.json` — GPT numbers source for 17A + 17A-tbd (gate file ✓)
- `results/analysis/cross_model_comparison.json` — Statistical comparison source for 17B (gate file ✓); also contains per-kernel agreement matrix
- `results/analysis/error_taxonomy.json` — Combined dual-model taxonomy; GPT data at `per_model["azure-gpt-4.1-mini"]` (gate file ✓; NOT error_taxonomy_gpt41mini.json)
- `results/analysis/coverage_gaps.md` — Direction coverage table, per-kernel agreement summary, footnote text for paper

### Paper Edit Targets
- `docs/paper/latex/paper.tex` — Primary edit target for 17A through 17E. Executor must grep for actual line numbers before editing.
- `docs/paper/latex/appendices.tex` — Target for GPT figure appendix (17E)

### Figure Files (post Phase 16-04)
- `docs/paper/figures/f3_kernel_model_heatmap_qwen.pdf` — F3 Qwen variant (main body)
- `docs/paper/figures/f3_kernel_model_heatmap_gpt.pdf` — F3 GPT variant (appendix)
- `docs/paper/figures/f4_failure_taxonomy_qwen.pdf` — F4 Qwen variant (main body)
- `docs/paper/figures/f4_failure_taxonomy_gpt.pdf` — F4 GPT variant (appendix)
- `docs/paper/figures/f5_pass_at_k_by_direction_qwen.pdf` — F5 Qwen variant (main body, new addition)
- `docs/paper/figures/f5_pass_at_k_by_direction_gpt.pdf` — F5 GPT variant (appendix)
- `docs/paper/figures/f6_cross_suite_comparison_qwen.pdf` — F6 Qwen variant (main body, new addition)
- `docs/paper/figures/f6_cross_suite_comparison_gpt.pdf` — F6 GPT variant (appendix)
- `docs/paper/figures/f7_augmentation_robustness.pdf` — Unified dual-model (no change)
- `docs/paper/figures/t2_model_comparison.tex` — T2 table (no change)

### Anonymization Code (for 17D)
- `scripts/evaluation/llm_evaluate.py` line ~570 (`build_translation_prompt()`) — Cross-check the 6 anonymization measures before writing 17D prose

### Master Plan
- `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` §Phase 17 (lines 195-343) — Original phase specification and rationale

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/paper/latex/paper.tex` — `\pending` macro at line 36-37; `\tbd` macro at line 39 (no argument)
- `results/analysis/paper_data.json` — Qwen data schema; paper_data_gpt41mini.json follows same schema
- `results/analysis/error_taxonomy.json` — Combined dual-model; use `per_model["azure-gpt-4.1-mini"]` for GPT error data

### Established Patterns
- All Qwen data fills have inline `% src: paper_data.json > ...` comments — GPT fills must follow same pattern with `% src: paper_data_gpt41mini.json > ...`
- Wilson 95% CIs are standard for all pass rate claims
- Figure captions in paper.tex use `\caption{...}` — add model name in parentheses at end

### Integration Points
- `tab:overall-pass`: GPT row (~line 690) + Aggregate row (~line 691) — both need fills
- `tab:direction-rates`: GPT column (~lines 939-944) — 6 directions filled, omp_target-to-cuda → "—" with footnote
- Section 6.9 insert point: after Section 6.8 (~line 1000 — verify with grep before inserting)
- F3 figure reference: ~line 831 in paper.tex — update to `_qwen.pdf`
- F4 figure reference: ~line 712 in paper.tex — update to `_qwen.pdf`
- `docs/paper/latex/appendices.tex` — target for new GPT figure section

### Per-Kernel Agreement Data (from coverage_gaps.md / cross_model_comparison.json)
- Both pass: **13 kernels**
- Both fail: **5 kernels**
- Qwen only pass: **11 kernels**
- GPT only pass: **2 kernels**
- Total common kernels: **31**

### GPT Eval Data Confirmed Present
- 897 files in `results/evaluation/azure-gpt-4.1-mini/`
- Directions: 7 (omp_target-to-cuda absent → D-02 fallback locked)

</code_context>

<specifics>
## Specific Ideas

- **lavamd example (17C):** L4 is PASS — must state this explicitly.
- **bptree example (17C):** L3 is PASS (partial recovery) then L4 is RUN_FAIL again — state recovery-then-reversion pattern explicitly.
- **Aggregate row in tab:overall-pass:** Sum of counts, NOT average of rates. Critical correctness rule.
- **Section 6.9 stat prerequisite:** Write actual chi-squared p-value and Cohen's h from cross_model_comparison.json — never write placeholder statistics.
- **Provider diversity framing:** GPT-4.1 mini described as "OpenAI via Azure" vs "Qwen via Together AI" — two providers, not two model rankings.
- **Figure caption model naming:** All main body F3/F4/F5/F6 captions must include "(Qwen 3.5 397B)"; appendix GPT captions must include "(GPT-4.1 mini)".

</specifics>

<deferred>
## Deferred Ideas

- omp_target-to-cuda cross-model comparison — blocked on Le's data. D-02-upgrade check at Phase 17 start.
- Per-kernel agreement matrix as a heatmap figure — JSON from cross_model_comparison.json is canonical; Samyak/Le decide during compression whether to promote to figure.
- Page budget compression — explicitly deferred to Samyak + Le manual edit after Phase 17 execution (D-05-compress).
- F5/F6 may be removed from main body by Samyak/Le during compression if page budget is tight — executor adds them, editorial decision follows.

</deferred>

---

*Phase: 17-paper-integration*
*Context gathered: 2026-04-07 (updated — gate file corrected to error_taxonomy.json, per-model figure handling locked D-09, Phase 16-04 completion required as gate, per-kernel agreement numbers added)*
