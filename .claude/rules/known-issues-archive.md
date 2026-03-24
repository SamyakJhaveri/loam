---
paths:
  - "c_augmentation/**"
  - "harness/**"
  - "scripts/augmentation/**"
  - "results/augmentation/**"
  - "specs/**"
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
