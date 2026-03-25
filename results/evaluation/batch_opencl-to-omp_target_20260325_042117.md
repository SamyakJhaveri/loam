# Eval Batch: opencl-to-omp_target — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.192× | wall_time | 42699 |
| xsbench | L1 | ✓ PASS | 1.156× | wall_time | 41514 |
| xsbench | L2 | ✓ PASS | 1.123× | wall_time | 94021 |
| xsbench | L3 | ✓ PASS | 1.146× | wall_time | 93700 |
| xsbench | L4 | ✓ PASS | 1.149× | wall_time | 43270 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 87297 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 87296 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 87304 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 87309 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 87332 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 64432 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 65549 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 69206 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 68778 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 69277 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L1 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L2 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L3 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
