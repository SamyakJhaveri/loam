# Requirements: SC26 Paper Completion Sprint

**Defined:** 2026-04-03
**Core Value:** Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

## v1 Requirements

Requirements for paper submission (deadline: April 8, 2026). Each maps to roadmap phases.

### Data Verification

- [x] **VERIFY-01**: Every numerical claim in Sections 1-5 cross-checked against ground truth JSON files (paper_data.json, statistical_analysis.json, selfrepair_analysis.json)
- [x] **VERIFY-02**: Suite-summary table (tab:suite-summary) verified: kernel count, spec count, API counts match manifest.jsonl + specs/ on disk
- [x] **VERIFY-03**: Augmentation level definitions table (tab:augmentation-levels) verified against LEVEL_FRACTIONS in c_augmentation/augment_dataset.py
- [x] **VERIFY-04**: Model config table (tab:model-config) coherent post-C1 swap: Qwen + GPT-4.1 mini descriptions accurate, no Gemini remnants
- [x] **VERIFY-05**: Hardware/software table (tab:hardware) verified against actual system (nvcc --version, gcc --version, GPU model)
- [x] **VERIFY-06**: Analysis files freshness assessed: paper_data.json (April 1) checked for coverage of all current Rodinia results; re-run if stale

### Benchmark Characterization

- [x] **CHAR-01**: SLoC analysis extended from 18 to all 35 kernels using scripts/analysis/sloc_analysis.py
- [x] **CHAR-02**: Domain category distribution computed from manifest.jsonl (12 categories)
- [x] **CHAR-03**: API coverage cross-tab produced (suite rows x API columns) and verified against spec files on disk
- [x] **CHAR-04**: Single-file vs multi-file translation breakdown computed per suite and per API
- [x] **CHAR-05**: Language feature grep completed on available source dirs (Rodinia + XSBench) for OpenMP 1.0-4.5, CUDA basic-9.0+, OpenCL 1.x-2.0 version indicators
- [x] **CHAR-06**: Language standard distribution extracted from spec JSONs (implementation.language_standard field)
- [x] **CHAR-07**: LaTeX characterization table (tab:benchmark-characterization) added to Section 4 of paper.tex with clear caption

### Introduction & Positioning

- [x] **INTRO-01**: Quantitative highlights woven into introduction (35 kernels, 96 specs, 4 APIs, SLoC range, multi-file %, augmentation levels) -- not as bullet list
- [x] **INTRO-02**: LASSI differentiation sharpened: augmentation robustness probing (LASSI has none), 5 suites vs 1, 6 directions vs 2, survey-grounded curation, raw model vs agentic pipeline, 96 specs vs 10 kernels
- [x] **INTRO-03**: Multi-file translation handling emphasized in intro + Section 4 with quantitative breakdown and kernel isolation "reviewer defense" point
- [x] **INTRO-04**: Benchmark differentiation in "Gap in Existing Evaluation" strengthened with concrete comparative data from characterization

### Augmentation Story

- [ ] **AUG-01**: Per-kernel x per-level status matrix built from raw Qwen result JSONs (cuda-to-omp, L0-L4) and saved to results/analysis/augmentation_per_kernel_matrix.json
- [ ] **AUG-02**: 2-3 motivating examples identified (kernels showing PASS->FAIL degradation across levels) OR null-result interpretation strengthened with per-kernel evidence
- [ ] **AUG-03**: LASSI augmentation positioning paragraphs written (complementary, not competing)
- [x] **AUG-04**: Augmentation trend graphs produced (per-kernel + aggregate, publication quality PDF+PNG, Okabe-Ito palette)

### Methodology & Reviewer Defense

- [ ] **METHOD-01**: Kernel isolation methodology explicitly justified: ParEval-Repo 0% on XSBench vs ParBench 68.8% on same kernel -- quantifies build-system vs translation skill
- [ ] **METHOD-02**: Statistical test choices justified in text: why Cochran-Armitage for trend, why McNemar for paired direction comparison, why Wilson CIs
- [ ] **METHOD-03**: Reproducibility claims backed by specific version pins: CUDA version, compiler versions, OS, GPU model, model API version, ParBench commit hash
- [ ] **METHOD-04**: Conjunction verification (exit_code AND stdout_pattern) methodology justified vs alternatives (BLEU, compilation-only)

### Quantitative Analysis

- [x] **QUANT-01**: Aggregate pass rates by suite (Rodinia, XSBench, RSBench, mixbench, HeCBench) with Wilson 95% CIs and sample sizes
- [x] **QUANT-02**: Per-direction pass rates for all 6 standard directions + omp_target case-study directions, with CIs
- [x] **QUANT-03**: Direction asymmetry analysis: McNemar's test p-values, paired differences, which direction is "easier" and by how much
- [x] **QUANT-04**: Per-augmentation-level pass rates (L0-L4) with Cochran-Armitage trend test p-value and Cohen's h effect sizes between adjacent levels
- [x] **QUANT-05**: Failure taxonomy distribution: BUILD_FAIL / RUN_FAIL / VERIFY_FAIL / EXTRACTION_FAIL counts and percentages, per-suite and aggregate, with top build error subcategories
- [x] **QUANT-06**: Self-repair effectiveness: overall repair rate, per-failure-type repair rates, regression rate, mean attempts to success, per-suite breakdown
- [x] **QUANT-07**: Pass@k estimates for k=1,3 from the s0/s1/s2 seed variants, per-direction and aggregate
- [x] **QUANT-08**: Per-kernel difficulty tiers: rank kernels by L0 pass rate, identify top-5 easiest and top-5 hardest, note anomalous per-direction patterns
- [x] **QUANT-09**: Translation complexity correlation: pass rate by complexity class (single_file, multi_to_single, single_to_multi, multi_to_multi) with Chi-squared test
- [x] **QUANT-10**: Cross-suite comparison: Rodinia aggregate vs XSBench vs RSBench vs mixbench (SLoC correlation, multi-file fraction)
- [x] **QUANT-11**: Token cost analysis: total input/output tokens, estimated cost per task, cost per PASS, cost per suite
- [x] **QUANT-12**: SLoC correlation: Spearman/Pearson correlation between kernel SLoC and pass rate
- [x] **QUANT-13**: OpenCL kernel-only effect: compare pass rates for X-to-OpenCL (kernel-only) vs X-to-OMP (full program)
- [x] **QUANT-14**: Every number has a provenance trail: source file path, field name, and exact value so paper.tex claims are auditable

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
| VERIFY-01 | Phase 12 → Phase 14 | Done, pending verification backfill |
| VERIFY-02 | Phase 1 | Complete |
| VERIFY-03 | Phase 1 | Complete |
| VERIFY-04 | Phase 1 | Complete |
| VERIFY-05 | Phase 1 | Complete |
| VERIFY-06 | Phase 1 | Complete |
| CHAR-01 | Phase 2 | Complete |
| CHAR-02 | Phase 2 | Complete |
| CHAR-03 | Phase 2 | Complete |
| CHAR-04 | Phase 2 | Complete |
| CHAR-05 | Phase 2 | Complete |
| CHAR-06 | Phase 2 | Complete |
| CHAR-07 | Phase 5 → Phase 14 | Done, pending verification backfill |
| INTRO-01 | Phase 5 → Phase 14 | Done, pending verification backfill |
| INTRO-02 | Phase 5 → Phase 14 | Done, pending verification backfill |
| INTRO-03 | Phase 5 → Phase 14 | Done, pending verification backfill |
| INTRO-04 | Phase 5 → Phase 14 | Done, pending verification backfill |
| AUG-01 | Phase 3 → Phase 14 | Done, pending verification backfill |
| AUG-02 | Phase 3 → Phase 14 | Done, pending verification backfill |
| AUG-03 | Phase 3 → Phase 14 | Done, pending verification backfill |
| AUG-04 | Phase 3 → Phase 13/14 | Done, pending wiring (P13) + verification (P14) |
| METHOD-01 | Phase 4 → Phase 14 | Done, pending verification backfill |
| METHOD-02 | Phase 4 → Phase 14 | Done, pending verification backfill |
| METHOD-03 | Phase 4 → Phase 14 | Done, pending verification backfill |
| METHOD-04 | Phase 4 → Phase 14 | Done, pending verification backfill |
| QUANT-01 | Phase 9 | Complete |
| QUANT-02 | Phase 9 | Complete |
| QUANT-03 | Phase 9 | Complete |
| QUANT-04 | Phase 9 | Complete |
| QUANT-05 | Phase 9 | Complete |
| QUANT-06 | Phase 9 | Complete |
| QUANT-07 | Phase 9 | Complete |
| QUANT-08 | Phase 9 | Complete |
| QUANT-09 | Phase 9 | Complete |
| QUANT-10 | Phase 9 | Complete |
| QUANT-11 | Phase 9 | Complete |
| QUANT-12 | Phase 9 | Complete |
| QUANT-13 | Phase 9 | Complete |
| QUANT-14 | Phase 9 | Complete |

**Coverage:**
- v1 requirements: 39 total
- Formally verified with VERIFICATION.md evidence: 25/39 (VERIFY-02-06, CHAR-01-06, QUANT-01-14)
- Checked `[x]` but pending Phase 14 verification backfill: 6/39 (VERIFY-01, CHAR-07, INTRO-01-04 — work done per Phase 5/12 SUMMARYs, no VERIFICATION.md)
- Unchecked, pending Phase 14 verification backfill: 8/39 (AUG-01-04, METHOD-01-04 — work done per Phase 3/4 SUMMARYs, no VERIFICATION.md)
- Mapped to phases: 39
- Unmapped: 0
- Gap closure reassignments: VERIFY-01→Phase 12/14, AUG-04→Phase 13/14, AUG-01-03→Phase 14, METHOD-01-04→Phase 14, CHAR-07/INTRO-01-04→Phase 14

---
*Requirements defined: 2026-04-03*
*Last updated: 2026-04-05 after gap closure plan + adversarial review — expanded Phase 14 scope, fixed 17 stale traceability entries, corrected coverage categories and VERIFY-01 status*
