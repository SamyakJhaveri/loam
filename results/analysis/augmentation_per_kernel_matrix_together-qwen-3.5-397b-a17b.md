# Per-Kernel Augmentation Matrix

Generated: 2026-04-24T21:01:46.753461+00:00
Data source: `results/evaluation/together-qwen-3.5-397b-a17b`
Direction: cuda-to-omp
Kernel count: 12

## Per-Kernel Status Table

| Kernel | Suite | L0 | L1 | L2 | L3 | L4 | Pattern | Known Fail |
|--------|-------|----|----|----|----|----|---------|-----------:|
| bfs | rodinia | ? | PASS | PASS | PASS | BUILD_FAIL | improvement |  |
| cfd | rodinia | ? | BUILD_FAIL | PASS | PASS | PASS | improvement |  |
| floydwarshall | hecbench | ? | PASS | PASS | PASS | PASS | improvement |  |
| heat2d | hecbench | ? | PASS | PASS | PASS | PASS | improvement |  |
| hotspot3d | rodinia | ? | PASS | PASS | PASS | PASS | improvement |  |
| iso2dfd | hecbench | ? | PASS | PASS | PASS | PASS | improvement |  |
| lud | rodinia | ? | PASS | PASS | RUN_FAIL | PASS | improvement |  |
| nw | rodinia | ? | PASS | PASS | RUN_FAIL | PASS | improvement |  |
| particlefilter | rodinia | ? | PASS | PASS | PASS | PASS | improvement |  |
| pathfinder | rodinia | ? | BUILD_FAIL | BUILD_FAIL | BUILD_FAIL | PASS | improvement |  |
| srad | rodinia | ? | PASS | PASS | PASS | PASS | improvement |  |
| stencil1d | hecbench | ? | BUILD_FAIL | VERIFY_FAIL | PASS | VERIFY_FAIL | improvement |  |

## Pattern Summary

- **stable_pass** (0): none
- **stable_fail** (0): none
- **degradation** (0): none
- **improvement** (12): bfs, cfd, floydwarshall, heat2d, hotspot3d, iso2dfd, lud, nw, particlefilter, pathfinder, srad, stencil1d
- **other** (0): none

## Aggregate Pass Rates

### All Kernels

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L1 | 9 | 12 | 75.0% | [46.8%, 91.1%] |
| L2 | 10 | 12 | 83.3% | [55.2%, 95.3%] |
| L3 | 9 | 12 | 75.0% | [46.8%, 91.1%] |
| L4 | 10 | 12 | 83.3% | [55.2%, 95.3%] |

### Excluding KNOWN_FAIL

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L1 | 9 | 12 | 75.0% | [46.8%, 91.1%] |
| L2 | 10 | 12 | 83.3% | [55.2%, 95.3%] |
| L3 | 9 | 12 | 75.0% | [46.8%, 91.1%] |
| L4 | 10 | 12 | 83.3% | [55.2%, 95.3%] |

## Exceptions

### bfs (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS
- Root cause: Not yet investigated

### cfd (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### floydwarshall (hecbench) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### heat2d (hecbench) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### hotspot3d (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### iso2dfd (hecbench) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### lud (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L4=PASS
- Root cause: Not yet investigated

### nw (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L4=PASS
- Root cause: Not yet investigated

### particlefilter (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### pathfinder (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L4=PASS
- Root cause: Not yet investigated

### srad (rodinia) -- improvement
- L0: UNKNOWN
- Affected: L1=PASS, L2=PASS, L3=PASS, L4=PASS
- Root cause: Not yet investigated

### stencil1d (hecbench) -- improvement
- L0: UNKNOWN
- Affected: L3=PASS
- Root cause: Not yet investigated

## Secondary Directions

| Direction | Kernels | L0 Rate | L1 Rate | L2 Rate | L3 Rate | L4 Rate |
|-----------|---------|---------|---------|---------|---------|---------|
| cuda-to-omp | 12 | 0.0% | 75.0% | 83.3% | 75.0% | 83.3% |
| cuda-to-opencl | 3 | 0.0% | 0.0% | 66.7% | 33.3% | 33.3% |
| omp-to-cuda | 8 | 0.0% | 75.0% | 75.0% | 62.5% | 50.0% |
| omp-to-omp_target | 3 | 0.0% | 100.0% | 66.7% | 33.3% | 33.3% |
| omp-to-opencl | 10 | 0.0% | 80.0% | 40.0% | 50.0% | 30.0% |
| omp_target-to-cuda | 8 | 0.0% | 87.5% | 75.0% | 75.0% | 62.5% |
| omp_target-to-omp | 3 | 0.0% | 100.0% | 100.0% | 66.7% | 100.0% |
| opencl-to-omp | 4 | 0.0% | 50.0% | 0.0% | 75.0% | 25.0% |
