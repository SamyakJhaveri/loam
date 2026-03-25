# Eval Batch: cuda-to-opencl — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 1.053× | wall_time | 50296 |
| xsbench | L1 | ✓ PASS | 1.058× | wall_time | 50305 |
| xsbench | L2 | ✓ PASS | 1.035× | wall_time | 50310 |
| xsbench | L3 | ✓ PASS | 1.045× | wall_time | 50374 |
| xsbench | L4 | ✓ PASS | 0.993× | wall_time | 50498 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 130901 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 130901 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 101569 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 122258 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 135906 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 81348 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 78040 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 82588 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 82699 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 80023 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L1 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L2 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L3 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L4 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
