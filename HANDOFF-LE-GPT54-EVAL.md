# HANDOFF — azure-gpt-5.4 Evaluation Campaign (NeurIPS 2026)

**Audience:** Le (or any fresh operator setting up ParBench on a new Linux GPU machine to run the `azure-gpt-5.4` evaluation campaign)
**Goal:** Clone the repo, adapt paths to your machine, verify the pipeline, and run Study 1 (canonical pass@3) + Study 2 (L0-conditional ablation) end-to-end for the NeurIPS 2026 paper.

This document is self-contained. Follow it linearly. Every `# <-- CHANGE THIS` marker is a place where you substitute your machine's value.

---

## Table of Contents

1. Machine Prerequisites
2. Clone & Setup
3. Benchmark Source Acquisition (all 5 suites)
4. Adapt Paths to Your Machine (CRITICAL)
5. Verify Setup (Smoke Tests)
6. Azure API Key Setup
7. Understanding the Experiment Protocol
8. Shell Setup (copy into every tmux session)
9. Run Canonical Evaluations (Study 1) — 30 commands
10. Derive L0 Passers (between Study 1 and Study 2)
11. Run Ablation Evaluations (Study 2) — 6 commands
12. Post-Eval Analysis
13. Troubleshooting
14. 8 KNOWN_FAIL Specs (excluded automatically)

---

## 1. Machine Prerequisites

- Ubuntu 22.04 or 24.04 LTS
- Python 3.12+
- NVIDIA GPU with CUDA 12.x support
- NVIDIA CUDA Toolkit 12.x (`nvcc`)
- NVIDIA HPC SDK 24.3+ (`nvc++` — required for OpenMP target offloading specs)
- GCC 12+ with OpenMP support (`-fopenmp`)
- `tmux` (for long-running eval sessions)
- `git`, `wget`, `unzip`
- Azure OpenAI deployment named **exactly** `gpt-5.4`, with:
  - `AZURE_OPENAI_API_KEY`
  - `AZURE_OPENAI_ENDPOINT` (e.g., `https://your-resource.openai.azure.com/`)
  - TPM quota ≥ 200k sustained

---

## 2. Clone & Setup

```bash
# 1. Clone
git clone <repo-url> parbench_sam
cd parbench_sam
export PROJECT_ROOT=$(pwd)     # MUST be absolute — used in every command below

# 2. Submodules (Rodinia benchmark source)
git submodule update --init --recursive
# This clones Rodinia at pinned commit 9c10d3ea into rodinia/

# 3. CRITICAL: create the rodinia-src symlink (not in git)
# Specs reference paths like "rodinia/rodinia-src/cuda/bfs/bfs.cu".
# The submodule populates rodinia/, so we need rodinia-src -> . inside it.
ln -s . rodinia/rodinia-src
# Verify:
ls rodinia/rodinia-src/cuda/bfs/bfs.cu    # must exist

# 4. Python venv
python3 -m venv env_parbench
source env_parbench/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements-lock.txt

# Verify deps:
python3 -c "import pydantic, jsonschema, openai; print('deps OK')"
python3 -m harness --help     # Should show: build, run, verify, prompt, info, pairs

# 5. Config file — MUST create before harness works
sed "s|{{PROJECT_ROOT}}|$PROJECT_ROOT|g" config/paths.json.template > config/paths.json
cat config/paths.json    # Sanity check — all three paths should point at $PROJECT_ROOT
```

Expected `config/paths.json`:
```json
{
    "project_root": "/abs/path/to/parbench_sam",
    "downloads_root": "/abs/path/to/parbench_sam",
    "hecbench_root": "/abs/path/to/parbench_sam"
}
```

---

## 3. Benchmark Source Acquisition (all 5 suites)

| Suite    | Acquisition                                                        | Target directory       |
|----------|--------------------------------------------------------------------|------------------------|
| Rodinia  | Git submodule at `9c10d3ea` + symlink (done in §2)                 | `rodinia/` (with `rodinia-src -> .` symlink) |
| HeCBench | ZIP download from GitHub (`master` branch, unpinned)               | `HeCBench-master/`     |
| XSBench  | Git clone at `ba08e5221af6106252b866e50ea123c69d31a4e2`            | `xsbench/xsbench-src/` |
| RSBench  | Git clone at `34b644787ea9af4fb188e1253da72e09bbed9989`            | `rsbench/rsbench-src/` |
| mixbench | Git clone at `32edeca98bdd63b32769e3c7460676b9fd567f06`            | `mixbench/mixbench-src/` |

### Exact commands

```bash
cd $PROJECT_ROOT

# HeCBench (1.4 GB zipped — ~2 min download)
wget https://github.com/zjin-lcf/HeCBench/archive/refs/heads/master.zip -O hecbench.zip
unzip -q hecbench.zip     # produces HeCBench-master/
rm hecbench.zip

# XSBench
mkdir -p xsbench && cd xsbench
git clone https://github.com/ANL-CESAR/XSBench xsbench-src
cd xsbench-src && git checkout ba08e5221af6106252b866e50ea123c69d31a4e2
cd $PROJECT_ROOT

# RSBench
mkdir -p rsbench && cd rsbench
git clone https://github.com/ANL-CESAR/RSBench rsbench-src
cd rsbench-src && git checkout 34b644787ea9af4fb188e1253da72e09bbed9989
cd $PROJECT_ROOT

# mixbench
mkdir -p mixbench && cd mixbench
git clone https://github.com/ekondis/mixbench mixbench-src
cd mixbench-src && git checkout 32edeca98bdd63b32769e3c7460676b9fd567f06
cd $PROJECT_ROOT

# Verify all sources present:
ls rodinia/rodinia-src/cuda/bfs/bfs.cu            # Rodinia CUDA source
ls HeCBench-master/src/nn-cuda/main.cu             # HeCBench CUDA source
ls xsbench/xsbench-src/cuda/Main.cu                # XSBench CUDA source
ls rsbench/rsbench-src/cuda/main.cu                # RSBench CUDA source
ls mixbench/mixbench-src/mixbench-cuda/main.cu     # mixbench CUDA source
```

---

## 4. Adapt Paths to Your Machine (CRITICAL)

The reference machine has hardcoded absolute paths embedded in the spec JSONs and in the Rodinia Makefile patch. Le's machine almost certainly differs. You must bulk-rewrite these **before** anything will build.

**What's hardcoded on the reference machine:**
- CUDA root: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda` (embedded in 39 spec JSONs)
- `nvc++` path: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc++` (embedded in 10 `omp_target` spec JSONs)
- GPU compute capability: `sm_89` / `cc89` (embedded in 206 spec JSONs — RTX 4070 Ada Lovelace)

### 4a. Detect your toolchain paths

```bash
# CUDA installation:
which nvcc
# Typical: /usr/local/cuda/bin/nvcc  →  CUDA_DIR = /usr/local/cuda

# NVIDIA HPC SDK (for nvc++):
which nvc++
# Typical: /opt/nvidia/hpc_sdk/Linux_x86_64/24.X/compilers/bin/nvc++
```

### 4b. Detect your GPU compute capability

```bash
nvidia-smi --query-gpu=compute_cap --format=csv,noheader
# Examples:
#   8.9 → sm_89 / cc89 (RTX 4070)
#   8.0 → sm_80 / cc80 (A100)
#   9.0 → sm_90 / cc90 (H100)
```

### 4c. Bulk-replace hardcoded paths in ALL spec JSONs

Edit the three variables below, then run the block as-is:

```bash
# ===== EDIT THESE =====
NEW_CUDA="/usr/local/cuda"                              # <-- CHANGE THIS to your CUDA root
NEW_NVC="$(which nvc++)"                                # auto-detect, or set manually
NEW_SM="sm_80"                                          # <-- CHANGE THIS to your sm_XX
# ======================

OLD_CUDA="/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda"
OLD_NVC="/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/compilers/bin/nvc++"
OLD_SM="sm_89"
OLD_CC="cc89"
NEW_CC="cc${NEW_SM#sm_}"

# Replace CUDA root (39 specs)
find specs/ -name '*.json' -exec sed -i "s|$OLD_CUDA|$NEW_CUDA|g" {} +

# Replace nvc++ path (10 omp_target specs)
find specs/ -name '*.json' -exec sed -i "s|$OLD_NVC|$NEW_NVC|g" {} +

# Replace GPU compute capability (206 specs)
find specs/ -name '*.json' -exec sed -i "s|$OLD_SM|$NEW_SM|g" {} +
find specs/ -name '*.json' -exec sed -i "s|$OLD_CC|$NEW_CC|g" {} +

# Sanity check — these should return 0:
grep -l "$OLD_CUDA" specs/*.json | wc -l
grep -l "$OLD_NVC" specs/*.json | wc -l
grep -l "$OLD_SM" specs/*.json | wc -l
```

**DO NOT commit these changes.** They are local-only adaptations.

### 4d. Apply Rodinia Makefile patches (AFTER §4c path rewrite)

The patch fixes Rodinia Makefiles for CUDA 12 and OpenCL compilation. The patch file itself contains the reference machine's `sm_89` and HPC SDK paths — apply, then rewrite.

```bash
cd $PROJECT_ROOT/rodinia/rodinia-src

# Apply the patch:
git apply ../../docs/rodinia_toolchain_patches.diff

# The patch embedded sm_89 and the HPC SDK CUDA path — rewrite them:
find . -name 'Makefile*' -exec sed -i "s|$OLD_CUDA|$NEW_CUDA|g" {} +
find . -name 'Makefile*' -exec sed -i "s|$OLD_SM|$NEW_SM|g" {} +
find . -name 'Makefile*' -exec sed -i "s|compute_89|compute_${NEW_SM#sm_}|g" {} +

cd $PROJECT_ROOT
```

---

## 5. Verify Setup (Smoke Tests)

```bash
source env_parbench/bin/activate

# 5a. Schema validation — ~15 errors are EXPECTED (phantom specs in manifest.jsonl)
python3 scripts/validate_schema.py --all
# Expected: ~15 errors. Anything beyond that indicates a real problem.

# 5b. Single CUDA spec build + run + verify
python3 -m harness -v verify specs/rodinia-bfs-cuda.json --project-root $PROJECT_ROOT
# Expected: BUILD: PASS | RUN: PASS | VERIFY: PASS

# 5c. Single OMP spec
python3 -m harness -v verify specs/rodinia-bfs-omp.json --project-root $PROJECT_ROOT
# Expected: PASS

# 5d. Single OpenCL spec
python3 -m harness -v verify specs/rodinia-bfs-opencl.json --project-root $PROJECT_ROOT
# Expected: PASS

# 5e. Full 88-spec sweep (~10-15 min)
python3 scripts/spec_tools/run_verify_sweep.py \
    --project-root $PROJECT_ROOT \
    --exclude-known-fail \
    --jobs 4
# Expected: PASS 88/88. If anything fails, re-check §4c/§4d.

# 5f. Verify Azure API path (dry run — no API call)
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

python3 scripts/evaluation/llm_evaluate.py \
    --source specs/rodinia-bfs-cuda.json \
    --target specs/rodinia-bfs-omp.json \
    --model azure-gpt-5.4 \
    --project-root $PROJECT_ROOT \
    --dry-run -v
# Expected: prints the prompt that would be sent. No actual API call.
```

If §5e passes 88/88, the pipeline is ready.

---

## 6. Azure API Key Setup

```bash
export AZURE_OPENAI_API_KEY="your-azure-api-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

**Critical facts about the Azure integration:**
- Your Azure deployment must be named **exactly** `gpt-5.4`. The pipeline strips the `azure-` prefix from the model ID: `azure-gpt-5.4 → gpt-5.4` (see `scripts/evaluation/llm_evaluate.py:917`).
- API version: `2025-01-01-preview`.
- When `--thinking on`, the pipeline injects `reasoning_effort="medium"` and **omits** `temperature` / `top_p`. Azure reasoning models reject `temperature != 1`.
- Model registry entry: `scripts/evaluation/llm_evaluate.py:110`.

Persist the env vars in `~/.bashrc` if you want them across sessions. Otherwise export in every tmux session (§8).

---

## 7. Understanding the Experiment Protocol

Two studies run **sequentially**. Do NOT start Study 2 until Study 1 is complete for the directions you care about — Study 2 depends on Study 1's L0 passer set.

### Study 1 — Canonical (run first)

- **Purpose:** Best-effort model capability measurement.
- **Sampling:** pass@3 — 3 samples per (source_spec, target_spec) pair.
- **Temperature:** `0.7` (ignored for Azure reasoning models; kept for record-keeping).
- **Augmentation:** L0 only (unperturbed source).
- **Thinking:** ON (`reasoning_effort="medium"` on Azure).
- **Self-repair:** OFF (`--max-retries 1` = zero-shot, no error-feedback loop).
- **Scope:** 88 curated non-KNOWN_FAIL specs × 6 directions × 3 samples.

### Study 2 — Ablation (run after canonical)

- **Purpose:** Robustness to semantic-preserving source perturbations.
- **Filter:** Only pairs where **≥ 1 of the 3 canonical samples PASSED** at L0 (pass@1-of-any).
- **Sampling:** pass@1 — 1 sample per (pair, level).
- **Temperature:** `0.0` (greedy).
- **Augmentation:** L0, L1, L2, L3, L4 (5 levels).
- **Thinking:** ON.
- **Self-repair:** OFF (`--max-retries 1`).
- **Scope:** L0-passer subset × 6 directions × 5 levels × 1 sample.

### Translation directions (6)

- `cuda-to-omp`, `omp-to-cuda`
- `cuda-to-opencl`, `opencl-to-cuda`
- `omp-to-opencl`, `opencl-to-omp`

### Benchmark suites (5) — separate invocation each

- `rodinia`, `hecbench`, `xsbench`, `rsbench`, `mixbench`

### Result file location

- Per-task: `results/evaluation/azure-gpt-5.4/{src_id}-to-{tgt_id}[-L{n}][-s{k}].json`
- `--resume` (default on) skips any (pair, level, sample) with an existing result JSON — keyed on **file existence**, not on parameters. If prior runs used wrong params, delete the specific file(s) first.

---

## 8. Shell Setup (copy into every tmux session)

Paste this at the top of every tmux session before launching eval commands:

```bash
export PROJECT_ROOT=/path/to/parbench_sam           # <-- CHANGE THIS
cd "$PROJECT_ROOT" && source env_parbench/bin/activate
export AZURE_OPENAI_API_KEY="your-key"              # <-- CHANGE THIS
export AZURE_OPENAI_ENDPOINT="https://..."          # <-- CHANGE THIS
AZURE=azure-gpt-5.4

# Registry sanity check:
python3 -c "from scripts.evaluation.llm_evaluate import MODEL_REGISTRY; assert '$AZURE' in MODEL_REGISTRY; print('registry OK')"

mkdir -p logs .planning/eval-selections
```

---

## 9. Run Canonical Evaluations (Study 1)

**Structure:** one tmux session per (suite, direction). 5 suites × 6 directions = **30 invocations**.

Key constraints:
- `--suite` is **required** (one value per invocation) to avoid cross-suite name collisions.
- `--suite` and `--task-list` are **mutually exclusive** — canonical uses `--suite`.
- Many (suite × direction) combos have zero eligible pairs (e.g., mixbench has no `opencl→omp` pair). `run_eval_batch.py` exits fast with 0 tasks — no harm running them all.
- Don't launch all 30 simultaneously — Azure TPM will throttle. Run in batches of 2–4.

### Template

Substitute `{SUITE}` and `{DIRECTION}`:

```bash
tmux new-session -d -s p3-az-{SUITE}-{DIR} "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
export AZURE_OPENAI_API_KEY='$AZURE_OPENAI_API_KEY' && export AZURE_OPENAI_ENDPOINT='$AZURE_OPENAI_ENDPOINT' && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite {SUITE} \
    --direction {DIRECTION} \
    --models azure-gpt-5.4 \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a logs/phase3-azure-{SUITE}-{DIR}.log"
```

### Full matrix — 30 commands

Replace the `tmux new-session -d -s` line's session name and the `--suite` / `--direction` / log path as shown. Everything else is identical.

#### rodinia (6)
```
SUITE=rodinia  DIRECTION=cuda-to-omp       SESSION=p3-az-rodinia-c2o     LOG=logs/phase3-azure-rodinia-c2o.log
SUITE=rodinia  DIRECTION=omp-to-cuda       SESSION=p3-az-rodinia-o2c     LOG=logs/phase3-azure-rodinia-o2c.log
SUITE=rodinia  DIRECTION=cuda-to-opencl    SESSION=p3-az-rodinia-c2ocl   LOG=logs/phase3-azure-rodinia-c2ocl.log
SUITE=rodinia  DIRECTION=opencl-to-cuda    SESSION=p3-az-rodinia-ocl2c   LOG=logs/phase3-azure-rodinia-ocl2c.log
SUITE=rodinia  DIRECTION=omp-to-opencl     SESSION=p3-az-rodinia-o2ocl   LOG=logs/phase3-azure-rodinia-o2ocl.log
SUITE=rodinia  DIRECTION=opencl-to-omp     SESSION=p3-az-rodinia-ocl2o   LOG=logs/phase3-azure-rodinia-ocl2o.log
```

#### hecbench (6)
```
SUITE=hecbench  DIRECTION=cuda-to-omp       SESSION=p3-az-hecbench-c2o     LOG=logs/phase3-azure-hecbench-c2o.log
SUITE=hecbench  DIRECTION=omp-to-cuda       SESSION=p3-az-hecbench-o2c     LOG=logs/phase3-azure-hecbench-o2c.log
SUITE=hecbench  DIRECTION=cuda-to-opencl    SESSION=p3-az-hecbench-c2ocl   LOG=logs/phase3-azure-hecbench-c2ocl.log
SUITE=hecbench  DIRECTION=opencl-to-cuda    SESSION=p3-az-hecbench-ocl2c   LOG=logs/phase3-azure-hecbench-ocl2c.log
SUITE=hecbench  DIRECTION=omp-to-opencl     SESSION=p3-az-hecbench-o2ocl   LOG=logs/phase3-azure-hecbench-o2ocl.log
SUITE=hecbench  DIRECTION=opencl-to-omp     SESSION=p3-az-hecbench-ocl2o   LOG=logs/phase3-azure-hecbench-ocl2o.log
```

#### xsbench (6)
```
SUITE=xsbench   DIRECTION=cuda-to-omp       SESSION=p3-az-xsbench-c2o      LOG=logs/phase3-azure-xsbench-c2o.log
SUITE=xsbench   DIRECTION=omp-to-cuda       SESSION=p3-az-xsbench-o2c      LOG=logs/phase3-azure-xsbench-o2c.log
SUITE=xsbench   DIRECTION=cuda-to-opencl    SESSION=p3-az-xsbench-c2ocl    LOG=logs/phase3-azure-xsbench-c2ocl.log
SUITE=xsbench   DIRECTION=opencl-to-cuda    SESSION=p3-az-xsbench-ocl2c    LOG=logs/phase3-azure-xsbench-ocl2c.log
SUITE=xsbench   DIRECTION=omp-to-opencl     SESSION=p3-az-xsbench-o2ocl    LOG=logs/phase3-azure-xsbench-o2ocl.log
SUITE=xsbench   DIRECTION=opencl-to-omp     SESSION=p3-az-xsbench-ocl2o    LOG=logs/phase3-azure-xsbench-ocl2o.log
```

#### rsbench (6)
```
SUITE=rsbench   DIRECTION=cuda-to-omp       SESSION=p3-az-rsbench-c2o      LOG=logs/phase3-azure-rsbench-c2o.log
SUITE=rsbench   DIRECTION=omp-to-cuda       SESSION=p3-az-rsbench-o2c      LOG=logs/phase3-azure-rsbench-o2c.log
SUITE=rsbench   DIRECTION=cuda-to-opencl    SESSION=p3-az-rsbench-c2ocl    LOG=logs/phase3-azure-rsbench-c2ocl.log
SUITE=rsbench   DIRECTION=opencl-to-cuda    SESSION=p3-az-rsbench-ocl2c    LOG=logs/phase3-azure-rsbench-ocl2c.log
SUITE=rsbench   DIRECTION=omp-to-opencl     SESSION=p3-az-rsbench-o2ocl    LOG=logs/phase3-azure-rsbench-o2ocl.log
SUITE=rsbench   DIRECTION=opencl-to-omp     SESSION=p3-az-rsbench-ocl2o    LOG=logs/phase3-azure-rsbench-ocl2o.log
```

#### mixbench (6)
```
SUITE=mixbench  DIRECTION=cuda-to-omp       SESSION=p3-az-mixbench-c2o     LOG=logs/phase3-azure-mixbench-c2o.log
SUITE=mixbench  DIRECTION=omp-to-cuda       SESSION=p3-az-mixbench-o2c     LOG=logs/phase3-azure-mixbench-o2c.log
SUITE=mixbench  DIRECTION=cuda-to-opencl    SESSION=p3-az-mixbench-c2ocl   LOG=logs/phase3-azure-mixbench-c2ocl.log
SUITE=mixbench  DIRECTION=opencl-to-cuda    SESSION=p3-az-mixbench-ocl2c   LOG=logs/phase3-azure-mixbench-ocl2c.log
SUITE=mixbench  DIRECTION=omp-to-opencl     SESSION=p3-az-mixbench-o2ocl   LOG=logs/phase3-azure-mixbench-o2ocl.log
SUITE=mixbench  DIRECTION=opencl-to-omp     SESSION=p3-az-mixbench-ocl2o   LOG=logs/phase3-azure-mixbench-ocl2o.log
```

### Example launch (concrete command)

```bash
tmux new-session -d -s p3-az-rodinia-c2o "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
export AZURE_OPENAI_API_KEY='$AZURE_OPENAI_API_KEY' && export AZURE_OPENAI_ENDPOINT='$AZURE_OPENAI_ENDPOINT' && \
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia \
    --direction cuda-to-omp \
    --models azure-gpt-5.4 \
    --augment-levels 0 \
    --num-samples 3 \
    --temperature 0.7 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a logs/phase3-azure-rodinia-c2o.log"
```

### Monitor progress

```bash
tmux list-sessions                                          # all active sessions
tmux attach -t p3-az-rodinia-c2o                             # watch one (C-b d to detach)
ls -lt results/evaluation/azure-gpt-5.4/*.json | head -5    # latest completed tasks
ls results/evaluation/azure-gpt-5.4/ | wc -l                 # total results so far
tail -f logs/phase3-azure-rodinia-c2o.log                    # follow log
```

---

## 10. Derive L0 Passers (between Study 1 and Study 2)

After ALL canonical runs complete for a given direction, derive that direction's L0-passer set. Ablation consumes these as `--task-list` files. Run all 6:

```bash
mkdir -p .planning/eval-selections

for DIR_TUPLE in \
    "cuda-to-omp:c2o" \
    "omp-to-cuda:o2c" \
    "cuda-to-opencl:c2ocl" \
    "opencl-to-cuda:ocl2c" \
    "omp-to-opencl:o2ocl" \
    "opencl-to-omp:ocl2o"; do
    DIR="${DIR_TUPLE%%:*}"
    TAG="${DIR_TUPLE##*:}"
    python3 -m scripts.evaluation.derive_l0_passers \
        --canonical-dir results/evaluation/azure-gpt-5.4 \
        --model azure-gpt-5.4 \
        --direction "$DIR" \
        --out ".planning/eval-selections/l0_passers_azure_${TAG}.json"
done

# Sanity check — count passers per direction:
for f in .planning/eval-selections/l0_passers_azure_*.json; do
    printf "%s: %s pairs\n" "$(basename $f)" "$(python3 -c "import json; print(len(json.load(open('$f'))))")"
done
```

Each output JSON is a list of `{source_id, target_id}` pairs where ≥1 of the 3 canonical samples at L0 passed verification. These feed Study 2 as `--task-list`.

---

## 11. Run Ablation Evaluations (Study 2)

One tmux session per direction — 6 invocations. Key difference from canonical:
- Uses `--task-list` (NOT `--suite`). They are mutually exclusive.
- 5 augmentation levels: `--augment-levels 0 1 2 3 4`
- Single sample per (pair, level): `--num-samples 1`
- Greedy: `--temperature 0.0`

### Template

```bash
tmux new-session -d -s p3-az-abl-{DIR} "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
export AZURE_OPENAI_API_KEY='$AZURE_OPENAI_API_KEY' && export AZURE_OPENAI_ENDPOINT='$AZURE_OPENAI_ENDPOINT' && \
python3 scripts/evaluation/run_eval_batch.py \
    --task-list .planning/eval-selections/l0_passers_azure_{TAG}.json \
    --direction {DIRECTION} \
    --models azure-gpt-5.4 \
    --augment-levels 0 1 2 3 4 \
    --num-samples 1 \
    --temperature 0.0 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a logs/phase3-azure-abl-{TAG}.log"
```

### Full matrix — 6 commands

| DIRECTION        | TAG    | task-list                                                   | session            |
|------------------|--------|-------------------------------------------------------------|--------------------|
| `cuda-to-omp`    | c2o    | `.planning/eval-selections/l0_passers_azure_c2o.json`       | p3-az-abl-c2o      |
| `omp-to-cuda`    | o2c    | `.planning/eval-selections/l0_passers_azure_o2c.json`       | p3-az-abl-o2c      |
| `cuda-to-opencl` | c2ocl  | `.planning/eval-selections/l0_passers_azure_c2ocl.json`     | p3-az-abl-c2ocl    |
| `opencl-to-cuda` | ocl2c  | `.planning/eval-selections/l0_passers_azure_ocl2c.json`     | p3-az-abl-ocl2c    |
| `omp-to-opencl`  | o2ocl  | `.planning/eval-selections/l0_passers_azure_o2ocl.json`     | p3-az-abl-o2ocl    |
| `opencl-to-omp`  | ocl2o  | `.planning/eval-selections/l0_passers_azure_ocl2o.json`     | p3-az-abl-ocl2o    |

### Concrete example (cuda-to-omp)

```bash
tmux new-session -d -s p3-az-abl-c2o "cd $PROJECT_ROOT && source env_parbench/bin/activate && \
export AZURE_OPENAI_API_KEY='$AZURE_OPENAI_API_KEY' && export AZURE_OPENAI_ENDPOINT='$AZURE_OPENAI_ENDPOINT' && \
python3 scripts/evaluation/run_eval_batch.py \
    --task-list .planning/eval-selections/l0_passers_azure_c2o.json \
    --direction cuda-to-omp \
    --models azure-gpt-5.4 \
    --augment-levels 0 1 2 3 4 \
    --num-samples 1 \
    --temperature 0.0 \
    --thinking on \
    --max-retries 1 \
    --resume \
    --project-root $PROJECT_ROOT \
    -v 2>&1 | tee -a logs/phase3-azure-abl-c2o.log"
```

---

## 12. Post-Eval Analysis

After both studies are complete:

```bash
# Aggregate all results:
python3 scripts/evaluation/analyze_eval.py \
    --project-root $PROJECT_ROOT \
    --model azure-gpt-5.4 \
    --write-dashboard \
    --show-gaps \
    --expected-models azure-gpt-5.4 \
    --expected-directions cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp \
    --expected-levels 0 1 2 3 4

# Outputs:
#   results/evaluation/eval_summary.json  (machine-readable)
#   results/evaluation/eval_summary.md    (publication-ready tables)
#   visualizations/eval_results_data.js   (dashboard data, if --write-dashboard)

# Refresh visualization data:
python3 scripts/generate_viz_data.py --project-root $PROJECT_ROOT
```

---

## 13. Troubleshooting

| Symptom | Diagnosis & Fix |
|---|---|
| BUILD_FAIL on every spec | `CUDA_DIR` / `sm_XX` still wrong. Check: `grep 'hpc_sdk' specs/rodinia-bfs-cuda.json` — if old path appears, re-do §4c. |
| "Working directory does not exist" | `config/paths.json` missing or wrong. Check: `cat config/paths.json`. Re-do §2 step 5. |
| Rodinia specs: "source file not found" | The `rodinia/rodinia-src -> .` symlink is missing. Re-do §2 step 3. |
| Azure API 400 | Deployment name mismatch. Must be **exactly** `gpt-5.4`. Check: `curl $AZURE_OPENAI_ENDPOINT/openai/deployments?api-version=2024-02-01 -H "api-key: $AZURE_OPENAI_API_KEY"` |
| "Unsupported value for temperature" (Azure) | Normal for Azure reasoning models. The pipeline already omits `temperature` / `top_p` when calling `azure-gpt-5.4`. If you see this, you're on stale code. |
| `--resume` skips tasks you want re-run | Keyed on file existence, not parameters. Check: `jq '.temperature' results/evaluation/azure-gpt-5.4/<file>.json`. Delete the specific JSONs you want re-run, then invoke again. |
| Hook blocks `rm` in `results/` | Pre-commit protection for CUDA↔OMP results. Be precise: delete one specific file, don't wildcard. Ask Samyak if unsure. |
| Schema validation shows ~15 errors | Expected. 5 deleted phantom Rodinia specs still referenced in append-only `manifest.jsonl`. Not a problem. |
| Pre-commit hook blocks commits | Don't commit the path adaptations from §4 — they're local-only. |
| Spec build uses wrong nvcc | Check `which nvcc` points at your expected install. The bulk-rewrite in §4c only replaces the reference machine's `/opt/nvidia/hpc_sdk/...` prefix — if your nvcc is elsewhere, that's fine as long as `NEW_CUDA` in §4c points at its parent. |
| Runs fail on `omp_target` specs only | The `nvc++` path rewrite in §4c only affects explicit path strings. If your `nvc++` is in `$PATH` but at a different location, add a symlink or adjust the spec build commands. |

---

## 14. KNOWN_FAIL Specs (excluded automatically)

These 8 specs are in `harness/constants.py:EXCLUDED_SPECS` and are skipped by the batch runner. No action needed.

| Spec | Reason |
|---|---|
| `rodinia-kmeans-cuda` | `texture<>` removed in CUDA 12 |
| `rodinia-mummergpu-cuda` | `texture<>` removed in CUDA 12 |
| `rodinia-mummergpu-omp` | `texture<>` + `cuMemGetInfo_v2` signature |
| `rodinia-hybridsort-cuda` | `GL/glew.h` not found (needs libglew-dev + display server) |
| `rodinia-nn-opencl` | TIMEOUT / SIGSEGV |
| `rodinia-kmeans-opencl` | SIGSEGV in OpenCL runtime |
| `hecbench-stencil1d-omp_target` | BUILD_FAIL |
| `hecbench-scan-omp_target` | VERIFY_FAIL on CPU target |

---

## Key File Reference

| File | Purpose |
|---|---|
| `config/paths.json.template` | Template — rendered to `config/paths.json` in §2 |
| `config/paths.json` | Machine paths (project_root, downloads_root, hecbench_root) |
| `docs/rodinia_toolchain_patches.diff` | Rodinia Makefile patches (§4d) |
| `requirements-lock.txt` | Pinned Python deps |
| `scripts/evaluation/run_eval_batch.py` | Batch orchestrator (canonical §9, ablation §11) |
| `scripts/evaluation/llm_evaluate.py` | Single-task evaluator. `MODEL_REGISTRY` entry for `azure-gpt-5.4` at line 110 |
| `scripts/evaluation/derive_l0_passers.py` | Builds ablation task-lists (§10) |
| `scripts/evaluation/analyze_eval.py` | Post-eval aggregation (§12) |
| `scripts/generate_viz_data.py` | Dashboard data refresh (§12) |
| `scripts/spec_tools/run_verify_sweep.py` | 88-spec setup sanity check (§5e) |
| `scripts/validate_schema.py` | JSON schema validator (§5a) |
| `harness/builder.py` | Compile logic |
| `harness/constants.py` | `EXCLUDED_SPECS` (§14) |
| `manifest.jsonl` | Kernel registry (append-only; batch runner enumerates pairs from it) |
| `schema/spec_schema.json` | Spec JSON Schema |
| `.gitmodules` | Rodinia submodule at `https://github.com/yuhc/gpu-rodinia` pinned to `9c10d3ea` |

---

## Success criteria

- §5e sweep returns `PASS 88/88`.
- §9 produces `results/evaluation/azure-gpt-5.4/*.json` for every canonical (pair, sample) combo in your 30-command matrix.
- §10 produces 6 task-list JSONs with non-empty passer sets.
- §11 produces ablation results at L0–L4 for every L0-passer pair.
- §12 `analyze_eval.py --show-gaps` reports no missing (model, direction, level) cells.

When all five are true, hand back the aggregated result tree and `results/evaluation/eval_summary.{json,md}`.

Good luck. Any questions, ping Samyak.
