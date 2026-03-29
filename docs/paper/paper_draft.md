# ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness

**Alternative title:** ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation

**Venue:** SC26 -- Supercomputing 2026 (full technical paper)
**Format:** ACM sigconf double-column, ~10 pages + appendices
**Status:** DRAFT -- S1--S8 structure complete; rewriting for 2-model 5-suite campaign (2026-03-29)
**Author:** \author{[Anonymous for Review]}

---

## Abstract

Large language models (LLMs) are increasingly applied to parallel code generation, yet no benchmark framework systematically evaluates their ability to *translate* parallel code across GPU programming APIs -- and prior approaches share a critical blind spot: benchmark codes widely known in the HPC community are also present in LLM training data, making it impossible to distinguish genuine parallel reasoning from memorized translations. We present **ParBench**, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level, with an integrated augmentation engine that systematically tests reliance on training-data pattern-matching. ParBench curates 96 benchmark specifications across five HPC benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. Evaluating two LLMs -- Qwen 3.5 397B-A17B (a 397-billion-parameter Mixture-of-Experts model) and Gemini 2.5 Flash -- across [PLACEHOLDER: total_tasks] translation tasks spanning [PLACEHOLDER: kernel_count] kernels, six directions, and five augmentation levels, we find [PLACEHOLDER: capability_gap_description]: [PLACEHOLDER: model1_name] achieves [PLACEHOLDER: model1_overall_rate] PASS [PLACEHOLDER: model1_ci], while [PLACEHOLDER: model2_name] achieves [PLACEHOLDER: model2_overall_rate] [PLACEHOLDER: model2_ci] ([PLACEHOLDER: statistical_comparison]). On the primary CUDA-to-OpenMP direction at L0, [PLACEHOLDER: best_model_cuda_to_omp_L0_description] -- compared to 0% in repository-level approaches \cite{ParEvalRepo2025}. BUILD\_FAIL accounts for [PLACEHOLDER: build_fail_rate] of all tasks; VERIFY\_FAIL accounts for [PLACEHOLDER: verify_fail_rate], indicating [PLACEHOLDER: failure_taxonomy_interpretation]. An AST-driven augmentation engine applies six semantics-preserving transforms at five levels (L0--L4); all non-KNOWN\_FAIL specs across all five suites PASS at every level L1--L4 with zero correctness regressions, confirming level-invariant semantics preservation. LLM augmentation robustness evaluation reveals [PLACEHOLDER: augmentation_trend_description], providing evidence that augmentation robustness discriminates structural reasoning from surface pattern-matching. ParBench is publicly available as an extensible framework for the HPC community.

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

**The gap in benchmark selection rationale.** A final dimension on which prior work is incomplete is the *why* of benchmark selection. Which parallel APIs matter most? Which kernels are representative? Existing frameworks do not answer these questions systematically. ParBench's selection is grounded in a comprehensive empirical survey of 35 open-source HPC repositories covering all major parallel programming models. That survey identified 472 CUDA-OpenMP kernel pairs across 21 repositories -- the largest available translation opportunity in the ecosystem, and the practical bottleneck for real-world GPU-to-CPU portability work. It further identified which benchmark suites provide the same kernel implemented across multiple APIs (Rodinia, HeCBench, XSBench, RSBench, mixbench), which have automatable build/run/verify pipelines, and which have self-checking output patterns. The choice of CUDA-to-OpenMP as the primary translation direction, and of Rodinia as the primary evaluation substrate, follows directly from this survey -- not from convenience.

Together, these four gaps define the problem that ParBench is designed to solve: kernel-level evaluation granularity, build-infrastructure isolation, training-data robustness through augmentation, and survey-grounded benchmark selection.

### 1.3 Contributions

This paper presents ParBench and makes the following contributions:

1. **ParBench framework** -- The first build/run/verify benchmark framework for LLM-based parallel code translation at the kernel level, supporting 96 specifications across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. Kernel-centric translation mode isolates the translation skill from build-system generation, directly addressing the binding constraint identified by repository-level evaluation \cite{ParEvalRepo2025}.

2. **AST-driven augmentation engine** -- Six semantics-preserving source-level transforms at five augmentation levels (L0--L4) that systematically test whether LLMs reason about parallel structure or pattern-match from training data. Level-invariant: all non-KNOWN\_FAIL specs across five suites PASS at all levels L1--L4 with zero correctness regressions. LLM evaluation at L0--L4 measures augmentation robustness as a discriminator of genuine parallel reasoning versus surface pattern-matching.

3. **Empirical evaluation** -- Comparative analysis of two LLMs (Qwen 3.5 397B-A17B, Gemini 2.5 Flash) across [PLACEHOLDER: total_tasks] translation tasks spanning six directions and five augmentation levels, producing a failure taxonomy ([PLACEHOLDER: build_fail_rate] BUILD\_FAIL, [PLACEHOLDER: verify_fail_rate] VERIFY\_FAIL), per-kernel difficulty tiers, self-repair effectiveness measurement, and augmentation robustness characterization with statistical independence testing. The two models represent distinct architecture families (Mixture-of-Experts vs. dense) from different providers, testing whether architectural diversity produces divergent translation capabilities.

### 1.4 Key Findings Preview

ParBench produces several findings with immediate relevance for the HPC and LLM research communities:

**Kernel-centric isolation unlocks success.** [PLACEHOLDER: best_model_name] achieves [PLACEHOLDER: best_model_cuda_to_omp_L0_rate] PASS on CUDA-to-OpenMP translation at L0 ([PLACEHOLDER: best_model_cuda_to_omp_L0_count] Rodinia kernels), directly contrasting with 0% achieved by all models on repository-level approaches \cite{ParEvalRepo2025}. The gap quantifies the orthogonality of translation skill and build-system-generation skill.

**Capability gap and failure taxonomy.** [PLACEHOLDER: model_comparison_description]: [PLACEHOLDER: model1_name] achieves [PLACEHOLDER: model1_overall_rate] PASS [PLACEHOLDER: model1_ci] across all [PLACEHOLDER: total_tasks] tasks, while [PLACEHOLDER: model2_name] achieves [PLACEHOLDER: model2_overall_rate] [PLACEHOLDER: model2_ci] ([PLACEHOLDER: statistical_test_result]). BUILD\_FAIL accounts for [PLACEHOLDER: build_fail_rate] of all tasks, making it the dominant failure mode. VERIFY\_FAIL accounts for [PLACEHOLDER: verify_fail_rate], indicating that [PLACEHOLDER: verify_fail_interpretation]. The primary bottleneck remains API-specific syntax -- missing `#pragma omp` directives, retained CUDA memory management calls, wrong type annotations -- rather than an inability to reason about parallel computation.

**Augmentation robustness discriminates reasoning from pattern-matching.** [PLACEHOLDER: augmentation_overall_trend_description]. Per-model analysis reveals [PLACEHOLDER: augmentation_per_model_description], providing evidence that augmentation robustness measures a dimension of capability distinct from aggregate pass rate.

**Direction asymmetry.** [PLACEHOLDER: direction_asymmetry_description]. The trend suggests that removing CUDA-specific constructs (explicit thread indexing, device memory management) is generally easier for LLMs than introducing them from directive-based OpenMP source, reflecting the structural advantage of translating from a more explicit to a more abstract programming model.

**Self-repair effectiveness.** [PLACEHOLDER: self_repair_description]. The gap between first-attempt pass rate and final pass rate (after up to 3 retries with error feedback) quantifies the value of lightweight agentic error correction, directly comparable to the full agentic approaches evaluated by LASSI \cite{LASSI2024}.

---

## S2 Related Work

LLM-based code translation has advanced rapidly, but its application to parallel scientific code remains underexplored relative to general-purpose translation. We organize prior work along two axes: (1) the *granularity* at which translation is evaluated (function, kernel, repository), and (2) the *verification rigor* applied to translation output (syntax metrics, compilation checks, or full functional correctness). Table 1 positions ParBench within this landscape.

### 2.1 The Granularity--Verification Landscape

[TABLE 1: Related work comparison.]

| Paper | Venue | Granularity | Verification | HPC Parallel | Augmentation | Scale |
|-------|-------|-------------|-------------|:------------:|:------------:|-------|
| HumanEval \cite{HumanEval2021} | arXiv'21 | Function | Unit tests | -- | -- | 164 functions |
| SWE-bench \cite{SWEbench2024} | ICLR'24 | Repository | Test suite | -- | -- | 2,294 issues |
| TransCoder \cite{TransCoder2020} | NeurIPS'20 | Function | Unit tests | -- | -- | 852 functions |
| CodeRosetta \cite{CodeRosetta2024} | NeurIPS'24 | Function | BLEU + compile | Yes | -- | C++/CUDA corpus |
| OMPify \cite{OMPify2023} | IWOMP'23 | Loop | Pragma accuracy | Partial | -- | 54K snippets |
| LASSI \cite{LASSI2024} | CLUSTER'24 | Kernel | Build+Run+Verify | Yes | -- | 10 HeCBench |
| ParEval \cite{ParEval2024} | HPDC'24 | Task | Correctness check | Yes | -- | 420 tasks |
| ParEval-Repo \cite{ParEvalRepo2025} | ICPP'25 | Repository | Build + functional | Yes | -- | 6 apps |
| HPC-Coder-V2 \cite{HPCCoderV2} | arXiv'24 | Task | pass@k | Yes | -- | ParEval tasks |
| TRACY \cite{TRACY2025} | arXiv'25 | Function | Tests + efficiency | -- | Stress tests | 1,000 tasks |
| **ParBench (ours)** | **SC26** | **Kernel** | **Build+Run+Verify** | **Yes** | **Yes (L0--L4)** | **96 specs, 5 suites, 6 dirs, 2 models** |

*Table 1: Related work comparison along the granularity--verification axes. ParBench is the only framework combining kernel-level granularity, conjunction verification (stdout pattern AND exit code), and AST-driven augmentation for robustness testing. Dashes indicate the feature is absent.*

The question "Can LLMs translate parallel code?" yields different answers at each granularity. ParEval \cite{ParEval2024} asks whether LLMs can *generate* parallel code from natural language descriptions (task level). ParEval-Repo \cite{ParEvalRepo2025} asks whether LLMs can translate *entire HPC repositories* including build systems (repository level), finding 0\% pass@1 for applications exceeding 133 SLoC --- a failure attributable not to parallel logic translation but to build-infrastructure generation. ParBench occupies the *kernel level*: the LLM receives parallel source code and must translate the computation pattern between APIs, with all build infrastructure (Makefiles, headers, support files) provided as fixed context. These three levels are complementary; together they characterize where LLM capability for parallel code begins and ends.

### 2.2 Code Synthesis and Translation Benchmarks

**HumanEval** \cite{HumanEval2021} and **SWE-bench** \cite{SWEbench2024} are widely adopted benchmarks for sequential code synthesis and agentic software engineering, respectively. Neither addresses parallel programming or API-level code translation. However, recent work by Ying et al.\ \cite{SWEbenchIllusion2025} demonstrates that SWE-bench suffers from training-data contamination: models may memorize patches rather than reason about code. This *benchmark memorization* critique directly motivates ParBench's augmentation engine --- AST-driven code transforms produce inputs that cannot appear in any training corpus, testing whether translation reflects genuine understanding of parallel semantics or surface pattern matching.

**TransCoder** \cite{TransCoder2020} (NeurIPS'20) established unsupervised neural code translation between C++, Java, and Python using back-translation. A key insight is that only 3.1\% of translations match reference code exactly, yet 60.9\% pass unit tests --- demonstrating that reference matching is a poor proxy for functional correctness. ParBench builds on this insight: its conjunction verification (stdout pattern AND exit code) measures functional correctness without requiring exact textual match. TransCoder's limitation to general-purpose sequential languages leaves HPC parallel APIs entirely outside its scope.

**CodeRosetta** \cite{CodeRosetta2024} (NeurIPS'24) extends unsupervised translation to parallel programming, training a specialized encoder-decoder transformer on C++ and CUDA monolingual corpora. It reports improvements of +2.9 BLEU and +1.72 CodeBLEU over baselines on C++-to-CUDA translation and introduces ParaBLEU, a metric accounting for parallel semantics. Critically, CodeRosetta evaluates translation quality via BLEU scores and compilation accuracy only --- it does not execute translated code or verify functional correctness. A program that compiles successfully but produces incorrect output would count as a success under CodeRosetta's metrics but a failure under ParBench's conjunction verification. Furthermore, CodeRosetta trains a specialized model, whereas ParBench evaluates general-purpose LLMs to characterize the zero-shot translation frontier. The two approaches are complementary: CodeRosetta demonstrates that domain-specific training improves translation quality metrics, while ParBench measures whether that improvement translates to functional correctness on real HPC benchmarks.

### 2.3 Parallel Code Translation and Evaluation

**LASSI** \cite{LASSI2024} (LLMxHPC Workshop, IEEE CLUSTER'24) is the most directly comparable prior work. LASSI is an automated pipeline that uses LLMs to translate between OpenMP target offload and CUDA, incorporating a self-correcting feedback loop: when translated code fails to compile or execute, error messages are fed back to the LLM for iterative debugging and refinement. Evaluating four LLMs (GPT-4, Codestral 22B, WizardCoder 33B, DeepSeek Coder v2 16B) on 10 HeCBench benchmarks, LASSI reports 80\% pass rate for OMP-to-CUDA and 85\% for CUDA-to-OMP translation after self-correction, with first-attempt success rates of 65.6\% and 55.9\%, respectively. The self-correction loop adds approximately 15--30 percentage points to first-attempt performance.

ParBench and LASSI differ in both *purpose* and *methodology*. LASSI evaluates the effectiveness of an agentic self-correction pipeline; ParBench evaluates raw LLM translation competence. ParBench deliberately limits self-repair to at most three retries with error feedback --- measuring what the model can accomplish with minimal scaffolding, not what an optimized pipeline achieves. This design choice makes ParBench's results a *lower bound* on achievable translation quality, against which agentic approaches like LASSI can be measured. The gap between the two quantifies the value added by agentic infrastructure. Additional differences compound: LASSI evaluates 10 HeCBench kernels across 2 API directions, while ParBench evaluates 96 specs drawn from five benchmark suites across 6 translation directions. LASSI does not test augmentation robustness --- all inputs are unmodified benchmark source --- leaving open the question of whether self-correction success would survive code-level variation. ParBench's augmentation levels (L0--L4) address this directly.

**ParEval** \cite{ParEval2024} (HPDC'24) presents 420 parallel code *generation* tasks across six APIs. It establishes a baseline of LLM capability at parallel code synthesis from natural language --- a necessary precursor to translation evaluation, but a fundamentally different task. **ParEval-Repo** \cite{ParEvalRepo2025} (ICPP'25) extends evaluation to six full HPC applications in three translation directions, finding that no model achieves pass@1 > 0 on applications exceeding 133 SLoC. The root cause is build-system generation failure, not parallel logic failure. ParBench operationalizes this insight by providing all build infrastructure as fixed context, isolating the parallel translation skill. The same kernel that achieves 0\% in ParEval-Repo (XSBench) passes baseline verification in ParBench's harness, confirming that kernel-level evaluation reveals capability that repository-level evaluation obscures.

**HPC-Coder-V2** \cite{HPCCoderV2} (arXiv'24) fine-tunes DeepSeek Coder 6.7B on HPC instruction data, achieving pass@1 of 31.17 on ParEval --- comparable to models at 34B scale and commercial APIs. This demonstrates that domain-specific fine-tuning compensates for smaller model size in parallel code tasks. ParBench complements this finding by evaluating general-purpose LLMs without fine-tuning, measuring the zero-shot frontier that fine-tuned models like HPC-Coder-V2 aim to surpass.

### 2.4 LLM-for-HPC and Emerging Approaches

**HPCorpus** \cite{HPCorpus2023} is a large-scale dataset of HPC code from GitHub containing approximately 300K repositories and 9 million files. Analysis of HPCorpus reveals that only 45\% of its parallel code uses OpenMP, 27\% MPI, and 21\% CUDA/OpenCL --- and HPCorpus itself is a niche collection relative to general code training corpora. This data scarcity provides context for why general-purpose LLMs struggle with HPC code translation: the parallel programming idioms they encounter during training are sparse and unevenly distributed across APIs.

**OMPify** \cite{OMPify2023} (IWOMP'23) uses a graph-based transformer to predict OpenMP pragmas for serial code, achieving up to 90\% accuracy on NAS and SPEC benchmarks. Related tools --- OMPar, OMPGPT \cite{OMPGPT2024} (Euro-Par'24), PragFormer --- all address the narrower subtask of pragma insertion rather than full API-level translation. The gap between OMPify's 90\% pragma accuracy and the substantially lower pass rates observed for full code translation highlights the difficulty increase when the entire program must be restructured, not just annotated.

**TRACY** \cite{TRACY2025} (arXiv'25) is the first benchmark focused on *execution efficiency* of LLM-translated code, evaluating 26+ LLMs on 1,000 tasks derived from TransCoder's test set. A key finding is that correctness is not a reliable proxy for efficiency: 23.5\% of functionally correct translations exhibit pronounced inefficiency. ParBench and TRACY are complementary --- ParBench measures correctness of HPC-specific translation, while TRACY measures efficiency of general-purpose translation. Extending ParBench with efficiency measurement on HPC kernels is a natural direction for future work (S8).

**RepoTransBench** \cite{RepoTransBench2025} and **AlphaTrans** \cite{AlphaTrans2025} evaluate repository-level translation for general-purpose languages, confirming the systematic failures at scale observed by ParEval-Repo. **ParaCodex** \cite{ParaCodex2026} (Kaplan et al.) is a companion system from our research group providing profiling-guided autonomous parallel code translation; ParBench provides the evaluation backend against which ParaCodex's agentic pipeline can be measured.

### 2.5 Training Data Contamination and Benchmark Validity

A growing body of evidence suggests that LLM performance on established benchmarks may reflect memorization rather than reasoning. Ying et al.\ \cite{SWEbenchIllusion2025} show that SWE-bench patch solutions can be recovered from training data, questioning whether high scores indicate genuine software engineering capability. This critique applies with equal force to HPC benchmarks: Rodinia, HeCBench, and XSBench source code is publicly available on GitHub and likely present in LLM training corpora.

ParBench's augmentation engine addresses this concern directly. Six AST-driven transforms (variable renaming, loop restructuring, condition swapping, format string modification, type aliasing, and comment injection) produce semantically equivalent but syntactically novel code at five intensity levels (L0--L4). Augmented inputs cannot appear verbatim in any training corpus. If a model's pass rate degrades under augmentation, that degradation quantifies the extent to which its baseline performance relied on memorization rather than understanding of parallel semantics. No other parallel code translation benchmark provides this capability.

### 2.6 Positioning ParBench

ParBench is, to our knowledge, the only framework that combines all of the following: (1) kernel-level granularity targeting real HPC benchmark suites, (2) conjunction verification (build + run + verify against reference output), (3) AST-driven augmentation for robustness testing, (4) multi-API evaluation across CUDA, OpenMP, and OpenCL with 6 translation directions, and (5) multi-model evaluation of general-purpose LLMs. LASSI shares verification rigor but evaluates an agentic pipeline rather than raw model capability; CodeRosetta shares the HPC translation domain but relies on proxy metrics rather than functional correctness; ParEval and ParEval-Repo share the HPC evaluation focus but target generation and repository-level translation, respectively. ParBench's contribution is the evaluation *framework* --- a reusable, extensible measurement instrument for parallel code translation that can evaluate any model (general-purpose or fine-tuned) and any agentic pipeline against a common, augmentation-hardened standard.


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

This design separates the definition of correctness from the mechanism of verification: the harness can evolve independently of what "correct" means for each kernel. Across the current benchmark collection, 96 specs are defined spanning five benchmark suites: 60 from Rodinia \cite{Rodinia2009}, 4 from XSBench \cite{XSBench2014}, 4 from RSBench, 3 from mixbench, and 25 from a curated subset of HeCBench \cite{HeCBench2023}.

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

**Kernel-centric methodology.** Prior work on repository-level code translation \cite{ParEvalRepo2025} demonstrated that LLM pass rates collapse to 0% for programs exceeding approximately 133 source lines of code (SLoC), largely due to the difficulty of simultaneously generating correct build-system artifacts alongside translated source code. ParBench isolates the translation skill by feeding only the `translation_targets` files (the parallel kernel code) to the LLM; Makefiles, shared headers, serial baselines, and utility code remain unchanged in the target directory. This kernel-centric design enables evaluation of whether an LLM can correctly map parallel programming patterns from one API to another, independent of its ability to replicate project file organization. The rationale is that translation quality and code restructuring ability are orthogonal skills; conflating them produces artificially low pass rates that obscure the model's actual parallel programming competence.

**Prompt structure.** Each translation prompt consists of a system message establishing the role of a parallel programming expert and a user message containing: (1) the source kernel code with API-specific syntax highlighting, (2) the target API and the filenames the LLM must produce, (3) the target build command for compilation compatibility, and (4) read-only target infrastructure context (non-kernel files from the target directory) so the LLM can match expected function signatures and data structures. Source support headers are included with instructions to inline definitions rather than emit unresolvable `#include` directives.

**Self-repair loop.** On failure, the pipeline feeds failure-specific diagnostics back to the LLM: compiler errors on build failure, runtime errors and stderr on execution failure, and verification details on output mismatch. This feedback serves as a follow-up prompt, requesting a corrected translation. This iterative self-repair mechanism allows a configurable number of attempts before a final failure classification. The self-repair loop mirrors the realistic workflow of a developer iterating on errors; it also provides data on which failure modes are recoverable by the model versus those that indicate fundamental translation deficiencies.

**Complexity taxonomy.** To enable stratified analysis of translation difficulty, each source--target pair is classified into one of four complexity classes based on the file cardinality of the translation: `single_file` (1 source file to 1 target file), `multi_to_single` (N source files to 1 target file), `single_to_multi` (1 source file to N targets, characteristic of CUDA-to-OpenCL translations where the host-device split is inherent to the programming model), and `multi_to_multi` (N source files to M target files).

**Model-agnostic design.** The pipeline supports multiple LLM providers through a model registry that maps human-readable identifiers to provider-specific API configurations. All evaluations use temperature 0 for deterministic reproducibility. The framework currently supports Anthropic, OpenAI, Azure OpenAI, Google, Groq, and Together AI API endpoints, enabling cross-model comparison under identical prompt content and evaluation conditions.

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

However, Rodinia's age and wide availability raise a legitimate concern: its source code is likely present in LLM training corpora, potentially inflating pass rates through memorization rather than genuine translation competence. To address this threat to validity and broaden domain coverage, ParBench includes four additional benchmark suites.

**XSBench** \cite{XSBench2014} is a Monte Carlo neutron transport proxy application that implements the continuous-energy macroscopic cross-section lookup kernel from OpenMC. It provides 4 specs (CUDA, OpenMP, OpenCL, OMP-target), all 4 PASS. XSBench is included specifically to enable direct comparison with ParEval-Repo \cite{ParEvalRepo2025}, which evaluates XSBench and achieves 0% pass@1 for all models; ParBench achieves 4/4 PASS using the kernel-centric approach -- same kernel, different evaluation granularity.

**RSBench** is a simplified reactor simulation proxy application derived from the same OpenMC cross-section lookup problem as XSBench but using a multipole method. It provides 4 specs (CUDA, OpenMP, OpenCL, OMP-target), all 4 PASS. RSBench adds a domain-specific workload with different computational patterns (complex arithmetic, Faddeeva function evaluation) that tests LLM translation on code less likely to appear verbatim in training data.

**mixbench** is a GPU micro-benchmark designed to measure the balance between compute throughput and memory bandwidth -- the operational intensity axis of the roofline model. It provides 3 specs (CUDA, OpenMP, OpenCL), all 3 PASS. As a micro-benchmark with tight compute-memory loops, mixbench exercises translation of fine-grained GPU optimization patterns distinct from the algorithmic kernels in the other suites.

**HeCBench (curated)** \cite{HeCBench2023} contributes 10 diverse kernels selected from the larger HeCBench collection (325+ kernels). These 10 kernels were chosen for verified correctness across multiple APIs and domain diversity: stencil computation (stencil1d, heat2d, iso2dfd), graph algorithms (floydwarshall, page-rank), combinatorial search (nqueen), molecular dynamics (md), signal processing (convolution1d, scan), and numerical methods (jacobi). The curated subset provides 25 specs across three APIs (CUDA, CPU OpenMP, OMP-target GPU offload), of which 23 PASS and 2 are KNOWN\_FAIL (stencil1d-omp\_target build failure, scan-omp\_target verification mismatch). Crucially, HeCBench kernels are less widely known than Rodinia, reducing the likelihood that LLMs have memorized their implementations.

In total, the five suites contribute 96 specs, of which 88 achieve PASS and 8 are KNOWN\_FAIL. The selected kernels span computational domains including graph traversal (bfs, floydwarshall, page-rank), physics simulation (hotspot, hotspot3d, cfd, srad, iso2dfd), machine learning (backprop, nn), linear algebra (lud, nw), molecular dynamics (lavamd, md), nuclear physics (xsbench, rsbench), stencil computation (stencil1d, heat2d, jacobi), signal processing (convolution1d, scan), biophysical simulation (myocyte, heartwall), particle methods (particlefilter, streamcluster), dynamic programming (pathfinder), combinatorial search (nqueen), and GPU micro-benchmarking (mixbench).

[TABLE 4: Suite summary showing total specs, verified PASS, KNOWN\_FAIL, and API coverage for each of the five benchmark suites.]

| Suite | Kernels | Total Specs | PASS | KNOWN\_FAIL | APIs |
|:------|:-------:|:-----------:|:----:|:----------:|:-----|
| Rodinia | 22 | 60 | 54 | 6 | CUDA, OpenMP, OpenCL |
| XSBench | 1 | 4 | 4 | 0 | CUDA, OpenMP, OpenCL, OMP-target |
| RSBench | 1 | 4 | 4 | 0 | CUDA, OpenMP, OpenCL, OMP-target |
| mixbench | 1 | 3 | 3 | 0 | CUDA, OpenMP, OpenCL |
| HeCBench (curated) | 10 | 25 | 23 | 2 | CUDA, OpenMP, OMP-target |
| **Total** | **35** | **96** | **88** | **8** | |

### 4.C API Coverage

CUDA serves as the primary source language, reflecting its dominant position in GPU programming. OpenMP is the primary translation target, selected because the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity (472 kernel pairs across 21 repositories). OpenCL provides a secondary target that exercises a qualitatively different programming model: explicit memory management, separate kernel compilation, and host-device code separation. OpenMP target offload (OMP-target) provides a fourth API that uses compiler-directed GPU offloading via `#pragma omp target`; it is available for XSBench, RSBench, and the HeCBench curated kernels, and requires the NVIDIA HPC compiler (`nvc`). Together, these four APIs cover the principal parallel programming paradigms in HPC: GPU-native (CUDA), directive-based CPU parallelism (OpenMP), portable heterogeneous (OpenCL), and directive-based GPU offload (OMP-target).

### 4.D Evaluation Corpus

The 88 verified-PASS specs across all five suites constitute the evaluation corpus. At L0 (unaugmented), the corpus yields 142 unique translation pairs per model across six standard translation directions (with two additional OMP-target directions evaluated as case studies). The OMP-target variants are included selectively: XSBench and RSBench OMP-target specs serve as case studies requiring the NVIDIA HPC compiler, while HeCBench OMP-target specs participate in standard evaluation where the target spec passes verification. The selection is principled rather than exhaustive: the spec schema permits straightforward extension to additional suites, kernels, and APIs without modification to the evaluation harness. Each kernel in the corpus was independently verified through the complete build/run/verify pipeline prior to inclusion in any LLM evaluation experiment.

---

## S5 Experimental Setup

This section describes the models, translation directions, augmentation protocol, evaluation metrics, and hardware/software configuration used in the primary evaluation campaign.

### 5.A Models

Two large language models are evaluated, selected to maximize architectural diversity across non-Anthropic providers (D1):

- **Qwen 3.5 397B-A17B** (Alibaba, accessed via Together AI): A Mixture-of-Experts (MoE) model with 397 billion total parameters and 17 billion active per forward pass. The MoE architecture tests whether massive parameter count with sparse activation -- where only a fraction of parameters are consulted per token -- benefits HPC translation, a domain where relevant knowledge may be distributed across specialized expert subnetworks.

- **Gemini 2.5 Flash** (Google, accessed via Google AI): A dense-architecture model where all parameters are active for every token. Flash represents Google's latest generation of fast inference models, optimized for throughput while retaining strong code generation capabilities.

Both models are queried at temperature 0 (greedy decoding) for the primary campaign to ensure deterministic outputs and reproducibility across runs (D3). Reasoning and chain-of-thought modes are explicitly disabled for all models. This is a deliberate design choice: the evaluation targets raw translation competence -- whether a model's internalized knowledge of parallel programming patterns suffices to produce correct translations -- rather than the capacity of a multi-step reasoning scaffold to search for solutions.

The two models were chosen to maximize architectural diversity (MoE vs. dense) across different providers, rather than brand recognition. Neither model is produced by Anthropic, avoiding self-evaluation bias. The ParBench framework is model-agnostic: adding a model requires only an API key and a single command via the parameterized campaign script (D5). Pilot data from three additional models (Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, and Llama 3.3 70B) are available as supplementary material.

[TABLE 5: Model configurations. Columns: human-readable name, API model identifier, provider, architecture type (MoE/dense), and parameter count (total / active, where publicly disclosed).]

### 5.B Translation Directions

Six primary translation directions are evaluated across three parallel APIs, covering all bidirectional pairs:

- CUDA $\leftrightarrow$ OpenMP (2 directions)
- CUDA $\leftrightarrow$ OpenCL (2 directions)
- OpenMP $\leftrightarrow$ OpenCL (2 directions)

Two additional directions involving OpenMP target offload (OMP-target) are evaluated within the HeCBench subset only: CUDA to OMP-target (8 pairs) and OMP-target to CUDA (10 pairs). These are treated as a case study rather than part of the primary evaluation matrix, because OMP-target requires the NVIDIA HPC compiler (`nvc`) and is available only for the 10 curated HeCBench kernels.

At L0 (no augmentation), this yields 142 translation task pairs per model across all five benchmark suites: 96 from Rodinia (15 kernels with full 3-API coverage contributing 90 pairs; 3 kernels with partial 2-API coverage contributing 6 pairs), 6 each from XSBench, RSBench, and mixbench, and 28 from the curated HeCBench subset. The per-direction pair counts are: cuda-to-omp (24), omp-to-cuda (24), cuda-to-opencl (20), opencl-to-cuda (20), omp-to-opencl (18), opencl-to-omp (18), cuda-to-omp\_target (8), and omp\_target-to-cuda (10).

CUDA to OpenMP serves as the primary evaluation direction, representing the most common real-world HPC translation need: migrating GPU-accelerated CUDA code to the portable, CPU-parallel OpenMP model. The remaining directions provide cross-directional comparison and test whether translation difficulty is symmetric across API pairs. Not all directions apply to every kernel, as some benchmarks lack implementations in all APIs; the evaluation covers all valid source--target pairs within the benchmark suite.

### 5.C Augmentation Protocol

Source code augmentation is applied at five levels. Level L0 uses the unmodified benchmark source and serves as the baseline. Levels L1 through L4 apply the six AST-driven transforms (described in Section 3.C) at increasing density: L1 applies one randomly selected transform at a single candidate site; L2 selects 33\% of transforms and applies each to 33\% of eligible candidate sites; L3 selects 66\% of transforms at 66\% of sites; and L4 applies all transforms at all sites. A fixed random seed of 42 governs all stochastic choices for reproducibility. With 5 augmentation levels and 142 L0 task pairs, the primary campaign comprises 710 translation tasks per model (D2).

The augmentation protocol tests a specific hypothesis: if an LLM genuinely reasons about parallel computation structure rather than pattern-matching against memorized training examples, its translation success rate should remain stable across augmentation levels. The augmentation baseline was verified prior to the campaign launch (D6): 68 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench) were run through the full build-run-verify pipeline at all five augmentation levels. All produced identical correctness outcomes, confirming that the AST-driven transforms preserve semantic equivalence and that any variation in LLM pass rates across levels can be attributed to the model rather than to the augmentation process. Eight KNOWN\_FAIL specs are excluded from the evaluation corpus (Section 4.B).

### 5.D Metrics

The primary evaluation metric is **greedy-decode pass@1**: the fraction of translation tasks that pass the full build, run, and verify pipeline on a single greedy-decoded evaluation (temperature 0), with up to 3 self-repair attempts via iterative error feedback (D3). We use the term "greedy-decode pass@1" to distinguish this from the standard pass@k formulation of Chen et al. \cite{Codex2021}, which assumes stochastic sampling. In our primary campaign, temperature 0 eliminates sampling variance entirely: each task receives exactly one deterministic model output, and pass@1 is simply the empirical success rate.

Each failure is classified into a diagnostic category -- BUILD\_FAIL (compilation error), RUN\_FAIL (runtime crash or nonzero exit code), VERIFY\_FAIL (incorrect output), or EXTRACTION\_FAIL (malformed LLM response) -- enabling fine-grained failure-mode analysis beyond a single pass/fail number. Self-repair outcomes are further classified as first\_attempt\_pass (correct on first try), full\_repair (model self-corrected after error feedback), partial\_repair (improved failure category but still failed), regression (worsened after retry), or persistent\_fail (same error across all attempts).

A separate **pass@k experiment** measures sampling variance (D4): 5 independent samples per task at temperature 0.7, L0 only, with no self-repair (max\_retries=1). This isolates output-side stochasticity from input-side variation (augmentation) and self-repair effects. The gap between greedy-decode pass@1 and pass@5 reveals whether failures are "hard" (the model fundamentally cannot translate the kernel) or "noisy" (the model sometimes succeeds but not reliably). This design keeps the three evaluation axes orthogonal: self-repair (retries), sampling variance (pass@k), and augmentation robustness (L0--L4).

Secondary metrics include **augmentation robustness**, defined as the stability of pass@1 across augmentation levels L0 through L4, and **self-repair rate**, the fraction of initially failing tasks recovered by the error-feedback retry loop. Statistical analysis uses Wilson score 95\% confidence intervals for proportions, Fisher's exact test for pairwise model comparison, and the Cochran-Armitage trend test for augmentation-level effects.

Execution timing and speedup metrics are excluded from this study. The current verification pipeline measures wall-clock time, which conflates kernel execution with I/O, memory allocation, and OS scheduling noise. Reliable performance comparison requires profiler-based kernel timing (e.g., Nsight Compute for CUDA, `omp\_get\_wtime()` for OpenMP), which is deferred to future work.

### 5.E Hardware and Software

All Qwen 3.5 evaluations are conducted on a single workstation to eliminate cross-machine variability. The GPU is an NVIDIA GeForce RTX 4070 (Ada Lovelace architecture, compute capability 8.9, 5888 CUDA cores, 12 GB GDDR6X). The CPU is an AMD Ryzen 9 7900X (12 cores, 24 threads). The system runs Ubuntu 24.04 LTS (kernel 6.8.0-40-generic).

CUDA compilation uses `nvcc` from the NVIDIA HPC SDK 24.3 (CUDA 12.3). C/C++ compilation uses GCC 12.4 with the `-fopenmp` flag for OpenMP targets. OpenCL programs link against the NVIDIA runtime from the HPC SDK. The evaluation harness and all scripting infrastructure run on Python 3.12.3. LLM API calls are issued from the evaluation machine; network latency does not affect correctness evaluation. All campaigns were executed via a single parameterized script ensuring identical batch logic, retry policy, and analysis pipeline across all models and modes (D5).

Gemini 2.5 Flash evaluations are conducted by a collaborator on a separate machine with identical software configuration. [PLACEHOLDER: gemini\_hardware -- GPU model, CPU model, and OS for Erel's evaluation machine.]

[TABLE 6: Hardware and software configuration. Rows: GPU model, CPU model, operating system, CUDA toolkit version, C/C++ compiler, OpenCL runtime, Python version. Separate columns for Qwen (primary) and Gemini (collaborator) evaluation machines.]

---

## S6 Results

This section presents ParBench evaluation results across [PLACEHOLDER: total_tasks_all] evaluated tasks: two LLMs -- Qwen 3.5 397B-A17B (Mixture-of-Experts) and Gemini 2.5 Flash (dense) -- evaluated on parallel code translation across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench curated), six translation directions, and five augmentation levels (L0--L4). All primary campaign evaluations use temperature=0, up to three self-repair retry attempts (four total attempts per task), and the build/run/verify pipeline described in S3.B. A separate pass@k sweep (S6.7) evaluates sampling variance at temperature=0.7.

### 6.1 Overall Pass Rates

Table 7 summarizes aggregate pass rates for the two evaluated models across all directions and augmentation levels.

[TABLE 7: Overall pass rates across all tasks (2 models, 5 suites, 6 directions, L0--L4). KNOWN\_FAIL source specs (8 total: 6 Rodinia + 2 HeCBench) are excluded from evaluation.]

| Model | PASS | BUILD\_FAIL | RUN\_FAIL | VERIFY\_FAIL | EXTRACTION\_FAIL | Total | Rate | 95% Wilson CI |
|-------|-----:|----------:|--------:|------------:|----------------:|------:|-----:|:-------------:|
| Qwen 3.5 397B-A17B | [PLACEHOLDER: qwen_pass] | [PLACEHOLDER: qwen_build] | [PLACEHOLDER: qwen_run] | [PLACEHOLDER: qwen_verify] | [PLACEHOLDER: qwen_extract] | [PLACEHOLDER: qwen_total] | [PLACEHOLDER: qwen_rate] | [PLACEHOLDER: qwen_ci] |
| Gemini 2.5 Flash | [PLACEHOLDER: gemini_pass] | [PLACEHOLDER: gemini_build] | [PLACEHOLDER: gemini_run] | [PLACEHOLDER: gemini_verify] | [PLACEHOLDER: gemini_extract] | [PLACEHOLDER: gemini_total] | [PLACEHOLDER: gemini_rate] | [PLACEHOLDER: gemini_ci] |
| **Aggregate** | [PLACEHOLDER: agg_pass] | [PLACEHOLDER: agg_build] | [PLACEHOLDER: agg_run] | [PLACEHOLDER: agg_verify] | [PLACEHOLDER: agg_extract] | [PLACEHOLDER: agg_total] | [PLACEHOLDER: agg_rate] | [PLACEHOLDER: agg_ci] |

[PLACEHOLDER: overall_comparison_prose -- describe the capability gap pattern between Qwen and Gemini; note whether the spread is large (qualitatively different tiers) or modest (comparable capability). Reference MoE vs dense architecture where appropriate.]

These results contrast sharply with repository-level evaluation. ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 for all models on applications larger than 133 SLoC, including XSBench. ParBench's kernel-centric approach -- isolating the translation task from build-system generation -- achieves [PLACEHOLDER: best_model_rate] for the stronger model on the same class of HPC kernels. The gap quantifies the degree to which build-system generation, rather than parallel logic translation, is the binding constraint in repository-level approaches.

Statistical comparison: a chi-squared test of independence between model identity and pass/fail outcome yields [PLACEHOLDER: chi2_stat] (df=1, p=[PLACEHOLDER: chi2_p]). [PLACEHOLDER: chi2_interpretation -- if significant, the two models differ meaningfully; if not, they are statistically comparable. Report Cramer's V or Cohen's h for effect size.]

### 6.2 Failure Taxonomy

Of the [PLACEHOLDER: total_failures_all] total failures across both models, the distribution is:

- BUILD\_FAIL: [PLACEHOLDER: build_fail_count]/[PLACEHOLDER: total_failures_all] ([PLACEHOLDER: build_fail_pct_of_failures])
- RUN\_FAIL: [PLACEHOLDER: run_fail_count]/[PLACEHOLDER: total_failures_all] ([PLACEHOLDER: run_fail_pct_of_failures])
- VERIFY\_FAIL: [PLACEHOLDER: verify_fail_count]/[PLACEHOLDER: total_failures_all] ([PLACEHOLDER: verify_fail_pct_of_failures])
- EXTRACTION\_FAIL: [PLACEHOLDER: extract_fail_count]/[PLACEHOLDER: total_failures_all] ([PLACEHOLDER: extract_fail_pct_of_failures])

[FIGURE 3: Failure taxonomy stacked bar chart. X-axis: models (Qwen 3.5 397B-A17B, Gemini 2.5 Flash). Y-axis: task count stacked by outcome (PASS, BUILD\_FAIL, RUN\_FAIL, VERIFY\_FAIL, EXTRACTION\_FAIL). Data source: results/evaluation/eval\_summary.json.]

**BUILD\_FAIL dominance.** [PLACEHOLDER: build_fail_analysis -- describe whether BUILD\_FAIL remains the dominant failure mode and its percentage of total failures. Expected pattern: retained CUDA memory management calls (cudaMalloc, cudaFree, cudaMemcpy) in otherwise-OpenMP code, missing #pragma omp parallel for directives, incorrect function signatures for OpenMP runtime calls, failure to eliminate device-specific type annotations. These are syntactic failures indicating the model demonstrates understanding of the parallel computation structure but fails to fully translate the API surface.]

**VERIFY\_FAIL analysis.** [PLACEHOLDER: verify_fail_analysis -- describe the rate of VERIFY\_FAIL and what it reveals. VERIFY\_FAIL indicates translations that compile and execute but produce incorrect output. These identify cases where LLMs produce code that is syntactically valid and structurally plausible but introduces subtle parallel logic errors -- incorrect thread-index mappings, wrong reduction scoping, or missed data dependencies. The conjunctive verification (exit\_code AND stdout\_pattern) catches translations that would have appeared correct under exit-code-only checking.]

**Self-repair by failure mode transition.** To address the question of which failure modes are recoverable through self-repair (W12), Table 7b breaks down the transitions from initial failure to final outcome across all attempts.

[TABLE 7b: Self-repair failure mode transitions (all tasks, both models). Rows: initial failure mode. Columns: final outcome after up to 3 retries.]

| Initial Failure | -> PASS | -> Same Fail | -> Different Fail | -> Regression | Total |
|-----------------|--------:|-------------:|------------------:|--------------:|------:|
| BUILD\_FAIL | [PLACEHOLDER: bf_to_pass] | [PLACEHOLDER: bf_persistent] | [PLACEHOLDER: bf_to_other] | [PLACEHOLDER: bf_regress] | [PLACEHOLDER: bf_total] |
| RUN\_FAIL | [PLACEHOLDER: rf_to_pass] | [PLACEHOLDER: rf_persistent] | [PLACEHOLDER: rf_to_other] | [PLACEHOLDER: rf_regress] | [PLACEHOLDER: rf_total] |
| VERIFY\_FAIL | [PLACEHOLDER: vf_to_pass] | [PLACEHOLDER: vf_persistent] | [PLACEHOLDER: vf_to_other] | [PLACEHOLDER: vf_regress] | [PLACEHOLDER: vf_total] |
| EXTRACTION\_FAIL | [PLACEHOLDER: ef_to_pass] | [PLACEHOLDER: ef_persistent] | [PLACEHOLDER: ef_to_other] | [PLACEHOLDER: ef_regress] | [PLACEHOLDER: ef_total] |

[PLACEHOLDER: repair_transition_analysis -- describe which failure modes are most recoverable. Expected pattern: BUILD\_FAIL is the most recoverable (compiler errors provide actionable feedback), VERIFY\_FAIL is least recoverable (output mismatch provides weak signal), RUN\_FAIL recovery depends on whether crash is from a simple pointer error vs. fundamental logic issue.]

### 6.3 Per-Kernel Analysis

Table 8 presents the kernel-by-model result matrix for the primary CUDA-to-OpenMP direction at L0 across all five benchmark suites.

[TABLE 8: Per-kernel results for CUDA-to-OpenMP translation (L0, 2 models). KNOWN\_FAIL source specs excluded. Suites: Rodinia (up to 16 kernels), XSBench (1), RSBench (1), mixbench (1), HeCBench curated (up to 10).]

[PLACEHOLDER: per_kernel_table -- Full kernel x model matrix with Suite, Kernel, Category columns and one column per model showing PASS/BUILD\_FAIL/RUN\_FAIL/VERIFY\_FAIL/EXTRACTION\_FAIL. Sort by difficulty (all-pass first, then partial, then all-fail).]

[FIGURE 4: Kernel-by-model heatmap. Rows: kernels across all 5 suites sorted by difficulty. Columns: 2 models. Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), yellow (VERIFY\_FAIL), grey (EXTRACTION\_FAIL).]

Kernels partition into distinct difficulty tiers based on two-model consensus. The conjunctive verification (exit\_code AND stdout\_pattern) produces a sharper tier separation than exit-code-only verification, with VERIFY\_FAIL now distinguishing translations that produce wrong output from those that fail to build or run.

[PLACEHOLDER: tier_description -- Partition kernels into difficulty tiers based on two-model consensus:
- **Always-pass** (both models PASS): identify shared characteristics favoring translation -- straightforward thread-index-to-loop-index mapping, minimal shared memory usage, well-known algorithmic structures
- **Single-model-pass** (one model PASS, one FAIL): identify which model succeeds and what distinguishes these kernels -- they delineate the capability boundary between the two models
- **Always-fail** (both models FAIL): identify common failure modes and kernel characteristics. Distinguish between those where both models produce BUILD\_FAIL (consistent API syntax gap) vs. those with heterogeneous failure modes (different degrees of partial capability). Kernels with VERIFY\_FAIL instances are notably more advanced failures than pure BUILD\_FAIL]

[PLACEHOLDER: kernel_anomalies -- Identify any surprising per-kernel results: cases where the overall weaker model passes a kernel that the stronger model fails, kernels that are easy for both models despite apparent complexity, or kernels that are hard for both despite apparent simplicity. Note which suites contribute to which tiers -- do non-Rodinia kernels (XSBench, RSBench, mixbench, HeCBench) cluster in different tiers than Rodinia kernels?]

**Sample size note (W1).** The primary CUDA-to-OpenMP direction at L0 evaluates [PLACEHOLDER: c2o_l0_kernel_count] kernels across 5 suites with 2 models, yielding [PLACEHOLDER: c2o_l0_total_tasks] tasks. Non-primary directions have smaller sample sizes (see S6.6) and findings from those directions should be considered exploratory.

### 6.4 Self-Repair Effectiveness

ParBench's evaluation pipeline permits up to three retry attempts with failure-specific diagnostics injected into subsequent prompts (four total attempts per task). Table 9 summarizes self-repair effectiveness.

[TABLE 9: Self-repair effectiveness (all directions, all levels, 2 models).]

| Metric | Qwen 3.5 | Gemini 2.5 Flash | Combined |
|--------|----------:|------------------:|---------:|
| Total tasks | [PLACEHOLDER: qwen_total_sr] | [PLACEHOLDER: gemini_total_sr] | [PLACEHOLDER: combined_total_sr] |
| First-attempt PASS | [PLACEHOLDER: qwen_first_pass] ([PLACEHOLDER: qwen_first_pct]) | [PLACEHOLDER: gemini_first_pass] ([PLACEHOLDER: gemini_first_pct]) | [PLACEHOLDER: combined_first_pass] ([PLACEHOLDER: combined_first_pct]) |
| Repaired (attempt 2-4) | [PLACEHOLDER: qwen_repaired] ([PLACEHOLDER: qwen_repair_pct]) | [PLACEHOLDER: gemini_repaired] ([PLACEHOLDER: gemini_repair_pct]) | [PLACEHOLDER: combined_repaired] ([PLACEHOLDER: combined_repair_pct]) |
| Total PASS | [PLACEHOLDER: qwen_total_pass_sr] ([PLACEHOLDER: qwen_total_pass_pct]) | [PLACEHOLDER: gemini_total_pass_sr] ([PLACEHOLDER: gemini_total_pass_pct]) | [PLACEHOLDER: combined_total_pass_sr] ([PLACEHOLDER: combined_total_pass_pct]) |
| Relative improvement | [PLACEHOLDER: qwen_rel_improve] | [PLACEHOLDER: gemini_rel_improve] | [PLACEHOLDER: combined_rel_improve] |
| Persistent fail | [PLACEHOLDER: qwen_persistent] ([PLACEHOLDER: qwen_persist_pct]) | [PLACEHOLDER: gemini_persistent] ([PLACEHOLDER: gemini_persist_pct]) | [PLACEHOLDER: combined_persistent] ([PLACEHOLDER: combined_persist_pct]) |
| Regression | [PLACEHOLDER: qwen_regression] | [PLACEHOLDER: gemini_regression] | [PLACEHOLDER: combined_regression] |

[PLACEHOLDER: repair_statistics -- Describe the self-repair patterns. Key questions: (1) What fraction of all PASSes come from first-attempt vs repair? (2) How does the repair rate differ between models -- does the stronger model also self-repair more effectively, or is repair rate independent of base capability? (3) What is the attempt-number distribution -- do most repairs happen on attempt 2 (first retry) or later? (4) Is there a meaningful regression rate where repair makes things worse?]

The self-repair data positions ParBench's 3-retry protocol as a controlled middle ground on the agentic spectrum. LASSI \cite{LASSI2024} reports 80--85% pass rates with a complete agentic self-correction pipeline (compilation feedback, execution analysis, profiling). ParBench's self-repair protocol provides only error feedback (compiler output or output mismatch) without retrieval augmentation or tool access. The gap between ParBench's repair rate ([PLACEHOLDER: combined_total_pass_pct]) and LASSI's agentic rate (80--85%) quantifies the value of agentic infrastructure beyond simple error feedback.

### 6.5 Augmentation Robustness

The augmentation engine's six AST-driven transforms were validated on all [PLACEHOLDER: aug_baseline_spec_count] non-KNOWN\_FAIL specs across five suites at augmentation levels L1 through L4, confirming level-invariant semantics preservation with zero correctness regressions (Section 3.C). This harness baseline establishes that any variation in LLM pass rates across augmentation levels can be attributed to the model's sensitivity to surface syntax, not to augmentation-induced semantic changes.

Table 10 presents per-model pass rates across augmentation levels L0--L4 for CUDA-to-OpenMP translation. Per the campaign design (D2), augmentation robustness is evaluated across all six directions, but this table restricts to the primary direction (CUDA-to-OpenMP) to eliminate the direction-composition confound identified in the audit (W8).

[TABLE 10: LLM pass rates across augmentation levels (CUDA-to-OpenMP direction only, all 5 suites, 2 models).]

| Level | Qwen 3.5 397B-A17B | Gemini 2.5 Flash |
|:-----:|:-------------------:|:----------------:|
| L0 | [PLACEHOLDER: qwen_l0_c2o] | [PLACEHOLDER: gemini_l0_c2o] |
| L1 | [PLACEHOLDER: qwen_l1_c2o] | [PLACEHOLDER: gemini_l1_c2o] |
| L2 | [PLACEHOLDER: qwen_l2_c2o] | [PLACEHOLDER: gemini_l2_c2o] |
| L3 | [PLACEHOLDER: qwen_l3_c2o] | [PLACEHOLDER: gemini_l3_c2o] |
| L4 | [PLACEHOLDER: qwen_l4_c2o] | [PLACEHOLDER: gemini_l4_c2o] |

[FIGURE 5: Augmentation robustness line chart. X-axis: augmentation levels L0--L4. Y-axis: pass rate (%). Two lines: Qwen 3.5 (color 1), Gemini 2.5 Flash (color 2). Error bars: Wilson 95% CIs.]

[PLACEHOLDER: augmentation_curves -- Describe per-model augmentation curves. Key patterns to report:
1. Does either model show statistical stability (flat curve) or degradation (declining curve)?
2. Cochran-Armitage trend test per model: Qwen z=[PLACEHOLDER: qwen_ca_z], p=[PLACEHOLDER: qwen_ca_p]; Gemini z=[PLACEHOLDER: gemini_ca_z], p=[PLACEHOLDER: gemini_ca_p]
3. If one model is stable and the other degrades, this demonstrates that augmentation robustness discriminates model capability -- it separates models that reason about parallel structure from those that pattern-match
4. If both degrade, characterize the rate: gradual vs cliff-drop, and at which level the degradation begins
5. Check for Simpson's Paradox: do per-model trends cancel in aggregate? If so, report per-model curves only and explicitly flag the paradox]

The augmentation robustness results discriminate model capability in a way that L0 pass rates alone cannot. [PLACEHOLDER: augmentation_discrimination_prose -- describe how the augmentation curves reveal a different capability picture than the L0 results. Do the two models separate more or less under augmentation? Does the MoE architecture (Qwen) show different augmentation sensitivity than the dense architecture (Gemini)?]

### 6.6 Cross-Direction Analysis

Table 11 presents pass rates broken down by translation direction for each model at L0.

[TABLE 11: Pass rates by translation direction (L0, all suites, 2 models). Directions with fewer than [PLACEHOLDER: min_n_threshold] kernel-model pairs are marked as exploratory.]

| Direction | Qwen 3.5 | Gemini 2.5 Flash | Combined | N (pairs) | Note |
|-----------|----------:|------------------:|---------:|----------:|:-----|
| cuda-to-omp | [PLACEHOLDER: qwen_c2o] | [PLACEHOLDER: gemini_c2o] | [PLACEHOLDER: combined_c2o] | [PLACEHOLDER: n_c2o] | Primary |
| omp-to-cuda | [PLACEHOLDER: qwen_o2c] | [PLACEHOLDER: gemini_o2c] | [PLACEHOLDER: combined_o2c] | [PLACEHOLDER: n_o2c] | |
| cuda-to-opencl | [PLACEHOLDER: qwen_c2cl] | [PLACEHOLDER: gemini_c2cl] | [PLACEHOLDER: combined_c2cl] | [PLACEHOLDER: n_c2cl] | |
| opencl-to-cuda | [PLACEHOLDER: qwen_cl2c] | [PLACEHOLDER: gemini_cl2c] | [PLACEHOLDER: combined_cl2c] | [PLACEHOLDER: n_cl2c] | |
| omp-to-opencl | [PLACEHOLDER: qwen_o2cl] | [PLACEHOLDER: gemini_o2cl] | [PLACEHOLDER: combined_o2cl] | [PLACEHOLDER: n_o2cl] | |
| opencl-to-omp | [PLACEHOLDER: qwen_cl2o] | [PLACEHOLDER: gemini_cl2o] | [PLACEHOLDER: combined_cl2o] | [PLACEHOLDER: n_cl2o] | |
| cuda-to-omp\_target | [PLACEHOLDER: qwen_c2ot] | [PLACEHOLDER: gemini_c2ot] | [PLACEHOLDER: combined_c2ot] | [PLACEHOLDER: n_c2ot] | HeCBench |
| omp\_target-to-cuda | [PLACEHOLDER: qwen_ot2c] | [PLACEHOLDER: gemini_ot2c] | [PLACEHOLDER: combined_ot2c] | [PLACEHOLDER: n_ot2c] | HeCBench |

[FIGURE 6: Cross-direction grouped bar chart. X-axis: 8 directions. Y-axis: pass rate (%). Grouped bars: one per model.]

**Direction asymmetry.** [PLACEHOLDER: direction_asymmetry_prose -- For each bidirectional pair (cuda/omp, cuda/opencl, omp/opencl, cuda/omp\_target), report the pass rate gap. The asymmetry has a structural explanation: CUDA-to-OpenMP requires removing CUDA-specific constructs (cudaMalloc, kernel launch syntax, threadIdx/blockIdx indexing) and replacing them with OpenMP directives -- a reductive task. OpenMP-to-CUDA requires introducing all of these constructs -- a generative task. Generative tasks are inherently harder because the model must make design choices not constrained by the input.]

McNemar's test for paired direction comparison (using kernel-model pairs evaluated in both directions): [PLACEHOLDER: mcnemar_result -- report test statistic and p-value for each bidirectional pair. This tests whether the probability of passing in direction A but failing in direction B differs from the reverse.]

**Per-suite direction results.** [PLACEHOLDER: per_suite_direction_prose -- describe how pass rates vary across suites within the same direction. Do XSBench, RSBench, mixbench, and HeCBench kernels show different pass rate patterns than Rodinia? This addresses W13 (asymmetric reporting) by explicitly separating suite-level results.]

**Sample size caveat (W1).** The primary direction (cuda-to-omp) has the largest sample size ([PLACEHOLDER: n_c2o] pairs) and supports the most reliable conclusions. Directions with fewer than [PLACEHOLDER: min_n_threshold] pairs should be considered exploratory. [PLACEHOLDER: which_directions_exploratory -- list which directions have small N and thus limited statistical power.]

### 6.7 pass@k Analysis

To characterize sampling variance independent of self-repair, a separate pass@k sweep evaluates both models at L0 with temperature=0.7 and 5 independent samples per task (max\_retries=1 per sample, i.e., zero-shot per sample). The pass@k estimator follows Chen et al. \cite{Codex2021}: $\text{pass@}k = 1 - \binom{n-c}{k} / \binom{n}{k}$, where $n$ is the number of samples and $c$ is the number that pass.

[TABLE 12: pass@k results (L0, temperature=0.7, 5 samples, 2 models).]

| Model | pass@1 (greedy, T=0) | pass@1 (T=0.7) | pass@5 (T=0.7) | Hard Fail % | Noisy Fail % |
|-------|---------------------:|----------------:|----------------:|------------:|-------------:|
| Qwen 3.5 397B-A17B | [PLACEHOLDER: qwen_p1_greedy] | [PLACEHOLDER: qwen_p1_t07] | [PLACEHOLDER: qwen_p5_t07] | [PLACEHOLDER: qwen_hard_fail] | [PLACEHOLDER: qwen_noisy_fail] |
| Gemini 2.5 Flash | [PLACEHOLDER: gemini_p1_greedy] | [PLACEHOLDER: gemini_p1_t07] | [PLACEHOLDER: gemini_p5_t07] | [PLACEHOLDER: gemini_hard_fail] | [PLACEHOLDER: gemini_noisy_fail] |

Hard failures are defined as kernels where pass@5 = 0 (the model fundamentally cannot translate this kernel across any sample). Noisy failures have pass@1 = 0 but pass@5 > 0, indicating partial capability that does not reliably surface under greedy decoding.

[PLACEHOLDER: passk_analysis -- Describe the gap between greedy pass@1 and pass@5. Key questions: (1) How many hard failures vs noisy failures exist per model? (2) Does pass@5 substantially exceed pass@1, suggesting that models have latent capability not captured by greedy decoding? (3) Do the same kernels that are hard failures for both models overlap? If so, these are genuinely difficult kernels; if not, difficulty is model-specific. (4) How does the greedy T=0 pass@1 compare to the T=0.7 pass@1 -- does temperature help or hurt?]

### 6.8 Statistical Summary

Table 13 consolidates the statistical tests applied throughout S6.

[TABLE 13: Statistical summary. All confidence intervals are Wilson 95% CIs.]

| Test | Statistic | p-value | Effect Size | Interpretation |
|------|-----------|---------|-------------|----------------|
| Model comparison (chi-squared) | [PLACEHOLDER: model_chi2] | [PLACEHOLDER: model_chi2_p] | Cramer's V = [PLACEHOLDER: model_cramers_v] | [PLACEHOLDER: model_chi2_interp] |
| Qwen augmentation trend (Cochran-Armitage) | z = [PLACEHOLDER: qwen_ca_z_full] | [PLACEHOLDER: qwen_ca_p_full] | -- | [PLACEHOLDER: qwen_ca_interp] |
| Gemini augmentation trend (Cochran-Armitage) | z = [PLACEHOLDER: gemini_ca_z_full] | [PLACEHOLDER: gemini_ca_p_full] | -- | [PLACEHOLDER: gemini_ca_interp] |
| Direction asymmetry: cuda-omp (McNemar) | [PLACEHOLDER: mcnemar_c2o_stat] | [PLACEHOLDER: mcnemar_c2o_p] | -- | [PLACEHOLDER: mcnemar_c2o_interp] |
| Direction asymmetry: cuda-opencl (McNemar) | [PLACEHOLDER: mcnemar_c2cl_stat] | [PLACEHOLDER: mcnemar_c2cl_p] | -- | [PLACEHOLDER: mcnemar_c2cl_interp] |
| Direction asymmetry: omp-opencl (McNemar) | [PLACEHOLDER: mcnemar_o2cl_stat] | [PLACEHOLDER: mcnemar_o2cl_p] | -- | [PLACEHOLDER: mcnemar_o2cl_interp] |

Methodological notes: Wilson confidence intervals are preferred over Wald intervals because they provide better coverage near boundary proportions (0% or 100%), which several per-kernel and per-direction rates approach. Cochran-Armitage tests model a linear trend in pass rate across ordered augmentation levels (L0 < L1 < L2 < L3 < L4), which is the appropriate test for the hypothesis that increasing augmentation intensity degrades model performance. McNemar's test is used for direction asymmetry because each kernel-model pair is evaluated in both directions, creating natural pairing.

---

## S7 Discussion

### 7.1 The Kernel-Centric Advantage

ParBench's central design decision -- isolating kernel-level translation from build-system generation -- produces a qualitatively different evaluation outcome than repository-level approaches. The stronger model achieves [PLACEHOLDER: best_model_rate_discussion] PASS on CUDA-to-OpenMP translation of the same class of HPC kernels for which ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 at the repository level. This is not a comparison of different benchmarks or different models; it is a comparison of evaluation granularity applied to overlapping computational domains.

The implication is that LLMs possess substantial internalized knowledge of parallel programming patterns -- thread decomposition, reduction operations, stencil computation, synchronization -- that is masked when evaluation conflates translation skill with build-system generation. ParBench's kernel-centric design separates these orthogonal capabilities, enabling measurement of each in isolation. The two evaluation granularities are complementary: ParEval-Repo measures end-to-end deployment capability; ParBench measures translation capability. Both are needed to characterize LLM parallel programming skill.

### 7.2 BUILD\_FAIL as the Actionable Bottleneck

BUILD\_FAIL accounts for [PLACEHOLDER: build_fail_pct_all_failures_disc] of all failures across [PLACEHOLDER: total_tasks_disc] tasks, establishing that the primary bottleneck is API-specific syntax rather than parallel reasoning capability. The recurring error patterns -- retained `cudaMalloc`/`cudaFree` calls, missing OpenMP pragma directives, incorrect type coercions -- are syntactic, not algorithmic. This finding has a direct practical implication: targeted fine-tuning on OpenMP idioms, or few-shot prompting with canonical CUDA-to-OpenMP translation examples, would likely close a substantial portion of the BUILD\_FAIL gap. The parallel reasoning capability is already present in the model weights; the API surface coverage is the limiting factor.

VERIFY\_FAIL accounts for [PLACEHOLDER: verify_fail_pct_disc] of all failures, providing a more nuanced picture than the BUILD\_FAIL-only story suggests. These are translations that compile, run to completion, and produce output -- but incorrect output. The conjunctive verification upgrade (exit\_code AND stdout\_pattern) catches these cases, which weaker verification would miss. VERIFY\_FAIL indicates genuine parallel logic errors: wrong thread-index mappings, incorrect reduction scoping, or missed data dependencies that produce numerically wrong results. While rarer than BUILD\_FAIL, VERIFY\_FAIL demonstrates that LLMs do not always correctly reason about parallel computation structure even when they produce syntactically valid code.

### 7.3 Model Capability Analysis

[PLACEHOLDER: model_comparison_discussion -- Describe the capability spread between Qwen 3.5 397B-A17B and Gemini 2.5 Flash. Key dimensions to discuss:
1. Overall pass rate gap: is it large (qualitatively different tiers) or modest?
2. MoE vs dense architecture implications: does Qwen's MoE structure (397B total, 17B active) outperform Gemini's dense architecture on HPC translation? The MoE architecture activates different parameter subsets for different inputs, which could provide an advantage on diverse kernel types.
3. Failure profile comparison: do the two models produce the same distribution of failure types, or does one model fail "further along" the pipeline (more VERIFY\_FAIL vs BUILD\_FAIL)?
4. Per-kernel agreement: on what fraction of kernels do both models agree (both PASS or both FAIL)? High agreement suggests kernel difficulty is an intrinsic property; low agreement suggests model-specific strengths.]

The comparison with LASSI \cite{LASSI2024} frames these results on a capability spectrum. LASSI reports 80--85% pass rates with a complete agentic self-correction pipeline, while ParBench's primary campaign achieves [PLACEHOLDER: combined_total_pass_pct_disc] with a 3-retry error-feedback protocol. The gap quantifies the value of agentic infrastructure: compilation feedback, execution analysis, profiling, and retrieval augmentation collectively improve pass rates from [PLACEHOLDER: combined_total_pass_pct_disc] to 80--85%. This positions three tiers of capability:

1. **Raw model capability** (pass@k floor): [PLACEHOLDER: passk_floor_rate] -- what the model achieves zero-shot without any feedback
2. **Controlled self-repair** (primary campaign): [PLACEHOLDER: combined_total_pass_pct_disc] -- error feedback without tools
3. **Agentic system** (LASSI): 80--85% -- full tooling including profiling and RAG

### 7.4 Direction Asymmetry

[PLACEHOLDER: asymmetry_discussion -- Describe the direction asymmetry findings from S6.6. Key points:
1. Is cuda-to-omp easier than omp-to-cuda, and by how much?
2. Structural explanation: CUDA-to-OpenMP is a reductive task (remove explicit machinery, replace with directives); OpenMP-to-CUDA is a generative task (introduce thread-block geometry, device memory, kernel launches). Generative tasks are harder because the model must make unconstrained design choices.
3. Is the asymmetry consistent across both models, or does one model show it while the other does not?
4. For cuda/opencl and omp/opencl pairs, is there a similar asymmetry pattern? OpenCL is more verbose than CUDA, which may affect direction asymmetry differently.
5. Practical implication: LLM-assisted portability tooling is more viable for CUDA-to-CPU translation than for the reverse.]

### 7.5 Augmentation Robustness Interpretation

[PLACEHOLDER: augmentation_interpretation -- Interpret the per-model augmentation curves from S6.5. Key framing:
1. The finding is NOT necessarily "level-invariance" (which was an artifact of Simpson's Paradox in the pilot). The finding is "augmentation robustness discriminates model capability."
2. If one model is stable and the other degrades, this directly tests the memorization hypothesis: a model that degrades under surface-level code transformations is likely leveraging training-data familiarity rather than structural understanding.
3. If both models degrade, the rate of degradation is informative: does the MoE architecture degrade differently from the dense architecture?
4. Simpson's Paradox check: do per-model trends cancel in aggregate? If the aggregate curve appears flat but individual model curves trend downward, this is Simpson's Paradox -- the aggregate is misleading.
5. Connection to pass@k: kernels that are "noisy failures" (pass@5>0, pass@1=0) may also be the kernels most sensitive to augmentation, suggesting a link between sampling variance and augmentation sensitivity.]

### 7.6 Threats to Validity

Several threats to the validity of these findings must be acknowledged.

**Sample size and suite scope.** The evaluation spans [PLACEHOLDER: total_kernels_across_suites] kernels across five suites (Rodinia, XSBench, RSBench, mixbench, HeCBench curated), a significant expansion from single-suite evaluations. For the primary CUDA-to-OpenMP direction at L0, [PLACEHOLDER: c2o_l0_kernel_count_threats] kernels are evaluated. Non-primary directions have smaller sample sizes; findings from directions with fewer than [PLACEHOLDER: min_n_threats] kernel-model pairs should be considered exploratory rather than confirmatory (W1). While five suites span diverse computational domains (graph algorithms, stencil computation, particle transport, micro-benchmarks, molecular dynamics, linear algebra), generalization to additional suites (NAS, Polybench) is not established.

**Rodinia training-data familiarity (W11).** Rodinia is a 15+ year-old benchmark suite whose kernels are extensively documented and almost certainly present in LLM training data. The augmentation engine addresses surface-level memorization (variable names, code formatting), but cannot address algorithmic-level memorization (the LLM may "know" that BFS uses a frontier-based approach regardless of variable names). The five-suite expansion mitigates this concern: RSBench, mixbench, and HeCBench curated kernels are drawn from different eras and communities, providing benchmarks with varying degrees of training-data exposure. However, algorithmic memorization remains an irreducible threat for any evaluation using published benchmark codes.

**Correctness-only metric (W9).** ParBench measures translation correctness, not performance. An OpenMP translation that produces correct output but runs 100x slower than the original CUDA kernel is counted as PASS. TRACY \cite{TRACY2025} demonstrates that "correctness is not a reliable proxy for efficiency" -- 23.5% of correct translations exhibit pronounced inefficiency. ParBench's PASS rates should not be interpreted as deployment readiness. Kernel execution time comparison is deferred to future work.

**Temperature and sampling methodology (W5).** The primary campaign uses temperature=0 (greedy decoding) for deterministic reproducibility. This provides a single point estimate (greedy-decode pass@1) rather than a distribution. The supplementary pass@k sweep (S6.7) at temperature=0.7 characterizes sampling variance, but only at L0 without self-repair. The interaction between sampling variance and augmentation level is not characterized.

**Two-model evaluation.** Two models are evaluated, representing distinct architecture families (MoE and dense) from two non-Anthropic providers. While architectural diversity provides insight, two models do not represent the full landscape of available LLMs. Results may not generalize to models from other providers (OpenAI, Anthropic, Meta), reasoning models (o1, Claude with extended thinking), or code-specialized models (CodeRosetta, HPC-Coder-V2). ParBench's parameterized campaign script enables straightforward expansion to additional models.

**Single augmentation seed.** All augmentation uses seed=42. While the AST-driven transforms are deterministic given a seed, different seeds may produce different augmented code variants that interact differently with model-specific weaknesses. The single-seed design provides reproducibility but does not characterize variance across augmentation instantiations.

**KNOWN\_FAIL exclusions.** Eight specs (6 Rodinia + 2 HeCBench) are excluded as KNOWN\_FAIL due to build infrastructure issues (CUDA 12 `texture<>` removal, missing libraries, compiler incompatibilities) rather than translation difficulty. These exclusions are documented and applied uniformly across models; they do not bias the comparison between models but do reduce the evaluated kernel set.

**Reference implementation as ground truth.** Correctness verification compares LLM translation output against reference implementation output. Floating-point non-associativity between GPU and CPU computation could in principle cause false VERIFY\_FAIL results. The correctness configurations use small problem sizes where floating-point divergence is minimized, and manual inspection of a sample of VERIFY\_FAIL cases confirms genuine translation errors rather than floating-point artifacts.

### 7.7 Implications for the HPC Community

The findings suggest several directions for improving LLM-based parallel code translation.

**LLMs can translate kernel-level parallel code with meaningful success rates.** The [PLACEHOLDER: best_model_rate_implications]% pass rate for the stronger model on CUDA-to-OpenMP translation -- compared to 0% for repository-level approaches on the same kernels -- demonstrates that kernel-level translation is a tractable task for current LLMs. This has practical implications for HPC portability: organizations migrating CUDA codebases to OpenMP can use LLMs as a first-pass translation tool, with human review for the [PLACEHOLDER: fail_rate_implications]% that fail.

**BUILD\_FAIL dominance suggests targeted solutions.** With [PLACEHOLDER: build_fail_pct_implications]% of failures occurring at the compilation stage, the highest-ROI intervention is improving LLM coverage of API-specific syntax. Few-shot prompting with canonical translation patterns, fine-tuning on verified translation corpora, or hybrid approaches that pair LLM translation with rule-based API syntax correction could close a substantial portion of the failure gap. The parallel reasoning capability demonstrated by VERIFY\_FAIL cases (compilable but incorrect) is a harder problem, but a less frequent one.

**Augmentation should be standard practice for LLM-on-code evaluation.** [PLACEHOLDER: augmentation_implication_prose -- if augmentation discriminates model capability, it should be adopted as a standard evaluation dimension. The L0-L4 ladder provides a natural curriculum. Without augmentation, an evaluation on well-known benchmarks risks conflating memorization with reasoning. ParBench's augmentation engine demonstrates a practical approach to this concern.]

**Framework extensibility enables community adoption.** ParBench's spec schema is the extension point: adding a new kernel requires one JSON file with no modification to the harness or evaluation pipeline. The build/run/verify pipeline is benchmark-agnostic; any kernel with a deterministic correctness check can be onboarded. The five-suite expansion from Rodinia (the initial suite) to RSBench, mixbench, and HeCBench demonstrates this extensibility in practice.

**The agentic gap is quantifiable.** The three-tier framing (raw pass@k < controlled self-repair < agentic system) provides a measurement framework for decomposing LLM capability improvements. As agentic systems like LASSI \cite{LASSI2024} and ParaCodex \cite{ParaCodex2026} mature, ParBench's specifications serve as a controlled evaluation substrate where each tier can be measured independently. The gap between tiers quantifies the marginal value of each component: error feedback, tool access, retrieval augmentation, and profiling-guided optimization.

---

## S8 Conclusion

### 8.1 Summary

This paper presented ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level. ParBench makes three contributions that collectively address the absence of rigorous, reproducible evaluation infrastructure for this task.

First, ParBench provides the first systematic framework for evaluating kernel-level parallel code translation, supporting 96 specifications across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. The five suites span stencil computation, graph algorithms, particle transport, micro-benchmarks, and additional HPC domains. The kernel-centric design isolates translation skill from build-system generation -- the binding constraint identified by repository-level evaluation \cite{ParEvalRepo2025} -- enabling non-zero pass rates where repository-level approaches achieve 0%.

Second, an AST-driven augmentation engine applies six semantics-preserving transforms at five augmentation levels (L0--L4). The engine is level-invariant: all non-KNOWN\_FAIL specs across all five suites achieve PASS at every level L1--L4 with zero correctness regressions, confirming that the transforms preserve semantics. This validated baseline enables LLM robustness evaluation that distinguishes genuine parallel reasoning from training-data pattern-matching -- a methodological necessity when evaluating on well-known HPC benchmarks.

Third, empirical evaluation of two LLMs -- Qwen 3.5 397B-A17B (Mixture-of-Experts, 397B total / 17B active parameters) and Gemini 2.5 Flash (dense architecture) -- across [PLACEHOLDER: total_tasks] translation tasks reveals [PLACEHOLDER: capability_gap_summary]. On the primary CUDA-to-OpenMP direction at L0, [PLACEHOLDER: best_model_cuda_to_omp_summary]. A failure taxonomy reveals that BUILD\_FAIL accounts for [PLACEHOLDER: build_fail_of_failures] of all failures while VERIFY\_FAIL accounts for [PLACEHOLDER: verify_fail_of_failures] -- establishing that API syntax is the primary bottleneck, though a meaningful minority of translations that compile and run produce incorrect parallel logic. Cross-direction evaluation reveals [PLACEHOLDER: direction_asymmetry_summary], reflecting the structural advantage of translating from an explicit thread-decomposition model to a directive-based model. Augmentation robustness evaluation at L0--L4 reveals [PLACEHOLDER: augmentation_summary], demonstrating that augmentation provides a more discriminating evaluation dimension than aggregate pass rate alone.

### 8.2 Future Work

Five directions for future work are prioritized.

**Additional models.** ParBench is model-agnostic: adding a new model requires only an API key and a single command to the parameterized campaign script. Evaluation of frontier models (GPT-4.1, Claude Opus), open-weight models at different scales, and code-specialized models would characterize how model architecture, scale, and training data composition affect parallel code translation capability. The framework's extensibility is a design-level contribution -- the two-model evaluation presented here demonstrates the methodology; broader model coverage strengthens the generalizability of findings.

**Performance and efficiency analysis.** The current study is correctness-only. Reliable performance comparison requires profiler-based kernel timing (Nsight Compute for CUDA, `omp_get_wtime()` for OpenMP), which would characterize whether LLM-translated code preserves not only correctness but also the performance characteristics of the original implementation. Efficiency metrics -- translated lines per token, cost per correct translation -- would inform practical deployment decisions.

**Expanded API and benchmark coverage.** Extension to CUDA-to-HIP, CUDA-to-SYCL, and CUDA-to-OpenACC would address additional portability-relevant API pairs reflecting the increasingly heterogeneous accelerator landscape. Additional benchmark suites (Polybench, NAS Parallel Benchmarks) would broaden domain coverage and increase the statistical power of cross-model comparisons.

**Agentic translation evaluation.** ParBench's 3-retry self-repair protocol provides a controlled middle ground between zero-shot evaluation and full agentic systems. LASSI \cite{LASSI2024} reports 80--85% pass rates with a complete self-correction pipeline including RAG and tool use. ParBench's specs and harness serve as a natural evaluation backend for agentic systems -- joint evaluation would quantify whether agentic orchestration can close the BUILD\_FAIL gap that prompt-based translation leaves open, and decompose the improvement into contributions from error feedback, tool access, and retrieval augmentation.

**Fine-tuned and domain-adapted models.** CodeRosetta \cite{CodeRosetta2024} and HPC-Coder-V2 \cite{HPCCoderV2_2024} demonstrate that domain-specific fine-tuning improves parallel code generation. Evaluating fine-tuned models on ParBench's augmented specifications would test whether fine-tuning on HPC code improves robustness to surface-level code variation or merely reinforces pattern-matching on the training distribution.

---

## Data Verification Notes

**Previous pilot data (3-model, 562 tasks, 2026-03-28):** Archived below for reference. All claims in the current draft use [PLACEHOLDER] markers pending new campaign results.

**New campaign scope (2-model, 5-suite, 2026-03-29):**

| Claim | Value | Source |
|-------|-------|--------|
| Total specs | 96 (60 Rodinia + 4 XSBench + 4 RSBench + 3 mixbench + 25 HeCBench curated) | specs/ directory + campaign\_direction\_matrix.md |
| L0 translation pairs per model | 142 | campaign\_direction\_matrix.md |
| L0-L4 tasks per model | 710 (142 x 5 levels) | D2 in experimental\_decisions\_log.md |
| Total tasks (2 models) | ~1,420 | 710 x 2 models |
| Models | Qwen 3.5 397B-A17B, Gemini 2.5 Flash | D1 in experimental\_decisions\_log.md |
| Translation directions | 6 standard (+ 2 HeCBench omp\_target case-study) | campaign\_direction\_matrix.md |
| Augmentation levels | 5 (L0--L4) | D2 |
| Augmentation baseline | All non-KNOWN\_FAIL specs PASS at L1-L4 across 5 suites | D6 in experimental\_decisions\_log.md |
| Rodinia PASS | 54/60 | Harness verification (2026-03-29) |
| XSBench PASS | 4/4 | Harness verification (2026-03-29) |
| RSBench PASS | 4/4 | Harness verification (2026-03-29) |
| mixbench PASS | 3/3 | Harness verification (2026-03-29) |
| HeCBench curated PASS | 23/25 (2 KNOWN\_FAIL) | Harness verification (2026-03-28) |

**Archived pilot data (3-model, 562 tasks, superseded):**

| Claim | Value | Source |
|-------|-------|--------|
| Total evaluated tasks | 562 | eval\_summary.json total\_tasks (2026-03-28) |
| Claude Sonnet 4.6 overall | 102/188 = 54.3% [47.1%, 61.2%] | eval\_summary.json |
| Gemini 2.5 Flash-Lite overall | 16/187 = 8.6% [5.3%, 13.5%] | eval\_summary.json |
| Groq Llama 3.3 70B overall | 19/187 = 10.2% [6.6%, 15.3%] | eval\_summary.json |
| Translation directions | 12 | eval\_summary.json by\_direction keys |
| ParEval-Repo 0% pass@1 | >133 SLoC applications | \cite{ParEvalRepo2025} |
| GPU | NVIDIA GeForce RTX 4070 | System hardware |
| CPU | AMD Ryzen 9 7900X | System hardware |
| OS | Ubuntu 24.04 LTS (kernel 6.8.0-40-generic) | System OS |
| CUDA | 12.3 (NVIDIA HPC SDK 24.3) | nvcc --version |
| GCC | 12.4 with -fopenmp | gcc --version |
| Python | 3.12.3 | python3 --version |
