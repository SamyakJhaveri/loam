---
paths:
  - "**/*.py"
---

# Python Rules

> Auto-loaded on `*.py` files.

## Interpreter

- Always `python3`, never bare `python`
- Venv: `source env_parbench/bin/activate` (created on Linux; may be broken on Mac)
- Install: `python3 -m pip install <pkg>` inside activated venv

## Testing

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

## Harness CLI

- Global flags (`-v`, `--json`) MUST come BEFORE the subcommand

## Style & Formatting

- 4-space indentation
- Double quotes for strings (consistent across `harness/`, `scripts/`, `c_augmentation/`)
- Line length: no explicit limit; most lines under 100 chars
- Trailing commas in multi-line data structures
- `from __future__ import annotations` at top of every module (PEP 604 unions, forward refs)
- `ruff` for lint/format if available
- Match existing file conventions when editing

## Naming

- snake_case Python modules: `spec_loader.py`, `build_error_taxonomy.py`, `augment_dataset.py`
- `test_` prefix for test files: `test_transforms.py`, `test_build_error_taxonomy.py`
- Spec JSON files: `{suite}-{kernel_slug}-{api}.json` (e.g., `rodinia-bfs-cuda.json`)
- snake_case functions: `build_spec()`, `run_spec()`, `verify_run()`, `load_manifest()`
- Private functions leading underscore: `_substitute_variables()`, `_run_shell()`, `_extract_kernel()`
- CLI command functions `cmd_` prefix: `cmd_build()`, `cmd_run()`, `cmd_verify()`
- snake_case variables: `project_root`, `build_result`, `spec_id`
- Constants UPPER_SNAKE_CASE: `BUILD_TIMEOUT_SECONDS`, `EXCLUDED_SPECS`, `MODEL_REGISTRY`
- PascalCase classes: `BuildResult`, `RunResult`, `VerificationResult`, `Status`, `AugmentationConfig`
- Dataclasses for harness result types (`harness/models.py`)
- Pydantic BaseModel for augmentation config (`c_augmentation/augment_dataset.py`)
- Enums: PascalCase class name, UPPER_CASE values (`Status.PASS`, `Status.FAIL`, `Status.TIMEOUT`)
- `kernel_name`: lowercase slug, `+` removed, no uppercase (e.g., `btree`, `hotspot3d`, `lavamd`)
- `unique_id`: `{source_suite}-{kernel_name}-{parallel_api}` (e.g., `rodinia-bfs-cuda`)
- Enforced by `scripts/validate_schema.py`

## Module Design

- `harness/` — proper Python package with `__init__.py`, invoked via `python3 -m harness`
- `scripts/evaluation/` — `__init__.py` present for package imports
- `c_augmentation/` — `__init__.py` present
- `scripts/analysis/` — NO `__init__.py`; scripts use `sys.path.insert` for imports

## Function Design

- Type annotations on all function signatures (return types included)
- Keyword-only for optional parameters via `*`:
  `def build_spec(spec, project_root, *, timeout=600, verbose=False)`
- `Path` for file paths; `dict[str, Any]` for spec dicts (not typed dicts or Pydantic)
- `bool` for flags (verbose, measure_cpu_time)
- Named dataclass instances for complex returns: `BuildResult`, `RunResult`, `VerificationResult`
- `list[str]` for validation errors (empty = valid)
- `int` for CLI commands (exit code)
- `dict[str, Any]` for JSON-serializable data

## Logging

- `log.debug()` — subprocess commands, internal state
- `log.info()` — stdout/stderr forwarding when verbose
- `log.warning()` — non-zero exit codes, skipped strategies
- `log.error()` — missing directories, unhandled exceptions
