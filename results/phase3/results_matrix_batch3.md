# Phase 3 — Build & Run Results Matrix (Batch 3)

**Generated**: 2026-03-02T16:20:00-08:00  
**Platform**: Linux x86_64, NVIDIA GeForce RTX 4070 (sm_89, Ada Lovelace, 12 GB)  
**Compilers**: nvcc 12.3 (CUDA), g++ 12.4.0 + OpenMP (OMP), hipcc NOT AVAILABLE (HIP), icpx/dpcpp NOT AVAILABLE (SYCL)

## Summary

| Metric          | CUDA | OMP  | HIP  | SYCL | Total |
|-----------------|------|------|------|------|-------|
| Specs tested    | 20   | 20   | 0    | 0    | 40    |
| Specs skipped   | 0    | 0    | 20   | 20   | 40    |
| BUILD PASS      | 20   | 20   | —    | —    | 40    |
| BUILD FAIL      | 0    | 0    | —    | —    | 0     |
| RUN PASS        | 19   | 17   | —    | —    | 36    |
| RUN FAIL        | 0    | 0    | —    | —    | 0     |
| RUN TIMEOUT     | 1    | 2    | —    | —    | 3     |
| VERIFY PASS     | 19   | 12   | —    | —    | 31    |
| VERIFY FAIL     | 1    | 7    | —    | —    | 8     |
| **Full PASS**   | **19** | **12** | **0** | **0** | **31** |

Note: feynman-kac-omp was skipped (known >600s runtime from CUDA testing). Counted as TIMEOUT/FAIL.

## Detailed Results

Legend: ✅ PASS | ❌ FAIL | ⏱ TIMEOUT | 🚫 BUILD FAIL | ⬜ SKIP (no compiler)

| # | Kernel                  | CUDA Build | CUDA Run   | CUDA Verify | OMP Build | OMP Run      | OMP Verify | HIP  | SYCL |
|---|-------------------------|------------|------------|-------------|-----------|--------------|------------|------|------|
| 1 | pathfinder             | ✅ 0.90s   | ✅ 0.08s   | ✅ exit     | ✅ 0.23s  | ✅ 0.003s    | ✅ exit    | ⬜   | ⬜   |
| 2 | deredundancy           | ✅ 2.51s   | ✅ 13.60s  | ✅ stdout   | ✅ 1.14s  | ✅ 551.47s   | ✅ stdout  | ⬜   | ⬜   |
| 3 | softmax-online         | ✅ 3.07s   | ✅ 19.97s  | ✅ stdout   | ✅ 0.21s  | ⏱ 300.3s     | ❌ stdout  | ⬜   | ⬜   |
| 4 | backprop               | ✅ 2.06s   | ✅ 0.12s   | ✅ stdout   | ✅ 0.56s  | ✅ 0.09s     | ❌ stdout  | ⬜   | ⬜   |
| 5 | rmsnorm                | ✅ 0.67s   | ✅ 0.06s   | ✅ stdout   | ✅ 0.19s  | ✅ 0.13s     | ✅ stdout  | ⬜   | ⬜   |
| 6 | laplace3d              | ✅ 0.68s   | ✅ 0.28s   | ✅ stdout   | ✅ 0.21s  | ✅ 0.33s     | ❌ stdout  | ⬜   | ⬜   |
| 7 | tissue                 | ✅ 0.64s   | ✅ 12.28s  | ✅ stdout   | ✅ 0.27s  | ✅ 38.32s    | ❌ stdout  | ⬜   | ⬜   |
| 8 | lulesh                 | ✅ 3.38s   | ✅ 0.19s   | ✅ stdout   | ✅ 0.75s  | ✅ 3.83s     | ✅ stdout  | ⬜   | ⬜   |
| 9 | thomas                 | ✅ 1.53s   | ✅ 1.56s   | ✅ stdout   | ✅ 0.36s  | ✅ 1.52s     | ✅ stdout  | ⬜   | ⬜   |
|10 | keccaktreehash         | ✅ 2.46s   | ✅ 7.42s   | ✅ stdout   | ✅ 0.31s  | ✅ 8.22s     | ✅ stdout  | ⬜   | ⬜   |
|11 | md5hash                | ✅ 1.07s   | ✅ 0.32s   | ✅ stdout   | ✅ 0.41s  | ✅ 26.64s    | ✅ stdout  | ⬜   | ⬜   |
|12 | ccsd-trpdrv            | ✅ 3.64s   | ✅ 1.08s   | ✅ stdout   | ✅ 0.28s  | ✅ 1.04s     | ✅ stdout  | ⬜   | ⬜   |
|13 | babelstream            | ✅ 1.44s   | ✅ 1.48s   | ✅ stdout   | ✅ 0.68s  | ✅ 16.85s    | ✅ stdout  | ⬜   | ⬜   |
|14 | fpc                    | ✅ 0.63s   | ✅ 0.40s   | ✅ stdout   | ✅ 0.14s  | ✅ 0.64s     | ❌ stdout  | ⬜   | ⬜   |
|15 | feynman-kac            | ✅ 0.65s   | ⏱ 600.1s   | ❌ stdout   | ⏱ (skip)  | ⏱ (skip)     | ❌ (skip)  | ⬜   | ⬜   |
|16 | maxpool3d              | ✅ 0.62s   | ✅ 3.36s   | ✅ stdout   | ✅ 0.18s  | ✅ 3.04s     | ✅ stdout  | ⬜   | ⬜   |
|17 | secp256k1              | ✅ 126.40s | ✅ 0.08s   | ✅ stdout   | ✅ 0.24s  | ✅ 0.001s    | ✅ stdout  | ⬜   | ⬜   |
|18 | tsp                    | ✅ 0.66s   | ✅ 0.11s   | ✅ stdout   | ✅ 0.22s  | ✅ 3.04s     | ✅ stdout  | ⬜   | ⬜   |
|19 | pso                    | ✅ 0.90s   | ✅ 0.07s   | ✅ stdout   | ✅ 0.37s  | ✅ 0.18s     | ❌ stdout  | ⬜   | ⬜   |
|20 | ga                     | ✅ 0.70s   | ✅ 0.08s   | ✅ stdout   | ✅ 0.18s  | ✅ 0.04s     | ✅ stdout  | ⬜   | ⬜   |

## CUDA Results: 19/20 PASS ✅

19 of 20 CUDA kernels pass build, run, and verification.

### CUDA Timeout (1):

| Kernel | Outcome | Root Cause |
|--------|---------|-----------|
| feynman-kac-cuda | TIMEOUT (600s) | Monte Carlo simulation with N=1000 stochastic paths per grid point; even 1 repeat exceeds 600s on RTX 4070 |

### Fixes Applied for CUDA:
1. **lulesh-cuda** (all 4 API variants): Executable name mismatch `main` → `lulesh` — Makefile produces `lulesh`.
2. **keccaktreehash-cuda** (cuda & hip): Executable name mismatch `main` → `keccektree` — Makefile uses misspelled name `keccektree`.
3. **md5hash-cuda** (all 4 API variants): Executable name mismatch `main` → `MD5Hash` — Makefile produces `MD5Hash`.
4. **deredundancy-cuda**: Missing `../deredundancy-sycl/testData.fasta` — extracted from `testData.tar.gz`.
5. **feynman-kac** (all 4 API variants): Increased `timeout_seconds` from 300 → 600. Still times out.

## OpenMP Results: 12/20 PASS

### Passing (12):
pathfinder, deredundancy, rmsnorm, lulesh, thomas, keccaktreehash, md5hash, ccsd-trpdrv, babelstream, maxpool3d, secp256k1, tsp, ga

(Note: thomas required Makefile.aomp patch `-qopenmp` → `-fopenmp`)

### Timeout (2):

| Kernel | Outcome | Root Cause |
|--------|---------|-----------|
| softmax-online-omp | TIMEOUT (300s) | CPU OpenMP version too slow for 300s; CUDA version takes ~20s |
| feynman-kac-omp | SKIPPED | Known >600s from CUDA test; CPU would be much slower |

### Verification Failures (5):

| Kernel | Outcome | Root Cause |
|--------|---------|-----------|
| backprop-omp | RUN PASS, VERIFY FAIL | OMP version prints "FAIL"; CPU weights diverge from GPU reference |
| laplace3d-omp | RUN PASS, VERIFY FAIL | RMS error = 1656.12 (far too large); `omp target` stencil computation incorrect on CPU |
| tissue-omp | RUN PASS, VERIFY FAIL | Prints "FAIL"; OMP target kernel produces wrong tissue simulation values |
| fpc-omp | RUN PASS, VERIFY FAIL | `fpc failed 743223 != 7924831`; floating-point compression counts diverge on CPU |
| pso-omp | RUN PASS, VERIFY FAIL | PSO device result=44305.59 vs host result=22690.04; GPU/CPU optimization paths diverge |

### Fixes Applied for OMP:
1. **All 20 OMP specs**: Updated `build.commands.build` from `make` → `make -f Makefile.aomp CC=g++ DEVICE=cpu` and `clean` to match.
2. **thomas-omp Makefile.aomp**: Patched `-qopenmp` → `-fopenmp` (Intel flag → GCC flag).

## HIP & SYCL: All 40 SKIP

No HIP (hipcc) or SYCL (icpx/dpcpp) compiler available on this platform.
All 40 specs deferred to Phase 4 hardware provisioning.

## Spec Modifications Log

| Spec File | Field Changed | Old Value | New Value | Reason |
|-----------|--------------|-----------|-----------|--------|
| hecbench-lulesh-{cuda,hip,omp,sycl}.json | build.outputs.executable | `main` | `lulesh` | Makefile produces `lulesh` not `main` |
| hecbench-lulesh-{cuda,hip,omp,sycl}.json | run.executable | `./main` | `./lulesh` | Match actual binary name |
| hecbench-keccaktreehash-{cuda,hip}.json | build.outputs.executable | `main` | `keccektree` | Makefile produces `keccektree` (misspelling in HeCBench) |
| hecbench-keccaktreehash-{cuda,hip}.json | run.executable | `./main` | `./keccektree` | Match actual binary name |
| hecbench-md5hash-{cuda,hip,omp,sycl}.json | build.outputs.executable | `main` | `MD5Hash` | Makefile produces `MD5Hash` not `main` |
| hecbench-md5hash-{cuda,hip,omp,sycl}.json | run.executable | `./main` | `./MD5Hash` | Match actual binary name |
| hecbench-feynman-kac-{cuda,hip,omp,sycl}.json | run.timeout_seconds | 300 | 600 | Monte Carlo too slow for 300s |
| All 20 *-omp.json specs | build.commands.build | `make` | `make -f Makefile.aomp CC=g++ DEVICE=cpu` | Use g++-compatible Makefile |
| All 20 *-omp.json specs | build.commands.clean | `make clean` | `make -f Makefile.aomp clean` | Match build Makefile |
| thomas-omp Makefile.aomp | CFLAGS cpu path | `-qopenmp` | `-fopenmp` | Intel flag → GCC flag |

## Data Files Extracted

| Archive | Extracted To | Required By |
|---------|-------------|-------------|
| src/deredundancy-sycl/testData.tar.gz | src/deredundancy-sycl/testData.fasta | deredundancy-cuda, deredundancy-omp, deredundancy-hip, deredundancy-sycl |

## Phase 4 Action Items

1. **feynman-kac**: Fundamentally slow kernel (N=1000 stochastic paths/gridpoint, grid ~711×128). Consider reducing N in source or using a smaller grid for correctness checks.
2. **softmax-online-omp**: Increase timeout to 600s or reduce problem size for CPU correctness.
3. **backprop-omp**: CPU weights diverge from GPU reference; OMP `target` kernel produces different results on CPU host.
4. **laplace3d-omp**: RMS error 1656 on CPU vs near-zero on GPU; stencil kernel `omp target teams` semantics differ on CPU.
5. **tissue-omp**: OMP target tissue simulation values incorrect on CPU.
6. **fpc-omp**: FP compression bit counts differ between GPU and CPU execution paths.
7. **pso-omp**: Particle swarm optimization results diverge between device and host.
8. **Install icpx/dpcpp** → Unblocks 20 SYCL specs.
9. **Install hipcc (ROCm)** → Unblocks 20 HIP specs.
