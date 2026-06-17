---
paths:
  - "**/*.py"
---

# Python Rules

> Auto-loaded on `*.py` files.

## Interpreter

- Always `python3`, never bare `python`
- uv-managed repo: prefix commands with `uv run` (no manual venv activation)
- Install: add to a `[dependency-groups]` group in `pyproject.toml`, then `uv sync --group <group>` — never pip

## Testing

```bash
uv run pytest tests/ -v
```

## Style & Formatting

- 4-space indentation
- Double quotes for strings
- Line length: no explicit limit; most lines under 100 chars
- Trailing commas in multi-line data structures
- `from __future__ import annotations` at top of every module (PEP 604 unions, forward refs)
- `ruff` for lint/format if available
- Match existing file conventions when editing

## Naming

- snake_case modules: `data_loader.py`, `build_pipeline.py`
- `test_` prefix for test files: `test_pipeline.py`, `test_models.py`
- snake_case functions: `load_data()`, `run_pipeline()`, `validate_output()`
- Private functions leading underscore: `_parse_config()`, `_run_subprocess()`
- snake_case variables: `project_root`, `build_result`, `config_path`
- Constants UPPER_SNAKE_CASE: `DEFAULT_TIMEOUT`, `MAX_RETRIES`
- PascalCase classes: `BuildResult`, `PipelineConfig`
- Enums: PascalCase class name, UPPER_CASE values (`Status.PASS`, `Status.FAIL`)

## Function Design

- Type annotations on all function signatures (return types included)
- Keyword-only for optional parameters via `*`:
  `def run_task(spec, root, *, timeout=600, verbose=False)`
- `Path` for file paths; `dict[str, Any]` for config dicts
- `bool` for flags (verbose, dry_run)
- Named dataclass instances for complex returns
- `list[str]` for validation errors (empty = valid)
- `int` for CLI commands (exit code)

## Logging

- `log.debug()` — subprocess commands, internal state
- `log.info()` — progress updates when verbose
- `log.warning()` — non-zero exit codes, skipped items
- `log.error()` — missing files, unhandled exceptions
