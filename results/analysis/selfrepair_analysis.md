# Self-Repair Analysis — ParBench Evaluation

**1248 total results**: 624 single-attempt, 624 multi-attempt (needed retry).

Of 624 retried translations:
- **117** (18.8%) achieved full repair (reached PASS)
- **63** (10.1%) showed partial improvement
- **440** (70.5%) showed no change
- **4** (0.6%) regressed to a worse status

## Table 1: Per-Model Self-Repair

| Model | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate | Improvement Rate |
|-------|-------------:|------------:|--------:|----------:|-----------:|------------:|-----------------:|
| Qwen 3.5 397B (Together) | 624 | 117 | 63 | 440 | 4 | 18.8% | 28.8% |

## Table 2: By Initial Failure Type

| Initial Failure | Count | Full Repair | Partial | No Change | Regression | Repair Rate |
|-----------------|------:|------------:|--------:|----------:|-----------:|------------:|
| EXTRACTION_FAIL | 27 | 15 | 12 | 0 | 0 | 55.6% |
| BUILD_FAIL | 391 | 72 | 48 | 270 | 1 | 18.4% |
| RUN_FAIL | 162 | 17 | 2 | 140 | 3 | 10.5% |
| VERIFY_FAIL | 38 | 8 | 0 | 30 | 0 | 21.1% |
| OTHER | 1 | 0 | 1 | 0 | 0 | 0.0% |

## Table 3: Per-Kernel Self-Repair (sorted by repair rate)

| Kernel | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate |
|--------|-------------:|------------:|--------:|----------:|-----------:|------------:|
| stencil1d | 1 | 1 | 0 | 0 | 0 | 100.0% |
| hotspot | 23 | 14 | 5 | 4 | 0 | 60.9% |
| iso2dfd | 10 | 5 | 1 | 4 | 0 | 50.0% |
| hotspot3d | 21 | 10 | 2 | 9 | 0 | 47.6% |
| jacobi | 7 | 3 | 1 | 3 | 0 | 42.9% |
| nqueen | 7 | 3 | 3 | 1 | 0 | 42.9% |
| cfd | 24 | 10 | 2 | 12 | 0 | 41.7% |
| particlefilter | 21 | 8 | 7 | 6 | 0 | 38.1% |
| pathfinder | 24 | 9 | 4 | 11 | 0 | 37.5% |
| md | 6 | 2 | 0 | 4 | 0 | 33.3% |
| backprop | 25 | 8 | 1 | 16 | 0 | 32.0% |
| nw | 22 | 7 | 0 | 15 | 0 | 31.8% |
| bfs | 20 | 6 | 2 | 12 | 0 | 30.0% |
| lud | 21 | 6 | 2 | 13 | 0 | 28.6% |
| srad | 24 | 6 | 2 | 16 | 0 | 25.0% |
| nn | 30 | 7 | 10 | 12 | 1 | 23.3% |
| mixbench | 28 | 6 | 0 | 22 | 0 | 21.4% |
| page-rank | 5 | 1 | 0 | 2 | 2 | 20.0% |
| scan | 11 | 1 | 2 | 8 | 0 | 9.1% |
| bptree | 28 | 2 | 4 | 22 | 0 | 7.1% |
| lavamd | 29 | 1 | 3 | 25 | 0 | 3.5% |
| streamcluster | 29 | 1 | 2 | 26 | 0 | 3.5% |
| convolution1d | 10 | 0 | 1 | 9 | 0 | 0.0% |
| dwt2d | 10 | 0 | 0 | 9 | 1 | 0.0% |
| floydwarshall | 4 | 0 | 2 | 2 | 0 | 0.0% |
| gaussian | 10 | 0 | 3 | 7 | 0 | 0.0% |
| heartwall | 30 | 0 | 1 | 29 | 0 | 0.0% |
| heat2d | 5 | 0 | 0 | 5 | 0 | 0.0% |
| hybridsort | 10 | 0 | 1 | 9 | 0 | 0.0% |
| kmeans | 30 | 0 | 0 | 30 | 0 | 0.0% |
| mummergpu | 10 | 0 | 0 | 10 | 0 | 0.0% |
| myocyte | 30 | 0 | 2 | 28 | 0 | 0.0% |
| rsbench | 29 | 0 | 0 | 29 | 0 | 0.0% |
| xsbench | 30 | 0 | 0 | 30 | 0 | 0.0% |

## Table 4: Token Overhead from Self-Repair

| Metric | Value |
|--------|------:|
| Total extra prompt tokens | 32,383,944 |
| Total extra completion tokens | 6,722,576 |
| Total extra tokens (all retries) | 39,106,520 |
| Mean extra tokens per retry | 62,671 |
| Full-repair extra prompt tokens | 2,286,403 |
| Full-repair extra completion tokens | 514,646 |

## Table 5: Repair Trajectory Patterns

| Trajectory | Count | % of Multi-Attempt |
|------------|------:|-------------------:|
| BUILD_FAIL → BUILD_FAIL → BUILD_FAIL | 264 | 42.3% |
| RUN_FAIL → RUN_FAIL → RUN_FAIL | 140 | 22.4% |
| BUILD_FAIL → PASS | 47 | 7.5% |
| VERIFY_FAIL → VERIFY_FAIL → VERIFY_FAIL | 30 | 4.8% |
| BUILD_FAIL → BUILD_FAIL → PASS | 23 | 3.7% |
| BUILD_FAIL → VERIFY_FAIL → VERIFY_FAIL | 13 | 2.1% |
| RUN_FAIL → PASS | 11 | 1.8% |
| BUILD_FAIL → BUILD_FAIL → RUN_FAIL | 10 | 1.6% |
| BUILD_FAIL → BUILD_FAIL → VERIFY_FAIL | 10 | 1.6% |
| EXTRACTION_FAIL → BUILD_FAIL → PASS | 8 | 1.3% |
| BUILD_FAIL → RUN_FAIL → RUN_FAIL | 7 | 1.1% |
| VERIFY_FAIL → PASS | 6 | 1.0% |
| RUN_FAIL → RUN_FAIL → PASS | 6 | 1.0% |
| EXTRACTION_FAIL → EXTRACTION_FAIL → VERIFY_FAIL | 6 | 1.0% |
| BUILD_FAIL → OTHER → OTHER | 5 | 0.8% |

## Interpretation

Self-repair (retry with error feedback) converts failing translations to PASS.
The repair rate varies by initial failure type: BUILD_FAIL errors are generally
more amenable to repair than RUN_FAIL (which often indicates deeper algorithmic
issues). EXTRACTION_FAIL can be repaired by reformatting the response.

Partial repairs (e.g., BUILD_FAIL → RUN_FAIL) show the LLM understood the
build error and fixed it, but introduced a runtime issue. This demonstrates
iterative improvement capability even when full repair isn't achieved.

