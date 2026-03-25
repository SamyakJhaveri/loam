# Eval Batch: omp-to-opencl — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.980× | wall_time | 45597 |
| xsbench | L1 | ✓ PASS | 1.018× | wall_time | 45615 |
| xsbench | L2 | ✓ PASS | 1.030× | wall_time | 45608 |
| xsbench | L3 | ✓ PASS | 1.030× | wall_time | 45598 |
| xsbench | L4 | ✓ PASS | 0.980× | wall_time | 45697 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 92822 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 92822 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 92773 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 92515 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 91801 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 73047 |
| xsbench | L1 | ✗ EXTRACTION_FAIL | — | None | 72541 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 75558 |
| xsbench | L3 | ✗ EXTRACTION_FAIL | — | None | 73131 |
| xsbench | L4 | ✗ EXTRACTION_FAIL | — | None | 72616 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L1 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L2 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L3 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L4 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
