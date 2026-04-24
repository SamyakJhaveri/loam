# Handoff: Le's Machine Setup Debugging Session (2026-04-23)

## Goal
Get the 88-spec verify sweep to PASS 88/88 on Le's machine (Argonne Polaris/Eagle cluster) before running the azure-gpt-5.4 evaluation campaign.

## Le's Machine Environment
- **Cluster:** Argonne Eagle/Polaris (`/lus/eagle/projects/argonne_tpc/chen/repo/parbench_sam`)
- **GPU:** 4x NVIDIA A100-SXM4-40GB (compute capability 8.0 → `sm_80`)
- **System GCC:** 7.5.0 (SUSE Linux) — too old, must load module
- **Module GCC:** `gcc-native/12.3` available
- **NVIDIA HPC SDK:** 25.5 (at `/opt/nvidia/hpc_sdk/Linux_x86_64/25.5/`)
- **CUDA:** 12.9 (at `/soft/compilers/cudatoolkit/cuda-12.9.1/`)
- **nvc++:** `/opt/nvidia/hpc_sdk/Linux_x86_64/25.5/compilers/bin/nvc++`
- **OpenCL headers:** `/soft/compilers/cudatoolkit/cuda-12.9.1/targets/x86_64-linux/include/CL/cl.h`

## Starting Point
Le followed HANDOFF-LE-GPT54-EVAL.md through §5e (full 88-spec sweep). Initial result: **PASS 81/88, FAIL 7**.

## What We Fixed (confirmed working)
| Spec | Problem | Fix | Status |
|------|---------|-----|--------|
| rodinia-heartwall-opencl | `CL/cl.h` not found by `timing.c` | Set `CPATH` and `C_INCLUDE_PATH` to include OpenCL headers dir | PASS |
| rodinia-myocyte-opencl | Same `CL/cl.h` issue | Same CPATH fix | PASS |
| hecbench-stencil1d-cuda | Spec `run.executable=./stencil_1d` but Le's HeCBench Makefile produces `main` | Changed spec `run.executable` to `./main` | PASS |
| hecbench-stencil1d-omp | Same executable mismatch + wrong build command in spec | Fixed build command to `make -f Makefile.aomp CC=g++ DEVICE=cpu` + executable to `main` | PASS |
| rodinia-particlefilter-omp Makefile | Le's Makefile had `-O0` instead of `-O3` | `git checkout -- openmp/particlefilter/Makefile` | Fixed (still crashes — see below) |

## Current State (after last attempt)
**PASS 76/88, FAIL 12** — regression caused by incomplete path replacement after `git checkout -- specs/`.

### Root Cause of Regression
We did `git checkout -- specs/` to restore all specs from git (fixing corrupt build commands), then re-ran §4c path replacements. But §4c only replaces:
- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda` → Le's CUDA path
- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc++` → Le's nvc++ path
- `sm_89` → `sm_80`

It MISSES other paths under the old HPC SDK root:
- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc` (without `++`) — used by omp_target specs
- `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/examples/OpenACC/SDK/include` — used by rodinia-cfd-cuda

### The 12 Current Failures

**Category 1: Incomplete path replacement (fixable — 4 specs)**
| Spec | Error | Fix |
|------|-------|-----|
| rodinia-cfd-cuda | BUILD_FAIL — old `24.3/examples/OpenACC` path | Replace all `24.3` → `25.5` |
| rsbench-rsbench-omp_target | BUILD_FAIL — old `24.3/compilers/bin/nvc` path | Same |
| xsbench-xsbench-omp_target | BUILD_FAIL — same | Same |
| (stencil1d-omp/cuda exe names) | git checkout undid our executable name fixes | Re-apply |

**Category 2: CUDA runtime failures (need investigation — 3 specs)**
| Spec | Error | Notes |
|------|-------|-------|
| mixbench-mixbench-cuda | BUILD PASS, RUN FAIL (exit_code) | May be A100-specific |
| rsbench-rsbench-cuda | BUILD PASS (44s), RUN FAIL (stdout_pattern) | Output doesn't match pattern |
| xsbench-xsbench-cuda | BUILD PASS (46s), RUN FAIL (stdout_pattern) | Output doesn't match pattern |

**Category 3: HeCBench OMP self-check failures (4 specs)**
| Spec | Error | Notes |
|------|-------|-------|
| hecbench-floydwarshall-omp | VERIFY FAIL (stdout_pattern) | Self-check fails on A100 |
| hecbench-heat2d-omp | VERIFY FAIL (stdout_pattern) | Same |
| hecbench-iso2dfd-omp | RUN FAIL + VERIFY FAIL | Euclidean norm=44.1 even with OMP_NUM_THREADS=1 |
| hecbench-scan-omp | VERIFY FAIL (stdout_pattern) | Same |

**Category 4: Environment-specific runtime crashes (2 specs)**
| Spec | Error | Notes |
|------|-------|-------|
| rodinia-bptree-opencl | `double free or corruption (out)` | A100 OpenCL runtime bug |
| rodinia-particlefilter-omp | `double free or corruption (!prev)` | Heap corruption, persists with -O3 |

## Next Steps (in order)

### Step 1: Fix the path replacement (do this FIRST)
```bash
cd "$PROJECT_ROOT"

# Nuclear option: replace ALL old HPC SDK version refs
find specs/ -name '*.json' -exec sed -i 's|/opt/nvidia/hpc_sdk/Linux_x86_64/24.3|/opt/nvidia/hpc_sdk/Linux_x86_64/25.5|g' {} +

# Verify nothing from 24.3 remains:
grep -rl "24\.3" specs/*.json | head -5
# Should return nothing

# Re-apply stencil1d executable fixes
python3 -c "
import json
for path in ['specs/hecbench-stencil1d-omp.json', 'specs/hecbench-stencil1d-cuda.json']:
    d = json.load(open(path))
    d['build']['outputs']['executable'] = 'main'
    d['run']['executable'] = './main'
    json.dump(d, open(path, 'w'), indent=2)
    print(f'Fixed executable in {path}')
"
```

### Step 2: Ensure correct module environment
```bash
module load PrgEnv-nvidia/8.6.0
module load gcc-native/12.3
export CPATH="/soft/compilers/cudatoolkit/cuda-12.9.1/targets/x86_64-linux/include:${CPATH:-}"
export C_INCLUDE_PATH="/soft/compilers/cudatoolkit/cuda-12.9.1/targets/x86_64-linux/include:${C_INCLUDE_PATH:-}"

# Verify both compilers available:
echo "g++: $(g++ --version 2>&1 | head -1)"
echo "nvc++: $(nvc++ --version 2>&1 | head -1)"
```

### Step 3: Re-run sweep
```bash
python3 scripts/spec_tools/run_verify_sweep.py \
    --project-root "$PROJECT_ROOT" \
    --exclude-known-fail \
    --jobs 4 2>&1 | grep -E "^(PASS|FAIL|---)"
```

### Step 4: Investigate remaining failures
For any specs that still fail after Step 1-3, run individually with verbose output:
```bash
python3 -m harness --project-root "$PROJECT_ROOT" -v verify specs/<failing-spec>.json 2>&1 | tail -20
```

For the HeCBench OMP self-check failures (Category 3) and runtime crashes (Category 4) — if they persist, they are environment-specific and Le should exclude them from the eval sweep. The eval harness only uses specs as source/target for LLM translation and skips specs that can't verify locally.

## Key Lessons Learned
1. **Le's HeCBench is a newer version** than ours (downloaded from unpinned master). Some Makefiles produce different binary names (`main` instead of `stencil_1d`).
2. **Le's spec files had corrupt build commands** — raw `g++` commands instead of `make -f Makefile.aomp`. Origin unknown. Fixed by `git checkout -- specs/` + path re-adaptation.
3. **§4c in the handoff is incomplete** — it only replaces 3 specific paths but specs contain other HPC SDK sub-paths. The fix is to replace the entire version prefix (`24.3` → `25.5`).
4. **Cray module conflicts**: Loading `gcc-native/12.3` can replace `PrgEnv-nvidia` with `PrgEnv-gnu`. Must load PrgEnv-nvidia FIRST, then gcc-native.
5. **CPATH required** for Rodinia OpenCL builds — `timing.c` includes `<CL/cl.h>` without `-I` flags.

## After 88/88 (or best achievable)
Continue with HANDOFF-LE-GPT54-EVAL.md:
- §6: Azure API key setup
- §8: Shell setup in tmux
- §9: Run canonical evals (Study 1) — use `run_phase3.sh` from §0
- §10: Derive L0 passers
- §11: Run ablation evals (Study 2)
- §12: Post-eval analysis
