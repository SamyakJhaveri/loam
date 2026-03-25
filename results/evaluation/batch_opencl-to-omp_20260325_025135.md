# Eval Batch: opencl-to-omp — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 97157 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 97255 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 97244 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 96569 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 96852 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 95391 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 103026 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 100007 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 99783 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 99885 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 67555 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 44884 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 71167 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 66586 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 67439 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L1 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L2 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L3 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
