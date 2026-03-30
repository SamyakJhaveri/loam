# translation_targets Narrowing Change Log

**Date:** 2026-03-29
**Basis:** `docs/plans/translation_targets_audit.md`
**Invariant:** Every entry in new `translation_targets` verified present in `prompt_payload`.

## Summary

29 spec files narrowed. Total files removed from translation_targets across all specs: 59.

## Change Details

| # | Spec | Before (count) | After (count) | Files Removed |
|---|------|-----------------|---------------|---------------|
| 1 | rodinia-myocyte-omp | 10 | 2 | cam.c, define.c, ecc.c, embedded_fehlberg_7_8.c, file.c, fin.c, solver.c, timer.c |
| 2 | xsbench-xsbench-cuda | 6 | 2 | Main.cu, io.cu, XSutils.cu, Materials.cu |
| 3 | xsbench-xsbench-omp | 6 | 2 | Main.c, io.c, XSutils.c, Materials.c |
| 4 | xsbench-xsbench-omp_target | 6 | 1 | Main.c, io.c, GridInit.c, XSutils.c, Materials.c |
| 5 | rsbench-rsbench-cuda | 6 | 2 | main.cu, io.cu, material.cu, utils.cu |
| 6 | rsbench-rsbench-omp | 6 | 1 | main.c, io.c, init.c, material.c, utils.c |
| 7 | rsbench-rsbench-omp_target | 6 | 1 | main.c, io.c, init.c, material.c, utils.c |
| 8 | mixbench-mixbench-cuda | 4 | 1 | main-cuda.cpp, mix_kernels_cuda.h, lcutil.h |
| 9 | mixbench-mixbench-omp | 3 | 1 | main.cpp, mix_kernels_cpu.h |
| 10 | hecbench-backprop-cuda | 6 | 3 | backprop.cu, facetrain.cu, imagenet.cu |
| 11 | hecbench-backprop-omp | 4 | 2 | facetrain.cpp, imagenet.cpp |
| 12 | hecbench-ccsd-trpdrv-cuda | 3 | 1 | main.cu, ccsd_trpdrv.cu |
| 13 | hecbench-ccsd-trpdrv-omp | 3 | 1 | main.cpp, ccsd_trpdrv.cpp |
| 14 | hecbench-keccaktreehash-cuda | 4 | 2 | main.cu, KeccakF.cu |
| 15 | hecbench-keccaktreehash-omp | 4 | 2 | main.cpp, KeccakF.cpp |
| 16 | hecbench-lulesh-cuda | 5 | 1 | lulesh-init.cu, lulesh-util.cu, lulesh-viz.cu, lulesh.h |
| 17 | hecbench-lulesh-omp | 5 | 2 | lulesh-init.cc, lulesh-util.cc, lulesh-viz.cc |
| 18 | hecbench-myocyte-cuda | 4 | 3 | main.cu |
| 19 | hecbench-nbody-cuda | 3 | 2 | main.cu |
| 20 | hecbench-pso-cuda | 3 | 1 | main.cpp, kernel.h |
| 21 | hecbench-thomas-cuda | 4 | 3 | ThomasMatrix.hpp |
| 22 | rodinia-bptree-cuda | 5 | 4 | util/cuda/cuda.cu |
| 23 | rodinia-dwt2d-cuda | 8 | 7 | dwt_cuda/common.cu |
| 24 | rodinia-heartwall-cuda | 3 | 2 | setdevice.cu |
| 25 | rodinia-heartwall-omp | 3 | 1 | define.c, kernel.c |
| 26 | rodinia-huffman-cuda | 7 | 6 | pabio_kernels_v2.cu |
| 27 | rodinia-lavamd-cuda | 3 | 2 | util/device/device.cu |
| 28 | rodinia-mummergpu-cuda | 3 | 2 | src/common.cu |
| 29 | rodinia-mummergpu-omp | 9 | 1 | src/PoolMalloc.cpp, src/common.cu, src/morton.c, src/mummergpu.cu, src/mummergpu_kernel.cu, src/mummergpu_main.cpp, src/smith-waterman.cpp, src/suffix-tree.cpp |

## Validation

- Schema validation: 15 pre-existing errors (5 phantom specs x 3), 0 new errors
- Invariant check: All `translation_targets` entries are subsets of `prompt_payload` -- VERIFIED
- No other spec fields modified (prompt_payload, run args, build commands untouched)
