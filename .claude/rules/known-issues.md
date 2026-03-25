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

## Current Spec Status (as of 2026-03-23)

**Rodinia:** 60 specs total, 54 PASS, 6 KNOWN_FAIL.
**XSBench:** 4 specs total, 4 PASS, 0 KNOWN_FAIL.
**Use the 54 Rodinia PASS + 3 standard XSBench specs (cuda, omp, opencl) for eval batches. omp_target excluded (requires nvc, case-study only).**

## KNOWN_FAIL Specs (6 — exclude from eval batches)

| Spec | Error | Why deferred |
|------|-------|-------------|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 | Texture reference → object rewrite needed |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 | Same rewrite in `mummergpu_kernel.cu` |
| `rodinia-mummergpu-omp` | `texture<>` + `cuMemGetInfo_v2` signature | OMP version also uses CUDA kernel |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found | Needs `libglew-dev` + display server |
| `rodinia-nn-opencl` | TIMEOUT / SIGSEGV | Pre-existing; never passed |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime | Pre-existing; never passed |

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
- OMP target uses `nvc` (NVIDIA HPC SDK 24.3), excluded from eval batches
- History/event checksum asymmetry: OMP=941535 (history), CUDA/OpenCL/OMP-target=945990 (event)
- Use 3 standard API specs (cuda, omp, opencl) for eval batches

## Hook Protection (updated 2026-03-23)

Hook regex: `/(rodinia|rodinia-src|HeCBench-master|hecbench|xsbench-src)/` — protects both direct
and symlink paths to benchmark sources.

## Augmentation Baseline (verified 2026-03-20)

54/60 PASS at all levels L1–L4 (level-invariant). Augmentation introduces zero new failures.
Verify transforms: `python3 -m pytest c_augmentation/test_transforms.py -v` (15 tests, all must pass)

## Eval Result Timing Limitations (SESSION 3b audit — 2026-03-24)

All 30 PASS results use `timing_method: "wall_time"`. Failure results have `timing_method: null`.
`translated_cpu_time_seconds` and `translated_kernel_time_seconds` are `null` in all 68 files.

**Do NOT use `speedup_ratio` from these results in the SC26 paper.** Sub-millisecond baseline
wall times (0.001s) produce unreliable ratios (e.g., nn=16.0x, bfs=0.002x). Wall-clock time
includes OS scheduling noise, I/O, and memory allocation — it is not kernel time.

For valid performance numbers: use `nvprof`/`ncu` for CUDA kernel time, and `perf` or
`omp_get_wtime()` around the parallel region for OMP. See `feedback_timing_measurement.md`.

## Eval Result JSON Schema Quirk (SESSION 3b audit — 2026-03-24)

Top-level `run_status`, `run_time_seconds`, `run_exit_code` fields can contain stale data
from a non-final attempt when a multi-attempt evaluation regresses to a build failure.
**Always use `overall_status` (not top-level `run_status`) as the authoritative verdict.**
The `attempts[]` array is the canonical per-attempt record.

This was a pipeline bug in `llm_evaluate.py` (fixed prospectively — future results are correct).
The 68 existing L0 result JSONs are not retroactively corrected; only gemini pathfinder is
affected (attempt 1 SIGSEGV, attempt 2 BUILD_FAIL; `overall_status` is correctly BUILD_FAIL).
