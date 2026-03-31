# Eval Campaign Findings Log

> Collected observations from eval runs to incorporate into the SC26 paper.
> Each finding includes the raw evidence and suggested paper section placement.
> Revisit once all eval campaigns are complete.

---

## Finding 1: Multi-File Translation Consistency Failure in OpenCL-to-CUDA (2026-03-31)

**Model:** Qwen 3.5 397B (together-qwen-3.5-397b-a17b)
**Direction:** opencl-to-cuda
**Kernel:** rodinia-lavamd
**Augmentation levels:** L0, L1, L2, L3, L4 — all BUILD_FAIL (15/15 attempts failed)
**Result files:** `results/evaluation/together-qwen-3.5-397b-a17b/rodinia-lavamd-opencl-to-rodinia-lavamd-cuda*.json`
**Cross-model data:** No other models have opencl-to-cuda lavamd results yet. Cannot confirm
whether this is Qwen-specific until other model campaigns complete.
**Critic review:** Adversarial review performed 2026-03-31. Original "semantic renaming" thesis
revised to "multi-file consistency failure" based on per-level evidence.

### Observation

The model translates OpenCL kernel computational patterns to CUDA correctly (`__global__`,
`blockIdx.x`, `threadIdx.x`, `__syncthreads()`) but **fails to produce a compilable
multi-file CUDA program**. The failure modes vary across augmentation levels — this is NOT
a single consistent bug, but a family of related multi-file consistency errors.

### Per-Level Error Taxonomy

| Level | Kernel function name | Naming correct? | Primary failure mode |
|-------|---------------------|-----------------|---------------------|
| L0 | `kernel_gpu_opencl` | NO | Identifier renaming failure (retained source name) |
| L1 | `kernel_gpu_cuda` | YES | Phantom dependencies (`timing.h`, `checkCUDAError`, `setdevice`) |
| L2 | `kernel_gpu_opencl` | NO | Identifier renaming failure (retained source name) |
| L3 | `kernel_gpu_cuda` | YES | Undefined helpers (`setdevice`, `checkCUDAError`) + missing symbol |
| L4 | `kernel_gpu_cuda` | YES | Undefined helpers (`setdevice`) + missing kernel launch symbol |

**Key insight:** The "semantic renaming failure" (keeping `kernel_gpu_opencl` in CUDA code) only
occurs at L0 and L2. At L1, L3, and L4, the model correctly renames the function but fails on
different issues: phantom include paths, undefined helper functions, and (in some attempts)
missing `<<<>>>` kernel launch syntax.

### Retry Behavior (3 attempts per level — consistent pattern)

All 5 levels share the same attempt-1 error: `timing.h` not found (model hallucinating a
non-existent header). Subsequent attempts diverge per level:

| Attempt | Consistent across levels? | Common errors |
|---------|--------------------------|---------------|
| 1 | YES — all 5 levels | `timing.h` not found (phantom dependency) |
| 2 | NO — varies by level | Mix of `checkCUDAError`/`setdevice` undefined, wrong include paths |
| 3 | NO — varies by level | Mix of naming bugs (L0/L2) or dependency bugs (L1/L3/L4) |

Each retry introduces **new error categories** without converging toward a fix. The model
cannot effectively diagnose multi-file compilation failures from compiler error feedback.

### Additional Error: Missing Kernel Launch Syntax

In several attempts (L0 final, L2, L4 attempt 3), the wrapper calls the kernel as a regular
C function (`kernel_gpu_cuda(...)`) rather than using CUDA kernel launch syntax
(`kernel_gpu_cuda<<<grid, block>>>(...)`). This is a separate error class — the model
understands CUDA kernel syntax in the `.cu` file but not the host-side launch protocol.

### Pipeline Verification (CONFIRMED correct)

Pipeline is correctly configured (not a pipeline bug):
- `translation_type: "full_program"` (correct for CUDA targets — both kernel + wrapper rewritten)
- `run_args_mode: "cross_api_source_args"` (correct for cross-API full-program translation)
- `verification_mode: "cross_api_combined_pattern"` (correct)
- `run_arguments_used: null` in all files (pipeline correctly short-circuits at BUILD_FAIL)

### Paper Relevance

**Suggested sections:** Failure Analysis (Section 6), Discussion

**Key points for the paper:**

1. **Failure taxonomy — "multi-file translation consistency failure"**: Full-program
   translations (where the LLM must rewrite both kernel and host code) expose a class
   of errors absent from kernel-only translations: phantom dependencies, cross-file
   identifier inconsistency, undefined helper functions, and missing host-side launch
   syntax. These are distinct from single-file syntax errors or wrong API calls.

2. **Self-repair ineffectiveness on multi-file errors**: The 3-attempt retry cycle does
   not converge toward a fix across any of the 5 augmentation levels (0/15 attempts
   succeed). Each retry introduces new error categories rather than addressing the root
   cause. Self-repair with compiler error feedback appears insufficient for errors that
   require coordinating changes across multiple files.

3. **Hybrid pipeline opportunity (narrower than originally claimed)**: A simple rename
   post-processing pass would only fix L0 and L2 (2/5 levels). A more comprehensive
   hybrid pipeline would need dependency resolution and scaffold generation to address
   L1/L3/L4 failures. Future work should explore multi-stage verification-correction
   pipelines rather than single-pass post-processing.

4. **Augmentation level invariance at the outcome level**: All levels produce BUILD_FAIL,
   but the *failure modes differ* across levels (L0/L2 naming bug vs. L1/L3/L4 dependency
   bugs). Augmentation does not rescue the translation outcome, but it does perturb which
   specific errors the model makes — suggesting the model's failure is not deterministic
   but reflects general difficulty with multi-file CUDA program scaffolding.

5. **No cross-model comparison yet**: This finding is currently single-model (Qwen 3.5 397B).
   Cannot conclude whether the failure pattern is model-specific or direction-specific until
   other models' opencl-to-cuda campaigns complete. Revisit when data is available.

### Related Work Connection

- TransCoder (Roziere et al., 2020): Neural code translators and identifier mapping
  (relevant to L0/L2 renaming failure subcategory)
- SWE-bench: Analogous "small fix, big impact" pattern — but our evidence shows the
  fix is NOT always small (L1/L3/L4 need scaffold-level changes, not just renaming)

---

## Finding 2: Threats to Validity — Comprehensive Adversarial Review (2026-03-31)

**Source:** Adversarial SC26 reviewer simulation (critic agent, Opus)
**Scope:** Full ParBench evaluation methodology, not just lavamd
**Suggested section:** Threats to Validity (Section 7 or 8), partially Discussion
**Status:** Pre-submission checklist — some threats require action, others require prose

### Threat Inventory (Priority-Ordered)

#### TIER 1: Must Address Before Submission (FATAL/MAJOR)

**Threat A: Single-Model Results**
- **Severity:** FATAL without mitigation
- **Issue:** If the paper only reports results from one model, it cannot claim to benchmark
  "LLMs" — it benchmarks one LLM. SC26 requires generalizability.
- **Current state:** Qwen 3.5 397B is the primary model. Historical pilot data exists for
  Claude Sonnet / Groq Llama 70B / Gemini Flash-Lite, but the full campaign infrastructure
  is only validated for Qwen + Gemini (planned).
- **Mitigation:** Minimum 3 models from different providers/architectures before submission.
  Qwen (MoE/Together) + Gemini (dense/Google) + one Anthropic or OpenAI model.
- **Paper treatment:** Report per-model results; do not aggregate across models without
  acknowledging architecture differences.

**Threat B: Rodinia Monoculture (External Validity)**
- **Severity:** MAJOR
- **Issue:** All evaluation results are from Rodinia benchmarks (21 kernels, circa 2009).
  Rodinia is likely in every LLM's training corpus. The benchmark is called "ParBench"
  (implying generality), but the evaluation is effectively "RodiniaBench."
- **Current state:** XSBench specs exist and are verified PASS (4/4). RSBench (4 specs)
  and mixbench (3 specs) are untested. HeCBench curated (25 specs, 23 PASS).
- **Mitigation:** Include at least 5-10 non-Rodinia kernels in the eval campaign.
  XSBench is lowest-hanging fruit (specs already verified).
- **Paper treatment:** Either include multi-suite results OR explicitly scope claims to
  Rodinia and acknowledge generalization as an open question. Option A is much stronger.

**Threat C: Binary PASS/FAIL at a Performance Conference**
- **Severity:** MAJOR
- **Issue:** SC is a *supercomputing* conference. A paper that measures only correctness
  (PASS/FAIL) without performance will raise eyebrows. A 100x-slower-but-correct
  translation gets PASS — is that useful?
- **Current state:** `speedup_ratio` is unreliable (sub-millisecond baselines, wall-clock
  timing). `translated_kernel_time_seconds` is null in all result files.
- **Mitigation options:**
  1. Run `nvprof`/`ncu` on PASS results for CUDA kernel time, `omp_get_wtime()` for OMP
  2. Present failure taxonomy (BUILD/RUN/VERIFY) as a first-class result — this is arguably
     more interesting than raw pass rate and IS within ParBench's current capabilities
  3. Frame the paper as "correctness-first evaluation" with performance as future work
- **Paper treatment:** The failure taxonomy (130 BUILD_FAIL, 120 RUN_FAIL, 46 VERIFY_FAIL,
  132 PASS from current data) tells a richer story than "22.4% pass rate." BUILD_FAIL =
  model doesn't understand target syntax. RUN_FAIL = understands syntax but not semantics.
  VERIFY_FAIL = semantics close but not exact. Present this taxonomy prominently.

**Threat D: Pseudoreplication via Augmentation Levels**
- **Severity:** MAJOR
- **Issue:** Augmentation levels L0-L4 are deterministic transforms of the same source
  (seed=42+level). Treating 5 levels × 18 kernels = 90 as 90 independent samples inflates
  statistical confidence. The correct analysis unit is 18 kernels at L0, with L1-L4 as
  *within-subject repeated measures*.
- **Example:** Reporting "cuda-to-omp: 57.8% (52/90)" when the independent sample is
  actually 18 kernels is pseudoreplication (Hurlbert, 1984).
- **Mitigation:**
  1. Report per-level results separately (L0 pass rate as primary metric)
  2. Use paired tests (McNemar's) for direction asymmetry comparisons on the same kernels
  3. Frame augmentation as a *robustness probe* ("does L3 augmentation degrade pass rate?")
     rather than a sample-size multiplier
  4. Report confidence intervals on the L0 sample (n=18 per direction)
- **Paper treatment:** Primary metric = per-kernel pass@1 at L0. Augmentation results
  presented as a separate robustness analysis, NOT aggregated with L0 to inflate N.
- **Key statistical note:** With n=18 at L0, a 61.1% pass rate has 95% CI of roughly
  36-83%. Cannot claim statistical significance between directions without paired tests.

#### TIER 2: Should Address in Paper (MODERATE)

**Threat 1: Filename Anonymization Reduces Naming Signal**
- **Severity:** MODERATE (defensible)
- **Issue:** Target filenames like `kernel_gpu_cuda.cu` encode naming conventions. Anonymizing
  to `translated_0.cu` removes this signal. The model must infer naming from infrastructure
  headers shown as read-only context.
- **Defense (strong):** Frame as deliberately conservative. "Results are a lower bound on
  translation capability; non-anonymized prompts could only improve pass rates." The
  anonymization prevents training-data contamination.
- **Killer evidence:** Run a 5-10 kernel ablation study (real filenames vs. anonymized).
  If delta is <5pp, the threat is a non-issue. This costs ~50 API calls and <2 hours.
  **Do this before submission — "future work" is the weakest play in academic writing.**
- **Paper treatment:** Acknowledge in Threats to Validity with the "lower bound" framing.
  If ablation is run, report the delta.

**Threat E: Contamination Despite Anonymization**
- **Severity:** MODERATE
- **Issue:** Filenames and kernel names are stripped, but algorithmic structure, struct
  names (`FOUR_VECTOR`, `par_str`, `box_str`), and magic constants
  (`NUMBER_PAR_PER_BOX = 100`) survive anonymization. A model with Rodinia in its training
  data can recognize kernels from struct names alone.
- **Defense:** Augmentation L3-L4 partially addresses this via variable renaming and
  arithmetic transformations. Compare L0 vs. L4 pass rates: if L4 is significantly lower,
  contamination may be contributing to L0 performance. If L0 ≈ L4, surface features
  aren't the driver.
- **Paper treatment:** Acknowledge that full decontamination is impossible without
  rewriting algorithms. Present L0-vs-L4 delta as indirect evidence of contamination effect.

**Threat G: Temperature=0.0 and pass@k Interaction**
- **Severity:** MODERATE
- **Issue:** All results use `temperature: 0.0` (greedy decoding). Multiple samples at
  temperature=0.0 produce identical or near-identical output (modulo API nondeterminism).
  pass@k at temperature=0.0 measures API randomness, not model capability.
- **Mitigation:** If pass@k is reported, must use temperature > 0.0 for k > 1 samples.
  Alternatively, report only pass@1 with temperature=0.0 (standard practice).
- **Paper treatment:** State temperature explicitly. If pass@k is a contribution, use
  appropriate temperature. If not, report pass@1 only.

#### TIER 3: Acknowledge Briefly (MINOR)

**Threat 2: No Explicit API-Mapping Guidance**
- **Severity:** MINOR
- **Issue:** Prompt says "translate OpenCL to CUDA" without mapping rules. But the system
  message says "You are a parallel programming expert specializing in X to Y translation."
  This is a design choice: ParBench measures *internalized API knowledge*, not
  *resourced problem-solving*.
- **Paper treatment:** Frame as intentional. Cite LASSI (Dearing et al., CLUSTER 2024)
  for comparison with agentic self-correction (80-85% vs. ParBench's ~30%).
- **Note:** The self-repair mechanism (compiler error feedback) partially compensates.
  Report pass@1 vs. pass@3 to quantify what error feedback adds.

**Threat F: Stale Eval Summary**
- **Severity:** MINOR (if resolved before submission)
- **Issue:** eval_summary.json may not reflect latest on-disk results (generated before
  pipeline fixes). Pre-fix vs. post-fix results must be clearly separated.
- **Mitigation:** Re-generate summary from actual results before any paper numbers.

**Threat H: Verification Proxy, Not Checksums**
- **Severity:** MINOR
- **Issue:** Most Rodinia specs verify via `stdout_pattern` (e.g., "Total time:") + exit_code.
  This is a proxy for correctness, not a checksum. A translation printing "Total time: 0.000"
  with wrong computational results would PASS.
- **Defense:** XSBench uses real checksums (941535/945990). Rodinia lacks built-in checksums
  for most kernels. The stdout_pattern + exit_code conjunction was validated during S-VERIFY
  (54/60 TRUE PASS, 0 FALSE_PASS).
- **Paper treatment:** Acknowledge as limitation. Note XSBench's stronger verification.

**Threat 3: Truncated Error Feedback**
- **Severity:** NEGLIGIBLE
- **Issue:** Originally cited as 500 chars, but actual truncation is 1500 chars (750 head +
  750 tail via `_head_tail()`). The 500-char figure is for run stderr, not build errors.
- **Paper treatment:** Not worth mentioning. Combine with Threat 2 if space permits.

### Pre-Submission Action Items

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| P0 | Run 3+ models (Qwen + Gemini + 1 more) | ~24h compute | Addresses FATAL Threat A |
| P0 | Include XSBench in eval campaign (5+ kernels) | ~4h | Addresses MAJOR Threat B |
| P1 | Separate L0 from L1-L4 in all reported statistics | ~2h analysis | Addresses MAJOR Threat D |
| P1 | Present failure taxonomy as first-class result | ~4h writing | Addresses MAJOR Threat C |
| P1 | Run filename ablation (5-10 kernels, real vs. anon) | ~2h | Addresses MODERATE Threat 1 |
| P2 | Compute L0-vs-L4 pass rate delta | ~1h analysis | Addresses MODERATE Threat E |
| P2 | Add paired statistical tests (McNemar's) | ~2h | Addresses MAJOR Threat D |
| P3 | Re-generate eval_summary.json from disk | ~10min | Addresses MINOR Threat F |

### Related Work for Threats Section

- Hurlbert (1984): "Pseudoreplication and the Design of Ecological Field Experiments" — 
  foundational paper on why L0-L4 are not independent samples
- LASSI (Dearing et al., CLUSTER 2024): Agentic self-correction benchmark for comparison
  with ParBench's error-feedback-only retry mechanism
- SWE-bench validity critiques (Jimenez et al., 2024): Faced similar questions about
  task specification sufficiency
- TransCoder (Roziere et al., 2020): Neural code translation and contamination risks

---

## Finding 3: Pass@k Campaign Preliminary Results — Self-Repair vs Stochastic Sampling (2026-03-31)

**Model:** Qwen 3.5 397B (together-qwen-3.5-397b-a17b)
**Campaign:** Campaign 2, pass@k sweep (L0 only, temp=0.7, max_retries=1, 3 samples per task)
**Direction analyzed:** cuda-to-omp (batch 1/28, campaign still running)
**Data snapshot:** 100+ pass@k files, 13 complete kernel triplets as of analysis time
**Agent team:** 4 agents (result-analyst, pipeline-investigator, critic, skill-updater)
**Status:** PRELIMINARY — campaign is ~7% complete (batch 1/28). Full results pending
completion of all 28 batches across 6 directions x 5 suites. These findings may be revised.

### Key Finding: Self-Repair Provides 2.3x Improvement

Primary campaign (temp=0.0, max_retries=3) achieves 63.6% pass rate (7/11 kernels) on
cuda-to-omp. Pass@3 at temp=0.7 with no self-repair achieves only 27.3% (3/11 kernels).
The 36.3 percentage point gap (2.3x ratio) demonstrates that self-repair and/or greedy
decoding are critical for translation success.

### Corrected Comparison Table (critic-verified)

| Kernel | Primary L0 (temp=0.0, retries=3) | s0 | s1 | s2 | pass@3? |
|--------|---|---|---|---|---|
| backprop | PASS (3 attempts) | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| bfs | PASS (1 attempt) | PASS | PASS | PASS | YES |
| bptree | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| cfd | PASS (1 attempt) | PASS | BUILD_FAIL | PASS | YES |
| heartwall | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| hotspot | PASS (2 attempts) | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| hotspot3d | PASS (2 attempts) | BUILD_FAIL | PASS | BUILD_FAIL | YES |
| kmeans | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| lavamd | PASS (2 attempts) | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| lud | PASS (2 attempts) | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| mummergpu | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| myocyte | BUILD_FAIL | EXTRACTION_FAIL | BUILD_FAIL | BUILD_FAIL | NO |
| nn | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | NO |

### Pipeline Audit (no bugs found)

- Temperature 0.7 propagated end-to-end to Together API (verified in code)
- max_retries=1 = exactly 1 attempt, no self-repair feedback
- Resume logic correctly handles sample-specific file paths
- No truncation: all completions have finish_reason=stop
- 4 minor concerns: no explicit seeds (relies on API stochasticity), file naming
  divergence in standalone mode, no rate limiter, max_tokens=81920 may exceed
  Together's cap

### Methodological Caveat: Confounded Variables

Temperature (0.0 vs 0.7) and retry count (3 vs 1) changed simultaneously. Cannot isolate
which factor dominates without ablation: (temp=0.0, retries=1) and (temp=0.7, retries=3).

Paper should say: "Self-repair with greedy decoding achieves a 2.3x improvement over
stochastic zero-shot sampling" — attributing to the combined effect.

### Critic Corrections (3 errors caught in initial analyst report)

1. **pass@3 miscalculation:** Initially reported as 50% (4/8) — actual is 27.3% (3/11).
   Analyst missed 3 kernels entirely.
2. **EXTRACTION_FAIL missed:** Analyst claimed zero EXTRACTION_FAIL — myocyte-s0 is
   EXTRACTION_FAIL (model produced 29K tokens but missed master.c).
3. **Build error diversity overstated:** 7/11 triplets have identical outcomes across all
   3 samples, not the diverse pattern initially claimed.

### Data Integrity (all checks pass)

- All pass@k files have temperature=0.7 (confirmed)
- All pass@k files have total_attempts=1 (confirmed)
- All pass@k files have sample_id field (0/1/2)
- verification_mode differs between primary (cross_api_source_pattern) and pass@k
  (cross_api_combined_pattern) — benign pipeline evolution, biases toward pass@k

### Paper Relevance

**Suggested sections:** Section 6 (Results) — subsection on self-repair effectiveness.
Also feeds into Section 7 (Discussion) — implications for LLM-for-HPC tooling.

**Key points for the paper:**

1. **Self-repair is the dominant success factor:** The 2.3x improvement from self-repair
   with greedy decoding over stochastic sampling suggests that iterative compiler-feedback
   loops are more effective than sampling diversity for HPC code translation.
2. **Stochastic sampling alone is insufficient:** At temp=0.7, most kernels fail identically
   across all 3 samples (7/11 triplets identical), indicating the model consistently
   generates the same class of errors regardless of sampling randomness.
3. **Ablation needed for clean attribution:** The confounded temperature/retry design means
   the paper must attribute results to the combined effect, not self-repair alone.

### Administrative Note

This session also updated `.claude/skills/agent-team/SKILL.md` with context discipline
rules (Section 3a) to prevent context rot in agent team teammates — a process improvement
discovered during this analysis when the result-analyst teammate loaded excessive context.

---

## Finding 4: Qwen 3.5 397B CUDA-to-OpenCL 0% Pass Rate — Model Quality Taxonomy (2026-03-31)

**Model:** Qwen 3.5 397B (together-qwen-3.5-397b-a17b)
**Direction:** cuda-to-opencl (kernel-only translation)
**Scope:** First 22 evaluations (bptree, backprop, bfs, cfd, dwt2d, gaussian, heartwall, hotspot)
**Result:** 0/22 PASS (5 RUN_FAIL, 17 VERIFY_FAIL or RUN_FAIL across 3 seeds each)
**Pipeline check:** CONFIRMED CORRECT — not a pipeline issue

### Broader Context (Full Qwen OpenCL Campaign)

From the complete Qwen evaluation across all kernels and directions:
- **OpenCL target: 18.1% pass (39/216)** — worst of all targets
- **OMP target: 44.5% pass (102/229)** — best target
- **CUDA target: 20.9% pass (51/244)** — middle
- OpenCL is **2.5x harder** than OMP for this model

Some kernels DO pass OpenCL translation: hotspot3d (60.9%), hotspot (47.8%), lud (45.0%),
particlefilter (40.0%). The pipeline works correctly for these. The 0% pass on the first
22 evaluations shown in the terminal reflects the specific kernel ordering, not a universal failure.

### Pipeline Verification (NOT a pipeline bug)

All result files show correct kernel-only translation configuration:
- `translation_type: "kernel_only"` (correct — only `.cl` files rewritten)
- `run_args_mode: "kernel_only_target_args"` (correct — host code uses target args)
- `verification_mode: "kernel_only_target_pattern"` (correct — host prints target patterns)
- Build succeeds in ALL cases (host C/C++ compiles fine)
- Failures occur at OpenCL runtime kernel compilation or execution — exactly where bad
  model-generated `.cl` code would fail

The S-OCLFIX kernel-only path is functioning as designed.

### Five Failure Patterns (All Model-Side)

| # | Pattern | Affected Kernels | Error | Root Cause |
|---|---------|-----------------|-------|------------|
| 1 | Missing `__global`/`__local`/`__constant` qualifiers | bptree, heartwall | `pointer arguments to kernel functions must reside in '__global', '__constant' or '__local' address space` | OpenCL requires explicit address space qualifiers on all kernel pointer params. CUDA uses unified virtual addressing — no equivalent concept exists in source. Model must **add** information not present in CUDA code. |
| 2 | CUDA keyword confusion | bfs | `unknown type name '__kernel__'` | Model writes `__kernel__` (CUDA double-underscore convention) instead of `__kernel` (OpenCL). Fundamental API keyword error. |
| 3 | C++ templates in OpenCL C | dwt2d | `use of undeclared identifier 'RDWT97'` + `expected expression` at `<>` | Model copies CUDA template syntax (`RDWT97<WIN_SX, WIN_SY>::run()`) verbatim. OpenCL C is C99-based — no templates, classes, or operator overloading. Correct translation requires manual template expansion into concrete functions. |
| 4 | Algorithmic corruption / infinite loop | gaussian (332s timeout) | Timeout at 300+ seconds (baseline: 0.073s) | Model generates syntactically valid kernel that hangs during execution. Likely broken loop bounds, barrier misuse, or work-group synchronization deadlock. |
| 5 | Runtime kernel build failure | backprop, cfd | `clBuildProgram() => -11` (CL_BUILD_PROGRAM_FAILURE) | Code passes host-side compilation but fails device-side OpenCL kernel compilation. Subtle semantic errors (wrong types, incompatible built-in function usage) that the offline compiler doesn't catch but the GPU driver rejects. |

### Why OpenCL Is Structurally the Hardest Translation Target for LLMs

1. **Address space qualifiers are additive information.** CUDA uses unified virtual addressing —
   no `__global`/`__local`/`__constant` distinction exists. CUDA→OpenCL translation requires
   the model to *infer and add* memory space annotations absent from the source. This is
   fundamentally harder than CUDA↔OMP where the mapping is more mechanical.

2. **OpenCL C is C99, not C++.** CUDA kernels freely use templates, classes, operator
   overloading, and other C++ features. The dwt2d failure exemplifies this: the original
   uses C++ templates that must be manually expanded into concrete C99 functions — a
   non-trivial semantic transformation beyond syntax mapping.

3. **Kernel-only translation amplifies difficulty.** The model only sees the `.cl` kernel
   file, not the host code. It must infer buffer layouts, data types, and memory access
   patterns from kernel signatures alone. For CUDA↔OMP full-program translation, the model
   sees and rewrites the complete program including data flow context.

4. **Training data scarcity.** OpenCL code is far less common than CUDA on GitHub (~5:1
   ratio). Models have less exposure to correct OpenCL idioms, so they fall back to CUDA
   patterns when uncertain — which is exactly what patterns #1 and #2 demonstrate.

### Per-Kernel Difficulty Tiers (from full campaign data)

| Tier | Kernels | OpenCL Pass Rate | Characteristic |
|------|---------|-----------------|----------------|
| Easy | hotspot3d, hotspot | 48-61% | Simple stencil patterns, few pointer params, no C++ features |
| Medium | lud, particlefilter, cfd, bfs, backprop | 25-45% | Moderate complexity, some pointer qualifiers needed |
| Hard | bptree, streamcluster, srad | 10-20% | Complex data structures, many pointer params |
| Impossible | gaussian, dwt2d, heartwall | 0% | C++ templates, complex synchronization, deep pointer chains |

### Paper Relevance

**Suggested sections:** Section 6 (Results — per-direction analysis), Section 7 (Discussion —
why OpenCL is hardest), Threats to Validity (verification limitations for OpenCL)

**Key points for the paper:**

1. **Direction asymmetry is real and large.** The same model (Qwen) achieves 44.5% on
   OMP targets but only 18.1% on OpenCL targets — a 2.5x gap. This is not random
   variation; it reflects structural differences in translation difficulty.

2. **Five-pattern failure taxonomy for OpenCL.** The error patterns above are classifiable
   and systematic, not random. This taxonomy is a contribution: it identifies *specific*
   LLM limitations (address space inference, C++→C99 decomposition, training data gaps)
   rather than just reporting a pass rate.

3. **Per-kernel difficulty is not monotonic.** hotspot3d passes at 61% while gaussian
   passes at 0%, for the same model and direction. Kernel structural complexity
   (templates, pointer depth, synchronization patterns) predicts difficulty better than
   kernel size or algorithmic domain.

4. **No other models have OpenCL results yet.** Cannot determine if this is Qwen-specific
   or universal. If Claude/Gemini show similar patterns, it's a structural limitation of
   current LLMs on OpenCL. If they perform significantly better, it's a Qwen weakness.
   **Cross-model OpenCL comparison is needed before submission.**

5. **Pipeline is validated for OpenCL.** The S-OCLFIX kernel-only path works correctly
   (proven by 18.1% pass rate and per-kernel variation). No pipeline changes needed.

### No Action Required

This is observational data for paper writing. No pipeline fix needed. Cross-model OpenCL
results (when available) will determine whether this finding generalizes beyond Qwen.

---

<!-- Add new findings below this line -->
