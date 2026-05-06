# Related Work Research Notes for SC26 Paper

> Generated: 2026-03-29
> Purpose: Structured research notes for 7 critical missing papers identified in SC26 paper audit.
> Status: Research notes for Samyak's review -- NOT final paper text.

---

## 1. LASSI (Dearing et al., LLMxHPC Workshop @ IEEE CLUSTER 2024)

### a) Full Citation
Matthew T. Dearing, Yiheng Tao, Xingfu Wu, Zhiling Lan, and Valerie Taylor.
"LASSI: An LLM-Based Automated Self-Correcting Pipeline for Translating Parallel Scientific Codes."
LLMxHPC Workshop at IEEE International Conference on Cluster Computing (CLUSTER), 2024.
arXiv: 2407.01638. IEEE Xplore: 10740822.

### b) Methodology Summary (3-5 sentences)
LASSI is an automated pipeline that uses existing LLMs (both open and closed-source) to translate
between parallel programming languages. The pipeline incorporates a self-correcting feedback loop:
when translated code fails to compile or execute correctly, the error messages are fed back to the
LLM as context for re-prompting, enabling iterative debugging and refactoring. They evaluate both
a "non-agentic" (single-pass) and a "top-down agentic" (iterative) approach. The pipeline operates
bidirectionally between OpenMP target offload and CUDA.

### c) Key Results / Claims
- **80%** of OpenMP-to-CUDA translations produce expected output (after self-correction)
- **85%** of CUDA-to-OpenMP translations produce expected output (after self-correction)
- First-attempt success: 65.6% (OMP-to-CUDA), 55.9% (CUDA-to-OMP) -- self-correction adds ~15-30pp
- ~78% of OMP-to-CUDA and ~62% of CUDA-to-OMP execute within 10% runtime of original
- Evaluated 4 LLMs: GPT-4 Large, Codestral (22B), WizardCoder (33B), DeepSeek Coder v2 (16B)

### d) Verification Approach
**Build + Run + Verify (output matching).** This is the same 3-stage verification as ParBench.
Successful translation requires: (1) compiles without errors, (2) executes without runtime errors,
(3) produces output matching the reference HeCBench implementation. This is a genuine
conjunction verification, comparable to ParBench's approach.

### e) Benchmarks Used
10 HeCBench benchmarks across 9 categories: matrix-rotate, jacobi, layout, atomicCost,
dense-embedding, pathfinder, bsearch, entropy, colorwheel, randomAccess.
**No Rodinia overlap.** HeCBench overlap with ParBench's curated 10 HeCBench kernels is possible
but the specific kernel selections differ (LASSI's 10 are mostly different from ParBench's 10).

### f) How ParBench Differs
| Dimension | LASSI | ParBench |
|-----------|-------|----------|
| Scope | Agent pipeline (self-correction) | Benchmark + harness (spec-driven) |
| APIs | CUDA <-> OMP target offload (2 APIs) | CUDA, OpenMP, OpenCL (3 APIs, 6+ directions) |
| Benchmarks | 10 HeCBench only | Rodinia (54), XSBench (4), RSBench, mixbench, HeCBench (curated) |
| Input variation | None | AST-driven augmentation (L0-L4) |
| LLM evaluation | 4 LLMs, agentic self-correction | 3+ general-purpose LLMs, non-agentic (measures raw capability) |
| Focus | Pipeline effectiveness (self-correction gain) | Benchmark design + systematic evaluation |
| Reproducibility | Per-trial, no augmentation control | Seeded augmentation, deterministic harness |

### g) What ParBench Can Cite
- The 80-85% pass rate as LASSI's headline result, noting it uses agentic self-correction
  (ParBench deliberately evaluates non-agentic translation to measure raw model capability)
- Their HeCBench benchmark selection methodology
- The observation that self-correction adds ~15-30 percentage points over first-attempt success
- Their finding that CUDA-to-OMP is easier than OMP-to-CUDA (aligns or contrasts with ParBench data)
- **Critical comparison point:** LASSI's 80-85% vs ParBench's 22.44% -- the difference is explained
  by (1) agentic self-correction, (2) smaller benchmark set, (3) possibly different difficulty mix

---

## 2. CodeRosetta (TehraniJamsaz et al., NeurIPS 2024)

### a) Full Citation
Ali TehraniJamsaz, Arijit Bhattacharjee, Le Chen, Nesreen K. Ahmed, Amir Yazdanbakhsh, and Ali Jannesari.
"CodeRosetta: Pushing the Boundaries of Unsupervised Code Translation for Parallel Programming."
Advances in Neural Information Processing Systems 37 (NeurIPS 2024), Main Conference Track.
arXiv: 2410.20527.

**NOTE:** The audit originally listed this as NeurIPS 2023; it is actually NeurIPS 2024.

### b) Methodology Summary
CodeRosetta is an encoder-decoder transformer model designed specifically for translating between
programming languages and their HPC extensions. It uses unsupervised training with three objectives:
Denoising Auto-Encoding (DAE), Back Translation, and a customized pretraining scheme that captures
code semantics and parallel structural nuances. The model is trained on monolingual corpora (no
parallel code pairs needed) and handles C++ <-> CUDA and Fortran <-> C++ translation.

### c) Key Results / Claims
- Outperforms state-of-the-art baselines by 2.9 BLEU and 1.72 CodeBLEU on C++ to CUDA
- Improves compilation accuracy by 6.05% over baselines
- Against general closed-source LLMs: +22.08 BLEU, +14.39 CodeBLEU, +2.75% compilation accuracy
- Demonstrates that specialized, smaller models can outperform general LLMs on HPC translation
- Introduced ParaBLEU metric that accounts for parallel semantics

### d) Verification Approach
**BLEU/CodeBLEU + Compilation accuracy only.** No runtime execution or functional correctness
verification. The "compilation accuracy" metric measures whether translated code compiles
successfully, but does NOT verify that it produces correct output. This is a significant limitation
compared to ParBench's build+run+verify conjunction.

### e) Benchmarks Used
Training uses monolingual code corpora. Evaluation benchmarks are not explicitly Rodinia or HeCBench.
The BabelTower benchmark (Wen et al., ICML 2022) is related work for CUDA translation evaluation.
**No Rodinia/XSBench overlap identified.**

### f) How ParBench Differs
| Dimension | CodeRosetta | ParBench |
|-----------|-------------|----------|
| Model type | Fine-tuned specialized transformer | Evaluates general-purpose LLMs |
| Verification | BLEU + compilation (no runtime) | Build + Run + Verify (conjunction) |
| Metrics | BLEU, CodeBLEU, ParaBLEU, compilation % | Pass/Fail with error taxonomy |
| APIs | C++ <-> CUDA, Fortran <-> C++ | CUDA <-> OMP <-> OpenCL |
| Training | Requires unsupervised training on code | Zero-shot / few-shot prompting |
| Augmentation | None | AST-driven input variation |
| Correctness guarantee | Compilation != correctness | Output verification against reference |

### g) What ParBench Can Cite
- CodeRosetta's finding that specialized models outperform general LLMs on BLEU metrics
- The gap between compilation success and functional correctness (ParBench addresses this)
- ParaBLEU as a parallel-aware translation metric
- Evidence that unsupervised training is viable for HPC code translation
- **Key positioning:** CodeRosetta optimizes translation quality metrics; ParBench measures
  end-to-end functional correctness. These are complementary, not competing, evaluations.

---

## 3. HPC-Coder-V2 (Chaturvedi et al., arXiv 2024)

### a) Full Citation
Aman Chaturvedi, Daniel Nichols, Siddharth Singh, and Abhinav Bhatele.
"HPC-Coder-V2: Studying Code LLMs Across Low-Resource Parallel Languages."
arXiv preprint, arXiv:2412.15178, December 2024.

### b) Methodology Summary
HPC-Coder-V2 conducts an in-depth study of fine-tuning specialized HPC code LLMs across multiple
axes. They fine-tune DeepSeek Coder 6.7B on three instruction datasets (hpc-instruct, oss-instruct,
evol-instruct) to produce models at 1.3B, 6.7B, and 16B parameter scales. The focus is on parallel
code GENERATION (not translation), targeting OpenMP, MPI, MPI+OpenMP, CUDA, HIP, and Kokkos.

### c) Key Results / Claims
- HPC-Coder-V2-6.7B achieves pass@1 of 31.17 on ParEval benchmark
- Best-performing open-source code LLM for parallel code generation under 30B parameters
- Scores comparably to 34B and commercial models (Phind-V2, GPT-4) on parallel code generation
- Demonstrates that domain-specific fine-tuning compensates for smaller model size

### d) Verification Approach
Evaluated on the **ParEval** benchmark for parallel code generation. ParEval presumably includes
compilation and execution checks (pass@k metric implies functional correctness), but the exact
verification methodology is not detailed in the available content.

### e) Benchmarks Used
**ParEval** benchmark -- a parallel code generation benchmark. No overlap with Rodinia or HeCBench.
ParEval tests code generation (writing code from scratch), not code translation.

### f) How ParBench Differs
| Dimension | HPC-Coder-V2 | ParBench |
|-----------|--------------|----------|
| Task | Code generation (from specification) | Code translation (between APIs) |
| Model approach | Fine-tuned specialized LLM | Evaluates off-the-shelf general LLMs |
| APIs | OMP, MPI, CUDA, HIP, Kokkos (6) | CUDA, OMP, OpenCL (3) |
| Benchmarks | ParEval (synthetic problems) | Rodinia, XSBench, HeCBench (real HPC apps) |
| Input | Natural language specification | Existing parallel source code |
| Augmentation | None | AST-driven code transforms |

### g) What ParBench Can Cite
- Evidence that general LLMs underperform on HPC code tasks vs. fine-tuned models
- The low-resource nature of parallel programming languages in training data
- ParEval as a complementary benchmark (generation vs. translation)
- **Positioning:** HPC-Coder-V2 shows fine-tuning helps for generation; ParBench asks whether
  general LLMs can translate between existing parallel implementations without fine-tuning

---

## 4. OMPify (Kadosh et al., IWOMP 2023)

### a) Full Citation
Tal Kadosh, Nadav Schneider, Niranjan Hasabnis, Timothy Mattson, Yuval Pinter, and Gal Oren.
"Advising OpenMP Parallelization via A Graph-Based Approach with Transformers."
19th International Workshop on OpenMP (IWOMP 2023), Bristol, UK, September 2023.
Springer LNCS, doi: 10.1007/978-3-031-40744-4_1. arXiv: 2305.11999.

### b) Methodology Summary
OMPify uses a Transformer-based model with a graph-based representation of source code to detect
and predict OpenMP pragmas and shared-memory attributes in parallel code, given its serial version.
The model leverages the inherent structure of code through graph representations and employs data
augmentation and curriculum learning techniques to improve robustness. It is trained on a corpus
of over 54,000 C/C++ code snippets (Open-OMP-Plus dataset).

### c) Key Results / Claims
- Up to 90% accuracy on NAS, SPEC, and PolyBench OpenMP benchmarks
- Outperforms ChatGPT and PragFormer in F1 score and accuracy
- Graph-based code representation captures structural patterns better than token-based approaches
- Data augmentation and curriculum learning improve generalization

### d) Verification Approach
**Pragma prediction accuracy only.** OMPify evaluates whether the predicted pragma matches the
reference pragma (F1 score, accuracy). It does NOT compile or run the parallelized code to verify
correctness. The evaluation is purely a classification/prediction task, not a functional test.

### e) Benchmarks Used
NAS Parallel Benchmarks, SPEC benchmarks, PolyBench. Training corpus: Open-OMP-Plus (54K+ snippets).
**No Rodinia overlap.**

### f) How ParBench Differs
| Dimension | OMPify | ParBench |
|-----------|--------|----------|
| Task | Pragma prediction (serial -> parallel) | Full API translation (parallel -> parallel) |
| Scope | OpenMP pragma insertion only | CUDA <-> OMP <-> OpenCL full code translation |
| Verification | Pragma matching accuracy | Build + Run + Verify (conjunction) |
| Model | Specialized transformer | General-purpose LLMs |
| Input | Serial code | Parallel code in source API |
| Output | OpenMP pragmas | Complete translated source code |
| Augmentation | Data augmentation for training | AST-driven input augmentation for evaluation |

### g) What ParBench Can Cite
- OMPify demonstrates that pragma prediction is a narrower, more tractable subtask
- ParBench addresses the harder problem: full API-level translation, not just pragma insertion
- The 90% pragma accuracy vs ParBench's 22.44% pass rate illustrates the difficulty gap between
  pragma prediction and full functional translation
- Graph-based code representations as an alternative to token-based approaches
- **Related tools in the OMPify family:** OMPar (OMPify + MonoCoder-OMP pipeline), OMPGPT,
  PragFormer, Graph2Par -- all focus on pragma insertion, none on full API translation

---

## 5. TransCoder (Roziere, Lachaux et al., NeurIPS 2020)

### a) Full Citation
Baptiste Roziere*, Marie-Anne Lachaux*, Lowik Chanussot, and Guillaume Lample.
"Unsupervised Translation of Programming Languages."
Advances in Neural Information Processing Systems 33 (NeurIPS 2020).
arXiv: 2006.03511.

### b) Methodology Summary
TransCoder is the seminal work on unsupervised neural code translation. It trains a seq2seq model
using three unsupervised objectives: Cross-lingual Masked Language Model pretraining, Denoising
Auto-Encoding, and Back Translation. The model is trained exclusively on monolingual source code
from GitHub (no parallel corpora required) and translates between C++, Java, and Python.

### c) Key Results / Claims
- 74.8% computational accuracy (CA@1) for C++ -> Java
- 68.7% CA@1 for Java -> Python
- Significantly outperforms rule-based commercial baselines (j2c, Tangible)
- Only 3.1% of translations match ground truth exactly, but 60.9% pass unit tests
  (demonstrates that reference matching is a poor metric for code translation)
- Increasing beam size improves performance by up to 33.7%

### d) Verification Approach
**Unit test execution.** They built a test set of 852 parallel functions with unit tests to check
functional correctness. The "computational accuracy" (CA) metric measures whether the translated
function produces correct output on all unit tests. This is a genuine functional correctness check,
not just syntax matching. However, these are single-function unit tests, not full-application
build+run+verify as in ParBench.

### e) Benchmarks Used
852 parallel functions sourced from GeeksForGeeks competitive programming problems, with
hand-written unit tests. Languages: C++, Java, Python.
**No HPC code, no Rodinia, no parallel programming APIs.**

### f) How ParBench Differs
| Dimension | TransCoder | ParBench |
|-----------|------------|----------|
| Languages | C++, Java, Python (general purpose) | CUDA, OpenMP, OpenCL (parallel HPC) |
| Code type | Single functions (competitive programming) | Full applications (real HPC benchmarks) |
| Model | Custom unsupervised neural model | General-purpose LLMs (zero-shot) |
| Verification | Unit tests per function | Build + Run + Verify full application |
| Scale | 852 functions | 58+ benchmark specs |
| Domain | General programming | HPC / parallel computing |
| Augmentation | None | AST-driven code transforms |

### g) What ParBench Can Cite
- TransCoder as the foundational work that established unsupervised code translation
- Their insight that reference matching is unreliable (3.1% match vs 60.9% functional pass)
  -- ParBench's conjunction verification builds on this insight
- The CA@k metric as precedent for pass@k evaluation
- TransCoder's limitation to general-purpose languages motivates ParBench's focus on HPC APIs
- CodeRosetta explicitly extends TransCoder's approach to parallel programming (C++/CUDA)
- **TransCoder-ST** (ICLR 2022 follow-up) added automated unit test generation

---

## 6. HPCorpus / MonoCoder (Kadosh et al., 2023-2024)

### a) Full Citation
**HPCorpus + Tokompiler paper:**
Tal Kadosh, Niranjan Hasabnis, Vy A. Vo, Nadav Schneider, Neva Krien, Abdul Wasay, Nesreen Ahmed,
Ted Willke, Guy Tamir, Yuval Pinter, Timothy Mattson, and Gal Oren.
"Scope is all you need: Transforming LLMs for HPC Code."
arXiv preprint, arXiv:2308.09440, August 2023.

**MonoCoder paper (uses HPCorpus):**
Tal Kadosh et al.
"MonoCoder: Domain-Specific Code Language Model for HPC Codes and Tasks."
IEEE HPEC 2024. arXiv: 2312.13322.

### b) Methodology Summary
HPCorpus is a large-scale dataset of HPC code collected from GitHub, containing ~300K repositories,
~70 GB, and ~9 million files across C, C++, and Fortran. The "Scope is all you need" paper introduces
Tokompiler, a specialized tokenizer for HPC code that leverages knowledge of language primitives.
MonoCoder, pre-trained on HPCorpus, is a domain-specific code LLM that is orders of magnitude
smaller than general LLMs but delivers competitive or better performance on HPC code tasks.

### c) Key Results / Claims
- HPCorpus: 300K repos, 70 GB, 9M files, ~155M functions across C/C++/Fortran
- Parallel API distribution in HPCorpus: 45% OpenMP, 27% MPI, 21% CUDA/OpenCL
- Tokompiler increases performance by 230% and training speed by 10%
- MonoCoder (smaller model) matches or beats larger general LLMs on HPC code completion
- Domain-specific pretraining on HPC code is more effective than general pretraining

### d) Verification Approach
**Code completion perplexity/accuracy.** Evaluated on code completion tasks using perplexity scores.
No build+run+verify evaluation. No code translation evaluation.

### e) Benchmarks Used
HPCorpus itself (for training/pretraining). Evaluation is on code completion tasks.
**No Rodinia or HeCBench benchmark overlap.**

### f) How ParBench Differs
| Dimension | HPCorpus/MonoCoder | ParBench |
|-----------|-------------------|----------|
| Contribution | Training dataset + tokenizer + model | Evaluation benchmark + harness |
| Task | Code completion / language modeling | Code translation correctness |
| Verification | Perplexity scores | Build + Run + Verify |
| Purpose | Enable better HPC code models | Evaluate existing models on translation |
| Relationship | Upstream (training data) | Downstream (evaluation) |

### g) What ParBench Can Cite
- HPCorpus statistics as evidence for WHY general LLMs fail on HPC code:
  HPC code is only a tiny fraction of general training data (45% OpenMP, 27% MPI, 21% CUDA in
  HPCorpus, but HPCorpus itself is a niche dataset compared to general code corpora)
- The 45/27/21 API distribution as context for ParBench's API selection (CUDA, OpenMP, OpenCL)
- MonoCoder's finding that domain-specific models outperform general ones as motivation for
  testing whether general LLMs can handle HPC translation without fine-tuning
- **Positioning:** HPCorpus identifies the data scarcity problem; ParBench measures its consequences

---

## 7. TRACY (Gong et al., arXiv 2025)

### a) Full Citation
Zhihao Gong, Zeyu Sun, Dong Huang, Qingyuan Liang, Jie M. Zhang, and Dan Hao.
"TRACY: Benchmarking Execution Efficiency of LLM-Based Code Translation."
arXiv preprint, arXiv:2508.11468, August 2025. Revised March 2026.

**NOTE:** Also appears as "TRACE" (arXiv:2603.16479) -- may be a renamed/updated version.

### b) Methodology Summary
TRACY is the first benchmark focused on evaluating execution EFFICIENCY (not just correctness) of
LLM-translated code. It includes 1,000 efficiency-critical tasks across C++, Java, and Python,
constructed through a two-stage LLM-driven pipeline: (1) stress test generation to amplify
performance differences, and (2) efficiency-oriented task pruning to isolate distinguishing tasks.
Built upon the TransCoder-Test dataset (568 problems from GeeksForGeeks).

### c) Key Results / Claims
- Evaluates 26-28 LLMs (both proprietary and open-source)
- Correctness is NOT a reliable proxy for efficiency: Claude-4-think ranks first on correctness
  but only eighth on time efficiency
- 23.5% of correct translations exhibit pronounced inefficiency
- Inefficiency taxonomy: algorithmic faults (11.9%), language construct mismatches (66.4%),
  resource mismanagement (21.7%)
- Median slowdown: 5.6x for algorithmic faults, 12.0x memory increase for resource mismanagement
- Inference-time prompt strategies bring only modest efficiency improvements

### d) Verification Approach
**Functional correctness + execution efficiency.** TRACY measures both passing rate (functional
correctness via test cases) AND execution time and peak memory usage (efficiency). Uses a "Beyond
score" metric that combines correctness and efficiency. This is more comprehensive than compile-only
but focuses on efficiency rather than correctness as the primary contribution.

### e) Benchmarks Used
Built on TransCoder-Test (Lachaux et al., 2020): 568 problems from GeeksForGeeks.
Languages: C++, Java, Python.
**No HPC code. No parallel programming APIs. No Rodinia/HeCBench.**

### f) How ParBench Differs
| Dimension | TRACY | ParBench |
|-----------|-------|----------|
| Focus | Translation efficiency | Translation correctness |
| Domain | General-purpose (competitive programming) | HPC / parallel computing |
| Languages | C++, Java, Python | CUDA, OpenMP, OpenCL |
| Metrics | Time efficiency, memory usage, Beyond score | Pass/Fail, error taxonomy |
| Code type | Single functions | Full applications |
| Parallelism | None (sequential code) | Parallel code translation |
| Augmentation | Stress test generation | AST-driven code transforms |
| # LLMs tested | 26-28 | 3+ |

### g) What ParBench Can Cite
- TRACY's finding that correctness does not predict efficiency -- ParBench can acknowledge this
  as a known limitation (ParBench measures correctness, not performance, by design)
- The inefficiency taxonomy (algorithmic, construct mismatch, resource) may have HPC analogues
- TRACY extends TransCoder-Test to efficiency; ParBench extends HPC benchmarks to translation
- **Complementary benchmarks:** TRACY = efficiency of general translation, ParBench = correctness
  of HPC translation. Together they cover orthogonal dimensions of code translation quality.
- ParBench's known limitation (wall-clock timing unreliable, see known-issues.md) is partially
  addressable by adopting TRACY-style stress testing in future work

---

## Differentiation Matrix

| Feature | LASSI | CodeRosetta | HPC-Coder-V2 | OMPify | TransCoder | HPCorpus | TRACY | **ParBench** |
|---------|-------|-------------|--------------|--------|------------|----------|-------|-------------|
| **Multi-API (3+)** | No (2) | No (2) | Yes (6) | No (1) | No (3 general) | N/A | No (3 general) | **Yes (3 HPC)** |
| **Build+Run+Verify** | Yes | No (BLEU+compile) | Unclear | No (pragma accuracy) | Yes (unit tests) | No (perplexity) | Yes (tests+efficiency) | **Yes** |
| **Real HPC benchmarks** | Yes (HeCBench) | Unclear | No (ParEval) | Partial (NAS/SPEC) | No (GeeksForGeeks) | N/A (dataset) | No (GeeksForGeeks) | **Yes (Rodinia, XSBench, HeCBench)** |
| **AST augmentation** | No | No | No | Data augmentation | No | No | Stress tests | **Yes** |
| **General-purpose LLMs** | Yes (4 LLMs) | No (custom model) | No (fine-tuned) | No (custom model) | No (custom model) | No (custom model) | Yes (26-28 LLMs) | **Yes (3+ LLMs)** |
| **Full code translation** | Yes | Yes | No (generation) | No (pragma only) | Yes (functions) | No (completion) | Yes (functions) | **Yes (full apps)** |
| **Parallel code** | Yes | Yes (C++/CUDA) | Yes | Yes (OMP only) | No | Yes (training data) | No | **Yes** |
| **Self-correction / agentic** | Yes | No | No | No | No | No | No | **No (by design)** |
| **Error taxonomy** | Partial | No | No | No | No | No | Yes (efficiency) | **Yes (BUILD/RUN/VERIFY)** |
| **Reproducibility controls** | Per-trial | Model weights | Model weights | Model weights | Model weights | Dataset release | Dataset release | **Seeded augmentation + specs** |

### Legend
- "Multi-API (3+)": Supports translation between 3 or more parallel APIs
- "Build+Run+Verify": Actually compiles, runs, and checks output correctness
- "Real HPC benchmarks": Uses established HPC benchmark suites (Rodinia, NAS, HeCBench, etc.)
- "AST augmentation": Systematically varies input code for controlled experiments
- "General-purpose LLMs": Evaluates off-the-shelf LLMs without fine-tuning

---

## Positioning Statement (Draft -- 2-3 Paragraphs)

**Paragraph 1 -- The Landscape:**
Recent work on LLM-based code translation spans a spectrum from general-purpose translation
(TransCoder [Roziere et al., NeurIPS 2020], TRACY [Gong et al., 2025]) to HPC-specific efforts
(LASSI [Dearing et al., CLUSTER 2024], CodeRosetta [TehraniJamsaz et al., NeurIPS 2024],
HPC-Coder-V2 [Chaturvedi et al., 2024]). Complementary work on OpenMP pragma insertion (OMPify
[Kadosh et al., IWOMP 2023]) and HPC training data (HPCorpus [Kadosh et al., 2023]) addresses
adjacent but distinct problems. These efforts differ fundamentally in (1) whether they build
specialized models or evaluate general-purpose LLMs, (2) whether they verify functional correctness
or rely on proxy metrics like BLEU, and (3) whether they target full API-level translation or
narrower subtasks like pragma insertion.

**Paragraph 2 -- ParBench's Niche:**
ParBench occupies a unique position in this landscape as a *benchmark-centric evaluation framework*
for parallel code translation. Unlike LASSI, which builds an agentic self-correction pipeline,
ParBench deliberately measures raw LLM translation capability without iterative refinement --
providing a controlled baseline against which agentic approaches can be compared. Unlike CodeRosetta
and HPC-Coder-V2, which train specialized models, ParBench evaluates general-purpose LLMs to
characterize the gap between general and specialized capability. Unlike OMPify, which addresses
the narrower task of pragma prediction, ParBench evaluates complete API-level code translation
across three HPC APIs (CUDA, OpenMP, OpenCL) with full build+run+verify conjunction verification
on real HPC benchmark suites including Rodinia, XSBench, and HeCBench.

**Paragraph 3 -- Unique Contributions:**
ParBench's AST-driven augmentation pipeline provides a capability not found in any of the surveyed
works: controlled, reproducible variation of input source code that enables systematic study of
how code complexity affects LLM translation success. Combined with its conjunction verification
(stdout_pattern AND exit_code, not just compilation success) and comprehensive error taxonomy
(BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL), ParBench provides the first end-to-end
evaluation infrastructure where the benchmark difficulty is independently adjustable and the
verification is functionally rigorous. The closest comparable work, LASSI, achieves 80-85%
pass rates on 10 HeCBench benchmarks with agentic self-correction; ParBench's 22.44% pass rate
across 468 evaluations (3 models x 54+ specs x multiple directions) without self-correction
establishes a complementary lower bound that quantifies how much of LASSI's improvement comes
from the pipeline versus the underlying model capability.

---

## Additional Notes for Samyak

### Papers NOT in the audit list but found during research -- consider adding:
1. **OMPar** (Scientific Computing Lab, 2024) -- Combines OMPify + MonoCoder-OMP for automatic
   parallelization. More recent than OMPify alone.
2. **OMPGPT** (Euro-Par 2024) -- 0.76B domain-specific model for OpenMP pragma generation,
   outperforms GPT-3.5. Uses Chain-of-OMP prompting strategy.
3. **UniPar** (2025) -- "A Unified LLM-Based Framework for Parallel and Accelerated Code
   Translation in HPC" -- appears very directly relevant, may be concurrent work.
4. **TransCoder-ST** (Roziere et al., ICLR 2022) -- Follow-up with automated unit test generation.
5. **BabelTower** (Wen et al., ICML 2022) -- Learning to auto-parallelize program translation,
   includes CUDA translation evaluation.

### Key comparative talking points for the SC26 paper:
1. **LASSI comparison is the most critical.** Their 80-85% vs our 22.44% will be the first
   question reviewers ask. The answer: agentic self-correction, smaller benchmark set, and
   ParBench measures raw capability by design.
2. **CodeRosetta's verification gap.** They report BLEU/compilation but no functional correctness.
   ParBench's conjunction verification is strictly stronger.
3. **The "fine-tuned vs general" axis.** CodeRosetta, HPC-Coder-V2, OMPify all use fine-tuned
   models. ParBench evaluates general LLMs. This is a deliberate methodological choice, not a
   limitation -- it measures the zero-shot frontier.
4. **HPCorpus explains the data scarcity.** Only 45% of HPCorpus repos use OpenMP -- and HPCorpus
   itself is a niche collection. General LLM training data has far less HPC code.
5. **TRACY is complementary.** They measure efficiency, we measure correctness. Cite approvingly
   and note that efficiency evaluation of HPC code translation is future work.
