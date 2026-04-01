# Appendix A: API Selection Rationale

This appendix provides the complete quantitative evidence underlying ParBench's selection of CUDA, OpenMP, and OpenCL as target parallel programming APIs. Figure 2 in the main paper presents a condensed 10-API co-occurrence matrix from the initial 21-repository survey; here we present the expanded data from the full survey and the kernel-level analysis that informed the final selection.

## A.1 Full API Co-Occurrence Data

The benchmark landscape survey progressed through multiple iterations, expanding from an initial seed of 21 repositories to a comprehensive survey of over 80 benchmark suites, mini-applications, proxy applications, libraries, and full applications. This broader survey captured 30+ distinct parallel programming APIs, providing a panoramic view of the HPC benchmarking ecosystem.

<!-- Figure A.1: api_cooccurrence_heatmap_v5.png -->
![Figure A.1: Expanded API co-occurrence heatmap across all surveyed repositories. Cell values indicate the number of repositories providing implementations in both the row and column APIs. The concentrated cluster of high co-occurrence among MPI, OpenMP, CUDA, HIP, and OpenACC in the upper-left quadrant reveals the core API ecosystem that dominates multi-API benchmark suites. Peripheral APIs such as Chapel, STM/TM, HLS, and Python show near-zero co-occurrence, reflecting their niche status in HPC benchmarking.](../../analysis/visualizations/api_cooccurrence_heatmap_v5.png)
<!-- \label{fig:api_cooccurrence_v5} -->

Figure 2 in the main paper presents the 10-API subset from the initial 21-repository survey; Figure A.1 extends this to the full expanded survey. The dominant pattern is preserved across survey scales: a dense co-occurrence cluster centered on MPI, OpenMP, CUDA, and HIP, with sparser connectivity among directive-based (OpenACC, OpenMP Target), portability (Kokkos, RAJA, SYCL), and niche APIs.

The force-directed network visualization in Figure A.2 makes the clustering structure explicit. Node sizes are proportional to the number of benchmarks implementing each API, and edges are drawn only for co-occurrence counts of 3 or more repositories. The result reveals three natural groupings:

<!-- Figure A.2: api_cooccurrence_network_color_v7.png -->
![Figure A.2: API co-occurrence network. Node size proportional to the number of benchmarks implementing each API; edges drawn for co-occurrence at least 3. APIs colored by family: vendor GPU (cyan), open standard GPU (red), directives (orange), message passing (green), portability libraries (grey), CPU parallel libraries (blue), single-source C++ (yellow), PGAS/one-sided (pink). The dense central cluster of MPI, OpenMP, CUDA, HIP, OpenACC, and OpenCL is clearly separated from peripheral APIs. Isolated nodes (Chapel, STM/TM, GSParLib, HLS, Python, Serial) have co-occurrence below 3 with all other APIs.](../../analysis/visualizations/api_cooccurrence_network_color_v7.png)
<!-- \label{fig:api_network_v7} -->

1. **Core cluster**: MPI (largest node), OpenMP, CUDA, HIP, OpenACC, and OpenCL form a tightly interconnected group. These APIs co-occur frequently because the benchmark suites that provide the richest multi-API material (HeCBench, Rodinia, RAJAPerf, BabelStream) implement most or all of them.

2. **Portability periphery**: SYCL, Kokkos, RAJA, and OpenMP Target connect to the core cluster but with weaker edges. These APIs are concentrated in a smaller number of suites (primarily RAJAPerf, BabelStream, and HeCBench).

3. **Isolated APIs**: OCCA, Thrust, Chapel, Coarray Fortran, Charm++, C++ AMP, UPC, OpenSHEM, HMPP, Python, HLS, GSParLib, STM/TM, and Serial appear as isolated or weakly connected nodes. Their co-occurrence with any other API falls below the edge threshold of 3.

Figure A.3 presents the per-API coverage in a ranked bar chart, making the quantitative dominance of the top-3 APIs clear.

<!-- Figure A.3: api_coverage_bar_v5.png -->
![Figure A.3: API coverage across the expanded benchmark survey. OpenMP (~50 benchmarks), MPI (~45), and CUDA (~38) dominate, with OpenACC (~17), HIP (~15), MPI+OpenMP (~15), and OpenCL (~13) forming a second tier. OpenMP Target (~8), SYCL (~7), Kokkos (~7), and RAJA (~7) form a third tier. APIs below 5 benchmarks (including GSParLib, STM/TM, HMPP, UPC++, Python, and HLS) were excluded from evaluation consideration due to insufficient benchmark material for statistical evaluation.](../../analysis/visualizations/api_coverage_bar_v5.png)
<!-- \label{fig:api_coverage_v5} -->

### Kernel-Level Co-Occurrence

The repository-level analysis in Figures A.1--A.3 counts how many *repositories* provide implementations in a given API pair, but does not capture the depth of coverage within each repository. A suite like HeCBench provides 516 individual kernels, each potentially implemented in multiple APIs, while a single-kernel mini-application like miniBUDE provides only 1 kernel across 12+ APIs. For translation evaluation, the kernel count is the relevant unit: it determines how many independent evaluation instances are available per direction.

<!-- Figure A.4: kernel_level_cooccurrence_heatmap.png -->
![Figure A.4: Kernel-level API co-occurrence matrix. Each cell counts the number of individual kernels with verified equivalent implementations in both the row and column APIs. The CUDA--HIP pair leads with 633 shared kernels, followed by CUDA--SYCL (616), CUDA--OpenMP (472), and HIP--SYCL (615). OpenCL has dramatically lower kernel-level coverage: only 27 kernels share implementations with CUDA, and 24 with OpenMP. OpenMP Target provides 106 shared kernels with each of CUDA, HIP, SYCL, and OpenMP, concentrated entirely in HeCBench. Sequential reference implementations exist for 106 kernels.](../../analysis/visualizations/kernel_level_cooccurrence_heatmap.png)
<!-- \label{fig:kernel_level_heatmap} -->

Figure A.4 provides the strongest quantitative evidence for API selection. The kernel-level data reveals a clear hierarchy:

- **Tier 1 (>600 kernel pairs):** CUDA--HIP (633), CUDA--SYCL (616), HIP--SYCL (615). These pairs are dominated by HeCBench's systematic multi-API coverage.
- **Tier 2 (~450 kernel pairs):** CUDA--OpenMP (472), HIP--OpenMP (453), SYCL--OpenMP (453). OpenMP's CPU threading model provides the deepest pool for *paradigm-crossing* translation evaluation.
- **Tier 3 (~100 kernel pairs):** OpenMP Target and Sequential at 106 each, concentrated in HeCBench.
- **Tier 4 (<30 kernel pairs):** OpenCL at 27 (CUDA--OpenCL) and 24 (OpenMP--OpenCL), with an OpenCL diagonal of 27 total kernels.

The network visualization in Figure A.5 makes this tiered structure visually apparent.

<!-- Figure A.5: kernel_level_cooccurrence_network.png -->
![Figure A.5: Kernel-level API co-occurrence network. Edges shown for at least 20 kernel pairs; edge width proportional to count. The tight CUDA/HIP/SYCL/OpenMP cluster reflects HeCBench and RAJAPerf's uniform multi-API coverage. OpenCL appears as a peripheral node with weak connections (27 CUDA--OpenCL kernel pairs, just above the 20-kernel threshold). RAJA, stdpar, and Thrust appear as isolated nodes with fewer than 20 kernel-level pairs.](../../analysis/visualizations/kernel_level_cooccurrence_network.png)
<!-- \label{fig:kernel_level_network} -->

## A.2 Translation Difficulty Taxonomy

The choice of API pairs for evaluation is motivated not only by data availability (Section A.1) but by the *structural transformation complexity* each translation direction demands. We classify translation directions into four categories:

**Syntactic renaming** (e.g., CUDA to HIP): Near-1:1 API call mapping. `cudaMalloc` becomes `hipMalloc`; kernel launch syntax is preserved verbatim; thread-index arithmetic (`threadIdx.x`, `blockIdx.x`) maps directly to HIP equivalents. This category tests API name lookup, not parallel reasoning.

```c
// CUDA                          // HIP (syntactic rename)
cudaMalloc(&d_a, size);          hipMalloc(&d_a, size);
kernel<<<grid, block>>>(d_a);    hipLaunchKernelGGL(kernel, grid, block, 0, 0, d_a);
cudaMemcpy(h_a, d_a, ...);      hipMemcpy(h_a, d_a, ...);
```

**Paradigm translation** (e.g., CUDA to OpenMP): SPMD to fork-join model transformation. Explicit GPU thread indexing must be converted to loop-based parallelism with OpenMP directives. Shared memory and synchronization primitives (`__shared__`, `__syncthreads()`) must be replaced with stack-allocated arrays and implicit barrier semantics. Memory management (`cudaMalloc`/`cudaMemcpy`/`cudaFree`) is entirely eliminated.

```c
// CUDA                                    // OpenMP (paradigm translation)
__global__ void kernel(float* a, int n) {  void kernel(float* a, int n) {
  int i = blockIdx.x * blockDim.x          #pragma omp parallel for
           + threadIdx.x;                    for (int i = 0; i < n; i++) {
  if (i < n) a[i] = a[i] * 2.0f;              a[i] = a[i] * 2.0f;
}                                            }
                                           }
```

**Architecture split** (e.g., CUDA to OpenCL): Unified single-source CUDA must be split into separate host code (OpenCL runtime API calls for platform/device/context/queue management) and kernel source (`.cl` files with OpenCL C syntax). The memory model changes from CUDA's unified virtual addressing to OpenCL's explicit buffer objects. Kernel launch syntax transforms from `<<<grid, block>>>` to `clEnqueueNDRangeKernel` with explicit work-group sizing.

**Directive insertion** (e.g., sequential C to OpenMP): Adding parallelism to sequential code by identifying parallelizable loops and inserting appropriate `#pragma omp` directives with correct data-sharing clauses (`shared`, `private`, `reduction`). This is the inverse of the paradigm translation direction and tests whether the LLM can *discover* parallelism rather than *translate* it.

ParBench focuses on paradigm translation (CUDA/OpenMP/OpenCL cross-translations) because this category maximizes the semantic challenge while remaining tractable for automated verification. Syntactic renaming (CUDA to HIP) is too easy to be informative; architecture split (CUDA to OpenCL) combines paradigm translation with source-file restructuring, adding confounding complexity.

## A.3 HIP and SYCL Exclusion Rationale

Despite the large kernel-level co-occurrence counts for CUDA--HIP (633) and CUDA--SYCL (616), these pairs were excluded from the primary evaluation for distinct reasons.

**HIP exclusion:** CUDA-to-HIP translation is predominantly a syntactic renaming task. The AMD HIP API was explicitly designed as a drop-in replacement for CUDA, preserving the SPMD programming model, kernel launch syntax, and memory management API. Automated tools such as `hipify-perl` and `hipify-clang` achieve near-perfect conversion rates. Evaluating LLMs on CUDA-to-HIP translation would measure API name lookup ability rather than parallel programming reasoning -- the core capability ParBench is designed to assess.

**SYCL exclusion:** While SYCL introduces a genuinely different programming model (single-source C++ with lambda-based kernel dispatch and buffer/accessor memory management), it preserves the GPU execution model. CUDA-to-SYCL translation is more complex than CUDA-to-HIP but remains within the same architectural paradigm (GPU offload). Furthermore, SYCL benchmark coverage is concentrated almost entirely in HeCBench, limiting the diversity of evaluation instances. The CUDA-to-OpenMP direction provides a more fundamental paradigm crossing (GPU SPMD to CPU fork-join) with better benchmark diversity across Rodinia, HeCBench, XSBench, and RSBench.

## A.4 OpenACC Exclusion

OpenACC was excluded despite appearing in approximately 17 benchmarks in the expanded survey (Figure A.3). Three factors motivated this decision:

1. **Limited co-occurrence with CUDA/OpenMP**: Of the 17 benchmarks with OpenACC, only 3 also provide both CUDA and OpenMP implementations. This yields insufficient material for statistically meaningful cross-API evaluation.

2. **Paradigm overlap with OpenMP**: OpenACC's directive-based model (`#pragma acc parallel loop`) occupies a similar conceptual niche to OpenMP's target offload directives (`#pragma omp target teams distribute`). Including both would provide diminishing returns in programming-model diversity.

3. **Compiler availability**: OpenACC compilation requires the NVIDIA HPC SDK (`nvc`) or GCC with `-fopenacc`. This is a less universally available toolchain than CUDA (`nvcc`) or OpenMP (any modern C/C++ compiler), introducing a confounding variable between compiler availability and LLM translation capability.

## A.5 OpenMP Target as Case Study

OpenMP target offload (`#pragma omp target`) occupies a middle ground between CPU OpenMP and GPU-native APIs. It uses the OpenMP directive model but targets GPU execution, requiring the programmer to specify data mapping (`#pragma omp target data map(...)`) and work distribution (`#pragma omp teams distribute parallel for`) explicitly.

ParBench evaluates OpenMP target as a case study rather than a primary direction for three reasons:

1. **Compiler requirement**: OpenMP target compilation for NVIDIA GPUs requires the NVIDIA HPC compiler `nvc` (part of the NVIDIA HPC SDK 24.3), which is not universally available. Standard GCC/Clang OpenMP support targets only CPU threading. This introduces a confounding variable: a failed build may indicate compiler unavailability rather than translation quality.

2. **Limited benchmark coverage**: OpenMP target implementations are available for XSBench, RSBench, and a subset of HeCBench curated kernels (106 kernel-level co-occurrences with CUDA, as shown in Figure A.4). Rodinia does not provide OpenMP target variants.

3. **Compilation model difference**: OpenMP target generates GPU offload code through the compiler, while CPU OpenMP generates threaded CPU code. A translation from CUDA to OpenMP target preserves GPU execution semantics but changes the syntax entirely; a translation from CUDA to CPU OpenMP changes both the execution model and the syntax. These are qualitatively different evaluation targets that should not be conflated in aggregate statistics.

The case study results for OpenMP target are reported separately in the evaluation (Section 6 of the main paper) to enable direct comparison with the primary CUDA/OpenMP/OpenCL directions without confounding the aggregate pass rates.
