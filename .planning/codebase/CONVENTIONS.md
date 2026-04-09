# Coding Conventions

**Analysis Date:** 2026-04-09

## Languages

**Primary:** Python 3.12+ (all tooling, harness, evaluation, analysis)
**Secondary:** C/C++/CUDA/OpenCL (benchmark source code under `rodinia/`, `HeCBench-master/`, etc. -- not authored in this project, but consumed by the harness)

**Rule:** Always use `python3`, never bare `python`. Enforced in `.claude/rules/python.md`.

## Style & Formatting

**Formatter:** `ruff` (>= 0.6.0), auto-run on every Python file edit via PostToolUse hook in `.claude/settings.json`:
```json
"command": "... ruff check --fix \"$FILE\" 2>/dev/null || true"
```

**Linting:** `ruff` (same tool). Listed in `[project.optional-dependencies.dev]` in `pyproject.toml`.

**Key style observations from codebase:**
- 4-space indentation throughout all Python files
- Double quotes for strings (consistent across `harness/`, `scripts/`, `c_augmentation/`)
- Line length: no explicit limit configured, but most lines stay under 100 characters
- Trailing commas used in multi-line data structures
- `from __future__ import annotations` at the top of every module (PEP 604 union syntax, forward refs)

## Naming Patterns

**Files:**
- snake_case for all Python modules: `spec_loader.py`, `build_error_taxonomy.py`, `augment_dataset.py`
- `test_` prefix for test files: `test_transforms.py`, `test_build_error_taxonomy.py`
- Spec JSON files: `{suite}-{kernel_slug}-{api}.json` (e.g., `rodinia-bfs-cuda.json`)

**Functions:**
- snake_case: `build_spec()`, `run_spec()`, `verify_run()`, `load_manifest()`
- Private functions with leading underscore: `_substitute_variables()`, `_run_shell()`, `_extract_kernel()`
- CLI command functions prefixed `cmd_`: `cmd_build()`, `cmd_run()`, `cmd_verify()`

**Variables:**
- snake_case: `project_root`, `build_result`, `spec_id`
- Type annotations on all function signatures (return types included)
- Constants are UPPER_SNAKE_CASE: `BUILD_TIMEOUT_SECONDS`, `EXCLUDED_SPECS`, `MODEL_REGISTRY`

**Classes:**
- PascalCase: `BuildResult`, `RunResult`, `VerificationResult`, `Status`, `AugmentationConfig`
- Dataclasses (not Pydantic models) for harness result types in `harness/models.py`
- Pydantic BaseModel for augmentation config in `c_augmentation/augment_dataset.py`

**Enums:**
- PascalCase class name, UPPER_CASE values: `Status.PASS`, `Status.FAIL`, `Status.TIMEOUT`

**Spec identity fields:**
- `kernel_name`: lowercase slug, `+` removed, no uppercase (e.g., `btree`, `hotspot3d`, `lavamd`)
- `unique_id`: `{source_suite}-{kernel_name}-{parallel_api}` (e.g., `rodinia-bfs-cuda`)
- Enforced by `scripts/validate_schema.py`

## Module Design

**Exports pattern:** No `__all__` lists used. Modules export everything at top-level.

**Barrel files:** `harness/__init__.py` contains a one-line comment only. Not used for re-exports.

**Package structure:**
- `harness/` is a proper Python package with `__init__.py`, invoked via `python3 -m harness`
- `scripts/evaluation/` has `__init__.py` for package imports
- `c_augmentation/` has `__init__.py` for package imports
- `scripts/analysis/` does NOT have `__init__.py` -- scripts use `sys.path.insert` for imports

## Import Organization

**Order (observed consistently):**
1. `from __future__ import annotations`
2. Standard library imports (`argparse`, `json`, `logging`, `sys`, `time`, `re`, `pathlib`)
3. Third-party imports (`pydantic`, `jsonschema`, `numpy`, `scipy`, `clang.cindex`)
4. Local/project imports (`from harness.models import ...`, `from harness.builder import ...`)

**Path manipulation pattern:** Scripts outside packages use `sys.path.insert(0, ...)` to resolve project-relative imports:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

**Path aliases:** None configured (no `pyproject.toml [tool.ruff.isort]` or similar). All imports use explicit relative or absolute paths.

## Error Handling

**Harness pattern -- Result objects, never exceptions:**
The harness pipeline never raises exceptions to communicate failure. Every operation returns a typed result object:
```python
# harness/builder.py
def build_spec(...) -> BuildResult:
    # Returns BuildResult(status=Status.FAIL, ...) on error
    # Returns BuildResult(status=Status.TIMEOUT, ...) on timeout
    # Returns BuildResult(status=Status.PASS, ...) on success
```

All `subprocess.TimeoutExpired`, `FileNotFoundError`, and generic `Exception` are caught and wrapped into result objects with appropriate `Status` enum values. The `stderr` field carries the error message.

**CLI top-level pattern -- catch-all with exit codes:**
```python
# harness/cli.py
try:
    rc = args.func(args)
except Exception as exc:
    log.error("Unhandled error: %s", exc, exc_info=args.verbose)
    print(f"ERROR: {exc}", file=sys.stderr)
    rc = 2
sys.exit(rc)
```
Exit codes: 0 = success, 1 = test failure (FAIL/VERIFY_FAIL), 2 = unhandled error.

**Evaluation pipeline -- early return on missing data:**
```python
# scripts/evaluation/llm_evaluate.py and run_eval_batch.py
if config is None:
    return RunResult(status=Status.ERROR, ..., stderr=f"Configuration '{configuration}' not found")
```

**JSON loading -- fail-fast with clear messages:**
```python
try:
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: jsonschema is required. Install with: pip install jsonschema")
    sys.exit(1)
```

**`or {}` guard for nullable JSON values (CRITICAL):**
```python
# CORRECT: handles JSON null values
(spec.get("baseline_results") or {}).get("configurations", {})

# WRONG: dict.get("key", {}) returns None when key exists with null value
spec.get("baseline_results", {}).get("configurations", {})
```
Documented in `.claude/rules/evaluation.md` as a known Python gotcha.

## Logging

**Framework:** Python `logging` module.

**Logger naming:** Per-module loggers using `__name__`:
```python
log = logging.getLogger(__name__)     # harness/builder.py, runner.py, verifier.py
log = logging.getLogger("harness")    # harness/cli.py (root harness logger)
```

**When to log:**
- `log.debug()` for subprocess commands and internal state
- `log.info()` for stdout/stderr forwarding when verbose
- `log.warning()` for non-zero exit codes and skipped strategies
- `log.error()` for missing directories and unhandled exceptions

**Configuration:** Set in `cli.py:main()` based on `--verbose` flag:
```python
level = logging.DEBUG if args.verbose else logging.WARNING
logging.basicConfig(level=level, format="%(name)s %(levelname)s: %(message)s")
```

**Analysis scripts:** Use `print()` directly for output, not `logging`. Only the harness uses structured logging.

## Comments & Documentation

**Module docstrings:** Every Python module has a docstring. Format:
```python
"""harness.builder — Compile a kernel from its spec."""
```
The `module — description` format is used consistently in `harness/`.

**Function docstrings:** NumPy-style for harness modules (`Parameters`, `Returns`, `Notes` sections with dashed underlines):
```python
def build_spec(spec, project_root, *, timeout=600, verbose=False) -> BuildResult:
    """Build a single kernel according to its spec.

    Parameters
    ----------
    spec:
        Parsed spec dict.
    project_root:
        Absolute path to the *parbench_sam/* project root.

    Returns
    -------
    BuildResult
    """
```

**Analysis scripts:** Use shorter docstrings without NumPy sections, often just a description.

**Inline comments:** Sparse. Used for non-obvious logic or to explain "why":
```python
# Use the spec's executable name as argv[0], not the resolved absolute path.
# On POSIX, subprocess resolves relative paths in cmd[0] against cwd.
cmd: list[str] = [executable] + [str(a) for a in arguments]
```

**Section dividers:** Consistent use of `# ---` comment blocks to separate logical sections:
```python
# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------
```

## Function Design

**Parameters:**
- Keyword-only for optional parameters using `*`: `def build_spec(spec, project_root, *, timeout=600, verbose=False)`
- `Path` for file paths, `dict[str, Any]` for spec dicts (not typed dicts or Pydantic models)
- `bool` for flags (verbose, measure_cpu_time)

**Return values:**
- Named dataclass instances for complex returns: `BuildResult`, `RunResult`, `VerificationResult`
- `list[str]` for validation errors (empty = valid)
- `int` for CLI commands (exit code)
- `dict[str, Any]` for JSON-serializable data

**Size:** Functions are moderate-length (20-60 lines typical). Longest functions are in `llm_evaluate.py` and `validate_schema.py` (pipeline orchestration).

## Data Patterns

**Spec dicts:** All spec data flows as `dict[str, Any]` -- parsed from JSON, never converted to typed models. Access via `.get()` with defaults:
```python
identity = spec.get("identity", {})
unique_id = identity.get("unique_id", "")
```

**Constants as frozensets:** Exclusion lists use `frozenset` for O(1) lookup and immutability:
```python
EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    ...
})
```

**Project root resolution:** Always resolved via `Path(__file__).resolve().parent.parent...`:
```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
```

**File path handling:** Always use `pathlib.Path`, never string concatenation for paths.

---

*Convention analysis: 2026-04-09*
