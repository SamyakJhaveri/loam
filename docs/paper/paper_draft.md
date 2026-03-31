# ParBench: Evaluating LLM Parallel Code Translation with Build-Run-Verify Correctness and Augmentation Robustness

**Alternative title:** ParBench: A Benchmark Framework for Evaluating LLM-Based Parallel Code Translation

**Venue:** SC26 -- Supercomputing 2026 (full technical paper)
**Format:** IEEE IEEEtran double-column, ~10 pages + appendices
**Status:** DRAFT -- S1--S8 structure complete; rewriting for 2-model 5-suite campaign (2026-03-29)
**Author:** \author{[Anonymous for Review]}

---

## Abstract

Large language models (LLMs) are increasingly applied to parallel code generation, yet no benchmark framework systematically evaluates their ability to *translate* parallel code across GPU programming APIs -- and prior approaches share a critical blind spot: benchmark codes widely known in the HPC community are also present in LLM training data, making it impossible to distinguish genuine parallel reasoning from memorized translations. We present **ParBench**, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level, with an integrated augmentation engine that systematically tests reliance on training-data pattern-matching. ParBench curates 96 benchmark specifications across five HPC benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. Evaluating two LLMs -- Qwen 3.5 397B-A17B (a 397-billion-parameter Mixture-of-Experts model) and Gemini 2.5 Flash -- across 1,420 translation tasks spanning 35 kernels, six directions, and five augmentation levels, we find [PENDING: capability gap description -- awaiting primary campaign results]: [PENDING: model1 name and overall rate with CI] while [PENDING: model2 name and overall rate with CI] ([PENDING: statistical comparison]). On the primary CUDA-to-OpenMP direction at L0, [PENDING: best model cuda-to-omp L0 description] -- compared to 0% in repository-level approaches \cite{ParEvalRepo2025}. BUILD\_FAIL accounts for [PENDING: build fail rate] of all tasks; VERIFY\_FAIL accounts for [PENDING: verify fail rate], indicating [PENDING: failure taxonomy interpretation]. An AST-driven augmentation engine applies six semantics-preserving transforms at five levels (L0--L4); 68 of 88 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench) PASS at every level L1--L4 with zero correctness regressions, confirming level-invariant semantics preservation. LLM augmentation robustness evaluation reveals [PENDING: augmentation trend description -- awaiting primary campaign results], providing evidence that augmentation robustness discriminates structural reasoning from surface pattern-matching. ParBench is publicly available as an extensible framework for the HPC community.

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

**Training data contamination -- the invisible gap.** A fourth gap cuts across all of the above: benchmark codes used in prior work are likely present in LLM training data, making it impossible to distinguish genuine parallel reasoning from memorized translations. Rodinia \cite{Rodinia2009}, XSBench, and similar proxy applications have been republished across hundreds of GitHub repositories. ParBench addresses this directly through an AST-driven augmentation engine that produces semantically equivalent but syntactically novel code variants, testing whether models reason about parallel structure or pattern-match from training data (Section 2.5, Section 3.C). Empirical results confirm the practical importance of this concern (Section 6.5).

**The gap in benchmark selection rationale.** A final dimension on which prior work is incomplete is the *why* of benchmark selection. Which parallel APIs matter most? Which kernels are representative? Existing frameworks do not answer these questions systematically. ParBench's selection is grounded in a comprehensive empirical survey of 35 open-source HPC repositories covering all major parallel programming models. That survey identified 472 CUDA-OpenMP kernel pairs across just 6 repositories -- the largest available translation opportunity in the ecosystem, and the practical bottleneck for real-world GPU-to-CPU portability work (Figure 2 visualizes API co-occurrence across surveyed repositories; Figure 3 illustrates how repository-level counting understates kernel-level translation opportunities by up to two orders of magnitude). The survey further identified which benchmark suites provide the same kernel implemented across multiple APIs (Rodinia, HeCBench, XSBench, RSBench, mixbench), which have automatable build/run/verify pipelines, and which have self-checking output patterns. The choice of CUDA-to-OpenMP as the primary translation direction, and of Rodinia as the primary evaluation substrate, follows directly from this survey -- not from convenience.

Together, these four gaps define the problem that ParBench is designed to solve: kernel-level evaluation granularity, build-infrastructure isolation, training-data robustness through augmentation, and survey-grounded benchmark selection.

### 1.3 Contributions

This paper presents ParBench and makes the following contributions:

1. **ParBench framework** -- The first build/run/verify benchmark framework for LLM-based parallel code translation at the kernel level, supporting 96 specifications across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. Kernel-centric translation mode isolates the translation skill from build-system generation, directly addressing the binding constraint identified by repository-level evaluation \cite{ParEvalRepo2025}.

2. **AST-driven augmentation engine** -- Six semantics-preserving source-level transforms at five augmentation levels (L0--L4) that systematically test whether LLMs reason about parallel structure or pattern-match from training data. Level-invariant: 68 of 88 non-KNOWN\_FAIL specs across five suites PASS at all levels L1--L4 with zero correctness regressions. LLM evaluation at L0--L4 measures augmentation robustness as a discriminator of genuine parallel reasoning versus surface pattern-matching.

3. **Empirical evaluation** -- Comparative analysis of two LLMs (Qwen 3.5 397B-A17B, Gemini 2.5 Flash) across 1,420 translation tasks spanning six directions and five augmentation levels, producing a failure taxonomy ([PENDING: build fail rate] BUILD\_FAIL, [PENDING: verify fail rate] VERIFY\_FAIL), per-kernel difficulty tiers, self-repair effectiveness measurement, augmentation robustness characterization with statistical independence testing, and a pass@k analysis at temperature 0.7 to separate deterministic failures from sampling-sensitive cases. The two models represent distinct architecture families (Mixture-of-Experts vs. dense) from different providers, testing whether architectural diversity produces divergent translation capabilities.

### 1.4 Key Findings Preview

ParBench produces several findings with immediate relevance for the HPC and LLM research communities:

**Kernel-centric isolation unlocks success.** [PENDING: best model name] achieves [PENDING: best model cuda-to-omp L0 rate] PASS on CUDA-to-OpenMP translation at L0 ([PENDING: kernel count] kernels across five suites), demonstrating that kernel-level evaluation reveals capability that repository-level approaches obscure. The gap quantifies the orthogonality of translation skill and build-system-generation skill.

**Capability gap and failure taxonomy.** [PENDING: model comparison description -- awaiting primary campaign results]. BUILD\_FAIL accounts for [PENDING: build fail rate] of all tasks, making it the dominant failure mode. VERIFY\_FAIL accounts for [PENDING: verify fail rate], indicating that [PENDING: verify fail interpretation]. The primary bottleneck remains API-specific syntax -- missing `#pragma omp` directives, retained CUDA memory management calls, wrong type annotations -- rather than an inability to reason about parallel computation.

**Augmentation robustness discriminates reasoning from pattern-matching.** [PENDING: augmentation overall trend description]. Per-model analysis reveals [PENDING: augmentation per-model description], providing evidence that augmentation robustness measures a dimension of capability distinct from aggregate pass rate.

**Direction asymmetry.** [PENDING: direction asymmetry description]. The trend suggests that removing CUDA-specific constructs (explicit thread indexing, device memory management) is generally easier for LLMs than introducing them from directive-based OpenMP source, reflecting the structural advantage of translating from a more explicit to a more abstract programming model.

**Self-repair effectiveness.** [PENDING: self-repair description]. The gap between first-attempt pass rate and final pass rate (after up to 3 retries with error feedback) quantifies the value of lightweight agentic error correction, directly comparable to the full agentic approaches evaluated by LASSI \cite{LASSI2024}.

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
| **ParBench (ours)** | **SC26** | **Kernel** | **Build+Run+Verify** | **Yes** | **Yes (L0--L4)** | **96 specs, 35 kernels, 5 suites, 6 dirs** |

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

ParBench's augmentation engine addresses this concern directly. Six AST-driven transforms --- variable and function renaming (ChangeNames, ChangeFunctionNames), condition branch swapping (SwapCondition), compound assignment expansion (ArithmeticTransform), typedef introduction (TypedefExpansion), and pointer-to-array index conversion (PointerArithmeticToArrayIndex) --- produce semantically equivalent but syntactically novel code at five intensity levels (L0--L4). Augmented inputs cannot appear verbatim in any training corpus. If a model's pass rate degrades under augmentation, that degradation quantifies the extent to which its baseline performance relied on memorization rather than understanding of parallel semantics. No other parallel code translation benchmark provides this capability.

### 2.6 Positioning ParBench

ParBench is, to our knowledge, the only framework that combines all of the following: (1) kernel-level granularity targeting real HPC benchmark suites, (2) conjunction verification (build + run + verify against reference output), (3) AST-driven augmentation for robustness testing, (4) multi-API evaluation across CUDA, OpenMP, and OpenCL with 6 translation directions, (5) multi-model evaluation of general-purpose LLMs, and (6) survey-grounded benchmark curation. No prior parallel code translation benchmark documents its selection rationale against a systematic survey of the available ecosystem. ParBench's curation is grounded in a 35-repository empirical survey that quantified kernel-level translation opportunities across all major parallel APIs (Section 4.A, Figures 2--4), ensuring that benchmark selection reflects the actual distribution of multi-API code in the HPC open-source ecosystem rather than researcher convenience. LASSI shares verification rigor but evaluates an agentic pipeline rather than raw model capability; CodeRosetta shares the HPC translation domain but relies on proxy metrics rather than functional correctness; ParEval and ParEval-Repo share the HPC evaluation focus but target generation and repository-level translation, respectively. ParBench's contribution is the evaluation *framework* --- a reusable, extensible measurement instrument for parallel code translation that can evaluate any model (general-purpose or fine-tuned) and any agentic pipeline against a common, augmentation-hardened standard.


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

**Verify stage.** The verifier applies the spec's verification strategies in declared order. For `exit_code` verification, the actual exit code is compared against the expected value. For `stdout_pattern` verification, a regular expression is applied to the captured stdout. The first strategy to produce a definitive PASS or FAIL terminates evaluation; if all strategies are exhausted without a conclusive result, the outcome is SKIP. In cross-API translation evaluation, the verification stage uses a combined pattern that accepts output matching either the source or target spec's stdout format (Section 3.D), preventing false negatives from format differences between API implementations.

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

The augmentation baseline confirms that the transforms are semantics-preserving: 68 of 88 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench) pass the build/run/verify pipeline at all levels L1--L4, with zero correctness regressions relative to L0. The 8 KNOWN\_FAIL specs (which fail at L0 due to CUDA 12 deprecations, missing system libraries, and pre-existing runtime errors) also fail identically at all augmented levels, confirming that augmentation introduces no new failures. Transform application frequency across 240 augmented tasks: SwapCondition (162), ArithmeticTransform (69), ChangeNames (55), TypedefExpansion (7), PointerArithmeticToArrayIndex (6), ChangeFunctionNames (2).

### 3.D Evaluation Pipeline: Kernel-Centric Translation

The evaluation pipeline orchestrates LLM-based parallel code translation through a structured prompt-response-verify cycle. Its design reflects a deliberate methodological choice: kernel-centric translation, in which only the parallel computation files are translated while the surrounding build infrastructure remains untouched.

**Kernel-centric methodology.** ParBench isolates the translation skill by feeding only the `translation_targets` files (the parallel kernel code) to the LLM; Makefiles, shared headers, serial baselines, and utility code remain unchanged in the target directory. This design enables evaluation of whether an LLM can correctly map parallel programming patterns from one API to another, independent of its ability to replicate project file organization. The rationale is that translation quality and code restructuring ability are orthogonal skills; conflating them produces artificially low pass rates that obscure the model's actual parallel programming competence.

**Prompt structure.** Each translation prompt consists of a system message establishing the role of a parallel programming expert and a user message containing: (1) the source kernel code with API-specific syntax highlighting, (2) the target API and the filenames the LLM must produce, (3) the target build command for compilation compatibility, and (4) read-only target infrastructure context (non-kernel files from the target directory) so the LLM can match expected function signatures and data structures. Source support headers are included with instructions to inline definitions rather than emit unresolvable `#include` directives.

**Cross-API argument and verification handling.** When translating between APIs (e.g., CUDA to OpenMP), the source and target implementations may expect different command-line arguments and produce different stdout formats. ParBench handles this asymmetry explicitly. For run arguments, the pipeline uses the *source* spec's arguments because LLMs preserve the source implementation's `argc`/`argv` parsing convention -- a translated binary retains the argument-handling logic of the code it was translated from, not the reference target implementation. For verification, the pipeline constructs a union of source and target `stdout_pattern` regexes via alternation (`source_pattern|target_pattern`), accommodating translations that produce either source-native or target-native output formats. This dual handling ensures that the evaluation measures translation quality rather than penalizing correct translations for superficial format differences.

**Kernel-only vs. full-program translation.** Not all cross-API translations require the LLM to rewrite the entire program. ParBench distinguishes *kernel-only* translations, where only the device kernel files are translated while the host code remains untouched, from *full-program* translations, where the LLM rewrites all source files including host-side API calls. The distinction arises naturally from API architecture: translations targeting OpenCL produce only `.cl` kernel files, because the OpenCL programming model separates kernel source (compiled at runtime via `clBuildProgram()`) from host orchestration code. In contrast, CUDA-to-OpenMP translations require rewriting the entire source file, replacing device kernels, memory management, and launch syntax with OpenMP pragmas and CPU-side equivalents. ParBench detects kernel-only translations automatically by checking whether all `translation_targets` in the target spec end with `.cl`. For kernel-only translations, the target spec's native run arguments and verification patterns are used directly (since the host binary is unchanged), whereas full-program translations use the cross-API argument and verification handling described above.

**False-positive detection for kernel-only translations.** Kernel-only translations introduce a subtle verification challenge: the host program may swallow kernel compilation errors and still produce expected output. For example, when translating CUDA to OpenCL, the host code catches a `clBuildProgram()` failure, prints an error-handling message that happens to match the expected stdout pattern, and exits with code 0 -- but the translated kernel never actually executed. To guard against such false positives, the verification pipeline includes a post-verification scan of stdout for OpenCL kernel build failure signatures. Translations that pass exit-code and stdout-pattern checks but contain evidence of kernel compilation failure are downgraded from PASS to VERIFY\_FAIL. This specificity filter reduces false positives with zero additional false negatives, since legitimate kernel executions do not produce `clBuildProgram()` error messages. Forensic analysis of early Qwen 3.5 cuda-to-opencl results (N=26) revealed a second class of false positive not caught by this guard: `clEnqueueReadBuffer` failures that occur *after* kernel compilation succeeds. In the `backprop` kernel, the host function `bpnn_train_kernel()` returns -1 on enqueue failure, but the caller in `facetrain.c` ignores this return value, prints the expected success message, and exits 0. The translated kernel never produces correct output, yet the task is classified as PASS. This gap -- where the `clBuildProgram()` guard catches compilation-stage false positives but not execution-stage false positives -- is being addressed with additional runtime error signature detection. The discovery illustrates the defense-in-depth challenge inherent in kernel-only evaluation: because the host binary is not rewritten by the LLM, any error path in the original host code that silently absorbs a failure becomes a potential false-positive vector.

**Self-repair loop.** On failure, the pipeline feeds failure-specific diagnostics back to the LLM: compiler errors on build failure, runtime errors and stderr on execution failure, and verification details on output mismatch. This feedback serves as a follow-up prompt, requesting a corrected translation. This iterative self-repair mechanism allows a configurable number of attempts before a final failure classification. The self-repair loop mirrors the realistic workflow of a developer iterating on errors; it also provides data on which failure modes are recoverable by the model versus those that indicate fundamental translation deficiencies.

**Complexity taxonomy.** To enable stratified analysis of translation difficulty, each source--target pair is classified into one of four complexity classes based on the file cardinality of the translation: `single_file` (1 source file to 1 target file), `multi_to_single` (N source files to 1 target file), `single_to_multi` (1 source file to N targets, characteristic of CUDA-to-OpenCL translations where the host-device split is inherent to the programming model), and `multi_to_multi` (N source files to M target files).

**Model-agnostic design.** The pipeline supports multiple LLM providers through a model registry that maps human-readable identifiers to provider-specific API configurations. All evaluations use temperature 0 for deterministic reproducibility. The framework currently supports Anthropic, OpenAI, Azure OpenAI, Google, Groq, and Together AI API endpoints, enabling cross-model comparison under identical prompt content and evaluation conditions.

---

## S4 Benchmark Curation

The benchmark corpus was assembled through a four-stage systematic process: surveying the landscape of open-source HPC benchmark repositories, quantifying kernel-level translation opportunities across parallel APIs, filtering candidate kernels through build/run/verify automation requirements, and verifying each selected kernel through the complete pipeline on the evaluation platform.

### 4.A Suite Selection

**Survey methodology.** We conducted a systematic survey of open-source HPC benchmark repositories, beginning with 40 candidate archives identified from the ECP proxy application catalog, published benchmark suites, and HPC conference proceedings. After excluding 5 repositories for download failures or insufficient documentation, 35 repositories were analyzed in detail. These span six benchmark types: suites (e.g., HeCBench \cite{HeCBench2023}, Rodinia \cite{Rodinia2009}, RAJAPerf, NAS NPB), mini-applications (e.g., BabelStream, CloverLeaf, LULESH, miniBUDE), proxy applications (e.g., SW4lite, CoMD, Kripke), full applications (e.g., LAMMPS, GROMACS), libraries (e.g., Kokkos Kernels, AMReX, MFEM), and microbenchmarks (e.g., STREAM, OSU OMB). Of the 35, 30 were classified Tier A (documented build, automated verification, active maintenance) and 5 as Tier B (partial verification or limited API coverage). Each repository was cataloged by the parallel APIs it provides, its kernel count, build system, and verification method.

**Repository-level vs. kernel-level counting.** A central finding of the survey is that repository-level counting dramatically understates the available benchmark material for translation evaluation. The API co-occurrence matrix (Figure 2) identifies 6 repositories containing both CUDA and OpenMP implementations. However, kernel-level analysis --- enumerating individual computational kernels that have verified equivalent implementations across APIs --- reveals 472 independent CUDA--OpenMP translation pairs across those same 6 repositories, a 79x multiplier (Figure 3). This extreme concentration is driven by large multi-kernel suites: HeCBench alone contributes 325 CUDA--OpenMP kernel pairs, RAJAPerf contributes 106, and Rodinia contributes 19. The same pattern holds across other API pairs: 633 CUDA--HIP kernel pairs (across 3 repositories, a 211x multiplier) and 616 CUDA--SYCL pairs (across 2 repositories, a 308x multiplier). This finding motivates a kernel-centric evaluation strategy in which benchmarks are evaluated at the granularity of individual computational kernels rather than entire repositories.

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

**Selection criteria.** Five criteria guided suite selection from the surveyed repositories:

1. **Multi-API kernel equivalence.** The repository must provide implementations of the *same* kernel in multiple parallel APIs within the same source tree, ensuring that translation pairs have authoritative reference implementations rather than independently developed programs.
2. **Build-run-verify automation.** Each kernel must be buildable, runnable, and verifiable without human intervention, using Makefiles or CMake, command-line arguments, and deterministic output.
3. **Self-checking correctness.** Kernels must produce self-checking output --- deterministic checksums, tolerance-bounded numerical comparison, or labeled correctness indicators (e.g., `PASS`/`FAIL`, `verify()`) --- enabling automated correctness verification without external reference files.
4. **Open-source availability.** All source code must be publicly available under an open-source license, ensuring reproducibility.
5. **Domain diversity.** Selected suites should collectively span a broad range of computational domains (graph traversal, stencil computation, linear algebra, molecular dynamics, machine learning, signal processing, etc.) to avoid over-representing any single algorithmic pattern.

These criteria are intentionally conservative: they exclude repositories that require interactive execution, external datasets not bundled with the source, or proprietary licenses. Applying them to the 35 surveyed repositories yields five suites that satisfy all five criteria and collectively provide maximum coverage of the CUDA--OpenMP--OpenCL API triple.

### 4.B Kernel Selection

Kernel selection proceeds in two stages: selection from HeCBench (which provides the largest pool of multi-API kernels) and curation of kernels from Rodinia and three additional suites.

**HeCBench selection funnel.** HeCBench \cite{HeCBench2023} is the largest source of multi-API kernel implementations in the survey, with 513 kernels spanning CUDA, HIP, SYCL, and OpenMP. We applied a structured selection funnel to identify kernels suitable for automated translation evaluation (Figure 4):

1. **4-API filter.** 327 kernels provide implementations in all four APIs (CUDA, HIP, SYCL, OpenMP).
2. **Build system filter.** 325 of these 327 have Makefiles present in the CUDA variant (2 excluded for missing build infrastructure).
3. **Self-checking filter.** 242 of the 325 contain self-checking output patterns --- string matching for `PASS`, `FAIL`, `verify`, or `correct` in the source --- enabling automated correctness verification.
4. **Complexity filter.** Kernels with more than 15 source files (too complex for single-prompt translation) or fewer than 2 files (too trivial to exercise meaningful translation competence) were excluded, as were kernels requiring external input data files not bundled with the source.
5. **Domain diversity selection.** From the remaining pool, 60 kernels were selected to maximize coverage across computational domains.

[Figure 4: HeCBench kernel selection funnel. Starting from 327 kernels with all 4 API variants, successive filters for build infrastructure (325), self-checking patterns (242), complexity bounds, and domain diversity yield the 60-kernel working set.]

The 60 selected HeCBench kernels span 41 distinct computational domains, including machine learning (6 kernels: backprop, geglu, knn, maxpool3d, rmsnorm, softmax-online), signal processing (4: convolutionseparable, dct8x8, fft, fwt), cryptography (3: aes, chacha20, secp256k1), bioinformatics (2: deredundancy, nw), dense linear algebra (2: gaussian, lud), graph algorithms (2: floydwarshall, mis), image processing (2: bilateral, sobel), memory bandwidth (2: babelstream, triad), numerical linear algebra (2: eigenvalue, thomas), and 29 additional domains with one kernel each. All 60 CUDA variants pass build/run/verify on the evaluation platform; 41 of the 60 OpenMP variants pass (68.3%), with the remaining 19 exhibiting upstream HeCBench issues (missing OMP source directories, numerical mismatches, runtime crashes, or timeouts) rather than ParBench harness defects.

From this 60-kernel working set, a curated subset of **10 kernels** was selected for inclusion in the evaluation corpus. These 10 were chosen for verified correctness across multiple APIs and maximum domain diversity: stencil computation (stencil1d, heat2d, iso2dfd), graph algorithms (floydwarshall, page-rank), combinatorial search (nqueen), molecular dynamics (md), signal processing (convolution1d, scan), and numerical methods (jacobi). The curated subset provides 25 specs across three API variants (CUDA, CPU OpenMP, and OMP-target GPU offload).

**Rodinia.** Rodinia \cite{Rodinia2009} provides ParBench's primary evaluation substrate. With thousands of citations, Rodinia is among the most-studied GPU benchmark suites in HPC literature, and critically provides CUDA, OpenMP, and OpenCL implementations of most kernels in the same source tree --- making it ideal for translation benchmarking where the reference implementation for each API is authoritative. ParBench includes 60 Rodinia specs covering 22 kernels across three APIs (22 CUDA, 18 OpenMP, 20 OpenCL; coverage is non-uniform because not all kernels have all three API variants). After systematic verification on the evaluation platform, 54/60 achieve PASS and 6 are KNOWN\_FAIL for platform-specific reasons:

- 2 specs fail because CUDA 12 removed the deprecated `texture<>` reference API (kmeans-cuda, mummergpu-cuda);
- 1 spec fails due to a missing OpenGL dependency (hybridsort-cuda);
- 1 spec inherits CUDA texture dependencies in its OpenMP variant (mummergpu-omp);
- 2 OpenCL specs exhibit pre-existing runtime crashes (nn-opencl, kmeans-opencl).

These failures are documented but excluded from the evaluation corpus; they reflect toolchain evolution, not benchmark design defects.

However, Rodinia's age and wide availability raise a legitimate concern: its source code is likely present in LLM training corpora, potentially inflating pass rates through memorization rather than genuine translation competence. To address this threat to validity and broaden domain coverage, ParBench includes four additional benchmark suites.

**XSBench** \cite{XSBench2014} is a Monte Carlo neutron transport proxy application that implements the continuous-energy macroscopic cross-section lookup kernel from OpenMC. It provides 4 specs (CUDA, OpenMP, OpenCL, OMP-target), all 4 PASS. XSBench is included specifically because it is also evaluated in prior repository-level work \cite{ParEvalRepo2025}, enabling direct comparison of evaluation granularity on the same kernel.

**RSBench and mixbench.** RSBench \cite{RSBench2014} (4 specs: CUDA, OpenMP, OpenCL, OMP-target) is a simplified reactor simulation proxy derived from the same OpenMC cross-section lookup as XSBench but using a multipole method, adding complex arithmetic and Faddeeva function evaluation patterns less likely to appear in training data. mixbench \cite{mixbench2017} (3 specs: CUDA, OpenMP, OpenCL) is a GPU micro-benchmark measuring the balance between compute throughput and memory bandwidth --- the operational intensity axis of the roofline model. Together they contribute domain diversity beyond Rodinia's traditional HPC kernels: nuclear physics simulation and fine-grained GPU characterization.

### 4.C API Coverage

The survey data directly inform ParBench's API selection. CUDA serves as the primary source language, reflecting its dominant position in GPU programming: it appears in more surveyed repositories than any other GPU-native API and contributes the largest kernel count in the survey. OpenMP is the primary translation target: the kernel-level survey identified CUDA-to-OpenMP as the largest translation opportunity among CPU-targeting APIs, with 472 kernel pairs across 6 repositories (Table 3). This is not coincidental --- OpenMP's pragma-based parallelism model makes it the natural CPU-parallel counterpart to CUDA's GPU-native model, and benchmark developers routinely provide both implementations.

OpenCL provides a secondary translation target that exercises a qualitatively different programming model from both CUDA and OpenMP. Where CUDA uses unified host-device source files and implicit memory management (in modern CUDA), and OpenMP uses compiler directives over sequential code, OpenCL requires explicit kernel compilation from string sources, manual buffer management, and strict host-device code separation. Rodinia's particular strength lies in its OpenCL coverage: 20 of 22 Rodinia kernels have OpenCL implementations, compared to only sparse OpenCL coverage in HeCBench and RAJAPerf. This makes Rodinia the primary source for OpenCL translation pairs.

OpenMP target offload (OMP-target) provides a fourth API that uses compiler-directed GPU offloading via `#pragma omp target`. It is available for XSBench, RSBench, and the HeCBench curated kernels, and requires the NVIDIA HPC compiler (`nvc`) rather than standard GCC. Because `nvc` is not universally available and OMP-target's compilation model differs substantially from CPU OpenMP, OMP-target directions are evaluated as case studies rather than as part of the standard evaluation.

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

---

## S5 Experimental Setup

This section describes the models, translation directions, augmentation protocol, evaluation metrics, and hardware/software configuration used in the primary evaluation campaign.

### 5.A Models

Two large language models are evaluated, selected to maximize architectural diversity across non-Anthropic providers (D1):

- **Qwen 3.5 397B-A17B** (Alibaba, accessed via Together AI): A Mixture-of-Experts (MoE) model with 397 billion total parameters and 17 billion active per forward pass. The MoE architecture tests whether massive parameter count with sparse activation -- where only a fraction of parameters are activated per token -- benefits HPC translation, a domain where relevant knowledge may be distributed across specialized expert subnetworks.

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

Source code augmentation is applied at five levels. Level L0 uses the unmodified benchmark source and serves as the baseline. Levels L1 through L4 apply the six AST-driven transforms (described in Section 3.C) at increasing density: L1 applies one randomly selected transform at a single candidate site; L2 selects 33\% of transforms and applies each to 33\% of eligible candidate sites; L3 selects 66\% of transforms at 66\% of sites; and L4 applies all transforms at all sites. A fixed random seed of 42 governs all stochastic choices for reproducibility. With 5 augmentation levels and 142 L0 task pairs, the primary campaign comprises 710 translation tasks per model (D2). An additional 80 tasks from 8 KNOWN\_FAIL specifications are excluded from analysis as they produce expected build or runtime failures unrelated to translation quality (Section 4.B).

The augmentation protocol tests a specific hypothesis: if an LLM genuinely reasons about parallel computation structure rather than pattern-matching against memorized training examples, its translation success rate should remain stable across augmentation levels. The augmentation baseline was verified prior to the campaign launch (D6): 68 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench) were run through the full build-run-verify pipeline at all five augmentation levels. All produced identical correctness outcomes, confirming that the AST-driven transforms preserve semantic equivalence and that any variation in LLM pass rates across levels can be attributed to the model rather than to the augmentation process. Eight KNOWN\_FAIL specs are excluded from the evaluation corpus (Section 4.B).

### 5.D Metrics

The primary evaluation metric is **greedy-decode pass@1**: the fraction of translation tasks that pass the full build, run, and verify pipeline on a single greedy-decoded evaluation (temperature 0), with up to 3 self-repair attempts via iterative error feedback (D3). We use the term "greedy-decode pass@1" to distinguish this from the standard pass@k formulation of Chen et al. \cite{HumanEval2021}, which assumes stochastic sampling. In our primary campaign, temperature 0 eliminates sampling variance entirely: each task receives exactly one deterministic model output, and pass@1 is simply the empirical success rate.

Each failure is classified into a diagnostic category -- BUILD\_FAIL (compilation error), RUN\_FAIL (runtime crash or nonzero exit code), VERIFY\_FAIL (incorrect output), or EXTRACTION\_FAIL (malformed LLM response) -- enabling fine-grained failure-mode analysis beyond a single pass/fail number. Self-repair outcomes are further classified as first\_attempt\_pass (correct on first try), full\_repair (model self-corrected after error feedback), partial\_repair (improved failure category but still failed), regression (worsened after retry), or persistent\_fail (same error across all attempts).

A separate **pass@k experiment** measures sampling variance (D4): 3 independent samples per task at temperature 0.7, L0 only, with no self-repair (max\_retries=1). This isolates output-side stochasticity from input-side variation (augmentation) and self-repair effects. The gap between greedy-decode pass@1 and pass@3 reveals whether failures are "hard" (the model fundamentally cannot translate the kernel) or "noisy" (the model sometimes succeeds but not reliably). This design keeps the three evaluation axes orthogonal: self-repair (retries), sampling variance (pass@k), and augmentation robustness (L0--L4).

Secondary metrics include **augmentation robustness**, defined as the stability of pass@1 across augmentation levels L0 through L4, and **self-repair rate**, the fraction of initially failing tasks recovered by the error-feedback retry loop. Statistical analysis uses Wilson score 95\% confidence intervals for proportions, Fisher's exact test for pairwise model comparison, and the Cochran-Armitage trend test for augmentation-level effects.

Execution timing and speedup metrics are excluded from this study. The current verification pipeline measures wall-clock time, which conflates kernel execution with I/O, memory allocation, and OS scheduling noise. Reliable performance comparison requires profiler-based kernel timing (e.g., Nsight Compute for CUDA, `omp\_get\_wtime()` for OpenMP), which is deferred to future work.

### 5.E Hardware and Software

All Qwen 3.5 evaluations are conducted on a single workstation to eliminate cross-machine variability. The GPU is an NVIDIA GeForce RTX 4070 (Ada Lovelace architecture, compute capability 8.9, 5888 CUDA cores, 12 GB GDDR6X). The CPU is an AMD Ryzen 9 7900X (12 cores, 24 threads). The system runs Ubuntu 24.04 LTS (kernel 6.8.0-40-generic).

CUDA compilation uses `nvcc` from the NVIDIA HPC SDK 24.3 (CUDA 12.3). C/C++ compilation uses GCC 12.4 with the `-fopenmp` flag for OpenMP targets. OpenCL programs link against the NVIDIA runtime from the HPC SDK. The evaluation harness and all scripting infrastructure run on Python 3.12.3. LLM API calls are issued from the evaluation machine; network latency does not affect correctness evaluation. All campaigns were executed via a single parameterized script ensuring identical batch logic, retry policy, and analysis pipeline across all models and modes (D5).

Gemini 2.5 Flash evaluations are conducted by a collaborator on a separate machine with identical software configuration. [PENDING: Gemini hardware -- GPU model, CPU model, and OS for Erel's evaluation machine.]

[TABLE 6: Hardware and software configuration. Rows: GPU model, CPU model, operating system, CUDA toolkit version, C/C++ compiler, OpenCL runtime, Python version. Separate columns for Qwen (primary) and Gemini (collaborator) evaluation machines.]

---

## S6 Results

This section presents ParBench evaluation results across [PENDING: total evaluated tasks] evaluated tasks: two LLMs -- Qwen 3.5 397B-A17B (Mixture-of-Experts) and Gemini 2.5 Flash (dense) -- evaluated on parallel code translation across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench curated), six translation directions, and five augmentation levels (L0--L4). All primary campaign evaluations use temperature=0, up to three self-repair retry attempts (four total attempts per task), and the build/run/verify pipeline described in S3.B. A separate pass@k sweep (S6.7) evaluates sampling variance at temperature=0.7.

### 6.1 Overall Pass Rates

Table 7 summarizes aggregate pass rates for the two evaluated models across all directions and augmentation levels.

[TABLE 7: Overall pass rates across all tasks (2 models, 5 suites, 6 directions, L0--L4). KNOWN\_FAIL source specs (8 total: 6 Rodinia + 2 HeCBench) are excluded from evaluation.]

| Model | PASS | BUILD\_FAIL | RUN\_FAIL | VERIFY\_FAIL | EXTRACTION\_FAIL | Total | Rate | 95% Wilson CI |
|-------|-----:|----------:|--------:|------------:|----------------:|------:|-----:|:-------------:|
| Qwen 3.5 397B-A17B | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Gemini 2.5 Flash | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| **Aggregate** | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

[PENDING: overall comparison prose -- describe the capability gap pattern between Qwen and Gemini; note whether the spread is large (qualitatively different tiers) or modest (comparable capability). Reference MoE vs dense architecture where appropriate. Awaiting primary campaign results.]

These results contrast sharply with repository-level evaluation. ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 for all models on applications larger than 133 SLoC, including XSBench. ParBench's kernel-centric approach -- isolating the translation task from build-system generation -- achieves [PENDING: best model rate] for the stronger model on the same class of HPC kernels. The gap quantifies the degree to which build-system generation, rather than parallel logic translation, is the binding constraint in repository-level approaches.

Statistical comparison: a chi-squared test of independence between model identity and pass/fail outcome yields [PENDING: chi2 stat] (df=1, p=[PENDING: chi2 p-value]). [PENDING: chi2 interpretation with Cramer's V effect size.]

### 6.2 Failure Taxonomy

Of the [PENDING: total failure count] total failures across both models, the distribution is:

- BUILD\_FAIL: [PENDING: count/total (pct)]
- RUN\_FAIL: [PENDING: count/total (pct)]
- VERIFY\_FAIL: [PENDING: count/total (pct)]
- EXTRACTION\_FAIL: [PENDING: count/total (pct)]

[FIGURE 5: Failure taxonomy stacked bar chart. X-axis: models (Qwen 3.5 397B-A17B, Gemini 2.5 Flash). Y-axis: task count stacked by outcome (PASS, BUILD\_FAIL, RUN\_FAIL, VERIFY\_FAIL, EXTRACTION\_FAIL). Data source: results/evaluation/eval\_summary.json.]

**BUILD\_FAIL dominance.** [PENDING: BUILD_FAIL analysis -- describe whether BUILD_FAIL remains the dominant failure mode and its percentage of total failures. Expected pattern: retained CUDA memory management calls in otherwise-OpenMP code, missing #pragma omp directives, incorrect function signatures. These are syntactic failures indicating the model demonstrates understanding of the parallel computation structure but fails to fully translate the API surface. Awaiting primary campaign results.]

**VERIFY\_FAIL analysis.** [PENDING: VERIFY_FAIL analysis -- describe the rate of VERIFY_FAIL and what it reveals. VERIFY_FAIL indicates translations that compile and execute but produce incorrect output, identifying subtle parallel logic errors. The conjunctive verification (exit_code AND stdout_pattern) catches translations that would have appeared correct under exit-code-only checking. Awaiting primary campaign results.]

**Failure mode shift in kernel-only translations.** The aggregate failure taxonomy above is dominated by full-program translation directions (CUDA-to-OpenMP, OpenMP-to-CUDA), where BUILD\_FAIL is the majority failure mode. OpenCL-target translations exhibit a structurally different distribution: zero tasks are classified as BUILD\_FAIL, because the host binary is never modified and always compiles successfully. Failures shift entirely to runtime categories. RUN\_FAIL occurs when the LLM-generated kernel fails `clBuildProgram()` at runtime and the host program propagates the error as a non-zero exit code or segmentation fault (process exit code -11, i.e., SIGSEGV). VERIFY\_FAIL occurs when either the kernel builds but produces numerically incorrect output, or when the host catches the kernel compilation error gracefully, prints a superficially correct message, and exits 0 (Section 3.D describes the false-positive guard that mitigates this). Early Qwen 3.5 cuda-to-opencl results (N=26) confirm this pattern: RUN\_FAIL and VERIFY\_FAIL account for all failures in roughly equal proportion. This structural difference has methodological implications: failure taxonomies aggregated across all directions may understate the diversity of failure modes, because the BUILD\_FAIL-dominated full-program directions mask the runtime-dominated kernel-only directions.

**Pipeline refinement note.** During initial campaign execution, a pipeline audit identified that cross-API translations were being run with the *target* spec's arguments rather than the *source* spec's arguments. Because LLM-translated binaries preserve the source implementation's argument-parsing convention, this produced systematic false negatives: translations that were functionally correct but received incompatible arguments, resulting in spurious RUN\_FAIL or VERIFY\_FAIL classifications. The pipeline was corrected to use source-spec arguments (Section 3.D), and all affected campaigns are being re-run with the fixed pipeline. The results reported in this section reflect the corrected pipeline. Additionally, the combined source/target verification pattern (Section 3.D) ensures that translations producing either source-native or target-native output formats are correctly classified as PASS. A second refinement addressed OpenCL-target translations specifically: the original pipeline applied the cross-API argument and verification logic uniformly, but kernel-only translations (where only `.cl` files are translated and the host binary is unchanged) require the target spec's native arguments and patterns, not the source spec's. This was corrected by the kernel-only detection predicate described in Section 3.D; prior to this fix, all OpenCL-target translations produced 0\% pass rate due to argument mismatches.

**Self-repair by failure mode transition.** To address the question of which failure modes are recoverable through self-repair (W12), Table 7b breaks down the transitions from initial failure to final outcome across all attempts.

[TABLE 7b: Self-repair failure mode transitions (all tasks, both models). Rows: initial failure mode. Columns: final outcome after up to 3 retries.]

| Initial Failure | -> PASS | -> Same Fail | -> Different Fail | -> Regression | Total |
|-----------------|--------:|-------------:|------------------:|--------------:|------:|
| BUILD\_FAIL | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| RUN\_FAIL | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| VERIFY\_FAIL | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| EXTRACTION\_FAIL | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

[PENDING: repair transition analysis -- describe which failure modes are most recoverable. Expected pattern: BUILD_FAIL most recoverable (compiler errors provide actionable feedback), VERIFY_FAIL least recoverable (output mismatch provides weak signal). Awaiting primary campaign results.]

### 6.3 Per-Kernel Analysis

Table 8 presents the kernel-by-model result matrix for the primary CUDA-to-OpenMP direction at L0 across all five benchmark suites.

[TABLE 8: Per-kernel results for CUDA-to-OpenMP translation (L0, 2 models). KNOWN\_FAIL source specs excluded. Suites: Rodinia (up to 16 kernels), XSBench (1), RSBench (1), mixbench (1), HeCBench curated (up to 10).]

[PENDING: per-kernel table -- Full kernel x model matrix with Suite, Kernel, Category columns and one column per model showing outcome. Sort by difficulty (all-pass first, then partial, then all-fail). Awaiting primary campaign results.]

[FIGURE 6: Kernel-by-model heatmap. Rows: kernels across all 5 suites sorted by difficulty. Columns: 2 models. Cell color: green (PASS), red (BUILD\_FAIL), orange (RUN\_FAIL), yellow (VERIFY\_FAIL), grey (EXTRACTION\_FAIL).]

Kernels partition into distinct difficulty tiers based on two-model consensus. The conjunctive verification (exit\_code AND stdout\_pattern) produces a sharper tier separation than exit-code-only verification, with VERIFY\_FAIL now distinguishing translations that produce wrong output from those that fail to build or run.

[PENDING: tier description -- Partition kernels into difficulty tiers based on two-model consensus: always-pass, single-model-pass, always-fail. Identify shared characteristics per tier and distinguish BUILD_FAIL-only from heterogeneous failure modes. Awaiting primary campaign results.]

[PENDING: kernel anomalies -- Identify surprising per-kernel results: cross-model inversions, suite-level clustering patterns. Awaiting primary campaign results.]

**Sample size note (W1).** The primary CUDA-to-OpenMP direction at L0 evaluates 24 kernel pairs across 5 suites with 2 models, yielding 48 tasks. Non-primary directions have smaller sample sizes (see S6.6) and findings from those directions should be considered exploratory.

### 6.4 Self-Repair Effectiveness

ParBench's evaluation pipeline permits up to three retry attempts with failure-specific diagnostics injected into subsequent prompts (four total attempts per task). Table 9 summarizes self-repair effectiveness.

[TABLE 9: Self-repair effectiveness (all directions, all levels, 2 models).]

| Metric | Qwen 3.5 | Gemini 2.5 Flash | Combined |
|--------|----------:|------------------:|---------:|
| Total tasks | [PENDING] | [PENDING] | [PENDING] |
| First-attempt PASS | [PENDING] | [PENDING] | [PENDING] |
| Repaired (attempt 2-4) | [PENDING] | [PENDING] | [PENDING] |
| Total PASS | [PENDING] | [PENDING] | [PENDING] |
| Relative improvement | [PENDING] | [PENDING] | [PENDING] |
| Persistent fail | [PENDING] | [PENDING] | [PENDING] |
| Regression | [PENDING] | [PENDING] | [PENDING] |

[PENDING: self-repair statistics -- describe repair patterns: first-attempt vs retry fraction, per-model repair rate differences, attempt-number distribution, regression rate. Awaiting primary campaign results.]

**Self-repair in kernel-only mode.** Kernel-only translations (targeting OpenCL) provide a natural experiment in self-repair quality: the error feedback comes from `clBuildProgram()` runtime errors rather than compiler errors, and the model must fix kernel source without seeing the host code. Early Qwen 3.5 cuda-to-opencl results (N=26) show that self-repair is effective for some kernel-only failures: `bfs` fails on attempt 0 (missing `__global` qualifiers and undeclared identifiers) but succeeds on attempt 1 after receiving the kernel compilation error log. However, self-repair is ineffective for *ceiling failures* where the entire translation approach is fundamentally wrong: `dwt2d` produces identical kernel compilation errors across all three retry attempts at every augmentation level, because the CUDA source uses C++ features (templates, operator overloads) that cannot be expressed in OpenCL C regardless of how many iterations the model attempts. This dichotomy -- recoverable syntax errors vs. irrecoverable language-gap errors -- suggests that self-repair effectiveness in kernel-only mode is bounded by whether the failure is a surface-level omission (missing qualifier, wrong function name) or a structural impossibility (source language features absent from the target).

The self-repair data positions ParBench's 3-retry protocol as a controlled middle ground on the agentic spectrum. LASSI \cite{LASSI2024} reports 80--85% pass rates with a complete agentic self-correction pipeline (compilation feedback, execution analysis, profiling). ParBench's self-repair protocol provides only error feedback (compiler output or output mismatch) without retrieval augmentation or tool access. The gap between ParBench's repair rate ([PENDING: combined total pass pct]) and LASSI's agentic rate (80--85%) quantifies the value of agentic infrastructure beyond simple error feedback.

### 6.5 Augmentation Robustness

The augmentation engine's six AST-driven transforms were validated on 68 of 88 non-KNOWN\_FAIL specs across five suites at augmentation levels L1 through L4, confirming level-invariant semantics preservation with zero correctness regressions (Section 3.C). The remaining 13 HeCBench specs were not explicitly verified at all augmentation levels due to source availability constraints (Section 4.B). This harness baseline establishes that any variation in LLM pass rates across augmentation levels can be attributed to the model's sensitivity to surface syntax, not to augmentation-induced semantic changes.

Table 10 presents per-model pass rates across augmentation levels L0--L4 for CUDA-to-OpenMP translation. Per the campaign design (D2), augmentation robustness is evaluated across all six directions, but this table restricts to the primary direction (CUDA-to-OpenMP) to eliminate the direction-composition confound identified in the audit (W8).

[TABLE 10: LLM pass rates across augmentation levels (CUDA-to-OpenMP direction only, all 5 suites, 2 models).]

| Level | Qwen 3.5 397B-A17B | Gemini 2.5 Flash |
|:-----:|:-------------------:|:----------------:|
| L0 | [PENDING] | [PENDING] |
| L1 | [PENDING] | [PENDING] |
| L2 | [PENDING] | [PENDING] |
| L3 | [PENDING] | [PENDING] |
| L4 | [PENDING] | [PENDING] |

[FIGURE 7: Augmentation robustness line chart. X-axis: augmentation levels L0--L4. Y-axis: pass rate (%). Two lines: Qwen 3.5 (color 1), Gemini 2.5 Flash (color 2). Error bars: Wilson 95% CIs.]

[PENDING: augmentation curves -- Describe per-model augmentation curves including Cochran-Armitage trend tests, stability vs degradation patterns, and Simpson's Paradox check. Awaiting primary campaign results.]

The augmentation robustness results discriminate model capability in a way that L0 pass rates alone cannot. [PENDING: augmentation discrimination prose -- describe how augmentation curves reveal a different capability picture than L0 results, including MoE vs dense architecture sensitivity comparison. Awaiting primary campaign results.]

### 6.6 Cross-Direction Analysis

Table 11 presents pass rates broken down by translation direction for each model at L0.

[TABLE 11: Pass rates by translation direction (L0, all suites, 2 models). Directions with fewer than 10 kernel-model pairs are marked as exploratory.]

| Direction | Qwen 3.5 | Gemini 2.5 Flash | Combined | N (pairs) | Note |
|-----------|----------:|------------------:|---------:|----------:|:-----|
| cuda-to-omp | [PENDING] | [PENDING] | [PENDING] | 24 | Primary |
| omp-to-cuda | [PENDING] | [PENDING] | [PENDING] | 24 | |
| cuda-to-opencl | [PENDING] | [PENDING] | [PENDING] | 20 | |
| opencl-to-cuda | [PENDING] | [PENDING] | [PENDING] | 20 | |
| omp-to-opencl | [PENDING] | [PENDING] | [PENDING] | 18 | |
| opencl-to-omp | [PENDING] | [PENDING] | [PENDING] | 18 | |
| cuda-to-omp\_target | [PENDING] | [PENDING] | [PENDING] | 8 | HeCBench case study |
| omp\_target-to-cuda | [PENDING] | [PENDING] | [PENDING] | 10 | HeCBench case study |

[FIGURE 8: Cross-direction grouped bar chart. X-axis: 8 directions. Y-axis: pass rate (%). Grouped bars: one per model.]

**Direction asymmetry.** [PENDING: direction asymmetry prose -- for each bidirectional pair, report the pass rate gap. CUDA-to-OpenMP is a reductive task; OpenMP-to-CUDA is a generative task. Awaiting primary campaign results.]

McNemar's test for paired direction comparison (using kernel-model pairs evaluated in both directions): [PENDING: McNemar test statistics and p-values for each bidirectional pair.]

**Per-suite direction results.** [PENDING: per-suite direction prose -- describe how pass rates vary across suites within the same direction, separating Rodinia from XSBench, RSBench, mixbench, and HeCBench. Awaiting primary campaign results.]

**OpenCL-target translation: kernel-only failure modes.** Translations targeting OpenCL exercise a qualitatively different failure mode from CUDA and OpenMP targets. Because OpenCL translations are kernel-only (Section 3.D) -- the LLM translates only `.cl` kernel files while the host program remains unchanged -- build failures are replaced by *kernel compilation failures* at runtime, when the host invokes `clBuildProgram()` on the LLM-generated kernel source. The failure distribution reflects this shift: for CUDA-to-OpenCL, zero results are classified as BUILD\_FAIL (the host binary always compiles), while VERIFY\_FAIL and RUN\_FAIL dominate in roughly equal proportion -- a stark contrast with CUDA-to-OpenMP, where BUILD\_FAIL accounts for the majority of failures. Two recurring error patterns emerge. First, missing `__global` address space qualifiers on kernel pointer arguments: CUDA has no equivalent syntactic requirement (pointers in CUDA device code are implicitly device-resident), so LLMs frequently omit the mandatory OpenCL qualifier, producing kernel compilation errors at `clBuildProgram()` time (OpenCL error code `CL_BUILD_PROGRAM_FAILURE`, -11). Second, API name hallucination: inspection of LLM-generated kernel source code reveals instances of nonexistent OpenCL built-in functions created by mapping CUDA concepts to invented names -- e.g., `get_block_id()` (nonexistent) instead of the correct `get_group_id()`, reflecting a CUDA `blockIdx` mental model applied to the OpenCL naming convention. This pattern was identified in the `backprop` kernel translation (4 instances in a single kernel file), suggesting that hallucinated API names may cluster within individual translations rather than appearing uniformly across kernels. These failures are LLM translation quality errors, not pipeline artifacts, confirming that the kernel-only evaluation infrastructure correctly isolates model capability for OpenCL targets.

**Augmentation sensitivity in kernel-only translations.** Per-kernel analysis of early Qwen 3.5 cuda-to-opencl results (N=26) reveals that augmentation interacts differently with kernel-only translations than with full-program translations. The `bfs` kernel passes at L0--L2 (via self-repair: attempt 0 fails due to missing `__global` qualifiers, attempt 1 succeeds after receiving `clBuildProgram()` error feedback) but fails at L3--L4, where the additional variable renaming and type substitution introduced by higher augmentation levels cause the LLM to lose track of which pointer parameters require address space qualifiers. This is direct evidence that augmentation specifically degrades OpenCL translation quality at higher levels -- a finding relevant to the augmentation robustness analysis (Section 6.5, Section 7.5). In contrast, `dwt2d` fails at all augmentation levels (L0--L4) because the CUDA source uses C++ language features (templates, operator overloads, class methods, reference parameters) that have no equivalent in OpenCL C. All three self-repair attempts at every level produce identical kernel compilation errors, indicating an *untranslatable ceiling*: no amount of self-repair can compensate for a translation that requires algorithmic rewrite rather than syntax correction. These two cases illustrate the spectrum of kernel-only translation failure: `bfs` represents a *recoverable-but-fragile* pattern where self-repair works at low augmentation but breaks at high augmentation, while `dwt2d` represents a *structural impossibility* where the source--target language gap exceeds what API translation can bridge.

**OpenCL direction asymmetry.** The CUDA--OpenCL bidirectional pair is expected to exhibit a pronounced direction asymmetry driven by structural differences in translation scope. OpenCL-to-CUDA is a full-program translation: the LLM must rewrite both the host code (replacing OpenCL buffer management, kernel launch, and result readback with CUDA equivalents) and the kernel code. In contrast, CUDA-to-OpenCL is a kernel-only translation where the host code is preserved. Partial results indicate that opencl-to-cuda is dominated by BUILD\_FAIL [PENDING: final opencl-to-cuda pass rate and failure distribution after batch completion], while CUDA-to-OpenCL achieves a substantially higher pass rate [PENDING: final cuda-to-opencl rate after batch completion]. If confirmed, this asymmetry would quantify the difficulty premium of full-program translation over kernel-only translation: when the LLM must reconstruct host-side API infrastructure in addition to translating kernel logic, pass rates are expected to drop sharply.

**Sample size caveat (W1).** The primary direction (cuda-to-omp) has the largest sample size (24 pairs) and supports the most reliable conclusions. Directions with fewer than 10 pairs should be considered exploratory. The two HeCBench case-study directions (cuda-to-omp\_target with 8 pairs and omp\_target-to-cuda with 10 pairs) have limited statistical power.

### 6.7 pass@k Analysis

To characterize sampling variance independent of self-repair, a separate pass@k sweep evaluates both models at L0 with temperature=0.7 and 3 independent samples per task (max\_retries=1 per sample, i.e., zero-shot per sample). The pass@k estimator follows Chen et al. \cite{HumanEval2021}: $\text{pass@}k = 1 - \binom{n-c}{k} / \binom{n}{k}$, where $n$ is the number of samples and $c$ is the number that pass.

[TABLE 12: pass@k results (L0, temperature=0.7, 3 samples, 2 models).]

| Model | pass@1 (greedy, T=0) | pass@1 (T=0.7) | pass@3 (T=0.7) | Hard Fail % | Noisy Fail % |
|-------|---------------------:|----------------:|----------------:|------------:|-------------:|
| Qwen 3.5 397B-A17B | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Gemini 2.5 Flash | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

Hard failures are defined as kernels where pass@3 = 0 (the model fundamentally cannot translate this kernel across any sample). Noisy failures have pass@1 = 0 but pass@3 > 0, indicating partial capability that does not reliably surface under greedy decoding.

[PENDING: pass@k analysis -- describe the gap between greedy pass@1 and pass@3, hard vs noisy failure counts per model, cross-model overlap of hard failures, and temperature effect on pass@1. Awaiting pass@k sweep results.]

### 6.8 Statistical Summary

Table 13 consolidates the statistical tests applied throughout S6.

[TABLE 13: Statistical summary. All confidence intervals are Wilson 95% CIs.]

| Test | Statistic | p-value | Effect Size | Interpretation |
|------|-----------|---------|-------------|----------------|
| Model comparison (chi-squared) | [PENDING] | [PENDING] | Cramer's V = [PENDING] | [PENDING] |
| Qwen augmentation trend (Cochran-Armitage) | z = [PENDING] | [PENDING] | -- | [PENDING] |
| Gemini augmentation trend (Cochran-Armitage) | z = [PENDING] | [PENDING] | -- | [PENDING] |
| Direction asymmetry: cuda-omp (McNemar) | [PENDING] | [PENDING] | -- | [PENDING] |
| Direction asymmetry: cuda-opencl (McNemar) | [PENDING] | [PENDING] | -- | [PENDING] |
| Direction asymmetry: omp-opencl (McNemar) | [PENDING] | [PENDING] | -- | [PENDING] |

Methodological notes: Wilson confidence intervals are preferred over Wald intervals because they provide better coverage near boundary proportions (0% or 100%), which several per-kernel and per-direction rates approach. Cochran-Armitage tests model a linear trend in pass rate across ordered augmentation levels (L0 < L1 < L2 < L3 < L4), which is the appropriate test for the hypothesis that increasing augmentation intensity degrades model performance. McNemar's test is used for direction asymmetry because each kernel-model pair is evaluated in both directions, creating natural pairing.

---

## S7 Discussion

### 7.1 The Kernel-Centric Advantage

ParBench's central design decision -- isolating kernel-level translation from build-system generation -- produces a qualitatively different evaluation outcome than repository-level approaches. The stronger model achieves [PENDING: best model rate] PASS on CUDA-to-OpenMP translation of the same class of HPC kernels for which ParEval-Repo \cite{ParEvalRepo2025} reports 0% pass@1 at the repository level. This is not a comparison of different benchmarks or different models; it is a comparison of evaluation granularity applied to overlapping computational domains.

The implication is that LLMs possess substantial internalized knowledge of parallel programming patterns -- thread decomposition, reduction operations, stencil computation, synchronization -- that is masked when evaluation conflates translation skill with build-system generation. ParBench's kernel-centric design separates these orthogonal capabilities, enabling measurement of each in isolation. The two evaluation granularities are complementary: ParEval-Repo measures end-to-end deployment capability; ParBench measures translation capability. Both are needed to characterize LLM parallel programming skill.

### 7.2 BUILD\_FAIL as the Actionable Bottleneck

BUILD\_FAIL accounts for [PENDING: BUILD_FAIL pct of all failures] of all failures across [PENDING: total tasks] tasks, establishing that the primary bottleneck is API-specific syntax rather than parallel reasoning capability. The recurring error patterns -- retained `cudaMalloc`/`cudaFree` calls, missing OpenMP pragma directives, incorrect type coercions -- are syntactic, not algorithmic. This finding has a direct practical implication: targeted fine-tuning on OpenMP idioms, or few-shot prompting with canonical CUDA-to-OpenMP translation examples, would likely close a substantial portion of the BUILD\_FAIL gap. The parallel reasoning capability is already present in the model weights; the API surface coverage is the limiting factor.

VERIFY\_FAIL accounts for [PENDING: VERIFY_FAIL pct of all failures] of all failures, providing a more nuanced picture than the BUILD\_FAIL-only story suggests. These are translations that compile, run to completion, and produce output -- but incorrect output. The conjunctive verification upgrade (exit\_code AND stdout\_pattern) catches these cases, which weaker verification would miss. VERIFY\_FAIL indicates genuine parallel logic errors: wrong thread-index mappings, incorrect reduction scoping, or missed data dependencies that produce numerically wrong results. While rarer than BUILD\_FAIL, VERIFY\_FAIL demonstrates that LLMs do not always correctly reason about parallel computation structure even when they produce syntactically valid code.

### 7.3 Model Capability Analysis

[PENDING: model comparison discussion -- describe capability spread between Qwen 3.5 397B-A17B and Gemini 2.5 Flash: overall pass rate gap, MoE vs dense architecture implications, failure profile comparison, per-kernel agreement. Awaiting primary campaign results.]

The comparison with LASSI \cite{LASSI2024} frames these results on a capability spectrum. LASSI reports 80--85% pass rates with a complete agentic self-correction pipeline, while ParBench's primary campaign achieves [PENDING: combined total pass pct] with a 3-retry error-feedback protocol. The gap quantifies the value of agentic infrastructure: compilation feedback, execution analysis, profiling, and retrieval augmentation collectively improve pass rates from [PENDING: combined total pass pct] to 80--85%. This positions three tiers of capability:

1. **Raw model capability** (pass@k floor): [PENDING: pass@k floor rate] -- what the model achieves zero-shot without any feedback
2. **Controlled self-repair** (primary campaign): [PENDING: combined total pass pct] -- error feedback without tools
3. **Agentic system** (LASSI): 80--85% -- full tooling including profiling and RAG

### 7.4 Direction Asymmetry

[PENDING: direction asymmetry discussion -- describe whether cuda-to-omp is easier than omp-to-cuda and by how much, structural explanation (reductive vs generative task), cross-model consistency of asymmetry, patterns for cuda/opencl and omp/opencl pairs, and practical implications. Awaiting primary campaign results.]

**OpenCL as a structurally distinct translation target.** Translations targeting OpenCL exhibit qualitatively different failure profiles from those targeting CUDA or OpenMP, reflecting the OpenCL programming model's unique architectural characteristics. OpenCL translations are *kernel-only*: only `.cl` kernel files are translated, while host code (buffer management, kernel launch, result readback) remains unchanged. This means translation failures manifest as runtime kernel compilation errors rather than build-time failures -- a distinction that shifts the failure taxonomy from BUILD\_FAIL toward VERIFY\_FAIL. Two systematic error patterns illuminate the nature of the challenge. First, OpenCL's `__global` address space qualifier on kernel pointer parameters has no CUDA equivalent; LLMs consistently omit it, producing kernel compilation failures that the host binary may silently absorb. Second, inspection of LLM-generated kernel source code reveals API name hallucination: the `backprop` kernel translation contains 4 instances of `get_block_id()` (which does not exist) instead of the correct `get_group_id()`, mapping the CUDA `blockIdx` abstraction to an invented function name rather than the correct OpenCL equivalent. These patterns suggest that LLM knowledge of OpenCL's API surface is shallower than for CUDA or OpenMP, consistent with the relative scarcity of OpenCL code in public training corpora.

Beyond API surface depth, OpenCL-target translations expose a *translatability ceiling* that CUDA and OpenMP targets do not encounter. The `dwt2d` kernel's CUDA source uses C++ language features -- templates, operator overloads, class methods, reference parameters -- that have no equivalent in OpenCL C. No amount of self-repair can bridge this gap because the failure is not syntactic but structural: the translation requires algorithmic rewrite, not syntax correction. This ceiling is orthogonal to LLM capability; it reflects a fundamental asymmetry in the expressiveness of the source and target languages. Future evaluation frameworks should distinguish *model failures* (where a more capable LLM might succeed) from *task impossibilities* (where the source--target language gap precludes any correct translation without host-code modification). Additionally, forensic analysis of early results uncovered a false-positive `backprop` PASS caused by `clEnqueueReadBuffer` failure being silently absorbed by host error-handling code (Section 3.D). This discovery -- made through systematic investigation of anomalous results, not through automated detection -- underscores the methodological importance of defense-in-depth verification for kernel-only evaluation, where the untouched host binary's error paths become a source of measurement error.

The CUDA--OpenCL bidirectional pair is expected to produce the largest direction asymmetry in the evaluation. Kernel-only CUDA-to-OpenCL translation achieves [PENDING: final cuda-to-opencl rate], while the reverse direction -- opencl-to-cuda, which requires full-program translation including host code reconstruction -- achieves [PENDING: final opencl-to-cuda rate], with BUILD\_FAIL expected to dominate the failure distribution. This asymmetry is structurally predictable: CUDA-to-OpenCL preserves the host binary and requires only kernel-file translation, while OpenCL-to-CUDA requires the LLM to reconstruct CUDA's unified host-device source model from OpenCL's split-compilation architecture. If confirmed, the gap between kernel-only and full-program pass rates would parallel the repository-level 0\% reported by ParEval-Repo \cite{ParEvalRepo2025}, but for a different reason: here the bottleneck is API-specific host code generation, not build-system generation.

### 7.5 Augmentation Robustness Interpretation

[PENDING: augmentation interpretation -- interpret per-model augmentation curves. Key framing: augmentation robustness discriminates model capability (not necessarily level-invariance); memorization hypothesis test; MoE vs dense degradation comparison; Simpson's Paradox check; connection to pass@k. Awaiting primary campaign results.]

### 7.6 Threats to Validity

Several threats to the validity of these findings must be acknowledged.

**Sample size and suite scope.** The evaluation spans 35 kernels across five suites (Rodinia, XSBench, RSBench, mixbench, HeCBench curated), a significant expansion from single-suite evaluations. For the primary CUDA-to-OpenMP direction at L0, 24 kernel pairs are evaluated. Non-primary directions have smaller sample sizes; findings from directions with fewer than 10 kernel-model pairs should be considered exploratory rather than confirmatory (W1). While five suites span diverse computational domains (graph algorithms, stencil computation, particle transport, micro-benchmarks, molecular dynamics, linear algebra), generalization to additional suites (NAS, Polybench) is not established.

**Rodinia training-data familiarity (W11).** Rodinia is a 15+ year-old benchmark suite whose kernels are extensively documented and almost certainly present in LLM training data. The augmentation engine addresses surface-level memorization (variable names, code formatting), but cannot address algorithmic-level memorization (the LLM may "know" that BFS uses a frontier-based approach regardless of variable names). The five-suite expansion mitigates this concern: RSBench, mixbench, and HeCBench curated kernels are drawn from different eras and communities, providing benchmarks with varying degrees of training-data exposure. However, algorithmic memorization remains an irreducible threat for any evaluation using published benchmark codes.

**Correctness-only metric (W9).** ParBench measures translation correctness, not performance. An OpenMP translation that produces correct output but runs 100x slower than the original CUDA kernel is counted as PASS. TRACY \cite{TRACY2025} demonstrates that "correctness is not a reliable proxy for efficiency" -- 23.5% of correct translations exhibit pronounced inefficiency. ParBench's PASS rates should not be interpreted as deployment readiness. Kernel execution time comparison is deferred to future work.

**Temperature and sampling methodology (W5).** The primary campaign uses temperature=0 (greedy decoding) for deterministic reproducibility. This provides a single point estimate (greedy-decode pass@1) rather than a distribution. The supplementary pass@k sweep (S6.7) at temperature=0.7 characterizes sampling variance, but only at L0 without self-repair. The interaction between sampling variance and augmentation level is not characterized.

**Two-model evaluation.** Two models are evaluated, representing distinct architecture families (MoE and dense) from two non-Anthropic providers. While architectural diversity provides insight, two models do not represent the full landscape of available LLMs. Results may not generalize to models from other providers (OpenAI, Anthropic, Meta), reasoning models (o1, Claude with extended thinking), or code-specialized models (CodeRosetta, HPC-Coder-V2). ParBench's parameterized campaign script enables straightforward expansion to additional models.

**Reference implementation as ground truth.** Correctness verification compares LLM translation output against reference implementation output. Floating-point non-associativity between GPU and CPU computation could in principle cause false VERIFY\_FAIL results. The correctness configurations use small problem sizes where floating-point divergence is minimized, and manual inspection of a sample of VERIFY\_FAIL cases confirms genuine translation errors rather than floating-point artifacts. Additionally, all augmentation uses a single seed (seed=42), providing reproducibility but not characterizing variance across augmentation instantiations; and 8 specs are excluded as KNOWN\_FAIL due to build infrastructure issues (applied uniformly across models).

**Pipeline evolution during development.** The evaluation pipeline underwent iterative refinement during campaign execution. An audit of early results identified that cross-API translations were evaluated using the target spec's run arguments rather than the source spec's, producing systematic false negatives for translations that correctly preserved the source implementation's argument-parsing convention. The fix -- using source-spec arguments for cross-API translations and combining source/target stdout verification patterns -- was applied before the final campaign results reported in this paper. We disclose this to acknowledge that evaluation infrastructure itself can be a source of measurement error in LLM benchmarking, and recommend that future benchmark frameworks include explicit cross-API argument and verification handling as part of the pipeline design.

### 7.7 Implications for the HPC Community

The findings suggest several directions for improving LLM-based parallel code translation.

**LLMs can translate kernel-level parallel code with meaningful success rates.** The [PENDING: best model rate]% pass rate for the stronger model on CUDA-to-OpenMP translation -- compared to 0% for repository-level approaches on the same kernels -- demonstrates that kernel-level translation is a tractable task for current LLMs. This has practical implications for HPC portability: organizations migrating CUDA codebases to OpenMP can use LLMs as a first-pass translation tool, with human review for the [PENDING: fail rate]% that fail.

**BUILD\_FAIL dominance suggests targeted solutions.** With [PENDING: BUILD_FAIL pct]% of failures occurring at the compilation stage, the highest-ROI intervention is improving LLM coverage of API-specific syntax. Few-shot prompting with canonical translation patterns, fine-tuning on verified translation corpora, or hybrid approaches that pair LLM translation with rule-based API syntax correction could close a substantial portion of the failure gap. The parallel reasoning capability demonstrated by VERIFY\_FAIL cases (compilable but incorrect) is a harder problem, but a less frequent one.

**Augmentation should be standard practice for LLM-on-code evaluation.** [PENDING: augmentation implication prose -- describe whether augmentation discriminates model capability and should be adopted as a standard evaluation dimension. Awaiting primary campaign results.]

**Framework extensibility enables community adoption.** ParBench's spec schema is the extension point: adding a new kernel requires one JSON file with no modification to the harness or evaluation pipeline. The build/run/verify pipeline is benchmark-agnostic; any kernel with a deterministic correctness check can be onboarded. The five-suite expansion from Rodinia (the initial suite) to RSBench, mixbench, and HeCBench demonstrates this extensibility in practice.

**The agentic gap is quantifiable.** The three-tier framing (raw pass@k < controlled self-repair < agentic system) provides a measurement framework for decomposing LLM capability improvements. As agentic systems like LASSI \cite{LASSI2024} and ParaCodex \cite{ParaCodex2026} mature, ParBench's specifications serve as a controlled evaluation substrate where each tier can be measured independently. The gap between tiers quantifies the marginal value of each component: error feedback, tool access, retrieval augmentation, and profiling-guided optimization.

---

## S8 Conclusion

### 8.1 Summary

This paper presented ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation at the kernel level. ParBench makes three contributions that collectively address the absence of rigorous, reproducible evaluation infrastructure for this task.

First, ParBench provides the first systematic framework for evaluating kernel-level parallel code translation, supporting 96 specifications across five benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench), six translation directions across three API pairs (CUDA, OpenMP, OpenCL), with two additional OpenMP-target directions evaluated as case studies. The five suites span stencil computation, graph algorithms, particle transport, micro-benchmarks, and additional HPC domains. The kernel-centric design isolates translation skill from build-system generation, enabling measurement of parallel translation capability independent of build infrastructure.

Second, an AST-driven augmentation engine applies six semantics-preserving transforms at five augmentation levels (L0--L4). The engine is level-invariant: 68 of 88 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench) achieve PASS at every level L1--L4 with zero correctness regressions, confirming that the transforms preserve semantics. This validated baseline enables LLM robustness evaluation that distinguishes genuine parallel reasoning from training-data pattern-matching -- a methodological necessity when evaluating on well-known HPC benchmarks.

Third, empirical evaluation of two LLMs -- Qwen 3.5 397B-A17B (Mixture-of-Experts, 397B total / 17B active parameters) and Gemini 2.5 Flash (dense architecture) -- across 1,420 translation tasks reveals [PENDING: capability gap summary]. On the primary CUDA-to-OpenMP direction at L0, [PENDING: best model cuda-to-omp summary]. A failure taxonomy reveals that BUILD\_FAIL accounts for [PENDING: BUILD_FAIL pct of all failures] of all failures while VERIFY\_FAIL accounts for [PENDING: VERIFY_FAIL pct of all failures] -- establishing that API syntax is the primary bottleneck, though a meaningful minority of translations that compile and run produce incorrect parallel logic. Cross-direction evaluation reveals [PENDING: direction asymmetry summary], reflecting the structural advantage of translating from an explicit thread-decomposition model to a directive-based model. Augmentation robustness evaluation at L0--L4 reveals [PENDING: augmentation summary], demonstrating that augmentation provides a more discriminating evaluation dimension than aggregate pass rate alone.

### 8.2 Future Work

Five directions for future work are prioritized.

**Additional models.** ParBench is model-agnostic: adding a new model requires only an API key and a single command to the parameterized campaign script. Evaluation of frontier models (GPT-4.1, Claude Opus), open-weight models at different scales, and code-specialized models would characterize how model architecture, scale, and training data composition affect parallel code translation capability. The framework's extensibility is a design-level contribution -- the two-model evaluation presented here demonstrates the methodology; broader model coverage strengthens the generalizability of findings.

**Performance and efficiency analysis.** The current study is correctness-only. Reliable performance comparison requires profiler-based kernel timing (Nsight Compute for CUDA, `omp_get_wtime()` for OpenMP), which would characterize whether LLM-translated code preserves not only correctness but also the performance characteristics of the original implementation. Efficiency metrics -- translated lines per token, cost per correct translation -- would inform practical deployment decisions.

**Expanded API and benchmark coverage.** Extension to CUDA-to-HIP, CUDA-to-SYCL, and CUDA-to-OpenACC would address additional portability-relevant API pairs reflecting the increasingly heterogeneous accelerator landscape. Additional benchmark suites (Polybench, NAS Parallel Benchmarks) would broaden domain coverage and increase the statistical power of cross-model comparisons.

**Agentic translation evaluation.** ParBench's 3-retry self-repair protocol provides a controlled middle ground between zero-shot evaluation and full agentic systems. LASSI \cite{LASSI2024} reports 80--85% pass rates with a complete self-correction pipeline including RAG and tool use. ParBench's specs and harness serve as a natural evaluation backend for agentic systems -- joint evaluation would quantify whether agentic orchestration can close the BUILD\_FAIL gap that prompt-based translation leaves open, and decompose the improvement into contributions from error feedback, tool access, and retrieval augmentation.

**Fine-tuned and domain-adapted models.** CodeRosetta \cite{CodeRosetta2024} and HPC-Coder-V2 \cite{HPCCoderV2} demonstrate that domain-specific fine-tuning improves parallel code generation. Evaluating fine-tuned models on ParBench's augmented specifications would test whether fine-tuning on HPC code improves robustness to surface-level code variation or merely reinforces pattern-matching on the training distribution.

