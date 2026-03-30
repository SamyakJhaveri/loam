# ParBench Onboarding Guide for Erel

**Purpose:** Set up ParBench from scratch on your machine and run the Gemini 2.5 Flash
evaluation campaign.

**Author:** Samyak Jhaveri (auto-generated from verified project state, 2026-03-29)

**Reference machine (known-working):**
- GPU: NVIDIA GeForce RTX 4070
- NVIDIA HPC SDK 24.3
- Ubuntu, kernel 6.8.0-40-generic
- Python 3.12.3

**Your machine (expected):**
- GPU: NVIDIA RTX 4060 Laptop (Ada/Lovelace, compute capability 8.9 -- same as RTX 4070)
- NVIDIA HPC SDK 25.7
- Ubuntu (version TBD)
- GCC (version TBD)

> **RTX 4060 Laptop vs RTX 4070:** Both are Ada/Lovelace architecture with compute
> capability 8.9. The 4060 Laptop has fewer CUDA cores (3072 vs 5888) and less VRAM
> (8GB vs 12GB). For ParBench: correctness results are identical (same architecture),
> only wall-clock timing will differ. No Rodinia benchmark at correctness config sizes
> requires >8GB VRAM.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Clone and Setup](#2-clone-and-setup)
3. [NVIDIA HPC SDK Configuration](#3-nvidia-hpc-sdk-configuration)
4. [Python Environment](#4-python-environment)
5. [Configuration Files](#5-configuration-files)
6. [Verification Checklist](#6-verification-checklist)
7. [Running the Campaign](#7-running-the-campaign)
8. [Monitoring and Troubleshooting](#8-monitoring-and-troubleshooting)
9. [Post-Campaign](#9-post-campaign)

---

## 1. Prerequisites

Before starting, verify you have these installed:

```bash
# Check your OS
lsb_release -a

# Check your kernel
uname -r

# Check GCC
gcc --version

# Check Python (must be 3.12+)
python3 --version

# Check NVIDIA driver and GPU
nvidia-smi

# Check NVIDIA HPC SDK is installed
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/

# Check nvcc
/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/bin/nvcc --version

# Check tmux is installed (needed for campaign runner)
tmux -V

# Check git
git --version
```

**Required software:**
- Git
- Python 3.12+ (system or pyenv)
- NVIDIA HPC SDK 25.7 (must include nvcc, nvc, OpenCL headers/libs)
- GCC (any recent version; 11+ recommended)
- tmux
- make
- wget or curl (for HeCBench download)
- unzip

**Install any missing packages:**
```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip tmux make wget unzip build-essential
```

---

## 2. Clone and Setup

### 2.1 Clone the main repository

```bash
cd ~/Desktop   # or wherever you want the project
git clone https://github.com/SamyakJhaveri/parbench_sam.git
cd parbench_sam
```

### 2.2 Initialize the Rodinia submodule

Rodinia is a git submodule. It pins to commit `9c10d3ea16ddba2ba057cc3951a9efc4c2cc18a4`
of `https://github.com/yuhc/gpu-rodinia`.

```bash
git submodule update --init --recursive
```

Verify the submodule initialized:
```bash
ls rodinia/cuda/bfs/bfs.cu
# Should exist. If rodinia/ is empty, the submodule did not initialize correctly.
```

**Create the `rodinia-src` symlink (REQUIRED):**

All Rodinia specs reference `repo_root: "rodinia/rodinia-src"`. The submodule root is
`rodinia/`, so a symlink is needed to make these paths resolve:

```bash
cd rodinia
ln -s . rodinia-src
cd ..
```

Verify:
```bash
ls rodinia/rodinia-src/cuda/bfs/bfs.cu
# Should exist via the symlink. If not, the symlink was not created correctly.
```

> **Why a symlink?** The spec JSON files use `"repo_root": "rodinia/rodinia-src"` for
> historical reasons. The submodule clones directly into `rodinia/` (not `rodinia/rodinia-src/`).
> Without this symlink, the harness cannot locate any Rodinia source files and ALL Rodinia
> specs will fail with file-not-found errors.

### 2.3 Apply Rodinia toolchain patches

The Rodinia source needs patches for the NVIDIA HPC SDK toolchain (paths, GPU arch flags,
OpenCL includes). A pre-built patch file exists:

```bash
cd rodinia
git apply ../docs/rodinia_toolchain_patches.diff
cd ..
```

**IMPORTANT: The patch was written for HPC SDK 24.3. You use 25.7.**

After applying the patch, you MUST update ALL CUDA paths in the patched files.

**Step 1: Find YOUR CUDA version subdirectory.** The HPC SDK bundles a specific CUDA
version in a subdirectory. The patch hardcodes `24.3/cuda/12.3` -- you need your equivalent:

```bash
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/
# Look for a version directory like 12.6, 12.8, etc. -- that's YOUR_CUDA_VERSION
```

**Step 2: Update `make.config`.** Edit `rodinia/common/make.config`:

```bash
nano rodinia/common/make.config
```

Find and replace the two hardcoded paths:

| Variable | Change from | Change to |
|----------|------------|-----------|
| `CUDA_DIR` | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/12.3` | `/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/YOUR_CUDA_VERSION` |
| `NV_OPENCL_DIR` | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/12.3` | `/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/YOUR_CUDA_VERSION` |

**Step 3: Update `cuda/lavaMD/makefile`.** This file also has a hardcoded path from the patch:

```bash
nano rodinia/cuda/lavaMD/makefile
```

Find the line with `-L/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64` and change `24.3`
to `25.7`.

**Step 4: Verify no remaining 24.3 references:**

```bash
grep -rn "24.3" rodinia/
# All matches should be fixed. If any remain, update them to 25.7.
```

**Verify the GPU architecture flag is correct:**
The patch sets `-arch=sm_89` / `--gpu-code=sm_89` which is correct for BOTH
RTX 4060 Laptop and RTX 4070 (both compute capability 8.9). No change needed.

**If `git apply` fails** (e.g., the patch was already partially applied):
```bash
cd rodinia
git checkout -- .          # reset submodule to pristine state
git apply ../docs/rodinia_toolchain_patches.diff
cd ..
```

### 2.4 Clone additional benchmark sources

These are NOT git submodules. Clone them at the exact commits used by Samyak.
Run all commands from the project root (`~/Desktop/parbench_sam`):

```bash
cd ~/Desktop/parbench_sam   # ensure you're at the project root

# XSBench
mkdir -p xsbench
git clone https://github.com/ANL-CESAR/XSBench.git xsbench/xsbench-src
cd xsbench/xsbench-src && git checkout ba08e5221af6106252b866e50ea123c69d31a4e2 && cd ../..

# RSBench
mkdir -p rsbench
git clone https://github.com/ANL-CESAR/RSBench.git rsbench/rsbench-src
cd rsbench/rsbench-src && git checkout 34b644787ea9af4fb188e1253da72e09bbed9989 && cd ../..

# mixbench
mkdir -p mixbench
git clone https://github.com/ekondis/mixbench.git mixbench/mixbench-src
cd mixbench/mixbench-src && git checkout 32edeca98bdd63b32769e3c7460676b9fd567f06 && cd ../..
```

Verify all checkouts are at the correct commits:
```bash
echo "XSBench: $(cd xsbench/xsbench-src && git rev-parse --short HEAD)"
echo "RSBench: $(cd rsbench/rsbench-src && git rev-parse --short HEAD)"
echo "mixbench: $(cd mixbench/mixbench-src && git rev-parse --short HEAD)"
# Expected: XSBench: ba08e52, RSBench: 34b6447, mixbench: 32edeca
```

### 2.5 Download HeCBench

HeCBench is NOT a git clone -- it's a large (~1.4 GB) zip download. The project
expects it to live at `HeCBench-master/` in the project root.

```bash
# Download the zip
wget -O HeCBench.zip "https://codeload.github.com/zjin-lcf/HeCBench/zip/refs/heads/master"

# Unzip (creates HeCBench-master/ directory)
unzip HeCBench.zip

# Verify
ls HeCBench-master/src/
# Should show many benchmark directories
```

> **Note:** If you skip this step, HeCBench-related specs will fail validation
> (~120 errors), but this does NOT affect Rodinia/XSBench/RSBench/mixbench evaluation.
> The campaign script will gracefully handle missing HeCBench specs.

### 2.6 Verify directory structure

After setup, your project root should contain:

```
parbench_sam/
  rodinia/                   <-- git submodule (patched)
    rodinia-src -> .         <-- symlink you created in Step 2.2 (REQUIRED)
    common/make.config       <-- patched CUDA paths
    cuda/                    <-- CUDA benchmark sources
    openmp/                  <-- OpenMP benchmark sources
    opencl/                  <-- OpenCL benchmark sources
  xsbench/xsbench-src/      <-- manual clone at ba08e52
  rsbench/rsbench-src/      <-- manual clone at 34b6447
  mixbench/mixbench-src/    <-- manual clone at 32edeca
  HeCBench-master/          <-- wget download (optional)
  specs/                    <-- benchmark specifications
  harness/                  <-- build/run/verify pipeline
  scripts/                  <-- evaluation, analysis, batch scripts
  config/paths.json         <-- MUST be updated (see Section 5)
  requirements.txt          <-- Python dependencies
  ...
```

---

## 3. NVIDIA HPC SDK Configuration

### 3.1 Locate your CUDA paths

HPC SDK 25.7 paths will differ from 24.3. Find yours:

```bash
# CUDA toolkit directory (find your CUDA version number)
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/
# Expected: a version directory like 12.6/ or 12.8/ plus bin/, lib64/, include/, etc.

# nvcc path
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/bin/nvcc

# nvc path (needed for OMP target specs)
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/bin/nvc

# OpenCL headers (check BOTH possible locations)
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/include/CL/ 2>/dev/null || \
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/targets/x86_64-linux/include/CL/

# OpenCL libraries (check BOTH possible locations)
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/lib64/libOpenCL* 2>/dev/null || \
ls /opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda/targets/x86_64-linux/lib/libOpenCL*
```

> **Note on `targets/` subdirectory:** The Rodinia patch uses
> `targets/x86_64-linux/lib` and `targets/x86_64-linux/include` instead of the
> top-level `lib64/` and `include/`. Verify which layout your SDK 25.7 uses. If your SDK
> has libraries in `lib64/` directly rather than `targets/x86_64-linux/lib/`, you may
> need to adjust the `make.config` `CUDA_LIB_DIR` and `NV_OPENCL_INC`/`NV_OPENCL_LIB`
> lines accordingly.

### 3.2 Set environment variables

Add these to your `~/.bashrc` (or run before each session).

> **Note on `CUDA_DIR`:** The Rodinia `make.config` sets its own `CUDA_DIR` variable
> internally (pointing to the versioned CUDA subdirectory like `25.7/cuda/12.6`).
> The shell `CUDA_DIR` below is for YOUR non-Rodinia tools. They do not conflict because
> Makefile variables are separate from shell environment variables.

```bash
# --- ParBench NVIDIA HPC SDK environment ---
# Adjust paths if your SDK is installed elsewhere

export CUDA_DIR="/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/cuda"
export PATH="${CUDA_DIR}/bin:${PATH}"
export LD_LIBRARY_PATH="${CUDA_DIR}/lib64:${LD_LIBRARY_PATH:-}"

# nvc compiler (for OMP target)
export PATH="/opt/nvidia/hpc_sdk/Linux_x86_64/25.7/compilers/bin:${PATH}"

# OpenCL
export OPENCL_INC="${CUDA_DIR}/include"
export OPENCL_LIB="${CUDA_DIR}/lib64"
```

After editing:
```bash
source ~/.bashrc
```

### 3.3 Verify CUDA setup

```bash
# nvcc should be on PATH
nvcc --version

# Should show your RTX 4060 Laptop
nvidia-smi

# nvc should be on PATH (for OMP target)
nvc --version

# Quick CUDA compilation test
echo '#include <stdio.h>
__global__ void hello() { printf("Hello from GPU!\\n"); }
int main() { hello<<<1,1>>>(); cudaDeviceSynchronize(); return 0; }
' > /tmp/test_cuda.cu
nvcc -arch=sm_89 /tmp/test_cuda.cu -o /tmp/test_cuda
/tmp/test_cuda
# Should print: Hello from GPU!
rm /tmp/test_cuda.cu /tmp/test_cuda
```

---

## 4. Python Environment

### 4.1 Create the virtual environment

```bash
cd ~/Desktop/parbench_sam    # your project root

python3 -m venv env_parbench
source env_parbench/bin/activate
```

### 4.2 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

The `requirements.txt` includes:
- **Core (harness):** pydantic>=2.0, jsonschema>=4.20, libclang>=18.1
- **Eval (LLM pipeline):** anthropic>=0.40.0, openai>=1.50.0
- **Analysis:** matplotlib>=3.9, numpy>=1.26
- **Dev:** pytest>=8.0, ruff>=0.6.0

Also install scipy (used by `scripts/analysis/` statistical tests; not in requirements.txt
because it's only needed for paper figure generation, not the core eval pipeline):
```bash
pip install scipy
```

### 4.3 Verify Python setup

```bash
# Should be inside the venv
which python3
# Expected: ~/Desktop/parbench_sam/env_parbench/bin/python3

python3 -c "import pydantic; print('pydantic', pydantic.__version__)"
python3 -c "import openai; print('openai', openai.__version__)"
python3 -c "import clang.cindex; print('libclang OK')"
```

---

## 5. Configuration Files

### 5.1 Update `config/paths.json`

This is the MOST IMPORTANT configuration step. Edit `config/paths.json` to point to
YOUR project root:

```bash
nano config/paths.json
```

Replace the contents with (using YOUR actual path):

```json
{
    "project_root": "/home/erel/Desktop/parbench_sam",
    "downloads_root": "/home/erel/Desktop/parbench_sam",
    "hecbench_root": "/home/erel/Desktop/parbench_sam"
}
```

> **All three values must be your project root** (NOT subdirectories like
> `parbench_sam/HeCBench-master`). The harness appends `HeCBench-master/` from the
> spec's `repo_root` field automatically. Similarly, `downloads_root` is the base for
> all spec `repo_root` paths (like `rodinia/rodinia-src`, `xsbench/xsbench-src`, etc.).

### 5.2 Update the campaign script

The campaign script `scripts/batch/run_eval_campaign.sh` has TWO hardcoded paths that
you MUST change:

```bash
nano scripts/batch/run_eval_campaign.sh
```

Change line 44:
```bash
# FROM:
PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
# TO:
PROJECT_ROOT="/home/erel/Desktop/parbench_sam"
```

Change line 477 (inside the Python heredoc):
```python
# FROM:
BASE = "/home/samyak/Desktop/parbench_sam"
# TO:
BASE = "/home/erel/Desktop/parbench_sam"
```

### 5.3 Set the Gemini API key

The eval pipeline needs a Gemini API key. The code checks:
```python
os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
```

Either variable works. `GEMINI_API_KEY` takes precedence.

```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

> **Get an API key:** Go to https://aistudio.google.com/apikey and create one.
> The Gemini 2.5 Flash model (`gemini-2.5-flash`) is available through the
> Google AI API with the OpenAI-compatible endpoint.

Add to `~/.bashrc` for persistence:
```bash
echo 'export GEMINI_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

---

## 6. Verification Checklist

Run these in order. Every step must pass before running the campaign.

### 6.1 Activate the venv

```bash
cd ~/Desktop/parbench_sam
source env_parbench/bin/activate
```

### 6.2 Schema validation

```bash
python3 scripts/validate_schema.py --all
```

**Expected output:**
- If HeCBench IS downloaded: ~15 errors (from 5 deleted phantom Rodinia specs in manifest).
- If HeCBench is NOT downloaded: ~135 errors (120 HeCBench disk-not-found + 15 phantom).
- All other specs should validate cleanly.
- This is pre-existing and expected. Do NOT try to fix these errors.

### 6.3 Unit tests

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

**Expected:** All 15 tests pass. If libclang is not found, reinstall:
`pip install --force-reinstall libclang>=18.1`

### 6.4 Harness smoke tests

Test that the build/run/verify pipeline works with real benchmarks:

```bash
# CUDA test
python3 -m harness -v verify specs/rodinia-bfs-cuda.json

# OpenMP test
python3 -m harness -v verify specs/rodinia-bfs-omp.json
```

**Expected:** Both should show `PASS`. If they fail:
- **BUILD_FAIL:** Check CUDA/compiler paths (Section 3). Verify `make.config` paths
  match your HPC SDK 25.7 installation.
- **RUN_FAIL:** Check that `nvidia-smi` shows your GPU. Check `LD_LIBRARY_PATH`.
- **VERIFY_FAIL:** Check that the binary produces output matching the spec's
  `stdout_pattern`. Run the binary manually and inspect stdout.

### 6.5 Eval pipeline dry-run

Test the LLM evaluation pipeline without actually calling the API:

```bash
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model gemini-2.5-flash \
  --project-root ~/Desktop/parbench_sam \
  --dry-run -v
```

**Expected:** Prints the system message and user message (the LLM prompt) to stdout,
then exits with a result JSON containing `"dry_run": true`. No API call is made.

This verifies:
- Spec loading works
- Source code reading works
- Prompt construction works
- Your `--project-root` path is correct

### 6.6 API connectivity test

Make ONE real API call to verify your key works:

```bash
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model gemini-2.5-flash \
  --project-root ~/Desktop/parbench_sam \
  -v
```

This will:
1. Call the Gemini 2.5 Flash API
2. Extract the translated OpenMP code
3. Build it
4. Run it
5. Verify the output

**Expected:** Either PASS (translation worked) or BUILD_FAIL/RUN_FAIL/VERIFY_FAIL
(translation had issues -- this is normal, not every translation succeeds). What matters
is that you do NOT get an API error like `401 Unauthorized` or connection timeout.

The result JSON is written to:
`results/evaluation/gemini-2.5-flash/rodinia-bfs-cuda-to-rodinia-bfs-omp.json`

---

## 7. Running the Campaign

### 7.0 Pre-campaign: Pull fixes, clear old results, update paths

**If you have already run a Gemini campaign before**, you MUST do these steps first.
If this is your first run, skip to 7.1.

**Pull latest pipeline fixes:**
```bash
cd ~/Desktop/parbench_sam    # your project root
git pull origin main
```

Recent fixes that affect result correctness:
- **pass@k filename collision fix** (`0b952d9`): Sample 0 now gets `-s0` tag, preventing
  overwrites with primary campaign results.
- **cross-API run args fix** (`3fbaacf`): Fixes ~20-30% false VERIFY_FAIL/RUN_FAIL.

**Clear old Gemini results** (required — `--resume` would skip existing files):
```bash
rm -rf results/evaluation/gemini-2.5-flash/
rm -f results/evaluation/gemini-2_5-flash_campaign.log
rm -f results/evaluation/gemini-2_5-flash_campaign_done.marker
rm -f results/evaluation/gemini-2_5-flash_passk.log
rm -f results/evaluation/gemini-2_5-flash_passk_done.marker

# Verify clean
ls results/evaluation/gemini-2.5-flash/ 2>/dev/null && echo "NOT CLEAN" || echo "CLEAN"
```

**Update campaign script paths** (two hardcoded references to Samyak's machine):
```bash
nano scripts/batch/run_eval_campaign.sh
```
- Line 44: Change `PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"` to YOUR project root
- Line 477: Change `BASE = "/home/samyak/Desktop/parbench_sam"` to YOUR project root

Verify: `grep -n "samyak" scripts/batch/run_eval_campaign.sh` should return nothing.

### 7.1 Primary campaign (790 tasks)

The primary campaign runs:
- **158 source-target pairs** across all suites (Rodinia, XSBench, RSBench, mixbench, HeCBench)
- **5 augmentation levels** (L0-L4) per pair
- **max_retries=3** (iterative self-repair with error feedback)
- **temperature=0.0** (deterministic/greedy decoding)
- **Total: 790 tasks**

```bash
source env_parbench/bin/activate
export GEMINI_API_KEY="your-key-here"

bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash
```

This automatically:
1. Checks your API key
2. Launches a detached tmux session named `gemini-2_5-flash_campaign`
3. Runs all 28 batches (6 Rodinia directions + 6 XSBench + 6 RSBench + 6 mixbench + 4 HeCBench)
4. Retries any failed batches once
5. Runs analysis at the end
6. Writes a done marker when complete

**You can safely disconnect SSH** -- the tmux session keeps running.

### 7.2 Pass@k sweep (after primary completes)

```bash
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k
```

The pass@k sweep runs:
- **158 pairs at L0 only**
- **5 independent samples** per pair (temperature=0.7)
- **max_retries=1** (zero-shot, no repair)
- **Total: 790 tasks** (158 pairs x 5 samples)
- **Filenames:** `-s0` through `-s4` tags — do NOT collide with primary results

### 7.3 Resuming after interruption

Both campaign modes use `--resume`, which means:
- If the process crashes, SSH disconnects, or you reboot, just run the same command again
- Completed tasks are detected by their result JSON files on disk
- Only remaining tasks are executed

```bash
# Resume primary campaign
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash

# Resume pass@k
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k
```

---

## 8. Monitoring and Troubleshooting

### 8.1 Attach to the tmux session

```bash
# Primary campaign
tmux attach -t gemini-2_5-flash_campaign

# Pass@k
tmux attach -t gemini-2_5-flash_passk

# Or use the --attach shortcut (matches the mode you want to attach to)
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash --attach          # primary
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k --attach   # pass@k
```

To detach without stopping: `Ctrl+B`, then `D`.

### 8.2 Check the log file

```bash
# Primary campaign log
tail -f results/evaluation/gemini-2_5-flash_campaign.log

# Pass@k log
tail -f results/evaluation/gemini-2_5-flash_passk.log
```

### 8.3 Check progress (count completed result files)

```bash
ls results/evaluation/gemini-2.5-flash/*.json 2>/dev/null | wc -l
# Compare against 790 expected tasks
```

Break down by suite:
```bash
for SUITE in rodinia xsbench rsbench mixbench hecbench; do
  COUNT=$(ls results/evaluation/gemini-2.5-flash/${SUITE}-*.json 2>/dev/null | wc -l)
  echo "$SUITE: $COUNT files"
done
```

### 8.4 Check the done marker

When the campaign finishes, a marker file is written:
```bash
cat results/evaluation/gemini-2_5-flash_campaign_done.marker
# Shows: COMPLETED timestamp, total files, elapsed time, any failed batches
```

### 8.5 Common issues

#### API key errors
```
FATAL: Neither GEMINI_API_KEY nor GOOGLE_API_KEY is set.
```
**Fix:** `export GEMINI_API_KEY="your-key-here"` before running the campaign.

#### Rate limiting (429 errors)
The Gemini API has rate limits (requests per minute and tokens per minute).
If you hit them, the pipeline will error on that task. The `--resume` flag means you
can just re-run the same campaign command and it will skip completed tasks, picking up
where it left off. The campaign script also includes a built-in retry pass for any
failed batches.

#### Quota exhaustion
If you see repeated 429 errors, your API key may have hit daily quota limits.
Check your usage at https://aistudio.google.com/ and wait for the quota to reset
(usually 24 hours). Then re-run the campaign command with `--resume`.

#### BUILD_FAIL on Rodinia CUDA benchmarks
If CUDA benchmarks fail to build, your `make.config` paths are wrong.
```bash
cat rodinia/common/make.config
# Verify CUDA_DIR and NV_OPENCL_DIR point to your 25.7 installation
# Also check:
grep -n "24.3" rodinia/common/make.config rodinia/cuda/lavaMD/makefile
# Should return nothing if all paths are updated
```

#### Known failures (expected)
These specs are KNOWN_FAIL -- they will fail and that is expected:
- `rodinia-kmeans-cuda` (texture<> removed in CUDA 12)
- `rodinia-mummergpu-cuda` (same)
- `rodinia-mummergpu-omp` (same + cuMemGetInfo_v2)
- `rodinia-hybridsort-cuda` (needs GL/glew.h)
- `rodinia-nn-opencl` (TIMEOUT/SIGSEGV)
- `rodinia-kmeans-opencl` (SIGSEGV)
- `hecbench-stencil1d-omp_target` (BUILD_FAIL)
- `hecbench-scan-omp_target` (VERIFY_FAIL)

The campaign runner handles these gracefully -- they do not stop the batch.

#### tmux session already exists
```
duplicate session: gemini-2_5-flash_campaign
```
**Fix:** The script auto-kills stale sessions, but if it does not:
```bash
tmux kill-session -t gemini-2_5-flash_campaign
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash
```

#### libclang errors in augmentation
If L1-L4 augmentation fails with libclang errors:
```bash
pip install --force-reinstall libclang>=18.1
# Also check:
python3 -c "from clang.cindex import Index; print('OK')"
```

---

## 9. Post-Campaign

### 9.1 Verify completeness

```bash
# Count total result files
ls results/evaluation/gemini-2.5-flash/*.json | wc -l
# Primary campaign: expect ~790 files (some KNOWN_FAIL specs produce fewer)

# Quick status breakdown
python3 -c "
import json, glob
files = glob.glob('results/evaluation/gemini-2.5-flash/*.json')
counts = {}
for f in files:
    r = json.loads(open(f).read())
    s = r.get('overall_status', 'UNKNOWN')
    counts[s] = counts.get(s, 0) + 1
total = len(files)
passes = counts.get('PASS', 0)
print(f'Total: {total}')
print(f'PASS: {passes}/{total} ({100*passes/total:.1f}%)')
for s, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {s}: {n}')
"
```

### 9.2 Run the analysis pipeline

```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root ~/Desktop/parbench_sam \
  --write-dashboard
```

This generates:
- `results/evaluation/eval_summary.json` -- machine-readable summary
- `results/evaluation/eval_summary.md` -- human-readable markdown report
- `visualizations/eval_results_data.js` -- dashboard data (via `--write-dashboard`)

### 9.3 Send results to Samyak

The key files to share:

```bash
# Create a tarball of all results
tar czf gemini-2.5-flash-results.tar.gz \
  results/evaluation/gemini-2.5-flash/ \
  results/evaluation/eval_summary.json \
  results/evaluation/eval_summary.md \
  results/evaluation/gemini-2_5-flash_campaign.log \
  results/evaluation/gemini-2_5-flash_campaign_done.marker
```

Or push to a branch:
```bash
git checkout -b erel/gemini-2.5-flash-results
git add results/evaluation/gemini-2.5-flash/
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git commit -m "Add Gemini 2.5 Flash eval results from Erel's machine (RTX 4060 Laptop)"
git push -u origin erel/gemini-2.5-flash-results
```

### 9.4 Record your environment

For the SC26 paper, we need your exact environment. Run and save:

```bash
echo "=== Erel's Machine Environment ===" > environment_erel.txt
echo "Date: $(date)" >> environment_erel.txt
echo "Hostname: $(hostname)" >> environment_erel.txt
echo "" >> environment_erel.txt
echo "OS:" >> environment_erel.txt
lsb_release -a >> environment_erel.txt 2>&1
echo "" >> environment_erel.txt
echo "Kernel:" >> environment_erel.txt
uname -a >> environment_erel.txt
echo "" >> environment_erel.txt
echo "GPU:" >> environment_erel.txt
nvidia-smi >> environment_erel.txt
echo "" >> environment_erel.txt
echo "CUDA:" >> environment_erel.txt
nvcc --version >> environment_erel.txt
echo "" >> environment_erel.txt
echo "GCC:" >> environment_erel.txt
gcc --version >> environment_erel.txt
echo "" >> environment_erel.txt
echo "Python:" >> environment_erel.txt
python3 --version >> environment_erel.txt
pip list >> environment_erel.txt 2>&1
echo "" >> environment_erel.txt
echo "NVC:" >> environment_erel.txt
nvc --version >> environment_erel.txt 2>&1

cat environment_erel.txt
```

Include `environment_erel.txt` when sharing results.

---

## Quick Reference

| What | Command |
|------|---------|
| Activate venv | `source env_parbench/bin/activate` |
| Validate specs | `python3 scripts/validate_schema.py --all` |
| Run unit tests | `python3 -m pytest c_augmentation/test_transforms.py -v` |
| Verify one spec | `python3 -m harness -v verify specs/rodinia-bfs-cuda.json` |
| Dry-run eval | `python3 scripts/evaluation/llm_evaluate.py --source X --target Y --model gemini-2.5-flash --project-root <path> --dry-run -v` |
| Start primary campaign | `bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash` |
| Start pass@k sweep | `bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k` |
| Attach to campaign | `bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash --attach` |
| Check progress | `ls results/evaluation/gemini-2.5-flash/*.json \| wc -l` |
| View campaign log | `tail -f results/evaluation/gemini-2_5-flash_campaign.log` |
| Run analysis | `python3 scripts/evaluation/analyze_eval.py --project-root <path> --write-dashboard` |
| Check symlink | `ls -la rodinia/rodinia-src` (should show `-> .`) |
