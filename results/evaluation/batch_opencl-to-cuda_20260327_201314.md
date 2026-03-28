# Eval Batch: opencl-to-cuda — 2026-03-27
**Date:** 2026-03-27  |  **Tasks:** 5

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 45404 |
| xsbench | L1 | ✗ EXTRACTION_FAIL | — | None | 57634 |
| xsbench | L2 | ✗ EXTRACTION_FAIL | — | None | 80833 |
| xsbench | L3 | ✗ EXTRACTION_FAIL | — | None | 80509 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 45454 |

## Cross-Model Summary

| Kernel | Level | groq-llama-3.3-70b-versatile |
|--------|-------|---|
| xsbench | L0 | ✗ RUN_FAIL |
| xsbench | L1 | ✗ EXTRACTION_FAIL |
| xsbench | L2 | ✗ EXTRACTION_FAIL |
| xsbench | L3 | ✗ EXTRACTION_FAIL |
| xsbench | L4 | ✗ RUN_FAIL |
