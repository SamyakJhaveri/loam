# Self-Repair Analysis — ParBench Evaluation

**1018 total results**: 547 single-attempt, 471 multi-attempt (needed retry).

Of 471 retried translations:
- **91** (19.3%) achieved full repair (reached PASS)
- **53** (11.3%) showed partial improvement
- **321** (68.2%) showed no change
- **6** (1.3%) regressed to a worse status

## Table 1: Per-Model Self-Repair

| Model | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate | Improvement Rate |
|-------|-------------:|------------:|--------:|----------:|-----------:|------------:|-----------------:|
| Qwen 3.5 397B (Together) | 471 | 91 | 53 | 321 | 6 | 19.3% | 30.6% |

## Table 2: By Initial Failure Type

| Initial Failure | Count | Full Repair | Partial | No Change | Regression | Repair Rate |
|-----------------|------:|------------:|--------:|----------:|-----------:|------------:|
| EXTRACTION_FAIL | 27 | 15 | 12 | 0 | 0 | 55.6% |
| BUILD_FAIL | 274 | 55 | 39 | 179 | 1 | 20.1% |
| RUN_FAIL | 128 | 14 | 1 | 112 | 1 | 10.9% |
| VERIFY_FAIL | 36 | 6 | 0 | 30 | 0 | 16.7% |
| OTHER | 1 | 0 | 1 | 0 | 0 | 0.0% |

## Table 3: Per-Kernel Self-Repair (sorted by repair rate)

| Kernel | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate |
|--------|-------------:|------------:|--------:|----------:|-----------:|------------:|
| hotspot | 23 | 14 | 5 | 4 | 0 | 60.9% |
| hotspot3d | 21 | 10 | 2 | 9 | 0 | 47.6% |
| cfd | 24 | 10 | 2 | 12 | 0 | 41.7% |
| particlefilter | 21 | 8 | 7 | 6 | 0 | 38.1% |
| pathfinder | 24 | 9 | 4 | 11 | 0 | 37.5% |
| nw | 22 | 7 | 0 | 15 | 0 | 31.8% |
| bfs | 20 | 6 | 2 | 12 | 0 | 30.0% |
| lud | 21 | 6 | 2 | 13 | 0 | 28.6% |
| srad | 24 | 6 | 2 | 16 | 0 | 25.0% |
| nn | 30 | 7 | 10 | 12 | 1 | 23.3% |
| backprop | 25 | 4 | 1 | 16 | 4 | 16.0% |
| bptree | 28 | 2 | 4 | 22 | 0 | 7.1% |
| lavamd | 29 | 1 | 3 | 25 | 0 | 3.5% |
| streamcluster | 29 | 1 | 2 | 26 | 0 | 3.5% |
| dwt2d | 10 | 0 | 0 | 9 | 1 | 0.0% |
| gaussian | 10 | 0 | 3 | 7 | 0 | 0.0% |
| heartwall | 30 | 0 | 1 | 29 | 0 | 0.0% |
| hybridsort | 10 | 0 | 1 | 9 | 0 | 0.0% |
| kmeans | 30 | 0 | 0 | 30 | 0 | 0.0% |
| mummergpu | 10 | 0 | 0 | 10 | 0 | 0.0% |
| myocyte | 30 | 0 | 2 | 28 | 0 | 0.0% |

## Table 4: Token Overhead from Self-Repair

| Metric | Value |
|--------|------:|
| Total extra prompt tokens | 27,024,023 |
| Total extra completion tokens | 5,696,653 |
| Total extra tokens (all retries) | 32,720,676 |
| Mean extra tokens per retry | 69,471 |
| Full-repair extra prompt tokens | 1,891,091 |
| Full-repair extra completion tokens | 436,157 |

## Table 5: Repair Trajectory Patterns

| Trajectory | Count | % of Multi-Attempt |
|------------|------:|-------------------:|
| BUILD_FAIL → BUILD_FAIL → BUILD_FAIL | 177 | 37.6% |
| RUN_FAIL → RUN_FAIL → RUN_FAIL | 112 | 23.8% |
| BUILD_FAIL → PASS | 39 | 8.3% |
| VERIFY_FAIL → VERIFY_FAIL → VERIFY_FAIL | 30 | 6.4% |
| BUILD_FAIL → BUILD_FAIL → PASS | 14 | 3.0% |
| BUILD_FAIL → VERIFY_FAIL → VERIFY_FAIL | 12 | 2.5% |
| RUN_FAIL → PASS | 10 | 2.1% |
| BUILD_FAIL → BUILD_FAIL → VERIFY_FAIL | 8 | 1.7% |
| EXTRACTION_FAIL → BUILD_FAIL → PASS | 8 | 1.7% |
| BUILD_FAIL → BUILD_FAIL → RUN_FAIL | 6 | 1.3% |
| EXTRACTION_FAIL → EXTRACTION_FAIL → VERIFY_FAIL | 6 | 1.3% |
| BUILD_FAIL → RUN_FAIL → RUN_FAIL | 5 | 1.1% |
| VERIFY_FAIL → PASS | 5 | 1.1% |
| BUILD_FAIL → OTHER → OTHER | 5 | 1.1% |
| PASS → PASS → PASS | 4 | 0.8% |

## Interpretation

Self-repair (retry with error feedback) converts failing translations to PASS.
The repair rate varies by initial failure type: BUILD_FAIL errors are generally
more amenable to repair than RUN_FAIL (which often indicates deeper algorithmic
issues). EXTRACTION_FAIL can be repaired by reformatting the response.

Partial repairs (e.g., BUILD_FAIL → RUN_FAIL) show the LLM understood the
build error and fixed it, but introduced a runtime issue. This demonstrates
iterative improvement capability even when full repair isn't achieved.

