# Guide: Re-running GPT-4.1-mini Evaluations (Non-Rodinia Benchmarks)

> **Audience:** Le Chen  
> **Date:** 2026-04-07  
> **Purpose:** Set up benchmark source files and re-run the GPT-4.1-mini evaluation campaign for non-Rodinia suites (HeCBench, XSBench, RSBench, mixbench) that had empty-prompt failures in the original Argonne/Polaris run.

---

## Background: What Went Wrong

The original GPT-4.1-mini eval campaign ran on Polaris at `/lus/eagle/projects/argonne_tpc/chen/repo/parbench_sam/`. The **Rodinia** results (693 files) are all valid. However, **108 of 204 non-Rodinia results are invalid** — the eval script couldn't find the benchmark source files on that machine, so the LLM received `<FILE NOT FOUND: /lus/eagle/projects/argonne_tpc/chen/repo/parbench_sam/HeCBench-master/...>` instead of actual source code and responded with "No source code provided for translation."

These invalid results are all marked `BUILD_FAIL` in the result JSONs.

### Invalid Result Breakdown (by suite and direction)

| Suite | Direction | Valid | Invalid |
|-------|-----------|-------|---------|
| **hecbench** | cuda-to-omp | 30 | 10 |
| **hecbench** | cuda-to-omp_target | 30 | 34 |
| **hecbench** | omp-to-cuda | 2 | 2 |
| **mixbench** | cuda-to-omp | 2 | 6 |
| **mixbench** | cuda-to-opencl | 0 | 8 |
| **mixbench** | omp-to-opencl | 1 | 7 |
| **mixbench** | opencl-to-omp | 1 | 7 |
| **rsbench** | cuda-to-omp | 1 | 7 |
| **rsbench** | cuda-to-opencl | 5 | 3 |
| **rsbench** | omp-to-opencl | 7 | 1 |
| **rsbench** | opencl-to-omp | 2 | 6 |
| **xsbench** | cuda-to-omp | 3 | 5 |
| **xsbench** | cuda-to-opencl | 2 | 6 |
| **xsbench** | omp-to-opencl | 5 | 3 |
| **xsbench** | opencl-to-omp | 2 | 6 |
| **Total** | | **96** | **108** |

---

## Step 1: Get the Benchmark Source Files

The eval pipeline reads source files **at runtime** from directories located relative to the project root. There is no pre-cached or pre-processed version. The path is resolved as:

```
config/paths.json → downloads_root / spec.provenance.repo_root / spec.provenance.source_path
```

You need **5 directories** at the project root. The Rodinia results are already valid, so Rodinia setup is only needed if you want to re-run those too (you probably don't).

### Required Directory Layout

```
parbench_sam/
├── specs/                        # Already in repo
├── harness/                      # Already in repo
├── scripts/                      # Already in repo
├── results/evaluation/           # Already has 897 GPT-4.1-mini results
├── config/paths.json             # Must update (Step 2)
│
├── rodinia/rodinia-src/          # 1.2 GB — git submodule (ALREADY WORKED — skip unless needed)
├── HeCBench-master/              # 1.4 GB — git clone or ZIP download
├── xsbench/xsbench-src/          # 11 MB  — git clone
├── rsbench/rsbench-src/          # 2.8 MB — git clone
└── mixbench/mixbench-src/        # 7.4 MB — git clone
```

### 1a. XSBench — clone, checkout exact commit, NO modifications needed

```bash
cd /path/to/parbench_sam
mkdir -p xsbench
git clone https://github.com/ANL-CESAR/XSBench.git xsbench/xsbench-src
cd xsbench/xsbench-src
git checkout ba08e5221af6106252b866e50ea123c69d31a4e2
cd ../..
```

### 1b. RSBench — clone, checkout exact commit, NO modifications needed

```bash
mkdir -p rsbench
git clone https://github.com/ANL-CESAR/RSBench.git rsbench/rsbench-src
cd rsbench/rsbench-src
git checkout 34b644787ea9af4fb188e1253da72e09bbed9989
cd ../..
```

### 1c. mixbench — clone, checkout exact commit, NO modifications needed

```bash
mkdir -p mixbench
git clone https://github.com/ekondis/mixbench.git mixbench/mixbench-src
cd mixbench/mixbench-src
git checkout 32edeca98bdd63b32769e3c7460676b9fd567f06
cd ../..
```

### 1d. HeCBench — clone + delete 2 files

HeCBench was originally downloaded as a ZIP archive (hence the `HeCBench-master/` directory name). You can either download the ZIP or clone the repo — just make sure the top-level directory is named `HeCBench-master`.

**Option A: Clone and rename**
```bash
git clone https://github.com/zjin-lcf/HeCBench.git HeCBench-master
```

**Option B: Download ZIP from GitHub**
Download from `https://github.com/zjin-lcf/HeCBench/archive/refs/heads/master.zip`, which extracts to `HeCBench-master/`.

**Then delete 2 CMakeLists.txt files** (they interfere with the Makefile-based build the specs use):
```bash
cd HeCBench-master
rm -f src/iso2dfd-cuda/CMakeLists.txt src/iso2dfd-omp/CMakeLists.txt
cd ..
```

> **Note:** HeCBench is not pinned to a specific commit in the specs (they say `"commit": "archive-download"`). A fresh clone should work fine — the kernels used in the eval (10 curated kernels) have stable APIs.

### 1e. Rodinia — ONLY if you need to re-run Rodinia evals (you probably don't)

The 693 Rodinia results are all valid. If you do need Rodinia:

```bash
git submodule update --init rodinia
```

Then apply the toolchain patch for your CUDA installation. The patch at `docs/rodinia_toolchain_patches.diff` is machine-specific (hardcodes CUDA paths for Samyak's NVIDIA HPC SDK 24.3). You'll need to edit `rodinia/rodinia-src/common/make.config` to point `CUDA_DIR`, `CUDA_LIB_DIR`, and `NV_OPENCL_DIR` to your CUDA installation.

---

## Step 2: Update `config/paths.json`

Edit `config/paths.json` to point to YOUR project root:

```json
{
    "project_root": "/path/to/your/parbench_sam",
    "downloads_root": "/path/to/your/parbench_sam",
    "hecbench_root": "/path/to/your/parbench_sam"
}
```

The `downloads_root` is the key one — it's the base path that gets combined with each spec's `repo_root` to find the source files.

---

## Step 3: Verify Benchmark Sources Are Accessible

Run this quick check to confirm the eval script can find all source files:

```bash
cd /path/to/parbench_sam
source env_parbench/bin/activate   # or create a new venv with: pip install -r requirements.txt

python3 -c "
import json, glob
from pathlib import Path
from harness.spec_loader import load_spec, resolve_paths

project_root = Path('.')  # run from parbench_sam/
missing = []
ok = 0
for spec_file in sorted(glob.glob('specs/*.json')):
    spec = load_spec(spec_file)
    suite = spec['identity']['source_suite']
    if suite == 'rodinia':
        continue  # skip Rodinia — already valid
    resolved = resolve_paths(spec, project_root)
    source_dir = resolved['_resolved']['source_dir']
    if not source_dir.is_dir():
        missing.append((spec['identity']['unique_id'], str(source_dir)))
    else:
        ok += 1

print(f'OK: {ok} specs have accessible source directories')
if missing:
    print(f'MISSING: {len(missing)} specs cannot find their source:')
    for uid, path in missing[:10]:
        print(f'  {uid} -> {path}')
else:
    print('All non-Rodinia source directories found!')
"
```

If anything is missing, the output will show exactly which spec and path failed.

---

## Step 4: Install Python Dependencies

```bash
python3 -m venv env_parbench   # or use existing venv
source env_parbench/bin/activate
pip install -r requirements.txt
```

Key packages needed for the eval pipeline:
- `openai>=1.50.0` — Azure OpenAI SDK (used for `azure-gpt-4.1-mini`)
- `pydantic>=2.0` — schema validation
- `jsonschema>=4.20` — spec validation
- `libclang>=18.1` — only needed for augmentation levels L1-L4

---

## Step 5: Set Up Azure API Credentials

The GPT-4.1-mini evals use Azure OpenAI. Set these environment variables:

```bash
export AZURE_OPENAI_API_KEY="<your-azure-api-key>"
export AZURE_OPENAI_ENDPOINT="https://galor-m8yvytc2-swedencentral.cognitiveservices.azure.com/"
```

The model ID in the eval is `azure-gpt-4.1-mini`. The script strips the `azure-` prefix to get the deployment name `gpt-4.1-mini`.

---

## Step 6: Delete Invalid Result Files

**Critical:** The 108 invalid results have `overall_status: "BUILD_FAIL"`. The `--resume` flag (enabled by default) treats `BUILD_FAIL` as a deterministic outcome and **will skip these files**. You must delete them first so the pipeline regenerates them.

### 6a. Dry run — inspect what would be deleted

```bash
python3 -c "
import json, os

d = 'results/evaluation/azure-gpt-4.1-mini'
to_delete = []
for f in sorted(os.listdir(d)):
    if not f.endswith('.json') or f.startswith('rodinia'):
        continue
    path = os.path.join(d, f)
    r = json.loads(open(path).read())
    tf = r.get('translated_files', {})
    all_content = ' '.join(tf.values()).lower()
    code_len = sum(len(v) for v in tf.values())
    # Invalid results have short stub responses with 'no source' / 'not provided' / 'file not found'
    is_invalid = (
        code_len < 300
        and ('not provided' in all_content
             or 'no source' in all_content
             or 'file not found' in all_content)
    )
    if is_invalid:
        to_delete.append(f)

print(f'Would delete {len(to_delete)} invalid result files:')
for f in to_delete[:10]:
    print(f'  {f}')
if len(to_delete) > 10:
    print(f'  ... and {len(to_delete) - 10} more')
"
```

### 6b. Actually delete them

```bash
python3 -c "
import json, os

d = 'results/evaluation/azure-gpt-4.1-mini'
deleted = 0
for f in sorted(os.listdir(d)):
    if not f.endswith('.json') or f.startswith('rodinia'):
        continue
    path = os.path.join(d, f)
    r = json.loads(open(path).read())
    tf = r.get('translated_files', {})
    all_content = ' '.join(tf.values()).lower()
    code_len = sum(len(v) for v in tf.values())
    is_invalid = (
        code_len < 300
        and ('not provided' in all_content
             or 'no source' in all_content
             or 'file not found' in all_content)
    )
    if is_invalid:
        os.remove(path)
        deleted += 1

print(f'Deleted {deleted} invalid result files')
"
```

---

## Step 7: Re-run the Eval Campaign

You can either use the canonical campaign script or run individual batches.

### Option A: Use the campaign script (recommended — handles all suites/directions)

```bash
bash scripts/batch/run_eval_campaign.sh azure-gpt-4.1-mini
```

This launches in a **tmux session** so you can disconnect SSH safely. It runs all 28 batches (all 5 suites, all directions) with `--resume`, so it will:
- **Skip** all existing valid results (Rodinia + valid non-Rodinia)
- **Regenerate** only the deleted invalid results
- Use augmentation levels L0-L4, temperature 0.0, max-retries 3

To attach to the running session:
```bash
bash scripts/batch/run_eval_campaign.sh azure-gpt-4.1-mini --attach
# or directly:
tmux attach -t azure-gpt-4_1-mini_campaign
```

### Option B: Run individual batches (if you want more control)

The non-Rodinia batches from the campaign script are:

```bash
source env_parbench/bin/activate
PROJECT_ROOT="/path/to/parbench_sam"

# ── XSBench: 6 directions ──
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction cuda-to-omp     --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction omp-to-cuda     --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction cuda-to-opencl  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction opencl-to-cuda  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction omp-to-opencl   --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite xsbench --direction opencl-to-omp   --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"

# ── RSBench: 6 directions ──
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction cuda-to-omp     --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction omp-to-cuda     --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction cuda-to-opencl  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction opencl-to-cuda  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction omp-to-opencl   --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite rsbench --direction opencl-to-omp   --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"

# ── mixbench: 6 directions ──
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction cuda-to-omp    --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction omp-to-cuda    --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction cuda-to-opencl --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction opencl-to-cuda --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction omp-to-opencl  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite mixbench --direction opencl-to-omp  --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"

# ── HeCBench: 4 directions (curated kernel lists) ──
# cuda <-> omp (CPU): 5 kernels
python3 scripts/evaluation/run_eval_batch.py --suite hecbench --direction cuda-to-omp    --kernels stencil1d heat2d floydwarshall scan iso2dfd --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
python3 scripts/evaluation/run_eval_batch.py --suite hecbench --direction omp-to-cuda    --kernels stencil1d heat2d floydwarshall scan iso2dfd --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
# cuda -> omp_target (GPU): 8 kernels (excludes stencil1d + scan which are KNOWN_FAIL targets)
python3 scripts/evaluation/run_eval_batch.py --suite hecbench --direction cuda-to-omp_target --kernels heat2d floydwarshall page-rank jacobi nqueen md convolution1d iso2dfd --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
# omp_target -> cuda: all 10 kernels (KNOWN_FAIL specs are fine as sources)
python3 scripts/evaluation/run_eval_batch.py --suite hecbench --direction omp_target-to-cuda --kernels stencil1d heat2d floydwarshall page-rank scan jacobi nqueen md convolution1d iso2dfd --models azure-gpt-4.1-mini --augment-levels 0 1 2 3 4 --max-retries 3 --resume -v --project-root "$PROJECT_ROOT"
```

> **Important for HeCBench:** You MUST use `--kernels` to filter to the 10 curated kernels. Without it, the script would match all 65+ HeCBench kernels in the manifest, which is not what the campaign intended.

---

## Step 8: Verify the Re-run

After the eval completes, check that no invalid results remain:

```bash
python3 -c "
import json, os

d = 'results/evaluation/azure-gpt-4.1-mini'
invalid = 0
total = 0
for f in sorted(os.listdir(d)):
    if not f.endswith('.json'):
        continue
    total += 1
    r = json.loads(open(os.path.join(d, f)).read())
    tf = r.get('translated_files', {})
    all_content = ' '.join(tf.values()).lower()
    code_len = sum(len(v) for v in tf.values())
    if code_len < 300 and ('not provided' in all_content or 'no source' in all_content or 'file not found' in all_content):
        invalid += 1
        print(f'  STILL INVALID: {f}')

print(f'Total: {total} results, {invalid} still invalid')
"
```

Then regenerate the analysis summary:

```bash
python3 scripts/evaluation/analyze_eval.py \
  --project-root /path/to/parbench_sam \
  --output-dir results/evaluation
```

---

## Hardware/Software Prerequisites

The eval pipeline needs the following to build/run/verify translated code:

- **NVIDIA GPU** with CUDA toolkit (nvcc, CUDA libraries)
- **GCC >= 9.0** with OpenMP support (`-fopenmp`)
- **OpenCL headers and runtime** (typically from CUDA toolkit)
- **NVIDIA HPC SDK** (for `nvc` compiler, only needed for `omp_target` specs)
- **Python 3.10+** with venv

The build/run/verify step happens locally on your machine — the LLM produces translated code, and the pipeline compiles and runs it to check if it works.

---

## Quick Reference: What Each Directory Contains

| Directory | Repo URL | Commit | Size | Modifications |
|-----------|----------|--------|------|---------------|
| `xsbench/xsbench-src/` | `github.com/ANL-CESAR/XSBench` | `ba08e52` | 11 MB | None |
| `rsbench/rsbench-src/` | `github.com/ANL-CESAR/RSBench` | `34b6447` | 2.8 MB | None |
| `mixbench/mixbench-src/` | `github.com/ekondis/mixbench` | `32edeca` | 7.4 MB | None |
| `HeCBench-master/` | `github.com/zjin-lcf/HeCBench` | latest master (or ZIP) | 1.4 GB | Delete 2 CMakeLists.txt in iso2dfd |
| `rodinia/rodinia-src/` | `github.com/yuhc/gpu-rodinia` | `9c10d3e` | 1.2 GB | Toolchain patches (machine-specific CUDA paths) |

---

## Troubleshooting

**"Makefile.nvc: No such file or directory"** — This means an `omp_target` spec is trying to build with `nvc` (NVIDIA HPC SDK compiler). Make sure the NVIDIA HPC SDK is installed and `nvc` is on your PATH.

**Empty LLM responses / "No source code provided"** — The eval script can't find the source files. Check:
1. Is the directory present? (e.g., `ls HeCBench-master/src/convolution1D-cuda/`)
2. Is `config/paths.json` pointing to the right `downloads_root`?
3. Run the verification script from Step 3.

**`--resume` skipping results you want to re-run** — The `--resume` flag skips any existing result file with status other than `ERROR` or `EXTRACTION_FAIL`. If you want to force a re-run, delete the specific result file first, then run with `--resume`.

**Azure API errors** — Make sure `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are set. The endpoint should be `https://galor-m8yvytc2-swedencentral.cognitiveservices.azure.com/`.
