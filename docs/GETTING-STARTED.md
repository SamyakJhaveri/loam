<!-- generated-by: gsd-doc-writer -->
# Getting Started

This guide walks you through setting up ParBench from scratch and running your first build-run-verify pipeline on a kernel spec.

## Prerequisites

ParBench requires the following software to be installed before you begin.

### Required (all workflows)

- `Python >= 3.12` (tested with 3.12.3; declared in `pyproject.toml` `requires-python`)
- `Git` (for cloning and submodule initialization)

### Required (build-run-verify pipeline)

The harness compiles and runs HPC benchmark kernels. You need the compilers for the parallel APIs you intend to test:

| API | Compiler | Tested Version |
|-----|----------|---------------|
| CUDA | `nvcc` | 12.3, V12.3.103 (NVIDIA HPC SDK 24.3) |
| OpenMP | `g++` with `-fopenmp` | GCC 12.4.0 (Ubuntu) |
| OpenCL | `gcc`/`g++` with OpenCL headers and runtime libraries | GCC 12.4.0, OpenCL headers from NVIDIA HPC SDK 24.3 |
| OMP target offload | `nvc++` | 24.3 (NVIDIA HPC SDK) |
| SYCL | `icpx -fsycl` (Intel oneAPI DPC++) | 2025.3.2 (CPU-only, no GPU SYCL backend) |

- **NVIDIA GPU** -- tested with GeForce RTX 4070 (compute capability sm_89)
- CUDA toolkit or NVIDIA HPC SDK providing `nvcc`, OpenCL headers, and `libOpenCL.so`

### Required (LLM evaluation pipeline)

- API key(s) for at least one supported LLM provider, set as environment variables. See [CONFIGURATION.md](CONFIGURATION.md) for the full list of supported providers and their environment variable names.

### Optional

- `Docker` -- for CPU-only validation without GPU hardware (schema validation, unit tests, analysis)
- `libclang-dev` (system package) -- required by the `libclang` Python binding used in `c_augmentation/`

## Installation Steps

### 1. Clone the repository

```bash
git clone https://github.com/SamyakJhaveri/parbench_sam.git
cd parbench_sam
```

### 2. Initialize the Rodinia submodule

The Rodinia benchmark source is included as a git submodule (pinned to commit `9c10d3ea`). You must initialize it for the harness to locate kernel source files.

```bash
git submodule update --init --recursive
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv env_parbench
source env_parbench/bin/activate
```

### 4. Install Python dependencies

Choose one of the following options:

**Option A -- Exact pinned versions (recommended for reproducibility):**

```bash
python3 -m pip install -r requirements-lock.txt
python3 -m pip install -e .
```

**Option B -- Minimum compatible versions:**

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
```

**Option C -- Install specific feature groups via `pyproject.toml`:**

```bash
# Core only (harness, schema validation, augmentation)
python3 -m pip install -e .

# Add LLM evaluation pipeline
python3 -m pip install -e ".[eval]"

# Add analysis and figure generation
python3 -m pip install -e ".[analysis]"

# Add development tools (pytest, ruff)
python3 -m pip install -e ".[dev]"

# Everything
python3 -m pip install -e ".[all]"
```

### 5. Configure platform paths

Copy the paths template and replace the placeholder with your actual project root:

```bash
cp config/paths.json.template config/paths.json
```

Edit `config/paths.json` so that all three keys point to the absolute path of your project root:

```json
{
    "project_root": "/absolute/path/to/parbench_sam",
    "downloads_root": "/absolute/path/to/parbench_sam",
    "hecbench_root": "/absolute/path/to/parbench_sam"
}
```

On the reference Linux machine, all three paths are `/home/samyak/Desktop/parbench_sam`. If you skip this step, the harness falls back to resolving paths relative to the `--project-root` CLI argument.

## Benchmark Suites

ParBench includes 206 kernel spec files across five benchmark suites:

| Suite | Specs | APIs | Notes |
|-------|-------|------|-------|
| Rodinia | 60 | CUDA, OpenMP, OpenCL, OMP target | 54 TRUE PASS, 6 KNOWN_FAIL |
| XSBench | 4 | CUDA, OpenMP, OpenCL, OMP target | All 4 PASS |
| RSBench | 4 | CUDA, OpenMP, OpenCL, OMP target | All 4 PASS |
| mixbench | 3 | CUDA, OpenMP, OpenCL | All 3 PASS |
| HeCBench | 135 | CUDA, OpenMP, OMP target | 65 unique kernels |

Each spec file is a JSON contract in `specs/` that fully describes a kernel variant -- its identity, source files, build commands, run arguments, and verification strategy. The harness uses these specs to drive the build-run-verify pipeline.

## First Run

After installation, verify everything works by running three commands in sequence.

### 1. Validate schemas

```bash
python3 scripts/validate_schema.py --all
```

This checks all spec files and manifest entries against their JSON Schemas. Expect approximately 15 errors from phantom Rodinia specs that were deleted but remain in the append-only manifest -- this is normal.

### 2. Run unit tests

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

All 15 tests should pass. These validate the AST-based augmentation transforms used to create diverse LLM inputs.

### 3. Run the build-run-verify pipeline on a single kernel

```bash
python3 -m harness verify specs/rodinia-bfs-cuda.json
```

This compiles the BFS CUDA kernel from the Rodinia benchmark, runs it with correctness-checking arguments, and verifies the output. You should see `PASS` for build, run, and verify stages.

For verbose output, place the `-v` flag **before** the subcommand:

```bash
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
```

### Harness subcommands

The harness supports several subcommands beyond `verify`:

| Subcommand | Description |
|------------|-------------|
| `build` | Compile a kernel only (no run or verify) |
| `run` | Run a previously built kernel (no build or verify) |
| `verify` | Full pipeline: build, run, and verify output |
| `prompt` | Print the LLM prompt that would be sent for translation |
| `info` | Display spec metadata summary |
| `pairs` | List all available translation pairs from the manifest |

Global flags (`-v`, `--json`, `--project-root`, `--manifest`) must appear **before** the subcommand.

## Running an LLM Evaluation

Once the harness is verified, you can run LLM-based kernel translation evaluations. This requires API keys for at least one supported provider (see [CONFIGURATION.md](CONFIGURATION.md)).

### Single translation (dry run)

Preview the prompt without calling the LLM:

```bash
python3 scripts/evaluation/llm_evaluate.py \
  --source specs/rodinia-bfs-cuda.json \
  --target specs/rodinia-bfs-omp.json \
  --model azure-gpt-4.1 \
  --project-root /path/to/parbench_sam \
  --dry-run
```

### Batch evaluation

Run a batch of kernel translations across a suite:

```bash
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --direction cuda-to-omp \
  --models azure-gpt-4.1 \
  --project-root /path/to/parbench_sam \
  --resume -v
```

The `--suite` flag is **required** to avoid cross-suite kernel name collisions (e.g., `nw` exists in both Rodinia and HeCBench). The `--resume` flag skips translations whose result files already exist. Results are written as per-task JSON files to `results/evaluation/{model_name}/`.

## Common Setup Issues

### Missing `libclang` or `libclang-dev`

**Symptom:** `ImportError` or `OSError` when importing `clang.cindex` during augmentation.

**Solution:** Install the system package for your platform:

```bash
# Ubuntu/Debian
sudo apt-get install libclang-dev

# macOS (Homebrew)
brew install llvm
```

The `libclang` Python package (listed in `requirements.txt`) provides the bindings, but it requires the native `libclang` shared library to be installed on your system.

### Wrong Python version

**Symptom:** `SyntaxError` or import failures on startup.

**Solution:** ParBench requires Python >= 3.12. Check your version:

```bash
python3 --version
```

If you have multiple Python versions, create the virtual environment with the correct one explicitly:

```bash
python3.12 -m venv env_parbench
```

### CUDA/OpenCL libraries not found at runtime

**Symptom:** `error while loading shared libraries: libcudart.so.12` or similar when running CUDA/OpenCL specs.

**Solution:** Ensure the CUDA runtime library path is in your `LD_LIBRARY_PATH`. On the reference platform:

```bash
export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64:$LD_LIBRARY_PATH
```

Several CUDA specs set this via their `run.environment_variables` field, but some may require it in your shell environment.

### `config/paths.json` missing or incorrect

**Symptom:** `FileNotFoundError` or spec path resolution failures when running the harness.

**Solution:** Copy the template and fill in the correct absolute path to your project root:

```bash
cp config/paths.json.template config/paths.json
# Edit config/paths.json — replace {{PROJECT_ROOT}} with your actual path
```

### Rodinia submodule not initialized

**Symptom:** Empty `rodinia/` directory, specs cannot find source files.

**Solution:** Initialize the submodule:

```bash
git submodule update --init --recursive
```

Note: Git worktrees do **not** initialize submodules automatically. If you are working in a worktree, the Rodinia sources will not be available. Only run evaluations from the main checkout.

### HeCBench source not cloned

**Symptom:** HeCBench specs fail with `FileNotFoundError` when the harness tries to locate source files.

**Solution:** HeCBench is not a git submodule -- it must be cloned separately into the project root:

```bash
cd /path/to/parbench_sam
git clone https://github.com/zjin-lcf/HeCBench.git HeCBench-master
```

The `HeCBench-master/` directory is gitignored but required on disk for any HeCBench spec to build and run.

## Alternative: Docker (CPU-Only)

If you do not have GPU hardware, you can run schema validation, unit tests, and analysis scripts inside a Docker container:

```bash
# Build the image
docker build -t parbench .

# Run schema validation (default command)
docker run --rm parbench

# Run unit tests
docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v
```

The Docker image uses `python:3.12-slim`, installs the pinned dependencies from `requirements-lock.txt`, and auto-generates `config/paths.json` with `/app` paths. GPU-dependent operations (CUDA builds, OpenCL kernel execution) are not available in the container.

## Next Steps

- **[ARCHITECTURE.md](ARCHITECTURE.md)** -- Understand the system components, data flow, and key abstractions.
- **[CONFIGURATION.md](CONFIGURATION.md)** -- Full reference for environment variables, config files, and per-environment overrides.
- **[DEVELOPMENT.md](DEVELOPMENT.md)** -- Local development setup, build commands, code style, and contribution workflow.
- **[TESTING.md](TESTING.md)** -- Test frameworks, running tests, coverage, and CI integration.
- **[GUIDE.md](../GUIDE.md)** -- Complete pipeline walkthrough, all commands, and instructions for adding new benchmarks.
- **[REPRODUCING.md](REPRODUCING.md)** -- Instructions for reproducing the SC26 paper results.
