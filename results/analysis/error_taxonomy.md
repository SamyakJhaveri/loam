# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 744  
**PASS:** 271 (36.4%)  
**Failures:** 473 (63.6%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 271 | 36.4% |
| BUILD_FAIL | 295 | 39.7% |
| RUN_FAIL | 131 | 17.6% |
| VERIFY_FAIL | 44 | 5.9% |
| EXTRACTION_FAIL | 3 | 0.4% |
| ERROR | 0 | 0.0% |
| **Total** | **744** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*295 total BUILD_FAIL results classified into 11 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `other_build` | 74 | 25.1% | Build failures not matching any specific pattern |
| 2 | `missing_header` | 68 | 23.1% | Missing or wrong #include directive — file not found |
| 3 | `undeclared_identifier` | 66 | 22.4% | Function, variable, or type not declared/defined in scope |
| 4 | `linker_error` | 38 | 12.9% | Compilation succeeded but linking failed (undefined references, etc.) |
| 5 | `syntax_error` | 16 | 5.4% | Parse errors, malformed code, unexpected tokens |
| 6 | `missing_target_api` | 15 | 5.1% | LLM translation contains no target API constructs (no pragmas/kernels for target language) |
| 7 | `type_mismatch` | 6 | 2.0% | Type mismatches, wrong function signatures, incompatible conversions |
| 8 | `retained_cuda_types` | 5 | 1.7% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 9 | `redefinition` | 4 | 1.4% | Duplicate or conflicting definitions of types/functions/variables |
| 10 | `implicit_declaration` | 2 | 0.7% | Missing function prototypes — implicit declaration warnings promoted to errors |
| 11 | `retained_opencl_api` | 1 | 0.3% | LLM retained OpenCL API calls in non-OpenCL target code |
| | **Total** | **295** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*131 total RUN_FAIL results classified into 5 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `opencl_jit_error` | 57 | 43.5% | OpenCL runtime kernel compilation failed (clBuildProgram errors) |
| 2 | `wrong_exit_code` | 36 | 27.5% | Non-zero exit code without crash signal or other specific error pattern |
| 3 | `segfault` | 22 | 16.8% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 4 | `wrong_checksum` | 15 | 11.5% | Program ran to completion but output checksum was incorrect |
| 5 | `abort` | 1 | 0.8% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| | **Total** | **131** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*3 total EXTRACTION_FAIL results classified into 2 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `no_code_blocks` | 2 | 66.7% | LLM response did not contain parseable code for expected target files |
| 2 | `missing_files` | 1 | 33.3% | Expected output files not found in LLM response |
| | **Total** | **3** | **100.0%** | |

## Table 4b: VERIFY_FAIL Root Cause Categories

*44 total VERIFY_FAIL results classified into 2 categories.*

| # | Category | Count | % of VERIFY_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `wrong_numerical_output` | 39 | 88.6% | Program produced output that did not match the expected stdout pattern |
| 2 | `pass_overall_mislabel` | 5 | 11.4% | Verify passed but overall_status is VERIFY_FAIL (pipeline labeling bug) |
| | **Total** | **44** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | azure-gpt-5.4 | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `other_build` | 0 | 74 | 74 |
| `missing_header` | 3 | 65 | 68 |
| `undeclared_identifier` | 0 | 66 | 66 |
| `linker_error` | 2 | 36 | 38 |
| `syntax_error` | 0 | 16 | 16 |
| `missing_target_api` | 0 | 15 | 15 |
| `type_mismatch` | 0 | 6 | 6 |
| `retained_cuda_types` | 0 | 5 | 5 |
| `redefinition` | 0 | 4 | 4 |
| `implicit_declaration` | 0 | 2 | 2 |
| `retained_opencl_api` | 0 | 1 | 1 |
| **Total** | **5** | **290** | **295** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | omp→cuda | opencl→cuda | cuda→omp | opencl→omp | cuda→omp_target | omp_target→cuda | omp→omp_target | omp_target→omp | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| `other_build` | 21 | 5 | 7 | 3 | 19 | 10 | 6 | 3 | 74 |
| `missing_header` | 12 | 26 | 20 | 10 | 0 | 0 | 0 | 0 | 68 |
| `undeclared_identifier` | 18 | 14 | 12 | 19 | 3 | 0 | 0 | 0 | 66 |
| `linker_error` | 6 | 15 | 8 | 9 | 0 | 0 | 0 | 0 | 38 |
| `syntax_error` | 0 | 1 | 2 | 0 | 5 | 7 | 1 | 0 | 16 |
| `missing_target_api` | 7 | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 15 |
| `type_mismatch` | 0 | 0 | 1 | 5 | 0 | 0 | 0 | 0 | 6 |
| `retained_cuda_types` | 0 | 0 | 1 | 3 | 1 | 0 | 0 | 0 | 5 |
| `redefinition` | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| `implicit_declaration` | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `retained_opencl_api` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **69** | **66** | **53** | **52** | **28** | **17** | **7** | **3** | **295** |

## Table 7: RUN_FAIL Categories by Model

| Category | azure-gpt-5.4 | together-qwen-3.5-397b-a17b | Total |
|----------|------:|------:|------:|
| `opencl_jit_error` | 0 | 57 | 57 |
| `wrong_exit_code` | 0 | 36 | 36 |
| `segfault` | 0 | 22 | 22 |
| `wrong_checksum` | 0 | 15 | 15 |
| `abort` | 0 | 1 | 1 |
| **Total** | **0** | **131** | **131** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| azure-gpt-5.4 | 36 | 28 | 5 | 0 | 1 | 2 | 0 | 77.8% |
| together-qwen-3.5-397b-a17b | 708 | 243 | 290 | 131 | 43 | 1 | 0 | 34.3% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | VERIFY_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|----------:|--------------:|------:|----------:|
| cuda→omp | 162 | 95 | 53 | 7 | 5 | 2 | 0 | 58.6% |
| cuda→omp_target | 30 | 0 | 28 | 2 | 0 | 0 | 0 | 0.0% |
| cuda→opencl | 81 | 8 | 0 | 61 | 12 | 0 | 0 | 9.9% |
| omp→cuda | 110 | 39 | 69 | 0 | 1 | 1 | 0 | 35.5% |
| omp→omp_target | 27 | 13 | 7 | 2 | 5 | 0 | 0 | 48.1% |
| omp→opencl | 100 | 39 | 0 | 50 | 11 | 0 | 0 | 39.0% |
| omp_target→cuda | 62 | 43 | 17 | 1 | 1 | 0 | 0 | 69.4% |
| omp_target→omp | 27 | 22 | 3 | 0 | 2 | 0 | 0 | 81.5% |
| opencl→cuda | 69 | 1 | 66 | 2 | 0 | 0 | 0 | 1.4% |
| opencl→omp | 76 | 11 | 52 | 6 | 7 | 0 | 0 | 14.5% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 25 | 8 | 32.0% | `undeclared_identifier` | 6 |
| bfs | 37 | 18 | 48.6% | `segfault` | 9 |
| bptree | 21 | 0 | 0.0% | `missing_header` | 11 |
| cfd | 25 | 9 | 36.0% | `wrong_numerical_output` | 6 |
| convolution1d | 10 | 2 | 20.0% | `other_build` | 8 |
| dwt2d | 6 | 0 | 0.0% | `segfault` | 3 |
| floydwarshall | 38 | 29 | 76.3% | `other_build` | 4 |
| gaussian | 6 | 0 | 0.0% | `wrong_exit_code` | 4 |
| heartwall | 21 | 2 | 9.5% | `missing_header` | 7 |
| heat2d | 38 | 29 | 76.3% | `other_build` | 4 |
| hotspot | 33 | 17 | 51.5% | `opencl_jit_error` | 7 |
| hotspot3d | 37 | 23 | 62.2% | `linker_error` | 5 |
| hybridsort | 6 | 0 | 0.0% | `missing_header` | 3 |
| iso2dfd | 38 | 32 | 84.2% | `other_build` | 4 |
| jacobi | 10 | 3 | 30.0% | `syntax_error` | 5 |
| kmeans | 18 | 0 | 0.0% | `wrong_numerical_output` | 6 |
| lavamd | 21 | 2 | 9.5% | `missing_header` | 11 |
| lud | 33 | 17 | 51.5% | `opencl_jit_error` | 5 |
| md | 10 | 4 | 40.0% | `other_build` | 3 |
| mixbench | 22 | 2 | 9.1% | `wrong_exit_code` | 7 |
| mummergpu | 6 | 0 | 0.0% | `other_build` | 4 |
| myocyte | 21 | 0 | 0.0% | `missing_header` | 9 |
| nn | 21 | 4 | 19.0% | `missing_header` | 6 |
| nqueen | 10 | 6 | 60.0% | `other_build` | 3 |
| nw | 33 | 14 | 42.4% | `undeclared_identifier` | 6 |
| page-rank | 10 | 6 | 60.0% | `other_build` | 3 |
| particlefilter | 26 | 9 | 34.6% | `missing_header` | 6 |
| pathfinder | 30 | 8 | 26.7% | `undeclared_identifier` | 12 |
| rsbench | 18 | 0 | 0.0% | `wrong_checksum` | 6 |
| scan | 18 | 2 | 11.1% | `other_build` | 8 |
| srad | 26 | 9 | 34.6% | `linker_error` | 6 |
| stencil1d | 26 | 14 | 53.8% | `other_build` | 6 |
| streamcluster | 22 | 1 | 4.5% | `undeclared_identifier` | 6 |
| xsbench | 22 | 1 | 4.5% | `wrong_checksum` | 9 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`other_build`** — 74 (25.1% of BUILD_FAIL)
2. **`missing_header`** — 68 (23.1% of BUILD_FAIL)
3. **`undeclared_identifier`** — 66 (22.4% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`opencl_jit_error`** — 57 (43.5% of RUN_FAIL)
2. **`wrong_exit_code`** — 36 (27.5% of RUN_FAIL)
3. **`segfault`** — 22 (16.8% of RUN_FAIL)

### Top VERIFY_FAIL Root Causes

1. **`wrong_numerical_output`** — 39 (88.6% of VERIFY_FAIL)
2. **`pass_overall_mislabel`** — 5 (11.4% of VERIFY_FAIL)

### Direction Asymmetry

- cuda→omp: 95/162 PASS (58.6%)
- cuda→omp_target: 0/30 PASS (0.0%)
- cuda→opencl: 8/81 PASS (9.9%)
- omp→cuda: 39/110 PASS (35.5%)
- omp→omp_target: 13/27 PASS (48.1%)
- omp→opencl: 39/100 PASS (39.0%)
- omp_target→cuda: 43/62 PASS (69.4%)
- omp_target→omp: 22/27 PASS (81.5%)
- opencl→cuda: 1/69 PASS (1.4%)
- opencl→omp: 11/76 PASS (14.5%)

### Compound Failures (Multiple Root Causes)

**107** results (22.6% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| missing_header + implicit_declaration | 26 |
| wrong_checksum + opencl_jit_error | 15 |
| missing_header + undeclared_identifier | 11 |
| missing_header + linker_error | 10 |
| undeclared_identifier + syntax_error | 10 |
| missing_target_api + undeclared_identifier | 8 |
| missing_target_api + linker_error | 7 |
| opencl_jit_error + data_file_missing | 7 |
| undeclared_identifier + redefinition | 7 |
| linker_error + implicit_declaration | 5 |

---

## Canonical Taxonomy (L0)

**Total:** 540  
**PASS:** 140 (25.9%)  
**Failures:** 400 (74.1%)

| Status | Count | % |
|--------|------:|--:|
| PASS | 140 | 25.9% |
| BUILD_FAIL | 263 | 48.7% |
| RUN_FAIL | 97 | 18.0% |
| VERIFY_FAIL | 37 | 6.9% |
| EXTRACTION_FAIL | 3 | 0.6% |

## Ablation Taxonomy (L1-L4)

**Total:** 204  
**PASS:** 131 (64.2%)  
**Failures:** 73 (35.8%)

| Level | Total | PASS | Pass Rate |
|-------|------:|-----:|----------:|
| L1 | 51 | 38 | 74.5% |
| L2 | 51 | 33 | 64.7% |
| L3 | 51 | 32 | 62.7% |
| L4 | 51 | 28 | 54.9% |

## Comparison: Canonical vs Ablation

- Canonical pass rate: 25.9%
- Ablation pass rate: 64.2%
- Delta: +38.3 pp
- *Ablation runs only on tasks that passed canonical, so higher pass rate is expected*
