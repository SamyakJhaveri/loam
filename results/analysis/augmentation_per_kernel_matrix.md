# Per-Kernel Augmentation Matrix

Generated: 2026-04-04T18:54:51.357491+00:00
Data source: `results/evaluation/together-qwen-3.5-397b-a17b`
Direction: cuda-to-omp
Kernel count: 26

## Per-Kernel Status Table

| Kernel | Suite | L0 | L1 | L2 | L3 | L4 | Pattern | Known Fail |
|--------|-------|----|----|----|----|----|---------|-----------:|
| backprop | rodinia | PASS | PASS | PASS | BUILD_FAIL | BUILD_FAIL | degradation |  |
| bfs | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| bptree | rodinia | BUILD_FAIL | RUN_FAIL | RUN_FAIL | PASS | BUILD_FAIL | improvement |  |
| cfd | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| floydwarshall | hecbench | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| heartwall | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | stable_fail |  |
| heat2d | hecbench | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| hotspot | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| hotspot3d | rodinia | PASS | BUILD_FAIL | PASS | PASS | PASS | degradation |  |
| iso2dfd | hecbench | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| kmeans | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | stable_fail | Yes |
| lavamd | rodinia | PASS | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL | PASS | degradation |  |
| lud | rodinia | PASS | PASS | BUILD_FAIL | RUN_FAIL | PASS | degradation |  |
| mixbench | mixbench | BUILD_FAIL | BUILD_FAIL | PASS | BUILD_FAIL | BUILD_FAIL | improvement |  |
| mummergpu | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | stable_fail | Yes |
| myocyte | rodinia | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | VERIFY_FAIL | BUILD_FAIL | other |  |
| nn | rodinia | BUILD_FAIL | PASS | PASS | BUILD_FAIL | PASS | improvement |  |
| nw | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| particlefilter | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| pathfinder | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| rsbench | rsbench | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | stable_fail |  |
| scan | hecbench | PASS | BUILD_FAIL | PASS | PASS | PASS | degradation |  |
| srad | rodinia | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| stencil1d | hecbench | PASS | PASS | PASS | PASS | PASS | stable_pass |  |
| streamcluster | rodinia | BUILD_FAIL | BUILD_FAIL | PASS | BUILD_FAIL | BUILD_FAIL | improvement |  |
| xsbench | xsbench | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | stable_fail |  |

## Pattern Summary

- **stable_pass** (11): bfs, cfd, floydwarshall, heat2d, hotspot, iso2dfd, nw, particlefilter, pathfinder, srad, stencil1d
- **stable_fail** (5): heartwall, kmeans, mummergpu, rsbench, xsbench
- **degradation** (5): backprop, hotspot3d, lavamd, lud, scan
- **improvement** (4): bptree, mixbench, nn, streamcluster
- **other** (1): myocyte

## Aggregate Pass Rates

### All Kernels

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 16 | 26 | 61.5% | [42.5%, 77.6%] |
| L1 | 14 | 26 | 53.8% | [35.4%, 71.2%] |
| L2 | 16 | 26 | 65.4% | [46.2%, 80.6%] |
| L3 | 14 | 26 | 53.8% | [35.4%, 71.2%] |
| L4 | 16 | 26 | 61.5% | [42.5%, 77.6%] |

### Excluding KNOWN_FAIL

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 16 | 24 | 66.7% | [46.7%, 82.0%] |
| L1 | 13 | 24 | 58.3% | [38.8%, 75.5%] |
| L2 | 16 | 24 | 70.8% | [50.8%, 85.1%] |
| L3 | 13 | 24 | 58.3% | [38.8%, 75.5%] |
| L4 | 16 | 24 | 66.7% | [46.7%, 82.0%] |

## Exceptions

### backprop (rodinia) -- degradation
- L0: PASS
- Affected: L3=BUILD_FAIL, L4=BUILD_FAIL
- Root cause: Linker error: multiple definition of 'gettime' and 'main' -- LLM duplicated functions across files when given augmented source. Augmentation engine validated separately (backprop-cuda PASSES at all harness levels). This is genuine model brittleness, not a transform artifact.

### bptree (rodinia) -- improvement
- L0: BUILD_FAIL
- Affected: L3=PASS
- Root cause: Not yet investigated

### hotspot3d (rodinia) -- degradation
- L0: PASS
- Affected: L1=BUILD_FAIL
- Root cause: Not yet investigated

### lavamd (rodinia) -- degradation
- L0: PASS
- Affected: L1=BUILD_FAIL, L2=BUILD_FAIL, L3=VERIFY_FAIL
- Root cause: Not yet investigated

### lud (rodinia) -- degradation
- L0: PASS
- Affected: L2=BUILD_FAIL, L3=RUN_FAIL
- Root cause: Not yet investigated

### mixbench (mixbench) -- improvement
- L0: BUILD_FAIL
- Affected: L2=PASS
- Root cause: Not yet investigated

### nn (rodinia) -- improvement
- L0: BUILD_FAIL
- Affected: L1=PASS, L2=PASS, L4=PASS
- Root cause: Not yet investigated

### scan (hecbench) -- degradation
- L0: PASS
- Affected: L1=BUILD_FAIL
- Root cause: Not yet investigated

### streamcluster (rodinia) -- improvement
- L0: BUILD_FAIL
- Affected: L2=PASS
- Root cause: Not yet investigated

## Secondary Directions

| Direction | Kernels | L0 Rate | L1 Rate | L2 Rate | L3 Rate | L4 Rate |
|-----------|---------|---------|---------|---------|---------|---------|
| cuda-to-omp | 26 | 61.5% | 53.8% | 65.4% | 53.8% | 61.5% |
| cuda-to-omp_target | 8 | 12.5% | 37.5% | 12.5% | 12.5% | 12.5% |
| cuda-to-opencl | 23 | 17.4% | 21.7% | 21.7% | 13.0% | 13.0% |
| omp-to-cuda | 26 | 53.8% | 46.2% | 46.2% | 53.8% | 42.3% |
| omp-to-opencl | 20 | 30.0% | 20.0% | 30.0% | 30.0% | 15.0% |
| omp_target-to-cuda | 10 | 70.0% | 70.0% | 80.0% | 90.0% | 80.0% |
| opencl-to-cuda | 23 | 8.7% | 8.7% | 4.3% | 4.3% | 0.0% |
| opencl-to-omp | 20 | 35.0% | 30.0% | 35.0% | 40.0% | 35.0% |
