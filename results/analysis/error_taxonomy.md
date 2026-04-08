# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 2158  
**PASS:** 602 (27.9%)  
**Failures:** 1556 (72.1%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 602 | 27.9% |
| BUILD_FAIL | 931 | 43.1% |
| RUN_FAIL | 374 | 17.3% |
| VERIFY_FAIL | 228 | 10.6% |
| EXTRACTION_FAIL | 22 | 1.0% |
| ERROR | 1 | 0.0% |
| **Total** | **2158** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*931 total BUILD_FAIL results classified into 12 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `missing_header` | 271 | 29.1% | Missing or wrong #include directive — file not found |
| 2 | `other_build` | 172 | 18.5% | Build failures not matching any specific pattern |
| 3 | `undeclared_identifier` | 151 | 16.2% | Function, variable, or type not declared/defined in scope |
| 4 | `missing_target_api` | 141 | 15.1% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 5 | `linker_error` | 116 | 12.5% | Compilation succeeded but linking failed (undefined references, etc.) |
| 6 | `syntax_error` | 23 | 2.5% | Parse errors, malformed code, unexpected tokens |
| 7 | `type_mismatch` | 18 | 1.9% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `implicit_declaration` | 17 | 1.8% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 9 | `redefinition` | 8 | 0.9% | Duplicate or conflicting definitions of types/functions/variables |
| 10 | `retained_cuda_types` | 6 | 0.6% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 11 | `retained_cuda_api` | 5 | 0.5% | LLM retained CUDA API calls/keywords in non-CUDA target code |
| 12 | `retained_opencl_api` | 3 | 0.3% | LLM retained OpenCL API calls in non-OpenCL target code |
| | **Total** | **931** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*374 total RUN_FAIL results classified into 7 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `wrong_exit_code` | 163 | 43.6% | Non-zero exit code without crash signal or other specific error pattern |
| 2 | `opencl_jit_error` | 109 | 29.1% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 3 | `segfault` | 44 | 11.8% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 4 | `wrong_checksum` | 31 | 8.3% | Program ran to completion but output checksum was incorrect |
| 5 | `abort` | 22 | 5.9% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| 6 | `data_file_missing` | 3 | 0.8% | Required input data file not found at expected path |
| 7 | `gpu_memory_error` | 2 | 0.5% | CUDA illegal memory access during kernel execution |
| | **Total** | **374** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*22 total EXTRACTION_FAIL results classified into 2 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `missing_files` | 18 | 81.8% | Expected output files not found in LLM response |
| 2 | `no_code_blocks` | 4 | 18.2% | LLM response did not contain parseable code for expected target files |
| | **Total** | **22** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*228 total VERIFY_FAIL results classified into 4 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 186 | 81.6% | Program produced output that did not match the expected stdout pattern |
| 2 | `other_verify` | 20 | 8.8% | Verification failure not matching any specific pattern |
| 3 | `missing_output` | 11 | 4.8% | Program produced no stdout output (empty or whitespace-only) |
| 4 | `verification_error` | 11 | 4.8% | Verification process itself errored (regex failure, harness issue) |
| | **Total** | **228** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `missing_header` | 151 | 120 | 271 |
| `other_build` | 86 | 86 | 172 |
| `undeclared_identifier` | 37 | 114 | 151 |
| `missing_target_api` | 62 | 79 | 141 |
| `linker_error` | 54 | 62 | 116 |
| `syntax_error` | 3 | 20 | 23 |
| `type_mismatch` | 4 | 14 | 18 |
| `implicit_declaration` | 11 | 6 | 17 |
| `redefinition` | 1 | 7 | 8 |
| `retained_cuda_types` | 1 | 5 | 6 |
| `retained_cuda_api` | 1 | 4 | 5 |
| `retained_opencl_api` | 0 | 3 | 3 |
| **Total** | **411** | **520** | **931** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | opencl→cuda | omp→cuda | cuda→omp | opencl→omp | cuda→omp_target | omp→opencl | cuda→opencl | omp_target→cuda | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| `missing_header` | 93 | 51 | 40 | 26 | 0 | 29 | 32 | 0 | 271 |
| `other_build` | 45 | 43 | 18 | 9 | 27 | 8 | 8 | 14 | 172 |
| `undeclared_identifier` | 33 | 34 | 30 | 38 | 11 | 0 | 0 | 5 | 151 |
| `missing_target_api` | 32 | 38 | 36 | 30 | 1 | 4 | 0 | 0 | 141 |
| `linker_error` | 47 | 13 | 22 | 34 | 0 | 0 | 0 | 0 | 116 |
| `syntax_error` | 5 | 2 | 6 | 3 | 4 | 0 | 0 | 3 | 23 |
| `type_mismatch` | 0 | 10 | 1 | 7 | 0 | 0 | 0 | 0 | 18 |
| `implicit_declaration` | 6 | 2 | 7 | 2 | 0 | 0 | 0 | 0 | 17 |
| `redefinition` | 3 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 8 |
| `retained_cuda_types` | 0 | 0 | 2 | 4 | 0 | 0 | 0 | 0 | 6 |
| `retained_cuda_api` | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 0 | 5 |
| `retained_opencl_api` | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| **Total** | **267** | **196** | **168** | **154** | **43** | **41** | **40** | **22** | **931** |

## Table 7: RUN_FAIL Categories by Model

| Category | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `wrong_exit_code` | 73 | 90 | 163 |
| `opencl_jit_error` | 9 | 100 | 109 |
| `segfault` | 17 | 27 | 44 |
| `wrong_checksum` | 0 | 31 | 31 |
| `abort` | 16 | 6 | 22 |
| `data_file_missing` | 1 | 2 | 3 |
| `gpu_memory_error` | 0 | 2 | 2 |
| **Total** | **116** | **258** | **374** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| azure-gpt-4.1-mini | 910 | 246 | 411 | 116 | 137 | 0 | 0 | 27.0% |
| together-qwen-3.5-397b-a17b | 1248 | 356 | 520 | 258 | 91 | 22 | 1 | 28.5% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 352 | 170 | 168 | 6 | 7 | 1 | 0 | 48.3% |
| cuda→omp_target | 64 | 7 | 43 | 12 | 2 | 0 | 0 | 10.9% |
| cuda→opencl | 344 | 73 | 40 | 190 | 38 | 2 | 1 | 21.2% |
| omp→cuda | 349 | 95 | 196 | 12 | 34 | 12 | 0 | 27.2% |
| omp→opencl | 296 | 83 | 41 | 130 | 38 | 4 | 0 | 28.0% |
| omp_target→cuda | 160 | 80 | 22 | 11 | 47 | 0 | 0 | 50.0% |
| opencl→cuda | 297 | 7 | 267 | 5 | 15 | 3 | 0 | 2.4% |
| opencl→omp | 296 | 87 | 154 | 8 | 47 | 0 | 0 | 29.4% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 91 | 35 | 38.5% | `linker_error` | 21 |
| bfs | 90 | 52 | 57.8% | `linker_error` | 11 |
| bptree | 93 | 6 | 6.5% | `missing_header` | 49 |
| cfd | 90 | 33 | 36.7% | `other_build` | 26 |
| convolution1d | 24 | 0 | 0.0% | `other_build` | 11 |
| dwt2d | 29 | 6 | 20.7% | `missing_header` | 12 |
| floydwarshall | 48 | 25 | 52.1% | `wrong_numerical_output` | 16 |
| gaussian | 29 | 0 | 0.0% | `wrong_exit_code` | 17 |
| heartwall | 90 | 0 | 0.0% | `undeclared_identifier` | 31 |
| heat2d | 48 | 26 | 54.2% | `wrong_numerical_output` | 14 |
| hotspot | 90 | 57 | 63.3% | `wrong_exit_code` | 9 |
| hotspot3d | 90 | 53 | 58.9% | `missing_header` | 11 |
| hybridsort | 29 | 0 | 0.0% | `opencl_jit_error` | 15 |
| iso2dfd | 48 | 22 | 45.8% | `wrong_exit_code` | 18 |
| jacobi | 24 | 13 | 54.2% | `syntax_error` | 5 |
| kmeans | 90 | 0 | 0.0% | `wrong_numerical_output` | 22 |
| lavamd | 90 | 6 | 6.7% | `missing_header` | 56 |
| lud | 90 | 27 | 30.0% | `missing_header` | 16 |
| md | 24 | 14 | 58.3% | `other_build` | 6 |
| mixbench | 61 | 11 | 18.0% | `missing_target_api` | 20 |
| mummergpu | 29 | 0 | 0.0% | `other_build` | 17 |
| myocyte | 90 | 0 | 0.0% | `missing_header` | 41 |
| nn | 90 | 18 | 20.0% | `wrong_exit_code` | 20 |
| nqueen | 24 | 8 | 33.3% | `wrong_numerical_output` | 9 |
| nw | 90 | 41 | 45.6% | `wrong_exit_code` | 16 |
| page-rank | 24 | 17 | 70.8% | `other_build` | 2 |
| particlefilter | 90 | 35 | 38.9% | `wrong_numerical_output` | 19 |
| pathfinder | 90 | 43 | 47.8% | `undeclared_identifier` | 17 |
| rsbench | 54 | 0 | 0.0% | `missing_target_api` | 17 |
| scan | 40 | 5 | 12.5% | `wrong_numerical_output` | 19 |
| srad | 90 | 23 | 25.6% | `wrong_exit_code` | 17 |
| stencil1d | 40 | 22 | 55.0% | `wrong_numerical_output` | 16 |
| streamcluster | 85 | 4 | 4.7% | `wrong_exit_code` | 30 |
| xsbench | 54 | 0 | 0.0% | `missing_target_api` | 21 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`missing_header`** — 271 (29.1% of BUILD_FAIL)
2. **`other_build`** — 172 (18.5% of BUILD_FAIL)
3. **`undeclared_identifier`** — 151 (16.2% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`wrong_exit_code`** — 163 (43.6% of RUN_FAIL)
2. **`opencl_jit_error`** — 109 (29.1% of RUN_FAIL)
3. **`segfault`** — 44 (11.8% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 186 (81.6% of VERIFY_FAIL)
2. **`other_verify`** — 20 (8.8% of VERIFY_FAIL)
3. **`missing_output`** — 11 (4.8% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 170/352 PASS (48.3%)
- cuda→omp_target: 7/64 PASS (10.9%)
- cuda→opencl: 73/344 PASS (21.2%)
- omp→cuda: 95/349 PASS (27.2%)
- omp→opencl: 83/296 PASS (28.0%)
- omp_target→cuda: 80/160 PASS (50.0%)
- opencl→cuda: 7/297 PASS (2.4%)
- opencl→omp: 87/296 PASS (29.4%)

### Compound Failures (Multiple Root Causes)

**432** results (27.8% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 105 |
| missing_target_api + linker_error | 53 |
| undeclared_identifier + syntax_error | 44 |
| missing_header + undeclared_identifier | 44 |
| missing_header + linker_error | 42 |
| missing_target_api + missing_header | 42 |
| linker_error + implicit_declaration | 33 |
| wrong_checksum + opencl_jit_error | 31 |
| missing_target_api + undeclared_identifier | 29 |
| missing_target_api + implicit_declaration | 20 |
