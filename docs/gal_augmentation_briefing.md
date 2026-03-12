# Answer for Gal: L1/L2 vs L3/L4 — What's Going On, and What To Do

**Date:** 2026-03-12
**Author:** Samyak (via ParBench evaluation pipeline)

---

## TL;DR

**Yes, use L2 and move to the testing stage.** L3/L4 have known bugs that are fixable but represent diminishing returns. L1/L2 are solid (92% pass rate against corrected baseline) and DO apply real, meaningful code transforms — they are not no-ops. This is sufficient for SC26.

---

## What L1/L2 vs L3/L4 Actually Means

The augmentation level controls **two dimensions simultaneously**:

| Level | How many of 5 transforms fire | How many edit sites per transform |
|-------|-------------------------------|----------------------------------|
| **L1** | 1 (randomly selected) | 1 site only |
| **L2** | 1 (randomly selected) | 33% of available sites |
| **L3** | 3 (randomly selected) | 66% of available sites |
| **L4** | All 5 transforms | 100% of available sites |

**The critical jump is L2 → L3**: going from 1 transform to 3, and from 33% to 66% of sites. Transforms are applied **sequentially** — each one rewrites the code, and the next one operates on already-modified code. This compounding is why L3/L4 break.

### The 5 Transforms

| # | Transform | What it does | Status |
|---|-----------|--------------|--------|
| 1 | **ArithmeticTransform** | `x += 1` ↔ `x = x + 1` | ✅ Safe |
| 2 | **SwapCondition** | `a < b` → `b > a` | ✅ Safe (after Bug C fix) |
| 3 | **PointerArithmeticToArrayIndex** | `*(arr+i)` ↔ `arr[i]` | ✅ Mostly safe (after Bug A/B fix) |
| 4 | **TypedefExpansion** | Expands typedef aliases to underlying types | ⚠️ Bug D: still broken |
| 5 | **ChangeNames** | Renames local variables | ⚠️ Bug E: broken at L3/L4 |

---

## Current Pass Rates (Post-fix, 60 Rodinia specs, evaluated 2026-03-11)

### Combined (all APIs)

| Level | PASS | BUILD_FAIL | FAIL | Pass Rate |
|-------|------|-----------|------|-----------|
| **L1** | **45/60** | 11 | 4 | **75%** |
| **L2** | **45/60** | 11 | 4 | **75%** |
| L3 | 29/60 | 29 | 2 | 48% |
| L4 | 22/60 | 35 | 3 | 37% |

### Per API

| API | Specs | L1 PASS | L2 PASS | L3 PASS | L4 PASS |
|-----|-------|---------|---------|---------|---------|
| CUDA | 22 | 15 (68%) | 15 (68%) | 13 (59%) | 11 (50%) |
| OMP | 18 | 15 (83%) | 14 (78%) | 9 (50%) | 7 (39%) |
| OpenCL | 20 | 15 (75%) | 16 (80%) | 7 (35%) | 4 (20%) |

### Against Corrected Baseline

Of the 60 specs, ~49–50 pass without any augmentation (baseline). Of those:
- L1: ~45/50 = **~90% corrected pass rate**
- L2: ~45/50 = **~90% corrected pass rate**

The 15 L1/L2 failures break down as:
- ~9 specs: fail at baseline (missing headers, deprecated APIs, source issues)
- 4 specs: runtime/correctness failures at baseline (`nn-cuda/omp/opencl`, `kmeans-opencl`)
- 2 specs: Bug D (`streamcluster-cuda`, `streamcluster-omp` — TypedefExpansion on struct pointers, fails even at L1)

---

## Remaining Bugs in L3/L4

### Already Fixed (2026-03-11)

| Bug | Description | Fix |
|-----|-------------|-----|
| **Bug A** | PointerArith: overlapping nested subscripts corrupt output | Added overlap filter + re-validation in `apply()` |
| **Bug B** | PointerArith: `arr[i].member` → wrong precedence | Emit `(*((arr)+(i))).member` |
| **Bug C** | SwapCondition: `fp = fopen() == 0` corrupts to non-lvalue | Skip comparisons where operand contains assignment |
| **Fix V** | Diagnostic threshold rejected valid code | Lowered from `>= Fatal` to `>= Error` |

### Still Unfixed

| Bug | Transform | Symptom | Affected | Effort |
|-----|-----------|---------|----------|--------|
| **Bug D** | TypedefExpansion | Expands struct/pointer typedefs → invalid C | 2 specs ALL levels | ~1 hr |
| **Bug E** | ChangeNames | Renames struct field references via token scan | ~8 specs at L3/L4 | ~2 hrs |
| **Bug F** | PointerArith | Empty parens from failed libclang child cursors in macros | ~7 specs at L3/L4 | ~1 hr |
| **Bug G** | PointerArith | `arr[0]/arr2[0]` → `*((arr)+(0))/*((arr2)+(0))` creates `/*` comment | ~5 specs at L3/L4 | ~1 hr |

### If Fixed: Expected Impact

- Bug D fix → recovers 2 specs at ALL levels (streamcluster)
- Bug E+F+G fix → could bring L3 from 48% → ~65–70%; L4 from 37% → ~50%
- Even with all fixed, L3/L4 will never reach 90%+ due to fundamental transform compounding

---

## Recommended Path Forward for SC26

### Decision: Use L2

1. **L2 applies real transforms** — seed 42 causes various transforms to fire across specs (SwapCondition, ArithmeticTransform, ChangeNames, PointerArith all observed at L2)
2. **92% corrected pass rate** — robust and defensible for a paper
3. **Simple story** — "1 randomly-selected transform applied to 33% of applicable sites"

### The 45 Clean Specs (pass at both L1 and L2)

**CUDA (15):** backprop, bfs, bptree, dwt2d, gaussian, heartwall, hotspot, hotspot3d, huffman, lavamd, lud, nw, particlefilter, pathfinder, srad

**OMP (14):** backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nw, particlefilter, pathfinder, srad

**OpenCL (16):** backprop, bfs, bptree, dwt2d, gaussian, heartwall, hotspot, hotspot3d, hybridsort, lavamd, lud, myocyte, nw, particlefilter, srad, streamcluster

### Optional: Fix Bug D (+2 specs)

Filing Bug D is a ~1 hour fix in `TypedefExpansion._find_candidates()` — filter out struct types, pointer-to-struct, and `size_t`. Would recover `streamcluster-cuda` and `streamcluster-omp`, bringing the clean set to 47 specs.

### Bug Fixing for Erel

If Erel has bandwidth (~5 hours total):
- **Bug D is worth fixing** — simple, recovers specs at all levels, good ROI
- **Bugs E/F/G are lower priority** — only affect L3/L4, not needed for SC26
- All are fixable — they're edge cases, not design flaws

---

## Key Files

| File | Purpose |
|------|---------|
| `c_augmentation/augment_dataset.py` | All transform implementations and bug fixes |
| `results/augmentation/eval_{cuda,omp,opencl}.json` | Per-spec post-fix evaluation data |
| `results/augmentation/eval_{cuda,omp,opencl}.md` | Human-readable evaluation reports |
| `results/augmentation/augmentation_status_report_2026-03-10.md` | Pre-fix bug documentation |
| `docs/gal_augmentation_briefing.md` | This document |
| `visualizations/augmentation_deep_dive.html` | Interactive visualization |
