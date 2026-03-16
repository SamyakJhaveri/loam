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

## Smoke Tests (verified 2026-03-06 — all PASS)

```
rodinia-bfs-cuda    BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-hotspot-omp BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-bfs-opencl  BUILD: PASS | RUN: PASS | VERIFY: PASS
```

Fixes applied: CUDA_DIR path, `make hotspot` target, OpenCL include/lib paths,
`CC_FLAGS=-std=c++14`, data path symlinks (`rodinia/rodinia-src/data/` → `rodinia-data/`).
