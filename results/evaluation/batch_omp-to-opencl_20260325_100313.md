# Eval Batch: omp-to-opencl — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 3

## claude-sonnet-4-6
**1/1 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✓ PASS | 1.152× | wall_time | 45597 |

## gemini-2.5-flash-lite
**0/1 PASS (0%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✗ RUN_FAIL | — | None | 92822 |

## groq-llama-3.3-70b-versatile
**0/1 PASS (0%)** | FAILURES=1 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| xsbench | ✗ EXTRACTION_FAIL | — | None | 72572 |

## Cross-Model Summary

| Kernel | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|---|---|---|
| xsbench | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
