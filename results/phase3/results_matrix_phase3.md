# Phase 3 — Build & Run Results Matrix (All 60 Kernels)

**Generated**: 2026-03-03T11:25:50
**Platform**: Linux x86_64, NVIDIA GeForce RTX 4070 (sm_89, Ada Lovelace, 12 GB)
**Compilers**: nvcc 12.3 (CUDA), g++ 12.4.0 + OpenMP (OMP)

## Summary

| Metric | CUDA | OMP | Total |
|--------|------|-----|-------|
| Specs | 60 | 60 | 120 |
| BUILD PASS | 60 | 57 | 117 |
| BUILD FAIL | 0 | 2 | 2 |
| SKIP | 0 | 1 | 1 |
| VERIFY PASS | 60 | 41 | 101 |
| VERIFY FAIL | 0 | 9 | 9 |
| RUN FAIL/TIMEOUT | 0 | 7 | 7 |
| **Full PASS** | **60** | **41** | **101** |

## Detailed Results

Legend: ✅ PASS | ❌ FAIL | ⏱ TIMEOUT | 🚫 BUILD FAIL | ⬜ SKIP

| # | Kernel | Batch | CUDA Build | CUDA Run | CUDA Verify | OMP Build | OMP Run | OMP Verify |
|---|--------|-------|------------|----------|-------------|-----------|---------|------------|
| 1 | aes | B1 | ✅ 1.29s | ✅ 0.07s | ✅ stdout | ✅ 0.61s | ✅ 1.93s | ✅ stdout |
| 2 | babelstream | B2 | ✅ 1.50s | ✅ 1.49s | ✅ stdout_pattern | ✅ 0.74s | ✅ 16.6s | ✅ stdout_pattern |
| 3 | backprop | B2 | ✅ 2.04s | ✅ 0.09s | ✅ stdout_pattern | ✅ 0.55s | ✅ 0.09s | ❌ stdout_pattern |
| 4 | bezier-surface | B3 | ✅ 1.01s | ✅ 0.08s | ✅ stdout_pattern | ✅ 0.32s | ✅ 0.01s | ✅ stdout_pattern |
| 5 | bilateral | B1 | ✅ 1.74s | ✅ 0.14s | ✅ stdout | ✅ 0.25s | ✅ 2.35s | ✅ stdout |
| 6 | binomial | B1 | ✅ 2.58s | ✅ 0.11s | ✅ stdout | ✅ 0.36s | ⏱ 600.1s | ❌ exit |
| 7 | ccsd-trpdrv | B2 | ✅ 3.66s | ✅ 1.07s | ✅ stdout_pattern | ✅ 0.28s | ✅ 0.99s | ✅ stdout_pattern |
| 8 | chacha20 | B1 | ✅ 1.38s | ✅ 0.02s | ✅ stdout | ✅ 0.16s | ✅ 0.001s | ✅ stdout |
| 9 | chi2 | B1 | ✅ 1.13s | ✅ 12.99s | ✅ stdout | ✅ 0.35s | ✅ 13.66s | ✅ stdout |
| 10 | convolution3d | B3 | ✅ 0.96s | ✅ 0.09s | ✅ stdout_pattern | ⬜ no dir | — | — |
| 11 | convolutionseparable | B1 | ✅ 2.16s | ✅ 0.04s | ✅ stdout | 🚫 | — | — |
| 12 | crc64 | B3 | ✅ 1.43s | ✅ 0.26s | ✅ stdout_pattern | ✅ 0.32s | ✅ 0.20s | ✅ stdout_pattern |
| 13 | dct8x8 | B1 | ✅ 2.27s | ✅ 0.07s | ✅ stdout | ✅ 0.33s | ❌ segfault | ❌ exit |
| 14 | deredundancy | B2 | ✅ 2.53s | ✅ 13.6s | ✅ stdout_pattern | ✅ 1.12s | ✅ 547.9s | ✅ stdout_pattern |
| 15 | eigenvalue | B1 | ✅ 2.30s | ✅ 0.42s | ✅ stdout | ✅ 0.44s | ✅ 0.35s | ✅ stdout |
| 16 | feynman-kac | B2 | ✅ 0.65s | ✅ 195.0s | ✅ stdout_pattern | ✅ 0.18s | ✅ 15.7s | ✅ stdout_pattern |
| 17 | fft | B1 | ✅ 1.73s | ✅ 0.08s | ✅ stdout | ✅ 0.46s | ✅ 2.17s | ❌ stdout |
| 18 | floydwarshall | B3 | ✅ 0.61s | ✅ 0.74s | ✅ stdout_pattern | ✅ 0.12s | ✅ 1.30s | ✅ stdout_pattern |
| 19 | fpc | B2 | ✅ 0.64s | ✅ 0.41s | ✅ stdout_pattern | ✅ 0.14s | ✅ 0.64s | ❌ stdout_pattern |
| 20 | fwt | B1 | ✅ 2.21s | ✅ 0.07s | ✅ stdout | ✅ 0.23s | ✅ 1.14s | ❌ stdout |
| 21 | ga | B2 | ✅ 0.70s | ✅ 0.09s | ✅ stdout_pattern | ✅ 0.18s | ✅ 0.03s | ✅ stdout_pattern |
| 22 | gaussian | B3 | ✅ 1.42s | ✅ 0.08s | ✅ stdout_pattern | ✅ 0.39s | ✅ 0.40s | ✅ stdout_pattern |
| 23 | geglu | B3 | ✅ 1.07s | ✅ 18.7s | ✅ stdout_pattern | ✅ 0.28s | ✅ 19.9s | ✅ stdout_pattern |
| 24 | heat2d | B3 | ✅ 0.56s | ✅ 0.23s | ✅ stdout_pattern | ✅ 0.17s | ✅ 0.28s | ✅ stdout_pattern |
| 25 | ising | B1 | ✅ 2.09s | ✅ 0.05s | ✅ stdout | ✅ 0.35s | ✅ 0.19s | ✅ stdout |
| 26 | iso2dfd | B3 | ✅ 1.02s | ✅ 0.14s | ✅ stdout_pattern | ✅ 0.35s | ✅ 0.08s | ✅ stdout_pattern |
| 27 | jenkins-hash | B3 | ✅ 0.62s | ✅ 0.76s | ✅ stdout_pattern | ✅ 0.12s | ✅ 0.65s | ✅ stdout_pattern |
| 28 | keccaktreehash | B2 | ✅ 2.46s | ✅ 7.42s | ✅ stdout_pattern | ✅ 0.30s | ✅ 8.14s | ✅ stdout_pattern |
| 29 | knn | B3 | ✅ 0.62s | ✅ 7.28s | ✅ stdout_pattern | ✅ 0.19s | ✅ 8.26s | ❌ stdout_pattern |
| 30 | laplace3d | B2 | ✅ 0.68s | ✅ 0.28s | ✅ stdout_pattern | ✅ 0.20s | ✅ 0.39s | ❌ stdout_pattern |
| 31 | lud | B1 | ✅ 2.07s | ✅ 0.08s | ✅ exit | ✅ 0.37s | ✅ 0.06s | ✅ exit |
| 32 | lulesh | B2 | ✅ 3.31s | ✅ 0.18s | ✅ stdout_pattern | ✅ 0.74s | ✅ 3.77s | ✅ stdout_pattern |
| 33 | mandelbrot | B3 | ✅ 0.99s | ✅ 0.23s | ✅ stdout_pattern | ✅ 0.27s | ✅ 0.20s | ✅ stdout_pattern |
| 34 | maxpool3d | B2 | ✅ 0.61s | ✅ 3.25s | ✅ stdout_pattern | ✅ 0.17s | ✅ 2.96s | ✅ stdout_pattern |
| 35 | md5hash | B2 | ✅ 1.08s | ✅ 0.36s | ✅ stdout_pattern | ✅ 0.40s | ✅ 26.6s | ✅ stdout_pattern |
| 36 | merge | B1 | ✅ 2.31s | ✅ 3.20s | ✅ stdout | ✅ 0.90s | ⏱ 300.1s | ❌ stdout |
| 37 | mis | B3 | ✅ 0.65s | ✅ 0.07s | ✅ exit_code | ✅ 0.13s | ❌ exit=255 | ❌ fail |
| 38 | murmurhash3 | B3 | ✅ 0.63s | ✅ 0.57s | ✅ stdout_pattern | ✅ 0.13s | ✅ 0.49s | ✅ stdout_pattern |
| 39 | myocyte | B3 | ✅ 1.08s | ✅ 0.09s | ✅ exit_code | ✅ 0.40s | ✅ 0.001s | ✅ exit_code |
| 40 | nbody | B1 | ✅ 2.37s | ✅ 0.31s | ✅ stdout | ✅ 0.74s | ✅ 6.78s | ✅ stdout |
| 41 | nn | B1 | ✅ 1.48s | ✅ 0.08s | ✅ exit | ✅ 0.40s | ✅ 0.008s | ✅ exit |
| 42 | nw | B3 | ✅ 0.80s | ✅ 1.96s | ✅ stdout_pattern | ✅ 0.27s | ✅ 35.6s | ✅ stdout_pattern |
| 43 | particle-diffusion | B1 | ✅ 2.34s | ✅ 0.21s | ✅ stdout | ✅ 0.36s | ✅ 0.64s | ❌ stdout |
| 44 | pathfinder | B2 | ✅ 0.83s | ✅ 0.07s | ✅ exit_code | ✅ 0.22s | ✅ 0.003s | ✅ exit_code |
| 45 | perplexity | B3 | ✅ 0.72s | ✅ 0.24s | ✅ stdout_pattern | ✅ 0.22s | ✅ 0.18s | ✅ stdout_pattern |
| 46 | popcount | B3 | ✅ 0.65s | ✅ 1.93s | ✅ exit_code | ✅ 0.17s | ✅ 1.81s | ✅ exit_code |
| 47 | pso | B2 | ✅ 0.90s | ✅ 0.07s | ✅ stdout_pattern | ✅ 0.35s | ✅ 0.15s | ❌ stdout_pattern |
| 48 | radixsort | B1 | ✅ 2.62s | ✅ 0.05s | ✅ stdout | ✅ 0.24s | ❌ segfault | ❌ stdout |
| 49 | rmsnorm | B2 | ✅ 0.67s | ✅ 0.06s | ✅ stdout_pattern | ✅ 0.19s | ✅ 0.13s | ✅ stdout_pattern |
| 50 | scan | B1 | ✅ 2.51s | ✅ 0.56s | ✅ stdout | ✅ 0.89s | ✅ 6.07s | ✅ stdout |
| 51 | secp256k1 | B2 | ✅ 126.2s | ✅ 0.08s | ✅ stdout_pattern | ✅ 0.23s | ✅ 0.001s | ✅ stdout_pattern |
| 52 | simplespmv | B1 | ✅ 3.75s | ✅ 0.12s | ✅ stdout | 🚫 | — | — |
| 53 | sobel | B1 | ✅ 1.45s | ✅ 0.08s | ✅ stdout | ✅ 0.52s | ✅ 0.01s | ✅ stdout |
| 54 | sobol | B3 | ✅ 2.79s | ✅ 5.41s | ✅ stdout_pattern | ✅ 0.59s | ❌ segfault | ❌ fail |
| 55 | softmax-online | B2 | ✅ 3.12s | ✅ 19.1s | ✅ stdout_pattern | ✅ 0.21s | ⏱ 300.3s | ❌ fail |
| 56 | stencil1d | B3 | ✅ 0.60s | ✅ 0.62s | ✅ stdout_pattern | ✅ 0.14s | ✅ 4.97s | ✅ stdout_pattern |
| 57 | thomas | B2 | ✅ 1.55s | ✅ 1.54s | ✅ stdout_pattern | ✅ 0.33s | ✅ 1.51s | ✅ stdout_pattern |
| 58 | tissue | B2 | ✅ 0.64s | ✅ 12.3s | ✅ stdout_pattern | ✅ 0.27s | ✅ 37.2s | ❌ stdout_pattern |
| 59 | triad | B3 | ✅ 2.55s | ✅ 0.18s | ✅ stdout_pattern | ✅ 1.84s | ✅ 0.36s | ✅ stdout_pattern |
| 60 | tsp | B2 | ✅ 0.66s | ✅ 0.10s | ✅ stdout_pattern | ✅ 0.23s | ✅ 2.86s | ✅ stdout_pattern |

## Notes

### Batch Definitions
- **B1** (20 kernels): Original Phase 3 selection
- **B2** (20 kernels): Second batch
- **B3** (20 kernels): Third batch

### CUDA: 60/60 PASS ✅
All 60 CUDA kernels pass build, run, and verification.

### OMP: 41/60 PASS
- 41 full pass, 9 verify fail, 7 run fail/timeout, 2 build fail, 1 skip
