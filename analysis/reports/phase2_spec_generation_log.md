# Phase 2: Spec Generation Log

**Date**: 2026-02-12
**Total new specs**: 60 (15 kernels × 4 APIs: cuda, hip, sycl, omp)
**Total specs**: 80 (5 pilot + 15 new × 4 APIs)
**Validation**: `python scripts/validate_schema.py --all` — ✓ All passed (0 errors, 12 warnings for build artifacts)

## Kernel List Changes

The original approved list proposed histogram, bwt, heat2d. These were replaced with **bilateral**, **chi2**, **fwt** during spec generation. Reasons:
- bilateral: well-structured bilateral filter with clear reference comparison
- chi2: compact chi-squared distance kernel with self-checking
- fwt: Fast Walsh Transform with clean prompt/reference separation

## File Classifications (CUDA variant shown — other APIs follow same pattern)

| Kernel | Category | Prompt Payload | Support Files | Verification Only | Strategy |
|--------|----------|---------------|---------------|-------------------|----------|
| aes | crypto | `kernels.cu`, `main.cu` | `Makefile`, `CMakeLists.txt`, `aes.h`, `utils.cu`, `COPYRIGHT`, `README` | `reference.cu` | stdout_pattern `"Pass"` |
| bilateral | image | `main.cu` | `Makefile`, `CMakeLists.txt` | `reference.h` | stdout_pattern `"PASS"` |
| chacha20 | crypto | `main.cu`, `chacha20.h` | `Makefile`, `CMakeLists.txt`, `LICENSE` | _(none)_ | stdout_pattern `"PASS"` |
| chi2 | other | `chi2.cu` | `Makefile`, `CMakeLists.txt` | `reference.h` | stdout_pattern `"PASS"` |
| convolutionseparable | other | `conv.cu`, `main.cu` | `Makefile`, `CMakeLists.txt`, `conv.h` | `conv_gold.cu` | stdout_pattern `"PASS"` |
| dct8x8 | other | `kernels.cu`, `main.cu` | `Makefile`, `CMakeLists.txt`, `DCT8x8.h` | `DCT8x8_gold.cu` | stdout_pattern `"PASS"` |
| eigenvalue | linear_algebra | `kernels.cu`, `main.cu` | `Makefile`, `CMakeLists.txt` | `reference.cu`, `reference.h`, `utils.cu` | stdout_pattern `"PASS"` |
| fft | other | `main.cu`, `fft1D_512.h`, `ifft1D_512.h` | `Makefile`, `CMakeLists.txt`, `LICENSE` | `reference.h` | stdout_pattern `"PASS"` |
| fwt | other | `main.cu`, `kernels.cu` | `Makefile`, `CMakeLists.txt` | `reference.cu` | stdout_pattern `"PASS"` |
| ising | physics | `main.cu` | `Makefile`, `CMakeLists.txt`, `cudamacro.h` | `reference.h` | stdout_pattern `"PASS"` |
| lud | linear_algebra | `lud.cu`, `lud_kernels.cu` | `Makefile`, `CMakeLists.txt`, `common/common.h` | `common/common.cpp` | exit_code + stdout_pattern |
| merge | sort | `main.cu`, `kernels.h` | `Makefile`, `CMakeLists.txt`, `COPYRIGHT` | _(none)_ | stdout_pattern `"PASS"` |
| nbody | physics | `GSimulation.cu`, `GSimulationKernels.hpp`, `main.cu` | `Makefile`, `CMakeLists.txt`, `GSimulation.hpp`, `Particle.hpp`, `type.hpp`, `License.txt`, `README.md` | `GSimulationReference.hpp` | stdout_pattern `"PASS"` |
| simplespmv | linear_algebra | `kernels.cu`, `main.cpp` | `Makefile`, `CMakeLists.txt`, `mv.h`, `LICENSE` | `utils.cpp` | exit_code |
| sobel | image | `kernels.cu`, `main.cu` | `Makefile`, `CMakeLists.txt`, `sobel.h`, `README` | `reference.cu` | stdout_pattern `"PASS"` |

## Decisions & Notes

1. **unique_id casing**: `convolutionSeparable` and `simpleSpmv` had camelCase kernel_name but the schema requires lowercase unique_id. Fixed by lowercasing kernel_name to `convolutionseparable` and `simplespmv` in both specs and manifest. Source directory paths (`src/convolutionSeparable-cuda/`) retained original casing.

2. **Orphan file warnings**: 
   - `utils.cu` / `utils.cpp` in aes specs → added to `support_files` (CPU-only utility functions `#include`'d by main)
   - `main2.cpp` in fwt-omp → added to `support_files` (alternative monolithic implementation, not used in default build)
   - Build artifacts (`main`, `*.o`) → ignored (12 remaining warnings, all build outputs)

3. **External input files**: aes requires `../urng-sycl/URNG_Input.bmp`, sobel requires `../sobel-sycl/SobelFilter_Input.bmp` — both referenced in run_command.

4. **Verification**: 13/15 kernels use stdout_pattern for `"PASS"` (aes uses `"Pass"`). lud uses exit_code + timing pattern. simplespmv uses exit_code based on error rates.

5. **No verification_only files**: chacha20 and merge have no separate reference files — correctness checking is inline.

## Domain Coverage (20 kernels total)

| Domain | Kernels |
|--------|---------|
| Sorting / parallel primitives | radixsort, merge |
| Reduction / prefix sum | scan |
| Graph / search | nn |
| Finance | binomial |
| Physics simulation | particle-diffusion, nbody |
| Statistical physics | ising |
| Cryptography | aes, chacha20 |
| Linear algebra | lud, eigenvalue, simplespmv |
| Image processing | sobel, bilateral |
| Signal processing | dct8x8, convolutionseparable, fft, fwt |
| Statistics | chi2 |
