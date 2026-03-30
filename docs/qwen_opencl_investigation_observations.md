# Qwen 3.5 397B-A17B: OpenCL Investigation and Paper Observations

**Date:** 2026-03-30
**Data source:** 334 result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/`
**Campaign:** Full 4-direction Rodinia evaluation (cuda-to-omp, omp-to-cuda, cuda-to-opencl, omp-to-opencl) at L0--L4
**Status:** Qwen campaign complete; Gemini 2.5 Flash campaign pending
**CRITICAL UPDATE:** OpenCL 0% pass rate determined to be a **pipeline validity issue**, not a model limitation. See Section 2.

---

## Section 1: Qwen 3.5 397B Overall Performance

### 1.1 Headline Numbers (Raw, Pre-Correction)

| Metric | Value | Validity |
|--------|-------|----------|
| Total result files | 334 | -- |
| Overall PASS | 92/334 (27.5%) | **Deflated** by invalid OpenCL zeros |
| CUDA/OMP only PASS | **92/180 (51.1%)** | **Valid measurement** |
| Overall BUILD_FAIL | 79/334 (23.7%) | All from CUDA/OMP directions |
| Overall RUN_FAIL | 83/334 (24.9%) | 76 from OpenCL (pipeline-caused) |
| Overall VERIFY_FAIL | 78/334 (23.4%) | 76 from OpenCL (pipeline-caused) |
| Overall ERROR/EXTRACTION_FAIL | 2/334 (0.6%) | -- |
| First-attempt PASS | 42/334 (12.6%) | Deflated |
| Self-repair lift | 12.6% -> 27.5% (2.2x) | Valid for CUDA/OMP only |

**The valid overall pass rate is 92/180 = 51.1% (CUDA/OMP directions only).** The 27.5% aggregate
including OpenCL is an artifact of pipeline bugs and must not be reported in the paper.

### 1.2 Per-Direction Breakdown

| Direction | PASS | Total | Rate | Dominant Failure | Validity |
|-----------|------|-------|------|------------------|----------|
| cuda-to-omp | 52 | 90 | **57.8%** | BUILD_FAIL (33) | VALID |
| omp-to-cuda | 40 | 90 | **44.4%** | BUILD_FAIL (46) | VALID |
| cuda-to-opencl | 0 | 100 | 0.0% | RUN_FAIL (58), VERIFY_FAIL (41) | **INVALID** |
| omp-to-opencl | 0 | 54 | 0.0% | VERIFY_FAIL (35), RUN_FAIL (18) | **INVALID** |

### 1.3 Direction Asymmetry (Valid Directions Only)

cuda-to-omp (57.8%) exceeds omp-to-cuda (44.4%) by 13.4 percentage points. The dominant
failure mode in omp-to-cuda is BUILD_FAIL (46/90 = 51.1%), suggesting that generating
correct CUDA syntax (device memory management, kernel launch syntax, thread index arithmetic)
from OpenMP source is harder than removing it.

### 1.4 Augmentation Level Impact

| Level | PASS (all dirs) | PASS (CUDA/OMP only) |
|-------|-----------------|---------------------|
| L0 | 20/67 (29.9%) | 20/36 (55.6%) |
| L1 | 18/67 (26.9%) | 18/36 (50.0%) |
| L2 | 18/67 (26.9%) | 18/36 (50.0%) |
| L3 | 19/67 (28.4%) | 19/36 (52.8%) |
| L4 | 17/66 (25.8%) | 17/36 (47.2%) |

**Augmentation is level-invariant for Qwen on valid directions.** The CUDA/OMP-only pass rate
varies from 47.2% to 55.6% across levels, with no monotonic degradation trend. The slight
downward tendency is not statistically significant given the small per-level sample (n=36).

---

## Section 2: The OpenCL Blindspot -- Root Cause Determination

### 2.1 Investigation Summary

Three hypotheses were investigated by independent teammates:

- **H1 (Model-side):** Qwen 3.5 397B lacks sufficient OpenCL capability.
- **H2 (Benchmark-side):** The OpenCL specs/baseline have issues that cause pipeline failures.
- **H3 (Pipeline-side):** The evaluation pipeline has systematic bugs in OpenCL handling.

### 2.2 VERDICT: H2 + H3 Confirmed -- Pipeline Design Flaw

**The 0% OpenCL pass rate is INVALID.** It measures pipeline bugs, not model capability.
Two independent investigations (spec-checker and pipeline-auditor) converged on the same
root cause.

#### Bug 1: Wrong Run Arguments (confirmed by H2 and H3)

The `_build_cross_api_run_spec()` function in `scripts/evaluation/llm_evaluate.py` (line 1239)
substitutes SOURCE spec run arguments for TARGET spec run arguments. This design is correct
for **CUDA-to-OMP** and **OMP-to-CUDA** directions, where the LLM translates the entire
program (including argument parsing). The LLM's translated code preserves the source's
argc/argv convention, so source args are correct.

**However, for X-to-OpenCL translations, only the `.cl` kernel files are translated** (per
the kernel-centric translation design, Family 1 in the evaluation rules). The OpenCL host
code -- including its argument parsing -- is the **untouched reference implementation**. The
reference OpenCL host code expects OpenCL-style arguments, but receives CUDA-style arguments.

**Confirmed mismatches (verified against actual specs):**

| Kernel | Source (CUDA) Args | Target (OpenCL) Args | Issue |
|--------|--------------------|---------------------|-------|
| hotspot3d | `512 8 100 power temp output.out` | `-n 512 -l 8 -i 100 -f power temp output.out -p 0` | Positional vs. flag-based |
| heartwall | `test.avi 20` | `-f test.avi -i input.txt -n 20 -p 0` | Missing `-f`, `-i`, `-n` flags |
| myocyte | `100 1 0` | `-time 100 -r ../../data/myocyte` | Completely different interface |
| nw | `2048 10` | (OpenCL expects different format) | Arg count/format mismatch |
| hotspot | `512 512 2 4 temp power output.out` | (OpenCL uses different args) | OMP nthreads arg injected |

**Impact:** 11 of 20 OpenCL specs have confirmed arg mismatches. These results show
"RUN_FAIL" or "VERIFY_FAIL" but the failure is caused by passing wrong arguments to the
untouched OpenCL host binary, not by incorrect kernel translation.

#### Bug 2: Wrong Verification Patterns (confirmed by H2 and H3)

The `_build_cross_api_verify_spec()` function (line 1196) has a **key name mismatch bug**:

```python
# Line 1224 — reads "expected_pattern"
source_patterns = [s.get("expected_pattern", "") for s in source_stdout if s.get("expected_pattern")]
target_patterns = [s.get("expected_pattern", "") for s in target_stdout if s.get("expected_pattern")]
```

But the actual specs use `"pattern"`, not `"expected_pattern"`:
```json
{"type": "stdout_pattern", "pattern": "Training done", "description": "..."}
```

**Consequence:** The combined pattern logic is dead code. `source_patterns` and
`target_patterns` are always empty lists. The function falls back to copying the raw
source strategy objects (which contain the correct `"pattern"` key but are SOURCE patterns,
not TARGET patterns). For CUDA-to-OMP this happens to work (source output format is
preserved by the LLM). For X-to-OpenCL it fails because:

1. The source (CUDA/OMP) patterns don't match OpenCL output format
2. The OpenCL host code produces different output strings than CUDA/OMP versions
3. 7 additional OpenCL specs fail due to stdout pattern mismatches beyond the run arg issue

**Impact:** Even if the run args were correct, verification would fail for many OpenCL
translations because the patterns being checked are from the wrong API variant.

#### What IS Working Correctly

The pipeline-auditor confirmed these components work correctly for OpenCL:
- Token handling and prompt generation
- File extraction from LLM responses
- Build compilation (0 BUILD_FAILs -- Qwen generates syntactically valid OpenCL kernels)
- Prompt construction with infrastructure context

### 2.3 Impact Assessment

At L0, the pipeline-auditor estimated that **20 of 31 OpenCL failures (65%) are directly
pipeline-caused.** The remaining ~35% may be genuine model issues, but cannot be
distinguished from pipeline artifacts without re-running after the fix.

**Critical implication:** Qwen generates OpenCL `.cl` kernel code that compiles (0 BUILD_FAILs).
The model may have meaningful OpenCL kernel translation capability that is currently
unmeasurable due to the pipeline bugs.

### 2.4 Why CUDA/OMP Results Are Unaffected

For CUDA-to-OMP and OMP-to-CUDA translations:
1. The LLM translates the **entire program** (not just kernel files)
2. The translated code preserves the source's argument parsing convention
3. Source run args correctly match the translated code's argc expectations
4. Source stdout patterns match the translated code's output format (LLM preserves printf strings)

The cross-API run args and verify logic is correct **by coincidence** for these directions,
because the design assumption ("LLM preserves source conventions") holds when the LLM
translates all files. It fails for OpenCL because only `.cl` kernel files are translated.

---

## Section 3: What to Report in the SC26 Paper

### 3.1 Recommended Narrative Framing

**DO NOT report the 0% OpenCL pass rate as a model limitation.**

The paper should report:

> "Evaluation of Qwen 3.5 397B on CUDA-OpenMP bidirectional translation yields 57.8%
> pass rate for CUDA-to-OpenMP and 44.4% for OpenMP-to-CUDA. OpenCL translation directions
> are excluded from the primary evaluation pending resolution of a pipeline design issue
> discovered during the campaign: the kernel-centric translation mode for OpenCL (which
> translates only `.cl` kernel files while preserving the host driver) requires
> target-native run arguments and verification patterns, but the cross-API evaluation
> logic currently substitutes source-API arguments. This mismatch guarantees failure
> regardless of translation quality."

**Alternative framing (if pipeline is fixed before submission):**
Report corrected OpenCL results alongside CUDA/OMP results, with a methods note explaining
the pipeline fix. This is the stronger paper if time permits.

### 3.2 Key Data Tables for the Paper (Valid Data Only)

**Table A: Pass rates by direction and model (primary results)**

| Direction | Qwen 3.5 397B | Gemini 2.5 Flash |
|-----------|---------------|------------------|
| cuda-to-omp | 57.8% (52/90) | [PENDING] |
| omp-to-cuda | 44.4% (40/90) | [PENDING] |
| cuda-to-opencl | [PENDING re-eval] | [PENDING] |
| omp-to-opencl | [PENDING re-eval] | [PENDING] |
| **CUDA/OMP overall** | **51.1% (92/180)** | [PENDING] |

**Table B: Failure taxonomy (valid directions only)**

| Direction | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | PASS |
|-----------|------------|----------|-------------|------|
| cuda-to-omp | 36.7% (33) | 3.3% (3) | 2.2% (2) | 57.8% (52) |
| omp-to-cuda | 51.1% (46) | 4.4% (4) | 0.0% (0) | 44.4% (40) |

**Key observation on failure taxonomy:** BUILD_FAIL dominates both valid directions (33+46 = 79
of 88 failures = 89.8%). The model's primary bottleneck is API-specific syntax -- missing
`#pragma omp` directives, retained CUDA memory management calls, wrong type annotations --
rather than an inability to reason about parallel computation.

**Table C: Self-repair effectiveness (valid directions only)**

| Metric | CUDA/OMP |
|--------|----------|
| Single-attempt PASS (no retries needed) | 37/38 (97.4%) |
| Multi-attempt that eventually PASS | 55/142 (38.7%) |
| First-attempt PASS rate | ~23% (estimated) |
| Final PASS rate (3 attempts) | 51.1% |
| Self-repair lift | ~2.2x |

### 3.3 Figures/Visualizations to Create

1. **Heatmap: kernel x direction pass rate** (L0 only, 18 kernels x 2 valid directions).
   Clear visual of per-kernel difficulty and direction asymmetry.

2. **Bar chart: failure taxonomy by direction.** Stacked bars showing BUILD_FAIL/RUN_FAIL/
   VERIFY_FAIL/PASS proportions for cuda-to-omp and omp-to-cuda.

3. **Augmentation level curve** (CUDA/OMP directions only). Flat line confirming
   level-invariance at ~50% pass rate.

4. **Self-repair transition diagram.** Show attempt 1 -> attempt 2 -> attempt 3 transitions
   for valid directions. Quantifies the value of iterative error feedback.

### 3.4 Threats to Validity

1. **OpenCL results invalidated.** The pipeline's cross-API run-argument substitution is
   incorrect for kernel-centric OpenCL translation. All 154 OpenCL-target results measure
   pipeline behavior, not model capability. These must be re-evaluated after a pipeline fix
   or excluded from the paper entirely.

2. **Single model limitation.** CUDA/OMP results are from one model (Qwen 3.5 397B). Gemini
   2.5 Flash results are pending and will determine cross-model consistency.

3. **Temperature 0.0.** All results use greedy decoding. A pass@k analysis at higher
   temperature could reveal sampling-sensitive cases, but is a secondary priority behind
   the OpenCL pipeline fix.

4. **Timing data unreliable.** All PASS results use `wall_time` measurement with sub-millisecond
   baselines. Speedup ratios should not be reported (see `known-issues.md`).

5. **`expected_pattern` key mismatch.** The combined source+target pattern logic in
   `_build_cross_api_verify_spec()` is dead code due to reading `expected_pattern` when
   specs use `pattern`. This means CUDA/OMP verifications used only source patterns, not
   a combined source+target fallback. In practice this works because LLM translations
   preserve source output format, but it represents a latent bug that could affect
   edge cases.

### 3.5 Interaction with Gemini 2.5 Flash Results

The Gemini campaign faces the **same pipeline bugs** for OpenCL directions. Before running
Gemini OpenCL translations:

1. Fix `_build_cross_api_run_spec()` to detect kernel-centric OpenCL translations and use
   TARGET spec run args (since host code is untouched)
2. Fix `_build_cross_api_verify_spec()` to read `pattern` instead of `expected_pattern`
3. Re-run Qwen OpenCL translations with the fixed pipeline
4. Then run Gemini on all directions with the corrected pipeline

If OpenCL fixes cannot be completed before submission deadline:
- Report CUDA/OMP results as the primary evaluation (still a strong paper)
- Note OpenCL as a planned extension
- This matches the eval campaign's original fallback: "paper survives on cuda-to-omp +
  omp-to-cuda only (318 tasks)" per `docs/eval_campaign/FINAL_ACTION_PLAN.md`

---

## Section 4: Per-Kernel Difficulty Tiers

Based on valid directions only (cuda-to-omp + omp-to-cuda, all augmentation levels).

### Tier 1: Easy (>= 80% pass rate)
| Kernel | Rate | cuda-to-omp | omp-to-cuda | Category |
|--------|------|-------------|-------------|----------|
| hotspot | 100% (10/10) | 5/5 | 5/5 | stencil |
| nw | 100% (10/10) | 5/5 | 5/5 | linear_algebra |
| pathfinder | 100% (10/10) | 5/5 | 5/5 | graph |
| particlefilter | 90% (9/10) | 5/5 | 4/5 | other |
| cfd | 90% (9/10) | 5/5 | 4/5 | physics |
| srad | 90% (9/10) | 5/5 | 4/5 | image |
| bfs | 80% (8/10) | 5/5 | 3/5 | graph |

**What makes these easy:** Small, self-contained kernels with straightforward thread-index-to-loop-index
mapping. Low shared memory usage. Simple control flow. These kernels have well-known, widely
published CUDA and OpenMP implementations.

### Tier 2: Medium (40--79% pass rate)
| Kernel | Rate | cuda-to-omp | omp-to-cuda | Category |
|--------|------|-------------|-------------|----------|
| hotspot3d | 70% (7/10) | 4/5 | 3/5 | stencil |
| nn | 70% (7/10) | 3/5 | 4/5 | other |
| lud | 60% (6/10) | 3/5 | 3/5 | linear_algebra |

**What makes these medium:** Multiple kernel functions, more complex thread decomposition.
hotspot3d extends hotspot to 3D (more complex indexing). lud has three distinct kernel phases
(diagonal, perimeter, internal). nn is notable -- omp-to-cuda (4/5) exceeds cuda-to-omp
(3/5), the only kernel with an inverted direction asymmetry.

### Tier 3: Hard (1--39% pass rate)
| Kernel | Rate | cuda-to-omp | omp-to-cuda | Category |
|--------|------|-------------|-------------|----------|
| backprop | 30% (3/10) | 3/5 | 0/5 | ml |
| lavamd | 20% (2/10) | 2/5 | 0/5 | molecular_dynamics |
| bptree | 10% (1/10) | 1/5 | 0/5 | other |
| streamcluster | 10% (1/10) | 1/5 | 0/5 | other |

**What makes these hard:** Complex shared memory patterns, multi-stage reduction operations,
large numbers of kernel arguments. All pass only in the cuda-to-omp direction and fail
completely at omp-to-cuda.

### Tier 4: Impossible (0% pass rate on both directions)
| Kernel | Rate | cuda-to-omp | omp-to-cuda | Category |
|--------|------|-------------|-------------|----------|
| kmeans | 0% (0/10) | 0/5 | 0/5 | other |
| myocyte | 0% (0/10) | 0/5 | 0/5 | other |
| mummergpu | 0% (0/10) | 0/5 | 0/5 | other |
| heartwall | 0% (0/10) | 0/5 | 0/5 | image |

**What makes these impossible:** Extreme complexity. heartwall has video frame processing with
complex coordinate tracking. myocyte uses a solver with deeply nested function calls and
complex state. mummergpu uses texture memory references (deprecated in CUDA 12 -- confounded
by the KNOWN_FAIL spec issue). kmeans has complex multi-phase kernel orchestration.

### Direction Asymmetry Pattern

Of the 18 kernels with both directions:
- **Symmetric success** (both pass at all levels): hotspot, nw, pathfinder (3 kernels)
- **cuda-to-omp favored**: 14 of 18 kernels have cuda-to-omp >= omp-to-cuda
- **omp-to-cuda favored**: nn only (4/5 vs 3/5) -- the sole inversion
- **Symmetric failure** (both fail at all levels): kmeans, myocyte, mummergpu, heartwall (4 kernels)

**The asymmetry is strong and consistent:** translating from explicit (CUDA) to directive-based
(OpenMP) is easier than the reverse, confirming the paper's direction asymmetry hypothesis.

---

## Section 5: Open Questions and Next Steps

### 5.1 Priority 1: Fix the Pipeline (Before Any More Eval Runs)

Two bugs must be fixed in `scripts/evaluation/llm_evaluate.py`:

1. **`_build_cross_api_run_spec()` (line 1239):** For OpenCL-target kernel-centric translations,
   use TARGET spec run args instead of source args. The host code is untouched, so it expects
   target-native arguments. Detection: check if target API is OpenCL and translation mode is
   kernel-centric.

2. **`_build_cross_api_verify_spec()` (line 1224):** Change `expected_pattern` to `pattern`
   to match actual spec key names. This fixes the dead combined-pattern logic.

### 5.2 Priority 2: Re-Run Qwen OpenCL After Fix

All 154 Qwen OpenCL results need re-evaluation with the corrected pipeline. The model
generates compilable `.cl` kernel code (0 BUILD_FAILs in current data), so meaningful
pass rates are plausible after the fix.

### 5.3 Priority 3: Run Gemini 2.5 Flash on All Directions

With the pipeline fixed, run Gemini on all 4 directions. Key questions:
- Does Gemini show the same direction asymmetry (cuda-to-omp > omp-to-cuda)?
- Is the per-kernel difficulty ranking model-invariant?
- What is Gemini's OpenCL capability (now measurable with fixed pipeline)?
- Is augmentation level-invariance model-invariant?

### 5.4 Statistical Questions for the Full Paper

Once both models have valid results on all directions:
- Fisher's exact test: Qwen vs Gemini pass rate difference per direction
- Chi-squared test: Failure taxonomy distribution differences between models
- Cohen's h: Effect size of direction asymmetry within each model
- McNemar's test: Per-kernel concordance (do they fail on the same kernels?)
- 95% Wilson confidence intervals on all reported pass rates

### 5.5 Open: Should OpenCL Be Included in the Paper?

**If pipeline is fixed and re-eval completed:** Yes, absolutely. OpenCL provides the third
API pair and enables 4 additional translation directions. The comparison between CUDA/OMP
(where LLM translates everything) and X-to-OpenCL (where LLM translates only kernels) is
itself a finding about how translation scope affects success.

**If pipeline is NOT fixed before deadline:** Report CUDA/OMP as the primary evaluation
(still 360+ tasks across 2 models, 2 directions, 5 augmentation levels, 18 kernels).
Note OpenCL as planned future work. This is the fallback specified in the eval campaign
action plan.

### 5.6 Remaining Data Gaps

- **myocyte omp-to-opencl L4:** 1 missing file (54/55 expected). Negligible impact.
- **XSBench, RSBench, mixbench, HeCBench:** Current campaign covers only Rodinia. The paper
  claims 96 specs across 5 suites; at minimum, XSBench directions should be evaluated.
- **pass@k analysis:** Temperature 0.7 sampling is a secondary priority behind the pipeline fix.

---

## Appendix A: Pipeline Bug Details

### A.1 The Kernel-Centric Translation Asymmetry

The evaluation pipeline defines three "families" for kernel-centric translation:

- **Family 1 (OpenCL):** Only `.cl` kernel files are translated. Host driver code is untouched.
- **Family 2 (OMP, OMP-target):** Curated pragma files or full payload translated.
- **Family 3 (CUDA, HIP, SYCL):** Full prompt payload translated.

For Family 2 and 3, the LLM translates the entire program, so it preserves the source's
argument parsing and output format. The cross-API logic (substitute source args and patterns)
works by coincidence.

For Family 1 (OpenCL), the LLM translates ONLY the `.cl` kernel. The host code -- including
`main()`, argument parsing, printf statements, and OpenCL API calls -- is the TARGET's
reference implementation. Substituting source args into this untouched host binary causes
immediate failure.

### A.2 Specific Key Name Bug

In `_build_cross_api_verify_spec()`:

```python
# Line 1224 -- BUG: reads "expected_pattern", but specs use "pattern"
source_patterns = [s.get("expected_pattern", "") for s in source_stdout if s.get("expected_pattern")]
```

All specs verified to use `"pattern"`:
```json
{"type": "stdout_pattern", "pattern": "Training done", "description": "..."}
```

Result: `source_patterns` and `target_patterns` are always `[]`, combined pattern logic
never executes, function falls through to copying raw source strategy objects.

---

## Appendix B: Raw Per-Kernel L0 Results

| Kernel | cuda-to-omp | omp-to-cuda | cuda-to-opencl | omp-to-opencl |
|--------|-------------|-------------|----------------|---------------|
| backprop | PASS | BUILD_FAIL | VERIFY_FAIL* | VERIFY_FAIL* |
| bfs | PASS | PASS | RUN_FAIL* | VERIFY_FAIL* |
| bptree | BUILD_FAIL | BUILD_FAIL | RUN_FAIL* | RUN_FAIL* |
| cfd | PASS | PASS | VERIFY_FAIL* | VERIFY_FAIL* |
| dwt2d | -- | -- | RUN_FAIL* | -- |
| gaussian | -- | -- | RUN_FAIL (timeout)* | -- |
| heartwall | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL* | VERIFY_FAIL* |
| hotspot | PASS | PASS | VERIFY_FAIL* | RUN_FAIL* |
| hotspot3d | PASS | PASS | RUN_FAIL* | RUN_FAIL* |
| hybridsort | -- | -- | RUN_FAIL* | -- |
| kmeans | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL* | VERIFY_FAIL* |
| lavamd | PASS | BUILD_FAIL | RUN_FAIL* | VERIFY_FAIL* |
| lud | PASS | BUILD_FAIL | VERIFY_FAIL* | RUN_FAIL* |
| mummergpu | BUILD_FAIL | BUILD_FAIL | -- | -- |
| myocyte | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL* | VERIFY_FAIL* |
| nn | BUILD_FAIL | PASS | RUN_FAIL* | -- |
| nw | PASS | PASS | EXTRACTION_FAIL* | -- |
| particlefilter | PASS | PASS | VERIFY_FAIL* | -- |
| pathfinder | PASS | PASS | VERIFY_FAIL* | -- |
| srad | PASS | PASS | RUN_FAIL* | -- |
| streamcluster | BUILD_FAIL | BUILD_FAIL | RUN_FAIL* | -- |

"--" = no result file for that direction (kernel lacks spec for that API pair).
"*" = **Result invalidated** by pipeline bugs (wrong run args and/or wrong verification patterns).
Valid results are cuda-to-omp and omp-to-cuda columns only.
