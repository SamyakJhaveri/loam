# Eval Batch: opencl-to-cuda — 2026-03-31
**Date:** 2026-03-31  |  **Tasks:** 60

## together-qwen-3.5-397b-a17b
**0/20 PASS (0%)** | FAILURES=20 | ERROR=0 | SKIP=0

| Kernel | Status | Speedup | Timing Method | Tokens |
|--------|--------|---------|---------------|--------|
| backprop | ✗ BUILD_FAIL | — | None | 14795 |
| bfs | ✗ BUILD_FAIL | — | None | 16381 |
| bptree | ✗ BUILD_FAIL | — | None | 33712 |
| cfd | ✗ BUILD_FAIL | — | None | 41484 |
| dwt2d | ✗ BUILD_FAIL | — | None | 34122 |
| gaussian | ✗ BUILD_FAIL | — | None | 21809 |
| heartwall | ✗ EXTRACTION_FAIL | — | None | 62873 |
| hotspot | ✗ BUILD_FAIL | — | None | 10520 |
| hotspot3d | ✗ BUILD_FAIL | — | None | 12385 |
| hybridsort | ✗ BUILD_FAIL | — | None | 38777 |
| kmeans | ✗ BUILD_FAIL | — | None | 33830 |
| lavamd | ✗ BUILD_FAIL | — | None | 12149 |
| lud | ✗ BUILD_FAIL | — | None | 13423 |
| myocyte | ✗ BUILD_FAIL | — | None | 61275 |
| nn | ✗ BUILD_FAIL | — | None | 17243 |
| nw | ✗ BUILD_FAIL | — | None | 16227 |
| particlefilter | ✗ BUILD_FAIL | — | None | 48708 |
| pathfinder | ✗ BUILD_FAIL | — | None | 10108 |
| srad | ✗ BUILD_FAIL | — | None | 21616 |
| streamcluster | ✗ BUILD_FAIL | — | None | 32805 |

## Cross-Model Summary

| Kernel | together-qwen-3.5-397b-a17b |
|--------|---|
| backprop | ✗ BUILD_FAIL |
| bfs | ✗ BUILD_FAIL |
| bptree | ✗ BUILD_FAIL |
| cfd | ✗ BUILD_FAIL |
| dwt2d | ✗ BUILD_FAIL |
| gaussian | ✗ BUILD_FAIL |
| heartwall | ✗ EXTRACTION_FAIL |
| hotspot | ✗ BUILD_FAIL |
| hotspot3d | ✗ BUILD_FAIL |
| hybridsort | ✗ BUILD_FAIL |
| kmeans | ✗ BUILD_FAIL |
| lavamd | ✗ BUILD_FAIL |
| lud | ✗ BUILD_FAIL |
| myocyte | ✗ BUILD_FAIL |
| nn | ✗ BUILD_FAIL |
| nw | ✗ BUILD_FAIL |
| particlefilter | ✗ BUILD_FAIL |
| pathfinder | ✗ BUILD_FAIL |
| srad | ✗ BUILD_FAIL |
| streamcluster | ✗ BUILD_FAIL |
