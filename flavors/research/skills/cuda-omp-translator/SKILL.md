---
name: cuda-omp-translator
description: "CUDA↔OpenMP translation pattern guide for evaluating and reviewing LLM-generated parallel code translations. Use when reviewing eval results that involve CUDA-to-OpenMP or OpenMP-to-CUDA translation pairs, when writing paper sections about translation patterns, when diagnosing why a specific translation failed to build or verify, or when creating new specs for CUDA/OpenMP kernel pairs. Covers memory model mapping, kernel launch → parallel region patterns, shared memory → threadprivate, atomic operations, and common pitfalls that cause BUILD_FAIL or VERIFY_FAIL."
---

# CUDA ↔ OpenMP Translation Guide

Reference for evaluating LLM-generated translations between CUDA and OpenMP. Organized by
pattern category — each section describes the source construct, the correct target construct,
and the failure modes LLMs commonly produce.

**Trigger:** `/cuda-omp-translator` or when reviewing CUDA↔OMP eval results.

## When to use

- Reviewing why an LLM translation got BUILD_FAIL or VERIFY_FAIL
- Writing paper sections about translation difficulty or pattern analysis
- Comparing translation quality across models for specific construct types
- Creating new benchmark specs for CUDA/OpenMP kernel pairs

## Core Translation Patterns

### 1. Kernel Launch → Parallel Region

**CUDA:**
```c
__global__ void kernel(float *data, int n) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid < n) data[tid] = data[tid] * 2.0f;
}
// Launch: kernel<<<grid, block>>>(d_data, n);
```

**OpenMP equivalent:**
```c
#pragma omp parallel for
for (int tid = 0; tid < n; tid++) {
    data[tid] = data[tid] * 2.0f;
}
```

**Common LLM failures:**
- Preserving `blockIdx`/`threadIdx` arithmetic instead of using loop index
- Missing `parallel for` — writing just `#pragma omp parallel` without work distribution
- Adding unnecessary `num_threads()` clause that limits parallelism

### 2. Device Memory → Stack/Heap Allocation

**CUDA:** `cudaMalloc`, `cudaMemcpy` (host↔device transfers)
**OpenMP:** Direct pointer use (shared memory space)

**Common LLM failures:**
- Leaving `cudaMalloc`/`cudaFree` calls that don't compile without CUDA runtime
- Translating `cudaMemcpy` to `memcpy` when data is already accessible (unnecessary copy)
- Not removing `__device__` / `__host__` qualifiers

### 3. Shared Memory → Thread-Local or Reduction

**CUDA:** `__shared__ float smem[BLOCK_SIZE];`
**OpenMP:** Depends on usage pattern:
- Read-only tile → no equivalent needed (cache handles it)
- Reduction accumulator → `#pragma omp parallel for reduction(+:sum)`
- Thread-local scratch → stack variable inside parallel region

**Common LLM failures:**
- Declaring a global array as shared-memory substitute (data race)
- Missing reduction clause — writing `sum += x` without `reduction(+:sum)`
- Translating shared memory as `threadprivate` when it should be a reduction

### 4. Atomic Operations

**CUDA:** `atomicAdd(&result, val);`
**OpenMP:** `#pragma omp atomic` or `#pragma omp critical`

**Common LLM failures:**
- Using `critical` where `atomic` suffices (performance kill, not correctness)
- Omitting atomic entirely — data race on shared accumulator
- Wrapping entire loop body in `critical` instead of just the update

### 5. Synchronization

**CUDA:** `__syncthreads()` (block-level barrier)
**OpenMP:** `#pragma omp barrier` (team-level barrier)

**Common LLM failures:**
- Placing barrier inside conditional (undefined behavior in OpenMP)
- Translating every `__syncthreads()` literally when the barrier is unnecessary in the flat parallel model
- Missing barrier when translating multi-phase algorithms (e.g., prefix scan)

### 6. Grid-Stride Loops

**CUDA:**
```c
for (int i = tid; i < n; i += gridDim.x * blockDim.x) { ... }
```

**OpenMP:** The `parallel for` schedule handles distribution — the grid-stride pattern disappears entirely.

**Common LLM failure:** Preserving the stride arithmetic inside the OMP parallel for, producing correct but unnecessarily complex code.

## Reverse Direction: OpenMP → CUDA

The reverse translation (OpenMP → CUDA) has distinct failure modes:

- **Missing bounds check:** OpenMP `parallel for` handles bounds implicitly; CUDA kernels need explicit `if (tid < n)` guards
- **Missing device memory management:** Forgetting `cudaMalloc`/`cudaMemcpy` for data that was just a pointer in OpenMP
- **Incorrect grid/block sizing:** LLMs often hardcode `<<<1, 256>>>` regardless of problem size
- **Missing `__global__` qualifier:** Defining the kernel as a regular function

## Diagnosis Checklist for Failed Translations

When an eval result shows BUILD_FAIL or VERIFY_FAIL for a CUDA↔OMP pair:

1. **BUILD_FAIL** — check for:
   - Leftover CUDA-specific types (`dim3`, `cudaError_t`, `__shared__`)
   - Missing OpenMP pragma on parallel loops
   - CUDA header includes (`cuda_runtime.h`) still present
   - Missing `-fopenmp` in build command (spec issue, not translation issue)

2. **VERIFY_FAIL** — check for:
   - Data races (missing `atomic`/`reduction`/`critical`)
   - Off-by-one in loop bounds vs CUDA thread index calculation
   - Floating-point reduction order differences (inherent — not a bug, see known-issues.md)
   - Uninitialized variables that CUDA zero-initializes but OpenMP doesn't

## Project-Specific Notes

- FP reduction-order divergence is common in parallel code — faithful translations may produce different bit-exact results due to floating-point associativity
- Always check `known-issues.md` KNOWN_FAIL list before investigating a failed translation
- Some synthesis asymmetries exist where macros or preprocessor directives differ between source and target paradigms
