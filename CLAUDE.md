# CLAUDE.md — ParBench

ParBench: benchmark for LLM-based parallel code translation (CUDA ↔ OpenMP ↔ OpenCL).

## Environment

- `python3` always, never `python`. Venv: `source env_parbench/bin/activate`
- Platform: `/home/samyak/` = Linux GPU machine, `/Users/samyakjhaveri/` = macOS dev
- `config/paths.json` has macOS paths. On Linux, project root = `/home/samyak/Desktop/parbench_sam`
- Linux NVIDIA HPC SDK 24.3 (non-standard):
  nvcc: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
  CUDA/OpenCL: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/{include,lib64}`

## Key Architecture

| Path | What it is |
|------|-----------|
| `specs/` | Kernel spec JSONs (`{suite}-{slug}-{api}.json`) |
| `manifest.jsonl` | Append-only kernel registry — never modify existing entries |
| `harness/` | Build→Run→Verify pipeline. Invoke: `python3 -m harness` |
| `c_augmentation/` | AST transforms (libclang). Tests: `pytest c_augmentation/test_transforms.py` |
| `scripts/evaluation/` | LLM eval pipeline (`run_eval_batch.py`, `llm_evaluate.py`) |
| `results/` | Immutable eval + augmentation result JSONs |
| `rodinia/rodinia-src/` | Git submodule (commit `9c10d3ea`) — **empty in worktrees** |
| `HeCBench-master/` | Gitignored but **cloned locally** (1874 benchmark dirs) — specs in `specs/hecbench-*.json` |

## Invariants

1. **`manifest.jsonl` is append-only** — never modify existing entries
2. **Result JSONs are immutable** — use `--resume` to skip existing
3. **Never run evaluations in worktrees** — submodules are empty there
4. **Never change spec run args** without reading the source's `argc` check first
5. **~15 `validate_schema.py --all` errors are expected** (phantom specs only — HeCBench **is** cloned locally) — do not fix
6. **8 KNOWN_FAIL specs** — exclude from eval batches (list in `known-issues.md`)

## Quality

- Read before editing. No partial implementations. Verify before reporting done.
- `ultrathink` for: architecture, eval pipeline, spec correctness, augmentation, published results.
- If unsure, say so explicitly — never guess silently.
- `/validate` before every commit. Pre-commit hook requires waves 1-3; wave 4 (self-critic/opus) is optional.
- **Model selection:** Use Opus for main work. Before commit/push: manually run `/model haiku` (faster, cheaper for transactional git ops).

## Conditional Rules (`.claude/rules/`, auto-loaded by file path)

| File | Triggers on | Key content |
|------|------------|-------------|
| `known-issues.md` | Always | KNOWN_FAIL list, build gotchas, spec status |
| `workflow.md` | Always | 6-stage workflow, agents, teams, anti-patterns |
| `spec-conventions.md` | `specs/`, `manifest.jsonl` | Naming, categories, run arg verification protocol |
| `evaluation.md` | `scripts/evaluation/` | `--suite` required, `--project-root` required, result schema |
| `augmentation.md` | `c_augmentation/`, `scripts/augmentation/` | `--project-root` required, transform bugs |
| `known-issues-archive.md` | `c_augmentation/`, `harness/`, `scripts/augmentation/`, `scripts/evaluation/`, `results/augmentation/`, `results/evaluation/`, `specs/`, `visualizations/` | Historical fix details, moved guardrails |
| `python.md` | `*.py` | `python3`, harness CLI flag ordering (`-v` before subcommand) |
| `validation-loop.md` | hooks, validation agents | 4-wave protocol (gate requires 1-3, wave 4 optional), sentinel, fix loop |
| `github-pages.md` | `visualizations/` | URL, staticrypt, data refresh |
| `frontend-design.md` | `visualizations/` | Design system, styling conventions |

<!-- GSD:project-start source:PROJECT.md -->
## Project

**ParBench**

ParBench is a kernel-centric benchmark framework for evaluating LLM-based parallel code translation (CUDA ↔ OpenMP ↔ OpenCL). It provides 96 executable specs across 5 benchmark suites, a build-run-verify harness, an AST-driven augmentation engine for robustness testing, and a two-campaign evaluation protocol. The current sprint hardens the full pipeline with TDD, integrates a new LLM provider (AskSage/Argonne), and runs multi-model evaluations for NeurIPS 2026 submission.

**Core Value:** Every evaluation result is reproducible and pipeline-correct — so model comparisons in the NeurIPS paper are defensible under peer review.

### Constraints

- **Timeline:** NeurIPS 2026 deadline **May 1, 2026** (Datasets & Benchmarks track)
- **Data immutability:** Never modify existing result JSONs — use --resume to append
- **Audit-first:** Pipeline must be hardened before new model evals are trusted
- **AskSage schema:** Adapter design blocked until full response schema confirmed by researcher
- **Lean planning:** PROJECT.md stays lightweight; phases added to milestones incrementally as work is scoped
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12+ — All pipeline code: harness, evaluation, augmentation, analysis, figure generation
- C/C++ (C++17) — Benchmark kernel source code (CUDA, OpenMP, OpenCL, SYCL targets)
- CUDA — GPU kernel code in Rodinia, HeCBench, XSBench, RSBench, mixbench suites
- HTML/CSS/JavaScript — Static dashboard visualizations in `visualizations/`
- LaTeX — SC26 paper in `docs/paper/latex/`
- Bash — Batch runner scripts in `scripts/batch/`, setup scripts
- JSON — Spec definitions (`specs/`), schemas (`schema/`), manifest (`manifest.jsonl`)
## Runtime
- Python 3.12.3 (Ubuntu 24.04)
- Virtual environment: `env_parbench/` (activate: `source env_parbench/bin/activate`)
- Always use `python3`, never bare `python`
- NVIDIA GeForce RTX 4070 (Ada Lovelace, sm_89, 12 GB VRAM)
- CUDA Toolkit 12.3 (nvcc at `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`)
- NVIDIA HPC SDK 24.3 (nvc++ 24.3-0, for OpenMP target offloading)
- OpenCL via NVIDIA CUDA (headers/libs at `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/{include,lib64}`)
- Intel oneAPI DPC++/C++ 2025.3.2 (SYCL, CPU-only — no GPU backend)
- AMD Ryzen 9 7900X (12 cores / 24 threads, 4.7 GHz base)
- GCC 12.4.0 / G++ 12.4.0 (Ubuntu)
- OpenMP via GCC `-fopenmp`
## Package Manager
- pip (via `python3 -m pip`)
- Lockfile: `requirements-lock.txt` (exact pinned versions from working environment)
- Flexible deps: `requirements.txt` (minimum version constraints)
- Build system: setuptools >= 68 (configured in `pyproject.toml`)
## Frameworks & Libraries
- pydantic 2.12.5 — Data validation for specs and results (`harness/models.py`)
- jsonschema 4.26.0 — Spec/manifest validation against JSON Schema (`scripts/validate_schema.py`)
- libclang 18.1.1 — AST analysis for C/C++/CUDA code augmentation (`c_augmentation/augment_dataset.py`)
- anthropic 0.85.0 — Anthropic API client for Claude models
- openai 2.28.0 — OpenAI API client (also used for Groq, Gemini, Together AI via OpenAI-compatible endpoints)
- matplotlib 3.10.8 — Publication-quality figures for SC26 paper (`scripts/generate_paper_figures.py`)
- numpy 2.4.3 — Numerical analysis (`scripts/analysis/`)
- pytest 9.0.2 — Test runner (`c_augmentation/test_transforms.py`, `tests/test_campaign_results.py`)
- ruff 0.11.13 — Python linter/formatter
- httpx 0.28.1 — HTTP client (used by anthropic SDK)
- tqdm 4.67.3 — Progress bars (used in batch evaluation)
- PyYAML 6.0.3 — YAML parsing
- pillow 12.1.1 — Image handling (matplotlib dependency)
## Build Tools
- setuptools >= 68 — Build backend (`pyproject.toml`)
- Package name: `parbench` v0.1.0
- Installable packages: `c_augmentation`, `harness`
- Optional dependency groups: `[eval]`, `[analysis]`, `[dev]`, `[all]`
- nvcc 12.3 (CUDA compilation) — at `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
- nvc++ 24.3 (OpenMP target offloading) — NVIDIA HPC SDK
- gcc/g++ 12.4.0 (OpenMP, serial C/C++)
- icpx (Intel oneAPI DPC++ — SYCL, CPU-only target)
- Make — Benchmark suites use Makefiles; harness executes `make` via spec build commands
- LaTeX toolchain — `docs/paper/latex/Makefile` for paper compilation
- BibTeX — `docs/paper/latex/references.bib`
- staticrypt (npm package, installed via `npm install -g staticrypt` in CI) — AES-256 HTML encryption
## Key Dependencies (with pinned versions)
| Package | Version (lock) | Purpose | Location |
|---------|---------------|---------|----------|
| pydantic | 2.12.5 | Spec/result data models | `harness/`, `c_augmentation/` |
| jsonschema | 4.26.0 | JSON Schema validation | `scripts/validate_schema.py` |
| libclang | 18.1.1 | C/C++ AST transforms | `c_augmentation/augment_dataset.py` |
| anthropic | 0.85.0 | Claude API client | `scripts/evaluation/llm_evaluate.py` |
| openai | 2.28.0 | OpenAI/Groq/Gemini/Together client | `scripts/evaluation/llm_evaluate.py` |
| matplotlib | 3.10.8 | Paper figures | `scripts/generate_paper_figures.py` |
| numpy | 2.4.3 | Numerical analysis | `scripts/analysis/` |
| pytest | 9.0.2 | Test runner | `c_augmentation/test_transforms.py` |
| ruff | 0.11.13 | Linting/formatting | Project-wide |
## Configuration
- `config/paths.json` — Machine-specific paths (project_root, downloads_root, hecbench_root)
- `config/paths.json.template` — Template with `{{PROJECT_ROOT}}` placeholders
- Generated by: `scripts/setup_claude_for_sam.sh`
- `schema/spec_schema.json` — JSON Schema for Level 2 kernel specs (34K lines)
- `schema/manifest_schema.json` — JSON Schema for manifest.jsonl entries
- `schema/reference_platform.json` — Reference hardware/software platform definition
- `templates/spec_template.json` — Template for new kernel specs
- Build commands are spec-embedded (each spec JSON contains its own build commands)
- Compiler flags vary per spec (CUDA arch, OpenMP flags, OpenCL version targeting)
- `config/compiler_inventory.txt` — Inventory of available compilers on the machine
## Platform Requirements
- Ubuntu 22.04/24.04 LTS
- Python 3.12+
- NVIDIA GPU with CUDA 12.x support
- NVIDIA HPC SDK 24.3 (for nvc++/OpenMP target offload)
- GCC 12+ with OpenMP support
- NVIDIA CUDA toolkit 12.3
- Intel oneAPI 2025.3 (optional, SYCL only)
- Python 3.12+
- No GPU compilation — evaluation must run on Linux GPU machine
- GitHub Actions (ubuntu-latest) for GitHub Pages deployment only
- No CI for compilation or evaluation — all eval runs are manual on the GPU machine
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Languages
## Style & Formatting
- 4-space indentation throughout all Python files
- Double quotes for strings (consistent across `harness/`, `scripts/`, `c_augmentation/`)
- Line length: no explicit limit configured, but most lines stay under 100 characters
- Trailing commas used in multi-line data structures
- `from __future__ import annotations` at the top of every module (PEP 604 union syntax, forward refs)
## Naming Patterns
- snake_case for all Python modules: `spec_loader.py`, `build_error_taxonomy.py`, `augment_dataset.py`
- `test_` prefix for test files: `test_transforms.py`, `test_build_error_taxonomy.py`
- Spec JSON files: `{suite}-{kernel_slug}-{api}.json` (e.g., `rodinia-bfs-cuda.json`)
- snake_case: `build_spec()`, `run_spec()`, `verify_run()`, `load_manifest()`
- Private functions with leading underscore: `_substitute_variables()`, `_run_shell()`, `_extract_kernel()`
- CLI command functions prefixed `cmd_`: `cmd_build()`, `cmd_run()`, `cmd_verify()`
- snake_case: `project_root`, `build_result`, `spec_id`
- Type annotations on all function signatures (return types included)
- Constants are UPPER_SNAKE_CASE: `BUILD_TIMEOUT_SECONDS`, `EXCLUDED_SPECS`, `MODEL_REGISTRY`
- PascalCase: `BuildResult`, `RunResult`, `VerificationResult`, `Status`, `AugmentationConfig`
- Dataclasses (not Pydantic models) for harness result types in `harness/models.py`
- Pydantic BaseModel for augmentation config in `c_augmentation/augment_dataset.py`
- PascalCase class name, UPPER_CASE values: `Status.PASS`, `Status.FAIL`, `Status.TIMEOUT`
- `kernel_name`: lowercase slug, `+` removed, no uppercase (e.g., `btree`, `hotspot3d`, `lavamd`)
- `unique_id`: `{source_suite}-{kernel_name}-{parallel_api}` (e.g., `rodinia-bfs-cuda`)
- Enforced by `scripts/validate_schema.py`
## Module Design
- `harness/` is a proper Python package with `__init__.py`, invoked via `python3 -m harness`
- `scripts/evaluation/` has `__init__.py` for package imports
- `c_augmentation/` has `__init__.py` for package imports
- `scripts/analysis/` does NOT have `__init__.py` -- scripts use `sys.path.insert` for imports
## Import Organization
## Error Handling
## Logging
- `log.debug()` for subprocess commands and internal state
- `log.info()` for stdout/stderr forwarding when verbose
- `log.warning()` for non-zero exit codes and skipped strategies
- `log.error()` for missing directories and unhandled exceptions
## Comments & Documentation
## Function Design
- Keyword-only for optional parameters using `*`: `def build_spec(spec, project_root, *, timeout=600, verbose=False)`
- `Path` for file paths, `dict[str, Any]` for spec dicts (not typed dicts or Pydantic models)
- `bool` for flags (verbose, measure_cpu_time)
- Named dataclass instances for complex returns: `BuildResult`, `RunResult`, `VerificationResult`
- `list[str]` for validation errors (empty = valid)
- `int` for CLI commands (exit code)
- `dict[str, Any]` for JSON-serializable data
## Data Patterns
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Spec-centric: Every operation is parameterized by a JSON kernel spec file
- Pipeline-oriented: Sequential stages (build -> run -> verify) with clear data contracts between stages
- Result immutability: Evaluation and augmentation result JSONs are append-only and never modified
- Manifest-driven: `manifest.jsonl` serves as the global kernel registry (append-only)
- Multi-suite: Supports Rodinia, HeCBench, XSBench, RSBench, mixbench benchmark suites
## Layers
- Purpose: Define kernels, their build/run/verify configurations, and metadata
- Location: `specs/` (208 JSON files), `manifest.jsonl`, `schema/spec_schema.json`
- Contains: Kernel identity, provenance, file lists, build commands, run configurations, verification strategies, hardware requirements, baseline results
- Depends on: Nothing (pure data)
- Used by: Harness, evaluation pipeline, augmentation pipeline, analysis scripts
- Purpose: Compile, execute, and verify benchmark kernels from spec definitions
- Location: `harness/` (7 Python modules)
- Contains: `spec_loader.py` (load specs, resolve paths, extract prompt payloads), `builder.py` (compile via subprocess), `runner.py` (execute with optional GNU time), `verifier.py` (exit_code + stdout_pattern strategies), `reporter.py` (format results), `models.py` (dataclasses: Status, BuildResult, RunResult, VerificationResult, MetricResult, SpecResult), `cli.py` (argparse CLI entry point)
- Depends on: Spec layer, benchmark source code on disk, system compilers (nvcc, gcc, nvc)
- Used by: LLM evaluation pipeline, augmentation verification, manual spec testing
- Purpose: Send source code to LLMs for translation, then grade results via harness
- Location: `scripts/evaluation/` (5 Python modules)
- Contains: `llm_evaluate.py` (single-task LLM call + build/run/verify cycle with iterative repair), `run_eval_batch.py` (batch orchestrator building task lists from manifest), `analyze_eval.py` (result aggregation into summaries), `reverify_pass_results.py` (re-check existing PASS results)
- Depends on: Harness layer, LLM API clients (anthropic, openai SDKs), spec layer
- Used by: Batch shell scripts in `scripts/batch/`, analysis scripts
- Purpose: Apply semantics-preserving C/C++ transforms to source code before LLM translation
- Location: `c_augmentation/` (core transforms), `scripts/augmentation/` (pipeline scripts)
- Contains: `augment_dataset.py` (66K lines: transform classes using libclang AST), `test_transforms.py` (unit tests), `validate_augmentation.py` (validation), `augment_verify.py` (augment -> build -> verify pipeline), `run_augment_batch.py` (batch runner)
- Depends on: libclang Python bindings, harness layer (for verification)
- Used by: Evaluation pipeline (via `augment_level` parameter), standalone augmentation verification
- Purpose: Aggregate evaluation results into tables, figures, and statistics for the SC26 paper
- Location: `scripts/analysis/` (20+ Python modules), `scripts/generate_paper_figures.py`
- Contains: `quantitative_findings.py`, `statistical_analysis.py`, `build_error_taxonomy.py`, `benchmark_characterization.py`, `cross_consistency_audit.py`, `token_analysis.py`, `augmentation_analysis.py`, `sloc_analysis.py`, `generate_paper_data.py`, `cross_model_comparison.py`, plus test files for each
- Depends on: Result JSONs in `results/evaluation/`, spec layer, manifest
- Used by: Paper LaTeX, visualization dashboard
- Purpose: Interactive HTML dashboard for browsing evaluation and augmentation results
- Location: `visualizations/` (HTML pages + JS data files)
- Contains: `overview.html`, `results.html`, `build_results.html`, `llm_evaluation.html`, `pipeline.html`, `architecture.html`, `augmentation_deep_dive.html`, `benchmark_landscape.html`, `sprint_dashboard.html`, data files (`results_data.js`, `eval_results_data.js`, `build_results_data.js`)
- Depends on: Data generated by `scripts/generate_viz_data.py` and `scripts/evaluation/analyze_eval.py --write-dashboard`
- Used by: GitHub Pages deployment, project stakeholders
## Data Flow
- No runtime state database; all state lives in JSON files on disk
- Evaluation state managed via file existence: `--resume` flag skips tasks whose result JSONs already exist
- Manifest is append-only: deleted specs leave orphan manifest entries (expected behavior)
- Baseline results stored directly in spec JSONs (`baseline_results` field)
## Key Abstractions
- Purpose: Complete definition of a single benchmark kernel variant
- Examples: `specs/rodinia-bfs-cuda.json`, `specs/hecbench-nn-omp.json`
- Pattern: JSON conforming to `schema/spec_schema.json` with sections: identity, provenance, files, implementation, build, run, verification, performance, hardware, baseline_results, metadata
- Schema version: `1.0.0`
- Purpose: A (source_spec, target_spec) pair defining a translation task
- Pattern: Same kernel_name, different parallel_api (e.g., rodinia-bfs-cuda -> rodinia-bfs-omp)
- Generated by: `find_translation_pairs()` in `harness/spec_loader.py` from manifest entries
- Purpose: Subset of `files.prompt_payload` that the LLM must produce (kernel-centric translation)
- Pattern: `files.translation_targets` field in every spec JSON
- Families: OpenCL targets = `.cl` files only (kernel-only); OMP/CUDA = curated kernel files
- Purpose: Complete record of a single LLM evaluation task
- Pattern: Per-task JSON with fields: overall_status, source_spec, target_spec, model, augment_level, attempts[], prompt_tokens, completion_tokens, timing data, translated code snippets
- Statuses: PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL, EXTRACTION_FAIL, ERROR, SKIP, TIMEOUT
- Purpose: Outcome type for any harness operation
- Values: PASS, FAIL, ERROR, TIMEOUT, SKIP
- Used by: BuildResult, RunResult, VerificationResult
- Purpose: Pluggable checker for kernel output correctness
- Implemented: `exit_code` (check return code), `stdout_pattern` (regex match on stdout)
- Stub/TODO: `numeric_comparison`, `file_diff`, `custom_script`
- Semantics: Conjunction -- ALL non-SKIP strategies must PASS for overall PASS
- Purpose: Semantics-preserving C/C++ code rewriting to test LLM robustness
- Examples: `ArithmeticTransform`, `SwapCondition`, `PointerArithmeticToArrayIndex`, `TypedefExpansion`, `ChangeNames`, `ChangeFunctionNames`
- Pattern: ABC subclass of `AstTransform` with `discover()` + `apply()` methods using libclang cursors
## Entry Points
- Location: `harness/__main__.py` -> `harness/cli.py:main()`
- Triggers: Manual spec testing, build verification
- Commands: `build`, `run`, `verify` (full pipeline), `prompt` (show LLM payload), `info` (spec summary), `pairs` (list translation pairs)
- Critical: `-v` flag must come BEFORE subcommand
- Location: `scripts/evaluation/run_eval_batch.py`
- Triggers: `python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp --models <model> --project-root <path> --resume -v`
- Responsibilities: Build task list from manifest, iterate tasks calling `evaluate_translation()`, write per-task results + batch summary
- Location: `scripts/evaluation/llm_evaluate.py`
- Triggers: Direct CLI or imported by `run_eval_batch.py`
- Responsibilities: End-to-end translation evaluation for one (source, target, model, level) tuple
- Location: `scripts/evaluation/analyze_eval.py`
- Triggers: `python3 scripts/evaluation/analyze_eval.py --project-root <path>`
- Responsibilities: Aggregate all result JSONs into `eval_summary.json` + `eval_summary.md`
- Location: `scripts/validate_schema.py`
- Triggers: Pre-commit validation, CI
- Responsibilities: Validate all specs against `schema/spec_schema.json`, cross-check manifest consistency
- Location: `scripts/augmentation/augment_verify.py`
- Triggers: Augmentation testing
- Responsibilities: Apply transforms at specified level, then build/run/verify via harness
- Location: `scripts/generate_paper_figures.py`
- Triggers: Paper preparation
- Responsibilities: Generate matplotlib figures from evaluation data for LaTeX
- Location: `scripts/batch/`
- Contains: `run_eval_campaign.sh` (full multi-direction campaign), `run_rodinia_batch.sh`, `run_cuda_batch.sh`, `run_omp_batch.sh`, `run_xsbench_eval.sh`, `run_rodinia_augmented_eval.sh`
## Error Handling
- Harness operations return typed result objects (BuildResult, RunResult, VerificationResult) with Status enum -- never raise exceptions for expected failures
- `evaluate_translation()` wraps the entire evaluation in try/finally to guarantee file restoration (backup/restore pattern)
- Build errors captured as head+tail snippets (`_head_tail()` function) for inclusion in retry prompts and result JSONs
- LLM API failures caught and stored in result JSON `error_message` field
- Iterative repair: on BUILD_FAIL, `analyze_build_failure()` parses linker errors, finds missing symbols in source files, generates targeted repair hints for the LLM retry
- Subprocess timeouts handled with configurable `timeout_seconds` (default 300s for run, 600s for build)
## Cross-Cutting Concerns
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| creating-agent-teams | Creates and launches coordinated agent teams using TeamCreate for multi-teammate tasks requiring cross-talk, shared task lists, and lifecycle management. Use when 2+ workers need to communicate findings to each other, not just report to parent. NOT for independent parallel tasks (use dispatching-parallel-agents instead). | `.claude/skills/agent-team/SKILL.md` |
| augment-test |  | `.claude/skills/augment-test/SKILL.md` |
| catchup |  | `.claude/skills/catchup/SKILL.md` |
| cite-check |  | `.claude/skills/cite-check/SKILL.md` |
| dream |  | `.claude/skills/dream/SKILL.md` |
| eval-run |  | `.claude/skills/eval-run/SKILL.md` |
| feature-dev |  | `.claude/skills/feature-dev/SKILL.md` |
| fix-bug |  | `.claude/skills/fix-bug/SKILL.md` |
| gen-spec |  | `.claude/skills/gen-spec/SKILL.md` |
| grill-research |  | `.claude/skills/grill-research/SKILL.md` |
| hypothesis-tree |  | `.claude/skills/hypothesis-tree/SKILL.md` |
| interpret-results |  | `.claude/skills/interpret-results/SKILL.md` |
| mentoring | "HPC/SE/research teaching framework — surfaces insights grounded in ParBench" | `.claude/skills/mentoring/SKILL.md` |
| model-route |  | `.claude/skills/model-route/SKILL.md` |
| overnight-eval |  | `.claude/skills/overnight-eval/SKILL.md` |
| paper-review-sim |  | `.claude/skills/paper-review-sim/SKILL.md` |
| post-eval |  | `.claude/skills/post-eval/SKILL.md` |
| ralph-loop |  | `.claude/skills/ralph-loop/SKILL.md` |
| reflect |  | `.claude/skills/reflect/SKILL.md` |
| review |  | `.claude/skills/review/SKILL.md` |
| session-start |  | `.claude/skills/session-start/SKILL.md` |
| spec-check |  | `.claude/skills/spec-check/SKILL.md` |
| techdebt |  | `.claude/skills/techdebt/SKILL.md` |
| validate |  | `.claude/skills/validate/SKILL.md` |
| workflow-ref | "Skill/agent reference table, agent teams, thinking levels, atomic task decomposition, memory hygiene, course correction" | `.claude/skills/workflow-ref/SKILL.md` |
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
