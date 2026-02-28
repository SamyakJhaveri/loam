# Phase 4: Install Missing Compilers & Build Remaining APIs

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

**Prerequisites**: Phases 0–3 are complete. CUDA and OpenMP builds are done. You know which APIs are missing compilers from `config/compiler_inventory.txt` and Phase 3 results.

### Context

You are working in `~/Desktop/parbench_sam/`. After Phase 3, you have results for CUDA and OpenMP (and possibly others). This phase fills in the gaps: installing HIP and/or SYCL compilers, then building and verifying the remaining specs.

### Important

- This machine has an **NVIDIA RTX 4070** GPU.
- HIP can run on NVIDIA GPUs via HIP's CUDA backend (you do NOT need an AMD GPU).
- SYCL (Intel oneAPI DPC++) can target NVIDIA GPUs via the CUDA backend plugin, or can run on CPU.

### Task 1: Install HIP for NVIDIA (if not already available)

Check if `hipcc` is available:
```bash
hipcc --version 2>&1
```

If NOT available, install HIP with NVIDIA backend:

```bash
# Option A: Install ROCm HIP (NVIDIA backend)
# Check Ubuntu version first
lsb_release -a

# For Ubuntu 22.04:
# Add ROCm repository
wget https://repo.radeon.com/rocm/rocm.gpg.key -O - | sudo apt-key add -
echo 'deb [arch=amd64] https://repo.radeon.com/rocm/apt/latest/ ubuntu main' | sudo tee /etc/apt/sources.list.d/rocm.list
sudo apt update
sudo apt install hip-runtime-nvidia hip-dev

# Verify
hipcc --version
```

If the package-based install is complicated, an alternative is to use HIP's source compilation or Docker. Note the approach that works and document it.

After installation, update `config/compiler_inventory.txt`.

### Task 2: Install Intel oneAPI DPC++/SYCL (if not already available)

Check if `icpx` is available:
```bash
icpx --version 2>&1
```

If NOT available:

```bash
# Install Intel oneAPI Base Toolkit
wget https://registrationcenter-download.intel.com/akdlm/IRC_NAS/... # (check latest URL)
# OR use apt:
wget -O- https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS.PUB | sudo gpg --dearmor -o /usr/share/keyrings/oneapi-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/oneapi-archive-keyring.gpg] https://apt.repos.intel.com/oneapi all main" | sudo tee /etc/apt/sources.list.d/oneAPI.list
sudo apt update
sudo apt install intel-oneapi-compiler-dpcpp-cpp

# Set up environment
source /opt/intel/oneapi/setvars.sh

# Verify
icpx --version
```

After installation, update `config/compiler_inventory.txt`.

### Task 3: Build and verify HIP specs

Once `hipcc` is available:

```bash
cd ~/Desktop/parbench_sam

for spec in specs/hecbench-*-hip.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-hip//')
    echo "=== Verifying ${kernel}-hip ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase3/verify_${kernel}_hip.log"
    echo ""
done 2>&1 | tee results/phase4/hip_verify_summary.log
```

Handle failures the same way as Phase 3 Step 6.

### Task 4: Build and verify SYCL specs

Once `icpx`/`dpcpp` is available:

```bash
# Make sure oneAPI env is sourced
source /opt/intel/oneapi/setvars.sh 2>/dev/null

cd ~/Desktop/parbench_sam

for spec in specs/hecbench-*-sycl.json; do
    kernel=$(basename "$spec" .json | sed 's/hecbench-//' | sed 's/-sycl//')
    echo "=== Verifying ${kernel}-sycl ==="
    python -m harness verify "$spec" --config correctness --json -v 2>&1 | tee "results/phase4/verify_${kernel}_sycl.log"
    echo ""
done 2>&1 | tee results/phase4/sycl_verify_summary.log
```

### Task 5: Update results matrix

Regenerate the consolidated results matrix including all 4 APIs:

```bash
cd ~/Desktop/parbench_sam

python3 -c "
import glob, os

results = []
for log_dir in ['results/phase3', 'results/phase4']:
    for log_file in sorted(glob.glob(f'{log_dir}/verify_*.log')):
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

# Deduplicate (prefer phase4 over phase3 for same kernel-api)
seen = {}
for r in results:
    key = f'{r[\"kernel\"]}-{r[\"api\"]}'
    seen[key] = r
results = sorted(seen.values(), key=lambda x: (x['kernel'], x['api']))

print('| Kernel | API | Build | Run | Verify |')
print('|--------|-----|-------|-----|--------|')
for r in results:
    print(f'| {r[\"kernel\"]} | {r[\"api\"]} | {r[\"build\"]} | {r[\"run\"]} | {r[\"verify\"]} |')

total = len(results)
passing = sum(1 for r in results if r['verify'] == 'PASS')
apis = {}
for r in results:
    apis.setdefault(r['api'], [0, 0])
    apis[r['api']][0] += 1
    if r['verify'] == 'PASS':
        apis[r['api']][1] += 1

print(f'\nTotal: {total} specs tested, {passing} fully passing')
for api, (t, p) in sorted(apis.items()):
    print(f'  {api}: {p}/{t} passing')
" > results/phase4/full_results_matrix.md

cat results/phase4/full_results_matrix.md
```

### Deliverables

1. Updated `config/compiler_inventory.txt` with newly installed compilers
2. `results/phase4/` directory with HIP and SYCL build/verify logs
3. `results/phase4/full_results_matrix.md` — consolidated 4-API pass/fail table
4. Updated specs for any that needed build command fixes
5. Documentation of installation steps that worked (for reproducibility)

### Notes

- If a compiler simply cannot be installed (e.g., no sudo access, package conflicts), document it and move on. The specs are still valid — they just can't be verified on this particular machine yet.
- If HIP-on-NVIDIA doesn't work well, that's okay — HIP specs are still valuable for machines with AMD GPUs.
- SYCL with NVIDIA backend can be tricky. If it doesn't work, try targeting CPU: modify SYCL build commands temporarily to compile for CPU target.
