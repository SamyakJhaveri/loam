# Requirements: SC26 Paper Completion Sprint

**Defined:** 2026-04-03
**Core Value:** Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

## v1 Requirements

Requirements for paper submission (deadline: April 8, 2026). Each maps to roadmap phases.

### Data Verification

- [ ] **VERIFY-01**: Every numerical claim in Sections 1-5 cross-checked against ground truth JSON files (paper_data.json, statistical_analysis.json, selfrepair_analysis.json)
- [ ] **VERIFY-02**: Suite-summary table (tab:suite-summary) verified: kernel count, spec count, API counts match manifest.jsonl + specs/ on disk
- [ ] **VERIFY-03**: Augmentation level definitions table (tab:augmentation-levels) verified against LEVEL_FRACTIONS in c_augmentation/augment_dataset.py
- [ ] **VERIFY-04**: Model config table (tab:model-config) coherent post-C1 swap: Qwen + GPT-4.1 mini descriptions accurate, no Gemini remnants
- [ ] **VERIFY-05**: Hardware/software table (tab:hardware) verified against actual system (nvcc --version, gcc --version, GPU model)
- [ ] **VERIFY-06**: Analysis files freshness assessed: paper_data.json (April 1) checked for coverage of all current Rodinia results; re-run if stale

### Benchmark Characterization

- [ ] **CHAR-01**: SLoC analysis extended from 18 to all 35 kernels using scripts/analysis/sloc_analysis.py
- [ ] **CHAR-02**: Domain category distribution computed from manifest.jsonl (12 categories)
- [ ] **CHAR-03**: API coverage cross-tab produced (suite rows x API columns) and verified against spec files on disk
- [ ] **CHAR-04**: Single-file vs multi-file translation breakdown computed per suite and per API
- [ ] **CHAR-05**: Language feature grep completed on available source dirs (Rodinia + XSBench) for OpenMP 1.0-4.5, CUDA basic-9.0+, OpenCL 1.x-2.0 version indicators
- [ ] **CHAR-06**: Language standard distribution extracted from spec JSONs (implementation.language_standard field)
- [ ] **CHAR-07**: LaTeX characterization table (tab:benchmark-characterization) added to Section 4 of paper.tex with clear caption

### Introduction & Positioning

- [ ] **INTRO-01**: Quantitative highlights woven into introduction (35 kernels, 96 specs, 4 APIs, SLoC range, multi-file %, augmentation levels) -- not as bullet list
- [ ] **INTRO-02**: LASSI differentiation sharpened: augmentation robustness probing (LASSI has none), 5 suites vs 1, 6 directions vs 2, survey-grounded curation, raw model vs agentic pipeline, 96 specs vs 10 kernels
- [ ] **INTRO-03**: Multi-file translation handling emphasized in intro + Section 4 with quantitative breakdown and kernel isolation "reviewer defense" point
- [ ] **INTRO-04**: Benchmark differentiation in "Gap in Existing Evaluation" strengthened with concrete comparative data from characterization

### Augmentation Story

- [ ] **AUG-01**: Per-kernel x per-level status matrix built from raw Qwen result JSONs (cuda-to-omp, L0-L4) and saved to results/analysis/augmentation_per_kernel_matrix.json
- [ ] **AUG-02**: 2-3 motivating examples identified (kernels showing PASS->FAIL degradation across levels) OR null-result interpretation strengthened with per-kernel evidence
- [ ] **AUG-03**: LASSI augmentation positioning paragraphs written (complementary, not competing)
- [ ] **AUG-04**: Augmentation trend graphs produced (per-kernel + aggregate, publication quality PDF+PNG, Okabe-Ito palette)

### Methodology & Reviewer Defense

- [ ] **METHOD-01**: Kernel isolation methodology explicitly justified: ParEval-Repo 0% on XSBench vs ParBench 68.8% on same kernel -- quantifies build-system vs translation skill
- [ ] **METHOD-02**: Statistical test choices justified in text: why Cochran-Armitage for trend, why McNemar for paired direction comparison, why Wilson CIs
- [ ] **METHOD-03**: Reproducibility claims backed by specific version pins: CUDA version, compiler versions, OS, GPU model, model API version, ParBench commit hash
- [ ] **METHOD-04**: Conjunction verification (exit_code AND stdout_pattern) methodology justified vs alternatives (BLEU, compilation-only)

## v2 Requirements

Deferred to post-submission or camera-ready revision.

### Pending Data Integration

- **PEND-01**: GPT-4.1 mini results integrated into all tables and analysis
- **PEND-02**: Non-Rodinia Qwen results (HeCBench, XSBench, RSBench, mixbench) integrated
- **PEND-03**: Results section (Section 6+) updated with complete campaign data
- **PEND-04**: Cross-model statistical comparison (chi-squared, effect sizes)
- **PEND-05**: Augmentation trend graphs with second model overlay

### Future Enhancement

- **FUT-01**: Performance/timing analysis with proper kernel-level profiling (nvprof/ncu)
- **FUT-02**: Efficiency measurement extension (TRACY-style)

## Out of Scope

| Feature | Reason |
|---------|--------|
| New eval runs or re-runs | Running tmux sessions must not be touched |
| Modification of existing result JSONs | Results are immutable by project invariant |
| New spec creation or modification | Benchmark is frozen for paper submission |
| GPT-4.1 mini data analysis | Blocked on Le's eval runs completing |
| Non-Rodinia Qwen data analysis | Blocked on tmux runs (qwen_hecbench, qwen_small) |
| Results section data updates | Depends on completed campaigns |
| Performance timing claims | Wall-clock times unreliable; kernel profiling not yet done |
| HeCBench source feature grep | Source not cloned locally (gitignored) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| VERIFY-01 | Phase 1 | Pending |
| VERIFY-02 | Phase 1 | Pending |
| VERIFY-03 | Phase 1 | Pending |
| VERIFY-04 | Phase 1 | Pending |
| VERIFY-05 | Phase 1 | Pending |
| VERIFY-06 | Phase 1 | Pending |
| CHAR-01 | Phase 2 | Pending |
| CHAR-02 | Phase 2 | Pending |
| CHAR-03 | Phase 2 | Pending |
| CHAR-04 | Phase 2 | Pending |
| CHAR-05 | Phase 2 | Pending |
| CHAR-06 | Phase 2 | Pending |
| CHAR-07 | Phase 5 | Pending |
| INTRO-01 | Phase 5 | Pending |
| INTRO-02 | Phase 5 | Pending |
| INTRO-03 | Phase 5 | Pending |
| INTRO-04 | Phase 5 | Pending |
| AUG-01 | Phase 3 | Pending |
| AUG-02 | Phase 3 | Pending |
| AUG-03 | Phase 3 | Pending |
| AUG-04 | Phase 3 | Pending |
| METHOD-01 | Phase 4 | Pending |
| METHOD-02 | Phase 4 | Pending |
| METHOD-03 | Phase 4 | Pending |
| METHOD-04 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0

---
*Requirements defined: 2026-04-03*
*Last updated: 2026-04-03 after roadmap creation -- traceability complete*
