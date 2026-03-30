# Erel's ParBench Setup Guide

**Purpose:** Quick-start guide for running ParBench eval campaigns on Erel's machine.
For the full onboarding walkthrough, see `docs/erel_onboarding_guide.md`.

**Last updated:** 2026-03-30

---

## 1. Prerequisites

- Git, Python 3.12+, tmux, make, build-essential
- NVIDIA HPC SDK (25.7 on your machine)
- CUDA-capable GPU (RTX 4060 Laptop confirmed compatible -- same sm_89 as RTX 4070)

```bash
sudo apt install -y git python3 python3-venv python3-pip tmux make build-essential
```

---

## 2. Clone and Initialize

```bash
cd /root
git clone https://github.com/SamyakJhaveri/parbench_sam.git parbench
cd /root/parbench

# Initialize Rodinia submodule
git submodule update --init --recursive

# Create required symlink (specs reference rodinia/rodinia-src)
cd rodinia && ln -s . rodinia-src && cd ..

# Clone additional benchmark sources
mkdir -p xsbench rsbench mixbench
git clone https://github.com/ANL-CESAR/XSBench.git xsbench/xsbench-src
cd xsbench/xsbench-src && git checkout ba08e52 && cd ../..
git clone https://github.com/ANL-CESAR/RSBench.git rsbench/rsbench-src
cd rsbench/rsbench-src && git checkout 34b6447 && cd ../..
git clone https://github.com/ekondis/mixbench.git mixbench/mixbench-src
cd mixbench/mixbench-src && git checkout 32edeca && cd ../..
```

---

## 3. CUDA Path Fix (HPC SDK 25.7 vs 24.3)

51 spec files contain 114 hardcoded references to HPC SDK 24.3 paths. You have two options:

### Option A: Symlink (quick, no file changes)

```bash
sudo ln -s /opt/nvidia/hpc_sdk/Linux_x86_64/25.7 /opt/nvidia/hpc_sdk/Linux_x86_64/24.3
```

This makes all existing paths resolve without modifying any files.

### Option B: sed replacement (clean, modifies specs)

```bash
# Fix all spec files
sed -i 's|/opt/nvidia/hpc_sdk/Linux_x86_64/24.3|/opt/nvidia/hpc_sdk/Linux_x86_64/25.7|g' specs/*.json

# Fix Rodinia build config
sed -i 's|/opt/nvidia/hpc_sdk/Linux_x86_64/24.3|/opt/nvidia/hpc_sdk/Linux_x86_64/25.7|g' rodinia/common/make.config
sed -i 's|/opt/nvidia/hpc_sdk/Linux_x86_64/24.3|/opt/nvidia/hpc_sdk/Linux_x86_64/25.7|g' rodinia/cuda/lavaMD/makefile
```

OpenCL specs also reference `OPENCL_INC` and `OPENCL_LIB` from the HPC SDK -- both are
covered by the same path prefix replacement above.

**Verify no stale 24.3 references remain:**
```bash
grep -r "24.3" specs/*.json rodinia/common/make.config | head -5
# Should return nothing after the fix
```

Also apply the Rodinia toolchain patches (GPU arch flags, etc.):
```bash
cd rodinia && git apply ../docs/rodinia_toolchain_patches.diff && cd ..
```

---

## 4. Configuration

### 4.1 config/paths.json

Update project root paths, or delete the file (the `--project-root` CLI flag overrides it):

```json
{
    "project_root": "/root/parbench",
    "downloads_root": "/root/parbench",
    "hecbench_root": "/root/parbench"
}
```

### 4.2 Python environment

```bash
cd /root/parbench
python3 -m venv env_parbench
source env_parbench/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install scipy  # needed for paper figure generation
```

### 4.3 API keys

```bash
export GEMINI_API_KEY="your-key-here"
# Add to ~/.bashrc for persistence
```

---

## 5. Pull Pipeline Fixes First

**Critical:** Before running any eval campaign, ensure you have the latest pipeline fixes
merged. Without the source-args fix, approximately 20-30% of VERIFY_FAILs and RUN_FAILs
are false negatives caused by argument mismatches between source and target specs.

```bash
cd /root/parbench
git pull origin main
```

---

## 6. Verification Checklist

Run these before starting any campaign:

```bash
source env_parbench/bin/activate

# Schema validation (~135 HeCBench errors are expected -- ignore them)
python3 scripts/validate_schema.py --all

# Unit tests (all 15 must pass)
python3 -m pytest c_augmentation/test_transforms.py -v

# Harness smoke test
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
python3 -m harness -v verify specs/rodinia-bfs-omp.json
# Both should show PASS
```

---

## 7. Running Eval Campaigns

### Single model, single direction

```bash
source env_parbench/bin/activate

python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models gemini-2.5-flash \
  --project-root /root/parbench \
  --resume -v
```

### All directions for one model

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction all \
  --models gemini-2.5-flash \
  --project-root /root/parbench \
  --resume -v
```

### Full campaign (tmux, survives SSH disconnect)

```bash
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash
# Attach: tmux attach -t gemini-2_5-flash_campaign
# Detach: Ctrl+B, then D
```

**Note:** Always pass `--suite rodinia` to avoid matching HeCBench kernels by name.

---

## 8. Known Issues

- **Git worktrees** do NOT initialize the Rodinia submodule -- always run from the main repo
- **8 KNOWN_FAIL specs** are auto-excluded from eval batches:
  `kmeans-cuda`, `mummergpu-cuda`, `mummergpu-omp`, `hybridsort-cuda`,
  `nn-opencl`, `kmeans-opencl`, `hecbench-stencil1d-omp_target`, `hecbench-scan-omp_target`
- **Results** are written to `results/evaluation/{model}/` -- use `--resume` to skip existing
- **Rate limiting (429):** Re-run the same command; `--resume` skips completed tasks

---

## 9. Verifying Results

```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root /root/parbench \
  --output-dir results/evaluation

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
print(f'Total: {total}, PASS: {passes}/{total} ({100*passes/total:.1f}%)')
for s, n in sorted(counts.items(), key=lambda x: -x[1]):
    print(f'  {s}: {n}')
"
```

### Sharing results with Samyak

```bash
# Option 1: tarball
tar czf gemini-2.5-flash-results.tar.gz \
  results/evaluation/gemini-2.5-flash/ \
  results/evaluation/eval_summary.json

# Option 2: push to a branch
git checkout -b erel/gemini-2.5-flash-results
git add results/evaluation/gemini-2.5-flash/
git commit -m "Add Gemini 2.5 Flash eval results (Erel's machine, RTX 4060 Laptop)"
git push -u origin erel/gemini-2.5-flash-results
```
