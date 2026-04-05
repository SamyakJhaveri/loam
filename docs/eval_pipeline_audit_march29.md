<!-- generated-by: gsd-doc-writer -->
# Evaluation Pipeline Audit — 2026-03-29

> **Line numbers updated 2026-04-05 to reflect current codebase.**

> **Context:** 4-agent investigation of 207 Qwen 3.5 (397B-A17B, via Together AI) eval
> results. Triggered by suspiciously low pass rates (14%) and high EXTRACTION_FAIL counts
> (39/207). All findings verified against source code and result JSON files.
>
> **Purpose:** This document records investigation findings, decisions, and rationale for
> the SC26 paper's methodology and threats-to-validity sections.

---

## 1. Investigation Summary

On 2026-03-29, a 4-agent investigation team was assembled to analyze the first Qwen 3.5
evaluation campaign results. The campaign used the Together AI provider with model
`Qwen/Qwen3.5-Coder-Instruct-397B-A17B` (a 397B-parameter Mixture-of-Experts model with
17B active parameters).

**Initial claimed results:** 29/207 = 14.0% overall pass rate.

**Investigation agents:**
1. **EXTRACTION_FAIL investigator** — analyzed 39 EXTRACTION_FAIL results for root cause
2. **False positive auditor** — audited all 29 claimed PASS results for correctness
3. **Kernel mapping analyst** — checked `translation_targets` breadth across all specs
4. **Together AI configuration researcher** — verified API parameters and model behavior

**Post-investigation corrected results:** 22/207 = 10.6% overall pass rate (7 false
positives downgraded to VERIFY_FAIL).

---

## 2. Findings (with Evidence)

### Finding 1: `max_tokens=16384` caused 28 EXTRACTION_FAILs

**Root cause:** All four LLM providers (Anthropic, Groq, Gemini, Together AI) used
`max_tokens=16384`. Multi-file kernels with large translation targets exhausted the
completion token budget before producing all expected files.

**Affected kernels (worst cases):**
- `myocyte` — 16 files in original `translation_targets`, largest prompt payload
- `mummergpu` — 9 files in original `translation_targets`
- `heartwall` — 3 files, still hit limit due to large kernel size

**Evidence:** 28 of 39 EXTRACTION_FAIL results had `finish_reason="length"` on at least
one attempt, indicating the LLM's response was truncated before completion.

**Fix applied:** Raised `max_tokens` from 16384. Per-provider values in
`scripts/evaluation/llm_evaluate.py`: Anthropic=32768 (line 794), OpenAI=32768 (line 829),
Azure=32768 (line 880), Groq=32768 (line 915), Gemini=65536 (line 949),
Together=81920 (line 993).

**Verification:** All six `max_tokens` occurrences in `llm_evaluate.py` are confirmed at their
respective per-provider values.

---

### Finding 2: Qwen thinking tokens leaked into extracted code

**Root cause:** Despite passing `chat_template_kwargs: {"enable_thinking": False}` via the
Together AI OpenAI-compatible client, at least 1 confirmed result contained thinking
artifacts in the extracted code.

**Evidence (backprop-omp-L1):** The extracted `backprop.c` file contained a `</think>` tag
at character position 30187 of 30197, along with 221 lines of natural-language reasoning
interleaved with or preceding the code. This NL contamination caused a BUILD_FAIL (the
compiler cannot parse English prose in a `.c` file).

**Scope:** Only 1 file was confirmed contaminated. The `enable_thinking=False` parameter
is the correct approach per Together AI documentation, making this an edge case rather
than a systematic failure. However, the risk is non-zero for any model with thinking
capability.

**Fix applied:** Added `strip_think_tags()` function at line 1033 of `llm_evaluate.py`.
The function handles three cases:
1. **Complete blocks:** `<think>...</think>` anywhere in the response (regex with `re.DOTALL`)
2. **Dangling close tag:** `</think>` at the start with no matching `<think>` (opening tag
   was in a prior chunk or response started mid-thought)
3. **Unclosed open tag:** `<think>...` at the end with no matching `</think>` (response
   truncated mid-thought)

The function is called on **all** LLM responses at line 1508, before code extraction:
```python
response_text = strip_think_tags(llm_result["response_text"])
```

**Design rationale:** Belt-and-suspenders defense. The provider-side `enable_thinking=False`
is the primary control; `strip_think_tags()` is the fallback. Applied to all providers,
not just Together AI, because any reasoning model could exhibit similar leakage.

---

### Finding 3: 7 false positive PASS results

The false positive auditor examined all 29 claimed PASS results and identified 7 that
should not have passed verification.

#### 3a. Five `backprop-opencl` false positives (L0 through L4)

**Mechanism:** The LLM-translated OpenCL kernel file (`.cl`) failed to compile at runtime
via `clBuildProgram()`, which returned error code `-11` (CL_BUILD_PROGRAM_FAILURE). However,
the host program caught the OpenCL error and continued execution. The host-side computation
produced output matching the `stdout_pattern`, and the process exited with code 0.

**Why verification missed it:** The `stdout_pattern + exit_code` conjunction verified:
(a) exit code was 0 (true — host caught the error), and (b) stdout matched the pattern
(true — host printed expected output from CPU-side fallback). Neither check detected that
the *translated parallel kernel* never executed.

**Implication for SC26 paper:** This reveals a fundamental limitation of black-box
verification for OpenCL workloads: OpenCL's runtime kernel compilation means kernel
failures are not always detectable via exit code or stdout pattern alone. The host program
may gracefully degrade to CPU execution.

#### 3b. One `lud-omp-L3` false positive

**Mechanism:** The translated file included `<omp.h>` but contained zero `#pragma omp`
directives. The code was entirely sequential, producing correct output by running the
algorithm on a single thread.

**Why verification missed it:** Sequential code produces correct results — the verification
only checks *correctness*, not *parallelism*. This is a correct translation in terms of
functional equivalence but a failed translation in terms of the research question (can the
LLM produce *parallel* code?).

**Implication for SC26 paper:** This is a threats-to-validity item. Our verification checks
functional correctness, not parallelism. A future enhancement could check for `#pragma omp`
presence or measure speedup vs. sequential baseline.

#### 3c. One `particlefilter-omp-L2` false positive

**Mechanism:** The translated `particlefilter_float.cpp` had a race condition in the
`likelihood_kernel` function. The OpenMP parallel loop wrote to shared `weights[]` array
without proper synchronization, corrupting the particle filter's probability estimates.
The final `XE` value was `1.93e55` (expected approximately 48 based on reference output).

**Why verification missed it:** The `stdout_pattern` matched the string
`"ENTIRE PROGRAM TOOK"` which the program always prints regardless of numerical accuracy.
The exit code was 0. The numerical corruption was invisible to pattern-based verification.

**Implication for SC26 paper:** Pattern-based verification cannot fully validate numerical
correctness. For numerically sensitive kernels, future work could add tolerance-based
output comparison. This is explicitly a threat to validity.

#### Fix applied: stdout error detection

Added `_check_stdout_error_indicators()` function at line 1187 of `llm_evaluate.py`. After
a result passes `stdout_pattern + exit_code` verification, stdout is scanned for known
error indicators:

| Pattern | Reason |
|---------|--------|
| `clBuildProgram\s*\(\)\s*=>\s*-\d+` | OpenCL kernel build failure |
| `clCompileProgram\s*\(\)\s*=>\s*-\d+` | OpenCL kernel compile failure |
| `Segmentation fault` | Segfault in stdout |
| `CUDA error:` | CUDA runtime error |
| `cudaError` | CUDA error |

If any pattern matches, the result is downgraded from PASS to VERIFY_FAIL with error
message `"False positive rejected: {reason}: {matched_text}"`.

**Note:** This fix catches the 5 `backprop-opencl` cases (clBuildProgram) but does NOT
catch the `lud-omp-L3` (sequential code) or `particlefilter-omp-L2` (numerical corruption)
cases. Those require different detection strategies (parallelism checking and numerical
tolerance, respectively) that are documented as future work.

**Corrected pass rate:** 29 - 7 = 22 genuine PASS results. 22/207 = 10.6%.

---

### Finding 4: 11 EXTRACTION_FAILs from model omission (not truncation)

**Root cause:** Qwen completed its response naturally (`finish_reason="stop"`) but only
produced 1 of 2+ expected files. The model chose not to generate the second file rather
than being cut off.

**Affected kernels (all 2-file targets):**
- `hotspot3d` (kernel + driver)
- `particlefilter` (multiple source files)
- `srad` (kernel + driver)
- `nw` (kernel + driver)

**Classification:** This is a model capability limitation, not a pipeline bug. The LLM
understood the instruction to produce multiple files but failed to follow through. The
4-tier extraction system (Tier 1: `filename=X` annotation, Tier 1.5: space-separated
filename, Tier 2: fuzzy filename match, Tier 3: single-file fallback) correctly identified
that not all target files were present and reported EXTRACTION_FAIL.

**Implication for SC26 paper:** EXTRACTION_FAIL should be subdivided in the error taxonomy:
- **Truncation** (finish_reason="length"): pipeline limitation, fixable with higher token budget
- **Model omission** (finish_reason="stop"): model capability gap, not fixable by pipeline changes

---

### Finding 5: 0% omp-to-cuda pass rate

All 90 omp-to-cuda translation attempts failed across all kernels and augmentation levels.
Failure breakdown:
- BUILD_FAIL: most common (LLM produces syntactically invalid CUDA)
- EXTRACTION_FAIL: second most common (LLM omits kernel files)
- RUN_FAIL: occasional (compiles but segfaults)
- VERIFY_FAIL: rare (runs but wrong output)

**Interpretation:** Qwen 3.5 (397B-A17B) cannot synthesize CUDA code from OpenMP input.
This is a genuine model limitation. CUDA requires explicit memory management
(`cudaMalloc`, `cudaMemcpy`, `cudaFree`), kernel launch syntax (`<<<blocks, threads>>>`),
and thread index arithmetic (`threadIdx.x + blockIdx.x * blockDim.x`) that must be
generated from scratch — not merely translated from OpenMP pragmas. The OMP-to-CUDA
direction is architecturally harder than CUDA-to-OMP because it requires *adding* GPU
infrastructure rather than *removing* it.

**Comparison:** In the 3-model evaluation (claude-sonnet, gemini-flash-lite, groq-llama),
omp-to-cuda was also the hardest direction but not 0%. This suggests Qwen 3.5 has
significantly weaker CUDA generation capability than the other evaluated models.

---

### Finding 6: Multi-file `translation_targets` too broad

**Observation:** Some CUDA and OMP specs included ALL source files as `translation_targets`,
while OpenCL specs correctly narrowed targets to just `.cl` kernel files.

**Problem:** Asking the LLM to translate infrastructure files (Makefiles, utility code,
I/O helpers) that don't contain parallel constructs conflates "translate the parallel
kernel" with "reproduce the entire codebase." This wastes tokens and creates unnecessary
EXTRACTION_FAIL risk (the LLM must produce more files, increasing the chance of omission
or truncation).

**Specific cases identified and fixed (see Decisions D4-D7 below):**
- `particlefilter-cuda`: 2 files → 1 file (dropped irrelevant executable)
- `cfd-cuda`: 4 files → 1 file (dropped 3 separate-executable files)
- `myocyte-cuda`: 16 files → 2 files (kept only `__global__` kernel files)

---

## 3. Decisions Made (with Rationale)

### D1: Raise `max_tokens` from 16384 (per-provider values)

**Rationale:** 16384 was insufficient for multi-file kernels. Values were raised per provider:
Anthropic/OpenAI/Azure/Groq=32768, Gemini=65536, Together=81920. 32768 is Qwen's official
recommended default; Gemini and Together AI support higher limits.

**Impact:** Eliminates truncation-caused EXTRACTION_FAILs for most kernels. The exception
may be `myocyte` with its deep include chain, but the spec narrowing (D6) reduces this
risk significantly.

**Trade-off:** Higher token costs per API call (~2x worst case). Acceptable given that the
alternative is systematically failing on multi-file kernels.

**Implementation:** 6 lines changed in `llm_evaluate.py` (lines 794, 829, 880, 915, 949, 993).

---

### D2: Strip think tags from all LLM responses

**Rationale:** Belt-and-suspenders defense against reasoning model think-tag leakage. The
`enable_thinking=False` parameter is the correct primary control, but the evidence shows
it is not 100% reliable. Stripping think tags from all responses prevents natural-language
contamination from causing BUILD_FAILs regardless of provider or model.

**Impact:** Eliminates thinking-contamination BUILD_FAILs. Applied universally (all
providers, all models) because any reasoning-capable model could exhibit leakage.

**Trade-off:** Minimal. The regex is fast and only affects responses that actually contain
think tags. No false positive risk — legitimate code would never contain `<think>` tags.

**Implementation:** `strip_think_tags()` function added at line 1033 of `llm_evaluate.py`.
Called at line 1508, before code extraction.

---

### D3: Add stdout error detection to reject false positives

**Rationale:** The `stdout_pattern + exit_code` conjunction verification cannot distinguish
between "program ran correctly" and "program caught a runtime error but continued
gracefully." Error strings in stdout indicate runtime failures even when `exit_code=0`.

**Patterns checked** (at line 1178 of `llm_evaluate.py`):
- `clBuildProgram() => -N` — OpenCL kernel build failure
- `clCompileProgram() => -N` — OpenCL kernel compile failure
- `Segmentation fault` — Segfault captured in stdout
- `CUDA error:` — CUDA runtime error
- `cudaError` — CUDA error (alternate format)

**Impact:** Prevents 5+ known false positives (the backprop-opencl cases). Produces more
conservative but more honest pass rates.

**Trade-off:** Could theoretically reject a genuine PASS if the program prints "error" as
part of normal diagnostic output. The patterns are specific enough (e.g., `clBuildProgram`
with a negative return code, not just the word "error") to minimize false rejection risk.

**Limitations:** Does NOT catch:
- Sequential-code false positives (lud-omp-L3 case): would require `#pragma omp` presence check
- Numerical corruption (particlefilter-omp-L2 case): would require tolerance-based output comparison
These are documented as future work and threats to validity.

**Implementation:** `_check_stdout_error_indicators()` function at line 1187, called at
line 1694 after initial PASS determination.

---

### D4: Narrow `particlefilter-cuda` translation_targets to 1 file

**Before:** `["ex_particle_CUDA_float_seq.cu", "ex_particle_CUDA_naive_seq.cu"]`
**After:** `["ex_particle_CUDA_float_seq.cu"]`

**Rationale:** `ex_particle_CUDA_naive_seq.cu` builds a different executable
(`particlefilter_naive`), not the spec's target executable (`particlefilter_float`).
Asking the LLM to translate an irrelevant file wastes tokens and creates unnecessary
EXTRACTION_FAIL risk.

---

### D5: Narrow `cfd-cuda` translation_targets to 1 file

**Before:** `["euler3d.cu", "euler3d_double.cu", "pre_euler3d.cu", "pre_euler3d_double.cu"]`
**After:** `["euler3d.cu"]`

**Rationale:** The 3 dropped files (`euler3d_double.cu`, `pre_euler3d.cu`,
`pre_euler3d_double.cu`) each compile to separate executables. Only `euler3d.cu` matches
the spec's `make euler3d` build command and the `euler3d.out` output executable.

---

### D6: Narrow `myocyte-cuda` translation_targets to 2 files

**Before:** 16 files (full source tree including all `__device__` helpers and infrastructure)
**After:** `["kernel.cu", "solver_2.cu"]`

**Rationale:** These are the only 2 files with `__global__` kernel definitions. The other
14 files are `__device__` helper functions and infrastructure code. The research question
is whether the LLM can translate parallel kernel code — not whether it can reproduce a
16-file include chain verbatim.

**Caveat:** The 14 helper files contain `__device__` functions called by the kernels. If
the LLM changes function signatures in the kernel files, the build may fail due to
mismatched declarations in the unchanged helper files. This is an *acceptable* failure
mode — it reveals whether the LLM understands cross-file API contracts. It is
architecturally different from the previous failure mode (EXTRACTION_FAIL due to token
exhaustion on 16 files).

---

### D7: Keep kernel+driver pairs (Category 3) as 2-file targets

**Affected specs:** `srad-cuda` (2 files), `nw-cuda` (2 files), `hotspot3d-cuda` (2 files),
`heartwall-cuda` (3 files, TBD for further narrowing), `lud-cuda` (2 files),
`backprop-cuda` (2 files).

**Rationale:** For CUDA-to-OMP translation, both the kernel definitions file *and* the
CUDA API driver code must change. The kernel file contains `__global__` functions; the
driver file contains `<<<blocks, threads>>>` launch syntax, `cudaMalloc`, `cudaMemcpy`,
etc. Translating only the kernel file would produce code that cannot be launched (the
driver still has CUDA-specific launch syntax).

Two files is a reasonable ask for any LLM. The multi-file EXTRACTION_FAILs at this scale
are model omission issues (Finding 4), not token budget issues.

---

### D8: Delete all previous Qwen results and re-run after fixes

**Rationale:** The combination of 7 false positives, 28 truncation-caused failures, and 1+
thinking-contaminated results makes the existing 207-result dataset unreliable for
publication. A clean re-run with the fixed pipeline produces trustworthy, publishable data.

**Protocol:**
1. Run small pilot first (2-3 kernels, L0 only) to verify fixes work end-to-end
2. Confirm: no truncation on multi-file kernels, no think-tag contamination, no false
   positives on OpenCL specs
3. Full campaign: all kernels, all augmentation levels, both directions

**Trade-off:** API cost for re-running 207+ evaluations. Justified because publishing data
with known false positives would undermine the paper's credibility. The cost of re-running
is far less than the cost of a reviewer discovering false positives post-submission.

---

## 4. Paper Implications

### 4.1 Methodology Section

The SC26 paper's methodology section should describe the following pipeline features,
which were added or refined as a result of this investigation:

**4-tier code extraction system:**
- Tier 1: Fenced code blocks with `filename=X` annotation (Claude/GPT style)
- Tier 1.5: Fenced blocks with space-separated filename (`lang filename.ext`; Llama style)
- Tier 2: Filename mentioned near a code fence (fuzzy match within N lines)
- Tier 3: Single target file + single code block (fallback for simple translations)

**Think-tag stripping** as a provider-specific preprocessing step. Reasoning models may
leak thinking tokens despite API-level disabling. The pipeline strips `<think>...</think>`
blocks before code extraction as a defense-in-depth measure.

**Stdout error detection** as a post-verification sanity check. After `stdout_pattern +
exit_code` verification passes, stdout is scanned for known runtime error indicators
(OpenCL build failures, CUDA errors, segfaults). This catches cases where the host program
handles errors gracefully but the translated kernel never actually executed.

**`max_tokens` configuration:** The pipeline uses per-provider max completion tokens:
Anthropic/OpenAI/Azure/Groq=32768, Gemini=65536, Together AI=81920. These values are
sufficient for single-file and 2-file translations but may be insufficient for kernels
with deep include chains (e.g., myocyte's full 16-file tree). The kernel-centric
translation design (narrowing `translation_targets` to kernel files only) mitigates this
by reducing the number of files the LLM must produce.

**Kernel-centric translation design:** The LLM translates only kernel files (files
containing `__global__` functions or `#pragma omp parallel` directives), not the full
project. Infrastructure code (I/O, Makefiles, utilities) remains unchanged in the target
directory.

### 4.2 Threats to Validity

The following threats should be acknowledged in the paper:

**T1: Pattern-based verification cannot fully validate numerical correctness.**
The particlefilter-omp-L2 false positive demonstrates that `stdout_pattern` matching
cannot detect numerical corruption. A translated kernel that produces `XE=1.93e55` instead
of `XE~48` still matches the pattern `"ENTIRE PROGRAM TOOK"`. Tolerance-based output
comparison would catch this but is not implemented in the current pipeline. (Mitigation:
manual inspection of a sample of PASS results; this threat is explicitly acknowledged.)

**T2: OpenCL's runtime kernel compilation creates an undetectable failure mode.**
When an OpenCL `.cl` kernel fails to compile at runtime, the host program may continue
with CPU-side fallback code, producing "correct" output that passes verification. The
stdout error detection (D3) partially mitigates this for `clBuildProgram` failures, but
other runtime failures may not produce detectable error strings.

**T3: Verification checks correctness, not parallelism.**
The lud-omp-L3 case demonstrates that a purely sequential translation (no `#pragma omp`
directives) produces correct output and passes verification. Our results may include
translations that are functionally correct but not actually parallel. (Mitigation: for the
paper, we could add a post-hoc `#pragma omp` presence check on PASS results and report
the parallelism rate separately from the correctness rate.)

**T4: `max_tokens` limits constrain maximum translation complexity.**
Multi-file kernels with deep `#include` chains (myocyte: 16 files) may be fundamentally
beyond single-prompt translation within typical token budgets. The kernel-centric design
mitigates this by narrowing targets, but some information loss is possible when the LLM
cannot see all helper files.

**T5: EXTRACTION_FAIL conflates pipeline limitations with model limitations.**
The EXTRACTION_FAIL category includes both truncation failures (pipeline constraint,
`finish_reason="length"`) and omission failures (model limitation, `finish_reason="stop"`).
These have different causes and implications. The paper should report them separately.

**T6: Model thinking behavior is not fully controllable.**
Despite API-level controls (`enable_thinking=False`, `reasoning_effort="none"`), reasoning
models may leak thinking tokens. The pipeline's `strip_think_tags()` function mitigates
this, but the possibility of subtle contamination (e.g., thinking that influences code
style without visible tags) cannot be fully ruled out.

### 4.3 Error Taxonomy for Results Section

The paper should use a refined 5-category taxonomy with subcategories:

| Status | Definition | Subcategories |
|--------|-----------|---------------|
| **PASS** | Translated code builds, runs, and produces correct output verified by stdout_pattern + exit_code + error detection | — |
| **EXTRACTION_FAIL** | Pipeline could not extract all expected files from LLM response | Truncation (finish_reason="length") vs. Omission (finish_reason="stop") |
| **BUILD_FAIL** | Extracted code fails to compile | Missing headers, syntax errors, wrong API calls, think-tag contamination |
| **RUN_FAIL** | Code compiles but crashes at runtime | Segfault, timeout, wrong arguments |
| **VERIFY_FAIL** | Code runs but produces incorrect output, or stdout contains error indicators | Wrong numerical output, runtime errors caught by error detection |

**Corrected Qwen 3.5 results (post-investigation):**

| Category | Count | Percentage |
|----------|-------|-----------|
| PASS | 22 | 10.6% |
| BUILD_FAIL | ~100 | ~48.3% |
| EXTRACTION_FAIL | 39 | 18.8% |
| RUN_FAIL | ~20 | ~9.7% |
| VERIFY_FAIL | ~26 | ~12.6% |

(Note: Approximate counts for BUILD_FAIL/RUN_FAIL/VERIFY_FAIL pending exact recount.
The 7 former PASS results are reclassified as VERIFY_FAIL: 5 backprop-opencl + 1 lud-omp-L3
+ 1 particlefilter-omp-L2.)

---

## 5. Timeline

| Time (approx.) | Event |
|-----------------|-------|
| 2026-03-29 ~19:00 UTC | Investigation started; 4 agents launched |
| ~19:20 UTC | 4 investigation agents completed initial analysis |
| ~19:26 UTC | 3 follow-up agents completed (kernel mapping, Together AI research, particlefilter audit) |
| ~19:27 UTC | Pipeline fixes implemented: max_tokens raised, think stripping added, error detection added |
| ~19:30 UTC | Spec narrowing implemented: particlefilter-cuda, cfd-cuda, myocyte-cuda |
| TBD | Pilot test: 2-3 kernels at L0 to verify fixes |
| TBD | Old Qwen results deleted |
| TBD | Full re-run campaign with fixed pipeline |

---

## 6. Files Modified

### Pipeline code
- `scripts/evaluation/llm_evaluate.py`
  - Lines 794, 829, 880, 915, 949, 993: `max_tokens` raised (Anthropic/OpenAI/Azure/Groq=32768, Gemini=65536, Together=81920)
  - Lines 1033-1058: `strip_think_tags()` function added
  - Line 1508: `strip_think_tags()` call before code extraction
  - Lines 1178-1193: `_STDOUT_ERROR_PATTERNS` and `_check_stdout_error_indicators()` added
  - Lines 1688-1702: Error detection applied after initial PASS determination

### Spec files
- `specs/rodinia-particlefilter-cuda.json`: `translation_targets` narrowed to 1 file
- `specs/rodinia-cfd-cuda.json`: `translation_targets` narrowed to 1 file
- `specs/rodinia-myocyte-cuda.json`: `translation_targets` narrowed to 2 files

### This document
- `docs/eval_pipeline_audit_march29.md`: This audit record

---

## 7. Cross-References

- **Verification strategy:** `results/evaluation/reverification_analysis.md` — S-VERIFY session
- **Kernel-centric translation design:** `docs/design/kernel_centric_translation.md` — Section 14
- **Known issues:** `.claude/rules/known-issues.md` — KNOWN_FAIL specs, timing limitations
- **Evaluation rules:** `.claude/rules/evaluation.md` — pipeline architecture, result JSON schema
- **Facts sheet:** `docs/facts_sheet_s_verify.md` — verified baseline numbers
- **Prior audit:** `docs/sc26_paper_audit_report.md` — 2026-03-28 4-agent paper audit

---

*Document created: 2026-03-29. Authors: Investigation team (4 agents + 3 follow-up agents)
coordinated by team lead, recorded by decision recorder agent.*
