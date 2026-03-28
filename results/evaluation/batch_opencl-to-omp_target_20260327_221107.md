# Eval Batch: opencl-to-omp_target — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ EXTRACTION_FAIL | — | None | 63940 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 44798 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 44804 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 44812 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 67804 |

## Cross-Model Summary

| Kernel | Level | groq-llama-3.3-70b-versatile |
|--------|-------|---|
| xsbench | L0 | ✗ EXTRACTION_FAIL |
| xsbench | L1 | ✗ BUILD_FAIL |
| xsbench | L2 | ✗ BUILD_FAIL |
| xsbench | L3 | ✗ BUILD_FAIL |
| xsbench | L4 | ✗ BUILD_FAIL |
