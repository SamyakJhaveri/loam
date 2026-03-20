# Known Issues & Gotchas

> Auto-loaded when working on augmentation, harness, or spec files.

## HeCBench Missing (pre-existing — ignore)

120 `source_dir` disk-not-found errors from `validate_schema.py --all` are expected.
HeCBench is not cloned locally. Do NOT try to fix these errors.

## Augmentation Transform Bugs (c_augmentation — status as of 2026-03-19)

Erel's fixes for Bugs A, B, C were cherry-picked from `origin/erel/aug` into main on 2026-03-19
(Task M9 of March 18 meeting plan). Also integrated: `ChangeFunctionNames` transform,
`LEVEL_FRACTIONS`/`_select_fraction()`, `_greedy_valid_subset()`, `filename` parameter threading,
OMP pragma awareness helpers, and UTF-8 safety in `_source_text()`.

**Verify fixes:** `python3 -m pytest c_augmentation/test_transforms.py -v`

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

## hotspot3d Double-Include (NOT a bug)

`3D.cu` includes `opt1.cu` via `#include "opt1.cu"`. No double-augmentation occurs
because `_cursor_in_main_file` in `augment_dataset.py` skips cursors from included files.

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

## OMP Spec Run Arg Bugs (fixed 2026-03-17)

Two rodinia OMP specs had incorrect run arguments:

**`rodinia-nw-omp`**: Had extra `"4"` arg in all argument lists — e.g. `["2048","10","4"]`.
The nw OMP reference (`needle.cpp`) only accepts 2 args: `<dimension> <penalty>`.
The `"4"` was a mistaken assumption about OMP thread-count CLI flag.
**Fixed**: removed `"4"` → `["2048","10"]` and `["8192","10"]`.

**`rodinia-hotspot-omp`**: Had extra `"512"` (grid_cols) and wrong power/temp file order.
The hotspot OMP reference (`hotspot_openmp.cpp`) uses ONE arg for grid_rows/grid_cols (square grid),
and expects `<temp_file>` at `argv[4]` and `<power_file>` at `argv[5]`.
**Fixed**: removed extra grid_cols, swapped power/temp to `["512","2","4","temp_512","power_512","output.out"]`.

## needle.h Missing from OMP Source Dir (permanently fixed 2026-03-18)

`rodinia/rodinia-src/openmp/nw/needle.cpp` includes `needle.h`, but the OMP directory
in the Rodinia repo at commit `9c10d3ea` never contained `needle.h` (it lives only in
`cuda/nw/`).

**Fix applied (permanent)**: `specs/rodinia-nw-omp.json` build command now passes
`-I../../cuda/nw` to the compiler:
```
make needle CC_FLAGS='-g -O3 -fopenmp -I../../cuda/nw'
```
The include path resolves to `rodinia-src/cuda/nw/` where `needle.h` permanently lives.
No file copy needed. `needle.h` removed from `support_files` in the OMP spec.
This fix is resilient to `git submodule update` — no re-copy required.

## SRAD Reference Binary May Be Stale (2026-03-17)

`rodinia/rodinia-src/openmp/srad/srad_v2/srad` may be a stale binary missing the `nthreads`
parameter. The current source expects 9 user args (includes `nthreads` at position 7),
but the stale binary only accepted 8. Always rebuild before using: `cd .../srad_v2 && make`.

## M10 Augmentation L1-L4 Verification (COMPLETE 2026-03-19)

All levels verified on srad-cuda and backprop-cuda with seed=42:
- L1: PASS (no transforms fire — trivial pass)
- L3: PASS (SwapCondition fires on both)
- L4: PASS (ArithmeticTransform + ChangeNames + SwapCondition fire)
PointerArithmeticToArrayIndex did NOT fire on any Rodinia CUDA spec — all use `arr[idx]` syntax.
M10 is COMPLETE. L1-L4 augmentation is stable across bfs, hotspot, nw, srad, backprop.

## Gaussian OMP Spec — Broken (2026-03-19)

`specs/rodinia-gaussian-omp.json` has `working_directory: "openmp/gaussian"` but the directory
`rodinia/openmp/gaussian/` does NOT exist in the Rodinia repo at commit `9c10d3ea`. Gaussian has
only CUDA and OpenCL versions in this commit — no OpenMP variant exists.
**Do not use rodinia-gaussian-omp in eval batches until fixed.**
Use streamcluster as replacement for 10-kernel batch.

## nn-omp filelist.txt Bug (FIXED 2026-03-19)

`specs/rodinia-nn-omp.json` had `filelist.txt` as run arg, but that file doesn't exist in
`openmp/nn/`. The correct file is `filelist_4` (already present in `openmp/nn/`, contains
correct relative paths to `../../data/nn/cane4_*.db`).
**Fixed**: changed `filelist.txt` → `filelist_4` in all run arguments.

## LLM CUDA→OMP Translation Quality Issues (updated 2026-03-19)

10-kernel batch results (azure-gpt-4.1, L0): **6/10 PASS (60%)**
PASS: bfs, hotspot, lud, nn, nw, pathfinder
BUILD_FAIL: backprop, kmeans, srad, streamcluster

Pattern analysis:
- **Multi-file with subdirectories** (kmeans, streamcluster): LLM can't produce files with
  paths like `kmeans_openmp/kmeans.c` in the code fence format — BUILD_FAIL every time.
- **SRAD azure**: BUILD_FAIL (differs from pilot RUN_FAIL — LLM output changed)
- **Backprop (both models)**: BUILD_FAIL consistently — file extraction fails for `.c` targets
- Known from 2026-03-17 pilot: SRAD (both models) drops `nthreads`; backprop/azure missing macros.

## Pipeline Fixes (2026-03-19)

### B8 — `--augment-levels` flag missing from batch runner (FIXED)

`scripts/evaluation/run_eval_batch.py` now accepts `--augment-levels 0 1 2 3 4` (default: `[0]`).
Each level generates separate tasks with result files tagged `-L1`, `-L2` etc. (L0 has no tag).
`augment_level` is now passed through to `evaluate_translation()`.

### analyze_eval.py — Results aggregator (NEW 2026-03-19)

`scripts/evaluation/analyze_eval.py` now exists. Aggregates all result JSONs into:
- `results/evaluation/eval_summary.json` — machine-readable (by model/direction/kernel/level)
- `results/evaluation/eval_summary.md` — publication-ready tables
- `visualizations/eval_results_data.js` — dashboard data (via `--write-dashboard`)
- `--show-gaps` prints which (kernel, model, direction, level) combinations are missing

## Git Worktrees and Submodules

Git worktrees do NOT initialize submodules. The `rodinia/` submodule will be empty
in any worktree. Any Rodinia build, evaluation, or harness verify will fail in a worktree
unless you manually symlink or copy the Rodinia source directories.

**Never run LLM evaluations in worktrees.** Only use worktrees for code review/inspection.
