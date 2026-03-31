# Eval Campaign Findings Log

> Collected observations from eval runs to incorporate into the SC26 paper.
> Each finding includes the raw evidence and suggested paper section placement.
> Revisit once all eval campaigns are complete.

---

## Finding 1: Multi-File Translation Consistency Failure in OpenCL-to-CUDA (2026-03-31)

**Model:** Qwen 3.5 397B (together-qwen-3.5-397b-a17b)
**Direction:** opencl-to-cuda
**Kernel:** rodinia-lavamd
**Augmentation levels:** L0, L1, L2, L3, L4 — all BUILD_FAIL (15/15 attempts failed)
**Result files:** `results/evaluation/together-qwen-3.5-397b-a17b/rodinia-lavamd-opencl-to-rodinia-lavamd-cuda*.json`
**Cross-model data:** No other models have opencl-to-cuda lavamd results yet. Cannot confirm
whether this is Qwen-specific until other model campaigns complete.
**Critic review:** Adversarial review performed 2026-03-31. Original "semantic renaming" thesis
revised to "multi-file consistency failure" based on per-level evidence.

### Observation

The model translates OpenCL kernel computational patterns to CUDA correctly (`__global__`,
`blockIdx.x`, `threadIdx.x`, `__syncthreads()`) but **fails to produce a compilable
multi-file CUDA program**. The failure modes vary across augmentation levels — this is NOT
a single consistent bug, but a family of related multi-file consistency errors.

### Per-Level Error Taxonomy

| Level | Kernel function name | Naming correct? | Primary failure mode |
|-------|---------------------|-----------------|---------------------|
| L0 | `kernel_gpu_opencl` | NO | Identifier renaming failure (retained source name) |
| L1 | `kernel_gpu_cuda` | YES | Phantom dependencies (`timing.h`, `checkCUDAError`, `setdevice`) |
| L2 | `kernel_gpu_opencl` | NO | Identifier renaming failure (retained source name) |
| L3 | `kernel_gpu_cuda` | YES | Undefined helpers (`setdevice`, `checkCUDAError`) + missing symbol |
| L4 | `kernel_gpu_cuda` | YES | Undefined helpers (`setdevice`) + missing kernel launch symbol |

**Key insight:** The "semantic renaming failure" (keeping `kernel_gpu_opencl` in CUDA code) only
occurs at L0 and L2. At L1, L3, and L4, the model correctly renames the function but fails on
different issues: phantom include paths, undefined helper functions, and (in some attempts)
missing `<<<>>>` kernel launch syntax.

### Retry Behavior (3 attempts per level — consistent pattern)

All 5 levels share the same attempt-1 error: `timing.h` not found (model hallucinating a
non-existent header). Subsequent attempts diverge per level:

| Attempt | Consistent across levels? | Common errors |
|---------|--------------------------|---------------|
| 1 | YES — all 5 levels | `timing.h` not found (phantom dependency) |
| 2 | NO — varies by level | Mix of `checkCUDAError`/`setdevice` undefined, wrong include paths |
| 3 | NO — varies by level | Mix of naming bugs (L0/L2) or dependency bugs (L1/L3/L4) |

Each retry introduces **new error categories** without converging toward a fix. The model
cannot effectively diagnose multi-file compilation failures from compiler error feedback.

### Additional Error: Missing Kernel Launch Syntax

In several attempts (L0 final, L2, L4 attempt 3), the wrapper calls the kernel as a regular
C function (`kernel_gpu_cuda(...)`) rather than using CUDA kernel launch syntax
(`kernel_gpu_cuda<<<grid, block>>>(...)`). This is a separate error class — the model
understands CUDA kernel syntax in the `.cu` file but not the host-side launch protocol.

### Pipeline Verification (CONFIRMED correct)

Pipeline is correctly configured (not a pipeline bug):
- `translation_type: "full_program"` (correct for CUDA targets — both kernel + wrapper rewritten)
- `run_args_mode: "cross_api_source_args"` (correct for cross-API full-program translation)
- `verification_mode: "cross_api_combined_pattern"` (correct)
- `run_arguments_used: null` in all files (pipeline correctly short-circuits at BUILD_FAIL)

### Paper Relevance

**Suggested sections:** Failure Analysis (Section 6), Discussion

**Key points for the paper:**

1. **Failure taxonomy — "multi-file translation consistency failure"**: Full-program
   translations (where the LLM must rewrite both kernel and host code) expose a class
   of errors absent from kernel-only translations: phantom dependencies, cross-file
   identifier inconsistency, undefined helper functions, and missing host-side launch
   syntax. These are distinct from single-file syntax errors or wrong API calls.

2. **Self-repair ineffectiveness on multi-file errors**: The 3-attempt retry cycle does
   not converge toward a fix across any of the 5 augmentation levels (0/15 attempts
   succeed). Each retry introduces new error categories rather than addressing the root
   cause. Self-repair with compiler error feedback appears insufficient for errors that
   require coordinating changes across multiple files.

3. **Hybrid pipeline opportunity (narrower than originally claimed)**: A simple rename
   post-processing pass would only fix L0 and L2 (2/5 levels). A more comprehensive
   hybrid pipeline would need dependency resolution and scaffold generation to address
   L1/L3/L4 failures. Future work should explore multi-stage verification-correction
   pipelines rather than single-pass post-processing.

4. **Augmentation level invariance at the outcome level**: All levels produce BUILD_FAIL,
   but the *failure modes differ* across levels (L0/L2 naming bug vs. L1/L3/L4 dependency
   bugs). Augmentation does not rescue the translation outcome, but it does perturb which
   specific errors the model makes — suggesting the model's failure is not deterministic
   but reflects general difficulty with multi-file CUDA program scaffolding.

5. **No cross-model comparison yet**: This finding is currently single-model (Qwen 3.5 397B).
   Cannot conclude whether the failure pattern is model-specific or direction-specific until
   other models' opencl-to-cuda campaigns complete. Revisit when data is available.

### Related Work Connection

- TransCoder (Roziere et al., 2020): Neural code translators and identifier mapping
  (relevant to L0/L2 renaming failure subcategory)
- SWE-bench: Analogous "small fix, big impact" pattern — but our evidence shows the
  fix is NOT always small (L1/L3/L4 need scaffold-level changes, not just renaming)

---

<!-- Add new findings below this line -->
