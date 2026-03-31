# Erel's ParBench Setup & Campaign Guide

**Purpose:** Quick-start guide for running ParBench eval campaigns on Erel's machine.
For the full onboarding walkthrough, see `docs/erel_onboarding_guide.md`.

**Last updated:** 2026-03-30 (updated with full redo instructions for Gemini primary + pass@k)

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

## 5. Pull Latest Pipeline Fixes

**Critical:** Before running any eval campaign, pull the latest code. Recent commits
fix issues that affect result correctness:

- **pass@k filename collision fix** (`0b952d9`): When `--num-samples > 1`, sample 0
  now gets a `-s0` tag, preventing overwrites with primary campaign L0 results.
- **cross-API run args fix** (`3fbaacf`): Target spec run arguments are now correctly
  generated for cross-API translations (fixes ~20-30% false VERIFY_FAIL/RUN_FAIL).
- **Qwen eval data + figure updates** (`2d6e4ac`, `37dc809`): Updated paper figures
  and viz data.

```bash
cd /root/parbench
git pull origin main
```

---

## 6. Clear Old Gemini Results (REQUIRED before redo)

**You must delete all existing Gemini results before re-running the campaign.**
The `--resume` flag skips tasks whose result files already exist on disk. If you don't
delete them first, the campaign will skip everything and think it's already done.

```bash
# Delete ALL existing Gemini primary + pass@k results
rm -rf /root/parbench/results/evaluation/gemini-2.5-flash/

# Also delete old log/marker files
rm -f /root/parbench/results/evaluation/gemini-2_5-flash_campaign.log
rm -f /root/parbench/results/evaluation/gemini-2_5-flash_campaign_done.marker
rm -f /root/parbench/results/evaluation/gemini-2_5-flash_passk.log
rm -f /root/parbench/results/evaluation/gemini-2_5-flash_passk_done.marker

# Verify the directory is gone
ls /root/parbench/results/evaluation/gemini-2.5-flash/ 2>/dev/null && echo "NOT CLEAN" || echo "CLEAN -- ready to go"
```

---

## 7. Verification Checklist

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

## 8. Update Campaign Script Paths

The campaign script has two hardcoded paths that point to Samyak's machine.
You MUST change them to your project root before running:

```bash
nano scripts/batch/run_eval_campaign.sh
```

**Change line 44:**
```bash
# FROM:
PROJECT_ROOT="/home/samyak/Desktop/parbench_sam"
# TO:
PROJECT_ROOT="/root/parbench"
```

**Change line 477 (inside the Python heredoc):**
```python
# FROM:
BASE = "/home/samyak/Desktop/parbench_sam"
# TO:
BASE = "/root/parbench"
```

**Verify no stale paths remain:**
```bash
grep -n "samyak" scripts/batch/run_eval_campaign.sh
# Should return nothing
```

---

## 9. Running the Gemini Eval Campaign (Full Redo)

The campaign runs **28 batches** across 5 suites (Rodinia, XSBench, RSBench, mixbench,
HeCBench) and 6 translation directions each. It self-launches in a tmux session so you
can safely disconnect SSH.

### Step 1: Primary campaign (790 tasks)

This runs all 158 source-target pairs at 5 augmentation levels (L0-L4), with iterative
self-repair (up to 3 attempts per task), deterministic decoding (temperature=0.0).

```bash
cd /root/parbench
source env_parbench/bin/activate
export GEMINI_API_KEY="your-key-here"

bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash
```

**Monitor progress:**
```bash
# Attach to tmux session
tmux attach -t gemini-2_5-flash_campaign
# Detach without stopping: Ctrl+B, then D

# Or watch the log file
tail -f results/evaluation/gemini-2_5-flash_campaign.log

# Count completed result files
ls results/evaluation/gemini-2.5-flash/*.json 2>/dev/null | wc -l
# Target: ~790 files (some KNOWN_FAIL specs produce fewer)
```

**If interrupted (SSH drops, reboot, etc.):** Just re-run the exact same command.
`--resume` skips completed tasks automatically:
```bash
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash
```

**When it finishes**, check the done marker:
```bash
cat results/evaluation/gemini-2_5-flash_campaign_done.marker
```

### Step 2: Pass@k sweep (474 tasks) — run AFTER primary completes

This runs 158 pairs at L0 only, with 3 independent stochastic samples per pair
(temperature=0.7), zero-shot (no retries). Result files get `-s0` through `-s2` tags,
so they do NOT collide with primary campaign results.

```bash
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k
```

**Monitor:**
```bash
tmux attach -t gemini-2_5-flash_passk
# Or:
tail -f results/evaluation/gemini-2_5-flash_passk.log
```

**If interrupted:** Same as primary — just re-run:
```bash
bash scripts/batch/run_eval_campaign.sh gemini-2.5-flash pass@k
```

### Alternative: Manual batch commands (if you prefer not to use the campaign script)

You can run individual suite+direction batches directly. This gives you more control
but requires you to run each direction manually.

**Primary mode (one suite, one direction):**
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models gemini-2.5-flash \
  --augment-levels 0 1 2 3 4 \
  --max-retries 3 \
  --temperature 0.0 \
  --num-samples 1 \
  --project-root /root/parbench \
  --resume -v
```

**Pass@k mode (one suite, one direction):**
```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models gemini-2.5-flash \
  --augment-levels 0 \
  --max-retries 1 \
  --temperature 0.7 \
  --num-samples 3 \
  --project-root /root/parbench \
  --resume -v
```

**All 6 directions per suite (primary example):**
```bash
for DIR in cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp; do
  python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction $DIR \
    --models gemini-2.5-flash \
    --augment-levels 0 1 2 3 4 \
    --max-retries 3 --temperature 0.0 --num-samples 1 \
    --project-root /root/parbench --resume -v
done
```

Repeat the loop above for each suite: `rodinia`, `xsbench`, `rsbench`, `mixbench`.
HeCBench requires `--kernels` to filter to curated kernels (the campaign script handles
this automatically — see the script source for the exact kernel lists).

---

## 10. Known Issues

- **Git worktrees** do NOT initialize the Rodinia submodule -- always run from the main repo
- **8 KNOWN_FAIL specs** are auto-excluded from eval batches:
  `kmeans-cuda`, `mummergpu-cuda`, `mummergpu-omp`, `hybridsort-cuda`,
  `nn-opencl`, `kmeans-opencl`, `hecbench-stencil1d-omp_target`, `hecbench-scan-omp_target`
- **Results** are written to `results/evaluation/{model}/` -- use `--resume` to skip existing
- **Rate limiting (429):** Re-run the same command; `--resume` skips completed tasks
- **pass@k result files** now use `-s0` through `-s2` tags (even sample 0). They do NOT
  overwrite primary campaign results. Both can coexist in the same directory.

---

## 11. Post-Campaign: Verify & Share Results

### Verify completeness

After BOTH campaigns (primary + pass@k) are done:

```bash
source env_parbench/bin/activate

# Count primary results (no -s tag)
PRIMARY=$(ls results/evaluation/gemini-2.5-flash/*.json 2>/dev/null | grep -v '\-s[0-9]' | wc -l)
echo "Primary results: $PRIMARY (target: ~790)"

# Count pass@k results (-s0 through -s2 tags)
PASSK=$(ls results/evaluation/gemini-2.5-flash/*-s[0-9].json 2>/dev/null | wc -l)
echo "Pass@k results: $PASSK (target: ~474)"

# Per-suite breakdown
for SUITE in rodinia xsbench rsbench mixbench hecbench; do
  COUNT=$(ls results/evaluation/gemini-2.5-flash/${SUITE}-*.json 2>/dev/null | wc -l)
  echo "  $SUITE: $COUNT files"
done
```

### Quick status breakdown

```bash
python3 -c "
import json, glob
files = glob.glob('results/evaluation/gemini-2.5-flash/*.json')
# Separate primary vs pass@k
primary = [f for f in files if '-s0.' not in f and '-s1.' not in f and '-s2.' not in f]
passk = [f for f in files if f not in primary]

for label, flist in [('PRIMARY', primary), ('PASS@K', passk)]:
    counts = {}
    for f in flist:
        r = json.loads(open(f).read())
        s = r.get('overall_status', 'UNKNOWN')
        counts[s] = counts.get(s, 0) + 1
    total = len(flist)
    passes = counts.get('PASS', 0)
    print(f'{label}: {passes}/{total} PASS ({100*passes/total:.1f}%)' if total else f'{label}: no results')
    for s, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f'  {s}: {n}')
    print()
"
```

### Run the analysis pipeline

```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root /root/parbench \
  --write-dashboard
```

### Share results with Samyak

```bash
# Option 1: tarball (includes both primary + pass@k)
tar czf gemini-2.5-flash-results.tar.gz \
  results/evaluation/gemini-2.5-flash/ \
  results/evaluation/eval_summary.json \
  results/evaluation/eval_summary.md \
  results/evaluation/gemini-2_5-flash_campaign.log \
  results/evaluation/gemini-2_5-flash_campaign_done.marker \
  results/evaluation/gemini-2_5-flash_passk.log \
  results/evaluation/gemini-2_5-flash_passk_done.marker

# Option 2: push to a branch
git checkout -b erel/gemini-2.5-flash-redo
git add results/evaluation/gemini-2.5-flash/
git add results/evaluation/eval_summary.json results/evaluation/eval_summary.md
git commit -m "Gemini 2.5 Flash eval redo: primary + pass@k (RTX 4060 Laptop, post pipeline fixes)"
git push -u origin erel/gemini-2.5-flash-redo
```
