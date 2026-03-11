# Augmentation Integration Test Results
**Date:** 2026-03-10
**Branch:** main (post `erel/aug` merge)
**Seed:** 42
**Tool:** `scripts/augment_verify.py`

---

## Phase 0 – Prerequisites: PASS
All imports resolved correctly:
- `clang.cindex` → `env_parbench/lib/.../clang/cindex.py`
- `pydantic.BaseModel` → OK
- `c_augmentation.augment_dataset` (all transforms + `augment_code`) → OK
- `ci.Index.create()` → OK

---

## Phase 1 – Unit Tests: 8/8 PASS (0.21s)
```
test_arithmetic_transform                      PASS
test_swap_condition_positive                   PASS
test_swap_condition_negative_template_and...  PASS
test_pointer_arithmetic_positive               PASS
test_pointer_arithmetic_negative_typedef_decl PASS
test_typedef_expansion                         PASS
test_change_names                              PASS
test_real_kernel_pipeline                      PASS
```

---

## Phase 2 – Prompt Path (`harness prompt --augment_level N`)

All 5 kernels × levels 0–4 produced output without crashes or `FILE NOT FOUND` errors.

### `.cl` Inconsistency (Known Issue)
`spec_loader.py:get_prompt_payload` (line 195) augments only:
```python
[".c", ".cpp", ".cu", ".h", ".hpp", ".cuh", ".dp.cpp"]
```
`.cl` is absent. Confirmed for `rodinia-nw-opencl`:
- `nw.cl` content is **identical** between `--augment_level 0` and `--augment_level 4`
- `nw.c` content **differs** (augmentation applied)

`augment_verify.py` includes `.cl` in `AUGMENTABLE_SUFFIXES` and does augment `.cl` files (confirmed at L3 below).

**Recommendation:** Add `.cl` to the suffix list in `spec_loader.py:get_prompt_payload` for consistency.

---

## Phase 3 – Full Pipeline (`augment_verify.py --seed 42`)

### Results Matrix

| Kernel | L1 | L2 | L3 | L4 |
|--------|----|----|----|----|
| rodinia-srad-omp | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| rodinia-bfs-cuda | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| rodinia-lavamd-cuda | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| rodinia-hotspot3d-cuda | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| rodinia-nw-opencl | ✓ PASS | ✓ PASS | ✓ PASS | ✗ BUILD_FAIL |

### Transforms Applied per Kernel × Level

| Kernel | L1 | L2 | L3 | L4 |
|--------|----|----|----|----|
| srad-omp | *(none)* | *(none)* | SwapCondition, PointerArith | Arith, ChangeNames, PointerArith, Swap |
| bfs-cuda | *(none)* | *(none)* | ChangeNames, PointerArith, Swap | ChangeNames, PointerArith, Swap |
| lavamd-cuda | *(none)* | *(none)* | ChangeNames, PointerArith, Swap | ChangeNames, PointerArith, Swap |
| hotspot3d-cuda | *(none)* | *(none)* | Arith, PointerArith, Swap | Arith, ChangeNames, PointerArith, Swap |
| nw-opencl | *(none)* | *(none)* | PointerArith, Swap | Arith, ChangeNames, PointerArith, Swap |

**Observation:** At L1 and L2, no transforms fired for any kernel with seed=42. Both L1 and L2 select `num_transforms=1` (since `max(1, int(5×0.33))=1`), and with this seed the randomly chosen single transform found no applicable candidates. The PASSes at L1/L2 are therefore not testing augmented correctness — they pass because the code was unchanged.

---

## Bugs Found

### Bug A — `PointerArithmeticToArrayIndex`: Overlapping/Nested Subscripts

**Severity:** HIGH (causes BUILD_FAIL at L3+)
**Affected:** srad-omp (L3, L4), bfs-cuda (L3, L4), lavamd-cuda (L3, L4), nw-opencl (L4)

**Root cause:** `AstTransform.apply()` collects *all* `ARRAY_SUBSCRIPT_EXPR` candidates including nested ones (e.g., `iS[i]` inside `J[iS[i]*cols+j]`). When multiple candidates are selected (at L3: 66% of all candidates), a nested subscript and its outer parent may both be selected. Both edits are collected into a single `RewriteCandidate` and applied in one pass via `_apply_candidate`. Since edits are applied at **original** byte offsets in reverse order, the inner edit shifts bytes, causing the outer edit's `end_offset` to point into the wrong position of the modified buffer.

**Example (srad-omp L3):**
```
// Original:
dS[k] = J[iS[i] * cols + j] - Jc;

// After combined edit (inner iS[i] + outer J[...] both selected):
*((dS) + (k)) = *((J) + (iS[i] * cols + j))ols + j] - Jc;
//                                                  ^^^^ stale bytes
```

**Fix:** Before returning from `AstTransform.apply()`, validate the combined `RewriteCandidate` with `_validate_rewrite`. Better yet, filter out candidates whose byte range overlaps any other selected candidate (standard non-overlapping edit selection).

---

### Bug B — `PointerArithmeticToArrayIndex`: Struct Member Access Precedence

**Severity:** HIGH (causes BUILD_FAIL at L3+)
**Affected:** bfs-cuda (L3, L4), lavamd-cuda (L3)

**Root cause:** When `arr[i].member` is transformed to `*((arr)+(i)).member`, the result is syntactically wrong. In C/C++, `.` has higher precedence than unary `*`, so `*ptr.member` parses as `*(ptr.member)`. The correct transformation requires extra parentheses: `(*((arr)+(i))).member`.

**Example (bfs-cuda L3):**
```
// Original:
g_graph_nodes[id].starting

// After transform:
*((g_graph_nodes) + (id)).starting
// Compiler error: expression must have class type but it has type "Node *"
```

**Fix:** In `PointerArithmeticToArrayIndex._find_candidates`, when the `ARRAY_SUBSCRIPT_EXPR` cursor's parent is a `MEMBER_REF_EXPR`, wrap the pointer form in an extra pair of parens: `(*((arr)+(i))).member` instead of `*((arr)+(i)).member`. Or more simply: always emit `(*((arr)+(i)))` instead of `*((arr)+(i))`.

---

### Bug C — `SwapCondition`: Assignment-in-Condition Precedence

**Severity:** HIGH (causes BUILD_FAIL at L3+)
**Affected:** hotspot3d-cuda (L3, L4)

**Root cause:** The expression `fp = fopen(file, "r") == 0` is parsed by C/C++ as `fp = (fopen(...) == 0)` (since `==` binds tighter than `=`). The libclang AST sees this as a `BINARY_OPERATOR ==` with LHS=`fp = fopen(file, "r")` and RHS=`0`. `SwapCondition` swaps to `0 == fp = fopen(file, "r")`, which parses as `(0 == fp) = fopen(...)` — assigning to a non-lvalue.

**Example (hotspot3d-cuda L3):**
```c
// Original:
if( fp = fopen(file, "r") == 0 )

// After SwapCondition:
if( 0 == fp = fopen(file, "r" ) )
// Compiler error: expression must be a modifiable lvalue
```

**Fix:** In `SwapCondition._find_candidates`, skip any `BINARY_OPERATOR ==` node where either child contains an assignment (`=`, `+=`, etc.). Alternatively, check if either operand's extent contains a `BINARY_OPERATOR =` cursor.

---

### Observation D — `nw-opencl` L3: `.cl` File Augmented via `augment_verify.py`

The `nw.cl` kernel file (OpenCL) was successfully augmented (`SwapCondition` applied) and the result built and ran correctly. This confirms that libclang can parse `.cl` files with `-xc++ -std=c++17` flags successfully for the Needleman-Wunsch kernel, and that `SwapCondition` produces valid code for it.

---

### Observation E — `hotspot3d-cuda` Double-Include Pattern: No Issue

`3D.cu` has `#include "opt1.cu"` at line 22. Both files are independently augmented by `_augment_payload`, and the `#include` at compile time picks up the modified `opt1.cu`. libclang's `_cursor_in_main_file` guard prevents double-augmentation: cursors from included files are skipped during AST traversal. No double-transform bug occurred.

---

## Summary

| Phase | Status |
|-------|--------|
| Phase 0: Prerequisites | ✓ PASS |
| Phase 1: Unit tests (8/8) | ✓ PASS |
| Phase 2: Prompt path (5×5 combos) | ✓ PASS (with `.cl` inconsistency noted) |
| Phase 3: augment_verify L1-L2 | ✓ PASS (no transforms fired — trivial) |
| Phase 3: augment_verify L3-L4 | ✗ PARTIAL (4/5 kernels BUILD_FAIL; nw-opencl L3 PASS) |

**Bugs requiring fixes before L3/L4 augmentation is production-ready:**
1. **Bug A** (overlapping nested subscripts) — validate combined candidates in `AstTransform.apply`
2. **Bug B** (struct member access precedence) — parenthesize pointer form as `(*((arr)+(i)))`
3. **Bug C** (assignment-in-condition) — skip `==` nodes where operands contain assignment

**The harness integration itself works correctly:** `augment_verify.py` correctly orchestrates the augment → copy → patch-spec → build → run → verify pipeline. The failures are all in the augmentation transforms themselves, not in the integration layer.
