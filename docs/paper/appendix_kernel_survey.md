# Appendix: Kernel Survey and Selection Details

**Status:** STUB -- content outline for Erel
**Target length:** 2--3 pages IEEE double-column

---

## Content Outline

### 1. Full 35-Repository Inventory Table

Complete table with columns:
- Repository name
- Year / latest release
- Tier (A or B)
- Benchmark type (suite, mini-app, proxy app, full app, library, microbenchmark)
- APIs provided (CUDA, OpenMP, OpenCL, HIP, SYCL, OpenACC, MPI, serial, etc.)
- Kernel count (per API where available)
- Build system (Make, CMake, other)
- Verification method (self-checking, reference file, visual, none)
- Maintenance status (active, archived, unmaintained)

### 2. Tier A/B Classification Rubric

Criteria for Tier A (30 repositories):
- Documented build process
- Automated verification (self-checking output or reference comparison)
- Active maintenance (commits within 2 years)

Criteria for Tier B (5 repositories):
- Partial verification only, or
- Limited API coverage, or
- Unmaintained but still buildable

### 3. HeCBench Selection Funnel Detail

Expand Figure 4 into a detailed accounting:
- **Stage 1:** 513 total HeCBench kernels → 327 with all 4 API variants (CUDA, HIP, SYCL, OpenMP)
- **Stage 2:** 327 → 325 with Makefiles in CUDA variant (2 excluded: [list names])
- **Stage 3:** 325 → 242 with self-checking output patterns (string matching for PASS/FAIL/verify/correct)
- **Stage 4:** Complexity filter (exclude >15 files or <2 files, exclude external input dependencies)
- **Stage 5:** 60 selected for domain diversity → 10 curated for evaluation corpus

Include the 60-kernel working set with domain classifications and API variant pass rates.

### 4. Rodinia 22-Kernel Inventory

Per-kernel table:
- Kernel name
- Computational domain
- API variants available (CUDA, OpenMP, OpenCL)
- Baseline status (PASS / KNOWN_FAIL)
- KNOWN_FAIL reason (if applicable)
- Number of source files per variant
- Lines of code (approximate)

### 5. XSBench / RSBench / mixbench Kernel Profiles

For each suite:
- Kernel description and computational domain
- API variants and baseline status
- Key algorithmic patterns (e.g., XSBench: Monte Carlo cross-section lookup, hash-based unionized grid)
- Verification method and expected output format
- Distinguishing characteristics for LLM translation evaluation

### 6. Exclusion Log with Reasons

Table of repositories/kernels considered but excluded:
- Repository exclusions (5 of 40 initial candidates): download failures, insufficient documentation
- Kernel exclusions within selected suites: missing API variants, no self-checking output, excessive complexity, external data dependencies
- Specific HeCBench exclusion reasons for the 242→60→10 reduction

---

## Data References

- Survey spreadsheet: [location TBD]
- 60-kernel domain classifications: HeCBench working set analysis
- KNOWN_FAIL analysis: `.claude/rules/known-issues.md`
- Rodinia kernel inventory: `specs/rodinia-*-*.json` (60 spec files)
- XSBench/RSBench/mixbench specs: `specs/{xsbench,rsbench,mixbench}-*.json`
- Selection funnel diagram: `docs/paper/figures/f4_selection_funnel.png`
