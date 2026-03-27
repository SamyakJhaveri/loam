# SLoC Characterization of ParBench Evaluated Kernels

**18 kernels** analyzed from Rodinia (17) + XSBench (1).
Physical SLoC = non-blank, non-comment lines (matches cloc methodology).
Source: actual CUDA source files from the benchmark repositories.

## Per-Kernel SLoC

| Kernel | Category | CUDA SLoC | CUDA Files | OMP SLoC | OMP Files | Complexity | Pass Rate |
|--------|----------|----------:|----------:|---------:|----------:|------------|----------:|
| myocyte | other | 3,304 | 16 | 1806 | 10 | multi_to_multi | 10.5% |
| cfd | physics | 1,955 | 4 | 400 | 1 | multi_to_single | 36.8% |
| xsbench | physics | 1,390 | 6 | 1238 | 6 | multi_to_multi | 26.7% |
| heartwall | image | 1,046 | 3 | 837 | 3 | multi_to_multi | 0.0% |
| particlefilter | physics | 1,023 | 2 | 400 | 1 | multi_to_single | 42.1% |
| srad | image | 391 | 2 | 173 | 1 | multi_to_single | 0.0% |
| streamcluster | other | 372 | 2 | 981 | 1 | multi_to_single | 26.3% |
| bptree | other | 327 | 5 | 1721 | 3 | multi_to_multi | 36.8% |
| nw | other | 319 | 2 | 291 | 1 | multi_to_single | 0.0% |
| kmeans | ml | 299 | 2 | 1048 | 4 | multi_to_single | 43.8% |
| lud | linear_algebra | 271 | 2 | 400 | 3 | multi_to_single | 52.6% |
| nn | graph | 259 | 1 | 111 | 1 | single_file | 68.4% |
| hotspot3d | physics | 246 | 2 | 206 | 1 | multi_to_single | 68.4% |
| hotspot | physics | 243 | 1 | 262 | 1 | single_file | 0.0% |
| bfs | graph | 242 | 3 | 144 | 1 | multi_to_single | 63.2% |
| lavamd | molecular_dynamics | 200 | 3 | 258 | 2 | multi_to_single | 63.2% |
| backprop | ml | 197 | 2 | 449 | 4 | multi_to_single | 57.9% |
| pathfinder | graph | 195 | 1 | 103 | 1 | single_file | 73.7% |

## Summary Statistics

| Metric | Value |
|--------|------:|
| Min SLoC | 195 |
| Max SLoC | 3,304 |
| Mean SLoC | 682.2 |
| Median SLoC | 309 |
| Std Dev | 797.9 |
| Total SLoC (all kernels) | 12,279 |

## SLoC Distribution

| Range | Count |
|-------|------:|
| <100 | 0 |
| 100-500 | 13 |
| 500-1000 | 0 |
| >1000 | 5 |

## ParEval-Repo Comparison

ParEval-Repo uses functions averaging ~133 SLoC (single-function snippets).
ParBench evaluates **full application kernels** with real build systems.

- **18/18** (100.0%) of ParBench kernels exceed ParEval-Repo's 133-SLoC average
- ParBench median: **309 SLoC** (2.3x ParEval-Repo)
- ParBench range: **195** to **3,304** SLoC

## SLoC vs. Pass Rate Correlation

Spearman rank correlation (SLoC vs. overall pass rate): **-0.6347**

Negative correlation suggests larger kernels are harder to translate correctly.
