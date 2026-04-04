# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 1248  
**PASS:** 356 (28.5%)  
**Failures:** 892 (71.5%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 356 | 28.5% |
| BUILD_FAIL | 520 | 41.7% |
| RUN_FAIL | 258 | 20.7% |
| VERIFY_FAIL | 91 | 7.3% |
| EXTRACTION_FAIL | 22 | 1.8% |
| ERROR | 1 | 0.1% |
| **Total** | **1248** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*520 total BUILD_FAIL results classified into 12 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `missing_header` | 120 | 23.1% | Missing or wrong #include directive — file not found |
| 2 | `undeclared_identifier` | 114 | 21.9% | Function, variable, or type not declared/defined in scope |
| 3 | `other_build` | 86 | 16.5% | Build failures not matching any specific pattern |
| 4 | `missing_target_api` | 79 | 15.2% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 5 | `linker_error` | 62 | 11.9% | Compilation succeeded but linking failed (undefined references, etc.) |
| 6 | `syntax_error` | 20 | 3.8% | Parse errors, malformed code, unexpected tokens |
| 7 | `type_mismatch` | 14 | 2.7% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `redefinition` | 7 | 1.3% | Duplicate or conflicting definitions of types/functions/variables |
| 9 | `implicit_declaration` | 6 | 1.2% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 10 | `retained_cuda_types` | 5 | 1.0% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 11 | `retained_cuda_api` | 4 | 0.8% | LLM retained CUDA API calls/keywords in non-CUDA target code |
| 12 | `retained_opencl_api` | 3 | 0.6% | LLM retained OpenCL API calls in non-OpenCL target code |
| | **Total** | **520** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*258 total RUN_FAIL results classified into 7 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `opencl_jit_error` | 100 | 38.8% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 2 | `wrong_exit_code` | 90 | 34.9% | Non-zero exit code without crash signal or other specific error pattern |
| 3 | `wrong_checksum` | 31 | 12.0% | Program ran to completion but output checksum was incorrect |
| 4 | `segfault` | 27 | 10.5% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 5 | `abort` | 6 | 2.3% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| 6 | `gpu_memory_error` | 2 | 0.8% | CUDA illegal memory access during kernel execution |
| 7 | `data_file_missing` | 2 | 0.8% | Required input data file not found at expected path |
| | **Total** | **258** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*22 total EXTRACTION_FAIL results classified into 2 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `missing_files` | 18 | 81.8% | Expected output files not found in LLM response |
| 2 | `no_code_blocks` | 4 | 18.2% | LLM response did not contain parseable code for expected target files |
| | **Total** | **22** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*91 total VERIFY_FAIL results classified into 3 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 77 | 84.6% | Program produced output that did not match the expected stdout pattern |
| 2 | `verification_error` | 9 | 9.9% | Verification process itself errored (regex failure, harness issue) |
| 3 | `missing_output` | 5 | 5.5% | Program produced no stdout output (empty or whitespace-only) |
| | **Total** | **91** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `missing_header` | 120 | 120 |
| `undeclared_identifier` | 114 | 114 |
| `other_build` | 86 | 86 |
| `missing_target_api` | 79 | 79 |
| `linker_error` | 62 | 62 |
| `syntax_error` | 20 | 20 |
| `type_mismatch` | 14 | 14 |
| `redefinition` | 7 | 7 |
| `implicit_declaration` | 6 | 6 |
| `retained_cuda_types` | 5 | 5 |
| `retained_cuda_api` | 4 | 4 |
| `retained_opencl_api` | 3 | 3 |
| **Total** | **520** | **520** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | opencl→cuda | omp→cuda | cuda→omp | opencl→omp | cuda→omp_target | omp_target→cuda | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|
| `missing_header` | 53 | 29 | 21 | 17 | 0 | 0 | 120 |
| `undeclared_identifier` | 27 | 25 | 25 | 22 | 11 | 4 | 114 |
| `other_build` | 7 | 25 | 10 | 4 | 27 | 13 | 86 |
| `missing_target_api` | 22 | 13 | 20 | 23 | 1 | 0 | 79 |
| `linker_error` | 37 | 6 | 9 | 10 | 0 | 0 | 62 |
| `syntax_error` | 4 | 1 | 5 | 3 | 4 | 3 | 20 |
| `type_mismatch` | 0 | 6 | 1 | 7 | 0 | 0 | 14 |
| `redefinition` | 3 | 3 | 1 | 0 | 0 | 0 | 7 |
| `implicit_declaration` | 0 | 2 | 4 | 0 | 0 | 0 | 6 |
| `retained_cuda_types` | 0 | 0 | 2 | 3 | 0 | 0 | 5 |
| `retained_cuda_api` | 0 | 0 | 3 | 1 | 0 | 0 | 4 |
| `retained_opencl_api` | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| **Total** | **156** | **110** | **101** | **90** | **43** | **20** | **520** |

## Table 7: RUN_FAIL Categories by Model

| Category | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|
| `opencl_jit_error` | 100 | 100 |
| `wrong_exit_code` | 90 | 90 |
| `wrong_checksum` | 31 | 31 |
| `segfault` | 27 | 27 |
| `abort` | 6 | 6 |
| `gpu_memory_error` | 2 | 2 |
| `data_file_missing` | 2 | 2 |
| **Total** | **258** | **258** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| together-qwen-3.5-397b-a17b | 1248 | 356 | 520 | 258 | 91 | 22 | 1 | 28.5% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 208 | 101 | 101 | 3 | 2 | 1 | 0 | 48.6% |
| cuda→omp_target | 64 | 7 | 43 | 12 | 2 | 0 | 0 | 10.9% |
| cuda→opencl | 184 | 28 | 0 | 131 | 22 | 2 | 1 | 15.2% |
| omp→cuda | 208 | 79 | 110 | 4 | 3 | 12 | 0 | 38.0% |
| omp→opencl | 160 | 36 | 0 | 98 | 22 | 4 | 0 | 22.5% |
| omp_target→cuda | 80 | 57 | 20 | 2 | 1 | 0 | 0 | 71.2% |
| opencl→cuda | 184 | 6 | 156 | 4 | 15 | 3 | 0 | 3.3% |
| opencl→omp | 160 | 42 | 90 | 4 | 24 | 0 | 0 | 26.2% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 48 | 19 | 39.6% | `linker_error` | 12 |
| bfs | 48 | 20 | 41.7% | `segfault` | 9 |
| bptree | 48 | 6 | 12.5% | `missing_header` | 25 |
| cfd | 48 | 18 | 37.5% | `wrong_numerical_output` | 16 |
| convolution1d | 16 | 0 | 0.0% | `other_build` | 11 |
| dwt2d | 16 | 0 | 0.0% | `segfault` | 8 |
| floydwarshall | 32 | 25 | 78.1% | `other_build` | 3 |
| gaussian | 16 | 0 | 0.0% | `wrong_exit_code` | 8 |
| heartwall | 48 | 0 | 0.0% | `undeclared_identifier` | 16 |
| heat2d | 32 | 24 | 75.0% | `other_build` | 5 |
| hotspot | 48 | 24 | 50.0% | `wrong_exit_code` | 8 |
| hotspot3d | 48 | 25 | 52.1% | `linker_error` | 8 |
| hybridsort | 16 | 0 | 0.0% | `missing_header` | 8 |
| iso2dfd | 32 | 22 | 68.8% | `undeclared_identifier` | 3 |
| jacobi | 16 | 6 | 37.5% | `syntax_error` | 5 |
| kmeans | 48 | 0 | 0.0% | `wrong_numerical_output` | 16 |
| lavamd | 48 | 2 | 4.2% | `missing_header` | 24 |
| lud | 48 | 19 | 39.6% | `wrong_exit_code` | 7 |
| md | 16 | 7 | 43.8% | `other_build` | 6 |
| mixbench | 48 | 10 | 20.8% | `missing_target_api` | 14 |
| mummergpu | 16 | 0 | 0.0% | `other_build` | 10 |
| myocyte | 48 | 0 | 0.0% | `missing_header` | 21 |
| nn | 48 | 8 | 16.7% | `wrong_exit_code` | 15 |
| nqueen | 16 | 8 | 50.0% | `other_build` | 3 |
| nw | 48 | 20 | 41.7% | `wrong_exit_code` | 8 |
| page-rank | 16 | 9 | 56.2% | `other_build` | 2 |
| particlefilter | 48 | 23 | 47.9% | `wrong_numerical_output` | 12 |
| pathfinder | 48 | 17 | 35.4% | `undeclared_identifier` | 11 |
| rsbench | 48 | 0 | 0.0% | `missing_target_api` | 17 |
| scan | 24 | 5 | 20.8% | `other_build` | 11 |
| srad | 48 | 15 | 31.2% | `opencl_jit_error` | 16 |
| stencil1d | 24 | 22 | 91.7% | `retained_cuda_types` | 2 |
| streamcluster | 48 | 2 | 4.2% | `undeclared_identifier` | 19 |
| xsbench | 48 | 0 | 0.0% | `missing_target_api` | 20 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`missing_header`** — 120 (23.1% of BUILD_FAIL)
2. **`undeclared_identifier`** — 114 (21.9% of BUILD_FAIL)
3. **`other_build`** — 86 (16.5% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`opencl_jit_error`** — 100 (38.8% of RUN_FAIL)
2. **`wrong_exit_code`** — 90 (34.9% of RUN_FAIL)
3. **`wrong_checksum`** — 31 (12.0% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 77 (84.6% of VERIFY_FAIL)
2. **`verification_error`** — 9 (9.9% of VERIFY_FAIL)
3. **`missing_output`** — 5 (5.5% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 101/208 PASS (48.6%)
- cuda→omp_target: 7/64 PASS (10.9%)
- cuda→opencl: 28/184 PASS (15.2%)
- omp→cuda: 79/208 PASS (38.0%)
- omp→opencl: 36/160 PASS (22.5%)
- omp_target→cuda: 57/80 PASS (71.2%)
- opencl→cuda: 6/184 PASS (3.3%)
- opencl→omp: 42/160 PASS (26.2%)

### Compound Failures (Multiple Root Causes)

**284** results (31.8% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 65 |
| missing_header + undeclared_identifier | 35 |
| missing_target_api + linker_error | 34 |
| missing_header + linker_error | 31 |
| wrong_checksum + opencl_jit_error | 31 |
| undeclared_identifier + syntax_error | 25 |
| missing_target_api + undeclared_identifier | 16 |
| missing_target_api + syntax_error | 13 |
| undeclared_identifier + redefinition | 13 |
| missing_target_api + missing_header | 12 |
