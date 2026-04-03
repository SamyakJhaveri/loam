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
- `/validate` before every commit. Pre-commit hook enforces `.validation_passed` sentinel.
- **Model selection:** Use Opus for main work. Before commit/push: manually run `/model haiku` (faster, cheaper for transactional git ops).

## Conditional Rules (`.claude/rules/`, auto-loaded by file path)

| File | Triggers on | Key content |
|------|------------|-------------|
| `known-issues.md` | Always | KNOWN_FAIL list, build gotchas, spec status |
| `workflow.md` | Always | 6-stage workflow, agents, teams, anti-patterns |
| `mentoring.md` | Always | HPC/SE/research teaching framework |
| `spec-conventions.md` | `specs/`, `manifest.jsonl` | Naming, categories, run arg verification protocol |
| `evaluation.md` | `scripts/evaluation/` | `--suite` required, `--project-root` required, result schema |
| `augmentation.md` | `c_augmentation/`, `scripts/augmentation/` | `--project-root` required, transform bugs |
| `known-issues-archive.md` | `c_augmentation/`, `harness/` | Historical fix details for augmentation/harness bugs |
| `python.md` | `*.py` | `python3`, harness CLI flag ordering (`-v` before subcommand) |
| `validation-loop.md` | hooks, validation agents | 4-wave protocol, sentinel, fix loop |
| `github-pages.md` | `visualizations/` | URL, staticrypt, data refresh |
| `frontend-design.md` | `visualizations/` | Design system, styling conventions |

<!-- GSD:project-start source:PROJECT.md -->
## Project

**SC26 Paper Completion Sprint**

A focused sprint to complete and strengthen the SC26 ParBench paper (`docs/paper/latex/paper.tex`) before the April 8, 2026 submission deadline. The paper presents ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. This sprint covers all tasks achievable with existing Qwen 3.5 397B evaluation data, focusing on pre-results sections (Sections 1-5) and quantitative rigor.

**Core Value:** Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

### Constraints

- **Deadline**: April 8, 2026 -- hard SC26 submission deadline
- **Data availability**: Only existing Qwen Rodinia data is complete; non-Rodinia and GPT data pending
- **Running evals**: Two tmux sessions MUST NOT be touched (qwen_hecbench, qwen_small)
- **Result immutability**: Never modify existing result JSONs
- **Page limit**: ~10 pages IEEE double-column format
- **Framing**: Benchmark paper, not model evaluation paper
- **HeCBench source**: Cloned locally (gitignored, 1874 dirs) — not a git submodule, so no version pinning
<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->
## Technology Stack

## Languages
- Python 3.12 — All pipeline code (harness, eval, augmentation, analysis, scripts)
- C/C++14/17, CUDA C++, OpenCL C — Benchmark kernel sources across all suites
- Bash — Batch runners (`scripts/batch/`), PBS job script
- JS/HTML/CSS — Visualization dashboards (`visualizations/`)
## Runtime
- Lockfile: `requirements-lock.txt` (pinned to Ubuntu 24.04 / Python 3.12.3, 2026-03-27)
- Loose deps: `requirements.txt`
## Frameworks
- pydantic 2.12.5 — Spec data validation and model definitions
- jsonschema 4.26.0 — JSON Schema validation (`schema/spec_schema.json`, `schema/manifest_schema.json`)
- libclang 18.1.1 — AST parsing for C/CUDA/OpenCL augmentation transforms in `c_augmentation/`; without it, `c_augmentation/` is non-functional
- pytest 9.0.2 — 15 augmentation unit tests must all pass before commit
- ruff 0.11.13 — Python linting/formatting; PostToolUse hook enforces on all `.py` edits
- Docker — CPU-only validation image (`Dockerfile`) using `python:3.12-slim`
- anthropic 0.85.0 — Anthropic API client (Claude models)
- openai 2.28.0 — OpenAI API client (also OpenAI-compatible adapter for Groq, Gemini, Together AI, Azure)
- matplotlib 3.10.8 — Figure generation for paper (`scripts/generate_paper_figures.py`)
- numpy 2.4.3 — Numerical analysis support
## Configuration
- `config/compiler_inventory.txt` — Captured compiler versions (nvcc 12.3, nvc++ 24.3, gcc 12.4.0)
- API keys configured as environment variables (not in files — see INTEGRATIONS.md)
- `pyproject.toml` — PEP 517 build config, declares `harness` and `c_augmentation` as installable packages
- `Dockerfile` — CPU-only validation container; uses `requirements-lock.txt`
## Compiler Toolchain (HPC-specific)
- Target GPU: NVIDIA GeForce RTX 4070, compute capability sm_89
- g++ 12.4.0 with `-fopenmp` flag
- gcc 12.4.0 (Ubuntu 12.4.0-2ubuntu1~24.04)
- OpenCL headers/libs from NVIDIA HPC SDK 24.3
- Build flag: `-DCL_TARGET_OPENCL_VERSION=120`
- nvc++ 24.3 (NVIDIA HPC SDK) with `-mp=gpu -gpu=cc89`
- Used exclusively for `omp_target` specs (excluded from standard eval batches)
- Intel oneAPI DPC++ 2025.3.2 at `/opt/intel/oneapi/compiler/2025.3/bin/compiler`
- CPU-only (no GPU SYCL backend on this machine)
## Platform Requirements
- ALCF Polaris cluster (`run_eval_campaign.pbs`) — PBS job scheduler, `/lus/eagle` filesystem
- HTTP proxy required at ALCF: `proxy.alcf.anl.gov:3128`
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->
## Conventions

## Naming Patterns
- Python modules use `snake_case.py` (e.g., `augment_dataset.py`, `run_eval_batch.py`, `spec_loader.py`)
- Test files are prefixed `test_` (e.g., `test_transforms.py`, `test_campaign_results.py`)
- Shell hooks use `kebab-case.sh` (e.g., `pre-commit-gate.sh`, `post-edit-test.sh`)
- Spec files use `{suite}-{kernel}-{api}.json` (e.g., `rodinia-bfs-cuda.json`)
- Public functions: `snake_case` (e.g., `build_spec`, `verify_run`, `load_manifest`)
- Private/internal functions: leading underscore `_snake_case` (e.g., `_check_exit_code`, `_build_tasks`, `_project_root`)
- CLI entry points named `cmd_{subcommand}` (e.g., `cmd_build`, `cmd_verify`, `cmd_pairs`)
- Test functions: `test_{description}` — explicit about what is being tested and expected behavior
- Logging instances: `log = logging.getLogger(__name__)` at module level (root logger named `"harness"` in `cli.py`, `__name__` elsewhere)
- Pydantic `BaseModel` subclasses for structured config (e.g., `AugmentationConfig` in `augment_dataset.py`)
- `dataclass` for result containers (e.g., `BuildResult`, `RunResult`, `VerificationResult`, `SpecResult` in `harness/models.py`)
- `Enum` for status values: `Status(Enum)` with lowercase string values (`"pass"`, `"fail"`, `"error"`, `"timeout"`, `"skip"`)
## Code Style
- Ruff is the linter/formatter: version `>=0.6.0` (declared in `pyproject.toml` dev dependencies)
- Ruff runs automatically via PostToolUse hook on every Edit/Write to any `.py` file with `ruff check --fix`
- No custom ruff config exists — uses ruff defaults
- Ruff fixes are applied as `# noqa: E402` inline suppression when late imports after `sys.path.insert()` are unavoidable
- `# type: ignore[assignment]` used for deliberate monkey-patching in tests (e.g., `random.random = always_zero`)
## Import Organization
- Scripts use `sys.path.insert(0, str(PROJECT_ROOT))` before local imports
- `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` pattern for scripts nested 2-3 levels deep
- None — no `__init__.py` barrel files in `scripts/`; `harness/` and `c_augmentation/` are proper packages with `__init__.py`
## Error Handling
- Harness pipeline uses `Status` enum; never raises exceptions across pipeline stages — returns structured result objects instead
- Validation scripts use `sys.exit(1)` on error, `sys.exit(0)` on success
- `or {}` guard for JSON fields that can be null: `(spec.get("baseline_results") or {}).get("configurations", {})` — not `dict.get("key", {})` which returns `None` when key exists with null value
- Functions returning error lists use `list[str]` (empty = no errors), not exceptions
- Pipeline stages return `Status.PASS` / `Status.FAIL` / `Status.ERROR` / `Status.SKIP` — never `True`/`False`
## Logging
- `print()`: user-facing output from CLI commands (not logging)
## Comments
- Section separators use dashed lines with label: `# ---------------------------------------------------------------------------\n# Section Name\n# ---------------------------------------------------------------------------`
- Bug/fix references in test docstrings: "Bug A: nested subscripts..." with explicit description of what was wrong
## Module Design
- `harness/` and `c_augmentation/` are proper packages (have `__init__.py`)
- `scripts/` subdirectories do NOT have `__init__.py` — imported via `sys.path` manipulation
- No barrel-style re-export in `__init__.py` files — imports go directly to the module
- Global flags (`-v`, `--json`, `--project-root`) MUST come BEFORE the subcommand
- Correct: `python3 -m harness -v verify specs/foo.json`
- Wrong: `python3 -m harness verify -v specs/foo.json`
- `argparse` for all CLI argument parsing (no click, typer, etc.)
## Spec JSON Conventions
- Always use `or {}` guard for nullable spec fields: `(spec.get("performance") or {}).get("metrics", [])`
- `overall_status` is authoritative for result verdicts — never `run_status` or `error_message`
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->
## Architecture

## Pattern Overview
- Spec-as-contract: each kernel variant is fully described by a JSON spec that drives build, run, verify, and LLM evaluation
- Kernel-centric translation: LLMs only produce kernel files; host infrastructure is untouched
## Layers
- Purpose: Declare what every kernel variant IS and how to verify it
- Location: `specs/`, `manifest.jsonl`, `schema/`
- Contains: 206 JSON spec files, append-only JSONL manifest, JSON Schema validators
- Depends on: Nothing (source of truth)
- Used by: harness, evaluation pipeline, augmentation pipeline
- Purpose: Build a spec's source, run it, and verify output — the "measurement instrument"
- Location: `harness/` (Python package)
- Contains: `spec_loader.py`, `builder.py`, `runner.py`, `verifier.py`, `models.py`, `reporter.py`, `cli.py`
- Depends on: spec files, benchmark source directories (via `config/paths.json`), `c_augmentation/` (optional, for augmented prompts)
- Used by: `scripts/evaluation/llm_evaluate.py`, `scripts/augmentation/augment_verify.py`, CLI (`python3 -m harness`)
- Purpose: Apply semantics-preserving AST transforms to kernel source to create diverse LLM inputs
- Location: `c_augmentation/augment_dataset.py`
- Contains: `Transform` ABC, `AstTransform` subclass, 6 concrete transform classes (see below), `augment_code()` entry point
- Depends on: `libclang` Python bindings
- Used by: `harness/spec_loader.py:get_prompt_payload()` (inline), `scripts/augmentation/augment_verify.py` (standalone)
- Purpose: Call LLMs to translate kernels; verify translated code using the harness; write result JSONs
- Location: `scripts/evaluation/`
- Contains: `llm_evaluate.py` (per-task orchestrator), `run_eval_batch.py` (batch runner), `analyze_eval.py` (aggregator)
- Depends on: harness package, spec files, LLM API keys (env vars)
- Used by: `scripts/batch/*.sh` shell scripts for campaign runs
- Purpose: Immutable per-task result JSONs and aggregate summaries
- Location: `results/evaluation/{model_name}/`, `results/augmentation/`, `results/analysis/`
- Contains: Per-task JSONs (`{src_id}-to-{tgt_id}.json`), batch summary JSONs/MDs, eval_summary.json
- Depends on: Nothing (append-only outputs)
- Used by: `analyze_eval.py`, `scripts/analysis/*.py`, paper figures
## Key Abstractions
- Purpose: Declarative contract defining a kernel variant's identity, source, build, run, and verification
- Examples: `specs/rodinia-bfs-cuda.json`, `specs/xsbench-xsbench-omp.json`
- Pattern: `{suite}-{kernel}-{api}.json`; top-level keys: `identity`, `provenance`, `files`, `implementation`, `build`, `run`, `verification`, `performance`, `hardware`, `baseline_results`
- `prompt_payload`: files the LLM SEES (kernel source)
- `support_files`: files needed to BUILD but not shown to LLM (headers, Makefile)
- `verification_only`: reference implementations NEVER shown to LLM
- `translation_targets`: subset of `prompt_payload`; which files the LLM must PRODUCE (kernel-centric)
- Purpose: Append-only registry linking kernel names to spec files; enables translation pair discovery
- Format: one JSON object per line: `{kernel_name, parallel_api, source_suite, category, spec_file, source_dir}`
- Purpose: Each subclass represents one semantics-preserving code rewrite
- Interface: `is_applicable(code, index, filename)` → bool; `apply(code, index, filename)` → `TransformResult`
- Concrete transforms: `ArithmeticTransform` (compound operators), `SwapCondition` (flip comparisons), `PointerArithmeticToArrayIndex` (ptr+i → arr[i]), `TypedefExpansion`, `ChangeNames` (variable renames), `ChangeFunctionNames`
- Level control: `_select_fraction()` selects 0% (L1=1 candidate) to 100% (L4=all) of candidates; shuffled before selection for randomness
- Overlap safety: `_greedy_valid_subset()` builds largest non-overlapping candidate set when merged set fails validation
- Location: `scripts/evaluation/llm_evaluate.py`
- Purpose: Maps model ID strings to provider info; drives `call_llm()` dispatch
- Current providers: Anthropic (`claude-*`), OpenAI (`gpt-*`, `o1-*`, `o3-*`, `o4-*`), Azure (`azure-*`), Groq (`groq-*`), Google Gemini (`gemini-*`), Together AI (`together-*`)
- Location: `harness/models.py`
- Aggregates: `BuildResult`, `dict[str, RunResult]`, `VerificationResult`, `list[MetricResult]`
- Status enum: `PASS`, `FAIL`, `ERROR`, `TIMEOUT`, `SKIP`
## Entry Points
- Location: `harness/__main__.py` → `harness/cli.py:main()`
- Invocation: `python3 -m harness [build|run|verify|prompt|info|pairs] specs/<name>.json`
- Global flags BEFORE subcommand: `-v`, `--json`, `--project-root`, `--manifest`
- Subcommands: `build` (compile only), `run` (run only), `verify` (full pipeline), `prompt` (print LLM prompt), `info` (spec summary), `pairs` (list translation pairs)
- Location: `scripts/evaluation/run_eval_batch.py`
- Invocation: `python3 scripts/evaluation/run_eval_batch.py --suite rodinia --direction cuda-to-omp --models <model> --project-root <root> --resume -v`
- CRITICAL: `--suite` is required to avoid cross-suite kernel name collisions
- Location: `scripts/evaluation/llm_evaluate.py:evaluate_translation()`
- Called by: `run_eval_batch.py` (importable) or directly via `__main__`
- Location: `scripts/augmentation/augment_verify.py`
- Invocation: `python3 scripts/augmentation/augment_verify.py specs/<name>.json --augment_level 2 --seed 42 --project-root <root>`
- Location: `scripts/evaluation/analyze_eval.py`
- Output: `results/evaluation/eval_summary.json`, `results/evaluation/eval_summary.md`
## Error Handling
- Harness stages return typed result objects (`BuildResult`, `RunResult`, `VerificationResult`) with `Status` enum; never raise on build/run/verify failure
- `evaluate_translation()` uses `try/finally` to guarantee `restore_files()` and `_unstage_support_headers()` always execute
- EXTRACTION_FAIL is a distinct status: LLM response had no parseable code for expected target files
- Iterative repair: on BUILD_FAIL/RUN_FAIL/VERIFY_FAIL, `_build_retry_message()` generates targeted feedback; `analyze_build_failure()` parses linker errors and maps missing symbols to source file locations
<!-- GSD:architecture-end -->

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:
- `/gsd:quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd:debug` for investigation and bug fixing
- `/gsd:execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd:profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
