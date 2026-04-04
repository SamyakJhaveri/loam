# Phase 02 Reflection: Benchmark Characterization Execution

**Topic:** `phase-02-characterization-execution`
**Date:** 2026-04-04
**Phase:** 02-benchmark-characterization-data (plans 02-01, 02-02, 02-03)

---

## 1. What Surprised Me

**The parallel agent schema divergence was exactly 8 mismatches, not 1-2.** Plans 02-01 (script) and 02-02 (tests) ran as independent agents. The plan's "Expected output JSON schema" (02-02-PLAN.md line 76-88) was a rough sketch, not a binding contract. The script author made reasonable naming decisions (`cuda_sloc`, nested `apis.{api}.tier`, `headline_payload_count`, `overall_tier`) that each individually make sense but collectively diverged from the test author's assumptions (`physical_sloc`, flat `tier`, `prompt_payload_count`, `tier`). The fix commit (419d105) touched all 8 at once. This is not a "miscommunication" -- it is the predictable consequence of two agents interpreting the same loose spec independently. The fact that there were exactly 8 (not 20+) suggests the plan was specific enough to constrain the coarse structure but too loose on field-level naming.

**The no-OMP kernel set is 9, not 5.** The 02-02 plan hardcoded 5 HeCBench kernels lacking OMP specs (convolution1d, jacobi, md, nqueen, page-rank). The actual count is 9: those 5, plus 3 deleted Rodinia phantoms (gaussian, huffman, hybridsort -- specs removed but manifest entries remain), plus dwt2d (which genuinely has no OMP variant in the Rodinia commit). This is an example of "documentation as ground truth" (anti-pattern #8 from workflow.md) -- the plan author assumed the known-issues list was complete instead of counting from disk. The script (02-01) silently handled all 9 correctly because it checked for OMP spec file existence; only the test's hardcoded expected-set needed updating.

**Four kernels have "undetected" language features, not just bptree.** The `grep_dir` function uses non-recursive `directory.glob(ext)`, which only searches top-level files. Four kernels (bptree, lavamd, lud, mummergpu) have all their `.cu` files in subdirectories (`kernel/`, `util/cuda/`, `cuda/`). The directories exist and are reachable, but the glob misses them. This means the language feature tier data in `benchmark_characterization.json` has 4 false "undetected" entries. For the paper, this needs fixing (all 4 kernels use `__global__` / `__shared__` and should be at least `cuda_basic`).

---

## 2. Pattern Proposal

**Pattern: Shared Interface Contract for Parallel Agent Outputs**

When two or more agents will execute in parallel and one produces output that the other validates, the plan must include a **binding interface contract** -- not a rough schema sketch, but an exact JSON path specification with field names, types, and nesting structure. This contract lives in the plan file and is referenced by both agent prompts.

**Codification:**

Before launching parallel agents where agent A produces data and agent B tests/validates it:

1. Write the exact output schema in a dedicated `## Interface Contract` section of the phase plan, specifying every JSON key name, its type, and its nesting depth. Use JSON Schema or a concrete example with all fields populated.
2. Include this contract verbatim in both agent prompts (not "see the plan" -- paste the actual contract).
3. Add a "Wave 1.5: Schema Reconciliation" step between parallel execution and dependent work. Run the test suite against the output and fix mismatches before proceeding. Budget 5 minutes for this step.

**Why this matters:** The 8 mismatches in Phase 02 cost one reconciliation commit and ~10 minutes of orchestrator time. For a larger phase with 20+ fields, this could balloon. The fix is cheap (write a more precise spec) and the cost of not doing it scales linearly with output complexity.

---

## 3. Prompt Improvement

**The plan should have specified the exact JSON output schema in both 02-01 and 02-02 plans, using concrete key names.**

The 02-02 plan included an "Expected output JSON schema" (lines 76-88) but it was pseudocode with placeholders like `{kernel_name: {...}}` and `"tier": str`. It said `physical_sloc` while the 02-01 plan said `omp_sloc / cuda_sloc` (implying the key would be `cuda_sloc`). Neither plan specified the nested `apis` structure for language features -- the test plan assumed flat `features_found` and `tier` at the kernel level, while the script plan said "tier assignment via regex grep" without specifying nesting.

**Concrete fix:** Replace the pseudocode schema in the plan with a complete JSON example, e.g.:

```json
{
  "sloc": {
    "per_kernel": {
      "bfs": {
        "kernel": "bfs",
        "suite": "rodinia",
        "cuda_sloc": 242,
        "omp_sloc": 198,
        "omp_cuda_ratio": 0.82,
        "num_source_files": 3,
        "num_target_files": 1
      }
    }
  },
  "language_features": {
    "per_kernel": {
      "bfs": {
        "kernel": "bfs",
        "suite": "rodinia",
        "apis": {
          "cuda": {"features_found": {"cuda_basic": ["__global__"]}, "tier": "cuda_basic"}
        },
        "overall_tier": "cuda_basic"
      }
    }
  }
}
```

This takes 5 minutes to write during planning and saves 10+ minutes during reconciliation. The ROI improves as the number of parallel agents increases.

---

## 4. Gotcha Discovered

**Non-recursive `glob()` in `grep_dir()` causes false "undetected" tiers for kernels with subdirectory source layouts.**

`scripts/analysis/benchmark_characterization.py` line 420 uses `directory.glob(ext)` to find source files. This is a non-recursive glob that only matches files in the immediate directory. Four Rodinia kernels store their `.cu`/`.c` files in subdirectories:

| Kernel | Directory | Subdirectories with source |
|--------|-----------|---------------------------|
| bptree | `cuda/b+tree/` | `kernel/`, `util/cuda/` |
| lavamd | `cuda/lavaMD/` | `kernel/`, `util/device/` |
| lud | `cuda/lud/` | `cuda/`, `base/`, `common/`, `tools/` |
| mummergpu | `cuda/mummergpu/` | (files are at top level, but OMP variant has subdirs) |

**Impact:** These 4 kernels show `overall_tier: "undetected"` in the characterization JSON. If this data flows into the paper's Table 1 (benchmark characterization), it would incorrectly suggest these kernels use no CUDA/OpenMP language features. All 4 actually use `__global__` and `__shared__` at minimum.

**Fix:** Change `directory.glob(ext)` to `directory.rglob(ext)` on line 420 of `benchmark_characterization.py`. This is a one-character change (`glob` to `rglob`) but affects the correctness of the language feature analysis for 4 out of 35 kernels (11.4%).

**Why this was not caught by tests or validation:** The test suite (`test_language_features_skip_missing_dirs`) only checks that *at least some* kernels have features. The validation script (`validate_characterization.py`) checks tier validity but accepts "undetected" as valid. Neither verifies that a kernel known to use `__global__` actually gets a CUDA tier. A spot-check test like `test_lavamd_has_cuda_features()` would have caught this.

---

*Reflection written by: Claude (Opus 4.6)*
*Session: Phase 02 post-execution reflection*
