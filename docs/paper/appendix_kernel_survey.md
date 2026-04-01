# Appendix B: Kernel Survey and Selection Details

This appendix documents the systematic survey and multi-stage selection process that produced ParBench's evaluation corpus. The main paper (Section 4) summarizes this process; here we provide the complete data, selection criteria, and exclusion rationale.

## B.1 Full Repository Inventory

The survey identified 35 benchmark repositories spanning five categories of HPC benchmark software. Figure B.1 shows the distribution across categories.

<!-- Figure B.1: benchmark_types.png -->
![Figure B.1: Distribution of benchmark types across the 35 surveyed repositories. Suites (13, 37%) and mini-applications (12, 34%) dominate, together accounting for 71% of the survey. Proxy applications (4, 11%), libraries (4, 11%), and full applications (2, 6%) complete the distribution. Suites and mini-applications provide the richest kernel-level material for translation evaluation because they contain multiple independent computational kernels with self-checking verification.](../../analysis/visualizations/benchmark_types.png)
<!-- \label{fig:benchmark_types} -->

The relationship between benchmarks and APIs is not uniform: some repositories implement a single API (e.g., SPEC OMP, PARSEC, LonestarGPU), while others provide implementations across 10+ APIs (BabelStream with 12, miniBUDE with 14). Figure B.2 visualizes this heterogeneity as a bipartite network.

<!-- Figure B.2: benchmark_api_bipartite_color_readable_v7.png -->
![Figure B.2: Bipartite network linking benchmarks (circles, right) to parallel APIs (squares, left). Benchmark nodes are colored by type (microbenchmarks, validation, suites, mini-applications/proxy apps/frameworks/libraries, applications) and sized proportional to the number of APIs they implement. API nodes are colored by family (vendor GPU, open standard GPU, directives, message passing, CPU parallel libs, portability libs, single-source C++, PGAS/one-sided, other). Green edges and green node outlines indicate verified download availability; grey indicates unverified. The dense connectivity between CUDA, OpenMP, HIP, and SYCL (left column) and the suite-type benchmarks (center) demonstrates the concentration of multi-API material in a small number of large suites, particularly HeCBench, RAJAPerf, and BabelStream.](../../analysis/visualizations/benchmark_api_bipartite_color_readable_v7.png)
<!-- \label{fig:bipartite_v7} -->

Figure B.3 quantifies the API breadth distribution across the surveyed benchmarks.

<!-- Figure B.3: benchmark_api_count_hist_v5.png -->
![Figure B.3: Distribution of API breadth (number of parallel APIs supported) across surveyed benchmarks. The modal benchmark supports 3 APIs, with a peak of approximately 18 benchmarks in the 3-API bin. A long tail extends to 12+ APIs, occupied by BabelStream and miniBUDE. Approximately 13 benchmarks support only 1--2 APIs (single-paradigm implementations). Benchmarks supporting 3 or more APIs are the primary candidates for multi-direction translation evaluation, as they provide natural reference implementations for cross-API comparison.](../../analysis/visualizations/benchmark_api_count_hist_v5.png)
<!-- \label{fig:api_count_hist} -->

The combination of Figures B.1--B.3 establishes that the benchmark landscape is dominated by a small number of large suites with broad API coverage. This Pareto distribution motivated the selection strategy: focus on the richest suites (HeCBench, Rodinia) supplemented by targeted mini-applications (XSBench, RSBench, mixbench) to ensure domain diversity.

## B.2 Quality Tier Classification

All 35 surveyed repositories were classified into two quality tiers based on three criteria: build documentation, verification capability, and maintenance status.

<!-- Figure B.4: quality_tiers.png -->
![Figure B.4: Quality tier distribution across surveyed repositories. 30 of 35 repositories (85%) meet Tier A criteria (documented build process, automated verification, and active maintenance within 2 years). 5 repositories (14%) are classified as Tier B due to partial verification, limited API coverage, or unmaintained status.](../../analysis/visualizations/quality_tiers.png)
<!-- \label{fig:quality_tiers} -->

**Tier A criteria** (all three required):
- Documented build process (Makefile, CMake, or equivalent with clear instructions)
- Automated verification: self-checking output (print PASS/FAIL, compute checksum, compare against reference) or reference output file comparison
- Active maintenance: commits within 2 years of the survey date, or stable release with no known build failures on modern toolchains

**Tier B criteria** (any one sufficient for downgrade):
- Partial verification only (e.g., visual output inspection, manual comparison)
- Limited API coverage (single API, reducing cross-translation utility)
- Unmaintained but still buildable (no commits in 2+ years, but Makefiles still produce working binaries)

Tier B repositories were not excluded from the survey but were deprioritized in kernel selection. Their kernels were considered only when no Tier A alternative existed for a given computational domain.

## B.3 Candidate Ranking and HeCBench Selection Funnel

The selection of individual kernels for ParBench's evaluation corpus required balancing two competing objectives: *kernel richness* (maximizing the number of independent evaluation instances) and *API breadth* (maximizing the number of translation directions per kernel). Figure B.5 plots these two dimensions for all surveyed repositories.

<!-- Figure B.5: kernel_api_bubble.png -->
![Figure B.5: Benchmark kernel richness (y-axis, capped at 100 for readability) vs. API breadth (x-axis, number of APIs supported). Bubble size proportional to total kernel count; color indicates benchmark type (suites in green, mini-applications in cyan, proxy applications in light blue, libraries in orange, microbenchmarks in coral, applications in dark blue). HeCBench (516 kernels, 4 APIs) dominates the upper region, with its bubble extending beyond the y-axis cap. RAJAPerf (80 kernels, 5 APIs) is the second-largest. CloverLeaf (23 kernels, 9 APIs) and BabelStream (5 kernels, 12 APIs) occupy the high-API-breadth region but with far fewer kernels. The optimal candidates for corpus construction lie in the high-kernel/moderate-API quadrant (upper-center).](../../analysis/visualizations/kernel_api_bubble.png)
<!-- \label{fig:kernel_api_bubble} -->

Figure B.6 presents the top candidates ranked by their combined kernel-count and API-breadth scores, revealing the fundamental tradeoff in corpus construction.

<!-- Figure B.6: top_candidates.png -->
![Figure B.6: Top "Rosetta Stone" candidates ranked by kernel count (blue bars, scaled for readability; true counts annotated above) and API breadth (red bars). HeCBench provides the largest kernel pool (516 kernels) but with only 4 primary APIs (CUDA, HIP, SYCL, OpenMP). BabelStream provides the broadest API coverage (12 APIs) but with only 5 kernels. RAJAPerf (80 kernels, 7 APIs) offers a balanced middle ground. Rodinia (24 kernels, 3 primary APIs) provides established, well-understood benchmarks with strong community recognition. The selection strategy balances kernel richness against API diversity, selecting HeCBench for scale and Rodinia for community trust.](../../analysis/visualizations/top_candidates.png)
<!-- \label{fig:top_candidates} -->

### HeCBench Selection Funnel

HeCBench's 516 kernels were filtered through a multi-stage funnel to identify the curated evaluation set:

- **Stage 1 (API filter):** 516 total kernels in the HeCBench repository. Of these, 272 kernels provide implementations in all 4 primary APIs (CUDA, HIP, SYCL, OpenMP) and have Makefiles and self-checking output. The remaining 244 kernels lack one or more API variants, lack Makefiles in the CUDA variant, or lack self-checking output patterns.

- **Stage 2 (Complexity filter):** The 272 candidates were filtered for evaluation tractability. Kernels with more than 15 source files or fewer than 2 source files were excluded (the former are too complex for single-prompt translation; the latter are trivial boilerplate). Kernels requiring external input data files were also excluded to ensure self-contained evaluation.

- **Stage 3 (Domain diversity):** From the complexity-filtered set, 60 kernels were selected to maximize domain diversity across computational categories: linear algebra, stencil computation, graph algorithms, machine learning, physics simulation, sorting, reduction, scan, image processing, and cryptography.

- **Stage 4 (Curation):** The 60-kernel working set was narrowed to a final curated set of 20 kernels based on manual inspection of build reliability, output determinism, and domain representativeness. Of these, 10 kernels were included in the current ParBench evaluation corpus, with the remaining 10 reserved for future expansion.

The final 20 curated HeCBench kernels span diverse computational domains and algorithmic patterns, ensuring that the evaluation corpus tests LLM translation capability across a representative sample of real HPC workloads.

## B.4 Rodinia Kernel Inventory

Rodinia provides the foundation of ParBench's evaluation corpus. As one of the most widely cited HPC benchmark suites (originally published at IISWC 2009), it offers strong community recognition and well-understood computational characteristics. ParBench uses 22 Rodinia kernels across three APIs (CUDA, OpenMP, OpenCL), yielding 60 total specs (some kernels lack one or more API variants).

Of these 60 specs:
- **54 TRUE PASS**: Verified correct output with exit code 0 and stdout pattern matching using conjunction verification (both conditions must hold).
- **6 KNOWN_FAIL**: Excluded from evaluation batches due to pre-existing build or runtime failures unrelated to LLM translation. These include 2 kernels using deprecated CUDA `texture<>` references removed in CUDA 12 (`kmeans-cuda`, `mummergpu-cuda`), 1 kernel requiring OpenGL dependencies (`hybridsort-cuda`), 1 kernel with CUDA API dependencies in its OpenMP variant (`mummergpu-omp`, which uses `texture<>` and `cuMemGetInfo_v2`), and 2 kernels with pre-existing OpenCL runtime issues (`nn-opencl`, `kmeans-opencl`).

Figure 3 in the main paper shows the repo-level vs. kernel-level comparison across all surveyed repositories; Rodinia's position reflects its moderate kernel count (22--24 kernels) with 3 API variants, providing 54 verified evaluation instances.

## B.5 XSBench, RSBench, and mixbench Profiles

Three additional benchmark suites complement Rodinia and HeCBench in the evaluation corpus:

**XSBench** (4 specs: CUDA, OpenMP, OpenCL, OpenMP Target): A Monte Carlo neutron cross-section lookup proxy application from Argonne National Laboratory. XSBench implements a hash-based unionized energy grid algorithm that is representative of nuclear reactor simulation workloads. All 4 API variants pass baseline verification. The OpenMP variant produces a history-based checksum (941535); the CUDA, OpenCL, and OpenMP Target variants produce an event-based checksum (945990). This asymmetry reflects algorithmic differences between the CPU and GPU implementations rather than correctness issues.

**RSBench** (4 specs: CUDA, OpenMP, OpenCL, OpenMP Target): A simplified variant of XSBench that isolates the multipole cross-section lookup kernel. RSBench was added to ParBench to enable controlled comparison with XSBench on the same algorithmic family at different complexity levels.

**mixbench** (3 specs: CUDA, OpenMP, OpenCL): A micro-benchmark designed to measure GPU arithmetic throughput at varying compute-to-memory ratios. mixbench exercises the roofline boundary, making it valuable for evaluating whether LLM translations preserve performance-critical arithmetic intensity.

## B.6 Exclusion Log and Verification Methods

Figure B.7 groups the surveyed benchmarks by their verification approach, illustrating the diversity of correctness checking methods across the survey and the basis for exclusion decisions.

<!-- Figure B.7: verification_network.png -->
![Figure B.7: Benchmarks grouped by verification method. Large colored nodes represent verification approaches: checksum comparison, convergence testing, reference output file comparison, output-to-standard comparison, and self-validation. Benchmark nodes (smaller, colored by type) are connected to their verification method(s). Benchmarks without automated verification appear as weakly connected or isolated nodes and were either excluded from the evaluation corpus or downgraded to Tier B. The checksum and reference output clusters contain the majority of Tier A benchmarks, reflecting the predominance of deterministic numerical verification in HPC benchmarking.](../../analysis/visualizations/verification_network.png)
<!-- \label{fig:verification_network} -->

### Repository-Level Exclusions

5 of the initial 40 candidate repositories were excluded during the survey phase:
- **Download failures** (2): Repository URLs were dead or access-restricted at the time of survey.
- **Insufficient documentation** (2): No build instructions, no Makefiles, or build system required proprietary dependencies not available on the evaluation platform.
- **Duplicate content** (1): One repository was a fork of an already-surveyed suite with no additional API variants.

### Kernel-Level Exclusions

Within the selected suites, individual kernels were excluded for the following reasons:
- **Missing API variants**: Kernels available in only one API (no cross-translation possible).
- **No self-checking output**: Kernels that produce graphical output, require manual inspection, or have no deterministic expected output.
- **Excessive complexity**: Kernels requiring more than 15 source files, external data files not included in the repository, or runtime dependencies (e.g., OpenGL, MPI multi-node) not available on the single-GPU evaluation platform.
- **Non-deterministic output**: Kernels whose output depends on execution order, random seeds without fixed initialization, or floating-point non-associativity beyond the tolerance of the verification method.

The complete exclusion log with per-kernel justifications is maintained in ParBench's specification metadata (`specs/*.json`) and the project's known-issues documentation.
