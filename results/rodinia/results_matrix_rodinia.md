# Rodinia Full Batch — Results Matrix

**Generated**: 2026-03-06T12:14:47
**Platform**: Linux x86_64, NVIDIA GeForce RTX 4070 (sm_89), AMD Ryzen 9 7900X
**Total specs**: 60 (22 kernels × CUDA/OMP/OpenCL, some kernels not in all APIs)

Legend: ✅ PASS | ❌ FAIL | ⏱ TIMEOUT | ⚠ ERROR | ❓ UNKNOWN | — not applicable

| # | Kernel | CUDA Build | CUDA Run | CUDA Verify | OMP Build | OMP Run | OMP Verify | OCL Build | OCL Run | OCL Verify |
|---|--------|-----------|----------|-------------|-----------|---------|------------|-----------|---------|------------|
| 1 | `backprop` | ✅ 0.7s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code | ✅ 0.6s | ✅ 0.0s | ✅ exit_code |
| 2 | `bfs` | ✅ 0.5s | ✅ 0.5s | ✅ exit_code | ✅ 0.1s | ✅ 0.0s | ✅ exit_code | ✅ 0.7s | ✅ 0.5s | ✅ exit_code |
| 3 | `bptree` | ✅ 1.8s | ✅ 0.4s | ✅ exit_code | ✅ 0.4s | ✅ 0.5s | ✅ exit_code | ✅ 0.5s | ✅ 0.5s | ✅ exit_code |
| 4 | `cfd` | ❌ 0.0s | ❓ 0.0s | ❌ exit_code | ✅ 0.4s | ✅ 4.1s | ✅ exit_code | ❌ 0.0s | ❓ 0.0s | ❌ exit_code |
| 5 | `dwt2d` | ✅ 6.3s | ✅ 0.1s | ✅ exit_code | — | — | — | ✅ 0.3s | ✅ 0.1s | ✅ exit_code |
| 6 | `gaussian` | ✅ 0.5s | ✅ 0.1s | ✅ exit_code | — | — | — | ✅ 0.7s | ✅ 0.1s | ✅ exit_code |
| 7 | `heartwall` | ✅ 1.0s | ✅ 0.3s | ✅ exit_code | ✅ 0.3s | ✅ 2.5s | ✅ exit_code | ✅ 0.5s | ✅ 0.0s | ✅ exit_code |
| 8 | `hotspot` | ✅ 0.5s | ✅ 0.1s | ✅ exit_code | ✅ 0.1s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.1s | ✅ exit_code |
| 9 | `hotspot3d` | ✅ 0.5s | ✅ 1.9s | ✅ exit_code | ✅ 0.1s | ✅ 1.3s | ✅ exit_code | ✅ 0.2s | ✅ 1.2s | ✅ exit_code |
| 10 | `huffman` | ✅ 3.3s | ✅ 0.1s | ✅ exit_code | — | — | — | — | — | — |
| 11 | `hybridsort` | ❌ 0.0s | ❓ 0.0s | ❌ exit_code | — | — | — | ✅ 0.1s | ✅ 0.4s | ✅ exit_code |
| 12 | `kmeans` | ❌ 0.0s | ❓ 0.0s | ❌ exit_code | ✅ 0.3s | ✅ 1.9s | ✅ exit_code | ✅ 0.8s | ❌ 1.5s | ❌ exit_code |
| 13 | `lavamd` | ✅ 1.0s | ✅ 0.0s | ✅ exit_code | ✅ 0.1s | ✅ 0.0s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code |
| 14 | `lud` | ✅ 1.2s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code | ✅ 0.4s | ✅ 0.2s | ✅ exit_code |
| 15 | `mummergpu` | ❌ 0.0s | ❓ 0.0s | ❌ exit_code | ❌ 0.0s | ❓ 0.0s | ❌ exit_code | — | — | — |
| 16 | `myocyte` | ✅ 1.6s | ✅ 0.9s | ✅ exit_code | ✅ 0.3s | ✅ 0.0s | ✅ exit_code | ✅ 0.3s | ✅ 0.0s | ✅ exit_code |
| 17 | `nn` | ✅ 1.1s | ✅ 0.1s | ✅ exit_code | ✅ 0.0s | ✅ 0.0s | ✅ exit_code | ✅ 0.6s | ❌ 1.1s | ❌ exit_code |
| 18 | `nw` | ✅ 0.6s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code | ✅ 0.3s | ✅ 0.1s | ✅ exit_code |
| 19 | `particlefilter` | ✅ 1.6s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code | ✅ 0.9s | ✅ 0.2s | ✅ exit_code |
| 20 | `pathfinder` | ✅ 0.5s | ✅ 0.1s | ✅ exit_code | ✅ 0.1s | ✅ 0.0s | ✅ exit_code | ❌ 0.0s | ❓ 0.0s | ❌ exit_code |
| 21 | `srad` | ✅ 0.5s | ✅ 0.1s | ✅ exit_code | ✅ 0.2s | ✅ 0.0s | ✅ exit_code | ✅ 0.2s | ✅ 0.1s | ✅ exit_code |
| 22 | `streamcluster` | ✅ 2.0s | ✅ 2.2s | ✅ exit_code | ✅ 0.7s | ✅ 24.9s | ✅ exit_code | ✅ 0.7s | ✅ 2.1s | ✅ exit_code |

## API Summary

| API | Total | Build PASS | Run PASS | Verify PASS | Full PASS |
|-----|-------|-----------|----------|-------------|-----------|
| CUDA | 22 | 18/22 | 18/22 | 18/22 | 18/22 |
| OMP | 18 | 17/18 | 17/18 | 17/18 | 17/18 |
| OPENCL | 20 | 18/20 | 16/20 | 16/20 | 16/20 |

## Failures (9 specs)

| Spec | Category | Details |
|------|----------|---------|
| `rodinia-cfd-cuda` | BUILD_FAIL | harness.builder INFO: [stderr] euler3d.cu:5:10: fatal error: helper_cuda.h: No such file or directory make: *** [Makefile:17: euler3d] Error 1 |
| `rodinia-cfd-opencl` | BUILD_FAIL | ream<char>’} to ‘const std::error_condition&’   513 \|   operator==(const error_condition& __lhs, const error_code& __rhs) noexcept make: *** [Makefil |
| `rodinia-hybridsort-cuda` | BUILD_FAIL | make: *** [Makefile:23: clean] Error 1 harness.builder INFO: [stderr] bucketsort.cu:10:10: fatal error: GL/glew.h: No such file or directory make: *** |
| `rodinia-kmeans-cuda` | BUILD_FAIL | kmeans_cuda_kernel.cu(89): error: no instance of overloaded function "tex1Dfetch" matches the argument list             argument types are: (<error-ty |
| `rodinia-mummergpu-cuda` | BUILD_FAIL | make[1]: *** [Makefile:114: obj/release/suffix-tree.cpp_o] Error 1 make: *** [Makefile:4: mummer] Error 2 |
| `rodinia-mummergpu-omp` | BUILD_FAIL | make[1]: *** [Makefile:114: obj/release/suffix-tree.cpp_o] Error 1 make: *** [Makefile:4: mummer] Error 2 |
| `rodinia-pathfinder-opencl` | BUILD_FAIL | make: *** [Makefile:32: main.o] Error 1 |
| `rodinia-kmeans-opencl` | RUN_SEGFAULT | exit=-11 \| stderr:  |
| `rodinia-nn-opencl` | RUN_SEGFAULT | exit=-11 \| stderr:  |
