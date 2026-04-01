## S4 Benchmark Curation

The benchmark corpus was assembled through a four-stage systematic process: surveying the landscape of open-source HPC benchmark repositories, quantifying kernel-level translation opportunities across parallel APIs, filtering candidate kernels through build/run/verify automation requirements, and verifying each selected kernel through the complete pipeline on the evaluation platform.

### 4.A Suite Selection

**Survey methodology.** We conducted a systematic survey of open-source HPC benchmark repositories, beginning with 40 candidate archives identified from the ECP proxy application catalog, published benchmark suites, and HPC conference proceedings. After excluding 3 failed downloads and 2 repositories with insufficient documentation, 35 repositories were analyzed in detail. These span six benchmark types: suites (e.g., HeCBench \cite{HeCBench2023}, Rodinia \cite{Rodinia2009}, RAJAPerf, NAS NPB), mini-applications (e.g., BabelStream, CloverLeaf, LULESH, miniBUDE), proxy applications (e.g., SW4lite, CoMD, Kripke), full applications (e.g., LAMMPS, GROMACS), libraries (e.g., Kokkos Kernels, AMReX, MFEM), and microbenchmarks (e.g., STREAM, OSU OMB). Of the 35, 30 were classified Tier A (high quality: documented build, automated verification, active maintenance) and 5 as Tier B (medium quality: partial verification or limited API coverage). Each repository was cataloged by the parallel APIs it provides, its kernel count, build system, and verification method.

**Repository-level vs. kernel-level counting.** A central finding of the survey is that repository-level counting dramatically understates the available benchmark material for translation evaluation. The API co-occurrence matrix (Figure 2) identifies 6 repositories containing both CUDA and OpenMP implementations. However, kernel-level analysis -- enumerating individual computational kernels that have verified equivalent implementations across APIs -- reveals 472 independent CUDA--OpenMP translation pairs across those same 6 repositories, a 79x multiplier (Figure 3). This extreme concentration is driven by large multi-kernel suites: HeCBench alone contributes 325 CUDA--OpenMP kernel pairs, RAJAPerf contributes 106, and Rodinia contributes 19. The same pattern holds across other API pairs: 633 CUDA--HIP kernel pairs (across 3 repositories, a 211x multiplier) and 616 CUDA--SYCL pairs (across 2 repositories, a 308x multiplier). This finding motivates a kernel-centric evaluation strategy in which benchmarks are evaluated at the granularity of individual computational kernels rather than entire repositories.

[Figure 2: API co-occurrence heatmap illustrating which parallel APIs appear together across the 35 surveyed repositories. The heatmap is derived from the API pairwise coverage matrix, with cell values indicating the number of repositories supporting each API pair.]

[Figure 3: Repository-level vs. kernel-level translation pair counts. Left bars show the number of repositories containing both APIs; right bars show the number of independent kernel-level translation pairs. The multipliers (79x--308x) demonstrate that repository-level counting substantially underestimates the translation evaluation opportunity.]

[TABLE 3: Survey -- Kernel-Level Translation Pair Counts.]

| API Pair | Repos with Both APIs | Kernel Pairs Available | Primary Sources |
|----------|:--------------------:|:---------------------:|:---------------|
| CUDA -- HIP | 3 | 633 | HeCBench (504), RAJAPerf (106), CloverLeaf (16) |
| CUDA -- SYCL | 2 | 616 | HeCBench (487), RAJAPerf (106), CloverLeaf (16) |
| CUDA -- OpenMP | 6 | 472 | HeCBench (325), RAJAPerf (106), Rodinia (19) |
| HIP -- OpenMP | 2 | 453 | HeCBench (324), RAJAPerf (106), CloverLeaf (16) |
| CUDA -- OpenCL | 6 | ~200 | Rodinia (19), Parboil, SHOC |

*The CUDA--OpenCL kernel count is approximate because OpenCL variants in HeCBench and RAJAPerf are not organized as separate directories with consistent naming conventions, preventing automated kernel-level enumeration. The count reflects Rodinia's 19 verified pairs plus manual spot-checks of Parboil and SHOC.*

**Selection criteria.** Five criteria guided suite selection from the surveyed repositories:

1. **Multi-API kernel equivalence.** The repository must provide implementations of the *same* kernel in multiple parallel APIs within the same source tree, ensuring that translation pairs have authoritative reference implementations rather than independently developed programs.
2. **Build-run-verify automation.** Each kernel must be buildable, runnable, and verifiable without human intervention, using Makefiles or CMake, command-line arguments, and deterministic output.
3. **Self-checking correctness.** Kernels must produce self-checking output -- deterministic checksums, tolerance-bounded numerical comparison, or labeled correctness indicators (e.g., `PASS`/`FAIL`, `verify()`) -- enabling automated correctness verification without external reference files.
4. **Open-source availability.** All source code must be publicly available under an open-source license, ensuring reproducibility.
5. **Domain diversity.** Selected suites should collectively span a broad range of computational domains (graph traversal, stencil computation, linear algebra, molecular dynamics, machine learning, signal processing, etc.) to avoid over-representing any single algorithmic pattern.

These criteria are intentionally conservative: they exclude repositories that require interactive execution, external datasets not bundled with the source, or proprietary licenses. Applying them to the 35 surveyed repositories yields five suites that satisfy all five criteria and collectively provide maximum coverage of the CUDA--OpenMP--OpenCL API triple.

### 4.B Kernel Selection

Kernel selection proceeds in two stages: selection from HeCBench (which provides the largest pool of multi-API kernels) and curation of kernels from Rodinia and three additional suites.

**HeCBench selection funnel.** HeCBench \cite{HeCBench2023} is the largest source of multi-API kernel implementations in the survey, with 513 kernels spanning CUDA, HIP, SYCL, and OpenMP. We applied a structured selection funnel to identify kernels suitable for automated translation evaluation [Figure 4]:

1. **4-API filter.** 327 kernels provide implementations in all four APIs (CUDA, HIP, SYCL, OpenMP).
2. **Build system filter.** 325 of these 327 have Makefiles present in the CUDA variant (2 excluded for missing build infrastructure).
3. **Self-checking filter.** 242 of the 325 contain self-checking output patterns -- string matching for `PASS`, `FAIL`, `verify`, or `correct` in the source -- enabling automated correctness verification.
4. **Complexity filter.** Kernels with more than 15 source files (too complex for single-prompt translation) or fewer than 2 files (too trivial to exercise meaningful translation competence) were excluded, as were kernels requiring external input data files not bundled with the source.
5. **Domain diversity selection.** From the remaining pool, 60 kernels were selected to maximize coverage across computational domains.

[Figure 4: HeCBench kernel selection funnel. Starting from 327 kernels with all 4 API variants, successive filters for build infrastructure (325), self-checking patterns (242), complexity bounds, and domain diversity yield the 60-kernel working set.]

The 60 selected HeCBench kernels span 41 distinct computational domains, including machine learning (6 kernels: backprop, geglu, knn, maxpool3d, rmsnorm, softmax-online), signal processing (4: convolutionseparable, dct8x8, fft, fwt), cryptography (3: aes, chacha20, secp256k1), bioinformatics (2: deredundancy, nw), dense linear algebra (2: gaussian, lud), graph algorithms (2: floydwarshall, mis), image processing (2: bilateral, sobel), memory bandwidth (2: babelstream, triad), numerical linear algebra (2: eigenvalue, thomas), and 29 additional domains with one kernel each. All 60 CUDA variants pass build/run/verify on the evaluation platform; 41 of the 60 OpenMP variants pass (68.3%), with the remaining 19 exhibiting upstream HeCBench issues (missing OMP source directories, numerical mismatches, runtime crashes, or timeouts) rather than ParBench harness defects.

From this 60-kernel working set, a curated subset of **10 kernels** was selected for inclusion in the evaluation corpus. These 10 were chosen for verified correctness across multiple APIs and maximum domain diversity: stencil computation (stencil1d, heat2d, iso2dfd), graph algorithms (floydwarshall, page-rank), combinatorial search (nqueen), molecular dynamics (md), signal processing (convolution1d, scan), and numerical methods (jacobi). The curated subset provides 25 specs across three API variants (CUDA, CPU OpenMP, and OMP-target GPU offload).

**Rodinia.** Rodinia \cite{Rodinia2009} provides ParBench's primary evaluation substrate. With thousands of citations, Rodinia is among the most-studied GPU benchmark suites in HPC literature, and critically provides CUDA, OpenMP, and OpenCL implementations of most kernels in the same source tree -- making it ideal for translation benchmarking where the reference implementation for each API is authoritative. ParBench includes 60 Rodinia specs covering 22 kernels across three APIs (22 CUDA, 18 OpenMP, 20 OpenCL; coverage is non-uniform because not all kernels have all three API variants). After systematic verification on the evaluation platform, 54/60 achieve PASS and 6 are KNOWN\_FAIL for platform-specific reasons:

- 2 specs fail because CUDA 12 removed the deprecated `texture<>` reference API (kmeans-cuda, mummergpu-cuda);
- 1 spec fails due to a missing OpenGL dependency (hybridsort-cuda);
- 1 spec inherits CUDA texture dependencies in its OpenMP variant (mummergpu-omp);
- 2 OpenCL specs exhibit pre-existing runtime crashes (nn-opencl, kmeans-opencl).

These failures are documented but excluded from the evaluation corpus; they reflect toolchain evolution, not benchmark design defects.

However, Rodinia's age and wide availability raise a legitimate concern: its source code is likely present in LLM training corpora, potentially inflating pass rates through memorization rather than genuine translation competence. To address this threat to validity and broaden domain coverage, ParBench includes four additional benchmark suites.

**XSBench** \cite{XSBench2014} is a Monte Carlo neutron transport proxy application that implements the continuous-energy macroscopic cross-section lookup kernel from OpenMC. It provides 4 specs (CUDA, OpenMP, OpenCL, OMP-target), all 4 PASS. XSBench is included specifically because it is also evaluated in prior repository-level work \cite{ParEvalRepo2025}, enabling direct comparison of evaluation granularity on the same kernel.

**RSBench and mixbench.** RSBench \cite{RSBench2014} (4 specs: CUDA, OpenMP, OpenCL, OMP-target) is a simplified reactor simulation proxy derived from the same OpenMC cross-section lookup as XSBench but using a multipole method, adding complex arithmetic and Faddeeva function evaluation patterns less likely to appear in training data. mixbench \cite{mixbench2017} (3 specs: CUDA, OpenMP, OpenCL) is a GPU micro-benchmark measuring the balance between compute throughput and memory bandwidth -- the operational intensity axis of the roofline model. Together they contribute domain diversity beyond Rodinia's traditional HPC kernels: nuclear physics simulation and fine-grained GPU characterization.

### 4.C API Coverage

The survey data directly inform ParBench's API selection. CUDA serves as the primary source language, reflecting its dominant position in GPU programming: it appears in more surveyed repositories than any other GPU-native API and contributes the largest kernel count in the survey. OpenMP is the primary translation target: the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity among CPU-targeting APIs, with 472 kernel pairs across 6 repositories (Table 3). This is not coincidental -- OpenMP's pragma-based parallelism model makes it the natural CPU-parallel counterpart to CUDA's GPU-native model, and benchmark developers routinely provide both implementations.

Although CUDA--HIP and CUDA--SYCL yield higher raw kernel-pair counts (633 and 616 respectively; Table 3), these pairs represent a qualitatively different --- and substantially easier --- translation challenge. HIP is designed as a near-syntactic mirror of CUDA: `cudaMalloc` maps to `hipMalloc`, kernel launch syntax is preserved verbatim, and thread-index arithmetic (`threadIdx.x`, `blockIdx.x`) transfers unchanged. SYCL similarly retains the single-source GPU execution model, substituting CUDA runtime calls with C++ accessor patterns. In contrast, CUDA-to-OpenMP translation requires structural program transformation: SPMD thread-index arithmetic must be refactored into fork-join loop parallelism, explicit GPU memory management (`cudaMalloc`/`cudaMemcpy`/`cudaFree`) must be eliminated entirely, and synchronization primitives (`__syncthreads()`) must be replaced with implicit OpenMP barrier semantics or explicit `critical`/`atomic` sections. This paradigm gap makes CUDA--OpenMP the most scientifically informative translation direction for evaluating whether LLMs reason about parallel structure rather than performing surface-level API renaming.

OpenCL provides a secondary translation target that exercises a qualitatively different programming model from both CUDA and OpenMP. Where CUDA uses unified host-device source files and implicit memory management (in modern CUDA), and OpenMP uses compiler directives over sequential code, OpenCL requires explicit kernel compilation from string sources, manual buffer management, and strict host-device code separation. Rodinia's particular strength lies in its OpenCL coverage: 20 of 22 Rodinia kernels have OpenCL implementations, compared to only sparse OpenCL coverage in HeCBench and RAJAPerf. This makes Rodinia the primary source for OpenCL translation pairs.

[TABLE: Programming model characteristics of the three primary translation APIs. These differences define the structural transformation challenges that LLM-based translation must address.]

| Property | CUDA | OpenMP | OpenCL |
|:---------|:-----|:-------|:-------|
| Execution model | SPMD (warps of 32 threads) | Fork-join thread teams | NDRange work-groups |
| Memory management | Explicit device allocation (`cudaMalloc`/`cudaMemcpy`) | Implicit shared CPU memory | Explicit buffer objects (`clCreateBuffer`/`clEnqueueReadBuffer`) |
| Kernel specification | Compiled with host code (`__global__` functions) | Pragma directives (`#pragma omp parallel for`) | Runtime string compilation (`clCreateProgramWithSource`) |
| Source structure | Single file (host + device code interleaved) | Single file (directives annotate sequential code) | Separate host program + `.cl` kernel files |
| Thread indexing | `threadIdx.x + blockIdx.x * blockDim.x` | Loop iteration variable or `omp_get_thread_num()` | `get_global_id(0)` |

OpenMP target offload (OMP-target) provides a fourth API that uses compiler-directed GPU offloading via `#pragma omp target`. It is available for XSBench, RSBench, and the HeCBench curated kernels, and requires the NVIDIA HPC compiler (`nvc`) rather than standard GCC. Because `nvc` is not universally available and OMP-target's compilation model differs substantially from CPU OpenMP, OMP-target directions are evaluated as case studies rather than as part of the standard evaluation. OpenACC was considered but excluded: it co-occurs with CUDA in only 3 of the 35 surveyed repositories (Figure 2), providing insufficient evaluation material. Moreover, OpenACC's directive-based model (`#pragma acc parallel`) occupies the same paradigm niche as OpenMP, offering less programming-model diversity than OpenCL as a secondary target.

Together, these four APIs cover the principal parallel programming paradigms in HPC: GPU-native (CUDA), directive-based CPU parallelism (OpenMP), portable heterogeneous compute (OpenCL), and directive-based GPU offload (OMP-target). The API pairwise coverage matrix from the survey (Table 3) confirms that CUDA--OpenMP is the highest-volume translation direction, justifying its selection as the primary evaluation axis.

### 4.D Evaluation Corpus

The five suites contribute a total of 96 benchmark specifications, of which 88 achieve PASS through the complete build/run/verify pipeline and 8 are KNOWN\_FAIL (Table 4). The 88 verified-PASS specs constitute the evaluation corpus.

[TABLE 4: Suite summary showing total specs, verified PASS, KNOWN\_FAIL, and API coverage for each of the five benchmark suites.]

| Suite | Kernels | Total Specs | PASS | KNOWN\_FAIL | APIs |
|:------|:-------:|:-----------:|:----:|:----------:|:-----|
| Rodinia | 22 | 60 | 54 | 6 | CUDA, OpenMP, OpenCL |
| HeCBench (curated) | 10 | 25 | 23 | 2 | CUDA, OpenMP, OMP-target |
| XSBench | 1 | 4 | 4 | 0 | CUDA, OpenMP, OpenCL, OMP-target |
| RSBench | 1 | 4 | 4 | 0 | CUDA, OpenMP, OpenCL, OMP-target |
| mixbench | 1 | 3 | 3 | 0 | CUDA, OpenMP, OpenCL |
| **Total** | **35** | **96** | **88** | **8** | |

The selected kernels span computational domains including graph traversal (bfs, floydwarshall, page-rank), physics simulation (hotspot, hotspot3d, cfd, srad, iso2dfd), machine learning (backprop, nn), linear algebra (lud, nw), molecular dynamics (lavamd, md), nuclear physics (xsbench, rsbench), stencil computation (stencil1d, heat2d, jacobi), signal processing (convolution1d, scan), biophysical simulation (myocyte, heartwall), particle methods (particlefilter, streamcluster), dynamic programming (pathfinder), combinatorial search (nqueen), and GPU micro-benchmarking (mixbench).

At L0 (unaugmented), the corpus yields 142 unique translation pairs per model across six standard translation directions, with two additional OMP-target directions evaluated as case studies. The OMP-target variants are included selectively: XSBench and RSBench OMP-target specs serve as case studies requiring the NVIDIA HPC compiler, while HeCBench OMP-target specs participate in standard evaluation where the target spec passes verification. The selection is principled rather than exhaustive: the spec schema permits straightforward extension to additional suites, kernels, and APIs without modification to the evaluation harness. Each kernel in the corpus was independently verified through the complete build/run/verify pipeline prior to inclusion in any LLM evaluation experiment.
