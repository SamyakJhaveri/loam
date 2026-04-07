# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 2145  
**PASS:** 578 (26.9%)  
**Failures:** 1567 (73.1%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 578 | 26.9% |
| BUILD_FAIL | 1035 | 48.3% |
| RUN_FAIL | 357 | 16.6% |
| VERIFY_FAIL | 151 | 7.0% |
| EXTRACTION_FAIL | 23 | 1.1% |
| ERROR | 1 | 0.0% |
| **Total** | **2145** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*1035 total BUILD_FAIL results classified into 12 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `missing_header` | 288 | 27.8% | Missing or wrong #include directive — file not found |
| 2 | `missing_target_api` | 275 | 26.6% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 3 | `other_build` | 148 | 14.3% | Build failures not matching any specific pattern |
| 4 | `undeclared_identifier` | 143 | 13.8% | Function, variable, or type not declared/defined in scope |
| 5 | `linker_error` | 113 | 10.9% | Compilation succeeded but linking failed (undefined references, etc.) |
| 6 | `syntax_error` | 21 | 2.0% | Parse errors, malformed code, unexpected tokens |
| 7 | `type_mismatch` | 14 | 1.4% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `implicit_declaration` | 11 | 1.1% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 9 | `redefinition` | 8 | 0.8% | Duplicate or conflicting definitions of types/functions/variables |
| 10 | `retained_cuda_types` | 6 | 0.6% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 11 | `retained_cuda_api` | 5 | 0.5% | LLM retained CUDA API calls/keywords in non-CUDA target code |
| 12 | `retained_opencl_api` | 3 | 0.3% | LLM retained OpenCL API calls in non-OpenCL target code |
| | **Total** | **1035** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*357 total RUN_FAIL results classified into 7 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `wrong_exit_code` | 147 | 41.2% | Non-zero exit code without crash signal or other specific error pattern |
| 2 | `opencl_jit_error` | 109 | 30.5% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 3 | `segfault` | 44 | 12.3% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 4 | `wrong_checksum` | 31 | 8.7% | Program ran to completion but output checksum was incorrect |
| 5 | `abort` | 21 | 5.9% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| 6 | `data_file_missing` | 3 | 0.8% | Required input data file not found at expected path |
| 7 | `gpu_memory_error` | 2 | 0.6% | CUDA illegal memory access during kernel execution |
| | **Total** | **357** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*23 total EXTRACTION_FAIL results classified into 2 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `missing_files` | 18 | 78.3% | Expected output files not found in LLM response |
| 2 | `no_code_blocks` | 5 | 21.7% | LLM response did not contain parseable code for expected target files |
| | **Total** | **23** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*151 total VERIFY_FAIL results classified into 4 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 109 | 72.2% | Program produced output that did not match the expected stdout pattern |
| 2 | `other_verify` | 20 | 13.2% | Verification failure not matching any specific pattern |
| 3 | `missing_output` | 11 | 7.3% | Program produced no stdout output (empty or whitespace-only) |
| 4 | `verification_error` | 11 | 7.3% | Verification process itself errored (regex failure, harness issue) |
| | **Total** | **151** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `missing_header` | 168 | 120 | 288 |
| `missing_target_api` | 196 | 79 | 275 |
| `other_build` | 62 | 86 | 148 |
| `undeclared_identifier` | 29 | 114 | 143 |
| `linker_error` | 51 | 62 | 113 |
| `syntax_error` | 1 | 20 | 21 |
| `type_mismatch` | 0 | 14 | 14 |
| `implicit_declaration` | 5 | 6 | 11 |
| `redefinition` | 1 | 7 | 8 |
| `retained_cuda_types` | 1 | 5 | 6 |
| `retained_cuda_api` | 1 | 4 | 5 |
| `retained_opencl_api` | 0 | 3 | 3 |
| **Total** | **515** | **520** | **1035** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | cuda→omp | omp→cuda | opencl→cuda | opencl→omp | cuda→omp_target | omp→opencl | cuda→opencl | omp_target→cuda | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| `missing_header` | 69 | 47 | 63 | 26 | 22 | 29 | 32 | 0 | 288 |
| `missing_target_api` | 67 | 41 | 23 | 53 | 43 | 24 | 24 | 0 | 275 |
| `other_build` | 22 | 44 | 12 | 10 | 27 | 12 | 8 | 13 | 148 |
| `undeclared_identifier` | 30 | 33 | 27 | 38 | 11 | 0 | 0 | 4 | 143 |
| `linker_error` | 22 | 11 | 46 | 34 | 0 | 0 | 0 | 0 | 113 |
| `syntax_error` | 6 | 1 | 4 | 3 | 4 | 0 | 0 | 3 | 21 |
| `type_mismatch` | 1 | 6 | 0 | 7 | 0 | 0 | 0 | 0 | 14 |
| `implicit_declaration` | 7 | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 11 |
| `redefinition` | 2 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 8 |
| `retained_cuda_types` | 2 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 6 |
| `retained_cuda_api` | 4 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 5 |
| `retained_opencl_api` | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| **Total** | **232** | **188** | **181** | **178** | **107** | **65** | **64** | **20** | **1035** |

## Table 7: RUN_FAIL Categories by Model

| Category | azure-gpt-4.1-mini | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `wrong_exit_code` | 57 | 90 | 147 |
| `opencl_jit_error` | 9 | 100 | 109 |
| `segfault` | 17 | 27 | 44 |
| `wrong_checksum` | 0 | 31 | 31 |
| `abort` | 15 | 6 | 21 |
| `data_file_missing` | 1 | 2 | 3 |
| `gpu_memory_error` | 0 | 2 | 2 |
| **Total** | **99** | **258** | **357** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| azure-gpt-4.1-mini | 897 | 222 | 515 | 99 | 60 | 1 | 0 | 24.7% |
| together-qwen-3.5-397b-a17b | 1248 | 356 | 520 | 258 | 91 | 22 | 1 | 28.5% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 416 | 170 | 232 | 6 | 7 | 1 | 0 | 40.9% |
| cuda→omp_target | 128 | 7 | 107 | 12 | 2 | 0 | 0 | 5.5% |
| cuda→opencl | 368 | 73 | 64 | 190 | 38 | 2 | 1 | 19.8% |
| omp→cuda | 302 | 94 | 188 | 4 | 3 | 13 | 0 | 31.1% |
| omp→opencl | 320 | 83 | 65 | 130 | 38 | 4 | 0 | 25.9% |
| omp_target→cuda | 80 | 57 | 20 | 2 | 1 | 0 | 0 | 71.2% |
| opencl→cuda | 211 | 7 | 181 | 5 | 15 | 3 | 0 | 3.3% |
| opencl→omp | 320 | 87 | 178 | 8 | 47 | 0 | 0 | 27.2% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 90 | 35 | 38.9% | `linker_error` | 21 |
| bfs | 90 | 52 | 57.8% | `linker_error` | 11 |
| bptree | 90 | 6 | 6.7% | `missing_header` | 45 |
| cfd | 90 | 33 | 36.7% | `other_build` | 26 |
| convolution1d | 24 | 0 | 0.0% | `other_build` | 11 |
| dwt2d | 29 | 6 | 20.7% | `missing_header` | 12 |
| floydwarshall | 49 | 25 | 51.0% | `missing_header` | 16 |
| gaussian | 26 | 1 | 3.8% | `wrong_exit_code` | 17 |
| heartwall | 85 | 0 | 0.0% | `undeclared_identifier` | 26 |
| heat2d | 49 | 24 | 49.0% | `missing_target_api` | 11 |
| hotspot | 85 | 57 | 67.1% | `wrong_exit_code` | 9 |
| hotspot3d | 85 | 53 | 62.4% | `linker_error` | 10 |
| hybridsort | 24 | 0 | 0.0% | `opencl_jit_error` | 15 |
| iso2dfd | 49 | 22 | 44.9% | `missing_target_api` | 11 |
| jacobi | 24 | 6 | 25.0% | `missing_target_api` | 8 |
| kmeans | 85 | 0 | 0.0% | `wrong_numerical_output` | 22 |
| lavamd | 85 | 6 | 7.1% | `missing_header` | 51 |
| lud | 85 | 27 | 31.8% | `missing_header` | 16 |
| md | 24 | 7 | 29.2% | `missing_target_api` | 8 |
| mixbench | 80 | 10 | 12.5% | `missing_target_api` | 42 |
| mummergpu | 29 | 0 | 0.0% | `other_build` | 17 |
| myocyte | 85 | 0 | 0.0% | `missing_header` | 38 |
| nn | 85 | 18 | 21.2% | `wrong_exit_code` | 20 |
| nqueen | 24 | 8 | 33.3% | `missing_header` | 7 |
| nw | 85 | 41 | 48.2% | `wrong_exit_code` | 16 |
| page-rank | 24 | 9 | 37.5% | `missing_target_api` | 6 |
| particlefilter | 85 | 35 | 41.2% | `wrong_numerical_output` | 19 |
| pathfinder | 85 | 43 | 50.6% | `undeclared_identifier` | 17 |
| rsbench | 80 | 0 | 0.0% | `missing_target_api` | 46 |
| scan | 33 | 5 | 15.2% | `other_build` | 11 |
| srad | 85 | 23 | 27.1% | `wrong_exit_code` | 17 |
| stencil1d | 32 | 22 | 68.8% | `missing_header` | 8 |
| streamcluster | 85 | 4 | 4.7% | `wrong_exit_code` | 30 |
| xsbench | 80 | 0 | 0.0% | `missing_target_api` | 50 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`missing_header`** — 288 (27.8% of BUILD_FAIL)
2. **`missing_target_api`** — 275 (26.6% of BUILD_FAIL)
3. **`other_build`** — 148 (14.3% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`wrong_exit_code`** — 147 (41.2% of RUN_FAIL)
2. **`opencl_jit_error`** — 109 (30.5% of RUN_FAIL)
3. **`segfault`** — 44 (12.3% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 109 (72.2% of VERIFY_FAIL)
2. **`other_verify`** — 20 (13.2% of VERIFY_FAIL)
3. **`missing_output`** — 11 (7.3% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 170/416 PASS (40.9%)
- cuda→omp_target: 7/128 PASS (5.5%)
- cuda→opencl: 73/368 PASS (19.8%)
- omp→cuda: 94/302 PASS (31.1%)
- omp→opencl: 83/320 PASS (25.9%)
- omp_target→cuda: 57/80 PASS (71.2%)
- opencl→cuda: 7/211 PASS (3.3%)
- opencl→omp: 87/320 PASS (27.2%)

### Compound Failures (Multiple Root Causes)

**465** results (29.7% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 96 |
| missing_target_api + missing_header | 94 |
| missing_target_api + linker_error | 51 |
| undeclared_identifier + syntax_error | 42 |
| missing_header + linker_error | 42 |
| missing_header + undeclared_identifier | 41 |
| linker_error + implicit_declaration | 33 |
| wrong_checksum + opencl_jit_error | 31 |
| missing_target_api + undeclared_identifier | 27 |
| missing_target_api + implicit_declaration | 21 |
