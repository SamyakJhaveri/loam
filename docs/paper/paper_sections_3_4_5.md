<!-- ParBench SC26 Paper — Sections III, IV, V -->
<!-- Format: IEEE conference (IEEEtran), double-anonymous -->
<!-- All numbers verified against source code and data files (2026-03-24) -->

## III. The ParBench Framework

ParBench is a benchmark framework designed to evaluate LLM-based parallel code translation through automated, end-to-end correctness assessment. The framework comprises four integrated components: (1) a declarative spec schema that encodes what constitutes correct execution for each benchmark kernel, (2) a three-stage build/run/verify harness pipeline that evaluates translated code, (3) an AST-driven augmentation engine that generates semantically equivalent code variants to probe translation robustness, and (4) an evaluation pipeline that orchestrates LLM-based translation with iterative self-repair. This section describes each component in detail.

[FIGURE 1: System architecture diagram showing the four ParBench components: Spec JSON feeds into the Harness Pipeline (Build, Run, Verify stages), the Augmentation Engine transforms source code at levels L0--L4 before prompting, and the Evaluation Pipeline orchestrates LLM calls with self-repair feedback loops. Result JSON is the final output.]

### A. Spec Schema: Declarative Correctness Contracts

Each benchmark in ParBench is described by a JSON specification (spec) that serves as a declarative contract defining what "correct execution" means for that kernel--API variant. The spec encodes all information required to build, run, and verify a benchmark without manual intervention, enabling fully automated evaluation. The schema (version 1.0.0) is formally defined in JSON Schema draft-07 and enforced by an offline validator.

A spec is organized into the following field groups:

**Identity and provenance.** The `identity` block assigns a globally unique identifier following the convention `{source_suite}-{kernel_name}-{parallel_api}` (e.g., `rodinia-bfs-cuda`), and records the parallel API from a controlled vocabulary of 14 supported APIs including CUDA, OpenMP, OpenCL, HIP, and SYCL. The `provenance` block pins the exact source repository and commit hash, ensuring reproducibility across environments.

**File partitioning.** The `files` block partitions benchmark source files into three disjoint sets: `prompt_payload` (files visible to the LLM during translation), `support_files` (build infrastructure such as Makefiles and shared headers, not shown to the LLM), and `verification_only` (reference implementations never exposed to the LLM). A fourth field, `translation_targets`, identifies the subset of `prompt_payload` that the LLM must produce---the kernel computation files. This field is central to the kernel-centric translation methodology described in Section III-D.

**Build, run, and verification.** The `build` block specifies the build system, compiler commands, environment variables, and expected executable path. The `run` block defines named input configurations (e.g., `correctness`, `performance`) with arguments, timeout, and optional environment variables. The `verification` block declares an ordered list of verification strategies---currently `exit_code` (check process return code) and `stdout_pattern` (regex match against captured standard output)---applied in sequence until a definitive PASS or FAIL is reached. Three additional strategies (`numeric_comparison`, `file_diff`, `custom_script`) are defined in the schema for future use.

**Baseline results.** The `baseline_results` block, populated by running the original implementation on the reference platform, records the expected output for each input configuration. This provides the ground truth against which translated code is compared.

The following condensed listing illustrates the essential structure using the BFS benchmark from Rodinia \cite{Rodinia2009}:

```json
{
  "identity": {
    "unique_id": "rodinia-bfs-cuda",
    "parallel_api": "cuda",
    "source_suite": "rodinia"
  },
  "files": {
    "prompt_payload": ["bfs.cu", "kernel.cu", "kernel2.cu"],
    "support_files": ["Makefile"],
    "translation_targets": ["bfs.cu", "kernel.cu", "kernel2.cu"]
  },
  "build": {
    "commands": { "build": "make CUDA_DIR=..." },
    "outputs": { "executable": "./bfs.out" }
  },
  "run": {
    "executable": "./bfs.out",
    "timeout_seconds": 300,
    "input_configurations": {
      "correctness": { "arguments": ["../../data/bfs/graph1MW_6.txt"] }
    }
  },
  "verification": {
    "strategies": [
      { "type": "exit_code", "expected": 0 }
    ]
  }
}
```

This design separates the definition of correctness from the mechanism of verification: the harness can evolve independently of what "correct" means for each kernel. Across the current benchmark collection, 184 specs are defined: 60 from Rodinia \cite{Rodinia2009}, 4 from XSBench \cite{XSBench2014}, and 120 from HeCBench \cite{HeCBench2021}.

### B. Harness Pipeline: Build, Run, Verify

The harness pipeline is a three-stage evaluation engine invoked via a command-line interface (`python3 -m harness`). Each stage consumes the output of the previous stage, and failure at any stage short-circuits subsequent stages---there is no reason to run code that did not compile, or to verify output from a crashed process.

**Build stage.** The builder resolves the spec's working directory, executes an optional clean command, runs any configure step, substitutes template variables (e.g., `${CUDA_DIR}`) in the build command, and invokes the build via a shell subprocess. After compilation, the builder verifies that the expected executable exists on disk. The build stage captures both stdout and stderr for diagnostic reporting and enforces a configurable timeout (default: 600 seconds).

**Run stage.** The runner executes the compiled binary with arguments drawn from the spec's named input configuration (typically `correctness`). Execution proceeds without a shell to avoid argument-parsing ambiguities. The runner captures stdout, stderr, exit code, and wall-clock duration, and enforces the spec-defined timeout (default: 300 seconds). An optional CPU-time measurement mode wraps execution with `/usr/bin/time -v` to capture user+system time independently of wall-clock duration.

**Verify stage.** The verifier applies the spec's verification strategies in declared order. For `exit_code` verification, the actual exit code is compared against the expected value. For `stdout_pattern` verification, a regular expression is applied to the captured stdout. The first strategy to produce a definitive PASS or FAIL terminates evaluation; if all strategies are exhausted without a conclusive result, the outcome is SKIP.

Each pipeline invocation produces one of four failure classifications---BUILD\_FAIL, RUN\_FAIL, VERIFY\_FAIL, or TIMEOUT---providing diagnostic granularity that enables systematic failure-mode analysis. A `--resume` flag allows batch evaluations to skip previously completed tasks, supporting append-only result accumulation without re-executing passing benchmarks.

### C. Augmentation Engine: Probing Robustness via Code Surface Variation

A central concern in evaluating LLM-based code translation is whether models genuinely reason about program structure or rely on memorized patterns from training data. Popular benchmarks such as those in the Rodinia suite \cite{Rodinia2009} are widely available in open-source repositories and likely present in LLM training corpora. To address this threat to validity, the augmentation engine generates semantically equivalent code variants by applying AST-level transformations that alter the syntactic surface of the source code while preserving its computational semantics.

The engine implements six transforms, each backed by libclang \cite{libclang} AST analysis to guarantee syntactic validity:

1. **SwapCondition** -- reverses operands of comparison expressions (e.g., `a < b` becomes `b > a`), with guards against side-effect-bearing subexpressions and assignments.
2. **ArithmeticTransform** -- converts between compound and expanded assignment forms (e.g., `x += 1` becomes `x = x + 1` and vice versa).
3. **ChangeNames** -- consistently renames local variables and function parameters using symbol-aware reference collection, respecting scope boundaries and OpenMP pragma clauses.
4. **TypedefExpansion** -- replaces typedef aliases with their underlying primitive types at AST-identified type-reference sites.
5. **PointerArithmeticToArrayIndex** -- converts between pointer dereference and array indexing notation (e.g., `*(arr + i)` becomes `arr[i]`).
6. **ChangeFunctionNames** -- renames internal-linkage helper functions across their definitions and all call sites within the translation unit.

All transforms operate on the parsed AST rather than on raw text, which avoids the fragility of regex-based rewriting. Each candidate rewrite is validated by re-parsing the transformed code and confirming that no new diagnostic errors are introduced. Overlapping candidates are resolved by a greedy subset-selection algorithm that maximizes the number of applied transforms without introducing conflicts.

| Level | Transform selection | Candidate fraction | Description |
|:-----:|:-------------------:|:------------------:|:------------|
| L0 | None (original) | 0% | Unmodified source code (baseline) |
| L1 | 1 transform | 1 site per transform | Minimal surface perturbation |
| L2 | 33% of transforms | 33% of candidates | Moderate obfuscation |
| L3 | 66% of transforms | 66% of candidates | Heavy obfuscation |
| L4 | All transforms | 100% of candidates | Maximum obfuscation |

Five augmentation levels (L0--L4) control the density of applied transforms. L0 is the unmodified source. At L1, exactly one transform is selected and applied to a single candidate site. Levels L2--L4 apply both transform selection and candidate-site selection at increasing fractions: the fraction mapping is $\{2: 0.33,\; 3: 0.66,\; 4: 1.0\}$, applied first to choose how many of the six transforms to run, then within each selected transform to choose how many eligible AST nodes to rewrite (with a minimum of one via $\max(1, \lfloor n \cdot f \rfloor)$).

The augmentation baseline confirms that the transforms are semantics-preserving: 54 of 60 Rodinia specs pass the build/run/verify pipeline at all levels L1--L4, with zero correctness regressions relative to L0. The 6 specs that fail at L0 (due to CUDA 12 deprecations, missing system libraries, and pre-existing runtime errors) also fail identically at all augmented levels, confirming that augmentation introduces no new failures.

### D. Evaluation Pipeline: Kernel-Centric Translation

The evaluation pipeline orchestrates LLM-based parallel code translation through a structured prompt-response-verify cycle. Its design reflects a deliberate methodological choice: kernel-centric translation, in which only the parallel computation files are translated while the surrounding build infrastructure remains untouched.

**Kernel-centric methodology.** Prior work on repository-level code translation \cite{ParEvalRepo2025} demonstrated that LLM pass rates collapse to 0% for programs exceeding approximately 133 source lines of code (SLoC), largely due to the difficulty of simultaneously generating correct build-system artifacts alongside translated source code. ParBench isolates the translation skill by feeding only the `translation_targets` files (the parallel kernel code) to the LLM; Makefiles, shared headers, serial baselines, and utility code remain unchanged in the target directory. This design enables evaluation of whether an LLM can correctly map parallel programming patterns from one API to another, independent of its ability to replicate project file organization.

**Prompt structure.** Each translation prompt consists of a system message establishing the role of a parallel programming expert and a user message containing: (1) the source kernel code with API-specific syntax highlighting, (2) the target API and the filenames the LLM must produce, (3) the target build command for compilation compatibility, and (4) read-only target infrastructure context (non-kernel files from the target directory) so the LLM can match expected function signatures and data structures. Source support headers are included with instructions to inline definitions rather than emit unresolvable `#include` directives.

**Self-repair loop.** On build failure, the pipeline feeds the compiler error message back to the LLM as a follow-up prompt, requesting a corrected translation. This iterative self-repair mechanism allows a configurable number of attempts before a final BUILD\_FAIL classification. The self-repair loop mirrors the realistic workflow of a developer iterating on compiler errors; it also provides data on which failure modes are recoverable by the model versus those that indicate fundamental translation deficiencies.

**Complexity taxonomy.** To enable stratified analysis of translation difficulty, each source--target pair is classified into one of four complexity classes based on the file cardinality of the translation: `single_file` (1 source file to 1 target file), `multi_to_single` (N source files to 1 target file), `single_to_multi` (1 source file to N targets, characteristic of CUDA-to-OpenCL translations where the host-device split is inherent to the programming model), and `multi_to_multi` (N source files to M target files).

**Model-agnostic design.** The pipeline supports multiple LLM providers through a model registry that maps human-readable identifiers to provider-specific API configurations. All evaluations use temperature 0 for deterministic reproducibility. The framework currently supports Anthropic, OpenAI, Azure OpenAI, Google, and Groq API endpoints, enabling cross-model comparison under identical prompt content and evaluation conditions.


## IV. Benchmark Curation

The benchmark corpus was assembled through a systematic selection process: surveying available HPC benchmark repositories, analyzing kernel-level translation opportunities, and filtering to a representative subset verified through the full build/run/verify pipeline.

### A. Suite Selection

A survey of 35 open-source HPC benchmark repositories was conducted, spanning suites, mini-applications, proxy applications, full applications, libraries, and microbenchmarks. The survey covered GPU computing across multiple parallel APIs.

A central finding of the survey is that repository-level counting dramatically overstates the available benchmark material. Naive analysis identifies 21 repositories containing both CUDA and OpenMP implementations, but kernel-level analysis reveals 472 independent CUDA--OpenMP translation pairs across those same repositories. The discrepancy ranges from 20$\times$ to 60$\times$, driven primarily by large suites such as HeCBench \cite{HeCBench2021} (325 four-API kernels) and RAJAPerf (106 six-API kernels). This motivates a kernel-centric evaluation strategy: benchmarks should be evaluated at the granularity of individual computational kernels, not entire repositories.

Five criteria guided suite selection: (1) availability of multiple API implementations of the same algorithm, (2) established community adoption with substantial citation history, (3) buildability with modern toolchains (CUDA 12, GCC 11+), (4) coverage of diverse computational domains, and (5) realistic complexity representative of production HPC workloads. Rodinia \cite{Rodinia2009} was selected as the primary suite: 22 distinct kernels across 3 APIs with over 14,000 citations, making it a de facto standard in GPU benchmarking. XSBench \cite{XSBench2014} was selected as a secondary suite: a production-grade Monte Carlo neutron transport proxy application providing a single complex kernel with 4 API variants.

### B. Kernel Selection

From Rodinia, 22 kernels were identified with implementations across up to 3 APIs (CUDA, OpenMP, OpenCL), yielding 60 specs. Each spec was independently verified through the full build/run/verify pipeline on the reference platform. Of these, 54 specs pass verification; 6 are classified as KNOWN\_FAIL due to external toolchain constraints rather than benchmark logic errors:

- 2 specs fail because CUDA 12 removed the deprecated `texture<>` reference API (kmeans-cuda, mummergpu-cuda);
- 1 spec fails due to a missing OpenGL dependency (hybridsort-cuda);
- 1 spec inherits CUDA texture dependencies in its OpenMP variant (mummergpu-omp);
- 2 OpenCL specs exhibit pre-existing runtime crashes (nn-opencl, kmeans-opencl).

These failures are documented but excluded from the evaluation corpus; they reflect toolchain evolution, not benchmark design defects.

From XSBench, 1 kernel across 4 API variants (CUDA, OpenMP, OpenCL, OpenMP target offload) yields 4 specs, all 4 verified PASS. An additional 60 HeCBench kernels (120 specs) are included in the framework schema for future expansion but were not deployed on the evaluation machine for this study.

The selected kernels span 10 computational domains: graph traversal (bfs), physics simulation (hotspot, hotspot3d, cfd, srad), machine learning (backprop, kmeans), linear algebra (lud, nw, gaussian), molecular dynamics (lavamd), image processing (dwt2d), dynamic programming (pathfinder), biophysical simulation (myocyte, heartwall), particle methods (particlefilter, streamcluster), and sorting (b+tree).

[TABLE III: Kernel $\times$ API verification matrix for Rodinia (22 kernels) and XSBench (1 kernel), showing PASS/KNOWN\_FAIL/not-available status for each API (CUDA, OpenMP, OpenCL)]

### C. API Coverage

CUDA serves as the primary source language, reflecting its dominant position in GPU programming. OpenMP is the primary translation target, selected because the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity (472 kernel pairs across 21 repositories). OpenCL provides a secondary target that exercises a qualitatively different programming model: explicit memory management, separate kernel compilation, and host-device code separation. Together, these three APIs cover the principal parallel programming paradigms in HPC: GPU-native (CUDA), directive-based (OpenMP), and portable heterogeneous (OpenCL).

### D. Representative Subset

The 57 verified-PASS specs (54 Rodinia + 3 XSBench standard APIs) constitute the evaluation corpus. The XSBench OpenMP target offload variant is excluded from standard evaluation batches because it requires the NVIDIA HPC compiler (`nvc`) and is treated as a case study. The selection is principled rather than exhaustive: the spec schema permits straightforward extension to additional suites, kernels, and APIs without modification to the evaluation harness. Each kernel in the corpus was independently verified through the complete build/run/verify pipeline prior to inclusion in any LLM evaluation experiment.


## V. Experimental Setup

This section describes the models, translation directions, augmentation protocol, evaluation metrics, and hardware configuration used in the evaluation.

### A. Models

Four large language models are evaluated, selected to span major commercial API providers and one open-weight alternative: GPT-4.1 (OpenAI, accessed via Azure), Claude Sonnet 4 (Anthropic), Gemini 2.5 Flash-Lite (Google), and Llama 3.3 70B (Meta, accessed via Groq). All models are queried at temperature 0 to ensure deterministic outputs and reproducibility across runs. Reasoning and chain-of-thought modes are explicitly disabled for all models. This is a deliberate design choice: the evaluation targets raw translation competence---whether a model's internalized knowledge of parallel programming patterns suffices to produce correct translations---rather than the capacity of a multi-step reasoning scaffold to search for solutions.

[TABLE IV: Model configurations. Columns: human-readable name, API model identifier, provider, access method, and parameter count (where publicly disclosed).]

### B. Translation Directions

Six translation directions are evaluated across the three parallel APIs:

- CUDA $\to$ OpenMP and OpenMP $\to$ CUDA
- CUDA $\to$ OpenCL and OpenCL $\to$ CUDA
- OpenMP $\to$ OpenCL and OpenCL $\to$ OpenMP

CUDA $\to$ OpenMP serves as the primary evaluation direction, as it represents the most common real-world HPC translation need: migrating GPU-accelerated CUDA code to the portable, CPU-parallel OpenMP model. The remaining five directions provide cross-directional comparison and test whether translation difficulty is symmetric across API pairs. Not all directions apply to every kernel, as some benchmarks lack implementations in all three APIs; the evaluation covers all valid source--target pairs within the benchmark suite.

### C. Augmentation Protocol

Source code augmentation is applied at five levels. Level L0 uses the unmodified benchmark source and serves as the baseline. Levels L1 through L4 apply the six AST-driven transforms (described in Section III-C) at increasing density: L1 applies one randomly selected transform at a single candidate site; L2 selects 33% of transforms and applies each to 33% of eligible candidate sites; L3 selects 66% of transforms at 66% of sites; and L4 applies all transforms at all sites. A fixed random seed of 42 governs all stochastic choices for reproducibility.

The augmentation protocol tests a specific hypothesis: if an LLM genuinely reasons about parallel computation structure rather than pattern-matching against memorized training examples, its translation success rate should remain stable across augmentation levels. The augmentation baseline was verified prior to LLM evaluation (Section III-C): zero new failures were introduced at any level, confirming that any variation in LLM pass rates across levels can be attributed to the model rather than to the augmentation process.

### D. Metrics

The primary evaluation metric is **Pass@1**: the fraction of translation tasks that pass the full build, run, and verify pipeline on a single evaluation (with up to two LLM attempts per task via the error-feedback self-repair mechanism). Each failure is classified into a diagnostic category---BUILD\_FAIL (compilation error), RUN\_FAIL (runtime crash or nonzero exit code), VERIFY\_FAIL (incorrect output), or EXTRACTION\_FAIL (malformed LLM response)---enabling fine-grained failure-mode analysis beyond a single pass/fail number.

Secondary metrics include **augmentation robustness**, defined as the stability of Pass@1 across augmentation levels L0 through L4, and **self-repair rate**, the fraction of initially failing tasks recovered by the error-feedback retry loop.

Execution timing and speedup metrics are excluded from this study. The current verification pipeline measures wall-clock time, which conflates kernel execution with I/O, memory allocation, and OS scheduling noise. Reliable performance comparison requires profiler-based kernel timing (e.g., `nvprof`/`ncu` for CUDA, `omp_get_wtime()` for OpenMP), which is deferred to future work.

### E. Hardware and Software

All evaluations are conducted on a single workstation to eliminate cross-machine variability. The GPU is an NVIDIA GeForce RTX 4070 (Ada Lovelace architecture, 5888 CUDA cores, 12 GB GDDR6X). The CPU is an AMD Ryzen 9 7900X (12 cores, 24 threads). The system runs Ubuntu 24.04 LTS (kernel 6.8).

CUDA compilation uses `nvcc` from the NVIDIA HPC SDK 24.3 (CUDA 12.3). C/C++ compilation uses GCC 12.4 with the `-fopenmp` flag for OpenMP targets. OpenCL programs link against the NVIDIA runtime from the HPC SDK. The evaluation harness and all scripting infrastructure run on Python 3.12.3. LLM API calls are issued from the same machine; network latency does not affect correctness evaluation.

[TABLE V: Hardware and software configuration. Rows: GPU model, CPU model, operating system, CUDA toolkit version, C/C++ compiler, OpenCL runtime, Python version.]
