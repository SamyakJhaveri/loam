# Eval Batch: omp-to-omp_target — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**4/5 PASS (80%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.229× | wall_time | 42610 |
| xsbench | L1 | ✓ PASS | 1.234× | wall_time | 42610 |
| xsbench | L2 | ✓ PASS | 1.221× | wall_time | 42614 |
| xsbench | L3 | ✓ PASS | 1.218× | wall_time | 42622 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 101760 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 99818 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 99818 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 99828 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 99696 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 93280 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 71372 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 88402 |
| xsbench | L2 | ✗ EXTRACTION_FAIL | — | None | 76158 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 72842 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 74543 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L1 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L2 | ✓ PASS | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L3 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✗ RUN_FAIL | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
