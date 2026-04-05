<!-- generated-by: gsd-doc-writer -->
# Development Guide

ParBench is a Python-based benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. This guide covers local development setup, available commands, code style, and contribution workflow.

## Local Setup

### Prerequisites

- **Python >= 3.12** (declared in `pyproject.toml`)
- **NVIDIA CUDA toolkit** (nvcc 12.3) for building CUDA specs
- **GCC 12.x** with `-fopenmp` for OpenMP specs
- **OpenCL headers and libraries** (from NVIDIA HPC SDK 24.3 or system packages) for OpenCL specs
- **libclang 18** system library (required by `c_augmentation/` AST transforms)
- **Git** (the Rodinia benchmark suite is a git submodule)

### Clone and install

```bash
# Clone with submodules (Rodinia benchmark source)
git clone --recurse-submodules https://github.com/SamyakJhaveri/parbench_sam.git
cd parbench_sam

# Create and activate a virtual environment
python3 -m venv env_parbench
source env_parbench/bin/activate

# Install all dependencies (core + eval + analysis + dev)
python3 -m pip install -r requirements.txt

# Or for exact reproduction of the tested environment:
python3 -m pip install -r requirements-lock.txt

# Install the project in editable mode (registers harness and c_augmentation packages)
python3 -m pip install -e .
```

### Configuration

Copy the paths configuration for your machine:

```bash
# config/paths.json must point to your project root.
# On Linux (GPU machine):
cat > config/paths.json << 'EOF'
{
    "project_root": "/home/samyak/Desktop/parbench_sam",
    "downloads_root": "/home/samyak/Desktop/parbench_sam",
    "hecbench_root": "/home/samyak/Desktop/parbench_sam"
}
EOF
```

See [CONFIGURATION.md](CONFIGURATION.md) for the full list of environment variables and config files.

### Environment variables

LLM evaluation requires API keys set as environment variables (not stored in files):

- `ANTHROPIC_API_KEY` -- for Claude models
- `OPENAI_API_KEY` -- for GPT models
- `GROQ_API_KEY` -- for Groq-hosted Llama models
- `GOOGLE_API_KEY` -- for Gemini models
- `TOGETHER_API_KEY` -- for Together AI-hosted models

These are only needed when running the evaluation pipeline. The harness (build/run/verify) and augmentation modules work without them.

## Build Commands

All commands assume the virtual environment is activated (`source env_parbench/bin/activate`).

### Harness CLI

The harness is invoked as a Python module. **Global flags (`-v`, `--json`, `--project-root`) must come BEFORE the subcommand.**

| Command | Description |
|---------|-------------|
| `python3 -m harness build specs/<name>.json` | Compile a kernel from its spec |
| `python3 -m harness run specs/<name>.json` | Run a compiled kernel (default: correctness config) |
| `python3 -m harness verify specs/<name>.json` | Full pipeline: build, run, verify |
| `python3 -m harness prompt specs/<name>.json` | Print the LLM prompt payload |
| `python3 -m harness info specs/<name>.json` | Print spec summary (no build/run) |
| `python3 -m harness pairs` | List all valid translation pairs from manifest |

Examples:

```bash
# Verbose build + run + verify
python3 -m harness -v verify specs/rodinia-bfs-cuda.json

# Print what the LLM would see (with L2 augmentation)
python3 -m harness prompt specs/rodinia-bfs-cuda.json --augment_level 2

# JSON output for machine consumption
python3 -m harness --json verify specs/rodinia-hotspot-omp.json
```

### Evaluation pipeline

| Command | Description |
|---------|-------------|
| `python3 scripts/evaluation/run_eval_batch.py --suite <suite> --direction <dir> --models <model> --project-root <root> --resume -v` | Batch LLM evaluation with resume support |
| `python3 scripts/evaluation/llm_evaluate.py --source <src.json> --target <tgt.json> --model <model> --project-root <root>` | Single translation task |
| `python3 scripts/evaluation/analyze_eval.py --project-root <root> --output-dir results/evaluation` | Aggregate results into summary JSON and Markdown |

**Critical:** Always pass `--suite` to `run_eval_batch.py` to avoid cross-suite kernel name collisions.

### Augmentation

| Command | Description |
|---------|-------------|
| `python3 scripts/augmentation/augment_verify.py specs/<name>.json --augment_level 2 --seed 42 --project-root <root>` | Augment and verify a single spec |
| `python3 scripts/augmentation/run_augment_batch.py` | Batch augmentation across specs |

### Schema validation

| Command | Description |
|---------|-------------|
| `python3 scripts/validate_schema.py --all` | Validate all specs and manifest entries against JSON Schema |
| `python3 scripts/validate_schema.py --spec specs/<name>.json` | Validate a single spec file |
| `python3 scripts/validate_schema.py --manifest manifest.jsonl` | Validate manifest entries only |

Note: approximately 15 validation errors from `--all` are expected (phantom specs deleted from `specs/` but still referenced in the append-only `manifest.jsonl`).

### Analysis and figures

| Command | Description |
|---------|-------------|
| `python3 scripts/generate_paper_figures.py --project-root <root> --figure all --output-dir docs/paper/figures` | Generate all publication figures |
| `python3 scripts/generate_paper_figures.py --project-root <root> --figure F3 --output-dir docs/paper/figures` | Generate a single figure |
| `python3 scripts/generate_viz_data.py` | Regenerate dashboard JS data files from result JSONs |

### Testing

| Command | Description |
|---------|-------------|
| `python3 -m pytest c_augmentation/test_transforms.py -v` | Run all 15 augmentation unit tests |
| `python3 -m pytest scripts/analysis/test_*.py -v` | Run analysis module tests |

See [TESTING.md](TESTING.md) for detailed test framework documentation.

### Docker (CPU-only validation)

```bash
# Build the validation image
docker build -t parbench .

# Run schema validation
docker run --rm parbench

# Run augmentation unit tests
docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v
```

The Docker image uses `python:3.12-slim` and installs from `requirements-lock.txt`. It does not include CUDA/GPU support -- use the host GPU setup for evaluation runs.

## Code Style

### Ruff (linter and formatter)

ParBench uses **Ruff** (`>= 0.6.0`, declared in `pyproject.toml` dev dependencies) as its sole Python linter and formatter. No custom ruff configuration file exists -- the project uses ruff defaults.

```bash
# Check for lint issues
ruff check .

# Auto-fix lint issues
ruff check --fix .

# Format code
ruff format .
```

Ruff runs automatically via a Claude Code PostToolUse hook on every edit to any `.py` file.

### Conventions

- **Interpreter:** Always `python3`, never bare `python`
- **Naming:** Modules use `snake_case.py`; test files prefixed `test_`; shell hooks use `kebab-case.sh`
- **Imports:** Scripts use `sys.path.insert(0, str(PROJECT_ROOT))` before local imports, with `# noqa: E402` for late imports
- **Error handling:** Harness pipeline stages return typed result objects with `Status` enum (`PASS`, `FAIL`, `ERROR`, `TIMEOUT`, `SKIP`) -- never raise exceptions across pipeline stages
- **Null-safe JSON access:** Always use `(spec.get("key") or {}).get("nested")` instead of `spec.get("key", {}).get("nested")` because `dict.get()` returns `None` (not the default) when the key exists with a null JSON value
- **Logging:** Module-level `log = logging.getLogger(__name__)`; root logger named `"harness"` in `cli.py`
- **CLI flags:** Global flags (`-v`, `--json`, `--project-root`) MUST come BEFORE the subcommand

### No additional linters

There is no ESLint, Prettier, Biome, or `.editorconfig` configuration. The JavaScript/HTML files in `visualizations/` are hand-authored without automated formatting.

## Branch Conventions

- **Main branch:** `main`
- **Feature branches:** Use `gsd/phase-NN-description` for planned phase work (e.g., `gsd/phase-08-figure-regeneration`)
- **Session branches:** Use `session/s-description` for focused work sessions (e.g., `session/s-bib`, `session/s-deps`)
- **Collaborator branches:** Use `name/topic` prefix (e.g., `erel/aug`, `erel/gemini-2.5-flash-results`)

### Commit message format

The project uses a conventional-commits-like format with a scope prefix:

```
type(scope): short description

Examples:
  feat(08): regenerate all publication figures for 5-suite 1,248-task dataset
  test(08): complete UAT - 8 passed, 0 issues
  docs(phase-08): update validation strategy
  fix(08): visual improvements and lint fixes for paper figures
  data(09): regenerate quantitative findings after UAT completion
```

Common types: `feat`, `fix`, `test`, `docs`, `data`, `refactor`.

## PR Process

There is no formal pull request template (`.github/PULL_REQUEST_TEMPLATE.md` does not exist). The following conventions are observed in practice:

- **Create a feature branch** from `main` using the naming conventions above
- **Run the augmentation unit tests** before submitting: `python3 -m pytest c_augmentation/test_transforms.py -v` (all 15 tests must pass)
- **Run schema validation** if specs or manifest were changed: `python3 scripts/validate_schema.py --all`
- **Never modify existing entries** in `manifest.jsonl` (append-only) or existing result JSONs in `results/` (immutable)
- **Never modify benchmark source** in `rodinia/rodinia-src/` unless documenting the patch in `docs/rodinia_toolchain_patches.diff`

### Key invariants to preserve

1. `manifest.jsonl` is append-only -- never modify or delete existing lines
2. Result JSONs in `results/` are immutable -- use `--resume` to skip existing results
3. Spec run arguments must be verified against the actual source's `argc` check before changing
4. The Rodinia submodule (`rodinia/rodinia-src/`) is pinned at commit `9c10d3ea`

## Next Steps

- [ARCHITECTURE.md](ARCHITECTURE.md) -- System design and component relationships
- [TESTING.md](TESTING.md) -- Test framework, running tests, and coverage details
- [CONFIGURATION.md](CONFIGURATION.md) -- Environment variables and config file reference
