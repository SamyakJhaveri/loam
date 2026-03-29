# ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness

**Alternative title:** ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation

**Venue:** SC26 -- Supercomputing 2026 (full technical paper)
**Format:** ACM sigconf double-column, ~10 pages + appendices
**Status:** DRAFT -- S1--S8 complete; revised with 562-task 3-model data (2026-03-28)
**Author:** \author{[Anonymous for Review]}

---

## Abstract

Large language models (LLMs) are increasingly applied to parallel code generation, yet no benchmark framework systematically evaluates their ability to *translate* parallel code across GPU programming APIs -- and prior approaches share a critical blind spot: benchmark codes widely known in the HPC community are also present in LLM training data, making it impossible to distinguish genuine parallel reasoning from memorized translations. We present **ParBench**, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level, with an integrated augmentation engine that systematically tests any reliance on training-data pattern-matching. ParBench curates 184 specs across three benchmark suites (Rodinia, HeCBench, XSBench), three parallel APIs (CUDA, OpenMP, OpenCL), and twelve translation directions. Evaluating three LLMs across 562 translation tasks spanning 18 Rodinia kernels, 1 XSBench kernel, twelve directions, and five augmentation levels, we find a striking two-tier capability gap: Claude Sonnet 4.6 achieves 54.26% PASS [47.1%, 61.2%], while Gemini 2.5 Flash-Lite (8.56% [5.3%, 13.5%]) and Llama 3.3 70B (10.16% [6.6%, 15.3%]) are statistically indistinguishable (Fisher's p=1.0, OR=0.83) -- a large effect (Cohen's h > 1.0, chi2(2)=136.93, p < 0.001). On the primary CUDA-to-OpenMP direction at L0, Claude Sonnet 4.6 achieves 56.3% (9/16 Rodinia kernels) -- compared to 0% in repository-level approaches \cite{ParEvalRepo2025}. BUILD\_FAIL accounts for 32.03% of all tasks; VERIFY\_FAIL is rare at 9.79% (55/562), indicating that when LLM-translated code compiles and runs, the parallel computation logic is largely correct. An AST-driven augmentation engine applies six semantics-preserving transforms at five levels (L0--L4); 54/60 Rodinia specs PASS at all levels L1--L4 with zero correctness regressions, confirming level-invariant semantics preservation. LLM augmentation robustness evaluation reveals that augmentation level has no statistically significant effect on pass rate (Cochran-Armitage p=0.22), though per-model analysis shows Claude Sonnet 4.6 maintains stable pass rates across all five augmentation levels while Gemini 2.5 Flash-Lite degrades from 18.8% at L0 to 0.0% at L4, providing evidence that augmentation robustness discriminates structural reasoning from surface pattern-matching. ParBench is publicly available as an extensible framework for the HPC community.

---

## S1 Introduction

### 1.1 Motivation

The rapid advance of large language models in code generation has raised a practical question of significant interest to the high-performance computing community: can LLMs reliably translate parallel code across GPU programming APIs? Such translation has clear practical value. Scientific applications written in CUDA for NVIDIA hardware must increasingly support AMD and Intel accelerators via OpenMP, OpenCL, HIP, or SYCL. Legacy codebases developed for one API must be ported to newer frameworks as hardware landscapes evolve. The manual cost of this porting work is substantial -- experienced GPU programmers spend days to weeks translating non-trivial kernels, ensuring thread-index arithmetic is correct, memory access patterns are coalesced, and synchronization semantics are preserved.

Parallel code is qualitatively different from sequential code in ways that matter for LLM evaluation. Thread synchronization, shared memory management, warp-level operations, and API-specific idioms (e.g., CUDA's `threadIdx`/`blockIdx` vs. OpenMP's `omp_get_thread_num()`) represent a rich, structured problem space that existing code benchmarks do not address. A model that can generate a correct Python function from a docstring has not demonstrated any ability to reason about GPU memory hierarchies or thread-index arithmetic. These are distinct capabilities, and they require distinct evaluation infrastructure.

### 1.2 The Gap in Existing Evaluation

The existing landscape of code benchmarks does not address kernel-level parallel code translation. Three categories of related work highlight what is missing:

**Sequential code benchmarks** such as HumanEval \cite{HumanEval2021} and SWE-bench \cite{SWEbench2024} evaluate code synthesis or software engineering tasks on sequential, primarily Python codebases. Parallelism is absent by design. Pass rates on these benchmarks reveal nothing about an LLM's ability to reason about thread-level concurrency or GPU memory models.

**Parallel code generation benchmarks** such as ParEval \cite{ParEval2024} evaluate whether LLMs can *synthesize* parallel code from scratch given a natural-language description. ParEval's 420 tasks span OpenMP, MPI, CUDA, and Kokkos, and represent a valuable contribution to understanding LLM code generation capability. However, synthesis from description is a fundamentally different task from translation between parallel APIs -- the source code structure, idioms, and existing thread decomposition must be preserved and adapted, not invented.

**Repository-level translation** is evaluated by ParEval-Repo \cite{ParEvalRepo2025}, which tests translation of six full HPC applications (109--3,039 source lines of code) across three directions (CUDA-to-OpenMP-Offload, CUDA-to-Kokkos, OpenMP-to-OpenMP-Offload) using five state-of-the-art models. The finding is definitive: no model achieves pass@k > 0 on applications larger than 133 SLoC. The authors identify a specific root cause: models must generate Makefiles and build infrastructure alongside the translated code, and build-system generation is the binding constraint, not parallel logic translation. ParEval-Repo even includes XSBench -- a widely-used Monte Carlo neutron transport kernel -- and achieves 0% pass for all models.

**Training data contamination -- the invisible gap.** A fourth and more fundamental gap cuts across all of the above: the benchmark codes used in prior work are already known to the models that trained on them. Rodinia \cite{Rodinia2009} (introduced in 2009) has been cited thousands of times, forked and republished in hundreds of GitHub repositories, and discussed in blog posts, tutorials, and academic papers that are standard LLM training data. XSBench, HPL, LULESH, and similar proxy applications are similarly ubiquitous. An LLM that has seen `backprop.cu` during pre-training need not understand thread-index arithmetic to produce a plausible OpenMP translation -- it can pattern-match from a memorized example. Without a mechanism to systematically vary the input code, there is no way to distinguish genuine parallel reasoning from training-data recall. This is not a criticism of any specific prior work; it is a structural limitation of evaluating LLM capability on any well-known, widely-published codebase. ParBench addresses this directly: the augmentation engine applies six AST-level transforms that alter variable names, condition orderings, arithmetic forms, and function identifiers, producing code that cannot be matched against any published version. The augmentation results presented in this paper confirm the practical importance of this concern: at least one evaluated model exhibits sharp pass-rate degradation under augmentation, providing direct evidence of reliance on surface pattern-matching (Section 6.5). Augmentation is a methodological necessity -- without it, LLM evaluation on HPC benchmarks is partially measuring what the model has memorized.

**The gap in benchmark selection rationale.** A final dimension on which prior work is incomplete is the *why* of benchmark selection. Which parallel APIs matter most? Which kernels are representative? Existing frameworks do not answer these questions systematically. ParBench's selection is grounded in a comprehensive empirical survey of 35 open-source HPC repositories covering all major parallel programming models. That survey identified 472 CUDA-OpenMP kernel pairs across 21 repositories -- the largest available translation opportunity in the ecosystem, and the practical bottleneck for real-world GPU-to-CPU portability work. It further identified which benchmark suites provide the same kernel implemented across multiple APIs (Rodinia, HeCBench, XSBench), which have automatable build/run/verify pipelines, and which have self-checking output patterns. The choice of CUDA-to-OpenMP as the primary translation direction, and of Rodinia as the primary evaluation substrate, follows directly from this survey -- not from convenience.

Together, these four gaps define the problem that ParBench is designed to solve: kernel-level evaluation granularity, build-infrastructure isolation, training-data robustness through augmentation, and survey-grounded benchmark selection.

### 1.3 Contributions

This paper presents ParBench and makes the following contributions:

1. **ParBench framework** -- The first build/run/verify benchmark framework for LLM-based parallel code translation at the kernel level, supporting 184 specs across three benchmark suites (Rodinia, HeCBench, XSBench), three parallel APIs (CUDA, OpenMP, OpenCL), and twelve translation directions. Kernel-centric translation mode isolates the translation skill from build-system generation.

2. **AST-driven augmentation engine** -- Six semantics-preserving source-level transforms at five augmentation levels (L0--L4) that systematically test whether LLMs reason about parallel structure or pattern-match from training data. Level-invariant: 54/60 Rodinia specs PASS at all levels L1--L4 with zero correctness regressions. LLM evaluation at L0--L4 reveals a sharp model-capability tier: Claude Sonnet 4.6 shows no significant augmentation trend (Cochran-Armitage p=0.88), while Gemini 2.5 Flash-Lite degrades from 18.8% to 0.0% at L4, establishing augmentation robustness as a discriminator of genuine parallel reasoning.

3. **Empirical evaluation** -- Comparative analysis of three LLMs (Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, Llama 3.3 70B) across 562 translation tasks spanning twelve directions and five augmentation levels, revealing a two-tier model capability gap (chi2(2)=136.93, p < 0.001), a failure taxonomy showing BUILD\_FAIL dominance (32.03%) and rare VERIFY\_FAIL (9.79%) across all 562 evaluated tasks, per-kernel difficulty analysis, self-repair effectiveness measurement, and augmentation robustness characterization with statistical independence testing.

### 1.4 Key Findings Preview

ParBench produces several findings with immediate relevance for the HPC and LLM research communities:

**Kernel-centric isolation unlocks success.** Claude Sonnet 4.6 achieves 56.3% PASS on CUDA-to-OpenMP translation at L0 (9/16 Rodinia kernels), directly contrasting with 0% achieved by all models on repository-level approaches \cite{ParEvalRepo2025}. The gap quantifies the orthogonality of translation skill and build-system-generation skill.

**Two-tier capability gap; BUILD\_FAIL dominates failures.** A striking two-tier capability gap emerges: Claude Sonnet 4.6 achieves 54.26% PASS [47.1%, 61.2%] across all 562 tasks, while Gemini 2.5 Flash-Lite (8.56%) and Llama 3.3 70B (10.16%) are statistically indistinguishable (Fisher's p=1.0). BUILD\_FAIL accounts for 32.03% of all tasks, making it the dominant failure mode. VERIFY\_FAIL accounts for 9.79% (55/562), indicating that a meaningful but small minority of translations that compile and run produce incorrect output. The primary bottleneck remains API-specific syntax -- missing `#pragma omp` directives, retained CUDA memory management calls, wrong type annotations -- rather than an inability to reason about parallel computation.

**Augmentation robustness discriminates reasoning from pattern-matching.** Augmentation level has no statistically significant effect on overall pass rate (Cochran-Armitage z=-1.24, p=0.22). However, per-model analysis reveals divergent patterns: Claude Sonnet 4.6 shows no significant augmentation trend (chi2=0.66, p=1.0; Cochran-Armitage z=-0.15, p=0.88), maintaining relatively stable performance despite per-level variation. In contrast, Gemini 2.5 Flash-Lite degrades from 18.8% at L0 to 0.0% at L4 -- a complete degradation suggesting reliance on surface pattern-matching disrupted by augmentation. Groq Llama 3.3 70B shows a downward trend from 18.8% to 6.3% (Cochran-Armitage z=-0.95, p=0.34).

**Model capability gap is large-effect.** Claude Sonnet 4.6 (54.26%) dramatically outperforms both Gemini 2.5 Flash-Lite (8.56%) and Llama 3.3 70B (10.16%), with odds ratios exceeding 10x (Cohen's h > 1.0, large effect). The two non-frontier models are statistically indistinguishable (OR=0.83, p=1.0), establishing a clear two-tier structure rather than a smooth capability continuum.

**Direction asymmetry.** CUDA-to-OpenMP translation shows a higher aggregate pass rate than OpenMP-to-CUDA (31.3% vs. 18.8% at L0, McNemar p=0.18, not significant after correction). The trend holds for Claude (+18.8pp) and Gemini (+18.8pp) but not for Groq (0.0pp, symmetric performance). The sample size (n=48 paired comparisons) is insufficient for statistical significance. The direction suggests that removing CUDA-specific constructs is generally easier for LLMs than introducing them from OpenMP source, though model-specific factors may override this for some models.

---

## S2 Related Work

### 2.1 The Three-Granularity Landscape

The question "Can LLMs translate parallel code?" can be asked at three granularities, and the answer depends critically on which granularity is chosen. Table 1 positions ParBench relative to the most closely related prior benchmarks:

[TABLE 1: Related work comparison.]

| Paper | Venue | Granularity | Core Question | Build+Run+Verify | Augmentation | Scale | Key Finding |
|-------|-------|-------------|---------------|:-----------------:|:------------:|-------|-------------|
| HumanEval \cite{HumanEval2021} | arXiv'21 | Function | Can LLMs synthesize sequential code from docstrings? | -- | -- | 164 Python functions | GPT-4: ~67% pass@1 |
| SWE-bench \cite{SWEbench2024} | ICLR'24 | Repository | Can LLMs resolve real GitHub issues? | Yes (test suite) | -- | 2,294 issues, 12 repos | Claude 3.5: ~49% resolve rate |
| ParEval \cite{ParEval2024} | HPDC'24 | Task | Can LLMs *generate* parallel code from descriptions? | Yes (correctness check) | -- | 420 tasks, 6 parallel APIs | Partial capability; CUDA/OpenMP harder than MPI |
| ParEval-Repo \cite{ParEvalRepo2025} | ICPP'25 | Repository | Can LLMs *translate* entire HPC repositories? | Yes (build + functional) | -- | 6 apps (109--3,039 SLoC), 3 directions, 5 models | 0% pass@1 for apps >133 SLoC; build-system generation is binding constraint |
| **ParBench (ours)** | **SC26** | **Kernel** | **Can LLMs translate parallel computation patterns?** | **Yes (build+run+verify)** | **Yes (6 AST transforms, L0--L4)** | **184 specs, 3 suites, 12 directions, 3 models** | **54.26% PASS (Claude); two-tier capability gap; BUILD\_FAIL dominates** |

*Table 1: Related work comparison. ParBench is the only kernel-level framework with a build+run+verify harness and augmentation engine. ParEval-Repo (project shorthand: "Paraval") is the closest prior work; ParBench's kernel-centric design directly addresses its key failure mode (build-system generation). Venue: ICPP'25 = 54th Int'l Conference on Parallel Processing, San Diego, CA, Sep 2025 (DOI: 10.1145/3754598.3754669).*

ParEval \cite{ParEval2024} asks whether LLMs can *generate* parallel code from scratch (task-level granularity). ParEval-Repo \cite{ParEvalRepo2025} asks whether LLMs can translate *entire repositories* including Makefiles and project structure (repository-level granularity). ParBench asks whether LLMs can translate *parallel computation patterns* when provided with kernel files and existing infrastructure (kernel-level granularity). These are not competing benchmarks -- they measure orthogonal capabilities. The three together characterize where LLM capability for parallel code begins and ends: generation is partially possible, repository-level translation is not, and kernel-level translation is the productive middle ground. ParBench evaluates this capability across twelve directions, three parallel APIs (plus OMP-target variants), and five augmentation levels.

### 2.2 Code Synthesis and Translation Benchmarks

**HumanEval** \cite{HumanEval2021} evaluates synthesis of 164 Python functions from docstrings. The benchmark has been widely adopted but addresses only sequential, single-function synthesis with no parallelism. Pass rates on HumanEval are orthogonal to the capability measured by ParBench.

**SWE-bench** \cite{SWEbench2024} evaluates software engineering tasks (bug fixing, feature addition) on real GitHub repositories. It tests agentic software engineering capability, not parallel code translation.

**TransCoder** \cite{TransCoder2020} proposes unsupervised statistical translation between C++, Java, and Python using back-translation. The approach is statistical rather than LLM-based and addresses general-purpose sequential languages; HPC parallel APIs are outside its scope.

**CodeRosetta** \cite{CodeRosetta2024} evaluates unsupervised parallel code translation (CUDA to HIP) using encoder-decoder models. It focuses on a single translation direction and does not include a build/run/verify harness, augmentation methodology, or systematic benchmark curation.

### 2.3 Parallel Code Evaluation

**ParEval** \cite{ParEval2024} (Davis et al., HPDC'24) presents 420 parallel code *generation* tasks spanning OpenMP, MPI, CUDA, Kokkos, and HIP. Tasks are described in natural language and models must generate correct parallel implementations. ParEval does not evaluate translation between APIs, does not include a build/run/verify pipeline, and does not test augmentation robustness. Its contribution is establishing a baseline of LLM capability at parallel code synthesis -- a necessary precursor to translation evaluation.

**ParEval-Repo** \cite{ParEvalRepo2025} (Davis et al., ICPP'25, DOI: 10.1145/3754598.3754669) extends the evaluation to six full HPC applications (109--3,039 SLoC) in three translation directions (CUDA-to-OpenMP-Offload, CUDA-to-Kokkos, OpenMP-to-OpenMP-Offload). Five models are evaluated: GPT-4o, o3/o4-mini, Llama 3.3, QwQ-32B, and Gemini. The key finding -- no model achieves pass@1 > 0 on applications larger than 133 SLoC -- is an important contribution that identifies the repository-level failure mode and motivates ParBench's kernel-centric design directly. The root cause identified by ParEval-Repo is not a failure of parallel logic translation but a failure to generate correct build infrastructure (Makefiles, CMake, cross-file dependencies) alongside the translated code. ParBench operationalizes this insight by providing all build infrastructure (Makefiles, headers, support files) as fixed context, isolating the parallel logic translation skill from build-system generation.

Where ParEval-Repo evaluates six representative HPC applications, ParBench's benchmark corpus is drawn from a 35-repository survey that identified 472 CUDA--OpenMP kernel pairs -- systematic selection rather than convenience sampling. ParBench evaluates twelve translation directions across three core APIs (CUDA, OpenMP, OpenCL) plus OMP-target variants, compared to ParEval-Repo's three directions. Critically, in ParBench the LLM never sees the verification logic -- the harness (build/run/verify) is external to the prompt. The model receives only source code and a translation instruction; test suites and correctness checks are applied after translation, preventing test leakage.

The same kernel that achieves 0% in ParEval-Repo (XSBench) achieves 4/4 PASS in ParBench's harness baseline under kernel-centric evaluation, and Claude Sonnet 4.6 achieves non-zero pass rates across multiple XSBench translation directions in the LLM evaluation. Together, ParBench and ParEval-Repo provide a complementary picture: ParEval-Repo establishes that repository-level translation is beyond current LLM capability, while ParBench demonstrates that the parallel logic translation skill, when isolated from build-system generation, is substantially present.

### 2.4 Repository-Level Code Translation

**RepoTransBench** \cite{RepoTransBench2025} evaluates repository-level translation across general-purpose programming languages, finding systematic failures at scale consistent with ParEval-Repo.

**AlphaTrans** \cite{AlphaTrans2025} proposes compositional code translation with validation, decomposing repository-level translation into per-method tasks. This compositional philosophy is related to ParBench's kernel-centric design, though AlphaTrans targets sequential languages.

**LASSI** \cite{LASSI2024} (CLUSTER'24) evaluates an LLM self-correcting pipeline for parallel code translation with iterative compiler feedback. ParBench includes a self-repair loop as a component of its evaluation methodology; LASSI's contribution is the repair system itself, while ParBench's is the evaluation framework.

### 2.5 LLM-for-HPC

**HPCorpus** \cite{HPCorpus2023} is a large-scale dataset of HPC code from GitHub, enabling pre-training and fine-tuning of LLMs on parallel code. ParBench provides a measurement instrument for capabilities that HPCorpus training is intended to develop.

**OMPify** \cite{OMPify2023} evaluates LLM-based generation of OpenMP pragma annotations for sequential loops -- a restricted form of parallel code translation that does not require preserving thread decomposition structure.

### 2.6 ParaCodex

**ParaCodex** \cite{ParaCodex2026} (Kaplan et al.) is a companion system from our research team providing profiling-guided autonomous parallel code translation via an agentic framework. ParBench is the measurement instrument; ParaCodex is a system to be measured. The two are complementary: ParBench's specs and harness can serve as the evaluation backend for ParaCodex's agentic pipeline. Joint evaluation is deferred to future work (S8).

---

## S3 ParBench Framework

ParBench is a benchmark framework designed to evaluate LLM-based parallel code translation through automated, end-to-end correctness assessment. The framework comprises four integrated components: (1) a declarative spec schema that encodes what constitutes correct execution for each benchmark kernel, (2) a three-stage build/run/verify harness pipeline that evaluates translated code, (3) an AST-driven augmentation engine that generates semantically equivalent code variants to probe translation robustness, and (4) an evaluation pipeline that orchestrates LLM-based translation with iterative self-repair. This section describes each component in detail.

[FIGURE 1: System architecture diagram showing the four ParBench components: Spec JSON feeds into the Harness Pipeline (Build, Run, Verify stages), the Augmentation Engine transforms source code at levels L0--L4 before prompting, and the Evaluation Pipeline orchestrates LLM calls with self-repair feedback loops. Result JSON is the final output.]

### 3.A Spec Schema: Declarative Correctness Contracts

Each benchmark in ParBench is described by a JSON specification (spec) that serves as a declarative contract defining what "correct execution" means for that kernel--API variant. The spec encodes all information required to build, run, and verify a benchmark without manual intervention, enabling fully automated evaluation. The schema (version 1.0.0) is formally defined in JSON Schema draft-07 and enforced by an offline validator.

A spec is organized into the following field groups:

**Identity and provenance.** The `identity` block assigns a globally unique identifier following the convention `{source_suite}-{kernel_name}-{parallel_api}` (e.g., `rodinia-bfs-cuda`), and records the parallel API from a controlled vocabulary of 15 APIs including CUDA, OpenMP, OpenCL, HIP, SYCL, and serial. The `provenance` block pins the exact source repository and commit hash, ensuring reproducibility across environments.

**File partitioning.** The `files` block partitions benchmark source files into three disjoint sets: `prompt_payload` (files visible to the LLM during translation), `support_files` (build infrastructure such as Makefiles and shared headers; header content is provided as read-only reference in the translation prompt), and `verification_only` (reference implementations never exposed to the LLM). A fourth field, `translation_targets`, identifies the subset of `prompt_payload` that the LLM must produce -- the kernel computation files. This field is central to the kernel-centric translation methodology described in Section 3.D.

**Build, run, and verification.** The `build` block specifies the build system, compiler commands, environment variables, and expected executable path. The `run` block defines named input configurations (e.g., `correctness`, `performance`) with arguments, timeout, and optional environment variables. The `verification` block declares an ordered list of verification strategies -- currently `exit_code` (check process return code) and `stdout_pattern` (regex match against captured standard output) -- applied in sequence until a definitive PASS or FAIL is reached. Three additional strategies (`numeric_comparison`, `file_diff`, `custom_script`) are defined in the schema for future use.

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

This design separates the definition of correctness from the mechanism of verification: the harness can evolve independently of what "correct" means for each kernel. Across the current benchmark collection, 184 specs are defined: 60 from Rodinia \cite{Rodinia2009}, 4 from XSBench \cite{XSBench2014}, and 120 from HeCBench \cite{HeCBench2023}.

### 3.B Harness Pipeline: Build, Run, Verify

The harness pipeline is a three-stage evaluation engine invoked via a command-line interface. Each stage consumes the output of the previous stage, and failure at any stage short-circuits subsequent stages -- there is no reason to run code that did not compile, or to verify output from a crashed process.

**Build stage.** The builder resolves the spec's working directory, executes an optional clean command, runs any configure step, substitutes template variables (e.g., `${CUDA_DIR}`) in the build command, and invokes the build via a shell subprocess. After compilation, the builder verifies that the expected executable exists on disk. The build stage captures both stdout and stderr for diagnostic reporting and enforces a configurable timeout (default: 600 seconds).

**Run stage.** The runner executes the compiled binary with arguments drawn from the spec's named input configuration (typically `correctness`). Execution proceeds without a shell to avoid argument-parsing ambiguities. The runner captures stdout, stderr, exit code, and wall-clock duration, and enforces the spec-defined timeout (default: 300 seconds). An optional CPU-time measurement mode wraps execution with `/usr/bin/time -v` to capture user+system time independently of wall-clock duration.

**Verify stage.** The verifier applies the spec's verification strategies in declared order. For `exit_code` verification, the actual exit code is compared against the expected value. For `stdout_pattern` verification, a regular expression is applied to the captured stdout. The first strategy to produce a definitive PASS or FAIL terminates evaluation; if all strategies are exhausted without a conclusive result, the outcome is SKIP.

Each harness invocation produces one of four failure classifications -- BUILD\_FAIL, RUN\_FAIL, VERIFY\_FAIL, or TIMEOUT -- providing diagnostic granularity that enables systematic failure-mode analysis. The evaluation pipeline (Section 3.D) adds a fifth classification, EXTRACTION\_FAIL, when the LLM response does not contain parseable target files. A `--resume` flag allows batch evaluations to skip previously completed tasks, supporting append-only result accumulation without re-executing passing benchmarks.

### 3.C Augmentation Engine: Probing Robustness via Code Surface Variation

A central concern in evaluating LLM-based code translation is whether models genuinely reason about program structure or rely on memorized patterns from training data. Popular benchmarks such as those in the Rodinia suite \cite{Rodinia2009} are widely available in open-source repositories and likely present in LLM training corpora. To address this threat to validity, the augmentation engine generates semantically equivalent code variants by applying AST-level transformations that alter the syntactic surface of the source code while preserving its computational semantics.

The engine implements six transforms, each backed by the libclang API for AST analysis to guarantee syntactic validity:

1. **SwapCondition** -- reverses operands of comparison expressions (e.g., `a < b` becomes `b > a`), with guards against side-effect-bearing subexpressions and assignments.
2. **ArithmeticTransform** -- converts between compound and expanded assignment forms (e.g., `x += 1` becomes `x = x + 1` and vice versa).
3. **ChangeNames** -- consistently renames local variables and function parameters using symbol-aware reference collection, respecting scope boundaries and OpenMP pragma clauses.
4. **TypedefExpansion** -- replaces typedef aliases with their underlying primitive types at AST-identified type-reference sites.
5. **PointerArithmeticToArrayIndex** -- converts between pointer dereference and array indexing notation (e.g., `*(arr + i)` becomes `arr[i]`).
6. **ChangeFunctionNames** -- renames internal-linkage helper functions across their definitions and all call sites within the translation unit.

All transforms operate on the parsed AST rather than on raw text, which avoids the fragility of regex-based rewriting. Each candidate rewrite is validated by re-parsing the transformed code and confirming that no new diagnostic errors are introduced. Overlapping candidates are resolved by a greedy subset-selection algorithm that maximizes the number of applied transforms without introducing conflicts.

[TABLE 2: Augmentation Level Definitions.]

| Level | Transform selection | Candidate fraction | Description |
|:-----:|:-------------------:|:------------------:|:------------|
| L0 | None (original) | 0% | Unmodified source code (baseline) |
| L1 | 1 transform | 1 site per transform | Minimal surface perturbation |
| L2 | 33% of transforms | 33% of candidates | Moderate obfuscation |
| L3 | 66% of transforms | 66% of candidates | Heavy obfuscation |
| L4 | All transforms | 100% of candidates | Maximum obfuscation |

Five augmentation levels (L0--L4) control the density of applied transforms. L0 is the unmodified source. At L1, exactly one transform is selected and applied to a single candidate site. Levels L2--L4 apply both transform selection and candidate-site selection at increasing fractions: the fraction mapping applies to choose how many of the six transforms to run: 33% at L2, 66% at L3, and 100% at L4. Within each selected transform, the same fraction determines how many eligible AST nodes to rewrite, with a minimum of one applied via $\max(1, \lfloor n \cdot f \rfloor)$.

The augmentation baseline confirms that the transforms are semantics-preserving: 54 of 60 Rodinia specs pass the build/run/verify pipeline at all levels L1--L4, with zero correctness regressions relative to L0. The 6 specs that fail at L0 (due to CUDA 12 deprecations, missing system libraries, and pre-existing runtime errors) also fail identically at all augmented levels, confirming that augmentation introduces no new failures. Transform application frequency across 240 augmented tasks: SwapCondition (162), ArithmeticTransform (69), ChangeNames (55), TypedefExpansion (7), PointerArithmeticToArrayIndex (6), ChangeFunctionNames (2).

### 3.D Evaluation Pipeline: Kernel-Centric Translation

The evaluation pipeline orchestrates LLM-based parallel code translation through a structured prompt-response-verify cycle. Its design reflects a deliberate methodological choice: kernel-centric translation, in which only the parallel computation files are translated while the surrounding build infrastructure remains untouched.

**Kernel-centric methodology.** Prior work on repository-level code translation \cite{ParEvalRepo2025} demonstrated that LLM pass rates collapse to 0% for programs exceeding approximately 133 source lines of code (SLoC), largely due to the difficulty of simultaneously generating correct build-system artifacts alongside translated source code. ParBench isolates the translation skill by feeding only the `translation_targets` files (the parallel kernel code) to the LLM; Makefiles, shared headers, serial baselines, and utility code remain unchanged in the target directory. This design enables evaluation of whether an LLM can correctly map parallel programming patterns from one API to another, independent of its ability to replicate project file organization.

**Prompt structure.** Each translation prompt consists of a system message establishing the role of a parallel programming expert and a user message containing: (1) the source kernel code with API-specific syntax highlighting, (2) the target API and the filenames the LLM must produce, (3) the target build command for compilation compatibility, and (4) read-only target infrastructure context (non-kernel files from the target directory) so the LLM can match expected function signatures and data structures. Source support headers are included with instructions to inline definitions rather than emit unresolvable `#include` directives.

**Self-repair loop.** On failure, the pipeline feeds failure-specific diagnostics back to the LLM: compiler errors on build failure, runtime errors and stderr on execution failure, and verification details on output mismatch. This feedback serves as a follow-up prompt, requesting a corrected translation. This iterative self-repair mechanism allows a configurable number of attempts before a final failure classification. The self-repair loop mirrors the realistic workflow of a developer iterating on errors; it also provides data on which failure modes are recoverable by the model versus those that indicate fundamental translation deficiencies.

**Complexity taxonomy.** To enable stratified analysis of translation difficulty, each source--target pair is classified into one of four complexity classes based on the file cardinality of the translation: `single_file` (1 source file to 1 target file), `multi_to_single` (N source files to 1 target file), `single_to_multi` (1 source file to N targets, characteristic of CUDA-to-OpenCL translations where the host-device split is inherent to the programming model), and `multi_to_multi` (N source files to M target files).

**Model-agnostic design.** The pipeline supports multiple LLM providers through a model registry that maps human-readable identifiers to provider-specific API configurations. All evaluations use temperature 0 for deterministic reproducibility. The framework currently supports Anthropic, OpenAI, Azure OpenAI, Google, and Groq API endpoints (three used in this evaluation), enabling cross-model comparison under identical prompt content and evaluation conditions.

---

## S4 Benchmark Curation

The benchmark corpus was assembled through a systematic selection process: surveying available HPC benchmark repositories, analyzing kernel-level translation opportunities, and filtering to a representative subset verified through the full build/run/verify pipeline.

### 4.A Suite Selection

A survey of 35 open-source HPC benchmark repositories was conducted, spanning suites, mini-applications, proxy applications, full applications, libraries, and microbenchmarks. The survey covered GPU computing across multiple parallel APIs.

A central finding of the survey is that repository-level counting dramatically overstates the available benchmark material. Naive analysis identifies 21 repositories containing both CUDA and OpenMP implementations, but kernel-level analysis reveals 472 independent CUDA--OpenMP translation pairs across those same repositories. The discrepancy ranges from 20x to 60x, driven primarily by large suites such as HeCBench \cite{HeCBench2023} (325 kernels with CUDA and OpenMP implementations) and other multi-API benchmark collections. This motivates a kernel-centric evaluation strategy: benchmarks should be evaluated at the granularity of individual computational kernels, not entire repositories.

[TABLE 3: Survey -- Kernel-Level Translation Pair Counts.]

| API Pair | Repos with Both APIs | Kernel Pairs Available |
|----------|:--------------------:|:---------------------:|
| CUDA -- OpenMP | 21 | 472 |
| CUDA -- HIP | 10 | 633 |
| CUDA -- SYCL | 9 | 616 |
| CUDA -- OpenCL | 7 | ~200 |

Five criteria guided suite selection:
1. Multiple parallel API variants of the *same* kernel in the same source tree
2. Build, run, and verify automatable without human intervention
3. Self-checking output patterns (deterministic checksums, tolerance-bounded comparison, or labeled correctness output)
4. Publicly available under an open-source license
5. Representative domain coverage

[FIGURE 2: API Co-occurrence Heatmap illustrating which parallel APIs appear together in the same repositories.]

### 4.B Kernel Selection

**Rodinia** \cite{Rodinia2009} provides ParBench's primary evaluation substrate. With thousands of citations, Rodinia is among the most-studied GPU benchmark suites in HPC literature, and critically provides CUDA, OpenMP, and OpenCL implementations of most kernels in the same source tree -- making it ideal for translation benchmarking where the reference implementation for each API is authoritative.

ParBench includes 60 Rodinia specs covering 22 kernels across three APIs (22 CUDA, 18 OpenMP, 20 OpenCL; coverage is non-uniform because not all kernels have all three API variants). After systematic verification on the evaluation platform, 54/60 achieve PASS and 6 are KNOWN\_FAIL for platform-specific reasons:

- 2 specs fail because CUDA 12 removed the deprecated `texture<>` reference API (kmeans-cuda, mummergpu-cuda);
- 1 spec fails due to a missing OpenGL dependency (hybridsort-cuda);
- 1 spec inherits CUDA texture dependencies in its OpenMP variant (mummergpu-omp);
- 2 OpenCL specs exhibit pre-existing runtime crashes (nn-opencl, kmeans-opencl).

These failures are documented but excluded from the evaluation corpus; they reflect toolchain evolution, not benchmark design defects.

**XSBench** \cite{XSBench2014} is a Monte Carlo neutron transport proxy application included specifically to enable direct comparison with ParEval-Repo, which evaluates XSBench and achieves 0% pass@1 for all models. ParBench achieves 4/4 PASS on XSBench (CUDA, OMP, OpenCL, OMP-target) using the kernel-centric approach -- same kernel, different evaluation granularity. An additional 60 HeCBench kernels (120 specs) are included in the framework schema for future expansion but were not deployed on the evaluation machine for this study.

The selected kernels span 11 computational domains: graph traversal (bfs), physics simulation (hotspot, hotspot3d, cfd, srad), machine learning (backprop, kmeans, nn), linear algebra (lud, nw, gaussian), molecular dynamics (lavamd, mummergpu), image processing (dwt2d), dynamic programming (pathfinder), biophysical simulation (myocyte, heartwall), particle methods (particlefilter, streamcluster), sorting (bptree, hybridsort), and compression (huffman).

[TABLE 4: Kernel x API verification matrix for Rodinia (22 kernels) and XSBench (1 kernel), showing PASS/KNOWN\_FAIL/not-available status for each API (CUDA, OpenMP, OpenCL).]

### 4.C API Coverage

CUDA serves as the primary source language, reflecting its dominant position in GPU programming. OpenMP is the primary translation target, selected because the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity (472 kernel pairs across 21 repositories). OpenCL provides a secondary target that exercises a qualitatively different programming model: explicit memory management, separate kernel compilation, and host-device code separation. Together, these three APIs cover the principal parallel programming paradigms in HPC: GPU-native (CUDA), directive-based (OpenMP), and portable heterogeneous (OpenCL).

### 4.D Representative Subset

The 57 verified-PASS specs (54 Rodinia + 3 XSBench standard APIs) constitute the evaluation corpus. The XSBench OpenMP target offload variant is excluded from standard evaluation batches because it requires the NVIDIA HPC compiler (`nvc`) and is treated as a case study. The selection is principled rather than exhaustive: the spec schema permits straightforward extension to additional suites, kernels, and APIs without modification to the evaluation harness. Each kernel in the corpus was independently verified through the complete build/run/verify pipeline prior to inclusion in any LLM evaluation experiment.

---

## S5 Experimental Setup

This section describes the models, translation directions, augmentation protocol, evaluation metrics, and hardware configuration used in the evaluation.

### 5.A Models

Three large language models are evaluated, selected to span a major commercial API provider, a cost-efficient proprietary alternative, and an open-weight model: Claude Sonnet 4.6 (Anthropic), Gemini 2.5 Flash-Lite (Google), and Llama 3.3 70B (Meta, accessed via Groq). All models are queried at temperature 0 to ensure deterministic outputs and reproducibility across runs. Reasoning and chain-of-thought modes are explicitly disabled for all models. This is a deliberate design choice: the evaluation targets raw translation competence -- whether a model's internalized knowledge of parallel programming patterns suffices to produce correct translations -- rather than the capacity of a multi-step reasoning scaffold to search for solutions.

[TABLE 5: Model configurations. Columns: human-readable name, API model identifier, provider, access method, and parameter count (where publicly disclosed).]

### 5.B Translation Directions

Twelve translation directions are evaluated across four parallel APIs. Six core directions span the three primary APIs:

- CUDA to OpenMP and OpenMP to CUDA
- CUDA to OpenCL and OpenCL to CUDA
- OpenMP to OpenCL and OpenCL to OpenMP

Six additional directions involve OpenMP target offload (OMP-target) variants, evaluated on XSBench where the OMP-target implementation is available: CUDA to OMP-target, OMP-target to CUDA, OMP to OMP-target, OMP-target to OMP, OMP-target to OpenCL, and OpenCL to OMP-target.

CUDA to OpenMP serves as the primary evaluation direction, as it represents the most common real-world HPC translation need: migrating GPU-accelerated CUDA code to the portable, CPU-parallel OpenMP model. The remaining directions provide cross-directional comparison and test whether translation difficulty is symmetric across API pairs. Not all directions apply to every kernel, as some benchmarks lack implementations in all APIs; the evaluation covers all valid source--target pairs within the benchmark suite.

### 5.C Augmentation Protocol

Source code augmentation is applied at five levels. Level L0 uses the unmodified benchmark source and serves as the baseline. Levels L1 through L4 apply the six AST-driven transforms (described in Section 3.C) at increasing density: L1 applies one randomly selected transform at a single candidate site; L2 selects 33% of transforms and applies each to 33% of eligible candidate sites; L3 selects 66% of transforms at 66% of sites; and L4 applies all transforms at all sites. A fixed random seed of 42 governs all stochastic choices for reproducibility.

The augmentation protocol tests a specific hypothesis: if an LLM genuinely reasons about parallel computation structure rather than pattern-matching against memorized training examples, its translation success rate should remain stable across augmentation levels. The augmentation baseline was verified prior to LLM evaluation (Section 3.C): zero new failures were introduced at any level, confirming that any variation in LLM pass rates across levels can be attributed to the model rather than to the augmentation process.

### 5.D Metrics

The primary evaluation metric is **pass@1**: the fraction of translation tasks that pass the full build, run, and verify pipeline on a single evaluation (with a configurable number of self-repair attempts via error feedback; two in this study). Each failure is classified into a diagnostic category -- BUILD\_FAIL (compilation error), RUN\_FAIL (runtime crash or nonzero exit code), VERIFY\_FAIL (incorrect output), or EXTRACTION\_FAIL (malformed LLM response) -- enabling fine-grained failure-mode analysis beyond a single pass/fail number.

Secondary metrics include **augmentation robustness**, defined as the stability of pass@1 across augmentation levels L0 through L4, and **self-repair rate**, the fraction of initially failing tasks recovered by the error-feedback retry loop.

Execution timing and speedup metrics are excluded from this study. The current verification pipeline measures wall-clock time, which conflates kernel execution with I/O, memory allocation, and OS scheduling noise. Reliable performance comparison requires profiler-based kernel timing (e.g., Nsight Compute for CUDA, `omp_get_wtime()` for OpenMP), which is deferred to future work.

### 5.E Hardware and Software

All evaluations are conducted on a single workstation to eliminate cross-machine variability. The GPU is an NVIDIA GeForce RTX 4070 (Ada Lovelace architecture, compute capability 8.9, 5888 CUDA cores, 12 GB GDDR6X). The CPU is an AMD Ryzen 9 7900X (12 cores, 24 threads). The system runs Ubuntu 24.04 LTS (kernel 6.8.0-40-generic).

CUDA compilation uses `nvcc` from the NVIDIA HPC SDK 24.3 (CUDA 12.3). C/C++ compilation uses GCC 12.4 with the `-fopenmp` flag for OpenMP targets. OpenCL programs link against the NVIDIA runtime from the HPC SDK. The evaluation harness and all scripting infrastructure run on Python 3.12.3. LLM API calls are issued from the same machine; network latency does not affect correctness evaluation.

[TABLE 6: Hardware and software configuration. Rows: GPU model, CPU model, operating system, CUDA toolkit version, C/C++ compiler, OpenCL runtime, Python version.]

---

## S6 Results

This section presents ParBench evaluation results across 562 evaluated tasks: three LLMs on CUDA-to-OpenMP translation of Rodinia kernels, augmentation robustness across five levels (L0--L4), self-repair effectiveness, Rodinia cross-direction evaluation (OpenMP-to-CUDA), and extended suite results on XSBench across twelve translation directions. All evaluations use temperature=0, up to two self-repair retry attempts (three total attempts per task), and the build/run/verify pipeline described in S3.B.

### 6.1 Overall Pass Rates -- CUDA-to-OpenMP, L0

Table 7 summarizes pass rates for the three evaluated models on Rodinia CUDA-to-OpenMP translation tasks at L0 (unmodified source).

[TABLE 7: Model pass rates on CUDA-to-OpenMP translation (L0, 16 Rodinia kernels, 3 models). Two KNOWN\_FAIL source specs (kmeans-cuda, mummergpu-cuda) are excluded.]

| Model | PASS | Total | Rate | BUILD\_FAIL | RUN\_FAIL | EXTRACTION\_FAIL | VERIFY\_FAIL |
|-------|-----:|------:|-----:|----------:|--------:|---------------:|------------:|
| claude-sonnet-4-6 | 9 | 16 | 56.3% | 2 | 1 | 0 | 4 |
| gemini-2.5-flash-lite | 3 | 16 | 18.8% | 8 | 2 | 1 | 2 |
| groq-llama-3.3-70b-versatile | 3 | 16 | 18.8% | 8 | 2 | 1 | 2 |
| **Total** | **15** | **48** | **31.3%** | **18** | **5** | **2** | **8** |

The aggregate pass rate across all three models is 15/48 (31.3%). Claude Sonnet 4.6 achieves the highest individual pass rate at 9/16 (56.3%), while Gemini 2.5 Flash-Lite and Llama 3.3 70B achieve identical rates of 3/16 (18.8%). The 37.5-percentage-point spread between Claude and the two non-frontier models reflects the two-tier capability gap that characterizes the full 562-task evaluation: Claude operates in a qualitatively different performance tier than Gemini and Groq, which are statistically indistinguishable from each other (Fisher's p=1.0, OR=0.83).

These results contrast sharply with repository-level evaluation. ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 for all models on applications larger than 133 SLoC, including XSBench. ParBench's kernel-centric approach -- isolating the translation task from build-system generation -- achieves 56.3% for the strongest model on the same class of HPC kernels. The gap quantifies the degree to which build-system generation, rather than parallel logic translation, is the binding constraint in repository-level approaches.

### 6.2 Failure Taxonomy

Of the 33 total failures across three models at L0, the distribution is:

- BUILD\_FAIL: 18/33 (54.5%)
- VERIFY\_FAIL: 8/33 (24.2%)
- RUN\_FAIL: 5/33 (15.2%)
- EXTRACTION\_FAIL: 2/33 (6.1%)

[FIGURE 3: Failure taxonomy stacked bar chart. X-axis: models (Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, Llama 3.3 70B). Y-axis: task count stacked by outcome (PASS, BUILD\_FAIL, RUN\_FAIL, VERIFY\_FAIL, EXTRACTION\_FAIL). Data source: results/evaluation/eval\_summary.json.]

BUILD\_FAIL dominance (54.5% of L0 failures) indicates that the primary bottleneck is API-specific syntax rather than parallel reasoning. Examination of build error logs reveals recurring patterns: retained CUDA memory management calls (`cudaMalloc`, `cudaFree`, `cudaMemcpy`) in otherwise-OpenMP code, missing `#pragma omp parallel for` directives, incorrect function signatures for OpenMP runtime calls, and failure to eliminate device-specific type annotations. These are syntactic failures -- the model demonstrates understanding of the parallel computation structure but fails to fully translate the API surface.

VERIFY\_FAIL (24.2% of L0 failures; 8/48 = 16.7% of all L0 tasks) indicates translations that compile and execute but produce incorrect output. This finding emerged after the S-VERIFY verification upgrade, which strengthened the harness from disjunctive (exit\_code OR stdout\_pattern) to conjunctive (exit\_code AND stdout\_pattern) verification. Several translations that previously appeared correct under exit-code-only checking were revealed to produce numerically wrong results. At the kernel level, Claude exhibits 4 VERIFY\_FAIL (bfs, nw, pathfinder, streamcluster), while both Gemini and Groq exhibit 2 each. The presence of VERIFY\_FAIL is scientifically informative: it identifies cases where LLMs produce code that is syntactically valid and structurally plausible but introduces subtle parallel logic errors -- incorrect thread-index mappings, wrong reduction scoping, or missed data dependencies.

Across all 562 evaluated tasks, the failure distribution is: BUILD\_FAIL 180/425 (42.4%), RUN\_FAIL 123/425 (28.9%), EXTRACTION\_FAIL 67/425 (15.8%), VERIFY\_FAIL 55/425 (12.9%). BUILD\_FAIL remains the dominant failure mode across all directions and augmentation levels.

RUN\_FAIL (14.3% of L0 failures) represents code that compiles but crashes or times out at runtime. These failures suggest that the translation preserves surface syntax correctly but introduces runtime errors in memory access patterns or argument handling.

EXTRACTION\_FAIL (5.7%) occurs exclusively in the two weaker models (Groq and Gemini, one instance each at L0), indicating occasional failure to produce well-formed source file output.

### 6.3 Per-Kernel Analysis

Table 8 presents the full kernel-by-model result matrix for all three models, revealing systematic structure in translation difficulty.

[TABLE 8: Per-kernel results for CUDA-to-OpenMP translation (L0, 16 Rodinia kernels, 3 models). KNOWN\_FAIL source specs (kmeans-cuda, mummergpu-cuda) excluded.]

| Kernel | Category | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b |
|--------|----------|---|---|---|
| backprop | ml | PASS | PASS | BUILD\_FAIL |
| bfs | graph | VERIFY\_FAIL | BUILD\_FAIL | VERIFY\_FAIL |
| bptree | other | PASS | PASS | PASS |
| cfd | physics | PASS | BUILD\_FAIL | BUILD\_FAIL |
| heartwall | image | BUILD\_FAIL | BUILD\_FAIL | BUILD\_FAIL |
| hotspot | stencil | RUN\_FAIL | RUN\_FAIL | RUN\_FAIL |
| hotspot3d | stencil | PASS | PASS | PASS |
| lavamd | molecular\_dynamics | PASS | VERIFY\_FAIL | BUILD\_FAIL |
| lud | linear\_algebra | PASS | BUILD\_FAIL | BUILD\_FAIL |
| myocyte | other | BUILD\_FAIL | BUILD\_FAIL | BUILD\_FAIL |
| nn | ml | PASS | VERIFY\_FAIL | RUN\_FAIL |
| nw | linear\_algebra | VERIFY\_FAIL | EXTRACTION\_FAIL | BUILD\_FAIL |
| particlefilter | other | PASS | BUILD\_FAIL | PASS |
| pathfinder | other | VERIFY\_FAIL | BUILD\_FAIL | VERIFY\_FAIL |
| srad | stencil | PASS | RUN\_FAIL | EXTRACTION\_FAIL |
| streamcluster | other | VERIFY\_FAIL | BUILD\_FAIL | BUILD\_FAIL |

[FIGURE 4: Kernel-by-model heatmap. Rows: 16 kernels sorted by difficulty. Columns: 3 models. Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), yellow (VERIFY\_FAIL), grey (EXTRACTION\_FAIL).]

The per-kernel analysis above addresses the primary CUDA-to-OpenMP direction with three models. Section 6.6 presents the cross-direction comparison (Table 11), where 16 of these kernels are evaluated in both CUDA-to-OpenMP and OpenMP-to-CUDA directions, revealing per-kernel direction asymmetry.

Kernels partition into distinct difficulty tiers based on three-model consensus. The post-S-VERIFY data (conjunctive stdout\_pattern+exit\_code verification) produces a sharper tier separation than exit-code-only verification, with VERIFY\_FAIL now distinguishing translations that produce wrong output from those that fail to build or run.

**Always-pass (2 kernels: bptree, hotspot3d).** All three models achieve PASS. These kernels share characteristics that favor translation: straightforward thread-index-to-loop-index mapping, minimal shared memory usage, and well-known algorithmic structures (B+ tree construction, 3D stencil computation). They represent the tier where all evaluated models possess sufficient parallel API knowledge.

**Always-fail (7 kernels: bfs, heartwall, hotspot, myocyte, nw, pathfinder, streamcluster).** No model achieves PASS. The failure modes are informative:

- *myocyte* is the most complex spec in the evaluation: 16 CUDA source files must be translated to 10 OpenMP target files (`multi_to_multi` complexity class). All three models produce BUILD\_FAIL. The sheer volume of coordinated translation required exceeds current LLM capability in a single prompt.
- *hotspot* compiles for all three models but crashes at runtime (RUN\_FAIL for all). The interleaved read-write stencil pattern on shared memory requires careful translation of CUDA shared memory to stack-allocated arrays with appropriate synchronization.
- *heartwall* produces BUILD\_FAIL for all three models, indicating a consistent gap in handling its complex image processing kernel structure.
- *bfs, nw, pathfinder, streamcluster* are notable always-fail kernels because they include VERIFY\_FAIL instances (Claude: bfs, nw, pathfinder, streamcluster; Groq: bfs, pathfinder). These translations compile, run, and produce output -- but the output is incorrect. This distinguishes them from pure build failures: the LLMs demonstrate sufficient API knowledge to produce runnable code, but introduce subtle parallel logic errors in thread-index mappings or reduction scoping.

**Claude+Gemini only (1 kernel: backprop).** Claude and Gemini pass; Groq fails with BUILD\_FAIL. This pattern is notable: Gemini (the weakest overall model at 8.56%) passes backprop while Groq (10.16% overall) fails. The result is consistent with domain-specific variation in model strengths -- backprop's reduction-heavy machine learning kernel involves CUDA reduction idioms (`__syncthreads()`, shared memory accumulation) that may be disproportionately represented in Gemini's training data despite its weaker overall coverage. This illustrates that per-kernel difficulty is not fully predicted by aggregate pass rate.

**Claude+Groq only (1 kernel: particlefilter).** Claude and Groq pass; Gemini fails with BUILD\_FAIL. The likelihood computation in particlefilter involves complex reduction patterns that Groq handles but Gemini cannot.

**Claude-only (5 kernels: cfd, lavamd, lud, nn, srad).** Only Claude Sonnet 4.6 passes. This is the largest tier, accounting for 5 of 16 kernels (31.3%), and sharply delineates the two-tier capability gap. These kernels span diverse computational domains -- Euler fluid dynamics (cfd), molecular dynamics (lavamd), matrix decomposition (lud), nearest-neighbor search (nn), and 2D stencil diffusion (srad). The diversity of domains within the Claude-only tier indicates that the capability gap is not domain-specific but reflects a general advantage in parallel API syntax coverage. Notably, nn and lavamd produce VERIFY\_FAIL for Gemini (compilable but incorrect output), suggesting Gemini has partial but insufficient understanding of these kernels' parallel structure.

### 6.4 Self-Repair Effectiveness

ParBench's evaluation pipeline permits up to two retry attempts with failure-specific diagnostics injected into subsequent prompts (three total attempts per task). Table 9 summarizes self-repair effectiveness.

[TABLE 9: Self-repair effectiveness across L0 CUDA-to-OpenMP translation tasks (3 models, 48 tasks, 16 Rodinia kernels).]

| Metric | Value |
|--------|------:|
| Total tasks | 48 |
| Passed on first attempt | 10 (20.8%) |
| Repaired by retry (attempts 2 or 3) | 5 (10.4%) |
| Total PASS after retries | 15 (31.3%) |
| Relative improvement from retry | 50.0% |
| Remained failed after all attempts | 33 (68.8%) |

At L0, self-repair adds 5 additional PASS results beyond first-attempt success, a 50.0% relative improvement (5 repairs from 10 first-attempt passes). First-attempt passes account for 66.7% of all passes (10/15), indicating that translation capability is primarily determined by the model's initial response quality, though the repair mechanism provides meaningful additional value.

Across all 562 evaluated tasks (all models, all augmentation levels, all twelve translation directions), the pattern is consistent: 107 first-attempt passes (19.0% of tasks) and 30 repairs, yielding 137 total passes (24.4% overall) and a 28.0% relative improvement (30/107). The repair mechanism is effective for syntax-level BUILD errors -- missing headers, undeclared variables, incorrect type annotations -- where the compiler error message provides actionable feedback. However, self-repair is ineffective for systematic API translation failures. Kernels like myocyte (BUILD\_FAIL for all models across all attempts) exhibit translation failures too fundamental for incremental compiler-feedback-driven correction. Self-repair is also ineffective for VERIFY\_FAIL: translations that produce wrong output receive only a generic "output mismatch" signal, which lacks the specificity of compiler error messages needed to guide correction.

### 6.5 Augmentation Robustness -- LLM Evaluation

The augmentation engine's six AST-driven transforms were first validated on the full 60-spec Rodinia suite at augmentation levels L1 through L4 (seed=42, 240 total tasks), confirming level-invariant semantics preservation: 54/60 PASS at every level with zero correctness regressions (Section 3.C). This harness baseline establishes that any variation in LLM pass rates across augmentation levels can be attributed to the model's sensitivity to surface syntax, not to augmentation-induced semantic changes.

Table 10 presents the LLM augmentation robustness results for three models evaluated across all five levels on CUDA-to-OpenMP translation of 16 Rodinia kernels.

[TABLE 10: LLM pass rates across augmentation levels (CUDA-to-OpenMP, 16 Rodinia kernels, 3 models). Statistical tests (chi-squared, Cochran-Armitage) include XSBench (17 kernels total); XSBench is FAIL at all levels for all models.]

| Level | Claude Sonnet 4.6 | Gemini 2.5 Flash-Lite | Groq Llama 3.3 70B |
|:-----:|:-----------------:|:---------------------:|:-------------------:|
| L0 | 9/16 (56.3%) | 3/16 (18.8%) | 3/16 (18.8%) |
| L1 | 8/16 (50.0%) | 3/16 (18.8%) | 2/16 (12.5%) |
| L2 | 8/16 (50.0%) | 3/16 (18.8%) | 2/16 (12.5%) |
| L3 | 7/16 (43.8%) | 2/16 (12.5%) | 2/16 (12.5%) |
| L4 | 9/16 (56.3%) | 0/16 (0.0%) | 1/16 (6.3%) |

[FIGURE 5: Augmentation robustness line chart. X-axis: augmentation levels L0--L4. Y-axis: pass rate (%). Lines: Claude Sonnet 4.6 (stable around 44--56%, no significant trend), Gemini 2.5 Flash-Lite (degrading from 18.8% to 0.0%), Groq Llama 3.3 70B (degrading from 18.8% to 6.3%).]

This result reveals a model-capability tier that directly tests the memorization hypothesis:

**Claude Sonnet 4.6: statistically stable.** Claude's pass rate varies between 43.8% (L3) and 56.3% (L0, L4) across augmentation levels, but neither the chi-squared test (chi2=0.66, p=1.0 Bonferroni-corrected) nor the Cochran-Armitage trend test (z=-0.15, p=0.88) detects a significant effect. The per-level variation reflects individual kernels flipping between PASS and VERIFY\_FAIL across augmentation variants -- a consequence of the stricter conjunctive verification -- rather than a systematic degradation pattern. The augmented code variants at L4 -- with all variable names changed, all conditions reversed, all arithmetic forms rewritten -- do not exist in any training corpus, yet Claude's aggregate performance is statistically indistinguishable from the unmodified source baseline.

**Gemini 2.5 Flash-Lite: complete degradation.** Gemini's pass rate declines from 3/16 (18.8%) at L0--L2 to 2/16 (12.5%) at L3 and 0/16 (0.0%) at L4 -- a complete collapse. This monotonic degradation as augmentation density increases is consistent with a model that relies on surface pattern-matching from training data: as the code surface diverges further from published Rodinia source, Gemini's translation accuracy decays to zero. Examination of L4 failure modes reveals cases where Gemini generates C++ syntax (e.g., `std::` namespace qualifiers) for targets that require plain C -- suggesting that the heavily transformed variable names and function identifiers confuse the model's language identification at the surface level.

**Groq Llama 3.3 70B: monotonic degradation.** Llama's pass counts follow a decreasing trajectory: 3, 2, 2, 2, 1 across L0--L4 (out of 16 Rodinia kernels per level). The Cochran-Armitage trend test (z=-0.95, p=0.34) does not reach significance, but the direction is consistently downward. At L4, only one kernel (bptree) survives augmentation. Like Gemini, this pattern is consistent with sensitivity to surface code modifications, though the degradation is less dramatic.

The augmentation robustness results stratify model capability in a way that L0 results alone cannot. At L0, all three models show similar non-frontier rates (Gemini and Groq both at 18.8%), but by L4, Gemini collapses to 0.0% while Groq retains 6.3%. Meanwhile, Claude's rate at L4 (56.3%) exceeds its L3 rate (43.8%), demonstrating that augmentation level does not meaningfully constrain its translation capability. Augmentation robustness is thus a more discriminating evaluation than pass@1 at a single level: it separates models that have internalized parallel computation structure from those that rely on surface cues.

### 6.6 Cross-Direction and Extended Suite Results

**Rodinia cross-direction evaluation: OpenMP-to-CUDA.** To test whether translation difficulty is direction-dependent, 16 Rodinia kernels were evaluated in the reverse direction (OpenMP-to-CUDA) using three models at L0, yielding 48 tasks. (The 17th kernel, kmeans, is excluded because it lacks a valid OpenMP source spec for use as OMP-to-CUDA input.) Table 11 presents the cross-direction comparison.

[TABLE 11: Direction comparison -- CUDA-to-OpenMP vs. OpenMP-to-CUDA (L0, 16 Rodinia kernels, 3 models).]

| Model | CUDA-to-OpenMP | OpenMP-to-CUDA | Gap |
|-------|:----------:|:----------:|:---:|
| claude-sonnet-4-6 | 9/16 (56.3%) | 6/16 (37.5%) | +18.8pp |
| gemini-2.5-flash-lite | 3/16 (18.8%) | 0/16 (0.0%) | +18.8pp |
| groq-llama-3.3-70b-versatile | 3/16 (18.8%) | 3/16 (18.8%) | +0.0pp |
| **Aggregate** | **15/48 (31.3%)** | **9/48 (18.8%)** | **+12.5pp** |

CUDA-to-OpenMP translation is 12.5 percentage points easier than OpenMP-to-CUDA in aggregate (31.3% vs. 18.8%). The asymmetry is most pronounced for Claude (+18.8pp) and Gemini (+18.8pp), while Groq shows no direction asymmetry (identical 18.8% in both directions). This asymmetry is consistent with the nature of the translation task: CUDA-to-OpenMP requires *removing* CUDA-specific constructs (`cudaMalloc`, kernel launch syntax, `threadIdx`/`blockIdx` indexing) and replacing them with OpenMP directives, while OpenMP-to-CUDA requires *introducing* all of these constructs from OpenMP source that contains no explicit thread-block decomposition, device memory management, or kernel launch configuration.

Per-kernel direction asymmetry reveals structured patterns across the 48 kernel-model cells: 5 cells (10.4%) pass in both directions (BOTH\_PASS), 10 cells (20.8%) pass CUDA-to-OpenMP only (C2O\_ONLY), 4 cells (8.3%) pass OpenMP-to-CUDA only (O2C\_ONLY), and 29 cells (60.4%) fail in both directions (BOTH\_FAIL). The 10:4 ratio of direction-exclusive passes favors CUDA-to-OpenMP, though the asymmetry is less extreme than a pure "removal is easier than generation" model would predict. The O2C\_ONLY exceptions include cases where a model succeeds at introducing CUDA constructs but fails at removing them, possibly due to kernel-specific patterns in training data. Notably, Groq's symmetric 18.8% rate in both directions suggests that its translation strategy is less direction-sensitive than Claude's or Gemini's.

**XSBench cross-direction evaluation.** XSBench was evaluated across all 12 API directions (CUDA to OpenMP, OpenMP to CUDA, CUDA to OpenCL, OpenCL to CUDA, OpenMP to OpenCL, OpenCL to OpenMP, and their reverse OMP-target variants) for three models at five augmentation levels, yielding 180 evaluated tasks. Selected directional aggregate results across all augmentation levels (3 models × 5 levels = 15 tasks per direction):

- CUDA to OpenCL: 5/15 PASS (33.3%) [L0 only: 1/3, driven by Claude PASS]
- OpenMP to CUDA: 6/15 PASS (40.0%) [L0 only: 2/3, Claude+Groq PASS]
- OpenCL to OpenMP: 0/15 PASS (0%) -- the most difficult direction [L0 only: 0/3]

Claude achieves non-zero pass rates in 10 of 12 evaluated directions, demonstrating broader cross-directional capability than Gemini or Groq. The 0% pass rate for OpenCL-to-OpenMP across all models highlights an asymmetry in translation difficulty: OpenCL's explicit device management and separate kernel compilation model present a qualitatively different challenge when mapping to OpenMP's directive-based paradigm.

A key finding is that ParBench's kernel-centric approach achieves non-zero pass rates across multiple translation directions on XSBench -- the same benchmark for which ParEval-Repo \cite{ParEvalRepo2025} reports 0% at the repository level. This confirms that the kernel-centric advantage generalizes beyond the primary CUDA-to-OpenMP direction.

**HeCBench.** 120 specs (60 CUDA, 60 OpenMP) are curated and schema-validated; evaluation is pending deployment of HeCBench source on the evaluation platform.

---

## S7 Discussion

### 7.1 The Kernel-Centric Advantage

ParBench's central design decision -- isolating kernel-level translation from build-system generation -- produces a qualitatively different evaluation outcome than repository-level approaches. Claude Sonnet 4.6 achieves 56.3% PASS on CUDA-to-OpenMP translation of the same class of HPC kernels for which ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 at the repository level. This is not a comparison of different benchmarks or different models; it is a comparison of evaluation granularity applied to overlapping computational domains.

The implication is that LLMs possess substantial internalized knowledge of parallel programming patterns -- thread decomposition, reduction operations, stencil computation, synchronization -- that is masked when evaluation conflates translation skill with build-system generation. ParBench's kernel-centric design separates these orthogonal capabilities, enabling measurement of each in isolation. The two evaluation granularities are complementary: ParEval-Repo measures end-to-end deployment capability; ParBench measures translation capability. Both are needed to characterize LLM parallel programming skill.

### 7.2 BUILD\_FAIL as the Actionable Bottleneck

BUILD\_FAIL dominance (18/33 = 54.5% of L0 failures; 180/425 = 42.4% of all failures across 562 tasks) establishes that the primary bottleneck is API-specific syntax rather than parallel reasoning capability. The recurring error patterns -- retained `cudaMalloc`/`cudaFree` calls, missing OpenMP pragma directives, incorrect type coercions -- are syntactic, not algorithmic. This finding has a direct practical implication: targeted fine-tuning on OpenMP idioms, or few-shot prompting with canonical CUDA-to-OpenMP translation examples, would likely close a substantial portion of the BUILD\_FAIL gap. The parallel reasoning is already present in the model weights; the API surface coverage is the limiting factor.

VERIFY\_FAIL (8/33 = 24.2% of L0 failures; 55/425 = 12.9% of all failures) provides a more nuanced picture than the BUILD\_FAIL-only story suggests. These are translations that compile, run to completion, and produce output -- but incorrect output. The S-VERIFY verification upgrade (from disjunctive exit-code-or-pattern to conjunctive exit-code-and-pattern checking) revealed these cases, which were previously masked by less stringent verification. VERIFY\_FAIL indicates genuine parallel logic errors: wrong thread-index mappings, incorrect reduction scoping, or missed data dependencies that produce numerically wrong results. The presence of VERIFY\_FAIL, while rarer than BUILD\_FAIL, demonstrates that LLMs do not always correctly reason about parallel computation structure even when they produce syntactically valid code.

RUN\_FAIL (5/33 = 15.2% of L0 failures) represents a subtler challenge. Kernels like hotspot compile for all three models but crash at runtime, suggesting that the translation preserves surface syntax while introducing errors in memory access patterns or thread synchronization that are not detectable at compile time. These failures require deeper semantic understanding of the source kernel's runtime behavior -- a harder problem than syntax translation.

### 7.3 Model Capability Spread

The 37.5-percentage-point spread between Claude Sonnet 4.6 (56.3%) and the two non-frontier models (both 18.8%) at L0 reflects a two-tier capability structure rather than a smooth continuum. The omnibus chi-squared test (chi2(2)=136.93, p < 0.001, Cramer's V=0.494) confirms that model identity is a strong predictor of pass rate. Pairwise comparisons show that Claude dramatically outperforms both Gemini (OR=12.68, Cohen's h=1.062, large effect) and Groq (OR=10.49, Cohen's h=1.007, large effect), while Gemini and Groq are statistically indistinguishable (OR=0.83, p=1.0, Cohen's h=-0.055).

The three-model per-kernel analysis reveals that the proprietary/open-weight distinction is less predictive than overall model capability. Gemini (proprietary) and Groq/Llama (open-weight) achieve identical L0 pass rates (18.8%), and their per-kernel failure profiles are strikingly similar: both produce 8 BUILD\_FAIL, 2 RUN\_FAIL, and 2 VERIFY\_FAIL at L0. The relevant axis is not access model (proprietary vs. open) but training data coverage and model scale.

Claude's failure profile at L0 (2 BUILD\_FAIL, 1 RUN\_FAIL, 4 VERIFY\_FAIL) is qualitatively different from the non-frontier models' profiles (dominated by BUILD\_FAIL). Claude's higher VERIFY\_FAIL count reflects its ability to produce compilable code for more kernels -- some of which produce incorrect output. This is a more advanced failure mode: the model has sufficient API syntax knowledge to clear the compilation barrier but introduces subtle parallel logic errors in the translated computation. The non-frontier models fail earlier in the pipeline (BUILD\_FAIL), never reaching the stage where output correctness can be evaluated.

### 7.4 Direction Asymmetry

The cross-direction evaluation (S6.6, Table 11) reveals that CUDA-to-OpenMP translation is easier than OpenMP-to-CUDA in aggregate, with a gap of 12.5 percentage points (31.3% vs. 18.8%). The asymmetry is strongest for Claude (+18.8pp) and Gemini (+18.8pp), while Groq shows no direction asymmetry (18.8% in both directions). This finding has a structural explanation rooted in the programming models.

CUDA source code encodes explicit thread decomposition: `threadIdx`, `blockIdx`, and `blockDim` define the mapping from threads to data elements; `__shared__` memory declares the scratchpad; `cudaMalloc`/`cudaMemcpy` manage device memory; and kernel launch syntax (`<<<blocks, threads>>>`) parameterizes the execution configuration. When translating CUDA to OpenMP, the LLM must *remove* this explicit machinery and replace it with higher-level directives (`#pragma omp parallel for`). The CUDA source provides a complete blueprint of the parallelism structure that the LLM can read and simplify.

In the reverse direction, OpenMP source provides only high-level annotations (`#pragma omp parallel for reduction(+:sum)`) over sequential-looking loop nests. The LLM must *introduce* thread-block geometry, device memory allocation, kernel launch parameters, and explicit synchronization -- none of which are present in the source. This is a generative task (introducing structure) rather than a reductive one (simplifying structure), and generative tasks are inherently harder because the model must make design choices not constrained by the input.

The per-kernel asymmetry data quantifies this effect: of 48 kernel-model cells, 10 pass CUDA-to-OMP only while 4 pass OMP-to-CUDA only -- a 2.5:1 ratio. The O2C\_ONLY exceptions prevent over-generalization but do not challenge the dominant pattern. Notably, the direction asymmetry is model-dependent: Claude and Gemini both show +18.8pp asymmetry, while Groq achieves identical rates in both directions (18.8%). Groq's symmetry may reflect a translation strategy less reliant on direction-specific source patterns. BOTH\_PASS cells (5/48 = 10.4%) identify the easiest kernels -- those where the parallel structure is transparent enough for bidirectional translation.

The practical implication is that LLM-assisted portability tooling is more viable for CUDA-to-CPU translation (where organizations migrate away from NVIDIA-specific code) than for the reverse, though the asymmetry varies by model.

### 7.5 Threats to Validity

Several threats to the validity of these findings must be acknowledged.

**Sample size.** The evaluation covers 16 Rodinia kernels for the primary CUDA-to-OpenMP direction: the 22 available CUDA kernels reduced by 6 that are ineligible. Four lack a valid OpenMP target spec: `dwt2d` has no OpenMP Rodinia implementation, and the OpenMP specs for `gaussian`, `huffman`, and `hybridsort` were phantom entries pointing to non-existent source directories and have been removed from the corpus. Two have KNOWN\_FAIL CUDA source specs: `kmeans-cuda` and `mummergpu-cuda` cannot build under CUDA 12 due to removed `texture<>` references. (The two OpenCL-only KNOWN\_FAIL specs -- nn-opencl and kmeans-opencl -- do not affect the CUDA-to-OpenMP direction.) While 16 kernels span diverse computational domains (graph, stencil, linear algebra, machine learning, molecular dynamics, fluid dynamics), generalization to larger benchmark suites (HeCBench, NAS, Polybench) is not established and is planned as future work.

**Correctness-only metric.** ParBench measures translation correctness, not performance. An OpenMP translation that produces correct output but runs 100x slower than the original CUDA kernel is counted as PASS. This is a deliberate design choice -- correctness is a prerequisite for performance analysis -- but it means pass rates should not be interpreted as deployment readiness. Kernel execution time comparison between CUDA and translated OpenMP is deferred to future work.

**Verification granularity.** The S-VERIFY upgrade strengthened verification from disjunctive (exit\_code OR stdout\_pattern) to conjunctive (exit\_code AND stdout\_pattern) checking, revealing 55 VERIFY\_FAIL cases previously masked by exit-code-only verification. While this represents a more accurate picture of translation correctness, the stdout\_pattern coverage varies across specs: some use kernel-specific numeric patterns while others use generic output matching. Future work should expand stdout\_pattern coverage to include fine-grained numeric output comparison for all kernels.

**Single translation direction emphasis.** The primary results report CUDA-to-OpenMP in detail. Rodinia cross-direction results (S6.6) confirm that CUDA-to-OpenMP is 12.5pp easier than the reverse direction in aggregate, and XSBench cross-direction results span all 12 API directions. However, whether the per-kernel findings fully generalize across all directions is not yet established. Each direction involves different translation challenges: OpenMP-to-CUDA requires introducing explicit thread-block decomposition, and CUDA-to-OpenCL requires generating separate kernel files.

**Temperature and seed.** All evaluations use temperature=0 and augmentation seed=42 for deterministic reproducibility. This provides a single point estimate rather than a distribution. Results could differ with temperature greater than 0, and the variance of LLM translation quality is not characterized by this evaluation.

**Three-model evaluation.** Three models are evaluated, spanning the proprietary/open-weight divide. A fourth model (GPT-4.1, accessed via Azure) was initially included but subsequently removed when the Azure deployment was disabled; results may not generalize to the GPT model family. Reasoning models (e.g., GPT-o1, Claude with extended thinking) are intentionally excluded to isolate base API knowledge from on-the-fly reasoning capability. The three-model set does not represent the full landscape of available LLMs; additional models would strengthen generalizability claims.

**Reference implementation as ground truth.** The Rodinia OpenMP reference output serves as the correctness standard. Floating-point non-associativity between CUDA GPU computation and OpenMP CPU computation could in principle cause false VERIFY\_FAIL results. While 55 VERIFY\_FAIL cases are observed across 562 tasks, manual inspection of a sample indicates these reflect genuine translation errors (wrong thread-index mappings, incorrect reduction scoping) rather than floating-point divergence artifacts. Nonetheless, the correctness configurations use small problem sizes where floating-point divergence is minimized.

**Kernel-centric scope.** ParBench intentionally excludes project-level restructuring (CMake generation, header reorganization, build-system adaptation). This is a design choice that enables measurement of translation skill in isolation, but it means results do not characterize LLM capability for end-to-end deployment. ParEval-Repo \cite{ParEvalRepo2025} provides the complementary measurement.

### 7.6 Augmentation Robustness Reveals a Model-Capability Tier

The augmentation robustness results stratify models in a way that the L0 results alone cannot. Claude's statistical stability across augmentation levels (Cochran-Armitage z=-0.15, p=0.88) provides evidence that it reasons about parallel program structure rather than pattern-matching from training data. While Claude's pass rate varies between 43.8% and 56.3% across levels -- reflecting individual kernels flipping at the VERIFY\_FAIL boundary under stricter conjunctive verification -- the aggregate performance is statistically indistinguishable across levels. The alternative hypothesis -- that Claude memorized all 16 Rodinia kernels in all augmentation variants -- is implausible given that the augmented variants did not exist in any training corpus.

Gemini's degradation is sharp and directional: it passes 3 of 16 kernels at L0--L2, loses one at L3, and collapses to 0 at L4. The L4 failure mode observed in build error logs includes generating C++ syntax (e.g., namespace qualifiers, C++-style casts) for targets that require plain C, suggesting that the heavily transformed variable names and function identifiers cause surface-level language confusion. This is consistent with a model that indexes on surface cues -- familiar variable names, known function signatures -- to determine the appropriate translation pattern.

Groq Llama 3.3 70B's decreasing pattern (3, 2, 2, 2, 1 across L0--L4) parallels Gemini's degradation at a smaller scale. The Cochran-Armitage test does not reach significance (p=0.34), but the consistent downward direction and the L4 collapse to a single kernel (bptree -- the simplest kernel in the evaluation) suggest sensitivity to augmentation similar in kind to Gemini's, if milder in degree.

These findings suggest that augmentation robustness is a better discriminator of genuine parallel reasoning capability than pass@1 at L0 alone. A model that achieves pass@1 on unmodified code but degrades under augmentation is likely leveraging training-data familiarity rather than structural understanding. Augmentation robustness should be considered a standard evaluation dimension for LLM code translation benchmarks, particularly when the benchmark codes are drawn from well-known, widely-published sources.

### 7.7 Implications

The findings suggest several directions for improving LLM-based parallel code translation.

**Targeted API syntax training.** BUILD\_FAIL dominance (42.4% of all failures) suggests that the highest-ROI intervention is improving LLM coverage of OpenMP syntax and idioms. The smaller but meaningful VERIFY\_FAIL rate (12.9%) indicates that parallel reasoning improvement is also needed, but the syntactic barrier is the more common bottleneck. Few-shot prompting with canonical CUDA-to-OpenMP translation patterns, or fine-tuning on a corpus of verified translations, could reduce BUILD\_FAIL rates substantially.

**Augmentation as training curriculum.** The L0--L4 augmentation ladder provides a natural curriculum for training or evaluating models on increasingly surface-varied parallel code. Claude's statistical stability across augmentation levels confirms that augmentation-robust models exist; the question is whether augmentation-sensitive models (Gemini, Llama) can be improved through exposure to augmented training examples.

**Framework as community infrastructure.** ParBench's spec schema is the extension point: adding a new kernel requires one JSON file with no modification to the harness or evaluation pipeline. Extension to HeCBench (120 specs curated), Polybench, and NAS parallel benchmarks would substantially broaden the evaluation substrate. The build/run/verify pipeline is benchmark-agnostic; any kernel with a deterministic correctness check can be onboarded.

**Agentic translation.** ParaCodex \cite{ParaCodex2026} provides profiling-guided autonomous parallel code translation via an agentic framework. ParBench's specs and harness serve as a natural evaluation backend for agentic systems that go beyond single-prompt translation to iterative profiling, repair, and optimization. Joint evaluation of ParaCodex against ParBench specs is planned as future work.

---

## S8 Conclusion

### 8.1 Summary

This paper presented ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level. ParBench makes four contributions.

First, ParBench provides the first systematic framework for evaluating kernel-level parallel code translation, supporting 184 specs across three benchmark suites (Rodinia, HeCBench, XSBench), three parallel APIs (CUDA, OpenMP, OpenCL), and twelve translation directions. The kernel-centric design isolates translation skill from build-system generation, the binding constraint identified by repository-level evaluation \cite{ParEvalRepo2025}.

Second, an AST-driven augmentation engine applies six semantics-preserving transforms at five augmentation levels (L0--L4). The engine is level-invariant at the harness level: 54/60 Rodinia specs achieve PASS at all levels L1--L4 with zero correctness regressions, confirming that the transforms preserve semantics and providing a validated baseline for LLM robustness evaluation.

Third, empirical evaluation of three LLMs across 562 translation tasks reveals a two-tier capability gap: Claude Sonnet 4.6 achieves 54.3% PASS [47.1%, 61.2%], while Gemini 2.5 Flash-Lite (8.6%) and Llama 3.3 70B (10.2%) are statistically indistinguishable (Fisher's p=1.0). On the primary CUDA-to-OpenMP direction at L0, Claude achieves 56.3% (9/16 Rodinia kernels). A failure taxonomy reveals that BUILD\_FAIL accounts for 42.4% of all failures (180/425) while VERIFY\_FAIL accounts for 12.9% (55/425) -- establishing that API syntax is the primary bottleneck, though a meaningful minority of translations that compile and run produce incorrect parallel logic. Cross-direction evaluation reveals a direction asymmetry: CUDA-to-OpenMP is 12.5 percentage points easier than OpenMP-to-CUDA in aggregate (31.3% vs. 18.8%), reflecting the structural advantage of translating from an explicit thread-decomposition model to a directive-based model.

Fourth, LLM augmentation robustness evaluation at L0--L4 reveals a sharp model-capability tier. Claude Sonnet 4.6 shows no significant augmentation trend (Cochran-Armitage p=0.88), maintaining statistically stable performance across all five augmentation levels. Gemini 2.5 Flash-Lite degrades from 18.8% to 0.0% at L4, consistent with reliance on surface pattern-matching disrupted by augmentation. This augmentation robustness dimension provides a more discriminating evaluation than pass@1 alone.

### 8.2 Future Work

Four directions for future work are prioritized.

**Cross-direction expansion.** XSBench cross-direction evaluation is complete across all 12 API directions, and Rodinia OpenMP-to-CUDA evaluation confirms a consistent 18.8pp direction asymmetry favoring CUDA-to-OpenMP (S6.6). Rodinia CUDA-to-OpenCL evaluation is planned. CUDA-to-OpenCL requires generating structurally distinct output (separate `.cl` kernel files), testing the single-to-multi file generation capability. Extension to CUDA-to-HIP and CUDA-to-SYCL would address additional portability-relevant API pairs.

**Extended benchmark suites.** HeCBench provides 120 curated specs spanning 13 computational domains beyond Rodinia's coverage; evaluation is pending platform deployment. Polybench and NAS parallel benchmarks represent additional extension targets that would broaden domain coverage and increase the statistical power of cross-model comparisons.

**Performance evaluation.** The current study is correctness-only. Reliable performance comparison requires profiler-based kernel timing (Nsight Compute for CUDA, `omp_get_wtime()` for OpenMP), which would characterize whether LLM-translated code preserves not only correctness but also the performance characteristics of the original implementation.

**Agentic translation evaluation.** ParaCodex \cite{ParaCodex2026} provides profiling-guided agentic parallel code translation. ParBench's specs and harness serve as a natural evaluation backend for agentic systems that iterate on translation quality using profiling feedback, build error repair, and performance optimization. Joint evaluation against ParBench specs would characterize whether agentic orchestration can close the BUILD\_FAIL gap that single-prompt translation leaves open.

---

## Data Verification Notes

All quantitative claims in this draft are verified against source files as of 2026-03-28 (post-S-VERIFY conjunctive verification, 562 tasks):

| Claim | Value | Source |
|-------|-------|--------|
| Total evaluated tasks | 562 | eval\_summary.json total\_tasks (2026-03-28) |
| Claude Sonnet 4.6 overall | 102/188 = 54.3% [47.1%, 61.2%] | eval\_summary.json + statistical\_analysis.json |
| Gemini 2.5 Flash-Lite overall | 16/187 = 8.6% [5.3%, 13.5%] | eval\_summary.json + statistical\_analysis.json |
| Groq Llama 3.3 70B overall | 19/187 = 10.2% [6.6%, 15.3%] | eval\_summary.json + statistical\_analysis.json |
| Claude L0 cuda-to-omp | 9/16 = 56.3% | Individual result JSONs (2026-03-28), excl. KNOWN\_FAIL sources |
| Gemini L0 cuda-to-omp | 3/16 = 18.8% | Individual result JSONs (2026-03-28), excl. KNOWN\_FAIL sources |
| Groq L0 cuda-to-omp | 3/16 = 18.8% | Individual result JSONs (2026-03-28), excl. KNOWN\_FAIL sources |
| Aggregate L0 cuda-to-omp | 15/48 = 31.3% | Computed: 9+3+3 = 15; 3×16 = 48 (excl. KNOWN\_FAIL sources) |
| BUILD\_FAIL (L0 c2o) | 18/33 = 54.5% | Computed from per-model L0 data (16 Rodinia kernels) |
| VERIFY\_FAIL (L0 c2o) | 8/33 = 24.2% | Computed from per-model L0 data |
| RUN\_FAIL (L0 c2o) | 5/33 = 15.2% | Computed from per-model L0 data |
| EXTRACTION\_FAIL (L0 c2o) | 2/33 = 6.1% | Computed from per-model L0 data |
| Failure taxonomy (all 562) | BUILD=180, RUN=123, VERIFY=55, EXTRACT=67 | eval\_summary.json failure\_taxonomy |
| Model comparison chi2 | chi2(2)=136.93, p < 0.001, V=0.494 | statistical\_analysis.json |
| Claude vs Gemini | OR=12.68, h=1.062 (large) | statistical\_analysis.json pairwise |
| Claude vs Groq | OR=10.49, h=1.007 (large) | statistical\_analysis.json pairwise |
| Gemini vs Groq | OR=0.83, p=1.0, h=-0.055 | statistical\_analysis.json pairwise |
| L0 self-repair (c2o) | 10 first-attempt + 5 repaired = 15 PASS | Individual result JSONs (16 Rodinia kernels) |
| All-task self-repair | 107 first-attempt + 30 repaired = 137 PASS | eval\_summary.json self\_repair |
| Claude augmentation L0-L4 (c2o) | 9, 8, 8, 7, 9 | 16 Rodinia kernels (excl. KNOWN\_FAIL); stat tests use 17 incl. XSBench |
| Gemini augmentation L0-L4 (c2o) | 3, 3, 3, 2, 0 | Individual L0-L4 result JSONs |
| Groq augmentation L0-L4 (c2o) | 3, 2, 2, 2, 1 | Individual L0-L4 result JSONs |
| Cochran-Armitage (Claude) | z=-0.15, p=0.88 | statistical\_analysis.json |
| Cochran-Armitage (overall) | z=-1.24, p=0.22 | statistical\_analysis.json |
| Always-pass kernels (3-model) | 2 (bptree, hotspot3d) | Per-kernel L0 matrix |
| Always-fail kernels (3-model) | 7 (bfs, heartwall, hotspot, myocyte, nw, pathfinder, streamcluster) | Per-kernel L0 matrix |
| Direction asymmetry (aggregate) | +12.5pp (C2O 31.3% vs O2C 18.8%) | Computed from L0 result files |
| Direction asymmetry (Claude) | +18.8pp (56.3% vs 37.5%) | Computed from L0 result files |
| Direction asymmetry (Gemini) | +18.8pp (18.8% vs 0.0%) | Computed from L0 result files |
| Direction asymmetry (Groq) | +0.0pp (18.8% vs 18.8%) | Computed from L0 result files |
| C2O\_ONLY cells | 10/48 | Computed from L0 paired cells |
| O2C\_ONLY cells | 4/48 | Computed from L0 paired cells |
| BOTH\_PASS cells | 5/48 | Computed from L0 paired cells |
| BOTH\_FAIL cells | 29/48 | Computed from L0 paired cells |
| Augmentation baseline | 54/60 PASS at L1-L4 | results/augmentation/retest\_post\_session2.md |
| Total specs | 184 (60 Rodinia + 120 HeCBench + 4 XSBench) | specs/ directory |
| Rodinia PASS | 54/60 | Harness verification |
| XSBench PASS | 4/4 | Harness verification |
| Translation directions | 12 | eval\_summary.json by\_direction keys |
| ParEval-Repo 0% pass@1 | >133 SLoC applications | \cite{ParEvalRepo2025} |
| GPU | NVIDIA GeForce RTX 4070 | System hardware |
| CPU | AMD Ryzen 9 7900X | System hardware |
| OS | Ubuntu 24.04 LTS (kernel 6.8.0-40-generic) | System OS |
| CUDA | 12.3 (NVIDIA HPC SDK 24.3) | nvcc --version |
| GCC | 12.4 with -fopenmp | gcc --version |
| Python | 3.12.3 | python3 --version |
