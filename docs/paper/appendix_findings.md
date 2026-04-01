# Appendix: Detailed Evaluation Findings

**Status:** STUB -- content outline for Erel
**Target length:** 3--4 pages IEEE double-column

---

## Content Outline

### 1. Per-Kernel Failure Mode Profiles

Expand Table 8 with per-direction breakdowns for each kernel:
- 18 Rodinia kernels × 6 directions = matrix of outcomes
- For each cell: PASS/BUILD_FAIL/RUN_FAIL/VERIFY_FAIL/EXTRACTION_FAIL across L0--L4
- Highlight direction-specific patterns (e.g., kernels that pass CUDA-to-OMP but fail OMP-to-CUDA)
- Include error subcategory detail (missing headers, undeclared identifiers, linker errors, etc.)

### 2. Self-Repair Transition Matrices Per Direction

For each of the 6 translation directions, provide:
- Initial failure mode → final outcome transition matrix
- Repair rate by direction
- Average attempts to success
- Token consumption per repair attempt
- Representative error-feedback → correction examples

### 3. Augmentation Transform Frequency Per Kernel/Level

Detailed table showing:
- Which transforms fire on which kernels (not all transforms apply to all kernels)
- Candidate site counts per transform per kernel
- Applied site counts at each level (L1--L4)
- Transform application frequency: SwapCondition (162), ArithmeticTransform (69), ChangeNames (55), TypedefExpansion (7), PointerArithmeticToArrayIndex (6), ChangeFunctionNames (2)

### 4. OpenCL False-Positive Forensic Report

Detailed analysis of the backprop false-positive case:
- Host code path: `bpnn_train_kernel()` returns -1 on `clEnqueueReadBuffer` failure
- Caller `facetrain.c` ignores return value, prints success message, exits 0
- Timeline of discovery and fix
- `clBuildProgram()` guard catches compilation-stage false positives but not execution-stage
- Recommendations for defense-in-depth verification in kernel-only evaluation

### 5. pass@k Per-Direction Breakdown

Expand Table 12 with per-direction pass@k data:
- 142 direction-kernel pairs broken down by direction
- Hard fail / noisy fail / always pass counts per direction
- Bimodal distribution analysis per direction
- Comparison of greedy-decode pass@1 vs. T=0.7 pass@1 vs. pass@3 per direction

### 6. XSBench Cross-Granularity Comparison

Detailed comparison with ParEval-Repo on XSBench:
- ParEval-Repo: 0% pass@k for all models (109--3,039 SLoC applications)
- ParBench: XSBench baseline verification PASS for all 4 API variants
- LLM translation results for XSBench across all directions
- Analysis of what kernel-centric isolation enables vs. repository-level evaluation
- Direct evidence that build-system generation is the binding constraint

### 7. Multi-Suite Augmentation Baseline Verification Details

Complete augmentation baseline data:
- 54 Rodinia specs: all PASS at L1--L4 (verified phases 3--5)
- 4 XSBench specs: all PASS at L1--L4
- 3 RSBench specs: PASS at L1--L4 (omp_target not explicitly verified)
- 3 mixbench specs: PASS at L1--L4
- 4 HeCBench spot-checked: PASS at L1--L4
- 8 KNOWN_FAIL specs: identical failures at all levels (confirming augmentation introduces no new failures)
- Per-level detailed output logs or checksums for reproducibility

---

## Data References

- Result JSONs: `results/evaluation/{model}/{direction}/` directories
- Attempt logs: `attempts[]` array within each result JSON
- Augmentation logs: `results/augmentation/phase{3,4,5}_*.json`, `full_aug_results.json`
- pass@k sweep results: `results/evaluation/qwen-3.5-coder/passk/` (or equivalent)
- XSBench specs: `specs/xsbench-*.json`
- Backprop forensic analysis: documented in S3.D of paper_draft.md
