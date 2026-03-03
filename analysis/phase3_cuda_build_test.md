# CUDA Build Test Results — Phase 3 (Batch 3)

**Date**: 2026-03-02
**Machine**: RTX 4070, sm_89, CUDA 12.3, nvcc V12.3.103, gcc 12.4.0
**Build command**: `make clean && make ARCH=sm_89` in each `<kernel>-cuda/` directory
**HeCBench path**: `/home/samyak/Desktop/downloads/HeCBench-master/src/`

## Results

| # | Kernel | Build Result | Time (s) | Notes |
|---|--------|:---:|---:|---|
| 1 | pathfinder | PASS | 1 | Clean build |
| 2 | deredundancy | PASS | 2 | Clean build |
| 3 | softmax-online | PASS | 4 | Clean build |
| 4 | backprop | PASS | 2 | Warnings: 17× unused return value from `fscanf`/`fread` (harmless) |
| 5 | rmsnorm | PASS | 0 | Clean build |
| 6 | laplace3d | PASS | 1 | Clean build |
| 7 | tissue | PASS | 1 | Clean build |
| 8 | lulesh | PASS | 3 | Clean build |
| 9 | thomas | PASS | 1 | Clean build |
| 10 | keccaktreehash | PASS | 3 | Clean build |
| 11 | md5hash | PASS | 1 | Clean build |
| 12 | ccsd-trpdrv | PASS | 4 | Clean build |
| 13 | babelstream | PASS | 1 | Clean build |
| 14 | fpc | PASS | 1 | Warnings: 5× unused return value from `posix_memalign` (harmless) |
| 15 | feynman-kac | PASS | 0 | Clean build |
| 16 | maxpool3d | PASS | 1 | Clean build |
| 17 | secp256k1 | PASS | 122 | Clean build; long compile time due to heavy template instantiation |
| 18 | tsp | PASS | 1 | Warnings: 11× unused return value from `fscanf` (harmless) |
| 19 | pso | PASS | 1 | Clean build |
| 20 | ga | PASS | 1 | Clean build |

## Summary

**20/20 CUDA builds passed.** No replacements needed.

### Warning Details

All warnings are standard `-Wunused-result` / `#1650-D` diagnostics from nvcc and gcc. They flag unchecked return values of `fscanf()`, `fread()`, and `posix_memalign()` — these are harmless in benchmark code and do not affect correctness.

| Kernel | Warning Count | Warning Type |
|--------|---:|---|
| backprop | 17 | `#1650-D` result of call is not used (`fscanf`, `fread`) |
| fpc | 5 | `#1650-D` / `-Wunused-result` (`posix_memalign`) |
| tsp | 11 | `#1650-D` / `-Wunused-result` (`fscanf`) |

### Notable Observations

- **secp256k1** takes ~122s to compile due to heavy elliptic-curve template code — this is expected and not a concern.
- All other kernels compile in ≤4s.
- Total batch build time: ~152s (dominated by secp256k1).
- No kernels require swapping with backups.

### Build Environment

```
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 12.3, V12.3.103
gcc (Ubuntu 12.4.0-2ubuntu1~24.04.1) 12.4.0
GPU: NVIDIA GeForce RTX 4070 (sm_89)
```
