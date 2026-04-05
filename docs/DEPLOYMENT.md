<!-- generated-by: gsd-doc-writer -->
# Deployment

ParBench is a research benchmark framework, not a hosted service. "Deployment" means setting up the framework on a machine with GPU compilers so that evaluation campaigns can run, and publishing visualization dashboards to GitHub Pages. There are three deployment targets: a local GPU workstation (primary), a Docker container (CPU-only validation), and the ALCF Polaris HPC cluster (large-scale campaigns).

## Deployment Targets

| Target | Config File | Purpose |
|--------|------------|---------|
| Local GPU workstation | `config/paths.json` | Full pipeline: build, run, verify kernels and run LLM evaluations |
| Docker container | `Dockerfile` | CPU-only validation: schema checks, unit tests, analysis scripts, figure generation |
| ALCF Polaris cluster | `run_eval_campaign.pbs` | Large-scale evaluation campaigns via PBS job scheduler |
| GitHub Pages | `.github/workflows/deploy-pages.yml` | Password-protected visualization dashboards |

### Local GPU Workstation

The primary deployment target. Requires NVIDIA GPU, CUDA toolkit, OpenCL headers/libraries, and a C++ compiler with OpenMP support. The reference platform uses:

- NVIDIA GeForce RTX 4070 (compute capability sm_89)
- CUDA 12.3 via NVIDIA HPC SDK 24.3 (`/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/`)
- gcc/g++ 12.4.0 with `-fopenmp`
- nvc++ 24.3 (for `omp_target` specs only)
- Intel oneAPI DPC++ 2025.3.2 (CPU-only SYCL, optional)
- Python 3.12 with virtual environment

Setup steps:

1. Clone the repository and create the virtual environment:

   ```bash
   git clone <repository-url>
   cd parbench_sam
   python3 -m venv env_parbench
   source env_parbench/bin/activate
   python3 -m pip install -r requirements-lock.txt
   pip install -e .
   ```

2. Configure paths by copying the template and setting the project root:

   ```bash
   cp config/paths.json.template config/paths.json
   # Edit config/paths.json — replace {{PROJECT_ROOT}} with the absolute path
   # to your parbench_sam directory
   ```

3. Initialize benchmark source submodules:

   ```bash
   git submodule update --init --recursive
   ```

4. Verify the installation:

   ```bash
   python3 scripts/validate_schema.py --all
   python3 -m harness verify specs/rodinia-bfs-cuda.json
   ```

### Docker Container (CPU-Only Validation)

The `Dockerfile` builds a lightweight image based on `python:3.12-slim` for running validation, tests, and analysis without GPU hardware. It does not support CUDA builds or OpenCL kernel execution.

**Build:**

```bash
docker build -t parbench .
```

**Run validation:**

```bash
docker run --rm parbench
# Default CMD runs: python3 scripts/validate_schema.py --all
```

**Run unit tests:**

```bash
docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v
```

**Run interactively:**

```bash
docker run --rm -it parbench bash
```

The Dockerfile automatically generates `config/paths.json` with all paths set to `/app` (the container working directory). It installs exact pinned dependencies from `requirements-lock.txt` (generated 2026-03-27 on Ubuntu 24.04 / Python 3.12.3) and registers the `harness` and `c_augmentation` packages via `pip install -e .`.

**What works in the container:** Schema validation, augmentation unit tests (15 tests via pytest), analysis scripts, figure generation (matplotlib), spec inspection (`python3 -m harness info`, `python3 -m harness prompt`).

**What does NOT work in the container:** Kernel compilation (`python3 -m harness build`), kernel execution (`python3 -m harness run`), full verification (`python3 -m harness verify`), LLM evaluation runs (no API keys configured by default).

### ALCF Polaris Cluster

The `run_eval_campaign.pbs` file is a PBS job script for running large-scale evaluation campaigns on the Argonne Leadership Computing Facility (ALCF) Polaris cluster.

**PBS directives:**

| Directive | Value |
|-----------|-------|
| Account | `argonne_tpc` |
| Queue | `debug` |
| Nodes | 1 (`select=1`) |
| Walltime | 10 hours |
| Filesystems | `home:eagle` |

<!-- VERIFY: ALCF Polaris cluster access requires an active ALCF allocation and account -->

**Proxy configuration:** The ALCF network requires an HTTP proxy for external API calls. The PBS script sets:

```bash
export HTTP_PROXY="http://proxy.alcf.anl.gov:3128"
export HTTPS_PROXY="http://proxy.alcf.anl.gov:3128"
```

**Repository path on Polaris:** `/lus/eagle/projects/argonne_tpc/chen/repo/pb2/`

<!-- VERIFY: Polaris repository path and ALCF project allocation name may change -->

The PBS script runs two campaign types sequentially:
1. **Primary campaign** (790 tasks): 158 pairs x 5 augmentation levels (L0-L4), temperature 0.0, max 3 retries
2. **Pass@k sweep** (474 tasks): 158 pairs x L0 only, temperature 0.7, 3 independent samples

### GitHub Pages (Visualization Dashboards)

Interactive HTML dashboards are deployed to GitHub Pages at:

**https://samyakjhaveri.github.io/parbench_sam/**

Dashboards are password-protected using staticrypt (AES-256 browser-side encryption). The password is stored as the `PAGES_PASSWORD` GitHub Actions secret.

**Deployment trigger:** The `.github/workflows/deploy-pages.yml` workflow runs on:
- Push to `main` branch when files in `visualizations/` change
- Manual trigger via `workflow_dispatch` (Actions tab)

**Deployed content:** The entire `visualizations/` directory, including HTML dashboards, CSS, JavaScript data files, and static assets.

## Build Pipeline

### GitHub Actions: Visualization Deployment

The only CI/CD pipeline is the GitHub Pages deployment workflow (`.github/workflows/deploy-pages.yml`).

**Trigger:** Push to `main` touching `visualizations/**`, or manual `workflow_dispatch`.

**Steps:**

1. Check out the repository (`actions/checkout@v4`)
2. Install staticrypt globally via npm
3. Encrypt all HTML files in `visualizations/` with the `PAGES_PASSWORD` secret (AES-256)
4. Configure GitHub Pages (`actions/configure-pages@v5`)
5. Upload the `visualizations/` directory as a Pages artifact (`actions/upload-pages-artifact@v4`)
6. Deploy to GitHub Pages (`actions/deploy-pages@v4`)

**Concurrency:** The workflow uses `group: pages` with `cancel-in-progress: false` to prevent concurrent deployments.

**Required secret:** `PAGES_PASSWORD` must be set in the repository's Actions secrets before the workflow can succeed. See `.github/PAGES_SETUP.md` for setup instructions.

### Local Evaluation Campaigns

Evaluation campaigns are not deployed via CI/CD. They are launched manually on the GPU workstation using tmux-based shell scripts or via PBS on Polaris.

**Local campaign runner** (`scripts/batch/run_eval_campaign.sh`):

```bash
# Launch a primary campaign (auto-creates tmux session)
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b

# Launch a pass@k sweep
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b pass@k

# Attach to running session
bash scripts/batch/run_eval_campaign.sh together-qwen-3.5-397b-a17b --attach
```

The campaign script:
1. Validates the API key for the chosen model provider
2. Launches itself inside a detached tmux session (SSH-disconnect safe)
3. Runs 28 batches across 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench) and multiple translation directions
4. Retries any failed batches in a second pass
5. Runs `analyze_eval.py` to regenerate summary data
6. Writes a completion marker to `results/evaluation/{model}_campaign_done.marker`
7. Logs all output to `results/evaluation/{model}_campaign.log`

**Results location:** `results/evaluation/{model-name}/` -- per-task JSON files, immutable once written. The `--resume` flag (enabled by default) skips existing results on re-runs.

## Environment Setup

### Required Environment Variables

LLM API keys must be set in the shell environment before running evaluation campaigns. See [CONFIGURATION.md](CONFIGURATION.md) for the full list.

| Variable | Required For | How to Set |
|----------|-------------|------------|
| `ANTHROPIC_API_KEY` | `claude-*` models | `export ANTHROPIC_API_KEY='sk-...'` |
| `OPENAI_API_KEY` | `gpt-*`, `o3-*`, `o4-*` models | `export OPENAI_API_KEY='sk-...'` |
| `AZURE_OPENAI_API_KEY` | `azure-*` models | `export AZURE_OPENAI_API_KEY='...'` |
| `AZURE_OPENAI_ENDPOINT` | `azure-*` models | `export AZURE_OPENAI_ENDPOINT='https://...'` |
| `GROQ_API_KEY` | `groq-*` models | `export GROQ_API_KEY='...'` |
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `gemini-*` models | `export GEMINI_API_KEY='...'` |
| `TOGETHER_API_KEY` | `together-*` models | `export TOGETHER_API_KEY='...'` |

Only the key for the specific model provider being used is required. The campaign runner validates the correct key is set before launching.

<!-- VERIFY: API key values and provider dashboard URLs are environment-specific -->

### Required Configuration Files

- **`config/paths.json`** -- Must exist with correct absolute paths for the current machine. See the `config/paths.json.template` for the format.

### Compiler Toolchain

For full pipeline functionality (build/run/verify), the following compilers must be available:

| Compiler | Required For | Reference Version |
|----------|-------------|------------------|
| nvcc (CUDA) | CUDA spec builds | 12.3 (NVIDIA HPC SDK 24.3) |
| g++ with `-fopenmp` | OpenMP spec builds | 12.4.0 |
| OpenCL headers + runtime | OpenCL spec builds | From NVIDIA HPC SDK 24.3 |

Compiler paths are hardcoded in individual spec files (e.g., `CUDA_DIR`, `OPENCL_INC`, `OPENCL_LIB` build variables). On a non-reference system, these spec-level paths may need updating. See [CONFIGURATION.md](CONFIGURATION.md) for details on spec build variables.

## Rollback Procedure

### GitHub Pages

To roll back a bad visualization deployment:

1. Go to the repository's Actions tab on GitHub
2. Find a previous successful run of "Deploy Visualizations to GitHub Pages"
3. Click "Re-run all jobs" to redeploy that version

Alternatively, revert the offending commit in `visualizations/` and push to `main` -- the workflow will auto-deploy the reverted state.

### Evaluation Results

Evaluation results are immutable -- they are never overwritten. If a campaign produces incorrect results (e.g., due to a harness bug), the standard procedure is:

1. Fix the underlying issue in the harness or evaluation code
2. Run a new campaign to a different output directory, or use `--resume` which will skip existing results and only fill in missing ones
3. Use `reverify_pass_results.py` to re-verify existing PASS results against corrected verification strategies without re-running LLM calls

There is no "rollback" for results because they are append-only. Incorrect results are documented and excluded from analysis rather than deleted.

### Docker Image

To roll back to a previous Docker image:

```bash
# Rebuild from a known-good commit
git checkout <known-good-commit>
docker build -t parbench .
```

## Monitoring

ParBench does not use external monitoring services (no Sentry, Datadog, New Relic, or OpenTelemetry). Monitoring is handled through:

### Campaign Progress Monitoring

- **tmux session:** Attach to the running tmux session to see live output:
  ```bash
  tmux attach -t <model_short>_campaign
  ```
- **Log files:** Campaign output is tee'd to `results/evaluation/{model}_campaign.log`
- **Done markers:** A `{model}_campaign_done.marker` file is written on completion with status, file count, and elapsed time
- **Result file count:** Monitor progress by counting result JSON files:
  ```bash
  ls results/evaluation/<model-name>/*.json | wc -l
  ```

### Visualization Dashboard Health

- **GitHub Actions:** Check the "Deploy Visualizations to GitHub Pages" workflow status in the repository's Actions tab
- **Manual verification:** Visit the deployed URL and verify dashboards load correctly

<!-- VERIFY: https://samyakjhaveri.github.io/parbench_sam/ is the current deployed URL -->

### Data Refresh for Dashboards

After an evaluation campaign completes, regenerate the dashboard data files:

```bash
python3 scripts/generate_viz_data.py
# Regenerates results_data.js and build_results_data.js
# Commit and push to main to trigger redeployment
```
