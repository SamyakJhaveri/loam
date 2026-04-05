<!-- generated-by: gsd-doc-writer -->
# Configuration

ParBench uses a combination of environment variables, JSON configuration files, and JSON spec files to control its behavior. There is no single `.env` file; all configuration is managed through explicit files and shell environment variables.

## Environment Variables

### LLM API Keys (Evaluation Pipeline)

The evaluation pipeline (`scripts/evaluation/llm_evaluate.py`) dispatches to different LLM providers based on the model ID prefix. Each provider requires its own API key set as an environment variable.

| Variable | Required For | Description |
|----------|-------------|-------------|
| `ANTHROPIC_API_KEY` | `claude-*` models | Anthropic API key for Claude models |
| `OPENAI_API_KEY` | `gpt-*`, `o1-*`, `o3-*`, `o4-*` models | OpenAI API key |
| `AZURE_OPENAI_API_KEY` | `azure-*` models | Azure OpenAI deployment API key |
| `AZURE_OPENAI_ENDPOINT` | `azure-*` models | Azure OpenAI endpoint URL (scheme + host only; path/query are stripped) |
| `GROQ_API_KEY` | `groq-*` models | Groq API key for Llama models |
| `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `gemini-*` models | Google AI API key (either variable name works) |
| `TOGETHER_API_KEY` | `together-*` models | Together AI API key for Qwen and other hosted models |

All API key variables are **required** only when running evaluations with that specific provider. The pipeline raises a `ValueError` at call time if the needed key is missing. Keys are never read from files -- they must be set in the shell environment.

### Runtime Environment Variables (Spec-Level)

Individual kernel specs can declare runtime environment variables in their `run.environment_variables` field. The harness runner (`harness/runner.py`) copies the current `os.environ`, overlays any spec-declared variables, and passes the result to the subprocess. Common examples found in specs:

| Variable | Used By | Description |
|----------|---------|-------------|
| `LD_LIBRARY_PATH` | Several CUDA specs (e.g., `rodinia-backprop-cuda`, `rodinia-dwt2d-cuda`, `rodinia-lavamd-cuda`) | Ensures `libcudart.so.12` is found at runtime; typically set to `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64` |

Most specs set `environment_variables` to `null`, meaning they inherit the shell environment as-is.

## Config File: `config/paths.json`

The primary configuration file. Used by `harness/spec_loader.py:load_config()` to resolve all relative paths in spec files to absolute paths.

```json
{
    "project_root": "/home/samyak/Desktop/parbench_sam",
    "downloads_root": "/home/samyak/Desktop/parbench_sam",
    "hecbench_root": "/home/samyak/Desktop/parbench_sam"
}
```

| Key | Required | Description |
|-----|----------|-------------|
| `project_root` | Yes | Absolute path to the ParBench project root directory |
| `downloads_root` | Yes | Absolute path used to resolve spec `provenance.repo_root` paths (benchmark source directories) |
| `hecbench_root` | Yes | Absolute path to the HeCBench source directory root |

A template is provided at `config/paths.json.template` with `{{PROJECT_ROOT}}` placeholders. Copy the template to `config/paths.json` and replace placeholders with the actual absolute path to your project root.

**Fallback behavior:** If `config/paths.json` is missing or unreadable, `spec_loader.py:resolve_paths()` falls back to resolving `repo_root` relative to the `--project-root` CLI argument.

**Docker override:** The `Dockerfile` auto-generates `config/paths.json` with all paths set to `/app` (the container working directory).

## Config File: `config/compiler_inventory.txt`

A captured snapshot of compiler and GPU information on the reference platform. This is an informational file (not parsed by any pipeline code) that records the exact toolchain versions used for baseline measurements.

Captured tools:

| Tool | Version | Path |
|------|---------|------|
| nvcc (CUDA compiler) | 12.3, V12.3.103 | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc` |
| nvc++ (NVIDIA HPC C++) | 24.3-0 | NVIDIA HPC SDK |
| gcc | 12.4.0 (Ubuntu 12.4.0-2ubuntu1~24.04) | System |
| g++ | 12.4.0 (Ubuntu 12.4.0-2ubuntu1~24.04) | System |
| Intel DPC++ | 2025.3.2 | `/opt/intel/oneapi/compiler/2025.3/bin/compiler` |
| GPU | NVIDIA GeForce RTX 4070, compute capability sm_89, 12282 MiB | -- |

## Config File: `schema/reference_platform.json`

Defines the shared reference hardware and software platform used for all baseline measurements. Spec files reference this via a `$ref` field in their `hardware.reference_platform` section.

| Key | Value |
|-----|-------|
| `platform_id` | `rtx4070-r9-7900x` |
| `gpu.model` | NVIDIA GeForce RTX 4070 |
| `gpu.compute_capability` | sm_89 |
| `gpu.vram_gb` | 12 |
| `cpu.model` | AMD Ryzen 9 7900X |
| `cpu.cores` | 12 |
| `cpu.threads` | 24 |

## JSON Schema Files

Located in `schema/`, these define the structure of specs and manifest entries. They are used by `scripts/validate_schema.py` for validation but do not contain runtime configuration.

| File | Purpose |
|------|---------|
| `schema/spec_schema.json` | JSON Schema (draft-07) for kernel spec files in `specs/`. Defines required fields: `spec_version`, `identity`, `provenance`, `files`, `implementation`, `build`, `run`, `verification`, `hardware`. |
| `schema/manifest_schema.json` | JSON Schema (draft-07) for each line in `manifest.jsonl`. Required fields: `kernel_name`, `parallel_api`, `source_suite`, `spec_file`, `source_dir`. |
| `schema/reference_platform.json` | Shared hardware platform definition (see above). |

## Required vs Optional Settings

### Required (pipeline will fail without these)

- **`config/paths.json`** -- Required by `harness/spec_loader.py` for path resolution. Without it, the harness falls back to `--project-root` but some paths may not resolve correctly.
- **LLM API key for the target provider** -- The evaluation pipeline raises `ValueError` immediately if the API key environment variable for the selected model prefix is not set.
- **`AZURE_OPENAI_ENDPOINT`** -- Additionally required (beyond the API key) when using `azure-*` models.

### Optional (have defaults or are informational)

- **`config/compiler_inventory.txt`** -- Informational only; not read by any pipeline code.
- **`schema/reference_platform.json`** -- Referenced by specs but not loaded at runtime by the harness.
- **Spec `run.timeout_seconds`** -- Defaults to `300` seconds if not specified in a spec file.
- **Spec `run.environment_variables`** -- Defaults to `null` (inherits shell environment).
- **`--project-root` CLI flag** -- Defaults to auto-detected project root in harness CLI and batch runner.
- **`--resume` flag** -- Defaults to `True` in `run_eval_batch.py` (skips existing result files).
- **`--temperature` flag** -- Defaults to `0.0` (greedy decoding) in `run_eval_batch.py`.
- **`--max-retries` flag** -- Defaults to `1` (zero-shot, no retries) in `run_eval_batch.py`.
- **`--augment-levels` flag** -- Defaults to `[0]` (no augmentation) in `run_eval_batch.py`.

## Spec Build Variables

Individual spec files can declare build-time variables in their `build.variables` field. These are substituted into build commands. Common variables across specs:

| Variable | Used By | Default | Description |
|----------|---------|---------|-------------|
| `CUDA_DIR` | CUDA specs (e.g., `rodinia-hotspot-cuda`, `rodinia-hotspot3d-cuda`, `rodinia-dwt2d-cuda`) | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda` | Path to CUDA toolkit installation |
| `OPENCL_INC` | OpenCL specs (e.g., `rodinia-nn-opencl`, `rodinia-backprop-opencl`, `rodinia-heartwall-opencl`) | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/include` | Path to OpenCL header files |
| `OPENCL_LIB` | OpenCL specs (same as above) | `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64` | Path to OpenCL library files |

These values are embedded directly in spec JSON files. On a different system, you would need to update the spec files or pass the correct paths via Makefile variable overrides.

## Per-Environment Overrides

ParBench does not use environment-file-based overrides (no `.env.development`, `.env.production`, etc.). Configuration varies by platform in two ways:

1. **`config/paths.json`** -- Must be updated per machine. The template (`config/paths.json.template`) uses `{{PROJECT_ROOT}}` placeholders. On the reference Linux machine, all three paths point to `/home/samyak/Desktop/parbench_sam`. On macOS, they would point to `/Users/samyakjhaveri/Desktop/parbench_sam`. In Docker, they point to `/app`.

2. **Spec build variables** -- CUDA and OpenCL paths in spec JSON files are hardcoded to the NVIDIA HPC SDK paths on the reference Linux machine (`/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/...`). On a system with a standard CUDA install, these would typically be `/usr/local/cuda`.

3. **Docker** -- The `Dockerfile` builds a CPU-only validation image. It auto-generates `config/paths.json` with `/app` paths and installs pinned dependencies from `requirements-lock.txt`. GPU-dependent operations (CUDA builds, OpenCL kernel execution) are not available in the container.

## Model Registry

The evaluation pipeline maintains a `MODEL_REGISTRY` dictionary in `scripts/evaluation/llm_evaluate.py` that maps model ID strings to provider metadata. This is not a config file but a code-level registry that determines API dispatch.

| Model ID | Provider | Notes |
|----------|----------|-------|
| `claude-sonnet-4-20250514` | Anthropic | Primary eval model |
| `claude-sonnet-4-6-20260218` | Anthropic | Latest Sonnet |
| `claude-opus-4-6-20260205` | Anthropic | Strongest reasoning |
| `claude-haiku-4-5-20251001` | Anthropic | Fast/cheap baseline |
| `gpt-4o` | OpenAI | Strong general-purpose |
| `gpt-4.1-2025-04-14` | OpenAI | Latest GPT-4 class |
| `o3-2025-04-16` | OpenAI | Reasoning model |
| `o4-mini-2025-04-16` | OpenAI | Fast reasoning |
| `azure-gpt-4.1` | Azure | GPT-4.1 via Azure OpenAI |
| `groq-llama-3.3-70b-versatile` | Groq | Llama 3.3 70B via Groq |
| `gemini-2.5-flash-lite` | Google | Gemini 2.5 Flash-Lite |
| `gemini-2.5-flash` | Google | Gemini 2.5 Flash (thinking disabled) |
| `together-qwen-3.5-397b-a17b` | Together AI | Qwen 3.5 397B MoE (thinking disabled) |

New models can be added by inserting an entry in `MODEL_REGISTRY` and ensuring the model ID prefix matches an existing provider branch in the `call_llm()` function.

## Dependency Configuration

### `pyproject.toml`

PEP 517 build configuration. Declares `parbench` as an installable package with optional dependency groups:

| Group | Packages | Purpose |
|-------|----------|---------|
| (core) | `pydantic>=2.0`, `jsonschema>=4.20`, `libclang>=18.1` | Harness, schema validation, AST augmentation |
| `eval` | `anthropic>=0.40.0`, `openai>=1.50.0` | LLM evaluation pipeline |
| `analysis` | `matplotlib>=3.9`, `numpy>=1.26` | Results analysis and figure generation |
| `dev` | `pytest>=8.0`, `ruff>=0.6.0` | Testing and linting |
| `all` | All of the above | Full install |

### `requirements.txt`

Loose dependency pins matching the `pyproject.toml` groups, suitable for `pip install -r requirements.txt`.

### `requirements-lock.txt`

Exact pinned versions from the working environment (Ubuntu 24.04, Python 3.12.3, generated 2026-03-27). Used by the `Dockerfile` for reproducible builds. Contains 49 packages with exact version pins.

### Python Version

Requires Python >= 3.12, as declared in `pyproject.toml` (`requires-python = ">=3.12"`).
