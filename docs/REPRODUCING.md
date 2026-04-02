# Reproducing ParBench Results

This document provides instructions for installing ParBench and reproducing the
results reported in the SC26 paper.

## Prerequisites

- **Python 3.12+** (tested with 3.12.3)
- **Git** (for cloning and submodule initialization)
- **GCC 12+** (for building Rodinia/XSBench benchmarks)

For full evaluation reproduction (GPU required):
- **NVIDIA GPU** (tested with GeForce RTX 4070)
- **CUDA 12.3+** (tested via NVIDIA HPC SDK 24.3)
- **LLM API keys** (see [LLM API Setup](#llm-api-setup))

## Quick Start (CPU-only validation)

This setup lets you run schema validation, unit tests, and analysis scripts
without a GPU.

```bash
# Clone the repository
git clone https://github.com/samyakjhaveri/parbench_sam.git
cd parbench_sam

# Initialize the Rodinia submodule (needed for source verification)
git submodule update --init --recursive

# Create and activate a virtual environment
python3 -m venv env_parbench
source env_parbench/bin/activate

# Install dependencies
# Option A: Exact pinned versions (recommended for reproduction)
pip install -r requirements-lock.txt
pip install -e .

# Option B: Minimum compatible versions
pip install -r requirements.txt
pip install -e .

# Verify installation
python3 scripts/validate_schema.py --all
# Expected: ~135 errors (HeCBench sources not included — this is normal)

# Run unit tests
python3 -m pytest c_augmentation/test_transforms.py -v
# Expected: 15 tests, all PASS
```

## Installation Options

ParBench uses optional dependency groups in `pyproject.toml`:

```bash
# Core only (harness, schema validation, augmentation)
pip install -e .

# With LLM evaluation support
pip install -e ".[eval]"

# With analysis and figure generation
pip install -e ".[analysis]"

# With development tools (pytest, ruff)
pip install -e ".[dev]"

# Everything
pip install -e ".[all]"
```

## Docker (CPU-only)

For a self-contained environment without manual dependency management:

```bash
docker build -t parbench .

# Run schema validation
docker run --rm parbench

# Run unit tests
docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v

# Interactive shell
docker run --rm -it parbench bash
```

## Full GPU Setup (for evaluation reproduction)

### 1. CUDA Toolchain

Install the NVIDIA HPC SDK or CUDA Toolkit. The paper results used:

```
NVIDIA HPC SDK 24.3
nvcc: V12.3 (Build cuda_12.3.r12.3/compiler.33492891_0)
```

Verify your installation:

```bash
nvcc --version
# Should show CUDA 12.x
```

### 2. Build Rodinia Benchmarks

```bash
# From project root
cd rodinia/rodinia-src

# Apply toolchain patches for your system
# (the repository includes patches for HPC SDK 24.3 paths)
make

# Verify a benchmark builds and runs
cd cuda/bfs
make
./bfs ../../data/bfs/graph4096.txt
```

### 3. Verify Harness Pipeline

```bash
# Activate your venv
source env_parbench/bin/activate

# Test the full build/run/verify pipeline on one spec
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
# Expected: PASS

# Test multiple specs
for spec in specs/rodinia-bfs-cuda.json specs/rodinia-hotspot-cuda.json specs/rodinia-srad-v2-cuda.json; do
    python3 -m harness -v verify "$spec"
done
```

### 4. LLM API Setup

The evaluation pipeline requires API keys for the LLM providers used in the paper.
Set these as environment variables:

```bash
# Anthropic (Claude Sonnet)
export ANTHROPIC_API_KEY="your-key-here"

# OpenAI (GPT-4.1)
export OPENAI_API_KEY="your-key-here"

# Groq (Llama 3.3 70B)
export GROQ_API_KEY="your-key-here"

# Google AI (Gemini 2.5 Flash-Lite)
export GEMINI_API_KEY="your-key-here"
```

### 5. Reproduce Evaluation Results

```bash
# Run a single evaluation (example: Claude Sonnet, CUDA-to-OMP)
python3 scripts/evaluation/run_eval_batch.py \
    --suite rodinia --direction cuda-to-omp \
    --models claude-sonnet-4-6 \
    --project-root $(pwd) \
    --resume -v

# Run all directions for one model
for direction in cuda-to-omp omp-to-cuda cuda-to-opencl opencl-to-cuda omp-to-opencl opencl-to-omp; do
    python3 scripts/evaluation/run_eval_batch.py \
        --suite rodinia --direction $direction \
        --models claude-sonnet-4-6 \
        --project-root $(pwd) \
        --resume -v
done
```

Results are written to `results/evaluation/<model>/<direction>/`.

### 6. Reproduce Augmentation Baselines

```bash
# Run augmentation at all levels for one spec
for level in 1 2 3 4; do
    python3 scripts/augmentation/augment_verify.py \
        specs/rodinia-bfs-cuda.json \
        --augment_level $level --seed 42 -v \
        --project-root $(pwd)
done

# Batch augmentation across all specs
python3 scripts/augmentation/run_augment_batch.py \
    --suite rodinia --project-root $(pwd) -v
```

### 7. Generate Paper Figures

```bash
# Generate all figures from evaluation results
python3 scripts/generate_paper_figures.py \
    --project-root . \
    --figure all \
    --output-dir docs/paper/figures

# Generate visualization data for the dashboard
python3 scripts/generate_viz_data.py
```

## Reproducing Paper Results — Summary

| What | Command | Expected |
|------|---------|----------|
| Schema validation | `python3 scripts/validate_schema.py --all` | ~135 HeCBench errors (expected) |
| Unit tests | `python3 -m pytest c_augmentation/test_transforms.py -v` | 15/15 PASS |
| Rodinia harness (54 specs) | `for f in specs/rodinia-*.json; do python3 -m harness -v verify "$f"; done` | 54 PASS, 6 KNOWN_FAIL |
| XSBench harness (4 specs) | `for f in specs/xsbench-*.json; do python3 -m harness -v verify "$f"; done` | 4 PASS |
| Augmentation baseline | `run_augment_batch.py --suite rodinia` | 54/60 PASS at L1-L4 |
| LLM eval (per model/direction) | `run_eval_batch.py --suite rodinia ...` | See paper Table 2 |

## Environment Used for Paper Results

| Component | Version |
|-----------|---------|
| OS | Ubuntu 24.04.4 LTS (kernel 6.8.0-40-generic) |
| GPU | NVIDIA GeForce RTX 4070 |
| CUDA | 12.3 (via NVIDIA HPC SDK 24.3) |
| GCC | 12.4.0 |
| Python | 3.12.3 |
| Package versions | See `requirements-lock.txt` |

### LLM Models

| Model | Provider | API |
|-------|----------|-----|
| Claude Sonnet 4 | Anthropic | `claude-sonnet-4-6` |
| GPT-4.1 | OpenAI (Azure) | `azure-gpt-4.1` |
| Llama 3.3 70B | Groq | `groq-llama-3.3-70b-versatile` |
| Gemini 2.5 Flash-Lite | Google AI | `gemini-2.5-flash-lite` |

## Troubleshooting

### `validate_schema.py` reports ~135 errors
This is expected. HeCBench benchmark sources are not bundled in the repository.
Only Rodinia and XSBench sources are included.

### Harness reports KNOWN_FAIL for 6 Rodinia specs
Six specs are known to fail due to CUDA 12 deprecations or missing system
libraries. See `CLAUDE.md` for the full list. These are excluded from evaluation.

### `libclang` import fails
Install the system `libclang-dev` package:
```bash
sudo apt-get install libclang-dev  # Ubuntu/Debian
brew install llvm                   # macOS
```
Then: `pip install libclang>=18.1`

### CUDA compiler not found
Ensure `nvcc` is on your PATH. For NVIDIA HPC SDK:
```bash
export PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin:$PATH
export LD_LIBRARY_PATH=/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64:$LD_LIBRARY_PATH
```
