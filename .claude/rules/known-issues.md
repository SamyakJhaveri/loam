# Known Issues & Gotchas

> Always loaded. Contains active guardrails that prevent recurring mistakes.
> Historical fix details are in `known-issues-archive.md` (conditional, loads on augmentation/harness files).

## HeCBench Missing (pre-existing — ignore)

~135 errors from `validate_schema.py --all` are expected (as of 2026-03-20):
- ~120 HeCBench `source_dir` disk-not-found errors — HeCBench is not cloned locally.
- 15 errors from the 5 deleted phantom Rodinia specs still referenced in manifest.jsonl
  (each generates 2 manifest errors + 1 "spec file not found" = 3 × 5 = 15).
  This is correct behavior — manifest.jsonl is append-only; spec files were deleted.
Do NOT try to fix any of these errors.

## Current Spec Status (as of 2026-03-28, post campaign expansion)

**Rodinia:** 60 specs total, 54 TRUE PASS, 0 FALSE_PASS, 6 KNOWN_FAIL.
**XSBench:** 4 specs total, 4 PASS, 0 KNOWN_FAIL.
**RSBench:** 4 specs (cuda, omp, opencl, omp_target), all 4 PASS — verified 2026-04-03.
**mixbench:** 3 specs (cuda, omp, opencl), all 3 PASS — verified 2026-04-03.
**HeCBench (curated):** 10 kernels, 25 specs (cuda + omp/omp_target), 23 PASS, 2 KNOWN_FAIL.
**All 65 Rodinia+XSBench+RSBench+mixbench non-KNOWN_FAIL specs verified PASS.**
**Use 54 Rodinia TRUE PASS + 3 XSBench + 4 RSBench + 3 mixbench specs for eval batches.**

## KNOWN_FAIL Specs (8 — exclude from eval batches)

| Spec | Error | Why deferred |
|------|-------|-------------|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 | Texture reference → object rewrite needed |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 | Same rewrite in `mummergpu_kernel.cu` |
| `rodinia-mummergpu-omp` | `texture<>` + `cuMemGetInfo_v2` signature | OMP version also uses CUDA kernel |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found | Needs `libglew-dev` + display server |
| `rodinia-nn-opencl` | TIMEOUT / SIGSEGV | Pre-existing; never passed |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime | Pre-existing; never passed |
| `hecbench-stencil1d-omp_target` | BUILD_FAIL | omp_target compile issue |
| `hecbench-scan-omp_target` | VERIFY_FAIL | Output mismatch on CPU target |

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

## OMP Spec Run Arg Rules (CRITICAL)

**Never change spec run args without reading the actual source's argc check.**
This rule exists because "fixes" based on documentation caused 2 specs to silently fail for weeks.

- **`rodinia-nw-omp`**: Source (`needle.cpp:249`) checks `argc == 4` → 3 args required.
  Correct: `["2048","10","4"]` (correctness), `["8192","10","4"]` (performance).
- **`rodinia-hotspot-omp`**: Source (`hotspot_openmp.cpp:282`) checks `argc != 8` → 7 args required.
  Correct: `["512","512","2","4","temp_512","power_512","output.out"]` (correctness).

## Key Build/Run Rules

- **needle.h**: `rodinia-nw-omp` build uses `-I../../cuda/nw` (needle.h lives in cuda/nw only).
- **SRAD binary**: May be stale — always rebuild before using: `cd .../srad_v2 && make`.
- **Spec-executable names**: Always verify `outputs.executable` matches the actual Makefile output
  (e.g., `euler3d.out` not `euler3d`, `pathfinder.out` not `pathfinder`).
- **Run arg format**: Always check source's `init()`/`argc` parsing before writing spec run args
  (e.g., pathfinder-opencl uses `-c/-r/-h` flags, not positional args).

## hotspot3d Double-Include (NOT a bug)

`3D.cu` includes `opt1.cu` via `#include "opt1.cu"`. No double-augmentation occurs
because `_cursor_in_main_file` in `augment_dataset.py` skips cursors from included files.

## Deleted Phantom Specs (5)

gaussian-omp, huffman-omp, huffman-opencl, hybridsort-omp, mummergpu-opencl — all pointed
to non-existent Rodinia directories at commit `9c10d3ea`. Deleted from `specs/`, manifest
entries remain (append-only). Use streamcluster or backprop as replacement for batches.

## Git Worktrees and Submodules

Git worktrees do NOT initialize submodules. The `rodinia/` submodule will be empty
in any worktree. **Never run LLM evaluations in worktrees.** Only use worktrees for code review.

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
