# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 1018  
**PASS:** 251 (24.7%)  
**Failures:** 767 (75.3%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 251 | 24.7% |
| BUILD_FAIL | 427 | 41.9% |
| RUN_FAIL | 224 | 22.0% |
| VERIFY_FAIL | 94 | 9.2% |
| EXTRACTION_FAIL | 22 | 2.2% |
| ERROR | 0 | 0.0% |
| **Total** | **1018** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*427 total BUILD_FAIL results classified into 11 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `missing_header` | 120 | 28.1% | Missing or wrong #include directive — file not found |
| 2 | `undeclared_identifier` | 105 | 24.6% | Function, variable, or type not declared/defined in scope |
| 3 | `linker_error` | 56 | 13.1% | Compilation succeeded but linking failed (undefined references, etc.) |
| 4 | `missing_target_api` | 52 | 12.2% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 5 | `other_build` | 49 | 11.5% | Build failures not matching any specific pattern |
| 6 | `syntax_error` | 15 | 3.5% | Parse errors, malformed code, unexpected tokens |
| 7 | `type_mismatch` | 10 | 2.3% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `redefinition` | 7 | 1.6% | Duplicate or conflicting definitions of types/functions/variables |
| 9 | `implicit_declaration` | 6 | 1.4% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 10 | `retained_cuda_types` | 5 | 1.2% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 11 | `retained_cuda_api` | 2 | 0.5% | LLM retained CUDA API calls/keywords in non-CUDA target code |
| | **Total** | **427** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*224 total RUN_FAIL results classified into 7 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `opencl_jit_error` | 98 | 43.8% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 2 | `wrong_exit_code` | 80 | 35.7% | Non-zero exit code without crash signal or other specific error pattern |
| 3 | `segfault` | 27 | 12.1% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 4 | `wrong_checksum` | 12 | 5.4% | Program ran to completion but output checksum was incorrect |
| 5 | `abort` | 3 | 1.3% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| 6 | `gpu_memory_error` | 2 | 0.9% | CUDA illegal memory access during kernel execution |
| 7 | `data_file_missing` | 2 | 0.9% | Required input data file not found at expected path |
| | **Total** | **224** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*22 total EXTRACTION_FAIL results classified into 2 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `missing_files` | 18 | 81.8% | Expected output files not found in LLM response |
| 2 | `no_code_blocks` | 4 | 18.2% | LLM response did not contain parseable code for expected target files |
| | **Total** | **22** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*94 total VERIFY_FAIL results classified into 4 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 73 | 77.7% | Program produced output that did not match the expected stdout pattern |
| 2 | `verification_error` | 9 | 9.6% | Verification process itself errored (regex failure, harness issue) |
| 3 | `pass_overall_mislabel` | 7 | 7.4% | Verify passed but overall_status is VERIFY_FAIL (pipeline labeling bug) |
| 4 | `missing_output` | 5 | 5.3% | Program produced no stdout output (empty or whitespace-only) |
| | **Total** | **94** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `missing_header` | 120 | 120 |
| `undeclared_identifier` | 105 | 105 |
| `linker_error` | 56 | 56 |
| `missing_target_api` | 52 | 52 |
| `other_build` | 49 | 49 |
| `syntax_error` | 15 | 15 |
| `type_mismatch` | 10 | 10 |
| `redefinition` | 7 | 7 |
| `implicit_declaration` | 6 | 6 |
| `retained_cuda_types` | 5 | 5 |
| `retained_cuda_api` | 2 | 2 |
| **Total** | **427** | **427** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | opencl→cuda | omp→cuda | cuda→omp | opencl→omp | cuda→omp_target | omp_target→cuda | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|
| `missing_header` | 53 | 29 | 21 | 17 | 0 | 0 | 120 |
| `undeclared_identifier` | 27 | 24 | 22 | 22 | 6 | 4 | 105 |
| `linker_error` | 37 | 3 | 6 | 10 | 0 | 0 | 56 |
| `missing_target_api` | 10 | 12 | 20 | 9 | 1 | 0 | 52 |
| `other_build` | 7 | 19 | 6 | 3 | 10 | 4 | 49 |
| `syntax_error` | 4 | 1 | 2 | 3 | 2 | 3 | 15 |
| `type_mismatch` | 0 | 2 | 1 | 7 | 0 | 0 | 10 |
| `redefinition` | 3 | 3 | 1 | 0 | 0 | 0 | 7 |
| `implicit_declaration` | 0 | 2 | 4 | 0 | 0 | 0 | 6 |
| `retained_cuda_types` | 0 | 0 | 2 | 3 | 0 | 0 | 5 |
| `retained_cuda_api` | 0 | 0 | 1 | 1 | 0 | 0 | 2 |
| **Total** | **141** | **95** | **86** | **75** | **19** | **11** | **427** |

## Table 7: RUN_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `opencl_jit_error` | 98 | 98 |
| `wrong_exit_code` | 80 | 80 |
| `segfault` | 27 | 27 |
| `wrong_checksum` | 12 | 12 |
| `abort` | 3 | 3 |
| `gpu_memory_error` | 2 | 2 |
| `data_file_missing` | 2 | 2 |
| **Total** | **224** | **224** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| together-qwen-3.5-397b-a17b | 1018 | 251 | 427 | 224 | 94 | 22 | 0 | 24.7% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 168 | 76 | 86 | 3 | 2 | 1 | 0 | 45.2% |
| cuda→omp_target | 24 | 0 | 19 | 5 | 0 | 0 | 0 | 0.0% |
| cuda→opencl | 169 | 20 | 0 | 118 | 29 | 2 | 0 | 11.8% |
| omp→cuda | 168 | 56 | 95 | 4 | 1 | 12 | 0 | 33.3% |
| omp→opencl | 145 | 33 | 0 | 86 | 22 | 4 | 0 | 22.8% |
| omp_target→cuda | 30 | 18 | 11 | 0 | 1 | 0 | 0 | 60.0% |
| opencl→cuda | 169 | 6 | 141 | 4 | 15 | 3 | 0 | 3.6% |
| opencl→omp | 145 | 42 | 75 | 4 | 24 | 0 | 0 | 29.0% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 48 | 12 | 25.0% | `linker_error` | 12 |
| bfs | 48 | 20 | 41.7% | `segfault` | 9 |
| bptree | 48 | 6 | 12.5% | `missing_header` | 25 |
| cfd | 48 | 18 | 37.5% | `wrong_numerical_output` | 16 |
| convolution1d | 6 | 0 | 0.0% | `other_build` | 3 |
| dwt2d | 16 | 0 | 0.0% | `segfault` | 8 |
| floydwarshall | 12 | 9 | 75.0% | `other_build` | 2 |
| gaussian | 16 | 0 | 0.0% | `wrong_exit_code` | 8 |
| heartwall | 48 | 0 | 0.0% | `undeclared_identifier` | 16 |
| heat2d | 12 | 9 | 75.0% | `undeclared_identifier` | 2 |
| hotspot | 48 | 24 | 50.0% | `wrong_exit_code` | 8 |
| hotspot3d | 48 | 25 | 52.1% | `linker_error` | 8 |
| hybridsort | 16 | 0 | 0.0% | `missing_header` | 8 |
| iso2dfd | 12 | 7 | 58.3% | `other_build` | 2 |
| jacobi | 6 | 0 | 0.0% | `syntax_error` | 4 |
| kmeans | 48 | 0 | 0.0% | `wrong_numerical_output` | 16 |
| lavamd | 48 | 2 | 4.2% | `missing_header` | 24 |
| lud | 48 | 19 | 39.6% | `wrong_exit_code` | 7 |
| md | 6 | 1 | 16.7% | `other_build` | 3 |
| mixbench | 18 | 2 | 11.1% | `missing_header` | 6 |
| mummergpu | 16 | 0 | 0.0% | `other_build` | 10 |
| myocyte | 48 | 0 | 0.0% | `missing_header` | 21 |
| nn | 48 | 8 | 16.7% | `wrong_exit_code` | 15 |
| nqueen | 6 | 2 | 33.3% | `other_build` | 2 |
| nw | 48 | 20 | 41.7% | `wrong_exit_code` | 8 |
| page-rank | 6 | 3 | 50.0% | `segfault` | 2 |
| particlefilter | 48 | 23 | 47.9% | `wrong_numerical_output` | 12 |
| pathfinder | 48 | 17 | 35.4% | `undeclared_identifier` | 11 |
| rsbench | 18 | 0 | 0.0% | `missing_target_api` | 8 |
| scan | 9 | 0 | 0.0% | `other_build` | 4 |
| srad | 48 | 15 | 31.2% | `opencl_jit_error` | 16 |
| stencil1d | 9 | 7 | 77.8% | `retained_cuda_types` | 2 |
| streamcluster | 48 | 2 | 4.2% | `undeclared_identifier` | 19 |
| xsbench | 18 | 0 | 0.0% | `missing_target_api` | 12 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`missing_header`** — 120 (28.1% of BUILD_FAIL)
2. **`undeclared_identifier`** — 105 (24.6% of BUILD_FAIL)
3. **`linker_error`** — 56 (13.1% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`opencl_jit_error`** — 98 (43.8% of RUN_FAIL)
2. **`wrong_exit_code`** — 80 (35.7% of RUN_FAIL)
3. **`segfault`** — 27 (12.1% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 73 (77.7% of VERIFY_FAIL)
2. **`verification_error`** — 9 (9.6% of VERIFY_FAIL)
3. **`pass_overall_mislabel`** — 7 (7.4% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 76/168 PASS (45.2%)
- cuda→omp_target: 0/24 PASS (0.0%)
- cuda→opencl: 20/169 PASS (11.8%)
- omp→cuda: 56/168 PASS (33.3%)
- omp→opencl: 33/145 PASS (22.8%)
- omp_target→cuda: 18/30 PASS (60.0%)
- opencl→cuda: 6/169 PASS (3.6%)
- opencl→omp: 42/145 PASS (29.0%)

### Compound Failures (Multiple Root Causes)

**240** results (31.3% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 65 |
| missing_header + undeclared_identifier | 35 |
| missing_header + linker_error | 31 |
| undeclared_identifier + syntax_error | 24 |
| missing_target_api + linker_error | 21 |
| missing_target_api + undeclared_identifier | 16 |
| undeclared_identifier + redefinition | 13 |
| missing_target_api + missing_header | 12 |
| wrong_checksum + opencl_jit_error | 12 |
| linker_error + implicit_declaration | 11 |
