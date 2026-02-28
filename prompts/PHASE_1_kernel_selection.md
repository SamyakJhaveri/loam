# Phase 1: Kernel Discovery & Selection (20 Kernels × 4 APIs)

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

**Prerequisites**: Phase 0 is complete. `~/Desktop/downloads/HeCBench-master/` exists and `config/paths.json` is configured.

### Context

You are working in `~/Desktop/parbench_sam/`. This project already has 5 pilot kernels (nn, scan, binomial, particle-diffusion, radixsort) with specs for 4 APIs each (CUDA, HIP, SYCL, OpenMP) — 20 specs total. We need to expand to **20 kernels total** (keeping the existing 5, adding 15 new ones).

### Your Task

Analyze HeCBench and propose 15 additional kernels that meet ALL of the following criteria:

#### Selection Criteria (ALL must be met)

1. **All 4 API variants exist**: The kernel MUST have directories for all 4: `<name>-cuda`, `<name>-hip`, `<name>-sycl`, AND `<name>-omp` under `~/Desktop/downloads/HeCBench-master/src/`

2. **Self-contained**: The kernel should compile with `make` using standard toolchains (no exotic dependencies beyond CUDA Toolkit, ROCm/HIP, Intel oneAPI/SYCL, and GCC+OpenMP)

3. **Self-checking or has clear output**: Ideally the kernel prints "PASS"/"FAIL" or a numeric result that can be verified. Check stdout patterns in the source code.

4. **Domain diversity**: Try to cover different computational domains. The existing 5 cover: graph search (nn), reduction (scan), physics (particle-diffusion), finance (binomial), sorting (radixsort). Try to add kernels from: linear algebra, image processing, cryptography, simulation, stencil computation, FFT, sparse computation, molecular dynamics, etc.

5. **Reasonable complexity**: Not trivially simple (like a vector add) but not so complex it has 20+ source files.

### Step-by-Step Process

#### Step 1: Find all kernels with all 4 API variants

Run this to find kernels that exist in all 4 APIs:

```bash
cd ~/Desktop/downloads/HeCBench-master/src

# Get all kernel base names (strip the -cuda/-hip/-sycl/-omp suffix)
for dir in *-cuda; do
    base="${dir%-cuda}"
    if [ -d "${base}-hip" ] && [ -d "${base}-sycl" ] && [ -d "${base}-omp" ]; then
        echo "$base"
    fi
done | sort > /tmp/all_4api_kernels.txt

wc -l /tmp/all_4api_kernels.txt
```

#### Step 2: Filter for compilability

For each candidate, quickly check if the CUDA variant has a Makefile and reasonable source structure:

```bash
while read kernel; do
    cuda_dir="~/Desktop/downloads/HeCBench-master/src/${kernel}-cuda"
    if [ -f "${cuda_dir}/Makefile" ]; then
        num_files=$(ls "${cuda_dir}"/*.cu "${cuda_dir}"/*.cpp "${cuda_dir}"/*.h 2>/dev/null | wc -l)
        echo "${kernel} (${num_files} source files)"
    fi
done < /tmp/all_4api_kernels.txt
```

#### Step 3: Check for self-checking behavior

For each candidate, grep for verification patterns:

```bash
while read kernel; do
    cuda_dir="~/Desktop/downloads/HeCBench-master/src/${kernel}-cuda"
    has_pass=$(grep -rl "PASS\|passed\|PASSED\|Correct\|CORRECT\|verified\|VERIFIED" "${cuda_dir}"/ 2>/dev/null | wc -l)
    echo "${kernel}: self_check=${has_pass}"
done < /tmp/all_4api_kernels.txt
```

#### Step 4: Propose 15 candidates

Based on Steps 1-3, produce a ranked list of 15 candidate kernels. For each, report:

- **Kernel name** (the directory base name)
- **Domain** (what computational domain it belongs to)
- **File count** per API variant
- **Self-checking?** (yes/no, and what pattern)
- **Why it's a good pick** (1 sentence)

Format the output as a markdown table and save it to:

```
~/Desktop/parbench_sam/analysis/kernel_selection_candidates.md
```

#### Step 5: Quick-build test (CUDA only)

For each of the 15 proposed candidates, attempt a quick CUDA build to verify compilability:

```bash
cd ~/Desktop/downloads/HeCBench-master/src/<kernel>-cuda
make ARCH=sm_89 2>&1 | tail -5
```

Record which ones compile successfully. If a candidate fails, note the error and suggest a replacement.

Save build results to:
```
~/Desktop/parbench_sam/analysis/kernel_selection_build_test.md
```

### Deliverables

1. `analysis/kernel_selection_candidates.md` — Table of 15 proposed kernels with metadata
2. `analysis/kernel_selection_build_test.md` — CUDA build test results for each candidate
3. A final recommended list of 15 kernels (+ the existing 5 = 20 total) that:
   - All have 4 API variants in HeCBench
   - CUDA variant compiles on this machine
   - Cover diverse computational domains
   - Have some form of output verification

### Do NOT

- Do NOT create any spec JSON files yet (that's Phase 2)
- Do NOT modify the manifest or existing specs
- Do NOT install any new compilers
- Do NOT attempt HIP/SYCL/OMP builds yet

### Important

Present the final list to me for approval BEFORE proceeding to Phase 2. I may want to swap some kernels or adjust the selection.
