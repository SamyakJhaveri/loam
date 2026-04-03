# Technology Stack

**Analysis Date:** 2026-04-03

## Languages

**Primary:**
- Python 3.12 — All pipeline code: harness, evaluation, augmentation, analysis, scripts
- C/C++ (C++14/17) — Benchmark kernel sources (CUDA, OpenMP, OpenCL implementations)
- CUDA C++ — GPU kernel sources in Rodinia, HeCBench, XSBench, RSBench, mixbench suites
- OpenCL C — Kernel files (`.cl`) used in OpenCL variants

**Secondary:**
- Bash — Batch runner scripts in `scripts/batch/`, PBS job script `run_eval_campaign.pbs`
- JavaScript — Visualization data blobs in `visualizations/eval_results_data.js`, `visualizations/results_data.js`
- HTML/CSS — Dashboard and result visualization pages in `visualizations/`
- JSON/JSONL — Spec files (`specs/*.json`), manifest (`manifest.jsonl`), result files (`results/evaluation/**/*.json`)

## Runtime

**Environment:**
- Python 3.12.3 (Ubuntu 24.04 LTS)
- Virtual environment: `env_parbench/` (created with `python3 -m venv`)
- Activation: `source env_parbench/bin/activate`

**Package Manager:**
- pip (via venv)
- Lockfile: `requirements-lock.txt` (present, pinned to Ubuntu 24.04 / Python 3.12.3, dated 2026-03-27)
- Loose deps: `requirements.txt`

## Frameworks

**Core:**
- pydantic 2.12.5 — Spec data validation and model definitions
- jsonschema 4.26.0 — JSON Schema validation (`schema/spec_schema.json`, `schema/manifest_schema.json`)
- libclang 18.1.1 — AST parsing for C/CUDA/OpenCL augmentation transforms in `c_augmentation/`

**Testing:**
- pytest 9.0.2 — Unit tests for augmentation transforms (`c_augmentation/test_transforms.py`) and analysis scripts

**Build/Dev:**
- ruff 0.11.13 — Python linting and formatting
- setuptools 68+ — Package build backend (`pyproject.toml`)
- Docker — CPU-only validation image (`Dockerfile`) using `python:3.12-slim`

**LLM Client SDKs:**
- anthropic 0.85.0 — Anthropic API client (Claude models)
- openai 2.28.0 — OpenAI API client (also used as OpenAI-compatible adapter for Groq, Google Gemini, Together AI, and Azure OpenAI)

**Data Analysis:**
- matplotlib 3.10.8 — Figure generation for paper (`scripts/generate_paper_figures.py`)
- numpy 2.4.3 — Numerical analysis support

**Utilities:**
- tqdm 4.67.3 — Progress bars in batch scripts
- PyYAML 6.0.3 — YAML parsing (indirect dependency)
- httpx 0.28.1 — Async HTTP client (anthropic SDK dependency)

## Key Dependencies

**Critical:**
- `anthropic==0.85.0` — Primary LLM API calls to Claude models; used in `scripts/evaluation/llm_evaluate.py`
- `openai==2.28.0` — OpenAI, Azure, Groq, Gemini, Together AI calls (all via OpenAI-compatible interface)
- `libclang==18.1.1` — Required for all AST-based augmentation transforms; without it, `c_augmentation/` is non-functional
- `pydantic==2.12.5` — Spec and result data validation throughout harness and evaluation pipeline
- `jsonschema==4.26.0` — Schema validation via `scripts/validate_schema.py --all`

**Infrastructure:**
- `pytest==9.0.2` — 15 augmentation unit tests must all pass before commit
- `ruff==0.11.13` — PostToolUse hook enforces Python style on all `.py` edits

## Configuration

**Environment:**
- `config/paths.json` — Project root, downloads root, HeCBench root paths (runtime-resolved)
- `config/paths.json.template` — Template for path config on new machines
- `config/compiler_inventory.txt` — Captured compiler versions (nvcc 12.3, nvc++ 24.3, gcc 12.4.0)
- API keys configured as environment variables (not in files — see INTEGRATIONS.md)

**Build:**
- `pyproject.toml` — PEP 517 build config, declares `harness` and `c_augmentation` as installable packages
- `Dockerfile` — CPU-only validation container; uses `requirements-lock.txt`

## Compiler Toolchain (HPC-specific)

**CUDA:**
- nvcc 12.3 — at `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
- CUDA include/lib at `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/{include,lib64}`
- Target GPU: NVIDIA GeForce RTX 4070, compute capability sm_89

**OpenMP:**
- g++ 12.4.0 with `-fopenmp` flag
- gcc 12.4.0 (Ubuntu 12.4.0-2ubuntu1~24.04)

**OpenCL:**
- OpenCL headers/libs from NVIDIA HPC SDK 24.3
- Build flag: `-DCL_TARGET_OPENCL_VERSION=120`

**OpenMP Target Offload (GPU):**
- nvc++ 24.3 (NVIDIA HPC SDK) with `-mp=gpu -gpu=cc89`
- Used exclusively for `omp_target` specs (excluded from standard eval batches)

**SYCL:**
- Intel oneAPI DPC++ 2025.3.2 at `/opt/intel/oneapi/compiler/2025.3/bin/compiler`
- CPU-only (no GPU SYCL backend on this machine)

## Platform Requirements

**Development:**
- Linux x86_64 (Ubuntu 22.04 or 24.04)
- Python 3.12+
- NVIDIA GPU (sm_60 minimum, sm_89 tested on RTX 4070)
- NVIDIA HPC SDK 24.3

**Production / Cluster:**
- ALCF Polaris cluster (`run_eval_campaign.pbs`) — PBS job scheduler, `/lus/eagle` filesystem
- HTTP proxy required at ALCF: `proxy.alcf.anl.gov:3128`

---

*Stack analysis: 2026-04-03*
