# Eval Batch: cuda-to-omp_target — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.087× | wall_time | 105543 |
| xsbench | L1 | ✓ PASS | 1.223× | wall_time | 109728 |
| xsbench | L2 | ✓ PASS | 1.078× | wall_time | 45031 |
| xsbench | L3 | ✓ PASS | 1.218× | wall_time | 105432 |
| xsbench | L4 | ✓ PASS | 1.070× | wall_time | 45585 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 93153 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 93153 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 93097 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 93337 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 93323 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ EXTRACTION_FAIL | — | None | 87716 |
| xsbench | L1 | ✗ EXTRACTION_FAIL | — | None | 87168 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 88411 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 77113 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 75241 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L1 | ✓ PASS | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L2 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L3 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
