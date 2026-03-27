# Error Taxonomy — ParBench LLM Evaluation Results

**Total results:** 500  
**PASS:** 169 (33.8%)  
**Failures:** 331 (66.2%)

## Table 1: Overall Status Distribution

| Status | Count | % of Total |
|--------|------:|----------:|
| PASS | 169 | 33.8% |
| BUILD_FAIL | 202 | 40.4% |
| RUN_FAIL | 89 | 17.8% |
| EXTRACTION_FAIL | 39 | 7.8% |
| ERROR | 1 | 0.2% |
| **Total** | **500** | **100.0%** |

## Table 2: BUILD_FAIL Root Cause Categories

*202 total BUILD_FAIL results classified into 10 categories.*

| # | Category | Count | % of BUILD_FAIL | Description |
|--:|----------|------:|----------------:|-------------|
| 1 | `undeclared_identifier` | 65 | 32.2% | Function, variable, or type not declared/defined in scope |
| 2 | `linker_error` | 41 | 20.3% | Compilation succeeded but linking failed (undefined references, etc.) |
| 3 | `missing_header` | 41 | 20.3% | Missing or wrong #include directive — file not found |
| 4 | `syntax_error` | 28 | 13.9% | Parse errors, malformed code, unexpected tokens |
| 5 | `retained_cuda_types` | 9 | 4.5% | LLM retained CUDA-specific types (float3, dim3, etc.) in non-CUDA target |
| 6 | `type_error` | 6 | 3.0% | Type mismatches, wrong function signatures, incompatible conversions |
| 7 | `retained_cuda_api` | 6 | 3.0% | LLM retained CUDA API calls/keywords in non-CUDA target code |
| 8 | `other_build` | 4 | 2.0% | Build failures not matching any specific pattern |
| 9 | `redefinition` | 1 | 0.5% | Duplicate or conflicting definitions of types/functions/variables |
| 10 | `implicit_declaration` | 1 | 0.5% | Missing function prototypes — implicit declaration warnings promoted to errors |
| | **Total** | **202** | **100.0%** | |

## Table 3: RUN_FAIL Root Cause Categories

*89 total RUN_FAIL results classified into 7 categories.*

| # | Category | Count | % of RUN_FAIL | Description |
|--:|----------|------:|-------------:|-------------|
| 1 | `wrong_checksum` | 38 | 42.7% | Program ran to completion but output checksum was incorrect |
| 2 | `wrong_args` | 35 | 39.3% | Translated binary expects different arguments than spec provides |
| 3 | `simulation_mode_unsupported` | 6 | 6.7% | XSBench translated code used wrong simulation mode (history vs event) |
| 4 | `gpu_memory_error` | 4 | 4.5% | CUDA illegal memory access during kernel execution |
| 5 | `segfault` | 3 | 3.4% | Process killed by SIGSEGV (signal 11) — null pointer or buffer overflow |
| 6 | `data_file_missing` | 2 | 2.2% | Required input data file not found at expected path |
| 7 | `abort` | 1 | 1.1% | Process killed by SIGABRT — stack smashing, assertion failure, or abort() |
| | **Total** | **89** | **100.0%** | |

## Table 4: EXTRACTION_FAIL Root Cause Categories

*39 total EXTRACTION_FAIL results classified into 1 categories.*

| # | Category | Count | % of EXTRACTION_FAIL | Description |
|--:|----------|------:|--------------------:|-------------|
| 1 | `no_parseable_code` | 39 | 100.0% | LLM response did not contain parseable code for expected target files |
| | **Total** | **39** | **100.0%** | |

## Table 5: BUILD_FAIL Categories by Model

| Category | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile | Total |
|----------|------:|------:|------:|------:|------:|
| `undeclared_identifier` | 0 | 6 | 21 | 38 | 65 |
| `linker_error` | 2 | 3 | 26 | 10 | 41 |
| `missing_header` | 2 | 6 | 19 | 14 | 41 |
| `syntax_error` | 0 | 0 | 21 | 7 | 28 |
| `retained_cuda_types` | 0 | 0 | 5 | 4 | 9 |
| `type_error` | 0 | 1 | 3 | 2 | 6 |
| `retained_cuda_api` | 0 | 0 | 5 | 1 | 6 |
| `other_build` | 0 | 0 | 0 | 4 | 4 |
| `redefinition` | 0 | 0 | 0 | 1 | 1 |
| `implicit_declaration` | 0 | 0 | 0 | 1 | 1 |
| **Total** | **4** | **16** | **100** | **82** | **202** |

## Table 6: BUILD_FAIL Categories by Direction

| Category | cuda→omp | omp→cuda | opencl→omp | opencl→omp_target | cuda→omp_target | omp→omp_target | omp_target→cuda | opencl→cuda | omp_target→omp | Total |
|----------|------:|------:|------:|------:|------:|------:|------:|------:|------:|------:|
| `undeclared_identifier` | 31 | 17 | 2 | 4 | 0 | 0 | 7 | 1 | 3 | 65 |
| `linker_error` | 24 | 4 | 0 | 1 | 3 | 9 | 0 | 0 | 0 | 41 |
| `missing_header` | 33 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 41 |
| `syntax_error` | 10 | 1 | 8 | 5 | 1 | 0 | 0 | 3 | 0 | 28 |
| `retained_cuda_types` | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 9 |
| `type_error` | 1 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 6 |
| `retained_cuda_api` | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |
| `other_build` | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 4 |
| `redefinition` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `implicit_declaration` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| **Total** | **116** | **33** | **10** | **10** | **9** | **9** | **8** | **4** | **3** | **202** |

## Table 7: RUN_FAIL Categories by Model

| Category | azure-gpt-4.1 | claude-sonnet-4-6 | gemini-2.5-flash-lite | groq-llama-3.3-70b-versatile | Total |
|----------|------:|------:|------:|------:|------:|
| `wrong_checksum` | 0 | 13 | 15 | 10 | 38 |
| `wrong_args` | 4 | 17 | 10 | 4 | 35 |
| `simulation_mode_unsupported` | 0 | 1 | 5 | 0 | 6 |
| `gpu_memory_error` | 0 | 0 | 0 | 4 | 4 |
| `segfault` | 0 | 0 | 2 | 1 | 3 |
| `data_file_missing` | 0 | 1 | 1 | 0 | 2 |
| `abort` | 0 | 0 | 0 | 1 | 1 |
| **Total** | **4** | **32** | **33** | **20** | **89** |

## Table 8: Complete Status Distribution by Model

| Model | Total | PASS | BUILD_FAIL | RUN_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-------|------:|-----:|----------:|--------:|--------------:|------:|----------:|
| azure-gpt-4.1 | 17 | 9 | 4 | 4 | 0 | 0 | 52.9% |
| claude-sonnet-4-6 | 161 | 113 | 16 | 32 | 0 | 0 | 70.2% |
| gemini-2.5-flash-lite | 161 | 17 | 100 | 33 | 11 | 0 | 10.6% |
| groq-llama-3.3-70b-versatile | 161 | 30 | 82 | 20 | 28 | 1 | 18.6% |

## Table 9: Complete Status Distribution by Direction

| Direction | Total | PASS | BUILD_FAIL | RUN_FAIL | EXTRACTION_FAIL | ERROR | Pass Rate |
|-----------|------:|-----:|----------:|--------:|--------------:|------:|----------:|
| cuda→omp | 287 | 110 | 116 | 39 | 22 | 0 | 38.3% |
| cuda→omp_target | 15 | 5 | 9 | 0 | 1 | 0 | 33.3% |
| cuda→opencl | 15 | 5 | 0 | 10 | 0 | 0 | 33.3% |
| omp→cuda | 63 | 17 | 33 | 10 | 3 | 0 | 27.0% |
| omp→omp_target | 15 | 4 | 9 | 1 | 1 | 0 | 26.7% |
| omp→opencl | 15 | 5 | 0 | 6 | 4 | 0 | 33.3% |
| omp_target→cuda | 15 | 6 | 8 | 0 | 1 | 0 | 40.0% |
| omp_target→omp | 15 | 2 | 3 | 8 | 1 | 1 | 13.3% |
| omp_target→opencl | 15 | 5 | 0 | 9 | 1 | 0 | 33.3% |
| opencl→cuda | 15 | 5 | 4 | 1 | 5 | 0 | 33.3% |
| opencl→omp | 15 | 0 | 10 | 5 | 0 | 0 | 0.0% |
| opencl→omp_target | 15 | 5 | 10 | 0 | 0 | 0 | 33.3% |

## Table 10: Per-Kernel Pass Rate and Primary Failure Mode

| Kernel | Total | PASS | Pass Rate | Primary Failure Mode | Primary Failure Count |
|--------|------:|-----:|----------:|---------------------|---------------------:|
| backprop | 19 | 11 | 57.9% | `linker_error` | 3 |
| bfs | 19 | 12 | 63.2% | `linker_error` | 5 |
| bptree | 19 | 7 | 36.8% | `missing_header` | 8 |
| cfd | 19 | 7 | 36.8% | `retained_cuda_types` | 9 |
| heartwall | 19 | 0 | 0.0% | `undeclared_identifier` | 10 |
| hotspot | 19 | 0 | 0.0% | `wrong_args` | 13 |
| hotspot3d | 19 | 13 | 68.4% | `undeclared_identifier` | 4 |
| kmeans | 16 | 7 | 43.8% | `linker_error` | 4 |
| lavamd | 19 | 12 | 63.2% | `missing_header` | 5 |
| lud | 19 | 10 | 52.6% | `syntax_error` | 3 |
| myocyte | 19 | 2 | 10.5% | `missing_header` | 15 |
| nn | 19 | 13 | 68.4% | `data_file_missing` | 2 |
| nw | 19 | 0 | 0.0% | `wrong_args` | 10 |
| particlefilter | 19 | 8 | 42.1% | `missing_header` | 7 |
| pathfinder | 19 | 14 | 73.7% | `syntax_error` | 3 |
| srad | 19 | 0 | 0.0% | `wrong_args` | 11 |
| streamcluster | 19 | 5 | 26.3% | `undeclared_identifier` | 8 |
| xsbench | 180 | 48 | 26.7% | `wrong_checksum` | 38 |

## Key Findings

### Top BUILD_FAIL Root Causes

1. **`undeclared_identifier`** — 65 (32.2% of BUILD_FAIL)
2. **`linker_error`** — 41 (20.3% of BUILD_FAIL)
3. **`missing_header`** — 41 (20.3% of BUILD_FAIL)

### Top RUN_FAIL Root Causes

1. **`wrong_checksum`** — 38 (42.7% of RUN_FAIL)
2. **`wrong_args`** — 35 (39.3% of RUN_FAIL)
3. **`simulation_mode_unsupported`** — 6 (6.7% of RUN_FAIL)

### Direction Asymmetry

- cuda→omp: 110/287 PASS (38.3%)
- cuda→omp_target: 5/15 PASS (33.3%)
- cuda→opencl: 5/15 PASS (33.3%)
- omp→cuda: 17/63 PASS (27.0%)
- omp→omp_target: 4/15 PASS (26.7%)
- omp→opencl: 5/15 PASS (33.3%)
- omp_target→cuda: 6/15 PASS (40.0%)
- omp_target→omp: 2/15 PASS (13.3%)
- omp_target→opencl: 5/15 PASS (33.3%)
- opencl→cuda: 5/15 PASS (33.3%)
- opencl→omp: 0/15 PASS (0.0%)
- opencl→omp_target: 5/15 PASS (33.3%)

### Compound Failures (Multiple Root Causes)

**106** results (32.0% of failures) have secondary error categories.

| Primary + Secondary | Count |
|---------------------|------:|
| wrong_checksum + opencl_jit_error | 25 |
| missing_header + implicit_declaration | 16 |
| linker_error + implicit_declaration | 14 |
| undeclared_identifier + syntax_error | 13 |
| missing_header + linker_error | 8 |
| missing_header + undeclared_identifier | 7 |
| retained_cuda_types + undeclared_identifier | 7 |
| missing_header + type_error | 6 |
| retained_cuda_api + missing_header | 5 |
| retained_cuda_api + undeclared_identifier | 5 |
