# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 708  
**PASS:** 251 (35.5%)  
**Failures:** 457 (64.5%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 251 | 35.5% |
| BUILD_FAIL | 291 | 41.1% |
| RUN_FAIL | 125 | 17.7% |
| VERIFY_FAIL | 40 | 5.6% |
| EXTRACTION_FAIL | 1 | 0.1% |
| ERROR | 0 | 0.0% |
| **Total** | **708** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*291 total BUILD_FAIL results classified into 11 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `other_build` | 75 | 25.8% | Build failures not matching any specific pattern |
| 2 | `missing_header` | 66 | 22.7% | Missing or wrong #include directive — file not found |
| 3 | `undeclared_identifier` | 59 | 20.3% | Function, variable, or type not declared/defined in scope |
| 4 | `linker_error` | 39 | 13.4% | Compilation succeeded but linking failed (undefined references, etc.) |
| 5 | `syntax_error` | 18 | 6.2% | Parse errors, malformed code, unexpected tokens |
| 6 | `missing_target_api` | 16 | 5.5% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 7 | `type_mismatch` | 7 | 2.4% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `retained_cuda_types` | 4 | 1.4% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 9 | `redefinition` | 4 | 1.4% | Duplicate or conflicting definitions of types/functions/variables |
| 10 | `implicit_declaration` | 2 | 0.7% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 11 | `retained_opencl_api` | 1 | 0.3% | LLM retained OpenCL API calls in non-OpenCL target code |
| | **Total** | **291** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*125 total RUN_FAIL results classified into 4 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `opencl_jit_error` | 56 | 44.8% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 2 | `wrong_exit_code` | 36 | 28.8% | Non-zero exit code without crash signal or other specific error pattern |
| 3 | `segfault` | 18 | 14.4% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 4 | `wrong_checksum` | 15 | 12.0% | Program ran to completion but output checksum was incorrect |
| | **Total** | **125** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*1 total EXTRACTION_FAIL results classified into 1 category.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `missing_files` | 1 | 100.0% | Expected output files not found in LLM response |
| | **Total** | **1** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*40 total VERIFY_FAIL results classified into 2 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 34 | 85.0% | Program produced output that did not match the expected stdout pattern |
| 2 | `pass_overall_mislabel` | 6 | 15.0% | Verify passed but overall_status is VERIFY_FAIL (pipeline labeling bug) |
| | **Total** | **40** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `other_build` | 75 | 75 |
| `missing_header` | 66 | 66 |
| `undeclared_identifier` | 59 | 59 |
| `linker_error` | 39 | 39 |
| `syntax_error` | 18 | 18 |
| `missing_target_api` | 16 | 16 |
| `type_mismatch` | 7 | 7 |
| `retained_cuda_types` | 4 | 4 |
| `redefinition` | 4 | 4 |
| `implicit_declaration` | 2 | 2 |
| `retained_opencl_api` | 1 | 1 |
| **Total** | **291** | **291** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | omp→cuda | opencl→cuda | opencl→omp | cuda→omp | cuda→omp_target | omp_target→cuda | omp→omp_target | omp_target→omp | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| `other_build` | 20 | 5 | 3 | 7 | 19 | 10 | 9 | 2 | 75 |
| `missing_header` | 12 | 26 | 11 | 17 | 0 | 0 | 0 | 0 | 66 |
| `undeclared_identifier` | 13 | 14 | 19 | 10 | 3 | 0 | 0 | 0 | 59 |
| `linker_error` | 9 | 15 | 8 | 7 | 0 | 0 | 0 | 0 | 39 |
| `syntax_error` | 0 | 1 | 0 | 2 | 5 | 9 | 1 | 0 | 18 |
| `missing_target_api` | 7 | 4 | 2 | 3 | 0 | 0 | 0 | 0 | 16 |
| `type_mismatch` | 0 | 0 | 6 | 1 | 0 | 0 | 0 | 0 | 7 |
| `retained_cuda_types` | 0 | 0 | 3 | 0 | 1 | 0 | 0 | 0 | 4 |
| `redefinition` | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| `implicit_declaration` | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `retained_opencl_api` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **66** | **66** | **53** | **47** | **28** | **19** | **10** | **2** | **291** |

## Table 7: RUN_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `opencl_jit_error` | 56 | 56 |
| `wrong_exit_code` | 36 | 36 |
| `segfault` | 18 | 18 |
| `wrong_checksum` | 15 | 15 |
| **Total** | **125** | **125** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| together-qwen-3.5-397b-a17b | 708 | 251 | 291 | 125 | 40 | 1 | 0 | 35.5% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 126 | 71 | 47 | 5 | 3 | 0 | 0 | 56.3% |
| cuda→omp_target | 30 | 0 | 28 | 2 | 0 | 0 | 0 | 0.0% |
| cuda→opencl | 81 | 5 | 0 | 64 | 12 | 0 | 0 | 6.2% |
| omp→cuda | 110 | 41 | 66 | 1 | 1 | 1 | 0 | 37.3% |
| omp→omp_target | 27 | 13 | 10 | 1 | 3 | 0 | 0 | 48.1% |
| omp→opencl | 100 | 44 | 0 | 44 | 12 | 0 | 0 | 44.0% |
| omp_target→cuda | 62 | 42 | 19 | 0 | 1 | 0 | 0 | 67.7% |
| omp_target→omp | 27 | 23 | 2 | 0 | 2 | 0 | 0 | 85.2% |
| opencl→cuda | 69 | 1 | 66 | 2 | 0 | 0 | 0 | 1.4% |
| opencl→omp | 76 | 11 | 53 | 6 | 6 | 0 | 0 | 14.5% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 22 | 4 | 18.2% | `undeclared_identifier` | 6 |
| bfs | 34 | 17 | 50.0% | `segfault` | 7 |
| bptree | 18 | 0 | 0.0% | `missing_header` | 9 |
| cfd | 22 | 7 | 31.8% | `wrong_numerical_output` | 6 |
| convolution1d | 10 | 2 | 20.0% | `other_build` | 8 |
| dwt2d | 6 | 0 | 0.0% | `segfault` | 3 |
| floydwarshall | 38 | 31 | 81.6% | `other_build` | 5 |
| gaussian | 6 | 0 | 0.0% | `wrong_exit_code` | 4 |
| heartwall | 18 | 0 | 0.0% | `missing_header` | 7 |
| heat2d | 38 | 29 | 76.3% | `other_build` | 4 |
| hotspot | 30 | 15 | 50.0% | `undeclared_identifier` | 6 |
| hotspot3d | 34 | 19 | 55.9% | `linker_error` | 5 |
| hybridsort | 6 | 0 | 0.0% | `missing_header` | 3 |
| iso2dfd | 38 | 32 | 84.2% | `other_build` | 4 |
| jacobi | 10 | 1 | 10.0% | `syntax_error` | 7 |
| kmeans | 18 | 0 | 0.0% | `wrong_numerical_output` | 6 |
| lavamd | 18 | 0 | 0.0% | `missing_header` | 11 |
| lud | 30 | 14 | 46.7% | `other_build` | 4 |
| md | 10 | 5 | 50.0% | `other_build` | 3 |
| mixbench | 22 | 3 | 13.6% | `wrong_exit_code` | 6 |
| mummergpu | 6 | 0 | 0.0% | `other_build` | 4 |
| myocyte | 18 | 0 | 0.0% | `missing_header` | 8 |
| nn | 18 | 1 | 5.6% | `missing_header` | 6 |
| nqueen | 10 | 6 | 60.0% | `other_build` | 3 |
| nw | 30 | 12 | 40.0% | `linker_error` | 6 |
| page-rank | 10 | 6 | 60.0% | `other_build` | 3 |
| particlefilter | 26 | 9 | 34.6% | `missing_header` | 7 |
| pathfinder | 30 | 10 | 33.3% | `undeclared_identifier` | 10 |
| rsbench | 18 | 0 | 0.0% | `wrong_checksum` | 6 |
| scan | 18 | 2 | 11.1% | `other_build` | 8 |
| srad | 26 | 9 | 34.6% | `opencl_jit_error` | 6 |
| stencil1d | 26 | 15 | 57.7% | `other_build` | 6 |
| streamcluster | 22 | 1 | 4.5% | `undeclared_identifier` | 6 |
| xsbench | 22 | 1 | 4.5% | `wrong_checksum` | 9 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`other_build`** — 75 (25.8% of BUILD_FAIL)
2. **`missing_header`** — 66 (22.7% of BUILD_FAIL)
3. **`undeclared_identifier`** — 59 (20.3% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`opencl_jit_error`** — 56 (44.8% of RUN_FAIL)
2. **`wrong_exit_code`** — 36 (28.8% of RUN_FAIL)
3. **`segfault`** — 18 (14.4% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 34 (85.0% of VERIFY_FAIL)
2. **`pass_overall_mislabel`** — 6 (15.0% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 71/126 PASS (56.3%)
- cuda→omp_target: 0/30 PASS (0.0%)
- cuda→opencl: 5/81 PASS (6.2%)
- omp→cuda: 41/110 PASS (37.3%)
- omp→omp_target: 13/27 PASS (48.1%)
- omp→opencl: 44/100 PASS (44.0%)
- omp_target→cuda: 42/62 PASS (67.7%)
- omp_target→omp: 23/27 PASS (85.2%)
- opencl→cuda: 1/69 PASS (1.4%)
- opencl→omp: 11/76 PASS (14.5%)

### Compound Failures (Multiple Root Causes)

**105** results (23.0% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 24 |
| wrong_checksum + opencl_jit_error | 15 |
| missing_header + undeclared_identifier | 12 |
| undeclared_identifier + syntax_error | 9 |
| missing_target_api + undeclared_identifier | 9 |
| missing_target_api + linker_error | 7 |
| missing_header + linker_error | 7 |
| undeclared_identifier + redefinition | 7 |
| opencl_jit_error + data_file_missing | 5 |
| linker_error + implicit_declaration | 4 |
