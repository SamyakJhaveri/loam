# Phase 17: Paper Integration — Dual-Model Results, Comparison & Differentiation

**Gathered:** 2026-04-07 (updated from initial version)
**Status:** Ready for planning

<domain>
## Phase Boundary

Update `docs/paper/latex/paper.tex` with GPT-4.1 mini data: fill all `\pending{...}` markers and `\tbd` table cells, write the new cross-model comparison section (Section 6.9), add augmentation degradation examples, and emphasize prompt anonymization as a key differentiator.

Phase 17 does NOT generate analysis files or figures — those are Phase 16's job. Phase 17 only reads Phase 16 outputs and writes paper.tex.

**Hard gate:** Phase 17 MUST NOT start until all three Phase 16 outputs exist on disk:
- `results/analysis/paper_data_gpt41mini.json`
- `results/analysis/cross_model_comparison.json`
- `results/analysis/error_taxonomy_gpt41mini.json`

</domain>

<decisions>
## Implementation Decisions

### omp_target-to-cuda Coverage (UPDATED)
- **D-01:** Proceed with **7-direction** cross-model comparison. `omp_target-to-cuda` GPT data has not arrived by April 7 EOD. Section 6.9, all cross-model prose, and per-direction tables use 7 directions.
- **D-01-upgrade:** If `omp_target-to-cuda` GPT results arrive in `results/evaluation/azure-gpt-4.1-mini/` before Phase 17 execution begins, executor may upgrade to 8 directions. Check once at Phase 17 start; do not check again mid-execution.
- **D-01-footnote:** All cross-model direction tables must include a footnote: "Cross-model comparison covers 7 of 8 evaluated directions; `omp_target-to-cuda` GPT-4.1 mini results were unavailable at submission."

### Marker Counts (CORRECTED from actual grep)
- **D-02:** Actual `\pending{...}` count: **18** (not 19 as originally estimated). Grep confirmed. Line 631 (`\pending{GPU model...}`) stays unfilled — see D-07.
- **D-03:** Actual `\tbd` cell count: **24** across two tables (not 18):
  - `tab:overall-pass` (line ~690-691): 9 cells in GPT row + 9 cells in Aggregate row = 18 cells
  - `tab:direction-rates` (lines ~939-944): 6 cells (one GPT column per direction, 7 directions minus 1 = 6 + omp_target-to-cuda → "—" with footnote)
  - Note: `omp_target-to-cuda` GPT column in direction table → `—` (not `\tbd`), no fill needed from data
- **D-03-aggregate:** Aggregate row in `tab:overall-pass` is **sum of counts** (Qwen + GPT), NOT average of pass rates. Executor must compute sums from raw numbers.

### Page Budget (UPDATED)
- **D-04:** Add ALL content during Phase 17 execution — no cuts, no deferrals. All tasks 17A, 17A-tbd, 17B, 17C, 17D, 17E execute fully as planned.
- **D-04-compress:** Samyak and Le will manually compress the paper to ≤10 pages before April 8 submission using their own editorial judgement. The executor's job is to produce complete content, not to trim.
- **D-04-appendix:** The per-kernel agreement matrix (from `cross_model_comparison.json`) may be moved to appendix by Samyak/Le during compression — executor places it in Section 6.9 main body for now.

### Execution Order Within Phase 17
- **D-05:** Strict Phase 16 gate. Do not start Phase 17 until all three output files listed in the domain boundary exist. Check existence before any paper.tex edit.
- **D-06:** Within Phase 17, execution order:
  1. **Wave 1 (one subagent):** 17A + 17A-tbd combined — fill all `\pending{...}` markers and all `\tbd` cells in one pass through paper.tex (document order). LaTeX compile check after this wave.
  2. **Wave 2 (sequential):** 17B (Section 6.9), then 17C (augmentation examples), then 17D (anonymization subsection). LaTeX compile checkpoint after each.
  3. **Wave 3:** 17E — wire any new figures from Phase 16 into paper.tex, update captions. Final LaTeX compile + page count check.

### Hardware Specs (line 631)
- **D-07:** `\pending{GPU model, CPU model, and OS for the collaborator's evaluation machine.}` at line ~631 stays **as-is**. Add an inline TODO comment: `% TODO(samyak): fill when Niranjan/Le provides machine specs`. Do NOT remove the `\pending{}` macro — Samyak will fill manually before submission.
- **D-07-count:** This means only **17** of the 18 `\pending{...}` markers will be filled by the executor. Line 631 is explicitly excluded.

### Section 6.9 Content
- **D-08:** Section 6.9 (Cross-Model Comparison) inserts after Section 6.8. Must contain:
  1. Overall pass rate comparison with actual chi-squared p-value and Wilson 95% CIs (no placeholder stats)
  2. Per-direction side-by-side for 7 common directions; explicit footnote for `omp_target-to-cuda`
  3. Failure taxonomy comparison: BUILD_FAIL dominance pattern (GPT vs Qwen)
  4. Per-kernel agreement matrix — four-way: both-pass / both-fail / Qwen-only-pass / GPT-only-pass
  5. Effect sizes (Cohen's h) overall and per-direction
- **D-08-framing:** Section 6.9 frames two models as demonstrating ParBench's utility, NOT as a model ranking. Both models are described as "providers" (provider diversity framing, established in Phase 15).

### Claude's Discretion
- Exact prose wording in Section 6.9 and 17C/17D — executor has freedom on sentence-level decisions within the constraints above
- How to present the four-way kernel matrix (table vs prose summary) — executor decides based on available space

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase 17 Plan
- `.planning/phases/17-paper-integration/PLAN.md` — Full task breakdown 17A through 17E, exact grep positions, verification checklist

### Phase 16 Context & Outputs
- `.planning/phases/16-gpt-data-analysis/16-CONTEXT.md` — Decisions on cross_model_comparison.py design (D-03: full 4-stat suite, D-04: four-way kernel matrix)
- `results/analysis/paper_data_gpt41mini.json` — GPT numbers source for 17A + 17A-tbd (must exist before Phase 17 starts)
- `results/analysis/cross_model_comparison.json` — Statistical comparison source for 17B (must exist before Phase 17 starts)
- `results/analysis/error_taxonomy_gpt41mini.json` — Error taxonomy for failure narrative in 17B/17C

### Paper Edit Target
- `docs/paper/latex/paper.tex` — Primary edit target. Executor must grep for actual line numbers before editing (line numbers in PLAN.md are approximate and drift with edits).

### Anonymization Code (for 17D)
- `scripts/evaluation/llm_evaluate.py` line ~570 (`build_translation_prompt()`) — Cross-check the 6 anonymization measures before writing 17D prose

### Master Plan
- `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` §Phase 17 (lines 195-343) — Original phase specification and rationale

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/paper/latex/paper.tex` — `\pending` macro defined at line 36-37 (takes 1 argument: `\pending{text}`); `\tbd` macro at line 39 (no argument: `\tbd`)
- `results/analysis/paper_data.json` — Qwen data schema; paper_data_gpt41mini.json will follow the same schema

### Established Patterns
- All Qwen data fills have inline `% src: paper_data.json > ...` comments — GPT fills must follow the same comment pattern with `% src: paper_data_gpt41mini.json > ...`
- Wilson 95% CIs are standard for all pass rate claims in the paper

### Integration Points
- `tab:overall-pass`: GPT row (line ~690) + Aggregate row (line ~691) — both need fills from paper_data_gpt41mini.json
- `tab:direction-rates`: GPT column (lines ~939-944) — 6 directions filled from data, `omp_target-to-cuda` → "—" with footnote
- Section 6.9 insert point: after Section 6.8 (~line 1000 — verify with grep before inserting)

### GPT Eval Data Confirmed Present
- 897 files in `results/evaluation/azure-gpt-4.1-mini/`
- Directions present: 7 (cuda-to-omp, cuda-to-opencl, omp-to-cuda, opencl-to-cuda, omp-to-opencl, opencl-to-omp, cuda-to-omp_target)
- Direction absent: omp_target-to-cuda → 7-direction fallback locked (D-01)

</code_context>

<specifics>
## Specific Ideas

- **lavamd example (17C):** L4 is PASS — must state this explicitly. Plan notes this was a critical correction from adversarial review.
- **bptree example (17C):** L3 is PASS (partial recovery) then L4 is RUN_FAIL again — state recovery-then-reversion pattern explicitly.
- **Aggregate row in tab:overall-pass:** Sum of counts, NOT average of rates. This is a critical correctness rule (PLAN.md notes this).
- **Section 6.9 stat prerequisite:** Write actual chi-squared p-value and Cohen's h from cross_model_comparison.json — never write placeholder statistics.
- **Provider diversity framing:** GPT-4.1 mini is described as "OpenAI via Azure" in contrast to "Qwen via Together AI" — two providers, not two model rankings.

</specifics>

<deferred>
## Deferred Ideas

- omp_target-to-cuda cross-model comparison — blocked on Le's data. If data arrives, upgrade from 7 to 8 directions (D-01-upgrade check at Phase 17 start).
- Per-kernel agreement matrix as a figure/heatmap — may not fit in 10-page limit; JSON output from Phase 16 is the canonical form. Samyak/Le decide during compression.
- Page budget compression — explicitly deferred to Samyak + Le manual edit after Phase 17 execution completes (D-04-compress).

</deferred>

---

*Phase: 17-paper-integration*
*Context gathered: 2026-04-07 (updated — corrected marker counts, locked omp_target-to-cuda fallback, added strict Phase 16 gate, no-cut page budget policy)*
