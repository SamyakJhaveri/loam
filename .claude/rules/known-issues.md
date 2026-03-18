# Known Issues & Gotchas

> Auto-loaded when working on augmentation, harness, or spec files.

## HeCBench Missing (pre-existing — ignore)

120 `source_dir` disk-not-found errors from `validate_schema.py --all` are expected.
HeCBench is not cloned locally. Do NOT try to fix these errors.

## Augmentation Transform Bugs (c_augmentation — as of 2026-03-10)

Three bugs cause BUILD_FAIL at augment level 3–4.
Levels 1–2 with seed=42 currently apply no transforms (randomly selects a transform with no candidates).

### Bug A — PointerArithmeticToArrayIndex: overlapping nested subscripts

When nested `ARRAY_SUBSCRIPT_EXPR` (e.g., `iS[i]` inside `J[iS[i]*cols+j]`) and its
parent are both selected, combined byte-offset edits corrupt the output.
**Fix:** validate the combined `RewriteCandidate` in `AstTransform.apply()`, or filter
overlapping candidates before selection.

### Bug B — PointerArithmeticToArrayIndex: struct member access precedence

`arr[i].member` → `*((arr)+(i)).member` is wrong; `.` binds tighter than `*`.
**Fix:** Must emit `(*((arr)+(i))).member`.

### Bug C — SwapCondition: assignment-in-condition

`fp = fopen(...) == 0` → `0 == fp = fopen(...)` produces `(0 == fp) = fopen(...)` — non-lvalue error.
**Fix:** skip `BINARY_OPERATOR ==` nodes where either child contains an assignment.

## .cl File Inconsistency

`harness/spec_loader.py:get_prompt_payload` (line 195) does NOT augment `.cl` files
(missing from suffix list). `scripts/augmentation/augment_verify.py` DOES augment `.cl`
files via `AUGMENTABLE_SUFFIXES`.
**Fix:** add `.cl` to the suffix list in `spec_loader.py`.

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

## LLM CUDA→OMP Translation Quality Issues (as of 2026-03-17)

Known patterns where LLMs fail to translate correctly:

- **SRAD (both models)**: LLM preserves CUDA's 8-arg interface, drops `nthreads` param.
  OMP reference needs 9 args. LLM must add `nthreads` as `argv[7]` and call `omp_set_num_threads()`.
- **Backprop claude**: Translates multi-file set but duplicates `gettime()` across files → linker error.
- **Backprop azure**: Uses `HEIGHT`/`WIDTH` macros from `backprop.h` without including/inlining → undeclared.
- **Hotspot claude**: Missing `#include <cstring>` for `memcpy` in translated file.

## Git Worktrees and Submodules

Git worktrees do NOT initialize submodules. The `rodinia/` submodule will be empty
in any worktree. Any Rodinia build, evaluation, or harness verify will fail in a worktree
unless you manually symlink or copy the Rodinia source directories.

**Never run LLM evaluations in worktrees.** Only use worktrees for code review/inspection.
