# Artifact Evaluation: ParBench

ParBench is a build-run-verify benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. This document provides setup instructions and a smoke test for SC26 artifact evaluation.

## Prerequisites

- Linux with NVIDIA GPU (tested on Ubuntu 24.04 LTS, NVIDIA RTX 4070 12GB)
- Python 3.12+
- NVIDIA HPC SDK 24.3 or CUDA Toolkit 12.x
- GCC 12.4+

## Quick Start

### 1. Clone and Initialize

```bash
git clone https://github.com/SamyakJhaveri/parbench_sam.git
cd parbench_sam
git submodule update --init --recursive
```

The Rodinia submodule (commit 9c10d3ea) will be checked out automatically.

### 2. Install Dependencies

```bash
python3 -m venv env_parbench
source env_parbench/bin/activate
pip install -r requirements-lock.txt
```

### 3. Configure Paths

Edit `config/paths.json` if your project root differs from the default. The default configuration assumes the project is at `/home/samyak/Desktop/parbench_sam`.

### 4. Smoke Test

```bash
python3 -m harness verify specs/rodinia-bfs-cuda.json
```

Expected output: BUILD: PASS, RUN: PASS, VERIFY: PASS

## Running LLM Evaluation

### Environment Variables

| Variable | Required | Provider | Purpose |
|----------|----------|----------|---------|
| TOGETHER_API_KEY | Yes | [Together AI](https://api.together.ai) | Qwen 3.5 397B inference for reproducing paper results |

### Example Command

```bash
export TOGETHER_API_KEY="your-key-here"
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia \
  --model together-qwen-3.5-397b-a17b \
  --project-root .
```
