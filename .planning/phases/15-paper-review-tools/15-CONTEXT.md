# Phase 15: Paper Review Tools - Context

**Gathered:** 2026-04-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Execute the fixes identified by the SC26 review panel simulation before the April 8 deadline. The panel review is complete (5 reviewer reports + panel-report.md exist). This phase implements 7 specific paper edits plus runs an adversarial multi-agent review of the Phases 16-18 GPT integration plan.

Two deliverables:
1. `docs/paper/latex/paper.tex` updated with 7 fixes (FIX-2a, FIX-2b, FIX-3, SF-1, SF-3, SF-6, SF-7)
2. Adversarial plan review verdict for `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` (Phases 16-18)

</domain>

<decisions>
## Implementation Decisions

### FIX-2b: omp_target McNemar Test
- **D-01:** Report the omp_target McNemar result in S6.5 alongside the other direction pairs. Do NOT drop it from the Bonferroni family. Report Cohen's h = -1.37, p = 0.0625 uncorrected, p = 0.25 Bonferroni-corrected. Note it as the most pronounced effect approaching significance.

### FIX-2c: Augmentation Claim Language
- **D-02:** DO NOT soften augmentation claim language. This was explicitly excluded by the user. Keep current wording ("confirming benchmark validity against training-data memorization concerns").

### GPT Data / Single-Model Reframe
- **D-03:** DO NOT reframe as single-model. DO NOT remove `\pending{}` macros or `\tbd` entries. GPT-4.1 mini data has arrived (897 files at `results/evaluation/azure-gpt-4.1-mini/`) and will be integrated in Phases 16-18. Preserve all two-model framing.

### SF-1: API Cost Data Placement
- **D-04:** Add cost data as an appendix table (not inline in S5.5). Simple 4-row table: total cost ($145.37), cost per task (~$0.13), total tokens (~120M), campaign duration (~6 days). Add a forward-reference sentence in S5.5 pointing to the appendix.
- Data source: `results/analysis/token_analysis.json`

### Plan Structure
- **D-05:** Two plans:
  - **Plan 1** (LaTeX paper edits): FIX-2a, FIX-2b, FIX-3, SF-1, SF-3, SF-6 — all 6 paper.tex changes + appendix additions
  - **Plan 2** (Infrastructure + plan review): SF-7 (LICENSE file) + adversarial multi-agent review of Phases 16-18 plan (`hashed-sauteeing-kite.md`)

### Excluded from Phase 15 Scope
- **D-06:** The following panel items are explicitly OUT of scope for this phase:
  - SF-2: HeCBench spec commit hashes (25 files) — deferred
  - SF-4: XSBench caveat in abstract/intro — deferred
  - NH-1 through NH-7 (nice-to-have items) — camera-ready or future work
  - FIX-1 (GPT data delivery/single-model reframe) — handled in Phases 16-18

### Claude's Discretion
- Exact wording of sentences reporting FIX-2a (Fisher test), FIX-2b (McNemar), and SF-3 (unbalanced design)
- Whether SF-3 unbalanced design clarification goes in abstract text vs. a footnote
- LaTeX table formatting for the appendix cost table
- Whether to add a reference to the appendix cost table in S5.5 as one sentence or a parenthetical
- Commit granularity (one commit per fix vs. one commit for all 6 LaTeX fixes)

</decisions>

<specifics>
## Specific Ideas

- FIX-2a context: The Fisher test (L0 vs pooled L1-L4, OR=0.41, p=0.0037, corrected p=0.0075) uses ALL directions (n=192), NOT the balanced CUDA-to-OMP subset used for Cochran-Armitage (n=120). Augmented code passing MORE than L0 actually strengthens the anti-memorization case — memorization would predict the opposite. The scope difference must be explained when reporting.
- FIX-2b context: R3-STATS explicitly recommended reporting it rather than dropping it. "Most interesting pair" framing is supported.
- FIX-3: The anonymization protocol (kernel-name stripping, comment removal, filename genericization) lives in `scripts/evaluation/llm_evaluate.py` ~lines 578-589. The system message template is ~lines 629-637. A 2-3 sentence inline description goes in S3.4 or S5.1 as well as the appendix listing.
- SF-6: "70% relative increase" (appears in S1 around line 180 and S6.3 around line 874) should become "70% relative increase (15.8 percentage points)" — absolute figure is 22.5% → 38.3%.
- Plan 2 adversarial review: uses 4 parallel agents as specified in `.planning/tmp/gpt-integration-plan-review-handoff.md`. Full instructions are in that file. Produces APPROVED / APPROVED WITH CONDITIONS / BLOCKED verdict.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Panel Review Output (source of all fixes)
- `.planning/phases/15-paper-review-tools/panel-report.md` — Full panel report, priority-ordered fix list, must-fix rationale
- `.planning/phases/15-paper-review-tools/r3-stats-review.md` — Statistical detail for FIX-2a and FIX-2b
- `.planning/tmp/review-fixes-handoff.md` — Exact fix specifications with "What NOT to Do" guardrails

### GPT Integration Plan (for Plan 2 review)
- `/home/samyak/.claude/plans/hashed-sauteeing-kite.md` — The plan to be adversarially reviewed
- `.planning/tmp/gpt-integration-plan-review-handoff.md` — 4-agent review panel design and instructions

### Primary Paper and Data
- `docs/paper/latex/paper.tex` — The paper (1112 lines, Sections S1-S8 + Appendices)
- `results/analysis/statistical_analysis.json` — Fisher exact test and McNemar direction_asymmetry fields
- `results/analysis/token_analysis.json` — API cost data source for SF-1
- `scripts/evaluation/llm_evaluate.py` — Prompt template and anonymization protocol source (~lines 578-637)

### Known State
- `results/evaluation/azure-gpt-4.1-mini/` — GPT-4.1 mini results (897 files, 26.6% pass rate) — present but not yet integrated

</canonical_refs>

<code_context>
## Existing Code Insights

### Paper Structure
- `paper.tex` is 1112 lines; augmentation robustness is S6.4 (Fisher test goes here) and S6.5 (McNemar direction asymmetry)
- Appendices are in `docs/paper/latex/appendices.tex` (separate file, included from paper.tex)
- `\pending{}` macro is defined twice (lines 36-37 duplicate) — do NOT fix this in Phase 15, leave for Phase 16-18
- `\parbench` macro is defined twice (lines 28, 53) — same, leave for GPT integration phase

### Data Files
- `results/analysis/statistical_analysis.json` contains both `augmentation_trends` (Cochran-Armitage) and `direction_asymmetry` (McNemar per direction pair including omp_target)
- `results/analysis/token_analysis.json` contains cost data (grep "145.37" to find the field path)

### Prompt Template
- System message: `llm_evaluate.py` ~lines 629-637
- Anonymization: `llm_evaluate.py` ~lines 578-589 (kernel-name stripping, comment removal, filename genericization)

</code_context>

<deferred>
## Deferred Ideas

- **SF-2** (HeCBench spec commit hash fix — 25 files): Deferred. Not in Phase 15 scope. Could go in Phase 16-18 or a separate cleanup phase.
- **SF-4** (XSBench caveat to abstract/intro): Deferred. Low effort (30 min) but out of Phase 15 scope.
- **NH-4** (Remove MoE architecture claim): Deferred to camera-ready.
- **NH-5** (Prompt sensitivity threat to validity): Deferred to camera-ready.
- **NH-6** (Expand pass@k to k=5): Deferred — requires new eval runs.
- **LaTeX duplicate `\newcommand` fix**: Deferred to Phase 16-18 (GPT integration) per panel report P5.

</deferred>

---

*Phase: 15-paper-review-tools*
*Context gathered: 2026-04-06*
