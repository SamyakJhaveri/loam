## IV. Benchmark Curation

The benchmark corpus was assembled through a systematic selection process: surveying available HPC benchmark repositories, analyzing kernel-level translation opportunities, and filtering to a representative subset verified through the full build/run/verify pipeline.

### A. Suite Selection

A survey of 35 open-source HPC benchmark repositories was conducted, spanning suites (13), mini-applications (12), proxy applications (4), full applications (4), libraries (4), and microbenchmarks (3). The survey covered GPU computing across multiple parallel APIs, with 30 repositories classified as Tier A (actively maintained, widely cited) and 5 as Tier B.

A central finding of the survey is that repository-level counting dramatically overstates the available benchmark material. Naive analysis identifies 21 repositories containing both CUDA and OpenMP implementations, but kernel-level analysis reveals 472 independent CUDA-OpenMP translation pairs across those same repositories \cite{HeCBench2024}. The discrepancy ranges from 20x to 60x, driven primarily by large suites such as HeCBench (325 four-API kernels) and RAJAPerf (106 six-API kernels). This motivates a kernel-centric evaluation strategy: benchmarks should be evaluated at the granularity of individual computational kernels, not entire repositories.

Five criteria guided suite selection: (1) availability of multiple API implementations of the same algorithm, (2) established community adoption with substantial citation history, (3) buildability with modern toolchains (CUDA 12, GCC 11+), (4) coverage of diverse computational domains, and (5) realistic complexity representative of production HPC workloads. Rodinia \cite{Rodinia2009} was selected as the primary suite: 22 distinct kernels across 3 APIs with over 14,000 citations, making it a de facto standard in GPU benchmarking. XSBench was selected as a secondary suite: a production-grade Monte Carlo neutron transport proxy application providing a single complex kernel with 4 API variants.

### B. Kernel Selection

From Rodinia, 22 kernels were identified with implementations across up to 3 APIs (CUDA, OpenMP, OpenCL), yielding 60 specs. Each spec was independently verified through the full build/run/verify pipeline on the reference platform (NVIDIA RTX 4070, AMD Ryzen 9 7900X, Ubuntu 22.04). Of these, 54 specs pass verification; 6 are classified as KNOWN\_FAIL due to external toolchain constraints rather than benchmark logic errors:

- 2 specs fail because CUDA 12 removed the deprecated `texture<>` reference API (kmeans-cuda, mummergpu-cuda);
- 1 spec fails due to a missing OpenGL dependency (hybridsort-cuda);
- 1 spec inherits CUDA texture dependencies in its OpenMP variant (mummergpu-omp);
- 2 OpenCL specs exhibit pre-existing runtime crashes (nn-opencl, kmeans-opencl).

These failures are documented but excluded from the evaluation corpus; they reflect toolchain evolution, not benchmark design defects.

From XSBench, 1 kernel across 4 API variants (CUDA, OpenMP, OpenCL, OpenMP target offload) yields 4 specs, all 4 verified PASS. An additional 60 HeCBench kernels (120 specs) are included in the framework schema for future expansion but were not deployed on the evaluation machine for this study.

The selected kernels span 10 computational domains: graph traversal (bfs), physics simulation (hotspot, hotspot3d, cfd, srad), machine learning (backprop, kmeans), linear algebra (lud, nw, gaussian), molecular dynamics (lavamd), image processing (dwt2d), dynamic programming (pathfinder), biophysical simulation (myocyte, heartwall), particle methods (particlefilter, streamcluster), and data structures (bptree).

[TABLE: Kernel x API verification matrix for Rodinia (22 kernels) and XSBench (1 kernel), showing PASS/KNOWN\_FAIL/not-available status for each API (CUDA, OpenMP, OpenCL)]

### C. API Coverage

CUDA serves as the primary source language, reflecting its dominant position in GPU programming. OpenMP is the primary translation target, selected because the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity (472 kernel pairs across 21 repositories). OpenCL provides a secondary target that exercises a qualitatively different programming model: explicit memory management, separate kernel compilation, and host-device code separation. Together, these three APIs cover the principal parallel programming paradigms in HPC: GPU-native (CUDA), directive-based (OpenMP), and portable heterogeneous (OpenCL).

### D. Representative Subset

The 57 verified-PASS specs (54 Rodinia + 3 XSBench standard APIs) constitute the evaluation corpus. The XSBench OpenMP target offload variant is excluded from standard evaluation batches because it requires the NVIDIA HPC compiler (nvc) and is treated as a case study. The selection is principled rather than exhaustive: the spec schema permits straightforward extension to additional suites, kernels, and APIs without modification to the evaluation harness. Each kernel in the corpus was independently verified through the complete build/run/verify pipeline prior to inclusion in any LLM evaluation experiment.

## V. Experimental Setup

This section describes the models, translation directions, augmentation protocol, evaluation metrics, and hardware configuration used in the ParBench evaluation.

### A. Models

Four large language models are evaluated, selected to span major commercial API providers and one open-weight alternative. GPT-4.1 \cite{GPT41} is accessed via Azure OpenAI; Claude Sonnet 4 \cite{ClaudeSonnet} via the Anthropic API; Gemini 2.5 Flash-Lite \cite{GeminiFlashLite} via the Google AI API; and Llama 3.3 70B \cite{Llama3} via the Groq inference API. All models are queried at temperature 0 to ensure deterministic outputs and reproducibility across runs. Reasoning and chain-of-thought modes are explicitly disabled for all models. This is a deliberate design choice: the evaluation targets raw translation competence---whether a model's internalized knowledge of parallel programming patterns suffices to produce correct translations---rather than the capacity of a multi-step reasoning scaffold to search for solutions. The model set covers three proprietary providers (OpenAI, Anthropic, Google) and one open-weight model (Meta), all accessible through standard API endpoints.

[TABLE V: Model configurations used in the evaluation. Columns: human-readable name, API model identifier, provider, access method, and parameter count (where publicly disclosed).]

### B. Translation Directions

Six translation directions are evaluated across the three parallel APIs represented in the Rodinia benchmark suite:

- CUDA to OpenMP and OpenMP to CUDA
- CUDA to OpenCL and OpenCL to CUDA
- OpenMP to OpenCL and OpenCL to OpenMP

CUDA to OpenMP serves as the primary evaluation direction, as it represents the most common real-world HPC translation need: migrating GPU-accelerated CUDA code to the portable, CPU-parallel OpenMP model \cite{Rodinia2009}. The remaining five directions provide cross-directional comparison and test whether translation difficulty is symmetric across API pairs. Not all directions apply to every kernel, as some Rodinia benchmarks lack implementations in all three APIs; the evaluation covers all valid source--target pairs within the benchmark suite.

### C. Augmentation Protocol

Source code augmentation is applied at five levels. Level L0 uses the unmodified benchmark source and serves as the baseline. Levels L1 through L4 apply the six AST-driven transforms (described in Section III) at increasing density: L1 applies one randomly selected transform at a single candidate site; L2 applies one transform at approximately 33\% of eligible sites; L3 applies three transforms at 66\% of eligible sites; and L4 applies all six transforms at 100\% of eligible sites. A fixed random seed of 42 governs all stochastic choices for reproducibility.

The augmentation protocol tests a specific hypothesis: if an LLM genuinely reasons about parallel computation structure rather than pattern-matching against memorized training examples, its translation success rate should remain stable across augmentation levels. Prior to LLM evaluation, the augmentation baseline was verified independently: 54 of 60 Rodinia specs produce correct output at all levels L1 through L4 with zero new failures introduced by augmentation, confirming that the transforms are semantics-preserving and that any variation in LLM pass rates across levels can be attributed to the model rather than to the augmentation process.

### D. Metrics

The primary evaluation metric is **Pass@1**: the fraction of translation tasks that pass the full build, run, and verify pipeline on a single evaluation (with up to two LLM attempts per task via the error-feedback retry mechanism). Each failure is classified into a diagnostic category---BUILD\_FAIL (compilation error), RUN\_FAIL (runtime crash or nonzero exit code), VERIFY\_FAIL (incorrect output), or EXTRACTION\_FAIL (malformed LLM response)---enabling fine-grained failure mode analysis beyond a single pass/fail number.

Secondary metrics include **augmentation robustness**, defined as the stability of Pass@1 across augmentation levels L0 through L4, and **self-repair rate**, the fraction of initially failing tasks recovered by the error-feedback retry loop, in which the compilation or runtime error message is appended to the conversation and the model is prompted to produce a corrected translation.

Execution timing and speedup metrics are excluded from this study. The current verification pipeline measures wall-clock time, which conflates kernel execution with I/O, memory allocation, and OS scheduling noise. Reliable performance comparison requires profiler-based kernel timing (e.g., \texttt{nvprof}/\texttt{ncu} for CUDA, \texttt{omp\_get\_wtime()} for OpenMP), which is deferred to future work.

### E. Hardware and Software

All evaluations are conducted on a single workstation to eliminate cross-machine variability. The GPU is an NVIDIA GeForce RTX 4070 (Ada Lovelace architecture, 5888 CUDA cores, 12 GB GDDR6X). The CPU is an AMD Ryzen 9 7900X (12 cores, 24 threads). The system runs Ubuntu Linux with kernel 6.8.0-40-generic.

CUDA compilation uses \texttt{nvcc} from the NVIDIA HPC SDK 24.3 (CUDA 12.3). OpenMP compilation uses GCC 12.4 with the \texttt{-fopenmp} flag. OpenCL programs link against the NVIDIA runtime from the HPC SDK. The evaluation harness and all scripting infrastructure run on Python 3.12.3. LLM API calls are issued from the same machine; network latency does not affect correctness evaluation.

[TABLE VI: Hardware and software configuration. Rows: GPU model, CPU model, operating system, CUDA version and compiler, C/C++ compiler, OpenCL runtime, Python version.]
