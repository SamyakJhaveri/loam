# Eval Batch: omp_target-to-omp — 2026-03-25
**Date:** 2026-03-25  |  **Tasks:** 15

## claude-sonnet-4-6
**2/5 PASS (40%)** | FAILURES=3 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✓ PASS | 0.721× | wall_time | 82635 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 81327 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 82220 |
| xsbench | L3 | ✓ PASS | 0.955× | wall_time | 84426 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 82194 |

## gemini-2.5-flash-lite
**0/5 PASS (0%)** | FAILURES=5 | ERROR=0 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ RUN_FAIL | — | None | 85208 |
| xsbench | L1 | ✗ RUN_FAIL | — | None | 85208 |
| xsbench | L2 | ✗ RUN_FAIL | — | None | 85228 |
| xsbench | L3 | ✗ RUN_FAIL | — | None | 85299 |
| xsbench | L4 | ✗ RUN_FAIL | — | None | 85414 |

## groq-llama-3.3-70b-versatile
**0/5 PASS (0%)** | FAILURES=4 | ERROR=1 | SKIP=0

| Kernel | Level | Status | Speedup | Timing Method | Tokens |
|--------|-------|--------|---------|---------------|--------|
| xsbench | L0 | ✗ EXTRACTION_FAIL | — | None | 58697 |
| xsbench | L1 | ✗ BUILD_FAIL | — | None | 57266 |
| xsbench | L2 | ! ERROR | — | None | — |
| xsbench | L3 | ✗ BUILD_FAIL | — | None | 57440 |
| xsbench | L4 | ✗ EXTRACTION_FAIL | — | None | 57060 |

## Cross-Model Summary

| Kernel | Level | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile |
|--------|-------|---|---|---|
| xsbench | L0 | ✓ PASS | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
| xsbench | L1 | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| xsbench | L2 | ✗ RUN_FAIL | ✗ RUN_FAIL | ! ERROR |
| xsbench | L3 | ✓ PASS | ✗ RUN_FAIL | ✗ BUILD_FAIL |
| xsbench | L4 | ✗ RUN_FAIL | ✗ RUN_FAIL | ✗ EXTRACTION_FAIL |
