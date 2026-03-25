# Eval Batch: omp_target-to-cuda — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.926× | wall_time | 34457 |
| xsbench | L1 | ✓ PASS | 0.917× | wall_time | 34723 |
| xsbench | L2 | ✓ PASS | 0.917× | wall_time | 34548 |
| xsbench | L3 | ✓ PASS | 0.919× | wall_time | 35241 |
| xsbench | L4 | ✓ PASS | 1.013× | wall_time | 73066 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 72182 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 72182 |
| xsbench | L2 | ✗ BUILD_FAIL | — | None | 86167 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 87735 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 87786 |

## groq-llama-3.3-70b-versatile
**1/5 PASS (20%)** | FAILURES=4 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 58199 |
| xsbench | L1 | ✓ PASS | 0.914× | wall_time | 28233 |
| xsbench | L2 | ✗ EXTRACTION_FAIL | — | None | 57701 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 55784 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 24957 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L1 | ✓ PASS | ✗ BUILD_FAIL | ✓ PASS |
| xsbench | L2 | ✓ PASS | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L3 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
