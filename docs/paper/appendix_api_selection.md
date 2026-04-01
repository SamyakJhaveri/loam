# Appendix: API Selection Rationale

**Status:** STUB -- content outline for Erel
**Target length:** 1.5--2 pages IEEE double-column

---

## Content Outline

### 1. Full API Co-Occurrence Data

Expand Figure 2 into a complete table showing the full 15×15 API pairwise coverage matrix from the 35-repository survey. Include per-repository API breakdowns with repository names, years, and maintenance status.

### 2. Translation Difficulty Taxonomy

Classify translation directions by structural transformation requirements:
- **Syntactic renaming** (e.g., CUDA → HIP): near-1:1 API call mapping
- **Paradigm translation** (e.g., CUDA → OpenMP): SPMD to fork-join, explicit to implicit memory
- **Architecture split** (e.g., CUDA → OpenCL): unified source to separate host/kernel files
- **Directive insertion** (e.g., serial → OpenMP): adding parallelism to sequential code

Include code examples showing the structural transformation for each category.

### 3. HIP/SYCL Exclusion Rationale

Provide code examples demonstrating the near-syntactic equivalence of CUDA ↔ HIP translation:
- `cudaMalloc` → `hipMalloc` (1:1 mapping)
- Kernel launch syntax preserved verbatim
- Thread-index arithmetic unchanged

Argue that CUDA-HIP translation is too easy to serve as a meaningful LLM evaluation target -- it tests API renaming skill, not parallel reasoning.

Similarly for SYCL: while the transformation is more complex than HIP, the single-source GPU model is preserved, making it less informative than the paradigm-crossing CUDA → OpenMP direction.

### 4. OpenACC Exclusion

- Only 3 of 35 surveyed repositories provide OpenACC implementations (Figure 2)
- Insufficient benchmark material for statistical evaluation
- Paradigm overlap with OpenMP (`#pragma acc parallel` vs. `#pragma omp parallel`)
- OpenACC's directive model occupies the same evaluation niche as OpenMP, offering less programming-model diversity than OpenCL

### 5. OMP-Target Case Study Justification

- OMP-target requires NVIDIA HPC compiler (`nvc`), not universally available
- Compilation model differs substantially from CPU OpenMP (GPU offload vs. CPU threading)
- Available for XSBench, RSBench, and HeCBench curated kernels only
- Evaluated as case study rather than primary direction to avoid confounding compiler availability with model capability

---

## Data References

- API co-occurrence matrix: `docs/survey/api_cooccurrence.csv` (or equivalent survey data)
- Per-repository API breakdown: survey spreadsheet
- HeCBench 4-API statistics: 327 kernels with all 4 APIs (CUDA, HIP, SYCL, OpenMP)
- Figure 2 source data: `docs/paper/figures/f2_api_cooccurrence_survey.png`
