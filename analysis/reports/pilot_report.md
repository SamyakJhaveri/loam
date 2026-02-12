# ParBench Pilot Report

_Generated: 2026-02-10 11:33:07 UTC_

## Summary

- **Total kernels:** 5
- **Total specs:** 20
- **Total translation pairs:** 60 (5 kernels × 12 pairs each)

## Kernel Coverage

| Kernel | cuda | hip | omp | sycl | APIs | Pairs |
| --- | --- | --- | --- | --- | --- | --- |
| binomial | ✓ | ✓ | ✓ | ✓ | 4 | 12 |
| nn | ✓ | ✓ | ✓ | ✓ | 4 | 12 |
| particle-diffusion | ✓ | ✓ | ✓ | ✓ | 4 | 12 |
| radixsort | ✓ | ✓ | ✓ | ✓ | 4 | 12 |
| scan | ✓ | ✓ | ✓ | ✓ | 4 | 12 |

## API Distribution

- **cuda:** 5 kernel(s)
- **hip:** 5 kernel(s)
- **omp:** 5 kernel(s)
- **sycl:** 5 kernel(s)

## File Classifications

### binomial

**cuda:**
- prompt_payload: kernel.cu, main.cu
- support_files: Makefile, CMakeLists.txt, binomialOptions.h, realtype.h
- verification_only: reference.cu

**hip:**
- prompt_payload: kernel.cu, main.cu
- support_files: Makefile, CMakeLists.txt, binomialOptions.h, realtype.h
- verification_only: reference.cu

**omp:**
- prompt_payload: kernel.cpp, main.cpp
- support_files: Makefile, Makefile.aomp, CMakeLists.txt, binomialOptions.h, realtype.h
- verification_only: reference.cpp

**sycl:**
- prompt_payload: kernel.cpp, main.cpp
- support_files: Makefile, CMakeLists.txt, binomialOptions.h, realtype.h
- verification_only: reference.cpp

### nn

**cuda:**
- prompt_payload: nearestNeighbor.cu, nearestNeighbor.h
- support_files: Makefile, CMakeLists.txt, utils.cu, utils.h, filelist.txt
- verification_only: (none)

**hip:**
- prompt_payload: nearestNeighbor.cu, nearestNeighbor.h
- support_files: Makefile, Makefile.hipcl, CMakeLists.txt, utils.cu, utils.h, filelist.txt
- verification_only: (none)

**omp:**
- prompt_payload: nearestNeighbor.cpp, nearestNeighbor.h
- support_files: Makefile, Makefile.aomp, Makefile.nvc, CMakeLists.txt, utils.cpp, utils.h, filelist.txt
- verification_only: (none)

**sycl:**
- prompt_payload: nearestNeighbor.cpp, nearestNeighbor.h
- support_files: Makefile, CMakeLists.txt, utils.cpp, utils.h, filelist.txt
- verification_only: (none)

### particle-diffusion

**cuda:**
- prompt_payload: motionsim.cu
- support_files: Makefile, CMakeLists.txt
- verification_only: reference.h

**hip:**
- prompt_payload: motionsim.cu
- support_files: Makefile, Makefile.hipcl, CMakeLists.txt
- verification_only: ../particle-diffusion-cuda/reference.h

**omp:**
- prompt_payload: motionsim.cpp
- support_files: Makefile, Makefile.aomp, Makefile.nvc, CMakeLists.txt
- verification_only: ../particle-diffusion-cuda/reference.h

**sycl:**
- prompt_payload: motionsim.cpp
- support_files: Makefile, CMakeLists.txt
- verification_only: ../particle-diffusion-cuda/reference.h

### radixsort

**cuda:**
- prompt_payload: main.cu, RadixSort.cu, RadixSort_kernels.cu, Scan.cu, Scan_kernels.cu
- support_files: Makefile, CMakeLists.txt, RadixSort.h, Scan.h
- verification_only: (none)

**hip:**
- prompt_payload: main.cu, RadixSort.cu, RadixSort_kernels.cu, Scan.cu, Scan_kernels.cu
- support_files: Makefile, Makefile.hipcl, CMakeLists.txt, RadixSort.h, Scan.h
- verification_only: (none)

**omp:**
- prompt_payload: main.cpp, RadixSort.cpp, RadixSort_kernels.cpp, Scan.cpp, Scan_kernels.cpp
- support_files: Makefile, Makefile.aomp, Makefile.nvc, CMakeLists.txt, RadixSort.h, Scan.h
- verification_only: (none)

**sycl:**
- prompt_payload: main.cpp, RadixSort.cpp, RadixSort_kernels.cpp, Scan.cpp, Scan_kernels.cpp
- support_files: Makefile, CMakeLists.txt, RadixSort.h, Scan.h
- verification_only: (none)

### scan

**cuda:**
- prompt_payload: main.cu
- support_files: Makefile, CMakeLists.txt
- verification_only: (none)

**hip:**
- prompt_payload: main.cu
- support_files: Makefile, Makefile.hipcl, CMakeLists.txt
- verification_only: (none)

**omp:**
- prompt_payload: main.cpp
- support_files: Makefile, Makefile.aomp, Makefile.nvc, CMakeLists.txt
- verification_only: (none)

**sycl:**
- prompt_payload: main.cpp
- support_files: Makefile, CMakeLists.txt
- verification_only: (none)

## Validation Status

✓ **20/20** specs pass all checks

### Validation Output

```
Validating manifest...
  ✓ manifest (manifest.jsonl): all entries valid

Validating referenced specs...
  ✓ spec (hecbench-binomial-cuda.json): valid
  ✓ spec (hecbench-binomial-hip.json): valid
  ✓ spec (hecbench-binomial-omp.json): valid
  ✓ spec (hecbench-binomial-sycl.json): valid
  ✓ spec (hecbench-nn-cuda.json): valid
  ✓ spec (hecbench-nn-hip.json): valid
  ✓ spec (hecbench-nn-omp.json): valid
  ✓ spec (hecbench-nn-sycl.json): valid
  ✓ spec (hecbench-particle-diffusion-cuda.json): valid
  ✓ spec (hecbench-particle-diffusion-hip.json): valid
  ✓ spec (hecbench-particle-diffusion-omp.json): valid
  ✓ spec (hecbench-particle-diffusion-sycl.json): valid
  ✓ spec (hecbench-radixsort-cuda.json): valid
  ✓ spec (hecbench-radixsort-hip.json): valid
  ✓ spec (hecbench-radixsort-omp.json): valid
  ✓ spec (hecbench-radixsort-sycl.json): valid
  ✓ spec (hecbench-scan-cuda.json): valid
  ✓ spec (hecbench-scan-hip.json): valid
  ✓ spec (hecbench-scan-omp.json): valid
  ✓ spec (hecbench-scan-sycl.json): valid

Checking for unreferenced specs...

Running manifest–spec consistency checks...
  ✓ manifest–spec consistency: all entries match

Running cross-kernel pairing checks...
  Kernels: 5
    binomial: cuda, hip, omp, sycl
    nn: cuda, hip, omp, sycl
    particle-diffusion: cuda, hip, omp, sycl
    radixsort: cuda, hip, omp, sycl
    scan: cuda, hip, omp, sycl
  Total translation pairs: 60

⚠ 10 warning(s):

  specs/hecbench-binomial-cuda.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['kernel.o', 'main', 'main.o', 'reference.o']
  specs/hecbench-binomial-omp.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['kernel.o', 'main', 'main.o', 'reference.o']
  specs/hecbench-nn-cuda.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'nearestNeighbor.o', 'utils.o']
  specs/hecbench-nn-omp.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'nearestNeighbor.o', 'utils.o']
  specs/hecbench-particle-diffusion-cuda.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'motionsim.o']
  specs/hecbench-particle-diffusion-omp.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'motionsim.o']
  specs/hecbench-radixsort-cuda.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['RadixSort.o', 'Scan.o', 'main', 'main.o']
  specs/hecbench-radixsort-omp.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['RadixSort.o', 'Scan.o', 'main', 'main.o']
  specs/hecbench-scan-cuda.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'main.o']
  specs/hecbench-scan-omp.json: ⚠ WARNING: [spec] files: orphan files in source dir not in any list: ['main', 'main.o']

✓ All validations passed.
```
