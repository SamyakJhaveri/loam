# Roadmap: SC26 Paper Completion Sprint

## Overview

This roadmap delivers a submission-ready SC26 paper by April 8, 2026. The work flows from verifying existing data claims (ground truth), through producing new quantitative characterization and augmentation analysis, to writing methodology defense and assembling polished introduction text with the characterization table. Every phase produces artifacts that downstream phases consume -- verification feeds characterization, characterization feeds the introduction, and augmentation analysis feeds both the augmentation story and motivating examples.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Data Verification & Ground Truth** - Cross-check every existing numerical claim and table against on-disk data files
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
- [ ] 01-01-PLAN.md -- Verify Abstract + S1 + S3 (data freeze, augmentation levels, headline numbers)
- [ ] 01-02-PLAN.md -- Verify S4 + S5 (suite-summary, hardware, model config, Gemini sweep)
- [ ] 01-03-PLAN.md -- Verify S6.1-S6.5 (aggregate results, failure taxonomy, self-repair, augmentation rates)
- [ ] 01-04-PLAN.md -- Verify S6.6-S6.8 + S7 (per-kernel, directions, pass@k, stats, discussion)
- [ ] 01-05-PLAN.md -- Regenerate all analysis files + figures (depends on 01-01 through 01-04)

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
**Plans**: TBD

Plans:
- [ ] 02-01: TBD
- [ ] 02-02: TBD
- [ ] 02-03: TBD

### Phase 3: Augmentation Analysis & Story
**Goal**: The augmentation section has concrete per-kernel evidence (matrix, examples or strengthened null-result), publication-quality graphs, and clear LASSI positioning
**Depends on**: Phase 1 (verified augmentation level definitions ensure correct level semantics)
**Requirements**: AUG-01, AUG-02, AUG-03, AUG-04
**Success Criteria** (what must be TRUE):
  1. Per-kernel x per-level status matrix exists as a JSON file (results/analysis/augmentation_per_kernel_matrix.json) built from raw Qwen result JSONs for cuda-to-omp L0-L4
  2. Either 2-3 specific kernels showing PASS-to-FAIL degradation are identified with exact level/direction, OR the null-result interpretation includes per-kernel evidence showing uniform PASS across levels
  3. Augmentation trend graphs (per-kernel + aggregate) exist as publication-quality PDF and PNG files using Okabe-Ito color palette
  4. LASSI augmentation positioning paragraphs exist in paper.tex framing ParBench augmentation as complementary (robustness probing vs. agentic correction)
**Plans**: TBD

Plans:
- [ ] 03-01: TBD
- [ ] 03-02: TBD
- [ ] 03-03: TBD

### Phase 4: Methodology & Reviewer Defense
**Goal**: Section 4 methodology descriptions are precise enough to withstand SC-level reviewer scrutiny, with explicit justifications for every methodological choice
**Depends on**: Phase 1 (verified hardware table and version pins feed reproducibility claims)
**Requirements**: METHOD-01, METHOD-02, METHOD-03, METHOD-04
**Success Criteria** (what must be TRUE):
  1. Kernel isolation methodology paragraph cites the ParEval-Repo 0% vs ParBench 68.8% XSBench comparison with exact numbers from result files
  2. Statistical test choices (Cochran-Armitage, McNemar, Wilson CI) are each justified in 1-2 sentences explaining why that test fits the data structure
  3. Reproducibility paragraph lists exact version pins: CUDA version, nvcc version, gcc version, OS, GPU model, model API versions, and ParBench commit hash
  4. Conjunction verification (exit_code AND stdout_pattern) is justified against alternatives (BLEU, compilation-only) with a concrete example of why weaker verification would misclassify a result
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

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

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
(Phases 2, 3, 4 can execute in parallel after Phase 1 completes)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Data Verification & Ground Truth | 0/5 | Not started | - |
| 2. Benchmark Characterization Data | 0/3 | Not started | - |
| 3. Augmentation Analysis & Story | 0/3 | Not started | - |
| 4. Methodology & Reviewer Defense | 0/2 | Not started | - |
| 5. Introduction, Positioning & Characterization Table | 0/3 | Not started | - |
