# Self-Repair Analysis — ParBench Evaluation

**500 total results**: 135 single-attempt, 365 multi-attempt (needed retry).

Of 365 retried translations:
- **35** (9.6%) achieved full repair (reached PASS)
- **56** (15.3%) showed partial improvement
- **242** (66.3%) showed no change
- **32** (8.8%) regressed to a worse status

## Table 1: Per-Model Self-Repair

| Model | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate | Improvement Rate |
|-------|-------------:|------------:|--------:|----------:|-----------:|------------:|-----------------:|
| Claude Sonnet 4 | 65 | 17 | 1 | 47 | 0 | 26.2% | 27.7% |
| Gemini 2.5 Flash-Lite | 148 | 4 | 44 | 92 | 8 | 2.7% | 32.4% |
| Groq Llama 3.3 70B | 142 | 12 | 8 | 98 | 24 | 8.5% | 14.1% |
| Azure GPT-4.1 | 10 | 2 | 3 | 5 | 0 | 20.0% | 50.0% |

## Table 2: By Initial Failure Type

| Initial Failure | Count | Full Repair | Partial | No Change | Regression | Repair Rate |
|-----------------|------:|------------:|--------:|----------:|-----------:|------------:|
| EXTRACTION_FAIL | 57 | 0 | 40 | 17 | 0 | 0.0% |
| BUILD_FAIL | 215 | 26 | 16 | 164 | 9 | 12.1% |
| RUN_FAIL | 93 | 9 | 0 | 61 | 23 | 9.7% |

## Table 3: Per-Kernel Self-Repair (sorted by repair rate)

| Kernel | Multi-Attempt | Full Repair | Partial | No Change | Regression | Repair Rate |
|--------|-------------:|------------:|--------:|----------:|-----------:|------------:|
| nn | 14 | 8 | 2 | 4 | 0 | 57.1% |
| pathfinder | 9 | 4 | 0 | 2 | 3 | 44.4% |
| lavamd | 9 | 2 | 0 | 5 | 2 | 22.2% |
| bptree | 14 | 2 | 4 | 8 | 0 | 14.3% |
| hotspot3d | 7 | 1 | 0 | 5 | 1 | 14.3% |
| bfs | 8 | 1 | 0 | 6 | 1 | 12.5% |
| streamcluster | 16 | 2 | 0 | 14 | 0 | 12.5% |
| kmeans | 10 | 1 | 0 | 6 | 3 | 10.0% |
| xsbench | 143 | 12 | 28 | 90 | 13 | 8.4% |
| particlefilter | 12 | 1 | 0 | 11 | 0 | 8.3% |
| myocyte | 18 | 1 | 4 | 13 | 0 | 5.6% |
| backprop | 8 | 0 | 0 | 8 | 0 | 0.0% |
| cfd | 12 | 0 | 0 | 12 | 0 | 0.0% |
| heartwall | 19 | 0 | 6 | 12 | 1 | 0.0% |
| hotspot | 19 | 0 | 5 | 12 | 2 | 0.0% |
| lud | 9 | 0 | 2 | 6 | 1 | 0.0% |
| nw | 19 | 0 | 4 | 15 | 0 | 0.0% |
| srad | 19 | 0 | 1 | 13 | 5 | 0.0% |

## Table 4: Token Overhead from Self-Repair

| Metric | Value |
|--------|------:|
| Total extra prompt tokens | 11,194,810 |
| Total extra completion tokens | 2,297,938 |
| Total extra tokens (all retries) | 13,492,748 |
| Mean extra tokens per retry | 36,966 |
| Full-repair extra prompt tokens | 833,667 |
| Full-repair extra completion tokens | 185,539 |

## Interpretation

Self-repair (retry with error feedback) converts failing translations to PASS.
The repair rate varies by initial failure type: BUILD_FAIL errors are generally
more amenable to repair than RUN_FAIL (which often indicates deeper algorithmic
issues). EXTRACTION_FAIL can be repaired by reformatting the response.

Partial repairs (e.g., BUILD_FAIL → RUN_FAIL) show the LLM understood the
build error and fixed it, but introduced a runtime issue. This demonstrates
iterative improvement capability even when full repair isn't achieved.

