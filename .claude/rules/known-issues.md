# Known Issues & Gotchas

> Auto-loaded when working on augmentation, harness, or spec files.

## HeCBench Missing (pre-existing — ignore)

~135 errors from `validate_schema.py --all` are expected (as of 2026-03-20):
- ~120 HeCBench `source_dir` disk-not-found errors — HeCBench is not cloned locally.
- 15 errors from the 5 deleted phantom Rodinia specs still referenced in manifest.jsonl
  (each generates 2 manifest errors + 1 "spec file not found" = 3 × 5 = 15).
  This is correct behavior — manifest.jsonl is append-only; spec files were deleted.
Do NOT try to fix any of these errors.

## Augmentation Transform Bugs (c_augmentation — status as of 2026-03-19)

Erel's fixes for Bugs A, B, C were cherry-picked from `origin/erel/aug` into main on 2026-03-19
(Task M9 of March 18 meeting plan). Also integrated: `ChangeFunctionNames` transform,
`LEVEL_FRACTIONS`/`_select_fraction()`, `_greedy_valid_subset()`, `filename` parameter threading,
OMP pragma awareness helpers, and UTF-8 safety in `_source_text()`.

**Verify fixes:** `python3 -m pytest c_augmentation/test_transforms.py -v` (15 tests, all must pass)

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
`scripts/augmentation/augment_verify.py` was already correct (passed `filename=str(fpath)`).
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

## OMP Spec Run Arg Bugs — March 17 "Fixes" Were Wrong (re-corrected 2026-03-20)

**CORRECTION:** The March 17 "fixes" to nw-omp and hotspot-omp were incorrect regressions.
Both specs have been restored to their original correct state (2026-03-20).

**`rodinia-nw-omp`** (CORRECTED 2026-03-20):
Source (`needle.cpp:249`) checks `argc == 4`, requiring **3 args**: `<dimension> <penalty> <num_threads>`.
The `"4"` was erroneously removed on 2026-03-17 based on a wrong reading of the source.
**Correct args**: `["2048","10","4"]` (correctness), `["8192","10","4"]` (performance).
Baseline stdout confirms: `"Num of threads: 4"` — the thread arg was always required.

**`rodinia-hotspot-omp`** (CORRECTED 2026-03-20):
Source (`hotspot_openmp.cpp:282`) checks `argc != 8`, requiring **7 args**:
`<grid_rows> <grid_cols> <sim_time> <num_threads> <temp_file> <power_file> <output_file>`.
`grid_cols` was erroneously removed on 2026-03-17.
**Correct args**: `["512","512","2","4","temp_512","power_512","output.out"]` (correctness),
`["1024","1024","2","4","temp_1024","power_1024","output.out"]` (performance).

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

**Post-M10b fixes applied (2026-03-20) — see M10b section below.**

**Correction to M10 spot-check claim:** `PointerArithmeticToArrayIndex` DOES fire on
`gaussian-cuda` and `gaussian-opencl` (both PASS). The M10 claim "doesn't fire on any
Rodinia CUDA spec" was based on only checking bfs/hotspot/nw/srad/backprop, none of which
use `*(ptr+i)` syntax. gaussian does.

**Transform frequency (across all 260 tasks):**
SwapCondition=162, ArithmeticTransform=69, ChangeNames=55, TypedefExpansion=7,
PointerArithmeticToArrayIndex=6, ChangeFunctionNames=2

## M10b Spec Fixes (2026-03-20) — 65 → 60 specs, target 54/60 PASS

Post-mortem on the 17 M10 failures revealed 3 distinct root causes. All fixable issues
have been addressed. Spec count reduced from 65 to 60 (5 phantom specs deleted).
mummergpu-cuda and mummergpu-omp moved to KNOWN_FAIL after Session 2 retest revealed
cascading CUDA 12 texture API removal (see below). Target revised from 56 to 54 PASS.

### Phantom Specs Deleted (5 ERROR → removed)

These specs pointed to Rodinia directories that don't exist at commit `9c10d3ea`.
They were created against Erel's forked commit `b0310d82` which was immediately reverted.
All 5 spec JSON files **deleted from `specs/`** (manifest.jsonl entries remain — append-only):

| Spec | Claimed directory | Reality |
|------|-------------------|---------|
| `rodinia-gaussian-omp` | `openmp/gaussian` | No OMP gaussian in Rodinia at 9c10d3ea |
| `rodinia-huffman-omp` | `openmp/huffman` | Huffman is CUDA-only |
| `rodinia-huffman-opencl` | `opencl/huffman` | Huffman is CUDA-only |
| `rodinia-hybridsort-omp` | `openmp/hybridsort` | Hybridsort has CUDA + OpenCL only |
| `rodinia-mummergpu-opencl` | `opencl/mummergpu` | Mummergpu has CUDA + OMP only |

### Spec Arg Fixes (3 FAIL → PASS expected)

**`rodinia-nn-cuda`** (FIXED 2026-03-20):
`filelist.txt` doesn't exist in `cuda/nn/`. The correct file is `filelist_4`.
Same bug as `nn-omp` (fixed 2026-03-19). Both specs now use `filelist_4`.

**`rodinia-hotspot-omp`** and **`rodinia-nw-omp`**: See "OMP Spec Run Arg Bugs" section above.

### Toolchain Fixes — GCC 12 / C++17 / OpenCL 3.0 incompatibilities (5 BUILD_FAIL → PASS expected)

**`rodinia-cfd-cuda`** (FIXED 2026-03-20, additional fix Session 2):
`helper_cuda.h` not found at `$(CUDA_DIR)/samples/common/inc`. File exists at:
`/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/examples/OpenACC/SDK/include/helper_cuda.h`
Fix: spec build command passes `KERNEL_DIM='-I.../examples/OpenACC/SDK/include'`.
`KERNEL_DIM` is only applied to the `euler3d` target in `cuda/cfd/Makefile` (not to
`euler3d_double`, `pre_euler3d`, `pre_euler3d_double`). Session 2 additional fix:
changed build target from `make` (all) to `make euler3d` — only the primary target
is needed and it's the only one that supports `KERNEL_DIM`.

**`rodinia-mummergpu-cuda`** and **`rodinia-mummergpu-omp`** (PARTIAL FIX → KNOWN_FAIL):
GCC 12 removed implicit `read()`/`lseek()` from POSIX — `<unistd.h>` must be explicit.
Fix applied: added `#include <unistd.h>` to both:
- `rodinia/rodinia-src/cuda/mummergpu/src/suffix-tree.cpp`
- `rodinia/rodinia-src/openmp/mummergpu/src/suffix-tree.cpp`
**Session 2 retest revealed cascade:** `unistd.h` fix resolved `suffix-tree.cpp` compile
error, but then `mummergpu_kernel.cu` fails with CUDA 12 `texture<>` API removal:
`texture<uint4, 2, cudaReadModeElementType>`, `cudaBindTextureToArray`,
`cudaUnbindTexture` — same class of error as `kmeans-cuda`. The OMP version also
compiles `mummergpu.cu`/`mummergpu_kernel.cu` via nvcc (same CUDA kernel).
Both specs moved to KNOWN_FAIL. See KNOWN_FAIL table below.

**`rodinia-cfd-opencl`** (FIXED 2026-03-20, additional fix Session 2):
Two issues: (1) `std::ifstream` can't be compared to `NULL` with `==` in C++14+ strict mode.
(2) OpenCL headers defaulting to 3.0, breaking older API calls.
Fix: `euler3d.cpp:276`: `if(file==NULL)` → `if(!file)`. Spec build command: added
`-DCL_TARGET_OPENCL_VERSION=120` to `FLAGS`.
**Session 2 additional fix:** Makefile produces `euler3d.out`, not `euler3d`.
Spec `outputs.executable` and `run.executable` updated to `"./euler3d.out"`.

**`rodinia-pathfinder-opencl`** (FIXED 2026-03-20, additional fix Session 2):
Two issues: (1) Global `int* data` conflicts with `std::data()` (C++17, GCC 12 default).
(2) OpenCL 3.0 headers deprecating `clCreateCommandQueue`.
Fix: Renamed `data` → `grid_data` throughout `opencl/pathfinder/main.cpp`.
Spec build command: `CXXFLAGS` overridden to include `-DCL_TARGET_OPENCL_VERSION=120`.
**Session 2 additional fixes:** (1) Makefile produces `pathfinder.out`, not `pathfinder`.
Spec `outputs.executable` and `run.executable` updated to `"./pathfinder.out"`.
(2) Run args were positional `["100000","100","20"]` but source uses named flags
`-c cols -r rows -h pyramid_height`. Fixed to `["-c","100000","-r","100","-h","20"]`.

### KNOWN_FAIL Specs (deferred — 6 specs)

These require either CUDA 12 API rewrites or system-level dependencies not present:

| Spec | Error | Why deferred |
|------|-------|-------------|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 | 50-100 lines of texture reference → texture object rewrite |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 | Same rewrite needed in `mummergpu_kernel.cu` |
| `rodinia-mummergpu-omp` | `texture<>` removed in CUDA 12 + `cuMemGetInfo_v2` signature change (`unsigned int*` → `size_t*`) | OMP version also uses CUDA kernel — same rewrite needed; additional `cuMemGetInfo` fix required |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found | Needs `libglew-dev` + display server; headless GPU machine |
| `rodinia-nn-opencl` | TIMEOUT (300s) from harness; SIGSEGV when run directly | Pre-existing; never passed. Harness arg `filelist.txt` doesn't exist in `opencl/nn/` — hangs on file I/O. Direct binary run crashes with SIGSEGV (exit -11) in OpenCL runtime |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime | Pre-existing; never passed; exit code -11 |

**Do not include these 6 specs in eval batches.** Use the 54 remaining PASS specs.

## Gaussian OMP Spec — DELETED (2026-03-20)

`specs/rodinia-gaussian-omp.json` was one of 5 phantom specs pointing to non-existent directories
at Rodinia commit `9c10d3ea`. It has been **deleted** from `specs/`. See M10b section above.
Gaussian has only CUDA and OpenCL versions in this commit — no OpenMP variant exists.
Use streamcluster or backprop as replacement for 10-kernel batch.

## nn-{omp,cuda} filelist.txt Bug (FIXED)

Both the OMP and CUDA nn specs had `filelist.txt` as a run arg, but that file doesn't exist
in either `openmp/nn/` or `cuda/nn/`. The correct file is `filelist_4`.

- `specs/rodinia-nn-omp.json`: Fixed 2026-03-19 — `filelist.txt` → `filelist_4`
- `specs/rodinia-nn-cuda.json`: Fixed 2026-03-20 — same bug, missed in the 2026-03-19 fix

`filelist_4` contains correct relative paths to `../../data/nn/cane4_*.db`.
Without this file, `fopen(NULL)` is called → SIGSEGV at runtime.

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

## Session 2 Targeted Retest (2026-03-20)

Ran `harness verify` at L0 on all 8 M10b-fixed specs and 4 original KNOWN_FAIL specs.
6/8 M10b-fixed specs verified PASS. 2 moved to KNOWN_FAIL (cascade from unistd.h fix).
4/4 original KNOWN_FAIL confirmed still failing for documented reasons.

**Final verified status after Session 2 (60 specs total):**

| Spec | Result | Root cause / fix |
|------|--------|-----------------|
| `rodinia-hotspot-omp` | **PASS** | 7 args restored (grid_cols was removed) |
| `rodinia-nw-omp` | **PASS** | 3 args restored (num_threads was removed) |
| `rodinia-nn-cuda` | **PASS** | `filelist.txt` → `filelist_4` |
| `rodinia-cfd-cuda` | **PASS** | `make euler3d` target only + `KERNEL_DIM` |
| `rodinia-cfd-opencl` | **PASS** | `./euler3d.out` executable + `-DCL_TARGET_OPENCL_VERSION=120` |
| `rodinia-pathfinder-opencl` | **PASS** | `./pathfinder.out` + named args `-c/-r/-h` |
| `rodinia-mummergpu-cuda` | **KNOWN_FAIL** | CUDA 12 texture<> API removal in mummergpu_kernel.cu |
| `rodinia-mummergpu-omp` | **KNOWN_FAIL** | OMP version also uses CUDA kernel — same texture<> issue |
| `rodinia-kmeans-cuda` | **KNOWN_FAIL** (confirmed) | CUDA 12 texture<> API removal |
| `rodinia-hybridsort-cuda` | **KNOWN_FAIL** (confirmed) | GL/glew.h not found |
| `rodinia-nn-opencl` | **KNOWN_FAIL** (confirmed) | TIMEOUT (300s) from harness (filelist.txt missing); SIGSEGV (exit -11) from direct run |
| `rodinia-kmeans-opencl` | **KNOWN_FAIL** (confirmed) | SIGSEGV in OpenCL runtime (exit -11) |

**Overall: 54/60 PASS, 6/60 KNOWN_FAIL.**
Use the 54 PASS specs for eval batches.

**Key discovery — cascading fixes:**
The M10b `unistd.h` fix for mummergpu resolved `suffix-tree.cpp` compile errors,
which exposed a deeper CUDA 12 `texture<>` API removal in `mummergpu_kernel.cu`.
This is a common pattern when fixing the first error in a multi-error chain reveals new errors
that were previously unreachable. Both mummergpu variants are now classified KNOWN_FAIL.

**Key discovery — spec-executable mismatches:**
`cfd-opencl` and `pathfinder-opencl` had specs declaring wrong executable names
(`./euler3d` vs `./euler3d.out`, `./pathfinder` vs `./pathfinder.out`).
Builds succeeded (exit 0) but harness post-build existence check at builder.py:178 failed.
Rule: always verify `outputs.executable` matches the actual Makefile output artifact.

**Key discovery — run arg format:**
`pathfinder-opencl` spec had positional args `["100000","100","20"]` but source parses
named flags `-c cols -r rows -h pyramid_height`. Rule: always check source's `init()`/`argc`
parsing before writing spec run args.

## Session 3 Independent Re-verification (2026-03-20)

Full re-run of all 12 Session 2 specs using wave-based parallel execution (Waves 1-4).
Commit `de95155` validated — all 12 classifications match. One failure mode detail corrected.

| Spec | Session 2 | Session 3 | Match |
|------|-----------|-----------|-------|
| `rodinia-hotspot-omp` | PASS | PASS | ✓ |
| `rodinia-nw-omp` | PASS | PASS | ✓ |
| `rodinia-nn-cuda` | PASS | PASS | ✓ |
| `rodinia-cfd-cuda` | PASS | PASS | ✓ |
| `rodinia-cfd-opencl` | PASS | PASS | ✓ |
| `rodinia-pathfinder-opencl` | PASS | PASS | ✓ |
| `rodinia-mummergpu-cuda` | BUILD_FAIL | BUILD_FAIL | ✓ |
| `rodinia-mummergpu-omp` | BUILD_FAIL | BUILD_FAIL | ✓ |
| `rodinia-kmeans-cuda` | BUILD_FAIL | BUILD_FAIL | ✓ |
| `rodinia-hybridsort-cuda` | BUILD_FAIL | BUILD_FAIL | ✓ |
| `rodinia-nn-opencl` | KNOWN_FAIL | KNOWN_FAIL | ✓ (mode: TIMEOUT from harness, SIGSEGV from direct run) |
| `rodinia-kmeans-opencl` | KNOWN_FAIL | KNOWN_FAIL | ✓ (SIGSEGV, exit -11) |

**Correction:** `nn-opencl` failure mode updated — harness produces TIMEOUT (spec uses `filelist.txt`
which doesn't exist in `opencl/nn/`), while direct binary run produces SIGSEGV (exit -11) in the
OpenCL runtime. Both confirm KNOWN_FAIL. Classification unchanged: 54/60 PASS.

**New finding (Session 3):** `mummergpu-omp` surfaces an additional CUDA 12 API change beyond
`texture<>` removal: `cuMemGetInfo_v2` signature changed from `(unsigned int*, unsigned int*)`
to `(size_t*, size_t*)`. This is a previously undocumented cascade error. KNOWN_FAIL table
updated to reflect both failure modes. Any mummergpu fix must address both the texture object
rewrite and the `cuMemGetInfo` signature update.

## Full Augmentation Batch Retest — 60 Specs × L1–L4 (2026-03-20)

Definitive augmentation baseline for SC26 paper. First run on the clean 60-spec set
(5 phantoms deleted, all M10b spec fixes applied, G1/G2 harness gaps fixed).
240 tasks (60 specs × 4 levels), seed=42, `--config correctness`.
Results: `results/augmentation/retest_post_session2.{json,md}`.

**54/60 PASS at all levels (level-invariant). No transform introduces new failures.**

| Level | PASS | BUILD_FAIL | FAIL | ERROR | Total |
|-------|------|-----------|------|-------|-------|
| L1    | 54   | 4         | 2    | 0     | 60    |
| L2    | 54   | 4         | 2    | 0     | 60    |
| L3    | 54   | 4         | 2    | 0     | 60    |
| L4    | 54   | 4         | 2    | 0     | 60    |

**BUILD_FAIL (4):** hybridsort-cuda, kmeans-cuda, mummergpu-cuda, mummergpu-omp
**FAIL (2):** kmeans-opencl, nn-opencl

**Improvement from M10 baseline:** 48/65 (73%) → 54/60 (90%)
(Numerator: +6 M10b fixes; Denominator: -5 phantom specs)

**M10b-fixed specs confirmed PASS (all 6):**
cfd-cuda, cfd-opencl, pathfinder-opencl, nn-cuda, hotspot-omp, nw-omp

**Transform frequency (across 240 tasks):**
SwapCondition=162, ArithmeticTransform=69, ChangeNames=55, TypedefExpansion=7,
PointerArithmeticToArrayIndex=6, ChangeFunctionNames=2

**Key result for SC26 paper:** Level-invariance holds across all 54 passing specs —
augmentation at L1–L4 introduces zero correctness regressions. Transforms are semantics-preserving.

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
