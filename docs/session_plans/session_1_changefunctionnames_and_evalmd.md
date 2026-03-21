# Session 1: Fix ChangeFunctionNames Harness Gap + Stale evaluation.md

> **Depends on:** Nothing (first in chain)
> **Blocks:** Session 2 (targeted retest), Session 3 (full retest)
> **Estimated time:** 15–20 minutes
> **Thinking level:** `ultrathink` (multi-file, cross-referencing)
> Use 5 subagents

---

## Objective

Two targeted edits to fix quality issues found in the sprint audit:
1. **Task 1a:** Add `ChangeFunctionNames` to harness `AugmentationConfig` (currently missing — `augment_verify.py` has it, `spec_loader.py` does not)
2. **Task 1b:** Fix stale OMP args in `.claude/rules/evaluation.md` (currently contradicts the actual spec JSONs and source code)

---

## Claude Code Prompt:

```
I need to complete Session 1 of the Sprint Audit Fix Plan: two targeted edits.

## Task 1a: Add ChangeFunctionNames to harness AugmentationConfig

**File:** `harness/spec_loader.py`

The import block at lines 167-174 imports transforms from `c_augmentation.augment_dataset`,
and lines 177-185 build the transforms list. `ChangeFunctionNames` is MISSING from both.

The reference implementation in `scripts/augmentation/augment_verify.py` (lines 50-70)
already includes `ChangeFunctionNames` correctly — use that as the pattern.

**Exact changes needed:**

1. Add `ChangeFunctionNames,` to the import block (after `ChangeNames,` on line 173):
```python
from c_augmentation.augment_dataset import (
    AugmentationConfig,
    ArithmeticTransform,
    SwapCondition,
    PointerArithmeticToArrayIndex,
    TypedefExpansion,
    ChangeNames,
    ChangeFunctionNames,
    augment_code
)
```

2. Add `ChangeFunctionNames(level=augment_level),` to the transforms list (after line 184):
```python
aug_config = AugmentationConfig(
    level=augment_level,
    transforms=[
        ArithmeticTransform(level=augment_level),
        SwapCondition(level=augment_level),
        PointerArithmeticToArrayIndex(level=augment_level),
        TypedefExpansion(level=augment_level),
        ChangeNames(level=augment_level),
        ChangeFunctionNames(level=augment_level),
    ]
)
```

## Task 1b: Fix stale OMP args in evaluation.md

**File:** `.claude/rules/evaluation.md` (around lines 116-120)

The current text says:
```
Known-correct args (verified 2026-03-17):
- `rodinia-nw-omp`: `['2048', '10']` — NOT `['2048', '10', '4']` (extra was wrong)
- `rodinia-hotspot-omp`: `['512', '2', '4', 'temp_512', 'power_512', 'output.out']` — note: single grid arg, temp BEFORE power
```

This is WRONG. The March 17 "fixes" were reverted on March 20. The actual specs and source code say:
- nw-omp needs 3 args: `['2048', '10', '4']` (source: `needle.cpp:249` checks `argc == 4`)
- hotspot-omp needs 7 args: `['512', '512', '2', '4', 'temp_512', 'power_512', 'output.out']` (source: `hotspot_openmp.cpp:282` checks `argc != 8`)

Replace with:
```
Known-correct args (re-verified 2026-03-20 against source argc checks):
- `rodinia-nw-omp`: `['2048', '10', '4']` — 3 args: <dimension> <penalty> <num_threads> (needle.cpp:249 checks argc==4)
- `rodinia-hotspot-omp`: `['512', '512', '2', '4', 'temp_512', 'power_512', 'output.out']` — 7 args: <rows> <cols> <sim_time> <threads> <temp> <power> <output> (hotspot_openmp.cpp:282 checks argc!=8)
```
Leave the srad-omp line unchanged — it was always correct.

## Verification (MANDATORY — run all before committing)

1. `source env_parbench/bin/activate && python3 -m pytest c_augmentation/test_transforms.py -v`
   → All 15 tests must pass (confirms ChangeFunctionNames import chain works)

2. `python3 -c "from harness.spec_loader import get_prompt_payload; print('Import OK')"`
   → Must print "Import OK" (confirms the new import resolves)

3. Cross-check: Read the actual spec JSONs to confirm evaluation.md now matches:
   - `specs/rodinia-nw-omp.json` → correctness_config.arguments should be `["2048","10","4"]`
   - `specs/rodinia-hotspot-omp.json` → correctness_config.arguments should be `["512","512","2","4","../../data/hotspot/temp_512","../../data/hotspot/power_512","output.out"]`

## Commit and Push

Commit ONLY after ALL verification passes. Then push immediately:

```
Fix ChangeFunctionNames harness gap and stale evaluation.md OMP args

- Add ChangeFunctionNames to spec_loader.py import + transforms list
  (was already in augment_verify.py but missing from harness path)
- Correct nw-omp and hotspot-omp args in evaluation.md rules file
  (March 17 "fixes" were wrong; restored to match source argc checks)
```

```bash
git push origin main
```
```

---

## Files Reference

| File | Lines | What Changes |
|------|-------|-------------|
| `harness/spec_loader.py` | 167-186 | Add `ChangeFunctionNames` to import + transforms list |
| `.claude/rules/evaluation.md` | 116-120 | Fix nw-omp (2→3 args) and hotspot-omp (6→7 args) |

## Cross-Reference Sources (for verification)

| Source | Evidence |
|--------|----------|
| `scripts/augmentation/augment_verify.py:53,68` | Already has `ChangeFunctionNames` — the reference pattern |
| `c_augmentation/augment_dataset.py:1479` | `class ChangeFunctionNames(Transform)` exists |
| `c_augmentation/test_transforms.py:169-248` | 4 unit tests for `ChangeFunctionNames` |
| `rodinia/rodinia-src/openmp/nw/needle.cpp:249` | `if (argc == 4)` — needs 3 user args |
| `rodinia/rodinia-src/openmp/hotspot/hotspot_openmp.cpp:282` | `if (argc != 8)` — needs 7 user args |
| `specs/rodinia-nw-omp.json:67-71` | correctness args: `["2048","10","4"]` |
| `specs/rodinia-hotspot-omp.json:71-79` | correctness args: `["512","512","2","4","...temp_512","...power_512","output.out"]` |

## Success Criteria

- [x] `ChangeFunctionNames` appears in `spec_loader.py` import AND transforms list
- [x] `evaluation.md` matches actual spec JSONs and source argc checks
- [x] All 15 unit tests pass
- [x] Import check passes
- [x] Verified, committed, and pushed to remote
