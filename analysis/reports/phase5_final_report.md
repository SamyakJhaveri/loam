# Phase 5: Baseline Population & Final Validation Report

**Generated**: 2026-02-13
**Platform**: rtx4070-r9-7900x (NVIDIA RTX 4070 + AMD Ryzen 9 7900X, Ubuntu 22.04)

---

## 1. Summary

| Metric | Count |
|--------|-------|
| Total kernels | 20 |
| Total API variants (specs) | 80 |
| Total directed translation pairs | 240 |
| Specs with `baseline_results` populated | 47 / 80 (58.8%) |
| Specs with `baseline_results: null` | 33 / 80 (41.2%) |

---

## 2. Pass Rates by API

| API | Passed | Failed/Skipped | Pass Rate | Notes |
|-----|--------|----------------|-----------|-------|
| **CUDA** | 20 | 0 | **100%** | All 20 kernels verified on RTX 4070. |
| **SYCL** | 16 | 4 | **80%** | High success rate via DPC++ (likely CUDA backend). Failures: *chacha20, merge, nbody, radixsort*. |
| **OpenMP** | 11 | 9 | **55%** | Mixed results. CPU offload working for simple kernels. Failures: *binomial, conv-sep, dct8x8, fft, fwt, merge, particle-diff, radixsort, simplespmv*. |
| **HIP** | 0 | 20 | **0%** | Expected on NVIDIA hardware without HIP-on-CUDA toolchain configured. |

---

## 3. Domain Distribution

| Domain | Count | Kernels |
|--------|-------|---------|
| Signal Processing | 4 | `convolutionseparable`, `dct8x8`, `fft`, `fwt` |
| Cryptography | 2 | `aes`, `chacha20` |
| Image Processing | 2 | `bilateral`, `sobel` |
| Parallel Primitives | 2 | `scan`, `radixsort` |
| Bioinformatics / Stat. Genetics | 1 | `chi2` |
| Physics Simulation | 1 | `nbody` |
| Computational Finance | 1 | `binomial` |
| Sparse Linear Algebra | 1 | `simplespmv` |
| Parallel Sorting | 1 | `merge` |
| Statistical Physics | 1 | `ising` |
| Nearest Neighbor Search | 1 | `nn` |
| Numerical Linear Algebra | 1 | `eigenvalue` |
| Dense Linear Algebra | 1 | `lud` |
| Monte Carlo Simulation | 1 | `particle-diffusion` |

---

## 4. Specs with `baseline_results: null` (33 specs)

The following 33 specs have `baseline_results: null` because they failed verification on the reference platform:

### HIP (20 specs - All failed)
- All 20 HIP specs failed due to missing `hipcc` or incompatible platform.

### OpenMP (9 specs failed)
- `hecbench-binomial-omp`
- `hecbench-convolutionseparable-omp`
- `hecbench-dct8x8-omp`
- `hecbench-fft-omp`
- `hecbench-fwt-omp`
- `hecbench-merge-omp`
- `hecbench-particle-diffusion-omp`
- `hecbench-radixsort-omp`
- `hecbench-simplespmv-omp`

### SYCL (4 specs failed)
- `hecbench-chacha20-sycl`
- `hecbench-merge-sycl`
- `hecbench-nbody-sycl`
- `hecbench-radixsort-sycl`

---

## 5. Known Issues & Limitations

1. **HIP Support**: The current reference platform (NVIDIA GPU) does not support HIP natively. HIP specs are currently untestable.
2. **OpenMP Offload**: OpenMP target offload support is partial. Some kernels fail to build or verify, likely needing specific compiler flags or environment tuning for the NVIDIA target.
3. **SYCL Verification**: 4 SYCL kernels failed verification. These likely have logic bugs in the port or precision differences.
4. **Baseline Completeness**: Only 59% of the suite has validated performance baselines. This is sufficient for Phase 1 of the paper (Code Translation) as long as we have at least one valid source/target for each pair, but for Performance Analysis, we need to improve the OpenMP/SYCL pass rate.

---

## 6. Deliverables Checklist

- [x] 47 passing specs updated with `baseline_results` from actual runs
- [x] `scripts/populate_baselines.py` — reusable baseline population script
- [x] `results/phase5/*.json` — 47 individual JSON result files
- [x] `results/phase5/*.log` — 47 individual log files
- [x] `results/phase5/all_translation_pairs.txt` — 240 directed translation pairs
- [x] `python scripts/validate_schema.py --all` passes cleanly (80/80 valid, 0 errors)
- [x] `analysis/reports/phase5_final_report.md` — this report

