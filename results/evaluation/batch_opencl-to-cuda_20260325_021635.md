# Eval Batch: opencl-to-cuda — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.052× | wall_time | 43901 |
| xsbench | L1 | ✓ PASS | 1.009× | wall_time | 91458 |
| xsbench | L2 | ✓ PASS | 1.002× | wall_time | 92122 |
| xsbench | L3 | ✓ PASS | 1.009× | wall_time | 44130 |
| xsbench | L4 | ✓ PASS | 0.928× | wall_time | 44034 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 103731 |
| xsbench | L1 | ✗ EXTRACTION_FAIL | — | None | 103626 |
| xsbench | L2 | ✗ EXTRACTION_FAIL | — | None | 100965 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 103670 |
| xsbench | L4 | ✗ BUILD_FAIL | — | None | 92656 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ BUILD_FAIL | — | None | 69024 |
| xsbench | L1 | ✗ EXTRACTION_FAIL | — | None | 80669 |
| xsbench | L2 | ✗ EXTRACTION_FAIL | — | None | 68291 |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 68260 |
| xsbench | L4 | ✗ EXTRACTION_FAIL | — | None | 79931 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L1 | ✓ PASS | ✗ EXTRACTION_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L2 | ✓ PASS | ✗ EXTRACTION_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L3 | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✓ PASS | ✗ BUILD_FAIL | ✗ EXTRACTION_FAIL |
