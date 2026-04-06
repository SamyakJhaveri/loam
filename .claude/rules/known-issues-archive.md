---
paths:
  - "c_augmentation/**"
  - "harness/**"
  - "scripts/augmentation/**"
  - "scripts/evaluation/**"
  - "results/augmentation/**"
  - "results/evaluation/**"
  - "specs/**"
  - "visualizations/**"
---

# Known Issues — Historical Archive

> Conditional: loads only when working on augmentation, harness, specs, or results files.
> For active guardrails, see `known-issues.md` (always loaded).

## Augmentation Transform Bugs (c_augmentation — all FIXED as of 2026-03-19)

Erel's fixes for Bugs A, B, C were cherry-picked from `origin/erel/aug` into main on 2026-03-19
(Task M9 of March 18 meeting plan). Also integrated: `ChangeFunctionNames` transform,
`LEVEL_FRACTIONS`/`_select_fraction()`, `_greedy_valid_subset()`, `filename` parameter threading,
OMP pragma awareness helpers, and UTF-8 safety in `_source_text()`.

### Gap G1 — ChangeFunctionNames Unit Tests (FIXED 2026-03-20)

`ChangeFunctionNames` (260 lines, merged in M9) had zero unit tests. 4 tests added on Day 3.
Writing the tests exposed a bonus bug: `_string_literals_in_file` had `values: set[str] = []`
(a list, not a set), causing `values.add()` to raise `AttributeError` silently inside
`try/except Exception: pass`. The OpenCL kernel-name safety guard was always broken.
**Fix:** `values: set[str] = set()` — 1-char change.

### Gap G2 — Filename Threading (FIXED 2026-03-20)

Two `augment_code()` call sites omitted `filename=`:
- `c_augmentation/augment_dataset.py:augment_sample()` — JSONL batch path
- `harness/spec_loader.py:get_prompt_payload()` — harness prompt path
Without `filename=`, libclang parsed `.cu`/`.cl` files as `.cpp`, missing CUDA/OpenCL extensions.
Both call sites now pass the actual filename as the `filename` kwarg.

If L3/L4 BUILD_FAIL issues persist after merge, they are residual and should be treated as
future work. Paper focuses on L0/L1/L2 (conservative augmentation — Gal, March 18 meeting).

### Bug A — PointerArithmeticToArrayIndex: overlapping nested subscripts (FIXED in erel/aug)

When nested `ARRAY_SUBSCRIPT_EXPR` (e.g., `iS[i]` inside `J[iS[i]*cols+j]`) and its
parent are both selected, combined byte-offset edits corrupt the output.
**Fix applied:** `_greedy_valid_subset()` in `AstTransform.apply()` builds the largest
non-overlapping subset of candidates that pass validation.

### Bug B — PointerArithmeticToArrayIndex: struct member access precedence (FIXED in erel/aug)

`arr[i].member` → `*((arr)+(i)).member` is wrong; `.` binds tighter than `*`.
**Fix applied:** Now emits `(*((arr)+(i))).member`.

### Bug C — SwapCondition: assignment-in-condition (FIXED in erel/aug)

`fp = fopen(...) == 0` → `0 == fp = fopen(...)` produces `(0 == fp) = fopen(...)` — non-lvalue error.
**Fix applied:** `_contains_side_effects()` guards SwapCondition from reordering expressions
with side effects (function calls, assignments, pre/post-increment).

## .cl File Inconsistency (FIXED 2026-03-19)

`harness/spec_loader.py:get_prompt_payload` now augments `.cl` files — added to suffix list on Day 2.
`scripts/augmentation/augment_verify.py` also augments `.cl` via `AUGMENTABLE_SUFFIXES`.
Both paths are now consistent.

## Smoke Tests (updated 2026-03-17 — all PASS)

```
rodinia-bfs-cuda    BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-hotspot-omp BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-nw-omp      BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-hotspot-omp BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-bfs-opencl  BUILD: PASS | RUN: PASS | VERIFY: PASS
```

Fixes applied: CUDA_DIR path, `make hotspot` target, OpenCL include/lib paths,
`CC_FLAGS=-std=c++14`, data path symlinks (`rodinia/rodinia-src/data/` → `rodinia-data/`).

## M10 Augmentation L1-L4 Verification (COMPLETE — 2026-03-20)

Full 65-spec retest completed 2026-03-20 (post-M9 + post-G2 fix), seed=42.
Results: `results/augmentation/retest_post_m9.json` / `.md`

**Key finding: results are level-invariant** — every spec that passes at L1 also passes at L4.
Augmentation transforms introduce zero new failures. The 17 failing specs fail due to
pre-existing spec/build issues, not transforms.

| Level | PASS | BUILD_FAIL | FAIL | ERROR |
|-------|------|-----------|------|-------|
| L1    | 48/65 (73%) | 7 | 5 | 5 |
| L2    | 48/65 (73%) | 7 | 5 | 5 |
| L3    | 48/65 (73%) | 7 | 5 | 5 |
| L4    | 48/65 (73%) | 7 | 5 | 5 |

**Failing specs (pre-existing issues — not augmentation-caused):**
- BUILD_FAIL: cfd-cuda, cfd-opencl, hybridsort-cuda, kmeans-cuda, mummergpu-cuda, mummergpu-omp, pathfinder-opencl
- FAIL (wrong output): hotspot-omp, kmeans-opencl, nn-cuda, nn-opencl, nw-omp
- ERROR (spec/setup): gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl

**Correction to M10 spot-check claim:** `PointerArithmeticToArrayIndex` DOES fire on
`gaussian-cuda` and `gaussian-opencl` (both PASS).

**Transform frequency (across all 260 tasks):**
SwapCondition=162, ArithmeticTransform=69, ChangeNames=55, TypedefExpansion=7,
PointerArithmeticToArrayIndex=6, ChangeFunctionNames=2

## M10b Spec Fixes (2026-03-20) — 65 → 60 specs, target 54/60 PASS

Post-mortem on the 17 M10 failures revealed 3 distinct root causes. All fixable issues
have been addressed. Spec count reduced from 65 to 60 (5 phantom specs deleted).
mummergpu-cuda and mummergpu-omp moved to KNOWN_FAIL after Session 2 retest revealed
cascading CUDA 12 texture API removal.

### Phantom Specs Deleted (5 ERROR → removed)

| Spec | Claimed directory | Reality |
|------|-------------------|---------|
| `rodinia-gaussian-omp` | `openmp/gaussian` | No OMP gaussian in Rodinia at 9c10d3ea |
| `rodinia-huffman-omp` | `openmp/huffman` | Huffman is CUDA-only |
| `rodinia-huffman-opencl` | `opencl/huffman` | Huffman is CUDA-only |
| `rodinia-hybridsort-omp` | `openmp/hybridsort` | Hybridsort has CUDA + OpenCL only |
| `rodinia-mummergpu-opencl` | `opencl/mummergpu` | Mummergpu has CUDA + OMP only |

### Toolchain Fixes — GCC 12 / C++17 / OpenCL 3.0 incompatibilities

**`rodinia-cfd-cuda`** (FIXED 2026-03-20, additional fix Session 2):
`helper_cuda.h` not found at `$(CUDA_DIR)/samples/common/inc`. Fix: spec build command
passes `KERNEL_DIM='-I.../examples/OpenACC/SDK/include'`. Changed build target to `make euler3d`.

**`rodinia-mummergpu-cuda`** and **`rodinia-mummergpu-omp`** (PARTIAL FIX → KNOWN_FAIL):
GCC 12 removed implicit `read()`/`lseek()` from POSIX. `unistd.h` fix was applied then
**reverted 2026-03-22** — both specs are KNOWN_FAIL due to deeper CUDA 12 `texture<>` removal.

**`rodinia-cfd-opencl`** (FIXED 2026-03-20, additional fix Session 2):
`if(file==NULL)` → `if(!file)`, added `-DCL_TARGET_OPENCL_VERSION=120`.
Executable: `./euler3d.out` (not `./euler3d`).

**`rodinia-pathfinder-opencl`** (FIXED 2026-03-20, additional fix Session 2):
Renamed `data` → `grid_data` (C++17 conflict). Added `-DCL_TARGET_OPENCL_VERSION=120`.
Executable: `./pathfinder.out`. Run args: named flags `-c/-r/-h` (not positional).

## nn-{omp,cuda} filelist.txt Bug (FIXED)

Both specs had `filelist.txt` as a run arg, but correct file is `filelist_4`.
- `specs/rodinia-nn-omp.json`: Fixed 2026-03-19
- `specs/rodinia-nn-cuda.json`: Fixed 2026-03-20

## LLM Multi-File Structural Mismatch (M11 — RESOLVED 2026-03-22)

3/4 BUILD_FAILs in Phase 1 pilot were structural failures — LLM asked to replicate full
project file structure. Resolution: kernel-centric translation (feed kernel files only).
Architecture: `docs/design/kernel_centric_translation.md`
Spec field: `files.translation_targets` — subset of `prompt_payload`

## LLM CUDA→OMP Translation Quality Issues (pre-M11 data — 2026-03-19)

**NOTE: These results are from full-project translation mode — obsolete after SESSION 1.5.**
10-kernel batch (azure-gpt-4.1, L0): 6/10 PASS (60%). BUILD_FAIL: backprop, kmeans, srad, streamcluster.

## Session 2 Targeted Retest (2026-03-20)

Ran `harness verify` at L0 on all 8 M10b-fixed specs and 4 original KNOWN_FAIL specs.
6/8 M10b-fixed specs verified PASS. 2 moved to KNOWN_FAIL (cascade from unistd.h fix).

| Spec | Result | Root cause / fix |
|------|--------|-----------------|
| `rodinia-hotspot-omp` | **PASS** | 7 args restored |
| `rodinia-nw-omp` | **PASS** | 3 args restored |
| `rodinia-nn-cuda` | **PASS** | `filelist_4` |
| `rodinia-cfd-cuda` | **PASS** | `make euler3d` + `KERNEL_DIM` |
| `rodinia-cfd-opencl` | **PASS** | `./euler3d.out` + OpenCL 1.2 |
| `rodinia-pathfinder-opencl` | **PASS** | `./pathfinder.out` + named args |
| `rodinia-mummergpu-cuda` | **KNOWN_FAIL** | CUDA 12 texture<> |
| `rodinia-mummergpu-omp` | **KNOWN_FAIL** | CUDA 12 texture<> + cuMemGetInfo |

**Key discoveries:**
- Cascading fixes: `unistd.h` fix exposed deeper `texture<>` API removal
- Spec-executable mismatches: always verify `outputs.executable` matches Makefile output
- Run arg format: always check source's argc parsing

## Session 3 Independent Re-verification (2026-03-20)

Full re-run of all 12 Session 2 specs. All 12 classifications match. Commit `de95155` validated.
`mummergpu-omp` surfaces additional `cuMemGetInfo_v2` signature change (`unsigned int*` → `size_t*`).

## Full Augmentation Batch Retest — 60 Specs × L1–L4 (2026-03-20)

Definitive augmentation baseline for SC26 paper. 240 tasks, seed=42, `--config correctness`.
Results: `results/augmentation/retest_post_session2.{json,md}`.

**54/60 PASS at all levels (level-invariant). No transform introduces new failures.**

| Level | PASS | BUILD_FAIL | FAIL | ERROR | Total |
|-------|------|-----------|------|-------|-------|
| L1    | 54   | 4         | 2    | 0     | 60    |
| L2    | 54   | 4         | 2    | 0     | 60    |
| L3    | 54   | 4         | 2    | 0     | 60    |
| L4    | 54   | 4         | 2    | 0     | 60    |

**Improvement from M10 baseline:** 48/65 (73%) → 54/60 (90%)

**Transform frequency (across 240 tasks):**
SwapCondition=162, ArithmeticTransform=69, ChangeNames=55, TypedefExpansion=7,
PointerArithmeticToArrayIndex=6, ChangeFunctionNames=2

## Pipeline Fixes (2026-03-19)

### B8 — `--augment-levels` flag (FIXED)

`scripts/evaluation/run_eval_batch.py` now accepts `--augment-levels 0 1 2 3 4` (default: `[0]`).

### analyze_eval.py — Results aggregator (NEW 2026-03-19)

Aggregates all result JSONs into `eval_summary.json`, `eval_summary.md`,
`eval_results_data.js` (via `--write-dashboard`). `--show-gaps` for missing combinations.

## XSBench Detailed Verification (SESSION 5 — 2026-03-23)

| Spec | Compiler | Build | Run | Verify | Augment L2 | Checksum |
|------|----------|-------|-----|--------|-----------|---------|
| `xsbench-xsbench-omp` | gcc-12 `-fopenmp` | PASS (0.5s) | PASS (0.8s) | PASS | PASS | 941535 (history) |
| `xsbench-xsbench-cuda` | nvcc 12.3 `-arch=sm_89` | PASS (22.6s) | PASS (0.5s) | PASS | PASS | 945990 (event) |
| `xsbench-xsbench-opencl` | gcc-12 + libOpenCL | PASS (0.5s) | PASS (0.4s) | PASS | PASS | 945990 (event) |
| `xsbench-xsbench-omp_target` | nvc 24.3 `-mp=gpu -gpu=cc89` | PASS (1.3s) | PASS (0.6s) | PASS | N/A | 945990 (event) |

- OMP target uses `nvc` (NVIDIA HPC SDK 24.3), excluded from eval batches
- History/event asymmetry: OMP=941535, CUDA/OpenCL/OMP-target=945990
- Augmentation L2 (seed=42) PASS on OMP, CUDA, OpenCL
- `baseline_results` populated in all 4 specs (2026-03-23, platform: rtx4070-linux-x86_64)

---

## Sections moved from known-issues.md (2026-04-06)

> The following sections were moved here to reduce always-loaded token overhead.
> They are historical reference, not active guardrails.

## FALSE_PASS Baseline Specs — ALL FIXED (S-VERIFY 2026-03-27)

Originally 9 specs discovered with wrong run args (exit_code=0 but wrong/no output).
All 9 specs now verified TRUE PASS. heartwall-opencl fixed via runner.py argv[0] change (2026-03-27).

| Spec | Fix Applied | Status |
|------|------------|--------|
| `rodinia-backprop-opencl` | Args `["-n","65536"]` (flag + divisible by 16) | FIXED — TRUE PASS |
| `rodinia-heartwall-opencl` | runner.py argv[0] fix (use relative path, not absolute) | FIXED — TRUE PASS |
| `rodinia-myocyte-omp` | Args `["100","1","1","4"]` (added threads arg) | FIXED — TRUE PASS |
| `rodinia-myocyte-opencl` | Args `["-time","100","-r","../../data/myocyte"]` (flags not positional) | FIXED — TRUE PASS |
| `rodinia-pathfinder-omp` | Args `["100000","100"]` (removed extra arg) | FIXED — TRUE PASS |
| `rodinia-bfs-omp` | Args `["4","../../data/bfs/graph1MW_6.txt"]` (added num_omp_threads) | FIXED — TRUE PASS |
| `rodinia-lavamd-cuda` | Args `["-boxes1d","10"]` (removed `-cores`, fixed `-boxes1d`) | FIXED — TRUE PASS |
| `rodinia-lavamd-omp` | Args `["-cores","4","-boxes1d","10"]` (fixed `-boxes1d`) | FIXED — TRUE PASS |
| `rodinia-lavamd-opencl` | Args `["-boxes1d","10"]` (removed `-cores`, fixed `-boxes1d`) | FIXED — TRUE PASS |

## hotspot3d Double-Include (NOT a bug)

`3D.cu` includes `opt1.cu` via `#include "opt1.cu"`. No double-augmentation occurs
because `_cursor_in_main_file` in `augment_dataset.py` skips cursors from included files.

## Rodinia Submodule Source Edit Policy (updated 2026-03-22)

**Current state:** 10 files modified from pristine commit `9c10d3ea` (down from 13).
- 9 Makefile/config patches (toolchain adaptation — safe)
- 1 documented source exception: `opencl/cfd/euler3d.cpp:276` — `if(file==NULL)` → `if(!file)`
  (C++11 portability fix, not a benchmark logic change)

**Patch file:** `docs/rodinia_toolchain_patches.diff` — regenerated after each submodule reset.

Build-flag alternative for pathfinder: spec passes `-std=c++14` in `CXXFLAGS` instead of
editing source. mummergpu `unistd.h` edits reverted — both specs are KNOWN_FAIL regardless.

## XSBench (SESSION 5 — 2026-03-23)

4/4 PASS. No KNOWN_FAIL. Key facts:
- No OpenACC variant exists (only cuda, omp, opencl, omp_target)
- OMP target uses `nvc` (NVIDIA HPC SDK 24.3), excluded from standard eval batches
- History/event checksum asymmetry: OMP=941535 (history), CUDA/OpenCL/OMP-target=945990 (event)
- Use 3 standard API specs (cuda, omp, opencl) for eval batches (omp_target = case-study only)
- SESSION 8 ran all 12 directions including omp_target (30 result files exist); those are case-study data, not part of the standard eval batch suite

## Hook Protection (updated 2026-03-30)

Hook regex: `/(rodinia|rodinia-src|HeCBench-master|hecbench|xsbench-src)/` — protects both direct
and symlink paths to benchmark sources.

**CUDA↔OMP Result Protection Hook** (`protect-cuda-omp-results.sh` — added 2026-03-30):
- Blocks `rm` commands targeting `results/evaluation/` files matching `*cuda*omp*` or `*omp*cuda*`
- Blocks wildcard `rm` in `results/evaluation/` that could expand to CUDA↔OMP files
- Blocks `run_eval_batch.py` with `cuda-to-omp` or `omp-to-cuda` direction without `--resume`
- ALLOWS all OpenCL-related operations (cuda-to-opencl, opencl-to-cuda, etc.)
- Registered as PreToolUse hook on Bash in `settings.json`

## Augmentation Baseline (verified 2026-03-20, updated S-VERIFY 2026-03-27)

54/60 Rodinia + 4/4 XSBench PASS at all levels L1–L4 (level-invariant) with
stdout_pattern+exit_code conjunction verification. 6 Rodinia KNOWN_FAIL excluded (4 BUILD_FAIL + 2 FAIL).
Augmentation introduces zero new failures beyond the baseline.
Verify transforms: `python3 -m pytest c_augmentation/test_transforms.py -v` (15 tests, all must pass)

## Eval Result Timing Limitations (SESSION 3b audit — 2026-03-24)

All 30 PASS results use `timing_method: "wall_time"`. Failure results have `timing_method: null`.
`translated_cpu_time_seconds` and `translated_kernel_time_seconds` are `null` in all 68 files.

**Do NOT use `speedup_ratio` from these results in the SC26 paper.** Sub-millisecond baseline
wall times (0.001s) produce unreliable ratios (e.g., nn=16.0x, bfs=0.002x). Wall-clock time
includes OS scheduling noise, I/O, and memory allocation — it is not kernel time.

For valid performance numbers: use `nvprof`/`ncu` for CUDA kernel time, and `perf` or
`omp_get_wtime()` around the parallel region for OMP. See `feedback_timing_measurement.md`.

## sprint_dashboard.html localStorage Divergence (2026-03-25)

**Problem:** `sprint_dashboard.html` uses browser localStorage as an overlay on top of a
hardcoded `DEFAULT_TASKS` JS array. A user who edits task statuses via the kanban board
writes to their *browser's* localStorage — but the **git-tracked HTML file is never updated**.

**Consequence:** A session author sees correct statuses in their browser (via localStorage),
pushes the branch, and assumes the merge will reflect those updates. It won't — the merged
HTML still has the old hardcoded values.

**Caught:** During post-merge validation of the W-S11 branch (2026-03-25). M11 showed as
`blocked` and Rodinia as `51/60` in the merged file despite the author having updated these
in their browser.

**Rule:** After any worktree dashboard session, **always grep the HTML file directly** for
the values you changed. Do not trust your browser view:
```bash
# Check M11 and Rodinia stat card directly — don't trust browser localStorage view
grep -n "M11\|Rodinia Specs\|stat-value" visualizations/sprint_dashboard.html | head -20
grep -n "status: 'blocked'\|status: 'todo'" visualizations/sprint_dashboard.html | grep -v "//\|kh-\|dropdown\|column\|label"
```
If the grep shows stale values, edit `DEFAULT_TASKS` in the HTML file before committing.

## Eval Result JSON Schema Quirk (SESSION 3b audit — 2026-03-24)

Top-level `run_status`, `run_time_seconds`, `run_exit_code` fields can contain stale data
from a non-final attempt when a multi-attempt evaluation regresses to a build failure.
**Always use `overall_status` (not top-level `run_status`) as the authoritative verdict.**
The `attempts[]` array is the canonical per-attempt record.

This was a pipeline bug in `llm_evaluate.py` (fixed prospectively — future results are correct).
The 68 existing L0 result JSONs are not retroactively corrected; only gemini pathfinder is
affected (attempt 1 SIGSEGV, attempt 2 BUILD_FAIL; `overall_status` is correctly BUILD_FAIL).

## Gemini Flash Lite Thinking Confound — Resolved (2026-03-26)

**Concern:** Gemini API calls initially lacked explicit thinking-disable parameters, raising
the possibility that Flash Lite used inference-time reasoning while Claude/Llama did not.

**Investigation (Session 9 audit):**
1. ALL 145 Gemini files were re-run on 2026-03-25 22:52-23:46 (after fix commit `01e1f01`)
2. Two test API calls (with and without `reasoning_effort="none"`) produced **identical**
   token counts (500/500) and identical output text
3. Flash Lite has thinking OFF by default — it is a distilled model without thinking capability

**Conclusion:** The confounding variable never existed. Existing Gemini results are valid.
The `reasoning_effort="none"` parameter in `llm_evaluate.py` is a belt-and-suspenders
safety measure, not a fix for an active problem.

## Per-Kernel Capability Anomaly: backprop (discovered 2026-03-25, updated 2026-03-28)

**Observation:** In the 3-model evaluation, `backprop` (9/18 = 50.00% overall) shows an
anomalous tier pattern: Gemini 2.5 Flash-Lite (weakest overall, 7.05%) passes backprop
at L0 CUDA-to-OMP, while Groq Llama 3.3 70B (8.33% overall) fails with BUILD_FAIL.
This violates the naive assumption that stronger models dominate everywhere.

*Historical note:* Originally observed in a 4-model evaluation that included azure-gpt-4.1.
GPT-4.1 was subsequently dropped (zero result files on disk). The anomaly persists in the
current 3-model data.

**Interpretation:** Domain-specific model strength. Backprop's reduction-heavy ML kernel
involves `__syncthreads()` and shared memory accumulation idioms that may appear heavily
in Gemini's training data relative to its overall OpenMP coverage.

**Paper treatment:** The anomaly is discussed as evidence that per-kernel difficulty is not
fully predicted by aggregate pass rate. *Note (2026-04-03):* Paper model lineup changed from
Qwen+Gemini to Qwen+GPT-4.1 mini. The "Claude+Gemini only" tier name is historical; per-kernel
tiers will be re-derived when GPT-4.1 mini data arrives.

**Rule:** When writing per-kernel tier descriptions from tabular data, verify EVERY cell in
the table against the prose claim. Do not assume rank-ordering is monotonic per kernel.

## OpenCL Kernel-Only Translation (SESSION S-OCLFIX — 2026-03-30)

**Bug fixed:** `llm_evaluate.py` cross-API run/verify logic assumed all translations rewrite
the host code (correct for CUDA↔OMP). But X-to-OpenCL is "kernel-only" — only `.cl` kernel
files are translated, host code is untouched. Three bugs caused 0% pass rate on ALL
OpenCL-target translations:

1. `_build_cross_api_run_spec()` sent SOURCE args to OpenCL binary (host expects TARGET args)
2. `_build_cross_api_verify_spec()` used SOURCE stdout patterns (host prints TARGET patterns)
3. Dead code: pattern extraction used key `"expected_pattern"` but specs use `"pattern"` —
   combined-pattern logic never fired, fell back to source-only patterns

**Fix:** Added `_is_kernel_only_translation(target_spec)` predicate. Returns `True` when ALL
`translation_targets` end with `.cl`. When True, both functions return `copy.deepcopy(target_spec)`
(target args and patterns unchanged). When False (CUDA/OMP targets), existing code path
is completely unchanged.

**Result JSON fields added:**
- `translation_type`: `"kernel_only"` or `"full_program"`
- `run_args_mode`: `"kernel_only_target_args"` / `"cross_api_source_args"` / `"same_api_target_args"`
- `verification_mode`: `"kernel_only_target_pattern"` / `"cross_api_combined_pattern"` / `"same_api_target_pattern"`

**Rule:** When adding new cross-API translation targets, check if they are kernel-only
(host code untouched) or full-program (host code rewritten by LLM). The `.cl` heuristic
works for OpenCL but may need extension for future APIs with separate kernel files.
