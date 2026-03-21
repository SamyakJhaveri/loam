# Session 2: Targeted Retest of 8 M10b-Fixed Specs at L0

> **Depends on:** Session 1 (committed)
> **Blocks:** Session 3 (full retest)
> **Estimated time:** 30–45 minutes (builds take time)
> **Thinking level:** `think hard` (debugging if failures occur)

---

## Objective

Run `harness verify` on the 8 specs that had M10b fixes applied. Record actual pass/fail
with real output — no "expected" claims. Also spot-check the 4 KNOWN_FAIL specs to confirm
they still fail for the documented reasons.

---

## Claude Code Prompt

Copy-paste this into a fresh `/clear` session:

```
I need to complete Session 2 of the Sprint Audit Fix Plan: targeted retest of 8 M10b-fixed specs.

**Pre-check:** Confirm Session 1 is committed:
```bash
git log --oneline -3
```
The most recent commit should mention "ChangeFunctionNames" or "evaluation.md". If not, STOP — Session 1 must be done first.

## Phase 1: Activate environment

```bash
source env_parbench/bin/activate
```

## Phase 2: Run the 8 M10b-fixed specs (sequential, one at a time)

Run each spec through `harness verify` and RECORD the actual stdout/stderr. Do NOT skip output.

**Previously BUILD_FAIL (5 specs — toolchain fixes applied):**

1. `python3 -m harness -v verify specs/rodinia-cfd-cuda.json`
   - Fix was: KERNEL_DIM include path for helper_cuda.h
   - Expected: BUILD_PASS → RUN → VERIFY

2. `python3 -m harness -v verify specs/rodinia-cfd-opencl.json`
   - Fix was: -DCL_TARGET_OPENCL_VERSION=120 + if(!file) instead of if(file==NULL)
   - Expected: BUILD_PASS → RUN → VERIFY

3. `python3 -m harness -v verify specs/rodinia-pathfinder-opencl.json`
   - Fix was: data→grid_data rename + -DCL_TARGET_OPENCL_VERSION=120
   - Expected: BUILD_PASS → RUN → VERIFY

4. `python3 -m harness -v verify specs/rodinia-mummergpu-cuda.json`
   - Fix was: #include <unistd.h> in suffix-tree.cpp
   - Expected: BUILD_PASS → RUN → VERIFY

5. `python3 -m harness -v verify specs/rodinia-mummergpu-omp.json`
   - Fix was: #include <unistd.h> in suffix-tree.cpp
   - Expected: BUILD_PASS → RUN → VERIFY

**Previously FAIL (3 specs — arg/filename fixes applied):**

6. `python3 -m harness -v verify specs/rodinia-hotspot-omp.json`
   - Fix was: restored grid_cols arg (7 args total)
   - Expected: RUN_PASS → VERIFY_PASS

7. `python3 -m harness -v verify specs/rodinia-nw-omp.json`
   - Fix was: restored num_threads arg (3 args total)
   - Expected: RUN_PASS → VERIFY_PASS

8. `python3 -m harness -v verify specs/rodinia-nn-cuda.json`
   - Fix was: filelist.txt → filelist_4
   - Expected: RUN_PASS → VERIFY_PASS

## Phase 3: Spot-check the 4 KNOWN_FAIL specs

These should STILL fail. Run them to confirm failure mode matches documentation:

9. `python3 -m harness -v verify specs/rodinia-kmeans-cuda.json`
   - Expected: BUILD_FAIL (texture<> removed in CUDA 12)

10. `python3 -m harness -v verify specs/rodinia-hybridsort-cuda.json`
    - Expected: BUILD_FAIL (GL/glew.h not found)

11. `python3 -m harness -v verify specs/rodinia-nn-opencl.json`
    - Expected: RUN_FAIL or SIGSEGV (OpenCL runtime crash)

12. `python3 -m harness -v verify specs/rodinia-kmeans-opencl.json`
    - Expected: RUN_FAIL or SIGSEGV (exit code -11)

## Phase 4: Record results

Create a results summary showing actual outcomes. Format:

```
## M10b Targeted Retest Results (Session 2)

| # | Spec | Previous Status | Current Status | Notes |
|---|------|----------------|----------------|-------|
| 1 | rodinia-cfd-cuda | BUILD_FAIL | ??? | ... |
...
```

## Phase 5: Handle failures

**If any of the 8 M10b specs FAIL:**
- Read the build/run error output carefully
- Check the spec JSON for correctness (build command, run args)
- Check the source code if needed
- Fix the issue IN THIS SESSION before committing
- Re-run the fixed spec to confirm PASS

**If a KNOWN_FAIL spec unexpectedly PASSES:**
- This is good news — document it and remove from KNOWN_FAIL list

## Phase 6: Update known-issues.md

Add a verification record to `.claude/rules/known-issues.md`:
```
## Session 2 Targeted Retest (2026-03-2X)

8/8 M10b-fixed specs verified PASS at L0.
4/4 KNOWN_FAIL specs confirmed still failing for documented reasons.
```

## Phase 7: Commit and Push

Commit ONLY after ALL verification passes. Then push immediately:

```
Verify M10b spec fixes: N/8 PASS at L0 (targeted retest)

- Ran harness verify on all 8 M10b-fixed specs
- [list actual results]
- 4 KNOWN_FAIL specs confirmed still failing
- [any additional fixes applied in this session]
```

```bash
git push origin main
```
```

---

## Specs Reference

### M10b-Fixed Specs (8 — expecting PASS)

| Spec | Fix Applied | Build Command Key Change |
|------|-------------|-------------------------|
| `rodinia-cfd-cuda` | `KERNEL_DIM='-I.../OpenACC/SDK/include'` | Finds `helper_cuda.h` |
| `rodinia-cfd-opencl` | `FLAGS` includes `-DCL_TARGET_OPENCL_VERSION=120` | OpenCL 3.0 compat |
| `rodinia-pathfinder-opencl` | `data`→`grid_data` + CL version flag | C++17 `std::data()` conflict |
| `rodinia-mummergpu-cuda` | `#include <unistd.h>` in source | GCC 12 implicit removal |
| `rodinia-mummergpu-omp` | `#include <unistd.h>` in source | GCC 12 implicit removal |
| `rodinia-hotspot-omp` | 7 args restored (was 6) | `hotspot_openmp.cpp:282` checks `argc!=8` |
| `rodinia-nw-omp` | 3 args restored (was 2) | `needle.cpp:249` checks `argc==4` |
| `rodinia-nn-cuda` | `filelist.txt`→`filelist_4` | File didn't exist |

### KNOWN_FAIL Specs (4 — expecting continued failure)

| Spec | Expected Failure | Root Cause |
|------|-----------------|------------|
| `rodinia-kmeans-cuda` | BUILD_FAIL | `texture<>` removed in CUDA 12 |
| `rodinia-hybridsort-cuda` | BUILD_FAIL | `GL/glew.h` not found (needs libglew-dev) |
| `rodinia-nn-opencl` | SIGSEGV | Pre-existing OpenCL runtime crash |
| `rodinia-kmeans-opencl` | SIGSEGV (exit -11) | Pre-existing OpenCL runtime crash |

## Troubleshooting Guide

**If cfd-cuda BUILD_FAIL persists:**
- Check if `helper_cuda.h` exists at the path in the spec's KERNEL_DIM
- Run: `ls /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/examples/OpenACC/SDK/include/helper_cuda.h`

**If mummergpu BUILD_FAIL persists:**
- Check if the `#include <unistd.h>` was actually added to the source
- Run: `head -20 rodinia/rodinia-src/cuda/mummergpu/src/suffix-tree.cpp`

**If pathfinder-opencl BUILD_FAIL persists:**
- Check if `data` was renamed to `grid_data` throughout
- Run: `grep -n "int\* data" rodinia/rodinia-src/opencl/pathfinder/main.cpp` (should return nothing)

**If nw-omp or hotspot-omp FAIL (wrong output):**
- The args are critical. Cross-check spec JSON against source argc:
  - `grep -n argc rodinia/rodinia-src/openmp/nw/needle.cpp`
  - `grep -n argc rodinia/rodinia-src/openmp/hotspot/hotspot_openmp.cpp`

## Success Criteria

- [ ] All 8 M10b specs show PASS
- [ ] All 4 KNOWN_FAIL specs fail for documented reasons
- [ ] Results recorded with actual output (not "expected")
- [ ] Any failures investigated and fixed in this session
- [ ] known-issues.md updated with verification record
- [ ] Verified, committed, and pushed to remote
