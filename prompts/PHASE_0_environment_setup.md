# Phase 0: Environment Setup & HeCBench Download

## Prompt for Claude Code (VSCode on Remote Linux PC)

---

You are working in the `~/Desktop/parbench_sam/` repository — a meta-benchmark framework for evaluating LLM translation of parallel code across APIs (CUDA, HIP, SYCL, OpenMP).

### Your Task

Set up the environment so the ParBench harness can find and operate on HeCBench kernel source code. This involves 3 things:

#### 1. Download HeCBench

Download the HeCBench repository into a `downloads/` directory adjacent to (or inside) the project:

```bash
mkdir -p ~/Desktop/downloads
cd ~/Desktop/downloads
wget https://github.com/zjin-lcf/HeCBench/archive/refs/heads/master.zip
unzip master.zip
# This produces ~/Desktop/downloads/HeCBench-master/
```

Verify it worked:
```bash
ls ~/Desktop/downloads/HeCBench-master/src/ | head -20
```

You should see directories like `binomial-cuda`, `nn-cuda`, `scan-sycl`, etc.

#### 2. Create `config/paths.json`

The harness code in `harness/spec_loader.py` loads `config/paths.json` to resolve file paths. The key field is `downloads_root` — it tells the harness where `HeCBench-master/` lives.

Create the file `~/Desktop/parbench_sam/config/paths.json` with this content:

```json
{
    "project_root": "/home/<YOUR_USERNAME>/Desktop/parbench_sam",
    "downloads_root": "/home/<YOUR_USERNAME>/Desktop/downloads",
    "hecbench_root": "/home/<YOUR_USERNAME>/Desktop/downloads/HeCBench-master"
}
```

Replace `<YOUR_USERNAME>` with the actual username on this machine (run `whoami` to check).

#### 3. Verify the existing pipeline works

The repo already has 20 spec files (5 kernels × 4 APIs) in `specs/`. Run the validator to confirm everything resolves:

```bash
cd ~/Desktop/parbench_sam
pip install jsonschema  # if not already installed
python scripts/validate_schema.py --all
```

**Expected output**: All 20 specs should pass validation. File existence checks should now find the actual source files under `downloads/HeCBench-master/src/`.

Then test the prompt extraction for one kernel to confirm path resolution works:

```bash
python -m harness prompt specs/hecbench-binomial-cuda.json
```

**Expected output**: You should see the full contents of `kernel.cu` and `main.cu` printed — NOT `<FILE NOT FOUND>` errors.

#### 4. Inventory available compilers

Run the following to document what's available on this machine:

```bash
echo "=== CUDA ===" && nvcc --version 2>&1 || echo "NOT FOUND"
echo "=== NVC++ ===" && nvc++ --version 2>&1 || echo "NOT FOUND"
echo "=== GCC ===" && gcc --version 2>&1 | head -1
echo "=== G++ ===" && g++ --version 2>&1 | head -1
echo "=== OpenMP ===" && echo '#include <omp.h>' | g++ -fopenmp -x c++ - -o /dev/null 2>&1 && echo "OpenMP: YES" || echo "OpenMP: NO"
echo "=== HIP ===" && hipcc --version 2>&1 || echo "NOT FOUND"
echo "=== SYCL (Intel oneAPI) ===" && icpx --version 2>&1 || echo "NOT FOUND"
echo "=== SYCL (DPC++) ===" && dpcpp --version 2>&1 || echo "NOT FOUND"
echo "=== GPU ===" && nvidia-smi --query-gpu=name,compute_cap,memory.total --format=csv,noheader 2>&1
echo "=== ARCH ===" && nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>&1 | head -1 | sed 's/\.//' | awk '{print "sm_"$1}'
```

Save the output to `config/compiler_inventory.txt` for reference in later phases.

### Deliverables

After this phase, you should have:
- `~/Desktop/downloads/HeCBench-master/` with full source tree
- `~/Desktop/parbench_sam/config/paths.json` correctly pointing to downloads
- `scripts/validate_schema.py --all` passing for all 20 existing specs
- `python -m harness prompt` showing actual file contents (not FILE NOT FOUND)
- `config/compiler_inventory.txt` documenting available compilers

### Do NOT

- Do NOT modify any existing spec files
- Do NOT modify any harness Python code
- Do NOT build or run any kernels yet (that's Phase 3)
