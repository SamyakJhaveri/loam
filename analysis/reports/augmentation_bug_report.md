# Augmentation Bug Report

**Date:** 2026-03-09
**Branch:** `erel/aug`
**Reported by:** Samyak
**Affects:** `c_augmentation/augment_dataset.py`

---

## Summary

Two bugs were found during Phase 2 integration testing of the `erel/aug` augmentation code with the ParBench harness. Both bugs are in `augment_dataset.py`. One was fixed during testing (the UTF-8/libclang offset mismatch + CUDA DECL_REF_EXPR miss); two remain open and are documented below for Erel to resolve.

---

## Bug 1 (Fixed) — UTF-8 Byte/Character Offset Mismatch in `_apply_candidate`

**Status:** Fixed (applied to `erel/aug` during this session)

**Root cause:** libclang reports all source positions as **byte offsets** in the UTF-8-encoded file. The original `_apply_candidate` used those offsets as Python *character* indices. Any multi-byte Unicode character in the source (e.g. an em-dash `—` in a comment — 3 UTF-8 bytes, 1 Python `str` character) caused all edits at positions after that character to land at wrong positions, producing garbled output like `&d_var_7sizeof(Node)` instead of `&var_7, sizeof(Node)`.

**Fix applied:** `_apply_candidate` now encodes the source to `bytes`, performs all slicing and replacement on `bytes`, then decodes back to `str`. The replacement string is also encoded to `bytes` before insertion.

---

## Bug 2 (Fixed) — `ChangeNames` Misses Reference Sites in CUDA-Specific Syntax

**Status:** Fixed (applied to `erel/aug` during this session)

**Root cause:** libclang, when parsing `.cu` files without full CUDA headers (as `augment_dataset.py` does), does not emit `DECL_REF_EXPR` AST nodes for variable references inside `cudaMemcpy(...)` arguments and kernel-launch `<<<>>>` syntax. The `_symbol_edits` AST walk found the declaration site and some references but missed the CUDA-call argument positions, producing **partial renames**: the `cudaMalloc` line got the new name but the `cudaMemcpy` line kept the original name. This produced code that did not compile.

**Fix applied:** After the `DECL_REF_EXPR` AST walk, a supplementary token scan is performed over all tokens in the owning function's extent. Any `IDENTIFIER` token matching the declaration's spelling that was not already covered by the AST walk is added as an additional edit. The existing `_validate_rewrite` guard rejects the whole rename if the result introduces unsafe output.

---

## Bug 3 (Open) — `PointerArithmeticToArrayIndex` Breaks Struct Member Access

**Status:** Open — needs fix from Erel

**File:** `c_augmentation/augment_dataset.py`, class `PointerArithmeticToArrayIndex`

**Observed symptom:** At `augment_level=4`, `rodinia-bfs-cuda.json` fails to build after augmentation. The build error is a type/syntax error in augmented `bfs.cu`.

**Root cause:** When the transform converts an `ARRAY_SUBSCRIPT_EXPR` to pointer arithmetic form, it uses the replacement:
```
*((base) + (idx))
```
This is correct when the subscript expression is standalone. However, when the subscript is immediately followed by a struct member access (`.` or `->`), the result is syntactically wrong:

```c
// Original
g_graph_nodes[i].starting

// After transform — WRONG
*((g_graph_nodes) + (i)).starting
// Parsed as: *(ptr.starting) because '.' binds tighter than '*'

// Correct form
(*((g_graph_nodes) + (i))).starting
```

The `.` operator has higher precedence than unary `*`, so the pointer dereference applies to the wrong subexpression.

**Fix needed:** In `PointerArithmeticToArrayIndex._find_candidates()`, when generating the replacement for an `ARRAY_SUBSCRIPT_EXPR`, check whether the cursor's parent is a `MEMBER_REF_EXPR` (i.e., the subscript result is immediately accessed with `.` or `->`). If so, wrap the entire pointer form in an extra pair of parentheses:
```python
replacement = f"(*({base_text}) + ({idx_text}))"  # for struct member access context
replacement = f"*(({base_text}) + ({idx_text}))"  # for all other contexts
```

Alternatively, always emit the fully-parenthesised form `(*((base) + (idx)))` — this is valid in all contexts and avoids the precedence issue entirely.

**Workaround (for now):** Do not use `augment_level=4` on CUDA specs with struct arrays (like `rodinia-bfs-cuda`). Levels 1–3 are less aggressive and the random sampling is less likely to hit this case.

---

## Bug 4 (Open) — `_validate_rewrite` Diagnostic Threshold Too Permissive

**Status:** Open — needs fix from Erel

**File:** `c_augmentation/augment_dataset.py`, function `_validate_rewrite`

**Current code:**
```python
def _fatal_diagnostics(tu: ci.TranslationUnit) -> int:
    return sum(
        1 for diag in tu.diagnostics
        if diag.severity >= ci.Diagnostic.Fatal  # severity == 4
    )

def _validate_rewrite(candidate, code, index):
    ...
    return _fatal_diagnostics(updated) <= _fatal_diagnostics(baseline)
```

**Problem:** The safety gate only rejects rewrites that introduce new **fatal** diagnostics (severity 4). Compile errors (severity 3, `Diagnostic.Error`) pass through undetected. This means a syntactically broken rewrite (like Bug 3 above) is accepted by `_validate_rewrite` and reaches `nvcc`, which then fails with an error.

This is directly responsible for Bug 3's BUILD_FAIL reaching the compiler instead of being silently rejected by the safety gate.

**Fix needed:** Change the diagnostic threshold from `Diagnostic.Fatal` (4) to `Diagnostic.Error` (3):

```python
def _fatal_diagnostics(tu: ci.TranslationUnit) -> int:
    return sum(
        1 for diag in tu.diagnostics
        if diag.severity >= ci.Diagnostic.Error  # severity >= 3
    )
```

**Trade-off to be aware of:** This stricter gate will reject more rewrites — including some that libclang reports as errors but that `nvcc` or `gcc` would actually accept (e.g., CUDA-specific constructs that libclang doesn't understand). In practice this means fewer augmentations get applied per file at any given level, but the ones that do are guaranteed to be syntactically valid from libclang's perspective. Whether this trade-off is acceptable depends on how aggressive you need the augmentation to be.

**Alternative (more surgical):** Keep the Fatal threshold globally but add an Error-level check specifically inside `PointerArithmeticToArrayIndex._find_candidates()` per candidate, so only the struct-member-access candidates are filtered out.

---

## Testing Context

These bugs were found during:
- **Phase 0:** Unit tests (`c_augmentation/test_transforms.py`) — all 8 pass after fixes for Bugs 1 and 2
- **Phase 2:** End-to-end `scripts/augment_verify.py` smoke test on 3 specs at levels 0–4

The following test triggers Bug 3 and Bug 4 reliably:
```bash
source env_parbench/bin/activate
python3 scripts/augment_verify.py specs/rodinia-bfs-cuda.json --augment_level 4 --seed 42
# Expected current output: BUILD_FAIL
# Expected after fix: PASS (or at minimum, no BUILD_FAIL — transforms safely skipped)
```
