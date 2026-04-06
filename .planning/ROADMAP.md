# Roadmap: SC26 Paper Completion Sprint

## Overview

This roadmap delivers a submission-ready SC26 paper by April 8, 2026. The work flows from verifying existing data claims (ground truth), through producing new quantitative characterization and augmentation analysis, to writing methodology defense and assembling polished introduction text with the characterization table. Every phase produces artifacts that downstream phases consume -- verification feeds characterization, characterization feeds the introduction, and augmentation analysis feeds both the augmentation story and motivating examples.

## Contingency: GPT-4.1 Mini Data

If Le's GPT-4.1 mini data has not arrived by **April 7, 2026 EOD**:
1. Remove all `\tbd` and `\pending{}` macros from paper.tex
2. Remove GPT-4.1 mini row from T2 table
3. Frame as "single-model evaluation with framework designed for multi-model extension"
4. Move GPT-4.1 mini to Future Work paragraph
5. This is a ~30-minute mechanical task, not a paper restructure

## Scope Decision: Section 6 Data Scope

**Decision (2026-04-05):** Section 6 primary analysis uses **Rodinia 480-task scope** (preserving existing Section 6 structure). A new **Cross-Suite Comparison subsection** uses the 700-task all-suite scope from `quantitative_findings.json`. Abstract headline uses all-suite figures. Methodology defense (Phase 4) uses all-suite Campaign 1 numbers (700 tasks).

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Data Verification & Ground Truth** - Cross-check every existing numerical claim and table against on-disk data files
- [ ] **Phase 2: Benchmark Characterization Data** - Produce all quantitative characterization metrics (SLoC, categories, API coverage, language features, multi-file breakdown)
- [ ] **Phase 3: Augmentation Analysis & Story** - Build per-kernel augmentation matrix, identify motivating examples, produce trend graphs, write LASSI positioning
- [ ] **Phase 4: Methodology & Reviewer Defense** - Write methodology justifications for kernel isolation, statistical tests, reproducibility, and verification approach
- [ ] **Phase 5: Introduction, Positioning & Characterization Table** - Weave quantitative highlights into introduction, sharpen differentiation, assemble LaTeX characterization table

## Phase Details

### Phase 1: Data Verification & Ground Truth
**Goal**: Every numerical claim and table in Sections 1-7 is verified against actual data files on disk, with no stale or incorrect values remaining, and all analysis files regenerated fresh
**Depends on**: Nothing (first phase)
**Requirements**: VERIFY-01, VERIFY-02, VERIFY-03, VERIFY-04, VERIFY-05, VERIFY-06
**Success Criteria** (what must be TRUE):
  1. Running a cross-check of every number in Sections 1-7 against paper_data.json, statistical_analysis.json, and selfrepair_analysis.json produces zero discrepancies
  2. Suite-summary table (tab:suite-summary) kernel count, spec count, and API counts match manifest.jsonl entry count and specs/ file count on disk
  3. Augmentation level definitions table matches LEVEL_FRACTIONS dictionary values in c_augmentation/augment_dataset.py
  4. Model config table contains only Qwen 3.5 397B and GPT-4.1 mini with accurate descriptions, zero Gemini references
  5. Hardware/software table matches actual nvcc --version, gcc --version, and nvidia-smi output on the Linux machine
  6. All analysis files and figures regenerated fresh at end of phase
**Plans**: 5 plans in 2 waves

Plans:
- [x] 01-01-PLAN.md -- Verify Abstract + S1 + S3 (data freeze, augmentation levels, headline numbers)
- [x] 01-02-PLAN.md -- Verify S4 + S5 (suite-summary, hardware, model config, Gemini sweep)
- [x] 01-03-PLAN.md -- Verify S6.1-S6.5 (aggregate results, failure taxonomy, self-repair, augmentation rates)
- [x] 01-04-PLAN.md -- Verify S6.6-S6.8 + S7 (per-kernel, directions, pass@k, stats, discussion)
- [x] 01-05-PLAN.md -- Regenerate all analysis files + figures (depends on 01-01 through 01-04)

### Phase 2: Benchmark Characterization Data
**Goal**: All quantitative benchmark characterization metrics are computed, saved to analysis files, and ready for the paper table and introduction
**Depends on**: Phase 1 (verified suite-summary ensures correct kernel/spec counts as input)
**Requirements**: CHAR-01, CHAR-02, CHAR-03, CHAR-04, CHAR-05, CHAR-06
**Success Criteria** (what must be TRUE):
  1. SLoC analysis covers all 35 kernels (not just 18) and results are saved to a JSON or CSV file in results/analysis/
  2. Domain category distribution (12 categories) is computed from manifest.jsonl and saved with counts and percentages
  3. API coverage cross-tab (suite rows x API columns) exists as a saved artifact and matches spec file counts on disk
  4. Single-file vs multi-file translation breakdown exists per suite and per API with exact counts
  5. Language feature grep results and language standard distribution are saved, covering Rodinia + XSBench source directories
**Plans**: 3 plans in 2 waves

Plans:
- [x] 02-01-PLAN.md -- [Wave 1] Complete characterization script (all 6 metrics: SLoC, categories, API coverage, multi-file, language features, language standards)
- [x] 02-02-PLAN.md -- [Wave 1] Comprehensive unit tests for characterization script (20+ tests, ground-truth validation)
- [x] 02-03-PLAN.md -- [Wave 2, depends on 02-01] Independent validation/cross-check script (8 check functions, different code path)

### Phase 3: Augmentation Analysis & Story
**Goal**: The augmentation section has concrete per-kernel evidence (matrix, examples or strengthened null-result), publication-quality graphs, and clear LASSI positioning
**Depends on**: Phase 1 (verified augmentation level definitions ensure correct level semantics)
**Requirements**: AUG-01, AUG-02, AUG-03, AUG-04
**Success Criteria** (what must be TRUE):
  1. Per-kernel x per-level status matrix exists as a JSON file (results/analysis/augmentation_per_kernel_matrix.json) built from raw Qwen result JSONs for cuda-to-omp L0-L4
  2. Either 2-3 specific kernels showing PASS-to-FAIL degradation are identified with exact level/direction, OR the null-result interpretation includes per-kernel evidence showing uniform PASS across levels
  3. Augmentation trend graphs (per-kernel + aggregate) exist as publication-quality PDF and PNG files using Okabe-Ito color palette
  4. LASSI augmentation positioning paragraphs exist in paper.tex framing ParBench augmentation as complementary (robustness probing vs. agentic correction)
**Plans**: 3 plans in 2 waves

Plans:
- [x] 03-01-PLAN.md -- [Wave 1] Augmentation matrix analysis script + tests (AUG-01, AUG-02: per-kernel matrix, pattern classification, aggregates, JSON+MD output)
- [x] 03-02-PLAN.md -- [Wave 2, depends on 03-01] Publication-quality augmentation figures (AUG-04: heatmap + aggregate trend with Wilson CIs)
- [x] 03-03-PLAN.md -- [Wave 1] LASSI positioning paragraphs in paper.tex Section 7.4 (AUG-03: complementary framing)

### Phase 4: Methodology & Reviewer Defense
**Goal**: Section 3-5 methodology descriptions are precise enough to withstand SC-level reviewer scrutiny, with explicit justifications for every methodological choice
**Depends on**: Phase 1 (verified hardware table and version pins feed reproducibility claims)
**Requirements**: METHOD-01, METHOD-02, METHOD-03, METHOD-04
**Success Criteria** (what must be TRUE):
  1. Kernel isolation methodology paragraph cites the ParEval-Repo 0% vs ParBench 64.2% XSBench comparison with exact numbers from quantitative_findings.json
  2. Statistical test choices (Cochran-Armitage, McNemar, Wilson CI) are each justified in 1-2 sentences explaining why that test fits the data structure
  3. Reproducibility paragraph lists exact version pins: CUDA version, nvcc version, gcc version, OS, GPU model, model API versions, and ParBench commit hash
  4. Conjunction verification (exit_code AND stdout_pattern) is justified against alternatives (BLEU, compilation-only) with a concrete example of why weaker verification would misclassify a result
**Plans**: 2 plans in 2 waves

Plans:
- [x] 04-01-PLAN.md -- [Wave 1] Kernel isolation defense paragraph (Section 3.4) + conjunction verification defense paragraph (Section 3.2) with provenance-tracked numbers
- [x] 04-02-PLAN.md -- [Wave 2, depends on 04-01] Statistical test justification rewrite (Section 5.4) + Bonferroni alpha update (Sections 6.6, 6.8) + reproducibility version pins (Section 5.5)

### Phase 5: Introduction, Positioning & Characterization Table
**Goal**: The introduction reads as a compelling benchmark paper with quantitative substance, and the characterization table is the anchor of Section 4
**Depends on**: Phase 2 (characterization data for table and intro numbers), Phase 3 (augmentation framing for intro), Phase 4 (methodology framing for intro)
**Requirements**: INTRO-01, INTRO-02, INTRO-03, INTRO-04, CHAR-07
**Success Criteria** (what must be TRUE):
  1. Introduction contains quantitative highlights (35 kernels, 96 specs, 4 APIs, SLoC range, multi-file percentage, augmentation levels) woven into prose, not as a bullet list
  2. LASSI differentiation paragraph includes at least 4 concrete dimensions (augmentation, suite count, direction count, spec count) with numbers
  3. Multi-file translation emphasis appears in both intro and Section 4 with the exact multi-file percentage and a kernel isolation "reviewer defense" callback
  4. "Gap in Existing Evaluation" paragraph uses concrete comparative data from the characterization table (e.g., SLoC range, category coverage) to quantify ParBench's contribution
  5. LaTeX characterization table (tab:benchmark-characterization) is present in paper.tex Section 4 with SLoC, categories, multi-file status, API coverage, and language features
**Plans**: 2 plans in 2 waves

Plans:
- [x] 05-01-PLAN.md -- [Wave 1] Update Section 1: scope teaser (1.1), ParEval-Repo contrast + LASSI differentiation + multi-file emphasis (1.2), all-suite number updates (1.3, 1.4)
- [x] 05-02-PLAN.md -- [Wave 2, depends on 05-01] Insert category distribution table (tab:category-distribution) in Section 4 with 10 categories and suite annotations

## Progress

**Execution Order:**

```
Phase 1 (DONE) ──► Phase 2 (DONE) ──► Phase 7 (DONE) ──► Phase 8 (DONE) ──► Phase 12 (DONE) ──► Phase 12.1 ──► Phase 11
                                                      └──► Phase 9 (DONE) ──────────────────────────────┘
Phase 3 (DONE) ──► Phase 13 ─────────────────────────────────────────────────────────────────────────────┘
Phase 4 (DONE) ──────────────────────────────────────────────────────────────────────────────────────────┘
Phase 5 (DONE) ─────────────────────────────────────────────────────────────────────────────────────────┘
Phase 14 (verification & housekeeping — independent) ──────────────────────────────────────────────────
```

**Critical path:** 1 → 2 → 7 → 9 → 12 → 12.1 → 11 (analysis → findings → fixes → paper)
**Gap closure path:** 7 → 12 → 12.1 → 11 (fix stale values + P0 fixes before integration)
**Parallel track A:** Phase 8 (figures) → Phase 13 (wiring) → Phase 11
**Parallel track B:** Phases 4, 5 COMPLETE — outputs feed into Phase 11
**Dropped:** Phase 6 (evidence already in existing data), Phase 10 (write directly from quantitative_findings.json)
**Independent:** Phase 14 (verification backfill) can run anytime
**Inserted:** Phase 12.1 (SC26 review P0 quick fixes — urgent factual accuracy)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Verification & Ground Truth | 5/5 | Complete | 2026-04-03 |
| 2. Benchmark Characterization Data | 3/3 | Complete | 2026-04-03 |
| 3. Augmentation Analysis & Story | 3/3 | Complete | 2026-04-04 |
| 4. Methodology & Reviewer Defense | 2/2 | Complete | 2026-04-05 |
| 5. Introduction, Positioning & Characterization Table | 2/2 | Complete | 2026-04-05 |
| 6. RSBench Single-File Re-spec Experiment | — | **Dropped** | - |
| 7. Full Analysis Regeneration | 2/2 | Complete | 2026-04-04 |
| 8. Figure Regeneration | 2/2 | Complete | 2026-04-04 |
| 9. Objective Quantitative Analysis | 3/3 | Complete | 2026-04-05 |
| 10. Qualitative Analysis & Research Narrative | — | **Dropped** (merged into Phase 11) | - |
| 11. Paper TeX Integration | 4/4 | Complete   | 2026-04-06 |
| 12. Fix Stale Pass@k Values | 3/3 | Complete   | 2026-04-06 |
| 12.1. SC26 Review P0 Quick Fixes | 1/1 | Complete   | 2026-04-06 |
| 13. Paper.tex Figure & Table Wiring | 2/2 | Complete   | 2026-04-06 |
| 14. Verification Backfill & Housekeeping | 0/1 | Not started (scope expanded: +artifact README, +API env docs) | - |

### Phase 6: RSBench Single-File Re-spec Controlled Experiment — **DROPPED**

**Status:** Dropped (2026-04-05). The multi-file translation hypothesis is already confirmed by existing data: 48.5% single-file vs 12.5% multi-file pass rate (from `quantitative_findings.json`). No controlled experiment needed — the existing observational comparison is sufficient for the SC26 paper. Use the controlled comparison in paper prose instead.
**Directory:** `.planning/phases/06-rsbench-singlefile-respec-experiment/`

### Phase 7: Full Analysis Regeneration

**Goal:** Re-run every analysis script against the complete 1,248-file Qwen 3.5 397B evaluation dataset (Rodinia 880 + HeCBench 224 + XSBench 48 + RSBench 48 + mixbench 48) to produce fresh JSON and Markdown outputs. This is the data foundation — every number in the paper traces back to these files. Scripts must process ALL suites (not just Rodinia's 480-task subset).
**Depends on:** Phase 1 (verified ground truth), Phase 2 (characterization data)
**Requirements**: REGEN-01 through REGEN-10
**Success Criteria** (what must be TRUE):
  1. `eval_summary.json` reflects all 1,248 Qwen result files across 5 suites (not just Rodinia 480) — verify `total_tasks` field
  2. `paper_data.json` regenerated TWICE: once with `--suite rodinia` (preserves 480-task primary campaign data for Sections 6.1-6.5), once WITHOUT `--suite` (full 1,248-task aggregate for cross-suite comparison)
  3. `error_taxonomy.json` covers failure modes across ALL suites — verify HeCBench, XSBench, RSBench, mixbench failures appear
  4. `selfrepair_analysis.json` includes cross-suite self-repair rates — verify non-Rodinia entries exist
  5. `statistical_analysis.json` includes cross-suite statistical tests — verify per-suite breakdowns present
  6. `sloc_analysis.json` unchanged from Phase 2 (all 35 kernels already covered) — re-validate, don't recompute
  7. `token_analysis.json` includes cost estimates for all 1,248 tasks — verify total_tasks matches
  8. `benchmark_characterization.json` unchanged — validate_characterization.py passes with zero errors
  9. `translation_complexity.csv` covers all suites (currently Rodinia+XSBench only — may need script update)
  10. If Phase 3 plan 03-01 completed: `augmentation_per_kernel_matrix.json` also regenerated
  11. No script errors, exceptions, or warnings during execution
  12. All Markdown (.md) companion files regenerated alongside their JSON counterparts

**Exact commands (run in order):**
```
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# 1. Aggregate eval summary (reads ALL model dirs)
python3 scripts/evaluation/analyze_eval.py --project-root . --model together-qwen-3.5-397b-a17b

# 2a. Paper data — Rodinia primary campaign (480 tasks, preserves existing Section 6 scope)
python3 scripts/analysis/generate_paper_data.py --suite rodinia --output results/analysis/paper_data_rodinia.json -v

# 2b. Paper data — ALL suites (1,248 tasks, cross-suite comparison)
python3 scripts/analysis/generate_paper_data.py --output results/analysis/paper_data.json -v

# 3. Error taxonomy
python3 scripts/analysis/build_error_taxonomy.py --project-root .

# 4. Self-repair analysis
python3 scripts/analysis/selfrepair_analysis.py --project-root .

# 5. Statistical analysis
python3 scripts/analysis/statistical_analysis.py --project-root . -v

# 6. Token analysis
python3 scripts/analysis/token_analysis.py --project-root .

# 7. Translation complexity (check if needs --suite update)
python3 scripts/analysis/classify_translation_pairs.py --project-root .

# 8. Validate characterization (no recompute — Phase 2 output is canonical)
python3 scripts/analysis/validate_characterization.py --project-root .
```

**Plans**: 2 plans in 1 wave

Plans:
- [x] 07-01-PLAN.md -- [Wave 1] Run analysis scripts 1-5 (eval summary, paper data ×2, error taxonomy, self-repair, statistical) — these are the core paper data sources
- [x] 07-02-PLAN.md -- [Wave 1] Run analysis scripts 6-8 (token, complexity, validation) + verify all outputs — these are supporting data and quality checks

### Phase 8: Figure Regeneration

**Goal:** Re-run `scripts/generate_paper_figures.py` against the refreshed Phase 7 analysis outputs to produce fresh publication-quality figures (PDF + PNG) for the SC26 paper. All 7 main-body figures (F2-F7 + architecture) and 4 appendix figures (C.1-C.4) plus the T2 LaTeX table must reflect the complete 1,248-task dataset. The script may need updates if it currently only processes Rodinia data or if new suites introduce new kernels/directions not yet in the figure logic.
**Depends on:** Phase 7 (needs fresh analysis JSON/CSV outputs)
**Requirements**: FIG-01 through FIG-07
**Success Criteria** (what must be TRUE):
  1. All existing figures regenerated: f2_repo_vs_kernel.pdf, f3_kernel_model_heatmap.pdf, f4_failure_taxonomy.pdf, f5_pass_at_k_by_direction.pdf, f6_xsbench_comparison.pdf, f7_augmentation_robustness.pdf
  2. All appendix figures regenerated: c1_repair_transition_matrix.pdf, c2_repair_rate_by_direction.pdf, c3_transform_frequency.pdf, c4_selection_funnel.pdf
  3. LaTeX table t2_model_comparison.tex regenerated
  4. PNG versions alongside every PDF for web/review use
  5. F3 (kernel×model heatmap) includes ALL suites' kernels — not just Rodinia 18
  6. F4 (failure taxonomy) covers failure modes across ALL suites
  7. F7 (augmentation robustness) uses fresh L0-L4 data from paper_data.json
  8. If generate_paper_figures.py needed updates (new suites, new kernels), the changes are minimal and tested
  9. No matplotlib warnings, missing data placeholders, or empty subplots
  10. parbench_architecture.drawio exported to PDF (manual or script)

**Exact commands:**
```
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate

# Regenerate all figures
python3 scripts/generate_paper_figures.py --project-root .

# Verify outputs exist
ls -la docs/paper/figures/*.pdf docs/paper/figures/*.png
```

**Risk:** `generate_paper_figures.py` may hardcode Rodinia kernel names or 480-task counts. Audit the script's data loading before running. If it reads from `paper_data.json`, check whether it uses the Rodinia-only or full-dataset version.

**Plans**: 2 plans in 2 waves

Plans:
- [x] 08-01-PLAN.md -- [Wave 1] Update script constants (2-model layout, 5-suite coverage), redesign F3 heatmap (29 kernels x 6 directions with suite grouping), F4 taxonomy (all suites), F6 (cross-suite bar chart), F7 (Qwen-only)
- [x] 08-02-PLAN.md -- [Wave 2, depends on 08-01] Restructure T2 table (2-model layout), run full figure generation, verify all 10 figures + T2 table output

### Phase 9: Objective Quantitative Analysis

**Goal:** Produce a comprehensive, structured quantitative findings document (`results/analysis/quantitative_findings.json` + `.md`) that extracts every publishable number from the Phase 7 analysis outputs. This document becomes the single source of truth for paper claims — every number in paper.tex must trace to a specific field in this file. The analysis must cover all dimensions: per-suite, per-direction, per-level, per-kernel, per-complexity-class, and cross-cutting comparisons.
**Depends on:** Phase 7 (fresh analysis JSONs required)
**Requirements**: QUANT-01 through QUANT-14
**Success Criteria** (what must be TRUE):
  1. **Aggregate pass rates** by suite (Rodinia, XSBench, RSBench, mixbench, HeCBench) with Wilson 95% CIs and sample sizes
  2. **Per-direction pass rates** for all 6 standard directions (cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp) + omp_target case-study directions, with CIs
  3. **Direction asymmetry analysis**: cuda→omp vs omp→cuda, cuda→opencl vs opencl→cuda — McNemar's test p-values, paired differences, which direction is "easier" and by how much
  4. **Per-augmentation-level pass rates** (L0-L4) with Cochran-Armitage trend test p-value and Cohen's h effect sizes between adjacent levels
  5. **Failure taxonomy distribution**: BUILD_FAIL / RUN_FAIL / VERIFY_FAIL / EXTRACTION_FAIL counts and percentages, per-suite and aggregate, with the most common build error categories from error_taxonomy.json
  6. **Self-repair effectiveness**: overall repair rate, per-failure-type repair rates, regression rate, mean attempts to success, per-suite breakdown
  7. **Pass@k estimates** for k=1,3,5,10 from the s0/s1/s2 seed variants, per-direction and aggregate
  8. **Per-kernel difficulty tiers**: rank all 33+ kernels by L0 pass rate across directions, identify top-5 easiest and top-5 hardest, note any anomalous per-direction patterns (e.g., backprop asymmetry)
  9. **Translation complexity correlation**: pass rate by complexity class (single_file, multi_to_single, single_to_multi, multi_to_multi) — is multi-file significantly harder? Chi-squared test
  10. **Cross-suite comparison**: Rodinia aggregate vs XSBench vs RSBench vs mixbench — are newer/smaller suites easier or harder? Why? (SLoC correlation, multi-file fraction)
  11. **Token cost analysis**: total input/output tokens, estimated cost per task, cost per PASS, cost per suite
  12. **SLoC correlation**: Spearman/Pearson correlation between kernel SLoC and pass rate — is larger code harder to translate?
  13. **OpenCL kernel-only effect**: compare pass rates for X-to-OpenCL (kernel-only translation) vs X-to-OMP (full program translation) — does kernel-only translation have higher pass rates?
  14. **Every number has a provenance trail**: each finding includes the source file path, field name, and exact value so paper.tex claims are auditable

**Output format:** JSON with sections matching the 14 criteria above, plus a Markdown companion with tables ready to copy-paste into paper sections.

**Plans**: 3 plans in 3 waves

Plans:
- [x] 09-01-PLAN.md -- [Wave 1] Create quantitative_findings.py with data pipeline, campaign separation, and dimensions 1-5 (aggregate, direction, asymmetry, augmentation, failure taxonomy) + provenance framework
- [x] 09-02-PLAN.md -- [Wave 2, depends on 09-01] Extend script with dimensions 6-13 (self-repair, pass@k, per-kernel tiers, complexity, cross-suite, token cost, SLoC correlation, OpenCL effect) + paper_claims mapping
- [x] 09-03-PLAN.md -- [Wave 3, depends on 09-01+02] Implement --validate: 10+ spot-checks, cross-checks, consistency checks, paper claims pre-audit

### Phase 10: Qualitative Analysis and Research Narrative — **DROPPED**

**Status:** Dropped (2026-04-05). The intermediate qualitative_narrative.md document was an over-engineered artifact that would not appear in the paper. Phase 11 will write qualitative claims directly from `quantitative_findings.json` + Phase 3/9 outputs. QUAL-01 through QUAL-07 narrative goals are absorbed into Phase 11's section-by-section writing tasks.
**Original depends on:** Phase 9
**Original requirements**: QUAL-01 through QUAL-07 (now addressed inline during Phase 11)

### Phase 11: Paper TeX Integration

**Goal:** Update `docs/paper/latex/paper.tex` so that every hardcoded number, table, figure reference, and narrative claim reflects the complete 1,248-task Qwen 3.5 397B dataset. The paper must be internally consistent: Abstract numbers match Section 6 numbers match figure captions match table footnotes. Every data claim must be traceable to a specific field in `results/analysis/quantitative_findings.json` or `paper_data.json`. Qualitative claims must be grounded directly in Phase 9 quantitative findings and Phase 3 augmentation outputs (Phase 10 narrative document was dropped — write directly from data). Additionally, this phase absorbs SC26 simulated review P0/P1 items requiring new analysis or substantive narrative changes (items that could not be handled as quick text fixes in Phase 12.1, and could not be added to already-completed Phases 4/5). The goal is a submission-ready draft where no reviewer can find a stale, unsubstantiated, or misleading claim.
**Depends on:** Phase 8 (fresh figures), Phase 9 (quantitative findings), Phase 4 (methodology defense text), Phase 12.1 (P0 quick fixes)
**Requirements**: TEX-01 through TEX-09
**SC26 Review Items (absorbed from Phases 4/5 which are already complete):**
  - P0-6: Cochran-Armitage power analysis — compute MDES at 80% power for n=24; either run on all 142 L0 pairs or report power limitation honestly (Raised by R2, R3, R5)
  - P0-7: Document HeCBench version/commit hash in Section 5 reproducibility (Raised by R4)
  - P1-8: Deepen VERIFY_FAIL analysis — add 5-10 case studies showing actual parallel logic errors: wrong reduction scope, race conditions, incorrect thread mapping (Raised by R1)
  - P1-9: Nuance "syntax vs reasoning" dichotomy — retained cudaMalloc in OMP = memory model reasoning failure, not just syntax. Reframe as spectrum (Raised by R1, R5)
  - P1-11: Ground per-kernel difficulty tiers in HPC concepts — Easy = regular parallelism + structured memory. Hard = irregular parallelism + data-dependent control flow (Raised by R1)
  - P1-14: Address XSBench 0% comparison honestly — ParBench also gets 0% on XSBench; acknowledge rather than implying kernel isolation solves the problem (Raised by R5)
  - P1-15: Reduce Discussion section redundancy — S7.1-S7.5 restate S6 findings; use page budget for deeper analysis (Raised by R5)
  - P1-16: Soften Cochran-Armitage interpretation — "failure to reject H0 ≠ evidence for H0"; change to "consistent with structural failures, though sample size limits detectable effect" (Raised by R2, R3)
  - P1-17: Report exact eval campaign commands with all flags in Section 5 (Raised by R4)
  - P1-19: McNemar power analysis caveat — n_discordant=6-9 gives effectively zero power; acknowledge this prominently (Raised by R3, R5)
**Success Criteria** (what must be TRUE):
  1. **Abstract** (TEX-01): Headline numbers updated — kernel count, spec count, suite count, API count, aggregate pass rate with CI, augmentation verdict, key finding. Every number matches Section 6.
  2. **Section 1 Introduction** (TEX-02): Quantitative highlights woven into prose (35 kernels, 96+ specs, 4 APIs, SLoC range 80-3304, multi-file %, augmentation levels). LASSI differentiation with ≥4 concrete dimensions. "Gap in existing evaluation" paragraph with comparative data.
  3. **Section 3 Design** (TEX-03): Architecture description verified against actual codebase. Spec-as-contract example uses a real spec. Kernel-centric translation explained with XSBench comparison. File role taxonomy (prompt_payload, support_files, verification_only, translation_targets) accurate.
  4. **Section 4 Augmentation** (TEX-04): Level definitions match `LEVEL_FRACTIONS` in `augment_dataset.py`. Cochran-Armitage p-value with MDES power analysis (P0-6). Softened interpretation (P1-16). Per-kernel evidence or strengthened null-result narrative from Phase 3. LASSI positioning from Phase 3 LASSI paragraphs. McNemar power caveat (P1-19).
  5. **Section 5 Methodology** (TEX-05): Suite-summary table matches manifest.jsonl counts. Hardware/software table matches actual system. Model config table accurate for Qwen 3.5 397B. Conjunction verification justified. Reproducibility pins including HeCBench commit hash (P0-7). Exact eval campaign commands with all flags (P1-17).
  6. **Section 6 Results** (TEX-06 — largest section): ALL aggregate pass rates, per-direction rates, failure taxonomy percentages updated. VERIFY_FAIL deepened with 5-10 case studies (P1-8). "Syntax vs reasoning" reframed as spectrum (P1-9). Per-kernel tiers grounded in HPC concepts (P1-11). XSBench 0% comparison addressed honestly (P1-14). Direction asymmetry with McNemar p-values + power caveat.
  7. **Section 7 Discussion** (TEX-07): Redundancy reduced (P1-15) — use freed page budget for deeper analysis. Threats to validity updated. Future work grounded in actual findings.
  8. **Section 8 Related Work** (TEX-08): ParBench positioned against LASSI, TransCoder, OMPify, HPC-Coder-v2, CodeRosetta, SWE-bench, HumanEval with concrete differentiators.
  9. **Cross-consistency check** (TEX-09): Run a final grep-based audit: extract every percentage and count from paper.tex and verify each against quantitative_findings.json or paper_data.json. Zero unverified numbers remain.

**Key constraint:** The paper is ~10 pages IEEE double-column. Every added sentence must earn its space. Prefer precise numbers over vague claims. Prefer one well-evidenced finding over three hand-wavy observations.

**Plans**: 4 plans in 4 waves

Plans:
- [x] 11-01-PLAN.md -- [Wave 1] Appendix D structure + float migration: move 17 floats to appendix, condense per-kernel table, inline S5 methodology key facts
- [x] 11-02-PLAN.md -- [Wave 2, depends on 11-01] Verify/update Abstract, S1, S2, S3, S8 numbers and related work positioning against paper_data.json
- [x] 11-03-PLAN.md -- [Wave 3, depends on 11-01+02] SC26 review items: P0-6 MDES power analysis, P1-8 VERIFY_FAIL case studies, P1-15 S7 Discussion merge (7->3 subsections), P0-7/P1-9/P1-11/P1-14/P1-16/P1-17/P1-19 brief items
- [x] 11-04-PLAN.md -- [Wave 4, depends on 11-03] Automated cross-consistency audit script (TEX-09)

### Phase 12: Fix Stale Pass@k Values in Paper.tex

**Goal:** Update every numerical claim in paper.tex (Abstract, Sections 1, 5, 6.1-6.8, 7, and 8) from stale Rodinia-only 480-task scope to the all-suite 710-task scope using paper_data.json as the single ground truth, closing the VERIFY-01 regression.
**Depends on:** Phase 7 (needs fresh paper_data.json as ground truth)
**Requirements**: VERIFY-01
**Gap Closure:** Closes VERIFY-01 regression from v1.0 milestone audit (BLOCKER)
**Success Criteria** (what must be TRUE):
  1. All pass@k values in paper.tex Sections 6.7-6.8 match paper_data.json
  2. All numerical claims across Abstract, S1, S5, S6.1-S6.8, S7, S8 reflect 710-task all-suite scope
  3. Per-kernel table expanded from 18 Rodinia rows to 31 all-suite rows
  4. Cochran-Armitage updated to z=0.0, p=1.0 (from paper_data.json)
  5. Self-repair narrative uses 70% relative increase (not "doubles")
  6. Zero stale values remain (no 480, no 36.2%, no 65.0%, no z=-0.17)

**Plans**: 3 plans in 3 waves

Plans:
- [x] 12-01-PLAN.md -- [Wave 1] Update Abstract, S1, S5.2-5.3, S6.1-6.2, S6.4-6.5 (aggregate stats, failure taxonomy, self-repair, augmentation)
- [x] 12-02-PLAN.md -- [Wave 2, depends on 12-01] Expand S6.3 per-kernel table, update S6.6-6.8, S7, S8, final stale-value sweep
- [x] 12-03-PLAN.md -- [Wave 3, gap closure] Add reader-visible explanation of 4 excluded kernels (kmeans, mummergpu, hybridsort, huffman) in S6.3 and S7

### Phase 12.1: SC26 Review P0 Quick Fixes (INSERTED)

**Goal:** Fix all factual accuracy issues in paper.tex flagged by the SC26 simulated peer review (average score 53.2, Weak Reject). All items are targeted text edits — no new analysis scripts or data regeneration required. These fixes must land BEFORE Phase 11 integration to avoid propagating errors.
**Depends on:** Phase 12 (stale pass@k values already fixed)
**Triggered by:** SC26 simulated review panel (2026-04-05), 5 reviewers, P0 items 2-5 + P1 items 10, 18
**Success Criteria** (what must be TRUE):
  1. Table 1 (line ~196): No longer claims "~2,500 eval tasks" or "2 models" — shows accurate current numbers (1,136 tasks, 1 model, with note that GPT-4.1 mini pending)
  2. 700-vs-710 inconsistency resolved: Lines ~333-335 (S3.2) use 710 denominator (not 700 from quantitative_findings.json campaign_1); Lines ~388-389 (S3.4) use 241/710 (not 237/700). Source: paper_data.json primary_campaign total=710
  3. Table 3 (line ~509): CUDA execution model reads "SIMT (warps of 32 threads)" not "SPMD"
  4. All ParBench-specific "greedy-decode pass@1" references renamed to "greedy pass rate"; other benchmarks' pass@1 references preserved
  5. Table 3 CUDA "Single file" claim updated to reflect that 51% of CUDA specs are multi-file (per paper's own Section 4 finding)
**Plans**: 1 plan (single wave — all edits are independent)

Plans:
- [x] 12.1-01-PLAN.md -- Fix 5 factual accuracy issues in paper.tex (Table 1, 700/710, SIMT/SPMD, pass@1 terminology, Table 3 single-file)

### Phase 13: Paper.tex Figure & Table Wiring

**Goal:** Wire regenerated Phase 8 figures and Phase 3 augmentation figures into paper.tex by fixing stale references, updating captions, and adding missing `\includegraphics` and `\input` commands. Also export the architecture diagram (Figure 1) from .drawio to PDF — currently the most-referenced figure in the paper is a placeholder. This closes 4 integration gaps and 2 E2E flow breaks identified by the milestone audit, plus P0-3 from SC26 review.
**Depends on:** Phase 8 (figures on disk), Phase 3 (aug figures on disk)
**Requirements**: AUG-04
**Gap Closure:** Closes 4 integration gaps + 2 E2E flow breaks from v1.0 milestone audit + P0-3 (Figure 1)
**SC26 Review Items:**
  - P0-3: Export `parbench_architecture.drawio` → PDF/PNG for Figure 1 (Raised by R1, R5)
**Success Criteria** (what must be TRUE):
  1. F6 reference updated: `f6_xsbench_comparison.pdf` → `f6_cross_suite_comparison.pdf` at paper.tex line ~1096, label renamed `fig:xsbench` → `fig:cross-suite`, caption updated for cross-suite framing
  2. F3 caption updated to reflect single-panel 29-kernel x 6-direction design (not "Triple-panel")
  3. `\includegraphics` added for `aug_heatmap.pdf` in Section 7.4 (aug_trend.pdf skipped — F7 covers aggregate trend; user decision D-01)
  4. Stale `t2_model_comparison.tex` deleted (T2 skipped — `tab:direction-rates` already covers per-direction data; user decision D-04)
  5. All figure/table references compile without LaTeX warnings
  6. `parbench_architecture.pdf` exists in `docs/paper/latex/figures/` and is referenced by `\includegraphics` in Figure 1
  7. Old F6 files (`f6_xsbench_comparison.pdf`, `.png`) deleted from `docs/paper/latex/figures/`

**Plans**: 2 plans

Plans:
- [x] 13-01-PLAN.md -- paper.tex figure wiring: architecture diagram, F3 caption, aug_heatmap ref, F6 cross-reference
- [x] 13-02-PLAN.md -- appendices.tex figure wiring: survey figure cleanup, F6 update, aug_heatmap insertion, stale file deletion

### Phase 14: Verification Backfill & Housekeeping

**Goal:** Create formal VERIFICATION.md for all completed phases that lack one (Phases 3, 4, 5, 8, and 12), update REQUIREMENTS.md checkboxes and traceability for ALL satisfied and orphaned requirements (not just a subset), refresh the ROADMAP.md progress table to reflect actual completion state, and add artifact evaluation documentation for SC26 reproducibility badges. This phase closes the root cause of 13 orphaned requirements identified by the v1.0 milestone audit.
**Depends on:** Phase 3, Phase 4, Phase 5, Phase 8, Phase 9, Phase 12 (needs satisfaction data from all completed phases)
**Requirements**: AUG-01, AUG-02, AUG-03, AUG-04, METHOD-01, METHOD-02, METHOD-03, METHOD-04, INTRO-01, INTRO-02, INTRO-03, INTRO-04, CHAR-07, VERIFY-01
**Gap Closure:** Closes ALL verification gaps and tracking staleness from v1.0 milestone audit + P1-12, P1-13 from SC26 review
**SC26 Review Items:**
  - P1-12: Add artifact evaluation README — clone steps, submodule init, dependency install, path config, smoke test commands (Raised by R4)
  - P1-13: Document required API environment variables — TOGETHER_API_KEY, AZURE_OPENAI_API_KEY, etc. (Raised by R4)
**Success Criteria** (what must be TRUE):
  1. Phase 3 VERIFICATION.md exists, covering AUG-01 through AUG-04 against success criteria
  2. Phase 4 VERIFICATION.md exists, covering METHOD-01 through METHOD-04 against success criteria
  3. Phase 5 VERIFICATION.md exists, covering INTRO-01 through INTRO-04 and CHAR-07 against success criteria
  4. Phase 8 VERIFICATION.md exists, covering FIG-01 through FIG-07 against success criteria
  5. Phase 12 VERIFICATION.md exists, covering VERIFY-01 against success criteria
  6. REQUIREMENTS.md checkboxes updated for remaining unchecked satisfied requirements: AUG-01-04 `[x]`, METHOD-01-04 `[x]` (8 checkbox updates — VERIFY-03 and QUANT-01-14 already fixed by gap closure commit)
  7. REQUIREMENTS.md traceability table status column updated: all orphaned → "Complete" (after verification backfill), VERIFY-01 → "Complete" (after Phase 12 verification)
  8. Coverage count in REQUIREMENTS.md updated to 39/39 (currently 31/39 checked + 8 pending)
  9. ROADMAP.md progress table reflects actual state (all completed phases marked)
  10. Artifact evaluation README exists with: clone instructions, submodule init, `pip install -r requirements-lock.txt`, `config/paths.json` setup, smoke test commands (`python3 -m harness verify specs/rodinia-bfs-cuda.json`)
  11. Required API environment variables documented (TOGETHER_API_KEY, AZURE_OPENAI_API_KEY, OPENAI_API_KEY, GROQ_API_KEY, GOOGLE_API_KEY)

**Plans**: 1 plan

Plans:
- [ ] 14-01-PLAN.md -- Create Phase 3, 4, 5, 8, 12 VERIFICATION.md files; update ALL checkboxes, traceability, and progress table; add artifact README
