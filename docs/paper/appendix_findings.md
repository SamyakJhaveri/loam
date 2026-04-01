# Appendix C: Detailed Evaluation Findings

This appendix provides per-kernel and per-direction breakdowns of the evaluation results summarized in Section 6 of the main paper. **Note: This appendix requires new figures generated from the evaluation result data (`results/evaluation/`). The existing survey visualizations in `analysis/visualizations/` do not cover evaluation findings. All figure positions below are marked as placeholders.**

## C.1 Per-Kernel Failure Mode Profiles

The aggregate pass rates reported in the main paper (Table 8) mask significant per-kernel variation. This section expands the evaluation matrix to show per-direction outcomes for each kernel.

[FIGURE PLACEHOLDER: C.1 -- Per-kernel x per-direction outcome heatmap. Rows = 18 Rodinia kernels + XSBench + HeCBench curated kernels. Columns = 6 primary translation directions (cuda-to-omp, omp-to-cuda, cuda-to-opencl, opencl-to-cuda, omp-to-opencl, opencl-to-omp). Cell values = PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL. Color-coded by outcome category. Data source: `results/evaluation/{model}/{direction}/*.json`, field `overall_status`.]

Key patterns to highlight:
- **Direction asymmetry**: Kernels that pass in one direction (e.g., CUDA-to-OpenMP) may fail in the reverse direction (OpenMP-to-CUDA), suggesting that LLMs find certain translation directions structurally harder than others.
- **Kernel difficulty tiers**: Some kernels (e.g., `bfs`, `nn`) pass across all models and directions, while others (e.g., `backprop`, `hotspot3D`) exhibit model-dependent success patterns.
- **Error subcategories**: BUILD_FAIL errors can be further classified by root cause: missing headers, undeclared identifiers, type mismatches, linker errors, and CUDA/OpenMP API misuse. This sub-classification reveals whether LLM failures are systematic (always the same error) or stochastic (different errors across attempts).

## C.2 Self-Repair Transition Matrices

ParBench's multi-attempt evaluation protocol allows LLMs to receive compiler/runtime error feedback and attempt corrections. This section documents the self-repair dynamics.

[FIGURE PLACEHOLDER: C.2a -- Sankey diagram or alluvial plot showing initial failure mode to final outcome transitions. Left column = initial attempt status (BUILD_FAIL, RUN_FAIL, VERIFY_FAIL). Right column = final attempt status (PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL). Flow width proportional to number of instances. Data source: `attempts[]` array in each result JSON.]

[FIGURE PLACEHOLDER: C.2b -- Self-repair rate by translation direction. Grouped bar chart: x-axis = 6 directions, y-axis = repair rate (fraction of initially-failing evaluations that eventually pass). Bars grouped by model. Data source: compare `attempts[0].status` to `overall_status` across all result JSONs.]

For each translation direction:
- **Initial failure mode distribution**: What fraction of first attempts result in BUILD_FAIL vs. RUN_FAIL vs. VERIFY_FAIL?
- **Repair rate**: What fraction of initially-failing evaluations are rescued by subsequent attempts?
- **Average attempts to success**: Among evaluations that eventually pass, how many attempts does the LLM require on average?
- **Token consumption**: Does self-repair consume significantly more tokens than first-attempt success?

## C.3 Augmentation Transform Frequency Per Kernel

ParBench's code augmentation pipeline applies six AST-level transforms at four intensity levels (L1--L4). The transforms do not apply uniformly: some kernels have many candidate sites for a given transform, while others have few or none.

[FIGURE PLACEHOLDER: C.3 -- Heatmap of transform frequency per kernel. Rows = kernels. Columns = 6 transforms (SwapCondition, ArithmeticTransform, ChangeNames, TypedefExpansion, PointerArithmeticToArrayIndex, ChangeFunctionNames). Cell values = number of candidate sites identified. Data source: `results/augmentation/full_aug_results.json`.]

Aggregate transform frequencies across the corpus:
- **SwapCondition**: 162 candidate sites (most common; targets `if/else` branches and ternary expressions)
- **ArithmeticTransform**: 69 candidate sites (commutative rewriting of arithmetic expressions)
- **ChangeNames**: 55 candidate sites (variable/parameter renaming)
- **TypedefExpansion**: 7 candidate sites (inline expansion of typedef aliases)
- **PointerArithmeticToArrayIndex**: 6 candidate sites (rewriting `*(ptr + i)` to `ptr[i]` and vice versa)
- **ChangeFunctionNames**: 2 candidate sites (least common; limited by function definition count in single-kernel files)

The level-invariance property (54/60 Rodinia specs pass at all levels L1--L4) confirms that augmentation introduces no new correctness failures. This is expected: all transforms preserve semantic equivalence by construction, and the augmentation unit tests (`c_augmentation/test_transforms.py`, 15 tests) verify this property for each transform in isolation.

## C.4 OpenCL False-Positive Forensic Report

During evaluation, the `backprop-opencl` kernel was identified as producing a false-positive PASS result under certain verification configurations. This section documents the root cause analysis.

**The bug:** The `backprop` OpenCL host code (`bpnn_train_kernel()`) calls `clEnqueueReadBuffer` to transfer results from GPU to host memory. If this call fails, the function returns -1. However, the caller (`facetrain.c`) ignores the return value, prints a success message regardless, and exits with code 0. A translation that produces syntactically valid but functionally incorrect OpenCL kernel code would pass exit-code verification while producing garbage output.

**The fix:** ParBench's verification was strengthened to use stdout pattern matching in conjunction with exit code checking. The conjunction requirement (`stdout_pattern AND exit_code == 0`) catches false positives where the host code reports success but the kernel output does not match the expected pattern.

**Defense in depth:** For OpenCL kernel-only translations (where the host code is untouched and only `.cl` kernel files are translated), `clBuildProgram` catches compilation-stage failures at runtime. However, kernels that compile but compute incorrect results require stdout pattern verification to detect.

[FIGURE PLACEHOLDER: C.4 -- Timeline diagram showing the false-positive discovery, root cause analysis, and verification fix sequence. Not strictly necessary; can be replaced with the prose description above.]

## C.5 pass@k Per-Direction Breakdown

The main paper reports aggregate pass@k statistics. This section breaks these down by translation direction to reveal direction-specific difficulty patterns.

[FIGURE PLACEHOLDER: C.5 -- pass@k curves by direction. 6 subplots (one per direction), each showing pass@1, pass@3 for each model. Alternative: single plot with direction on x-axis and pass@k on y-axis, lines colored by model. Data source: `results/evaluation/` result JSONs, using the `attempts[]` array to compute pass@k.]

For each direction, evaluations fall into three categories:
- **Hard fail**: 0/k attempts pass (the LLM consistently fails on this kernel-direction pair)
- **Noisy fail**: Some attempts pass, others fail (stochastic success dependent on generation quality)
- **Always pass**: k/k attempts pass (the LLM reliably handles this kernel-direction pair)

The distribution across these categories varies by direction. Paradigm-crossing directions (CUDA-to-OpenMP, OpenMP-to-CUDA) show more noisy-fail instances than same-paradigm directions, consistent with the higher structural transformation complexity identified in Appendix A.2.

## C.6 XSBench Cross-Granularity Comparison

XSBench provides a unique opportunity for cross-granularity comparison with prior work. ParEval-Repo (Nichols et al., 2024) evaluates LLM code generation on repository-level tasks including XSBench, reporting 0% pass@k across all models tested (for applications spanning 109--3,039 SLoC).

[FIGURE PLACEHOLDER: C.6 -- Side-by-side comparison table or bar chart. Left: ParEval-Repo results for XSBench (0% pass@k, all models). Right: ParBench results for XSBench kernel-level translation (pass rates by model and direction). Data source: ParBench results from `results/evaluation/*/` for xsbench specs; ParEval-Repo numbers from published paper.]

ParBench's kernel-centric isolation enables successful translation where repository-level evaluation fails. The binding constraint in repository-level evaluation is not the translation of computational kernels but the generation of build systems, driver code, and I/O handling. By isolating the kernel and providing the surrounding build infrastructure, ParBench measures translation capability without confounding it with software engineering overhead.

## C.7 Multi-Suite Augmentation Baseline Verification

The augmentation baseline verification confirms that code augmentation at levels L1--L4 introduces no new correctness failures beyond the 6 pre-existing KNOWN_FAIL specs. Complete verification data:

- **Rodinia (54 specs):** All PASS at L1, L2, L3, and L4. Verified across augmentation phases 3--5.
- **XSBench (4 specs):** All PASS at L1--L4.
- **RSBench (3 specs):** PASS at L1--L4 (OpenMP Target variant not explicitly verified due to compiler dependency).
- **mixbench (3 specs):** PASS at L1--L4.
- **HeCBench curated (4 spot-checked):** PASS at L1--L4.
- **KNOWN_FAIL specs (6):** Identical failures at all augmentation levels, confirming that augmentation does not change failure modes for pre-existing issues.

[FIGURE PLACEHOLDER: C.7 -- Augmentation level invariance plot. X-axis = augmentation level (L0, L1, L2, L3, L4). Y-axis = pass count. Lines for each suite (Rodinia, XSBench, RSBench, mixbench). Expected result: flat lines at the baseline pass count for each suite. Data source: `results/augmentation/phase{3,4,5}_*.json`, `full_aug_results.json`.]

The level-invariance result is methodologically significant: it confirms that the augmentation transforms are semantically equivalent (they do not alter program behavior) and that the verification pipeline is robust to syntactic variation in the source code. This property is a prerequisite for using augmented code as controlled input variation in the LLM evaluation experiments.

---

**[AUTHOR NOTE]:** This appendix requires a dedicated visualization pipeline to generate Figures C.1--C.7 from the evaluation result data in `results/evaluation/`. The existing figures in `analysis/visualizations/` cover the survey and selection phases (Appendices A and B) but do not include evaluation outcome visualizations. A script analogous to `scripts/generate_viz_data.py` should be created to produce these figures from the result JSONs.
