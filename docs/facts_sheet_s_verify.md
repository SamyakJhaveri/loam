# S-VERIFY Facts Sheet (Ground Truth)
Generated: 2026-03-28

## Spec Baseline
- Total Rodinia specs: 60
- Rodinia TRUE PASS: 54
- Rodinia KNOWN_FAIL: 6
  - `rodinia-kmeans-cuda` (texture<> removed in CUDA 12)
  - `rodinia-mummergpu-cuda` (texture<> removed in CUDA 12)
  - `rodinia-mummergpu-omp` (texture<> + cuMemGetInfo_v2 signature)
  - `rodinia-hybridsort-cuda` (GL/glew.h not found)
  - `rodinia-nn-opencl` (TIMEOUT / SIGSEGV)
  - `rodinia-kmeans-opencl` (SIGSEGV in OpenCL runtime)
- XSBench specs: 4, all PASS (cuda, omp, opencl, omp_target)
- Total non-KNOWN_FAIL PASS: 58 (54 Rodinia + 4 XSBench)
- Eval batch eligible: 57 (54 Rodinia TRUE PASS + 3 XSBench standard; omp_target excluded)

## Eval Results Summary

### Models evaluated
| Model ID | Pass | Total | Rate |
|----------|------|-------|------|
| claude-sonnet-4-6 | 81 | 156 | 51.92% |
| gemini-2.5-flash-lite | 11 | 156 | 7.05% |
| groq-llama-3.3-70b-versatile | 13 | 156 | 8.33% |
| **All models** | **105** | **468** | **22.44%** |

NOTE: eval_summary.json excludes kmeans and mummergpu results (KNOWN_FAIL source specs).
36 additional raw result files exist on disk (12 per model) for those kernels but are not
counted in the summary. Claude-sonnet has 5 additional PASS results from kmeans-cuda-to-omp
translations that are correctly excluded from the summary totals.

### Translation directions
| Direction | Pass | Total | Rate |
|-----------|------|-------|------|
| cuda-to-omp | 62 | 255 | 24.31% |
| cuda-to-omp_target | 4 | 15 | 26.67% |
| cuda-to-opencl | 5 | 15 | 33.33% |
| omp-to-cuda | 9 | 63 | 14.29% |
| omp-to-omp_target | 0 | 15 | 0.00% |
| omp-to-opencl | 5 | 15 | 33.33% |
| omp_target-to-cuda | 4 | 15 | 26.67% |
| omp_target-to-omp | 3 | 15 | 20.00% |
| omp_target-to-opencl | 4 | 15 | 26.67% |
| opencl-to-cuda | 5 | 15 | 33.33% |
| opencl-to-omp | 0 | 15 | 0.00% |
| opencl-to-omp_target | 4 | 15 | 26.67% |

12 translation directions total. Two directions have 0% pass rate: omp-to-omp_target, opencl-to-omp.

### Per-augmentation-level pass rates
| Level | Pass | Total | Rate |
|-------|------|-------|------|
| L0 | 31 | 132 | 23.48% |
| L1 | 20 | 84 | 23.81% |
| L2 | 21 | 84 | 25.00% |
| L3 | 17 | 84 | 20.24% |
| L4 | 16 | 84 | 19.05% |

### Failure taxonomy (across all 468 tasks)
| Status | Count | % of total |
|--------|-------|-----------|
| PASS | 105 | 22.44% |
| BUILD_FAIL | 180 | 38.46% |
| RUN_FAIL | 89 | 19.02% |
| EXTRACTION_FAIL | 49 | 10.47% |
| VERIFY_FAIL | 45 | 9.62% |

### Self-repair statistics
- Attempt 1 PASS: 78 (74.3% of all 105 PASSes)
- Repaired by retry: 27 (25.7% of all 105 PASSes)
- Total tasks evaluated: 468

### Per-kernel pass rates (from eval_summary.json)
| Kernel | Pass | Total | Rate |
|--------|------|-------|------|
| bptree | 12 | 18 | 66.67% |
| hotspot3d | 11 | 18 | 61.11% |
| particlefilter | 10 | 18 | 55.56% |
| backprop | 9 | 18 | 50.00% |
| lud | 8 | 18 | 44.44% |
| lavamd | 7 | 18 | 38.89% |
| cfd | 5 | 18 | 27.78% |
| nn | 3 | 18 | 16.67% |
| srad | 2 | 18 | 11.11% |
| bfs | 1 | 18 | 5.56% |
| hotspot | 1 | 18 | 5.56% |
| pathfinder | 1 | 18 | 5.56% |
| streamcluster | 1 | 18 | 5.56% |
| xsbench | 34 | 180 | 18.89% |
| heartwall | 0 | 18 | 0.00% |
| myocyte | 0 | 18 | 0.00% |
| nw | 0 | 18 | 0.00% |

## Augmentation Baseline

### Rodinia (definitive: retest_post_session2.json)
- Level-invariance claim: **VERIFIED YES**
- 54/60 PASS at ALL levels L1-L4 (identical counts)
- 4 BUILD_FAIL at all levels (KNOWN_FAIL specs: kmeans-cuda, mummergpu-cuda, mummergpu-omp, hybridsort-cuda)
- 2 FAIL at all levels (nn-opencl, kmeans-opencl -- also KNOWN_FAIL)
- Augmentation introduces ZERO new failures beyond the pre-existing 6 KNOWN_FAIL

| Level | PASS | BUILD_FAIL | FAIL |
|-------|------|-----------|------|
| L1 | 54 | 4 | 2 |
| L2 | 54 | 4 | 2 |
| L3 | 54 | 4 | 2 |
| L4 | 54 | 4 | 2 |

### XSBench (from xsbench_L2_seed42.json)
- 3/3 PASS at L2 (cuda, omp, opencl)
- omp_target not tested (requires nvc)
- Full L1-L4 sweep not recorded separately; L2 spot-check PASS for all 3 standard APIs

## Spot-Check Verification

### Files checked (9 total, 3 per model)

**claude-sonnet-4-6:**
- `rodinia-backprop-cuda-to-rodinia-backprop-omp.json`: overall_status=PASS (L0) -- matches summary (backprop 9/18 PASS)
- `rodinia-bptree-cuda-to-rodinia-bptree-omp.json`: overall_status=PASS (L0) -- matches summary (bptree 12/18 PASS)
- `rodinia-hotspot3d-cuda-to-rodinia-hotspot3d-omp.json`: overall_status=PASS (L0) -- matches summary (hotspot3d 11/18 PASS)

**gemini-2.5-flash-lite:**
- `rodinia-backprop-cuda-to-rodinia-backprop-omp.json`: overall_status=PASS (L0) -- matches summary
- `rodinia-bptree-cuda-to-rodinia-bptree-omp.json`: overall_status=PASS (L0) -- matches summary
- `rodinia-myocyte-cuda-to-rodinia-myocyte-omp.json`: overall_status=BUILD_FAIL (L0) -- matches summary (myocyte 0/18 PASS, 17 BUILD_FAIL)

**groq-llama-3.3-70b-versatile:**
- `rodinia-backprop-cuda-to-rodinia-backprop-omp.json`: overall_status=BUILD_FAIL (L0) -- consistent (backprop 9 BUILD_FAIL across models)
- `rodinia-bptree-cuda-to-rodinia-bptree-omp.json`: overall_status=PASS (L0) -- matches summary
- `rodinia-hotspot3d-cuda-to-rodinia-hotspot3d-omp.json`: overall_status=PASS (L0) -- matches summary

### Full recount verification
Independently recounted all 504 raw result JSON files (168 per model), excluding 36
kmeans/mummergpu files. Per-model pass counts, per-direction counts, and per-level counts
all match eval_summary.json exactly. **No discrepancies found.**

### Discrepancies found
**NONE.** All numbers in eval_summary.json are verified correct against raw result files.

NOTE: Raw disk has 504 result files (168 per model), not 468. The 36 extra files are
kmeans and mummergpu eval results (KNOWN_FAIL source specs) that eval_summary.json
correctly excludes. 5 of these extra files (claude-sonnet kmeans-cuda-to-omp at L0-L4)
have overall_status=PASS but are correctly excluded since the source spec is KNOWN_FAIL.

## Key Numbers for Cross-Reference

All other agents MUST use these numbers. Any deviation is a bug.

```
SPEC COUNTS:
  Rodinia total:                60
  Rodinia TRUE PASS:            54
  Rodinia KNOWN_FAIL:           6
  XSBench total:                4  (all PASS)
  Non-KNOWN_FAIL PASS:          58
  Eval batch eligible:          57  (excl. xsbench-omp_target)

EVAL TOTALS:
  Models:                       3  (claude-sonnet-4-6, gemini-2.5-flash-lite, groq-llama-3.3-70b-versatile)
  Total tasks (in summary):     468
  Total raw files on disk:      504  (extra 36 = kmeans+mummergpu, excluded from summary)
  Translation directions:       12
  Overall pass rate:            105/468 = 22.44%

PER-MODEL PASS RATES:
  claude-sonnet-4-6:            81/156 = 51.92%
  gemini-2.5-flash-lite:        11/156 = 7.05%
  groq-llama-3.3-70b-versatile: 13/156 = 8.33%

FAILURE BREAKDOWN (468 tasks):
  BUILD_FAIL:                   180 (38.46%)
  RUN_FAIL:                     89  (19.02%)
  EXTRACTION_FAIL:              49  (10.47%)
  VERIFY_FAIL:                  45  (9.62%)

SELF-REPAIR:
  First-attempt PASS:           78
  Repaired by retry:            27
  Total PASS:                   105

AUGMENTATION (Rodinia):
  Level-invariant:              YES
  PASS at L1-L4:                54/60 (all identical)
  Failures at L1-L4:            6/60 (all pre-existing KNOWN_FAIL)

AUGMENTATION (XSBench):
  L2 PASS:                      3/3 (cuda, omp, opencl)
```
