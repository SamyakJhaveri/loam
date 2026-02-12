# Phase 5 E2E Test Report — FINAL

**Completed**: 2026-02-11
**Platform**: RTX 4070 / Ryzen 9 7900X / Ubuntu 22.04

---

## Environment

| Component | Version |
|-----------|---------|
| GPU | NVIDIA GeForce RTX 4070 (sm_89, 12GB, Ada Lovelace) |
| CPU | AMD Ryzen 9 7900X (12c/24t, 4.7GHz base) |
| OS | Ubuntu 22.04 LTS |
| CUDA Toolkit | 12.3 (V12.3.103) |
| Driver | 550.144.03 |
| GCC | 12.4.0 |
| Python | 3.12.3 |
| Make | 4.3 |
| CMake | 3.30.1 |
| APIs available | CUDA ✓, OpenMP ✓, HIP ✗, SYCL ✗ |

---

## Stage Summary

| Stage | Status | Notes |
|-------|--------|-------|
| 1. Environment Verification | ✅ | All tools present, GPU detected |
| 2. Fix Paths | ✅ | No fixes needed — paths already correct |
| 3. Structural Validation | ✅ | Schema + validator fixed; all 20 specs pass |
| 4. Harness Dry Run | ✅ | info ×20, prompt ×2, pairs ×60 all work |
| 5. Build CUDA | ✅ | 5/5 kernels built with `make ARCH=sm_89` |
| 6. Build OpenMP | ✅ | 5/5 kernels built with `make -f Makefile.aomp CC=g++ DEVICE=cpu` |
| 7. Run + Verify | ✅ | 7 PASS, 2 FAIL (expected), 1 HANG (expected) |
| 8. Collect Baselines | ✅ | 3 runs each, metrics averaged, specs updated |
| 9. Full Re-validation | ✅ | Schema: 0 errors, 10 warnings (build artifacts) |
| 10. Final Report | ✅ | This document |

---

## Build Results Matrix

| Kernel | CUDA | OMP | HIP | SYCL |
|--------|------|-----|-----|------|
| nn | ✅ | ✅ | skip | skip |
| scan | ✅ | ✅ | skip | skip |
| particle-diffusion | ✅ | ✅ | skip | skip |
| binomial | ✅ | ✅ | skip | skip |
| radixsort | ✅ | ✅ | skip | skip |

All 10 executables built successfully. HIP/SYCL skipped (toolchains not installed).

---

## Correctness Verification Matrix

| Kernel | CUDA | OMP | HIP | SYCL |
|--------|------|-----|-----|------|
| nn | ✅ PASS | ✅ PASS | skip | skip |
| scan | ✅ PASS | ✅ PASS* | skip | skip |
| particle-diffusion | ✅ PASS | ❌ FAIL | skip | skip |
| binomial | ✅ PASS | ⏳ HANG | skip | skip |
| radixsort | ✅ PASS | 💥 SEGFAULT | skip | skip |

\* scan-omp requires `OMP_NUM_THREADS=1024` environment variable workaround.

### Harness CLI Verification (build → run → verify pipeline)

| Spec | BUILD | RUN | VERIFY | Strategy |
|------|-------|-----|--------|----------|
| nn-cuda | PASS (1.5s) | PASS (0.09s) | PASS | exit_code |
| scan-cuda | PASS (1.7s) | PASS (0.38s) | PASS | stdout_pattern |
| particle-diffusion-cuda | PASS (1.0s) | PASS (0.73s) | PASS | stdout_pattern |
| binomial-cuda | PASS (1.6s) | PASS (1.01s) | PASS | exit_code |
| radixsort-cuda | PASS (1.6s) | PASS (0.11s) | PASS | stdout_pattern |
| nn-omp | PASS (0.4s) | PASS (0.008s) | PASS | exit_code |
| scan-omp | PASS (0.9s) | PASS (6.1s) | PASS | stdout_pattern |
| particle-diffusion-omp | PASS (0.3s) | PASS (0.6s) | **FAIL** | stdout_pattern |
| radixsort-omp | PASS (0.2s) | **FAIL** (1.1s) | **FAIL** | stdout_pattern |
| binomial-omp | — | — | — | skipped (hangs >10min) |

---

## Baseline Performance (3-run averages, correctness config)

| Kernel | API | Wall Time | Key Metric | Unit |
|--------|-----|-----------|------------|------|
| nn | CUDA | 0.075s | kernel_time = 57.31 | μs |
| nn | OMP | 0.008s | kernel_time = 440.00 | μs |
| scan | CUDA | 0.381s | scan_with_bc = 33.45 | μs |
| scan | OMP | 6.108s | scan_with_bc = 51815.06 | μs |
| particle-diffusion | CUDA | 0.727s | kernel_time = 0.000495 | s |
| binomial | CUDA | 1.006s | kernel_time = 770.83 | μs |
| radixsort | CUDA | 0.119s | sort_time = 0.001405 | s |

---

## OMP Failure Analysis

All 4 OMP failures are **inherent GPU→CPU portability defects** in HeCBench source code. None are ParBench build configuration issues.

### 1. scan-omp — RESOLVED with workaround
- **Root cause**: Blelloch scan requires exactly N/2 threads per team (`thread_limit(N/2)`). CPU caps at nproc=24; only elements 0..47 processed.
- **Workaround**: `OMP_NUM_THREADS=1024` added to spec's `environment_variables`
- **Status**: PASS with workaround

### 2. particle-diffusion-omp — FAIL (exit 0)
- **Root cause**: `#pragma omp target data map(alloc:)` is a no-op on CPU fallback — pointer aliases host memory. Kernel modifies particleX/Y in-place; sequential reference `motion_host()` starts from corrupted state.
- **Category**: `benchmark_source_gpu_memory_model`

### 3. radixsort-omp — SEGFAULT (exit 139)
- **Root cause**: Warp-synchronous scan functions (`scanwarp`, `warpScanInclusive`) assume GPU lockstep execution. With ≥2 CPU threads → data race → out-of-bounds writes → SEGFAULT. With 1 thread: no crash but wrong sort result.
- **Category**: `benchmark_source_gpu_assumption`

### 4. binomial-omp — HANG (>10min)
- **Root cause**: Hardcoded 1000 iterations × 1024 options × 2048 timesteps. Each step is a sequential tree traversal on CPU. With no GPU acceleration, total work is ~2 billion operations serially per option.
- **Category**: `benchmark_source_timeout`

---

## Files Modified During Phase 5

| File | Change |
|------|--------|
| `schema/spec_schema.json` | Added "skip" to status enum; null types; skip_reason, fail_reason, fail_category, reproducibility, note properties |
| `scripts/validate_schema.py` | Fixed warning detection bug (line ~577): `startswith("⚠")` → `"⚠ WARNING:" not in e` |
| `specs/hecbench-*-cuda.json` (5) | Reordered verification strategies (stdout_pattern first where applicable); updated baselines with real measurements |
| `specs/hecbench-*-omp.json` (5) | nn-omp: baseline pass. scan-omp: added OMP_NUM_THREADS workaround. 3 others: documented failures with root causes |
| `specs/hecbench-*-{hip,sycl}.json` (10) | Updated timestamps |

---

## Schema Validation Final State

```
✓ All validations passed.
⚠ 10 warning(s): orphan build artifact files (.o, main) in source dirs
```

---

## Translation Pair Coverage

- **5 kernels** × **4 APIs** = **20 specs** → **60 translation pairs**
- Buildable on this platform: 10 (5 CUDA + 5 OMP)
- Passing end-to-end: 7 (5 CUDA + nn-omp + scan-omp with workaround)
- Documented failures: 3 (particle-diffusion-omp, radixsort-omp, binomial-omp)
- Skipped (no toolchain): 10 (all HIP + SYCL)
