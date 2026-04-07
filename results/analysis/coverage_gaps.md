# Coverage Gaps: GPT-4.1 Mini vs Qwen 3.5 397B

**Generated:** 2026-04-07T00:00:00+00:00
**Phase:** 16-gpt-data-analysis

## Direction Coverage

| Direction | Qwen | GPT | Status |
|-----------|------|-----|--------|
| cuda-to-omp | Y | Y | Both |
| omp-to-cuda | Y | Y | Both |
| cuda-to-opencl | Y | Y | Both |
| opencl-to-cuda | Y | Y | Both |
| omp-to-opencl | Y | Y | Both |
| opencl-to-omp | Y | Y | Both |
| cuda-to-omp_target | Y | Y | Both |
| omp_target-to-cuda | Y | **N** | **GPT missing** |

**Common directions:** 7
**GPT-only directions:** none
**Qwen-only directions:** omp_target-to-cuda

## Impact on Paper

- Cross-model comparison (Section 6.9) covers 7 of 8 directions
- Per-direction tables should use "---" for GPT omp_target-to-cuda cells
- Footnote text: "Cross-model comparison covers 7 of 8 translation directions; omp_target-to-cuda GPT-4.1 mini results were unavailable at submission time."

## Per-Kernel Agreement Summary

From cross_model_comparison.json:
- Both pass: 13 kernels
- Both fail: 5 kernels
- Qwen only pass: 11 kernels
- GPT only pass: 2 kernels
- Total common kernels: 31

## Data Sources

- results/analysis/cross_model_comparison.json
- results/analysis/paper_data.json (Qwen)
- results/analysis/paper_data_gpt41mini.json (GPT)
