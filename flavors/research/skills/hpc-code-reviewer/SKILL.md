---
name: hpc-code-reviewer
description: "Code review checklist for parallel code correctness in CUDA, OpenMP, and OpenCL. Use when reviewing LLM-generated parallel code translations, when auditing benchmark source code for correctness issues, when writing the paper's 'common failure modes' section, or when a translated kernel has a subtle VERIFY_FAIL that needs root cause analysis. Covers data races, memory model violations, synchronization bugs, numerical precision issues, and API-specific pitfalls."
---

# HPC Code Reviewer

Structured code review for parallel code correctness. Targets CUDA, OpenMP, and OpenCL
code — both human-written benchmark sources and LLM-generated translations.

**Trigger:** `/hpc-code-reviewer` or when reviewing parallel code for correctness.

## When to use

- Diagnosing VERIFY_FAIL in eval results (subtle correctness bugs)
- Reviewing LLM-generated translations for common parallel programming errors
- Auditing benchmark source code before adding to spec corpus
- Writing paper analysis of failure mode taxonomy

## Review Checklist

### 1. Data Races

**CUDA:**
- [ ] Multiple threads writing to same global memory location without atomics
- [ ] Shared memory accessed without `__syncthreads()` between write and read phases
- [ ] Warp-divergent code accessing shared memory (bank conflicts are perf, not correctness)

**OpenMP:**
- [ ] Shared variable written inside `parallel for` without `reduction`, `atomic`, or `critical`
- [ ] Loop-carried dependency without proper `ordered` or serialization
- [ ] `firstprivate`/`lastprivate` misuse — variable scope incorrect

**OpenCL:**
- [ ] Local memory (`__local`) accessed without `barrier(CLK_LOCAL_MEM_FENCE)`
- [ ] Global memory written by multiple work-items without atomic functions
- [ ] Missing `mem_fence()` between global reads and local writes

### 2. Memory Model Violations

- [ ] **CUDA:** Reading from `__shared__` before all threads in block have written (missing `__syncthreads()`)
- [ ] **OpenMP:** Assuming memory visibility without `flush` (implicit in most constructs, but explicit when using `omp_lock_t`)
- [ ] **OpenCL:** Mixing `CLK_LOCAL_MEM_FENCE` and `CLK_GLOBAL_MEM_FENCE` incorrectly
- [ ] **Cross-API:** Assuming same memory ordering guarantees across APIs

### 3. Synchronization Bugs

- [ ] Barrier inside conditional branch (undefined behavior in OpenMP and OpenCL)
- [ ] Missing barrier between producer-consumer phases in multi-pass algorithms
- [ ] Deadlock from nested critical sections or mismatched lock/unlock
- [ ] Over-synchronization (correct but kills performance — note but don't flag as bug)

### 4. Numerical Precision

- [ ] Reduction order difference producing different FP results (inherent — not a bug)
- [ ] Missing `volatile` on shared accumulator when order matters
- [ ] `float` vs `double` mismatch between source and translation
- [ ] Fused multiply-add (`fma`) vs separate multiply+add producing different results

### 5. API-Specific Pitfalls

**CUDA:**
- [ ] `texture<>` usage (removed in CUDA 12 — use texture objects)
- [ ] Deprecated memory management (`cudaMallocHost` vs `cudaHostAlloc`)
- [ ] Kernel launch with 0 threads in any dimension

**OpenMP:**
- [ ] `num_threads()` clause that silently reduces parallelism
- [ ] `schedule(static)` when `dynamic` is needed for load balance
- [ ] `collapse(2)` on non-rectangular loops

**OpenCL:**
- [ ] Kernel-only translation missing host-side buffer creation and enqueue
- [ ] Work-group size not evenly dividing global size
- [ ] Missing `clFinish()` / `clFlush()` before reading results

### 6. Translation-Specific Issues

- [ ] Leftover source-API identifiers that don't exist in target API
- [ ] Control flow restructuring that changes algorithm semantics
- [ ] Off-by-one errors from index mapping (CUDA 0-based thread ID → OpenMP loop bounds)
- [ ] Missing initialization of variables that the source API zero-initializes

## Severity Classification

| Severity | Meaning | Example |
|----------|---------|---------|
| **P0: Correctness** | Wrong results or crash | Data race on output array |
| **P1: Portability** | Works on some configs, fails on others | Hardcoded warp size (32) |
| **P2: Performance** | Correct but unnecessarily slow | Critical section around entire loop body |
| **P3: Style** | Correct but hard to maintain | Preserved CUDA naming in OpenMP code |

## Output Format

For each issue found, report:
```
[P<severity>] <category> — <one-line description>
  File: <path>:<line>
  Evidence: <relevant code snippet>
  Fix: <what the correct code should look like>
```
