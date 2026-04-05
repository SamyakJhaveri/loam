# Phase 5: Introduction, Positioning & Characterization Table - Context

**Gathered:** 2026-04-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Write/update the Introduction (Section 1) of paper.tex with quantitative highlights woven into prose, sharpen LASSI differentiation, assemble a second LaTeX characterization table (API coverage + category distribution), and emphasize multi-file translation as a key difficulty dimension. This phase edits text in paper.tex — it consumes data from Phases 2, 3, 4, and 9, but produces no new analysis artifacts.

</domain>

<decisions>
## Implementation Decisions

### Characterization Table Design (CHAR-07)
- **D-01:** Two separate tables in Section 4. The existing `tab:benchmark-characterization` (SLoC, Multi-File, Std.) stays as-is. A new second table is added with API coverage cross-tab (suite rows x CUDA/OMP/OpenCL/OMP-Target columns showing spec counts) and category distribution (12 categories with kernel counts).
- **D-02:** Category data comes from `benchmark_characterization.json` — 12 categories across 35 kernels. Present as a compact section within the second table or as a sub-table, whichever fits best in IEEE double-column format.
- **D-03:** API coverage cross-tab uses spec counts per cell (e.g., Rodinia: 22 CUDA, 22 OMP, 16 OpenCL, 0 OMP-Target). Data from `benchmark_characterization.json > api_coverage`.

### Introduction Quantitative Density (INTRO-01)
- **D-04:** Light touch in Sections 1.1 and 1.2. Main quantitative payload remains in Contributions (1.3) and Key Findings (1.4).
- **D-05:** Section 1.1 (Motivation): Add one-sentence scope teaser — 35 kernels, 5 suites, 80–3,304 SLoC range. No pass rates or failure taxonomy in Motivation.
- **D-06:** Section 1.2 (Gap): Add ParBench vs. ParEval-Repo contrast — "31 of 35 ParBench kernels exceed ParEval-Repo's 133 SLoC threshold, yet kernel isolation achieves 38.0% pass rate vs. 0% at repository level." Quantifies the gap ParBench fills.

### LASSI Differentiation (INTRO-02)
- **D-07:** LASSI comparison paragraph goes in the Gap section (1.2), after the ParEval-Repo paragraph. Complementary tone, not adversarial (per Phase 3 D-07/D-08).
- **D-08:** 4 differentiation dimensions with numbers: (1) augmentation robustness probing (LASSI has none), (2) 5 suites vs 1, (3) 6 directions vs 2, (4) 96 specs vs 10 kernels. Leave "raw vs agentic" and "survey-grounded curation" for Related Work (Section 2).

### Multi-File Translation Emphasis (INTRO-03)
- **D-09:** Multi-file emphasis goes in the Gap section (1.2), alongside the ParEval-Repo kernel isolation contrast. Frame as: beyond isolating kernel translation from build-system generation, ParBench evaluates multi-file coordination — 25% of specs require translating 2+ files, revealing an independent difficulty dimension.
- **D-10:** Multi-file pass rate comparison (single-file 51.3% vs multi-file lower rates, chi-squared p<0.001) supports the claim. Connect to kernel isolation "reviewer defense" from Phase 4 D-03.

### Data Scope for Introduction Numbers (INTRO-01, INTRO-04)
- **D-11:** All-suite Campaign 1 scope (700 tasks, 38.0% [34.5%, 41.6%]) for all introduction headline numbers — Abstract, Contributions (1.3), Key Findings (1.4). This is consistent with the roadmap scope decision.
- **D-12:** Section 6 continues using Rodinia 480-task scope for detailed analysis. The introduction uses the broader scope to represent the full framework evaluation.

### Claude's Discretion
- Exact sentence placement and transitions within each subsection
- Whether the second characterization table uses a single combined layout (API + categories) or two mini-tables
- LaTeX table formatting details (column alignment, caption wording)
- How to handle the transition from existing ParEval-Repo text to new LASSI paragraph in Section 1.2
- Whether to add LaTeX source comments citing `quantitative_findings.json` field paths for new numbers
- How to update existing numbers in Sections 1.3-1.4 from Rodinia scope to all-suite scope (mechanical replacement with verification)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper (primary edit target)
- `docs/paper/latex/paper.tex` — All edits go here. Key sections for Phase 5:
  - Section 1.1 (Motivation, ~line 80): scope teaser insertion
  - Section 1.2 (Gap, ~line 87): ParEval-Repo contrast, LASSI paragraph, multi-file emphasis
  - Section 1.3 (Contributions, ~line 108): update numbers to all-suite scope
  - Section 1.4 (Key Findings, ~line 130): update numbers to all-suite scope
  - Section 4 (~line 530): existing characterization table + new second table
  - **Line numbers are approximate — planner must grep for actual subsection boundaries.**

### Data sources (ground truth for numbers)
- `results/analysis/quantitative_findings.json` — Primary provenance source. Campaign 1 = 700 primary tasks across 5 suites. Key paths: `campaign_1.aggregate_pass_rates.overall` (38.0%, n=700), `campaign_1.failure_taxonomy.status_counts`, `campaign_1.complexity_correlation`
- `results/analysis/benchmark_characterization.json` — All Phase 2 characterization data: SLoC (35 kernels), categories (12), API coverage, multi-file breakdown, language features
- `results/analysis/paper_data.json` — Full 1,248-task aggregate (includes augmented). For all-suite headline numbers.
- `results/analysis/paper_data_rodinia.json` — Rodinia 480-task scope. For Section 6 cross-reference only.
- `results/analysis/sloc_analysis.json` — SLoC per kernel (35 kernels, min 80, max 3304, median 271)

### Prior phase outputs consumed
- `.planning/phases/02-benchmark-characterization-data/02-CONTEXT.md` — D-01: single combined `benchmark_characterization.json`. D-02: multi-file uses `translation_targets > 1`. D-05: category distribution with suite annotations.
- `.planning/phases/03-augmentation-analysis-story/03-CONTEXT.md` — D-07/D-08: LASSI positioning is complementary, brief (1-2 paragraphs). D-09: augmentation figures in `docs/paper/figures/`.
- `.planning/phases/04-methodology-reviewer-defense/04-CONTEXT.md` — D-03: kernel isolation defense uses all-suite numbers (64.2% CUDA-to-OMP, 33.9% BUILD_FAIL). D-05: statistical test rewrite at line ~644.

### Requirements
- `.planning/REQUIREMENTS.md` — INTRO-01 through INTRO-04, CHAR-07

### Related work references
- ParEval-Repo cite key: `\cite{ParEvalRepo2025}` — 0% pass rate, 133 SLoC threshold
- LASSI cite key: `\cite{LASSI2024}` — 10 HeCBench kernels, 80-85% with agentic correction, 2 directions

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `benchmark_characterization.json` has all data needed for the second table: `api_coverage` section (suite x API matrix), `categories` section (12 categories with kernel counts and suite annotations)
- `quantitative_findings.json` has `paper_claims` array mapping claim IDs to exact source values — use for provenance comments in LaTeX
- Existing characterization table LaTeX at lines 547-568 can serve as template for the second table's formatting

### Established Patterns
- Phase 1 established inline LaTeX source comments (e.g., `% src: paper_data.json > field`). Continue this pattern, now pointing to `quantitative_findings.json` and `benchmark_characterization.json` field paths.
- Phase 4 established the pattern of using all-suite Campaign 1 numbers for methodology claims.
- IEEE double-column table width: ~3.5 inches per column for `table` environment, ~7 inches for `table*`.

### Integration Points
- Sections 1.3 and 1.4 currently cite Rodinia 480-task numbers (36.2%, 30.8% BUILD_FAIL, etc.) — these must be updated to all-suite 700-task equivalents (38.0%, 33.9% BUILD_FAIL, etc.)
- The new LASSI paragraph in Section 1.2 cross-references Related Work Section 2 which already has a LASSI comparison table
- The second characterization table in Section 4 adds data alongside the existing table at line 547
- Phase 4's kernel isolation paragraph in Section 3.4 already cites 64.2% CUDA-to-OMP across all suites — the intro's ParEval-Repo contrast (38.0% all-suite overall) should be consistent

</code_context>

<specifics>
## Specific Ideas

- Niranjan (advisor, April 2): "Benchmark characterization table with concrete numbers" was a directive — the second table directly addresses this
- The intro LASSI paragraph should echo the complementary framing already in paper.tex Section 7.4 (written in Phase 3)
- Multi-file pass rate gap (single-file 51.3% vs multi-file lower, p<0.001) is a strong finding — make it concrete in the Gap section, not vague
- All number updates from Rodinia to all-suite scope must be mechanically verified against `quantitative_findings.json` to avoid introducing stale data

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-introduction-positioning-characterization-table*
*Context gathered: 2026-04-05*
