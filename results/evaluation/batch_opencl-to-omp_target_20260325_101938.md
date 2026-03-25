# Eval Batch: opencl-to-omp_target — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 3

## claude-sonnet-4-6
**1/1 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✓ PASS | 1.180× | wall_time | 43344 |

## gemini-2.5-flash-lite
**0/1 PASS (0%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✗ BUILD_FAIL | — | None | 87297 |

## groq-llama-3.3-70b-versatile
**0/1 PASS (0%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✗ BUILD_FAIL | — | None | 68725 |

## Cross-Model Summary

| Kernel | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|---|---|---|
| xsbench | ✓ PASS | ✗ BUILD_FAIL | ✗ BUILD_FAIL |
