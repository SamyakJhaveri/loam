# Coding Conventions

**Analysis Date:** 2026-04-03

## Naming Patterns

**Files:**
- Python modules use `snake_case.py` (e.g., `augment_dataset.py`, `run_eval_batch.py`, `spec_loader.py`)
- Test files are prefixed `test_` (e.g., `test_transforms.py`, `test_campaign_results.py`)
- Shell hooks use `kebab-case.sh` (e.g., `pre-commit-gate.sh`, `post-edit-test.sh`)
- Spec files use `{suite}-{kernel}-{api}.json` (e.g., `rodinia-bfs-cuda.json`)

**Functions:**
- Public functions: `snake_case` (e.g., `build_spec`, `verify_run`, `load_manifest`)
- Private/internal functions: leading underscore `_snake_case` (e.g., `_check_exit_code`, `_build_tasks`, `_project_root`)
- CLI entry points named `cmd_{subcommand}` (e.g., `cmd_build`, `cmd_verify`, `cmd_pairs`)
- Test functions: `test_{description}` — explicit about what is being tested and expected behavior

**Variables and parameters:**
- `snake_case` throughout
- Boolean keyword-only args use `*` separator in signatures: `def build_spec(spec, project_root, *, verbose: bool = False)`
- Logging instances: `log = logging.getLogger(__name__)` at module level (root logger named `"harness"` in `cli.py`, `__name__` elsewhere)

**Types:**
- Pydantic `BaseModel` subclasses for structured config (e.g., `AugmentationConfig` in `augment_dataset.py`)
- `dataclass` for result containers (e.g., `BuildResult`, `RunResult`, `VerificationResult`, `SpecResult` in `harness/models.py`)
- `Enum` for status values: `Status(Enum)` with lowercase string values (`"pass"`, `"fail"`, `"error"`, `"timeout"`, `"skip"`)

**Constants:**
- `UPPER_SNAKE_CASE` at module level (e.g., `BUILD_TIMEOUT_SECONDS`, `BASELINE_ERROR_THRESHOLD`, `EXCLUDED_SPECS`)
- Multi-word constants prefer descriptive names: `AUGMENTABLE_SUFFIXES`, `COMPARISON_OPERATORS`, `MODEL_REGISTRY`

## Code Style

**Formatting:**
- Ruff is the linter/formatter: version `>=0.6.0` (declared in `pyproject.toml` dev dependencies)
- Ruff runs automatically via PostToolUse hook on every Edit/Write to any `.py` file with `ruff check --fix`
- No custom ruff config exists — uses ruff defaults
- Ruff fixes are applied as `# noqa: E402` inline suppression when late imports after `sys.path.insert()` are unavoidable

**Linting:**
- Ruff (replaces flake8, isort, pyupgrade)
- `# noqa: E402` used for intentional late imports (sys.path manipulation before harness imports)
- `# type: ignore[assignment]` used for deliberate monkey-patching in tests (e.g., `random.random = always_zero`)
- No mypy or pyright configured

## Import Organization

**Order:**
1. `from __future__ import annotations` (first, in all `harness/` and `scripts/evaluation/` files)
2. Standard library imports (alphabetical within group)
3. Third-party imports (pydantic, clang, jsonschema, anthropic, etc.)
4. Local/project imports (harness.*, scripts.*)

**Path manipulation:**
- Scripts use `sys.path.insert(0, str(PROJECT_ROOT))` before local imports
- `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` pattern for scripts nested 2-3 levels deep
- Example from `run_eval_batch.py`:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from harness.spec_loader import load_manifest  # noqa: E402
```

**Path Aliases:**
- None — no `__init__.py` barrel files in `scripts/`; `harness/` and `c_augmentation/` are proper packages with `__init__.py`

## Error Handling

**Patterns:**
- Harness pipeline uses `Status` enum; never raises exceptions across pipeline stages — returns structured result objects instead
- CLI layer catches top-level exceptions and prints to stderr with `log.error(..., exc_info=args.verbose)`
- Validation scripts use `sys.exit(1)` on error, `sys.exit(0)` on success
- `or {}` guard for JSON fields that can be null: `(spec.get("baseline_results") or {}).get("configurations", {})` — not `dict.get("key", {})` which returns `None` when key exists with null value
- Try/except used narrowly around specific operations (JSON decode, float conversion, regex), not broadly

**Return values:**
- Functions returning error lists use `list[str]` (empty = no errors), not exceptions
- Pipeline stages return `Status.PASS` / `Status.FAIL` / `Status.ERROR` / `Status.SKIP` — never `True`/`False`

## Logging

**Framework:** Python `logging` module

**Pattern:**
```python
import logging
log = logging.getLogger(__name__)   # in modules
log = logging.getLogger("harness")  # in harness/cli.py (root for the package)
```

**When to log:**
- `log.debug()`: internal state, metric extraction misses, skipped strategies
- `log.warning()`: unknown strategy types, failed metric extraction, unexpected conditions
- `log.error()`: unhandled exceptions at CLI boundary
- `print()`: user-facing output from CLI commands (not logging)

**CLI logging setup:**
```python
level = logging.DEBUG if args.verbose else logging.WARNING
logging.basicConfig(level=level, format="%(name)s %(levelname)s: %(message)s")
```

## Comments

**When to Comment:**
- Module-level docstrings on all public modules — includes usage examples (CLI commands copy-pasteable)
- Function docstrings use NumPy/Google hybrid style with `Parameters`, `Returns` sections for public functions
- Inline comments for non-obvious logic, especially AST transform decisions
- Section separators use dashed lines with label: `# ---------------------------------------------------------------------------\n# Section Name\n# ---------------------------------------------------------------------------`
- Bug/fix references in test docstrings: "Bug A: nested subscripts..." with explicit description of what was wrong

**Docstring style (public functions):**
```python
def verify_run(spec: dict[str, Any], run_result: RunResult) -> VerificationResult:
    """Apply ALL verification strategies; every non-SKIP strategy must PASS.

    Parameters
    ----------
    spec:
        Parsed spec dict.
    run_result:
        The :class:`RunResult` to verify.

    Returns
    -------
    VerificationResult
    """
```

## Function Design

**Size:** Functions are kept focused. Harness functions (builder, runner, verifier) are 30-80 lines. The main pipeline modules (`llm_evaluate.py` at 2083 lines, `augment_dataset.py` at 1952 lines) are large but use internal section separators and private helpers to organize logic.

**Parameters:** Keyword-only boolean flags separated by `*` (PEP 3102):
```python
def run_spec(spec, project_root, configuration="correctness", *, verbose=False, measure_cpu_time=False):
```

**Return Values:**
- Harness functions return structured dataclass instances (`BuildResult`, `RunResult`, `VerificationResult`)
- Validation functions return `list[str]` (errors) — empty list means valid
- Analysis functions return `dict` with named keys

## Module Design

**Exports:**
- `harness/` and `c_augmentation/` are proper packages (have `__init__.py`)
- `scripts/` subdirectories do NOT have `__init__.py` — imported via `sys.path` manipulation
- No barrel-style re-export in `__init__.py` files — imports go directly to the module

**Harness CLI invocation:**
- Global flags (`-v`, `--json`, `--project-root`) MUST come BEFORE the subcommand
- Correct: `python3 -m harness -v verify specs/foo.json`
- Wrong: `python3 -m harness verify -v specs/foo.json`

**Script entry points:**
- All CLI scripts use `if __name__ == "__main__": main()` or `raise SystemExit(main())`
- `argparse` for all CLI argument parsing (no click, typer, etc.)

## Spec JSON Conventions

**Immutability rules:**
- `manifest.jsonl` is append-only — never modify or delete existing entries
- Result JSONs in `results/` are immutable — use `--resume` flag to skip re-running
- Spec `run.arguments` must never change without reading the source binary's `argc` check first

**Spec field access:**
- Always use `or {}` guard for nullable spec fields: `(spec.get("performance") or {}).get("metrics", [])`
- `overall_status` is authoritative for result verdicts — never `run_status` or `error_message`

## Python Version and Interpreter

- **Always `python3`** — never bare `python`
- Requires Python `>=3.12` (declared in `pyproject.toml`)
- Venv: `source env_parbench/bin/activate` before running any project code
- Install packages: `python3 -m pip install <pkg>` inside activated venv

---

*Convention analysis: 2026-04-03*
