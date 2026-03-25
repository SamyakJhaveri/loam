# Eval Batch: omp_target-to-opencl — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**5/5 PASS (100%)** | FAILURES=0 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.826× | wall_time | 38930 |
| xsbench | L1 | ✓ PASS | 1.038× | wall_time | 39075 |
| xsbench | L2 | ✓ PASS | 1.035× | wall_time | 38945 |
| xsbench | L3 | ✓ PASS | 1.033× | wall_time | 38797 |
| xsbench | L4 | ✓ PASS | 1.040× | wall_time | 38919 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 105496 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 105496 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 87053 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 100474 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 82642 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ EXTRACTION_FAIL | — | None | 61762 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 62728 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 65382 |
| xsbench | L3 | ✗ EXTRACTION_FAIL | — | None | 62234 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 62443 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L1 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L2 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
| xsbench | L3 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L4 | ✓ PASS | ✗ RUN_FAIL | ✗ RUN_FAIL |
