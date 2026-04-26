# Per-Kernel Augmentation Matrix

Generated: 2026-04-25T23:01:53.491605+00:00
Data source: `results/evaluation/azure-gpt-5.4`
Direction: cuda-to-omp
Kernel count: 10

## Per-Kernel Status Table

| Kernel | Suite | L0 | L1 | L2 | L3 | L4 | Pattern | Known Fail |
|--------|-------|----|----|----|----|----|---------|-----------:|
| backprop | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| bfs | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| bptree | rodinia | BUILD_FAIL | ? | ? | ? | ? | other |  |
| cfd | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| heartwall | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| hotspot | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| hotspot3d | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| lavamd | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| lud | rodinia | PASS | ? | ? | ? | ? | degradation |  |
| myocyte | rodinia | BUILD_FAIL | ? | ? | ? | ? | other |  |

## Pattern Summary

- **stable_pass** (0): none
- **stable_fail** (0): none
- **degradation** (8): backprop, bfs, cfd, heartwall, hotspot, hotspot3d, lavamd, lud
- **improvement** (0): none
- **other** (2): bptree, myocyte

## Aggregate Pass Rates

### All Kernels

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 8 | 10 | 80.0% | [49.0%, 94.3%] |
| L1 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L2 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L3 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L4 | 0 | 0 | 0.0% | [0.0%, 0.0%] |

### Excluding KNOWN_FAIL

| Level | Pass | Total | Rate | 95% CI |
|-------|------|-------|------|--------|
| L0 | 8 | 10 | 80.0% | [49.0%, 94.3%] |
| L1 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L2 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L3 | 0 | 0 | 0.0% | [0.0%, 0.0%] |
| L4 | 0 | 0 | 0.0% | [0.0%, 0.0%] |

## Exceptions

### backprop (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Linker error: multiple definition of 'gettime' and 'main' -- LLM duplicated functions across files when given augmented source. Augmentation engine validated separately (backprop-cuda PASSES at all harness levels). This is genuine model brittleness, not a transform artifact.

### bfs (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### cfd (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### heartwall (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### hotspot (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### hotspot3d (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### lavamd (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

### lud (rodinia) -- degradation
- L0: PASS
- Affected: L1=UNKNOWN, L2=UNKNOWN, L3=UNKNOWN, L4=UNKNOWN
- Root cause: Not yet investigated

## Secondary Directions

| Direction | Kernels | L0 Rate | L1 Rate | L2 Rate | L3 Rate | L4 Rate |
|-----------|---------|---------|---------|---------|---------|---------|
