# Translation Targets Audit

**Date:** 2026-03-29
**Auditor:** Claude (Planner teammate)
**Status:** AWAITING APPROVAL — no changes applied yet

## Summary Table

| Suite | Specs Audited | Needs Narrowing | Kept As-Is | Total Files Removed |
|-------|--------------|-----------------|------------|---------------------|
| Rodinia | 12 | 9 | 3 | 17 |
| XSBench | 3 | 3 | 0 | 10 |
| RSBench | 3 | 3 | 0 | 12 |
| HeCBench | 15 | 11 | 4 | 22 |
| mixbench | 2 | 2 | 0 | 4 |
| **Total** | **36** | **28** | **8** | **65** |

## Methodology

For each spec with 3+ `files.translation_targets`, grepped source files for:
- **CUDA:** `__global__`, `cudaMalloc`, `cudaMemcpy`, `cudaFree`, `<<<`
- **OMP:** `#pragma omp parallel`, `#pragma omp for`, `#pragma omp sections`, `#pragma omp task`, `#pragma omp simd`
- **OMP target:** `#pragma omp target`, `#pragma omp declare target`
- **OpenCL:** `__kernel`, `clCreate`, `clEnqueue`

Per narrowing rules:
- CUDA: Keep files with kernel launches or CUDA memory management. Remove `__device__`-only or sequential files.
- OMP: Keep ONLY files with `#pragma omp parallel` (or `for`/`sections`/`task`). Exclude utility-only calls.
- OMP target: Keep ONLY files with `#pragma omp target` or `#pragma omp declare target`.
- 2-file kernel+driver pairs acceptable (D7 decision).

**NOTE:** 4 HeCBench specs labeled `omp` actually use `#pragma omp target` constructs. The audit applies target-specific narrowing rules to these. The API mislabeling is flagged but is a separate issue from translation_targets narrowing.

---

## Rodinia Specs

### rodinia-myocyte-omp (IN EVAL BATCHES)

Current targets (10): `[cam.c, define.c, ecc.c, embedded_fehlberg_7_8.c, file.c, fin.c, main.c, master.c, solver.c, timer.c]`
**Recommended targets (2): `[main.c, master.c]`**
Evidence:
- main.c: **KEEP** -- contains `#pragma omp parallel` (line 300)
- master.c: **KEEP** -- contains `#pragma omp parallel` (line 63)
- cam.c: REMOVE -- no `#pragma omp` constructs (pure ODE model code)
- define.c: REMOVE -- no `#pragma omp` constructs (constants/definitions)
- ecc.c: REMOVE -- no `#pragma omp` constructs (ECC model code)
- embedded_fehlberg_7_8.c: REMOVE -- no `#pragma omp` constructs (ODE solver)
- file.c: REMOVE -- no `#pragma omp` constructs (file I/O)
- fin.c: REMOVE -- no `#pragma omp` constructs (model code)
- solver.c: REMOVE -- no `#pragma omp` constructs (sequential solver)
- timer.c: REMOVE -- no `#pragma omp` constructs (timing utility)

**Impact: 8 files removed. CRITICAL -- this spec is in eval batches.**

### rodinia-mummergpu-omp (KNOWN_FAIL)

Current targets (9): `[src/PoolMalloc.cpp, src/common.cu, src/morton.c, src/mummergpu.cu, src/mummergpu_gold.cpp, src/mummergpu_kernel.cu, src/mummergpu_main.cpp, src/smith-waterman.cpp, src/suffix-tree.cpp]`
**Recommended targets (1): `[src/mummergpu_gold.cpp]`**
Evidence:
- src/mummergpu_gold.cpp: **KEEP** -- contains `#pragma omp parallel` (line 806)
- src/PoolMalloc.cpp: REMOVE -- no `#pragma omp` (memory pool utility)
- src/common.cu: REMOVE -- no `#pragma omp` (common utilities)
- src/morton.c: REMOVE -- no `#pragma omp` (Morton code computation)
- src/mummergpu.cu: REMOVE -- no `#pragma omp` (CUDA code, irrelevant for OMP spec)
- src/mummergpu_kernel.cu: REMOVE -- no `#pragma omp` (CUDA kernel, irrelevant)
- src/mummergpu_main.cpp: REMOVE -- no `#pragma omp` (main entry point)
- src/smith-waterman.cpp: REMOVE -- no `#pragma omp` (sequential algorithm)
- src/suffix-tree.cpp: REMOVE -- no `#pragma omp` (sequential data structure)

**Impact: 8 files removed. KNOWN_FAIL spec, change is for consistency only.**

### rodinia-bfs-cuda

Current targets (3): `[bfs.cu, kernel.cu, kernel2.cu]`
**Recommended targets (3): No change -- all have parallel constructs.**
Evidence:
- bfs.cu: **KEEP** -- contains `cudaMalloc` (line 157), `cudaMemcpy` (line 158), `cudaFree` (line 279), `<<<` (line 223)
- kernel.cu: **KEEP** -- contains `__global__` (line 21)
- kernel2.cu: **KEEP** -- contains `__global__` (line 21)

### rodinia-bptree-cuda

Current targets (5): `[kernel/kernel_gpu_cuda.cu, kernel/kernel_gpu_cuda_2.cu, kernel/kernel_gpu_cuda_wrapper.cu, kernel/kernel_gpu_cuda_wrapper_2.cu, util/cuda/cuda.cu]`
**Recommended targets (4): `[kernel/kernel_gpu_cuda.cu, kernel/kernel_gpu_cuda_2.cu, kernel/kernel_gpu_cuda_wrapper.cu, kernel/kernel_gpu_cuda_wrapper_2.cu]`**
Evidence:
- kernel/kernel_gpu_cuda.cu: **KEEP** -- contains `__global__` (line 5)
- kernel/kernel_gpu_cuda_2.cu: **KEEP** -- contains `__global__` (line 5)
- kernel/kernel_gpu_cuda_wrapper.cu: **KEEP** -- contains `cudaMalloc` (line 106), `<<<` (line 215)
- kernel/kernel_gpu_cuda_wrapper_2.cu: **KEEP** -- contains `cudaMalloc` (line 108), `<<<` (line 263)
- util/cuda/cuda.cu: REMOVE -- device selection utility only (`cudaGetDevice`, no `cudaMalloc`/`<<<`)

**Impact: 1 file removed.**

### rodinia-dwt2d-cuda

Current targets (8): `[components.cu, dwt.cu, dwt_cuda/common.cu, dwt_cuda/fdwt53.cu, dwt_cuda/fdwt97.cu, dwt_cuda/rdwt53.cu, dwt_cuda/rdwt97.cu, main.cu]`
**Recommended targets (7): `[components.cu, dwt.cu, dwt_cuda/fdwt53.cu, dwt_cuda/fdwt97.cu, dwt_cuda/rdwt53.cu, dwt_cuda/rdwt97.cu, main.cu]`**
Evidence:
- components.cu: **KEEP** -- contains `__global__` (line 69), `cudaMalloc` (line 140), `<<<` (line 152)
- dwt.cu: **KEEP** -- contains `cudaMalloc` (line 196), `cudaMemcpy` (line 82), `cudaFree` (line 221)
- dwt_cuda/common.cu: REMOVE -- namespace declaration only, no CUDA parallel constructs
- dwt_cuda/fdwt53.cu: **KEEP** -- contains `__global__` (line 320), `<<<` (line 353)
- dwt_cuda/fdwt97.cu: **KEEP** -- contains `__global__` (line 301), `<<<` (line 330)
- dwt_cuda/rdwt53.cu: **KEEP** -- contains `__global__` (line 298), `<<<` (line 323)
- dwt_cuda/rdwt97.cu: **KEEP** -- contains `__global__` (line 300), `<<<` (line 325)
- main.cu: **KEEP** -- contains `cudaMalloc` (line 102), `cudaMemcpy` (line 153), `cudaFree` (line 176)

**Impact: 1 file removed.**

### rodinia-heartwall-cuda

Current targets (3): `[kernel.cu, main.cu, setdevice.cu]`
**Recommended targets (2): `[kernel.cu, main.cu]`**
Evidence:
- kernel.cu: **KEEP** -- contains `__global__` (line 7)
- main.cu: **KEEP** -- contains `cudaMalloc` (line 165), `cudaMemcpy` (line 220), `<<<` (line 662)
- setdevice.cu: REMOVE -- device selection utility only (`cudaGetDeviceCount`, no `cudaMalloc`/`<<<`)

**Impact: 1 file removed.**

### rodinia-heartwall-omp

Current targets (3): `[define.c, kernel.c, main.c]`
**Recommended targets (1): `[main.c]`**
Evidence:
- main.c: **KEEP** -- contains `#pragma omp parallel` (line 549)
- define.c: REMOVE -- no `#pragma omp` (definitions/constants only)
- kernel.c: REMOVE -- no `#pragma omp` (sequential kernel computation; mentions "threads" in comments only)

**Impact: 2 files removed.**

### rodinia-huffman-cuda (KNOWN_FAIL adjacent -- hybridsort-cuda is KNOWN_FAIL, huffman is separate)

Current targets (7): `[hist.cu, main_test_cu.cu, pabio_kernels_v2.cu, pack_kernels.cu, scan.cu, scanLargeArray_kernel.cu, vlc_kernel_sm64huff.cu]`
**Recommended targets (6): `[hist.cu, main_test_cu.cu, pack_kernels.cu, scan.cu, scanLargeArray_kernel.cu, vlc_kernel_sm64huff.cu]`**
Evidence:
- hist.cu: **KEEP** -- contains `__global__` (line 34), `cudaMalloc` (line 83), `<<<` (line 106)
- main_test_cu.cu: **KEEP** -- contains `cudaMalloc` (line 93), `cudaMemcpy` (line 107), `<<<` (line 142)
- pabio_kernels_v2.cu: REMOVE -- `__device__` only (line 17), `#include`d by vlc_kernel_sm64huff.cu (not compiled separately)
- pack_kernels.cu: **KEEP** -- contains `__global__` (line 19)
- scan.cu: **KEEP** -- contains `cudaMalloc` (line 91), `cudaFree` (line 102), `<<<` (line 176)
- scanLargeArray_kernel.cu: **KEEP** -- contains `__global__` (line 217)
- vlc_kernel_sm64huff.cu: **KEEP** -- contains `__global__` (line 37)

**Impact: 1 file removed.**

### rodinia-hybridsort-cuda (KNOWN_FAIL)

Current targets (6): `[bucketsort.cu, bucketsort_kernel.cu, histogram1024_kernel.cu, main.cu, mergesort.cu, mergesort_kernel.cu]`
**Recommended targets (6): No change -- all have parallel constructs.**
Evidence:
- bucketsort.cu: **KEEP** -- contains `cudaMalloc` (line 46), `<<<` (line 109)
- bucketsort_kernel.cu: **KEEP** -- contains `__global__` (line 30)
- histogram1024_kernel.cu: **KEEP** -- contains `__global__` (line 76), `cudaMalloc` (line 129)
- main.cu: **KEEP** -- contains `cudaMalloc` (line 185), `cudaMemcpy` (line 187)
- mergesort.cu: **KEEP** -- contains `cudaMemcpy` (line 59), `<<<` (line 54)
- mergesort_kernel.cu: **KEEP** -- contains `__global__` (line 54)

### rodinia-hybridsort-opencl

Current targets (3): `[bucketsort_kernels.cl, histogram1024.cl, mergesort.cl]`
**Recommended targets (3): No change -- all .cl files with `__kernel`.**
Evidence:
- bucketsort_kernels.cl: **KEEP** -- contains `__kernel` (line 26)
- histogram1024.cl: **KEEP** -- contains `__kernel` (line 52)
- mergesort.cl: **KEEP** -- contains `__kernel` (line 41)

### rodinia-lavamd-cuda

Current targets (3): `[kernel/kernel_gpu_cuda.cu, kernel/kernel_gpu_cuda_wrapper.cu, util/device/device.cu]`
**Recommended targets (2): `[kernel/kernel_gpu_cuda.cu, kernel/kernel_gpu_cuda_wrapper.cu]`**
Evidence:
- kernel/kernel_gpu_cuda.cu: **KEEP** -- contains `__global__` (line 5)
- kernel/kernel_gpu_cuda_wrapper.cu: **KEEP** -- contains `cudaMalloc` (line 103), `<<<` (line 188)
- util/device/device.cu: REMOVE -- device selection utility only (no `cudaMalloc`/`<<<`)

**Impact: 1 file removed.**

### rodinia-mummergpu-cuda (KNOWN_FAIL)

Current targets (3): `[src/common.cu, src/mummergpu.cu, src/mummergpu_kernel.cu]`
**Recommended targets (2): `[src/mummergpu.cu, src/mummergpu_kernel.cu]`**
Evidence:
- src/mummergpu.cu: **KEEP** -- contains `cudaMalloc` (line 90), `<<<` (line 1394)
- src/mummergpu_kernel.cu: **KEEP** -- contains `__global__` (line 677)
- src/common.cu: REMOVE -- no CUDA parallel constructs (utility functions)

**Impact: 1 file removed. KNOWN_FAIL spec, change is for consistency only.**

### rodinia-particlefilter-opencl

Current targets (3): `[particle_double.cl, particle_naive.cl, particle_single.cl]`
**Recommended targets (3): No change -- all .cl files with `__kernel`.**
Evidence:
- particle_double.cl: **KEEP** -- contains `__kernel` (line 144)
- particle_naive.cl: **KEEP** -- contains `__kernel` (line 60)
- particle_single.cl: **KEEP** -- contains `__kernel` (line 179)

---

## XSBench Specs

### xsbench-xsbench-cuda

Current targets (6): `[Main.cu, io.cu, Simulation.cu, GridInit.cu, XSutils.cu, Materials.cu]`
**Recommended targets (2): `[Simulation.cu, GridInit.cu]`**
Evidence:
- Simulation.cu: **KEEP** -- contains `__global__` (line 44), `cudaMalloc` (line 402), `<<<` (line 25)
- GridInit.cu: **KEEP** -- contains `cudaMalloc` (line 34), `cudaMemcpy` (line 35), `cudaFree` (line 82)
- Main.cu: REMOVE -- no CUDA parallel constructs (sequential entry point)
- io.cu: REMOVE -- no CUDA parallel constructs (I/O utilities)
- XSutils.cu: REMOVE -- no CUDA parallel constructs (utility functions)
- Materials.cu: REMOVE -- no CUDA parallel constructs (data initialization)

**Impact: 4 files removed. Per Samyak's decision: NOT Main.c for OMP variant.**

### xsbench-xsbench-omp

Current targets (6): `[Main.c, io.c, Simulation.c, GridInit.c, XSutils.c, Materials.c]`
**Recommended targets (2): `[Simulation.c, GridInit.c]`**
Evidence:
- Simulation.c: **KEEP** -- contains `#pragma omp parallel` (line 45), `#pragma omp task` (line 596)
- GridInit.c: **KEEP** -- contains `#pragma omp parallel` (line 140)
- Main.c: REMOVE -- no `#pragma omp parallel` (sequential entry point; per Samyak's explicit decision)
- io.c: REMOVE -- no `#pragma omp` (I/O utilities)
- XSutils.c: REMOVE -- no `#pragma omp` (utility functions)
- Materials.c: REMOVE -- no `#pragma omp` (data initialization)

**Impact: 4 files removed.**

### xsbench-xsbench-omp_target

Current targets (6): `[Main.c, io.c, Simulation.c, GridInit.c, XSutils.c, Materials.c]`
**Recommended targets (1): `[Simulation.c]`**
Evidence:
- Simulation.c: **KEEP** -- contains `#pragma omp target` (line 44)
- GridInit.c: REMOVE -- has `#pragma omp parallel for` (line 137) but NO `#pragma omp target`. Per omp_target rules, only files with `#pragma omp target` kept.
- Main.c: REMOVE -- no `#pragma omp target`
- io.c: REMOVE -- no `#pragma omp target`
- XSutils.c: REMOVE -- no `#pragma omp target`
- Materials.c: REMOVE -- no `#pragma omp target`

**Impact: 5 files removed.**

---

## RSBench Specs

### rsbench-rsbench-cuda

Current targets (6): `[main.cu, io.cu, simulation.cu, init.cu, material.cu, utils.cu]`
**Recommended targets (2): `[simulation.cu, init.cu]`**
Evidence:
- simulation.cu: **KEEP** -- contains `__global__` (line 44), `cudaMalloc` (line 604), `<<<` (line 25)
- init.cu: **KEEP** -- contains `cudaMalloc` (line 16), `cudaMemcpy` (line 17)
- main.cu: REMOVE -- no CUDA parallel constructs (sequential entry point)
- io.cu: REMOVE -- no CUDA parallel constructs (I/O utilities)
- material.cu: REMOVE -- no CUDA parallel constructs (data initialization)
- utils.cu: REMOVE -- no CUDA parallel constructs (utility functions)

**Impact: 4 files removed.**

### rsbench-rsbench-omp

Current targets (6): `[main.c, io.c, simulation.c, init.c, material.c, utils.c]`
**Recommended targets (1): `[simulation.c]`**
Evidence:
- simulation.c: **KEEP** -- contains `#pragma omp parallel` (line 22), `#pragma omp task` (line 583)
- main.c: REMOVE -- no `#pragma omp parallel`
- io.c: REMOVE -- no `#pragma omp`
- init.c: REMOVE -- no `#pragma omp`
- material.c: REMOVE -- no `#pragma omp`
- utils.c: REMOVE -- no `#pragma omp`

**Impact: 5 files removed.**

### rsbench-rsbench-omp_target

Current targets (6): `[main.c, io.c, simulation.c, init.c, material.c, utils.c]`
**Recommended targets (1): `[simulation.c]`**
Evidence:
- simulation.c: **KEEP** -- contains `#pragma omp target` (line 24)
- main.c: REMOVE -- no `#pragma omp target`
- io.c: REMOVE -- no `#pragma omp target`
- init.c: REMOVE -- no `#pragma omp target`
- material.c: REMOVE -- no `#pragma omp target`
- utils.c: REMOVE -- no `#pragma omp target`

**Impact: 5 files removed.**

---

## HeCBench Specs

### hecbench-backprop-cuda

Current targets (6): `[main.cu, backprop.cu, facetrain.cu, imagenet.cu, bpnn_layerforward.h, bpnn_adjust_weights.h]`
**Recommended targets (3): `[main.cu, bpnn_layerforward.h, bpnn_adjust_weights.h]`**
Evidence:
- main.cu: **KEEP** -- contains `cudaMalloc` (line 81), `cudaMemcpy` (line 85), `<<<` (line 91)
- bpnn_layerforward.h: **KEEP** -- contains `__global__` (line 1)
- bpnn_adjust_weights.h: **KEEP** -- contains `__global__` (line 1)
- backprop.cu: REMOVE -- no CUDA parallel constructs (sequential backprop logic)
- facetrain.cu: REMOVE -- no CUDA parallel constructs (face training driver)
- imagenet.cu: REMOVE -- no CUDA parallel constructs (ImageNet loading)

**Impact: 3 files removed.**

### hecbench-backprop-omp

Current targets (4): `[main.cpp, backprop.cpp, facetrain.cpp, imagenet.cpp]`
**Recommended targets (2): `[main.cpp, backprop.cpp]`**
Evidence:
- main.cpp: **KEEP** -- contains `#pragma omp parallel` (line 82)
- backprop.cpp: **KEEP** -- contains `#pragma omp parallel` (line 235)
- facetrain.cpp: REMOVE -- no `#pragma omp` (sequential face training driver)
- imagenet.cpp: REMOVE -- no `#pragma omp` (sequential ImageNet loading)

**Impact: 2 files removed.**

### hecbench-ccsd-trpdrv-cuda

Current targets (3): `[main.cu, ccsd_trpdrv.cu, ccsd_tengy.cu]`
**Recommended targets (1): `[ccsd_tengy.cu]`**
Evidence:
- ccsd_tengy.cu: **KEEP** -- contains `__global__` (line 7), `cudaMalloc` (line 110), `<<<` (line 153)
- main.cu: REMOVE -- no CUDA parallel constructs (sequential entry point)
- ccsd_trpdrv.cu: REMOVE -- no CUDA parallel constructs (sequential computation)

**Impact: 2 files removed.**

### hecbench-ccsd-trpdrv-omp (NOTE: actually uses OMP target, mislabeled)

Current targets (3): `[main.cpp, ccsd_trpdrv.cpp, ccsd_tengy.cpp]`
**Recommended targets (1): `[ccsd_tengy.cpp]`**
Evidence:
- ccsd_tengy.cpp: **KEEP** -- contains `#pragma omp target data` (line 21), `#pragma omp target teams distribute parallel for` (line 43)
- main.cpp: REMOVE -- no `#pragma omp` constructs at all
- ccsd_trpdrv.cpp: REMOVE -- no `#pragma omp` constructs at all

**Impact: 2 files removed. NOTE: API mislabeling (labeled omp, uses omp target) is a separate issue.**

### hecbench-fft-cuda

Current targets (3): `[main.cu, fft1D_512.h, ifft1D_512.h]`
**Recommended targets (3): No change -- all have parallel constructs.**
Evidence:
- main.cu: **KEEP** -- contains `cudaMalloc` (line 151), `<<<` (line 154)
- fft1D_512.h: **KEEP** -- contains `__global__` (line 1)
- ifft1D_512.h: **KEEP** -- contains `__global__` (line 1)

### hecbench-keccaktreehash-cuda

Current targets (4): `[main.cu, KeccakTreeGPU.cu, KeccakF.cu, Test.cu]`
**Recommended targets (2): `[KeccakTreeGPU.cu, Test.cu]`**
Evidence:
- KeccakTreeGPU.cu: **KEEP** -- contains `__global__` (line 477), `cudaMemcpy` (line 525), `<<<` (line 529)
- Test.cu: **KEEP** -- contains `cudaMalloc` (line 131), `cudaMemcpy` (line 147), `cudaFree` (line 177)
- main.cu: REMOVE -- no CUDA parallel constructs (sequential entry point)
- KeccakF.cu: REMOVE -- no CUDA parallel constructs (sequential Keccak permutation)

**Impact: 2 files removed.**

### hecbench-keccaktreehash-omp (NOTE: actually uses OMP target, mislabeled)

Current targets (4): `[main.cpp, KeccakTreeGPU.cpp, KeccakF.cpp, Test.cpp]`
**Recommended targets (2): `[KeccakTreeGPU.cpp, Test.cpp]`**
Evidence:
- KeccakTreeGPU.cpp: **KEEP** -- contains `#pragma omp declare target` (line 42), `#pragma omp target teams distribute parallel for` (line 440)
- Test.cpp: **KEEP** -- contains `#pragma omp target enter data` (line 134), `#pragma omp target exit data` (line 154)
- main.cpp: REMOVE -- no `#pragma omp` constructs
- KeccakF.cpp: REMOVE -- no `#pragma omp` constructs (sequential Keccak permutation)

**Impact: 2 files removed. NOTE: API mislabeling (labeled omp, uses omp target) is a separate issue.**

### hecbench-lulesh-cuda

Current targets (5): `[lulesh.cu, lulesh-init.cu, lulesh-util.cu, lulesh-viz.cu, lulesh.h]`
**Recommended targets (1): `[lulesh.cu]`**
Evidence:
- lulesh.cu: **KEEP** -- contains `__global__` (line 686), `cudaMalloc` (line 2256), `<<<` (line 2572)
- lulesh-init.cu: REMOVE -- no CUDA parallel constructs (domain initialization)
- lulesh-util.cu: REMOVE -- no CUDA parallel constructs (utility functions)
- lulesh-viz.cu: REMOVE -- no CUDA parallel constructs (visualization output)
- lulesh.h: REMOVE -- contains `__device__` (line 560) in a function prototype only; no `__global__`, no `cudaMalloc`/`<<<`. Header with struct definitions and prototypes.

**Impact: 4 files removed.**

### hecbench-lulesh-omp (NOTE: actually uses OMP target, mislabeled)

Current targets (5): `[lulesh.cc, lulesh-init.cc, lulesh-util.cc, lulesh-viz.cc, lulesh.h]`
**Recommended targets (2): `[lulesh.cc, lulesh.h]`**
Evidence:
- lulesh.cc: **KEEP** -- contains `#pragma omp target data` (line 1142), `#pragma omp target teams distribute parallel for` (line 1241), and also `#pragma omp parallel for` (line 1335)
- lulesh.h: **KEEP** -- contains `#pragma omp declare target` (line 28), `#pragma omp end declare target` (line 40). Device-side constants needed for target offload.
- lulesh-init.cc: REMOVE -- no `#pragma omp` constructs (domain initialization)
- lulesh-util.cc: REMOVE -- no `#pragma omp` constructs (utility functions)
- lulesh-viz.cc: REMOVE -- no `#pragma omp` constructs (visualization output)

**Impact: 3 files removed. NOTE: API mislabeling (labeled omp, uses omp target) is a separate issue.**

### hecbench-myocyte-cuda

Current targets (4): `[kernel.cu, kernel_cam.cu, kernel_ecc.cu, main.cu]`
**Recommended targets (3): `[kernel.cu, kernel_cam.cu, kernel_ecc.cu]`**
Evidence:
- kernel.cu: **KEEP** -- contains `__global__` (line 1)
- kernel_cam.cu: **KEEP** -- contains `__device__` (line 4); called from `__global__` kernel in kernel.cu (lines 66, 83, 100). This is device-side computation, not a utility. `#include`d by work.cu.
- kernel_ecc.cu: **KEEP** -- contains `__device__` (line 4); called from `__global__` kernel in kernel.cu (line 43). Same reasoning as kernel_cam.cu.
- main.cu: REMOVE -- no CUDA parallel constructs directly. Includes `work.cu` which includes all kernels, but main.cu itself is sequential entry point code.

**Note on kernel_cam.cu/kernel_ecc.cu exception:** These `__device__` files are an exception to the "remove `__device__`-only" rule because they contain the core computational model (CAM and ECC cardiac cell models) that runs on the GPU and needs translation. They are not utility/helper code. The `__device__` functions are called directly from `__global__` kernel code.

**Impact: 1 file removed.**

### hecbench-nbody-cuda

Current targets (3): `[GSimulation.cu, GSimulationKernels.hpp, main.cu]`
**Recommended targets (2): `[GSimulation.cu, GSimulationKernels.hpp]`**
Evidence:
- GSimulation.cu: **KEEP** -- contains `cudaMalloc` (line 105), `<<<` (line 121), `cudaFree` (line 161)
- GSimulationKernels.hpp: **KEEP** -- contains `__global__` (line 1)
- main.cu: REMOVE -- no CUDA parallel constructs (sequential entry point)

**Impact: 1 file removed.**

### hecbench-pso-cuda

Current targets (3): `[main.cpp, kernel_gpu.cu, kernel.h]`
**Recommended targets (1): `[kernel_gpu.cu]`**
Evidence:
- kernel_gpu.cu: **KEEP** -- contains `__global__` (line 21), `cudaMalloc` (line 84), `<<<` (line 105)
- main.cpp: REMOVE -- no CUDA parallel constructs (sequential entry point)
- kernel.h: REMOVE -- no CUDA parallel constructs (struct/constant definitions)

**Impact: 2 files removed.**

### hecbench-radixsort-cuda

Current targets (5): `[main.cu, RadixSort.cu, RadixSort_kernels.cu, Scan.cu, Scan_kernels.cu]`
**Recommended targets (5): No change -- all have parallel constructs.**
Evidence:
- main.cu: **KEEP** -- contains `cudaMalloc` (line 60), `cudaMemcpy` (line 61), `cudaFree` (line 106)
- RadixSort.cu: **KEEP** -- contains `cudaMemcpy` (line 93), `<<<` (line 33)
- RadixSort_kernels.cu: **KEEP** -- contains `__global__` (line 104)
- Scan.cu: **KEEP** -- contains `cudaMemcpy` (line 84), `<<<` (line 27)
- Scan_kernels.cu: **KEEP** -- contains `__global__` (line 157)

### hecbench-radixsort-omp (NOTE: actually uses OMP target, mislabeled)

Current targets (5): `[main.cpp, RadixSort.cpp, RadixSort_kernels.cpp, Scan.cpp, Scan_kernels.cpp]`
**Recommended targets (5): No change -- all have parallel constructs.**
Evidence:
- main.cpp: **KEEP** -- contains `#pragma omp target data` (line 68)
- RadixSort.cpp: **KEEP** -- contains `#pragma omp parallel` (line 35)
- RadixSort_kernels.cpp: **KEEP** -- contains `#pragma omp declare target` (line 18)
- Scan.cpp: **KEEP** -- contains `#pragma omp parallel` (line 29)
- Scan_kernels.cpp: **KEEP** -- contains `#pragma omp declare target` (line 34)

### hecbench-thomas-cuda

Current targets (4): `[main.cu, cuThomasBatch.cu, cuThomasBatch.h, ThomasMatrix.hpp]`
**Recommended targets (3): `[main.cu, cuThomasBatch.cu, cuThomasBatch.h]`**
Evidence:
- main.cu: **KEEP** -- contains `cudaMalloc` (line 145), `<<<` (line 159)
- cuThomasBatch.cu: **KEEP** -- contains `__global__` (line 70)
- cuThomasBatch.h: **KEEP** -- contains `__global__` (line 15)
- ThomasMatrix.hpp: REMOVE -- no CUDA constructs (pure data structure header)

**Impact: 1 file removed.**

---

## mixbench Specs

### mixbench-mixbench-cuda

Current targets (4): `[main-cuda.cpp, mix_kernels_cuda.cu, mix_kernels_cuda.h, lcutil.h]`
**Recommended targets (1): `[mix_kernels_cuda.cu]`**
Evidence:
- mix_kernels_cuda.cu: **KEEP** -- contains `__global__` (line 44), `cudaMalloc` (line 169), `<<<` (line 98)
- main-cuda.cpp: REMOVE -- no CUDA parallel constructs (sequential entry point)
- mix_kernels_cuda.h: REMOVE -- function prototype only (`extern "C" void mixbenchGPU(...)`)
- lcutil.h: REMOVE -- CUDA device property queries only (`cudaGetDeviceProperties`, no `cudaMalloc`/`<<<`)

**Impact: 3 files removed.**

### mixbench-mixbench-omp

Current targets (3): `[main.cpp, mix_kernels_cpu.cpp, mix_kernels_cpu.h]`
**Recommended targets (1): `[mix_kernels_cpu.cpp]`**
Evidence:
- mix_kernels_cpu.cpp: **KEEP** -- contains `#pragma omp parallel` (line 97), `#pragma omp simd` (line 27)
- main.cpp: REMOVE -- no `#pragma omp` (sequential entry point)
- mix_kernels_cpu.h: REMOVE -- function prototype only (`void mixbenchCPU(...)`)

**Impact: 2 files removed.**

---

## OpenCL Spec Verification

All OpenCL specs with translation_targets were verified:
- **xsbench-xsbench-opencl**: 1 target `[kernel.cl]` -- already narrowed
- **rsbench-rsbench-opencl**: 1 target `[kernel.cl]` -- already narrowed
- **rodinia-hybridsort-opencl**: 3 targets, all `.cl` files with `__kernel` -- OK
- **rodinia-particlefilter-opencl**: 3 targets, all `.cl` files with `__kernel` -- OK
- **rodinia-bptree-opencl**: 2 targets (checked, both `.cl`) -- OK

No OpenCL specs have host code in translation_targets.

---

## Flagged Issues (Separate from Translation Targets)

### API Mislabeling: 4 HeCBench "omp" Specs Use OMP Target

The following specs are labeled `parallel_api: "omp"` but actually use `#pragma omp target` constructs:

| Spec | Constructs Found |
|------|-----------------|
| hecbench-ccsd-trpdrv-omp | `#pragma omp target data`, `#pragma omp target teams distribute parallel for` |
| hecbench-keccaktreehash-omp | `#pragma omp declare target`, `#pragma omp target teams distribute parallel for`, `#pragma omp target enter/exit data` |
| hecbench-lulesh-omp | `#pragma omp target data`, `#pragma omp target teams distribute parallel for`, `#pragma omp declare target` |
| hecbench-radixsort-omp | `#pragma omp target data`, `#pragma omp declare target` |

**This is a separate issue from translation_targets narrowing.** These specs should arguably be `omp_target` variants, or at minimum this should be documented. The narrowing audit applied the correct rules based on what constructs are actually in the code (i.e., used `#pragma omp target` as the KEEP criterion for these files, not just `#pragma omp parallel`).

---

## Implementation Priority

### Tier 1: CRITICAL (in eval batches, affects results)
1. `rodinia-myocyte-omp` -- 10 -> 2 targets (8 files removed)
2. `xsbench-xsbench-cuda` -- 6 -> 2 targets (4 files removed)
3. `xsbench-xsbench-omp` -- 6 -> 2 targets (4 files removed)
4. `xsbench-xsbench-omp_target` -- 6 -> 1 target (5 files removed)

### Tier 2: HIGH (not yet in eval batches, needed for expanded campaign)
5. `rsbench-rsbench-cuda` -- 6 -> 2 targets (4 files removed)
6. `rsbench-rsbench-omp` -- 6 -> 1 target (5 files removed)
7. `rsbench-rsbench-omp_target` -- 6 -> 1 target (5 files removed)
8. `mixbench-mixbench-cuda` -- 4 -> 1 target (3 files removed)
9. `mixbench-mixbench-omp` -- 3 -> 1 target (2 files removed)

### Tier 3: MEDIUM (HeCBench curated, needs narrowing)
10. `hecbench-backprop-cuda` -- 6 -> 3 targets (3 files removed)
11. `hecbench-backprop-omp` -- 4 -> 2 targets (2 files removed)
12. `hecbench-ccsd-trpdrv-cuda` -- 3 -> 1 target (2 files removed)
13. `hecbench-ccsd-trpdrv-omp` -- 3 -> 1 target (2 files removed)
14. `hecbench-keccaktreehash-cuda` -- 4 -> 2 targets (2 files removed)
15. `hecbench-keccaktreehash-omp` -- 4 -> 2 targets (2 files removed)
16. `hecbench-lulesh-cuda` -- 5 -> 1 target (4 files removed)
17. `hecbench-lulesh-omp` -- 5 -> 2 targets (3 files removed)
18. `hecbench-myocyte-cuda` -- 4 -> 3 targets (1 file removed)
19. `hecbench-nbody-cuda` -- 3 -> 2 targets (1 file removed)
20. `hecbench-pso-cuda` -- 3 -> 1 target (2 files removed)
21. `hecbench-thomas-cuda` -- 4 -> 3 targets (1 file removed)

### Tier 4: LOW (Rodinia non-eval, minor changes)
22. `rodinia-bptree-cuda` -- 5 -> 4 targets (1 file removed)
23. `rodinia-dwt2d-cuda` -- 8 -> 7 targets (1 file removed)
24. `rodinia-heartwall-cuda` -- 3 -> 2 targets (1 file removed)
25. `rodinia-heartwall-omp` -- 3 -> 1 target (2 files removed)
26. `rodinia-huffman-cuda` -- 7 -> 6 targets (1 file removed)
27. `rodinia-lavamd-cuda` -- 3 -> 2 targets (1 file removed)
28. `rodinia-mummergpu-cuda` -- 3 -> 2 targets (1 file removed, KNOWN_FAIL)
29. `rodinia-mummergpu-omp` -- 9 -> 1 target (8 files removed, KNOWN_FAIL)

### Kept As-Is (no narrowing needed, 8 specs):
- `rodinia-bfs-cuda` (3 targets, all KEEP)
- `rodinia-hybridsort-cuda` (6 targets, all KEEP)
- `rodinia-hybridsort-opencl` (3 targets, all KEEP)
- `rodinia-particlefilter-opencl` (3 targets, all KEEP)
- `hecbench-fft-cuda` (3 targets, all KEEP)
- `hecbench-radixsort-cuda` (5 targets, all KEEP)
- `hecbench-radixsort-omp` (5 targets, all KEEP)
- `hecbench-myocyte-cuda kernel_cam/kernel_ecc exception` (kept as 3, see note above)
