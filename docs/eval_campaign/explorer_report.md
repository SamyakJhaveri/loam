# Explorer Report: Definitive Evaluation Gap Matrix

**Generated:** 2026-03-28
**Author:** Explorer Agent (eval-campaign team)

---

## Task 1: Eval-Eligible Translation Pairs

### Spec Inventory

**Rodinia specs (non-KNOWN_FAIL):** 54 specs across 21 kernel slugs

| Kernel | CUDA | OMP | OpenCL | Notes |
|--------|------|-----|--------|-------|
| backprop | Y | Y | Y | All 3 APIs |
| bfs | Y | Y | Y | All 3 APIs |
| bptree | Y | Y | Y | All 3 APIs |
| cfd | Y | Y | Y | All 3 APIs |
| dwt2d | Y | - | Y | No OMP variant |
| gaussian | Y | - | Y | No OMP variant |
| heartwall | Y | Y | Y | All 3 APIs |
| hotspot | Y | Y | Y | All 3 APIs |
| hotspot3d | Y | Y | Y | All 3 APIs |
| huffman | Y | - | - | CUDA only |
| hybridsort | - | - | Y | OpenCL only (CUDA is KNOWN_FAIL) |
| kmeans | - | Y | - | CUDA and OpenCL are KNOWN_FAIL |
| lavamd | Y | Y | Y | All 3 APIs |
| lud | Y | Y | Y | All 3 APIs |
| mummergpu | - | - | - | CUDA and OMP both KNOWN_FAIL |
| myocyte | Y | Y | Y | All 3 APIs |
| nn | Y | Y | - | OpenCL is KNOWN_FAIL |
| nw | Y | Y | Y | All 3 APIs |
| particlefilter | Y | Y | Y | All 3 APIs |
| pathfinder | Y | Y | Y | All 3 APIs |
| srad | Y | Y | Y | All 3 APIs |
| streamcluster | Y | Y | Y | All 3 APIs |

**XSBench specs (standard, excluding omp_target):** 3 specs
- xsbench-xsbench-cuda
- xsbench-xsbench-omp
- xsbench-xsbench-opencl

**KNOWN_FAIL specs (6, excluded from all directions):**
- rodinia-kmeans-cuda (CUDA 12 texture)
- rodinia-mummergpu-cuda (CUDA 12 texture)
- rodinia-mummergpu-omp (uses CUDA kernel)
- rodinia-hybridsort-cuda (GL/glew.h)
- rodinia-nn-opencl (TIMEOUT/SIGSEGV)
- rodinia-kmeans-opencl (SIGSEGV)

### Eligible Kernels Per Direction

| Direction | Rodinia Kernels | XSBench | Total |
|-----------|----------------|---------|-------|
| cuda-to-omp | 16 | 1 | **17** |
| omp-to-cuda | 16 | 1 | **17** |
| cuda-to-opencl | 17 | 1 | **18** |
| opencl-to-cuda | 17 | 1 | **18** |
| omp-to-opencl | 15 | 1 | **16** |
| opencl-to-omp | 15 | 1 | **16** |

**Direction-specific notes:**
- cuda-to-opencl and opencl-to-cuda have 17 Rodinia kernels (not 15) because dwt2d and gaussian have both CUDA and OpenCL but no OMP
- omp-to-opencl and opencl-to-omp have 15 Rodinia kernels (the 13 with all 3 APIs + hotspot, hotspot3d, etc. — all that have both OMP and OpenCL)
- nn is eligible for cuda-to-omp/omp-to-cuda but NOT for any OpenCL direction (nn-opencl is KNOWN_FAIL)

**Rodinia kernels eligible for cuda-to-omp/omp-to-cuda (16):**
backprop, bfs, bptree, cfd, heartwall, hotspot, hotspot3d, lavamd, lud, myocyte, nn, nw, particlefilter, pathfinder, srad, streamcluster

**Additional Rodinia kernels eligible for cuda-to-opencl/opencl-to-cuda (2 more = 17):**
dwt2d, gaussian

**Rodinia kernels eligible for omp-to-opencl/opencl-to-omp (15):**
Same as cuda-to-omp minus nn (since nn-opencl is KNOWN_FAIL)

---

## Task 2: Inventory of Existing Results

### Per-Model Counts (standard 6 directions only)

| Direction | Claude | Gemini | Groq | Total |
|-----------|--------|--------|------|-------|
| cuda-to-omp L0 | 17 | 17 | 17 | 51 |
| cuda-to-omp L1 | 17 | 17 | 17 | 51 |
| cuda-to-omp L2 | 17 | 17 | 17 | 51 |
| cuda-to-omp L3 | 17 | 17 | 17 | 51 |
| cuda-to-omp L4 | 17 | 17 | 17 | 51 |
| **cuda-to-omp subtotal** | **85** | **85** | **85** | **255** |
| omp-to-cuda L0 | 17 | 17 | 17 | 51 |
| omp-to-cuda L1 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| omp-to-cuda L2 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| omp-to-cuda L3 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| omp-to-cuda L4 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| **omp-to-cuda subtotal** | **21** | **21** | **21** | **63** |
| cuda-to-opencl L0 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| cuda-to-opencl L1-L4 | 4 (xsbench) | 4 (xsbench) | 4 (xsbench) | 12 |
| **cuda-to-opencl subtotal** | **5** | **5** | **5** | **15** |
| opencl-to-cuda L0 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| opencl-to-cuda L1-L4 | 4 (xsbench) | 4 (xsbench) | 4 (xsbench) | 12 |
| **opencl-to-cuda subtotal** | **5** | **5** | **5** | **15** |
| omp-to-opencl L0 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| omp-to-opencl L1-L4 | 4 (xsbench) | 4 (xsbench) | 4 (xsbench) | 12 |
| **omp-to-opencl subtotal** | **5** | **5** | **5** | **15** |
| opencl-to-omp L0 | 1 (xsbench) | 1 (xsbench) | 1 (xsbench) | 3 |
| opencl-to-omp L1-L4 | 4 (xsbench) | 4 (xsbench) | 4 (xsbench) | 12 |
| **opencl-to-omp subtotal** | **5** | **5** | **5** | **15** |
| **GRAND TOTAL** | **126** | **126** | **126** | **378** |

**Key finding:** All 3 models have identical file coverage — perfectly symmetric. XSBench is complete for all 6 standard directions at all 5 levels. The gaps are entirely Rodinia kernels in non-cuda-to-omp directions.

### Additional existing results (NOT part of standard 6, case-study only):

All 3 models also have results for 6 omp_target directions (30 files each, 5 levels each). These are case-study data and excluded from the standard eval.

---

## Task 3: Gap Matrix

### Summary

| Direction | Eligible | Done | Missing | % Complete |
|-----------|----------|------|---------|------------|
| cuda-to-omp | 255 | 255 | **0** | 100.0% |
| omp-to-cuda | 255 | 63 | **192** | 24.7% |
| cuda-to-opencl | 270 | 15 | **255** | 5.6% |
| opencl-to-cuda | 270 | 15 | **255** | 5.6% |
| omp-to-opencl | 240 | 15 | **225** | 6.3% |
| opencl-to-omp | 240 | 15 | **225** | 6.3% |
| **TOTAL** | **1530** | **378** | **1152** | **24.7%** |

### Gap Breakdown by Category

**Gap A — omp-to-cuda L1-L4 (Rodinia only):**
- Missing: 16 Rodinia kernels x 4 levels x 3 models = **192 tasks**
- L0 is complete for all models
- XSBench L1-L4 is complete for all models
- These are ALL 16 Rodinia kernels that have both OMP and CUDA variants

**Gap B — cuda-to-opencl (ALL Rodinia):**
- Missing: 17 Rodinia kernels x 5 levels x 3 models = **255 tasks**
- Zero Rodinia results exist for this direction
- XSBench complete at all levels for all models

**Gap C — opencl-to-cuda (ALL Rodinia):**
- Missing: 17 Rodinia kernels x 5 levels x 3 models = **255 tasks**
- Zero Rodinia results exist for this direction
- XSBench complete at all levels for all models

**Gap D — omp-to-opencl (ALL Rodinia):**
- Missing: 15 Rodinia kernels x 5 levels x 3 models = **225 tasks**
- Zero Rodinia results exist for this direction
- XSBench complete at all levels for all models

**Gap E — opencl-to-omp (ALL Rodinia):**
- Missing: 15 Rodinia kernels x 5 levels x 3 models = **225 tasks**
- Zero Rodinia results exist for this direction
- XSBench complete at all levels for all models

### Gap by Level Type

| Gap | L0 Missing | L1-L4 Missing | Total Missing |
|-----|-----------|---------------|---------------|
| omp-to-cuda | 0 | 192 | 192 |
| cuda-to-opencl | 51 | 204 | 255 |
| opencl-to-cuda | 51 | 204 | 255 |
| omp-to-opencl | 45 | 180 | 225 |
| opencl-to-omp | 45 | 180 | 225 |
| **Total** | **192** | **960** | **1152** |

### L0 Gaps Specifically (Most Critical — New Directions)

| Direction | L0 Missing Kernels (per model) | L0 Tasks Missing |
|-----------|-------------------------------|-----------------|
| cuda-to-opencl | 17 Rodinia x 3 models | 51 |
| opencl-to-cuda | 17 Rodinia x 3 models | 51 |
| omp-to-opencl | 15 Rodinia x 3 models | 45 |
| opencl-to-omp | 15 Rodinia x 3 models | 45 |
| **L0 Total** | | **192** |

### L1-L4 Gaps (Augmentation Levels)

| Direction | L1-L4 Missing Kernels (per model per level) | L1-L4 Tasks Missing |
|-----------|---------------------------------------------|---------------------|
| omp-to-cuda | 16 Rodinia x 4 levels x 3 models | 192 |
| cuda-to-opencl | 17 Rodinia x 4 levels x 3 models | 204 |
| opencl-to-cuda | 17 Rodinia x 4 levels x 3 models | 204 |
| omp-to-opencl | 15 Rodinia x 4 levels x 3 models | 180 |
| opencl-to-omp | 15 Rodinia x 4 levels x 3 models | 180 |
| **L1-L4 Total** | | **960** |

---

## Task 4: Retryable Failures (EXTRACTION_FAIL)

**53 total EXTRACTION_FAIL results across all models.** These are in EXISTING result files — they count as "done" in the gap matrix (file exists) but have failed status. They are candidates for deletion + re-run.

### Status Distribution (All 504 existing result files including omp_target)

| Status | Count | % |
|--------|-------|---|
| BUILD_FAIL | 206 | 40.9% |
| PASS | 110 | 21.8% |
| RUN_FAIL | 90 | 17.9% |
| EXTRACTION_FAIL | 53 | 10.5% |
| VERIFY_FAIL | 45 | 8.9% |

### EXTRACTION_FAIL by Model

| Model | Count | In Standard Dirs | In omp_target Dirs |
|-------|-------|-----------------|-------------------|
| Claude | 11 | ~6 | ~5 |
| Gemini | 12 | ~9 | ~3 |
| Groq | 30 | ~10 | ~20 |

### EXTRACTION_FAIL in Standard 6 Directions (retry candidates)

**Claude (6 in standard dirs):**
- rodinia-cfd-omp-to-rodinia-cfd-cuda.json (L0)
- xsbench-xsbench-omp-to-xsbench-xsbench-cuda.json (L0)
- xsbench-xsbench-omp-to-xsbench-xsbench-cuda-L1.json
- xsbench-xsbench-omp-to-xsbench-xsbench-cuda-L2.json
- xsbench-xsbench-omp-to-xsbench-xsbench-cuda-L3.json
- xsbench-xsbench-omp-to-xsbench-xsbench-cuda-L4.json

**Gemini (9 in standard dirs):**
- rodinia-bptree-omp-to-rodinia-bptree-cuda.json (L0)
- rodinia-hotspot3d-cuda-to-rodinia-hotspot3d-omp-L3.json
- rodinia-kmeans-cuda-to-rodinia-kmeans-omp-L4.json (KNOWN_FAIL source, ignore)
- rodinia-lud-omp-to-rodinia-lud-cuda.json (L0)
- rodinia-nw-cuda-to-rodinia-nw-omp.json (L0)
- rodinia-nw-cuda-to-rodinia-nw-omp-L1.json
- rodinia-nw-cuda-to-rodinia-nw-omp-L2.json
- rodinia-nw-cuda-to-rodinia-nw-omp-L4.json
- rodinia-srad-cuda-to-rodinia-srad-omp-L4.json

**Groq (10 in standard dirs):**
- rodinia-cfd-omp-to-rodinia-cfd-cuda.json (L0)
- rodinia-heartwall-cuda-to-rodinia-heartwall-omp-L1.json
- rodinia-heartwall-cuda-to-rodinia-heartwall-omp-L2.json
- rodinia-heartwall-cuda-to-rodinia-heartwall-omp-L4.json
- rodinia-heartwall-omp-to-rodinia-heartwall-cuda.json (L0)
- rodinia-kmeans-omp-to-rodinia-kmeans-cuda.json (L0, KNOWN_FAIL target)
- rodinia-lavamd-cuda-to-rodinia-lavamd-omp-L4.json
- rodinia-lud-cuda-to-rodinia-lud-omp-L1.json
- rodinia-srad-cuda-to-rodinia-srad-omp-L2.json
- rodinia-srad-cuda-to-rodinia-srad-omp-L3.json
- rodinia-srad-cuda-to-rodinia-srad-omp.json (L0)

**EXTRACTION_FAIL retry recommendation:** Delete these files and re-run. The `--resume` flag in `run_eval_batch.py` will skip existing files, so these must be deleted first.

Excluding KNOWN_FAIL-related files, there are approximately **23 standard-direction EXTRACTION_FAIL files** worth retrying.

---

## Task 5: Summary Statistics

### Grand Totals

| Metric | Count |
|--------|-------|
| Total eligible tasks (6 dirs x 5 levels x 3 models) | **1,530** |
| Total DONE (file exists) | **378** |
| Total MISSING (no file) | **1,152** |
| Completion rate | **24.7%** |
| EXTRACTION_FAIL (retryable, in standard dirs) | **~23** |

### Gap Sizes (for Planner scheduling)

| Gap ID | Direction | L0 Missing | L1-L4 Missing | Total | Priority |
|--------|-----------|-----------|---------------|-------|----------|
| A | omp-to-cuda | 0 | 192 | **192** | HIGH (completes bidirectional with cuda-to-omp) |
| B | cuda-to-opencl | 51 | 204 | **255** | HIGH (new direction, largest gap) |
| C | opencl-to-cuda | 51 | 204 | **255** | HIGH (new direction, largest gap) |
| D | omp-to-opencl | 45 | 180 | **225** | MEDIUM |
| E | opencl-to-omp | 45 | 180 | **225** | MEDIUM |

### Per-Direction Batch Sizes (for run_eval_batch.py planning)

Each `run_eval_batch.py` invocation handles one (suite, direction, model) combination.

| Direction | Suite | Kernels | x3 models = L0 tasks | x5 levels x3 models = total tasks |
|-----------|-------|---------|----------------------|-----------------------------------|
| omp-to-cuda | rodinia | 16 | 0 (L0 done) | 192 (L1-L4 only) |
| cuda-to-opencl | rodinia | 17 | 51 | 255 |
| opencl-to-cuda | rodinia | 17 | 51 | 255 |
| omp-to-opencl | rodinia | 15 | 45 | 225 |
| opencl-to-omp | rodinia | 15 | 45 | 225 |

XSBench is 100% complete for all 6 standard directions at all 5 levels for all 3 models.

### What's Complete vs What Needs Work

**COMPLETE (no action needed):**
- cuda-to-omp: ALL 255 tasks (17 kernels x 5 levels x 3 models)
- XSBench: ALL 6 directions x 5 levels x 3 models = 90 tasks
- omp-to-cuda L0: All 17 eligible kernels x 3 models = 51 tasks
- All omp_target directions (case-study, 90 tasks)

**NEEDS WORK:**
- 1,152 missing Rodinia tasks across 5 directions
- ~23 EXTRACTION_FAIL retries across existing results

### Recommended Execution Order

1. **L0 first** across all new directions (192 L0 tasks) — establishes baseline pass rates
2. **omp-to-cuda L1-L4** (192 tasks) — completes the bidirectional pair with fully-done cuda-to-omp
3. **L1-L4 for remaining 4 directions** (768 tasks) — augmentation impact data
4. **EXTRACTION_FAIL retries** (23 tasks) — improve existing data quality

---

## Cross-Validation Checks

1. **Spec count verification:** 60 Rodinia specs on disk, minus 6 KNOWN_FAIL = 54 TRUE PASS. Confirmed.
2. **XSBench count:** 4 specs on disk, minus 1 omp_target = 3 standard. Confirmed.
3. **File counts verified:** `ls | wc -l` for each model directory = 168 files each (including omp_target directions). Confirmed all 3 models have identical file counts.
4. **Gap arithmetic:** 1530 eligible - 378 done = 1152 missing. Verified per-direction sums: 0 + 192 + 255 + 255 + 225 + 225 = 1152. Confirmed.
