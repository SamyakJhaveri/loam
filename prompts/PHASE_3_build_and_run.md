# Phase 3: Build & Run Pipeline for Available Compilers

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

**Prerequisites**: Phases 0–2 are complete. You have 80 spec files (20 kernels × 4 APIs), `manifest.jsonl` is updated, and `validate_schema.py --all` passes.

### Context

You are working in `~/Desktop/parbench_sam/`. The harness CLI supports:
- `python -m harness build specs/<spec>.json` — compile a kernel
- `python -m harness run specs/<spec>.json --config correctness` — run a compiled kernel
- `python -m harness verify specs/<spec>.json` — full pipeline: build → run → verify
- `python -m harness verify specs/<spec>.json --json` — same but also outputs machine-readable JSON

Check `config/compiler_inventory.txt` (from Phase 0) to know which compilers are available. You will likely have CUDA (nvcc) and GCC+OpenMP. HIP and SYCL may or may not be available yet.

### Your Task

Systematically build, run, and verify every kernel variant for which you have a working compiler. Record all results.

### Step-by-Step Process

#### Step 1: Determine which APIs can be built now

Based on the compiler inventory:
- **CUDA**: If `nvcc` is available → build all 20 CUDA specs
- **OpenMP**: If `g++ -fopenmp` works → build all 20 OpenMP specs
- **HIP**: If `hipcc` is available → build all 20 HIP specs
- **SYCL**: If `icpx` or `dpcpp` is available → build all 20 SYCL specs

#### Step 2: Build all CUDA variants first

CUDA is the primary API. Build each one individually, capturing results:

```bash
cd ~/Desktop/parbench_sam

# Create results directory
mkdir -p results/phase3

# Build each CUDA spec
for spec in specs/hecbench-*-cuda.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-cuda//')
    echo "=== Building ${kernel}-cuda ==="
    python -m harness build "$spec" -v 2>&1 | tee "results/phase3/build_${kernel}_cuda.log"
    echo "Exit code: $?"
    echo ""
done 2>&1 | tee results/phase3/cuda_build_summary.log
```

#### Step 3: Run and verify CUDA variants that built successfully

For each CUDA spec that compiled:

```bash
for spec in specs/hecbench-*-cuda.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-cuda//')
    echo "=== Verifying ${kernel}-cuda ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase3/verify_${kernel}_cuda.log"
    echo ""
done 2>&1 | tee results/phase3/cuda_verify_summary.log
```

#### Step 4: Repeat for OpenMP variants

```bash
for spec in specs/hecbench-*-omp.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-omp//')
    echo "=== Verifying ${kernel}-omp ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase3/verify_${kernel}_omp.log"
    echo ""
done 2>&1 | tee results/phase3/omp_verify_summary.log
```

#### Step 5: Attempt HIP and SYCL if compilers are available

If `hipcc` is available:
```bash
for spec in specs/hecbench-*-hip.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-hip//')
    echo "=== Verifying ${kernel}-hip ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase3/verify_${kernel}_hip.log"
    echo ""
done 2>&1 | tee results/phase3/hip_verify_summary.log
```

If `icpx`/`dpcpp` is available:
```bash
for spec in specs/hecbench-*-sycl.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-sycl//')
    echo "=== Verifying ${kernel}-sycl ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase3/verify_${kernel}_sycl.log"
    echo ""
done 2>&1 | tee results/phase3/sycl_verify_summary.log
```

#### Step 6: Handle build failures

For each build failure:

1. **Read the error log** carefully
2. **Common fixes**:
   - Wrong ARCH flag → update the spec's `build.commands.build`
   - Missing header → check if a header needs to move from `support_files` to `prompt_payload` or vice versa
   - Missing input file → add to `support_files` and `run.input_configurations.correctness.input_files`
   - Linker error → check if additional source files need to be compiled (may need Makefile adjustment, which means the spec's build command needs updating)
3. **Update the spec** if needed and re-run
4. **If unfixable** (e.g., kernel requires a library not available), mark it in the results and note it as a candidate for replacement

#### Step 7: Generate results summary

Create a consolidated results table:

```bash
cd ~/Desktop/parbench_sam

python3 -c "
import json, glob, os

results = []
for log_file in sorted(glob.glob('results/phase3/verify_*.log')):
    basename = os.path.basename(log_file).replace('verify_', '').replace('.log', '')
    parts = basename.rsplit('_', 1)
    kernel, api = parts[0], parts[1]
    with open(log_file) as f:
        content = f.read()
    build_pass = 'BUILD: PASS' in content
    run_pass = 'RUN: PASS' in content
    verify_pass = 'VERIFY: PASS' in content
    results.append({
        'kernel': kernel, 'api': api,
        'build': 'PASS' if build_pass else 'FAIL',
        'run': 'PASS' if run_pass else 'FAIL',
        'verify': 'PASS' if verify_pass else 'FAIL'
    })

# Print markdown table
print('| Kernel | API | Build | Run | Verify |')
print('|--------|-----|-------|-----|--------|')
for r in results:
    print(f'| {r[\"kernel\"]} | {r[\"api\"]} | {r[\"build\"]} | {r[\"run\"]} | {r[\"verify\"]} |')

# Count
total = len(results)
passing = sum(1 for r in results if r['verify'] == 'PASS')
print(f'\nTotal: {total} specs tested, {passing} fully passing')
" > results/phase3/results_matrix.md

cat results/phase3/results_matrix.md
```

### Deliverables

1. `results/phase3/` directory with individual build/verify logs for every attempted spec
2. `results/phase3/results_matrix.md` — consolidated pass/fail table
3. Updated spec files for any that needed fixes (document changes)
4. A list of any kernels that failed and cannot be fixed (candidates for Phase 1 replacement)

### Do NOT

- Do NOT install new compilers (that's Phase 4)
- Do NOT populate `baseline_results` in specs yet (that's Phase 5)
- Do NOT modify the harness Python code — if the harness has a bug, note it and work around it
- Do NOT delete any specs even if they fail to build for one API — they may work once compilers are installed
