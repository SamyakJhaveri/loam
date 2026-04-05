<!-- generated-by: gsd-doc-writer -->
# Testing

ParBench uses **pytest 9.0.2** for all Python tests, supplemented by schema validation scripts and a Docker-based CPU-only validation image. There is no centralized test configuration file; tests are co-located with the modules they cover.

## Test Framework and Setup

**Framework:** [pytest](https://docs.pytest.org/) 9.0.2 (pinned in `requirements-lock.txt`, declared as a dev dependency in `pyproject.toml`).

**Required setup before running tests:**

1. Activate the virtual environment:
   ```bash
   source env_parbench/bin/activate
   ```
2. Ensure dependencies are installed:
   ```bash
   python3 -m pip install -r requirements-lock.txt
   ```
3. The `libclang` system library must be available for augmentation tests (installed via `apt-get install libclang-dev` on Ubuntu/Debian).

## Running Tests

### Augmentation Transform Tests (15 tests)

The primary unit test suite covers the AST-driven augmentation transforms in `c_augmentation/`:

```bash
python3 -m pytest c_augmentation/test_transforms.py -v
```

These 15 tests must all pass before any commit. They are also triggered automatically by the `post-edit-test.sh` hook whenever a file in `c_augmentation/` is edited.

### Analysis Script Tests

Tests for the paper data generation and analysis scripts live in `scripts/analysis/`:

```bash
# All analysis tests
python3 -m pytest scripts/analysis/ -v

# Individual test files
python3 -m pytest scripts/analysis/test_generate_paper_data.py -v
python3 -m pytest scripts/analysis/test_build_error_taxonomy.py -v
python3 -m pytest scripts/analysis/test_statistical_analysis.py -v
python3 -m pytest scripts/analysis/test_token_analysis.py -v
python3 -m pytest scripts/analysis/test_benchmark_characterization.py -v
python3 -m pytest scripts/analysis/test_augmentation_analysis.py -v
python3 -m pytest scripts/analysis/test_quantitative_findings.py -v
```

### Figure Generation Tests

Tests validating the paper figure generation pipeline:

```bash
python3 -m pytest scripts/evaluation/test_generate_paper_figures.py -v
```

### Run a Single Test

```bash
python3 -m pytest c_augmentation/test_transforms.py::test_arithmetic_transform -v
```

## Writing New Tests

### File Naming Convention

- Test files are prefixed with `test_` (e.g., `test_transforms.py`, `test_generate_paper_data.py`).
- Test functions follow the pattern `test_{description}()` with explicit names describing what is being tested.
- Test classes use `class Test{Feature}:` grouping (e.g., `TestMatrixStructure`, `TestPassAtKStochasticFilter`).

### Test File Locations

| Module Under Test | Test File Location |
|---|---|
| `c_augmentation/augment_dataset.py` | `c_augmentation/test_transforms.py` |
| `scripts/analysis/build_error_taxonomy.py` | `scripts/analysis/test_build_error_taxonomy.py` |
| `scripts/analysis/statistical_analysis.py` | `scripts/analysis/test_statistical_analysis.py` |
| `scripts/analysis/token_analysis.py` | `scripts/analysis/test_token_analysis.py` |
| `scripts/analysis/generate_paper_data.py` | `scripts/analysis/test_generate_paper_data.py` |
| `scripts/analysis/benchmark_characterization.py` | `scripts/analysis/test_benchmark_characterization.py` |
| `scripts/analysis/augmentation_analysis.py` | `scripts/analysis/test_augmentation_analysis.py` |
| `scripts/analysis/quantitative_findings.py` | `scripts/analysis/test_quantitative_findings.py` |
| `scripts/generate_paper_figures.py` | `scripts/evaluation/test_generate_paper_figures.py` |

### Import Pattern

Since `scripts/` subdirectories do not have `__init__.py` files, tests use `sys.path.insert()` to make modules importable:

```python
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
```

Or for tests co-located with the module:

```python
sys.path.insert(0, str(Path(__file__).parent))
```

### Test Helpers

- `c_augmentation/test_transforms.py` provides `deterministic_random()` (context manager that pins `random.random` to 0.0), `assert_parseable()` (verifies code parses without fatal clang errors), and `apply_deterministically()` (applies a transform with pinned randomness).
- Analysis test files typically include `_make_record()` or `_make_result()` helper functions that construct minimal synthetic result dicts for testing.
- `scripts/analysis/test_generate_paper_data.py` uses a `paper_data` module-scoped pytest fixture that loads the real `results/analysis/paper_data.json` file once for all tests.

### Test Categories

1. **Unit tests** -- Test individual functions in isolation with synthetic data (e.g., `test_wilson_ci_fields`, `test_classify_verify_fail_wrong_output`).
2. **Integration tests** -- Run scripts end-to-end via `subprocess.run()` and verify they produce valid output (e.g., `test_script_runs_and_produces_json`).
3. **Ground-truth validation tests** -- Load real result JSONs from `results/` and verify computed metrics match independently derived expected values (e.g., `test_campaign_totals`, `test_individual_status_counts`).
4. **Cross-consistency tests** -- Verify that totals sum correctly, rates are in valid ranges, and different views of the same data agree (e.g., `test_direction_totals_sum`, `test_no_negative_rates`).

## Schema Validation

In addition to pytest-based tests, ParBench uses JSON Schema validation for spec files and manifest entries:

```bash
# Validate all specs and manifest entries
python3 scripts/validate_schema.py --all

# Validate a single spec
python3 scripts/validate_schema.py --spec specs/rodinia-bfs-cuda.json

# Validate manifest only
python3 scripts/validate_schema.py --manifest manifest.jsonl
```

Schemas are defined in `schema/spec_schema.json` and `schema/manifest_schema.json`.

**Note:** Approximately 15 validation errors are expected when running `--all`. These come from 5 deleted phantom Rodinia specs still referenced in `manifest.jsonl` (the manifest is append-only). These errors are not bugs and should not be fixed.

## Coverage Requirements

No coverage threshold is configured. Tests focus on correctness verification against known ground-truth values rather than line coverage metrics.

## Docker Validation

A CPU-only Docker image provides a reproducible test environment without GPU dependencies:

```bash
# Build the image
docker build -t parbench .

# Run augmentation tests
docker run --rm parbench python3 -m pytest c_augmentation/test_transforms.py -v

# Run schema validation
docker run --rm parbench python3 scripts/validate_schema.py --all
```

The `Dockerfile` uses `python:3.12-slim`, installs `libclang-dev`, and uses `requirements-lock.txt` for exact version pinning.

## CI Integration

The project has a single GitHub Actions workflow (`.github/workflows/deploy-pages.yml`) that deploys the visualization dashboards to GitHub Pages. It triggers on pushes to `main` that modify `visualizations/**` files. This workflow does not run tests.

There is no CI workflow that runs the test suite automatically. Tests are enforced locally through the pre-commit validation loop:

1. **Post-edit hook** (`.claude/hooks/post-edit-test.sh`) -- Automatically runs relevant tests after file edits as advisory feedback. Triggered for `c_augmentation/`, `harness/`, `scripts/evaluation/`, and `specs/` files.
2. **Pre-commit gate** (`.claude/hooks/pre-commit-gate.sh`) -- Blocks `git commit` unless a `.validation_passed` sentinel file exists and is less than 30 minutes old. The sentinel is written by the `/validate` workflow after all 4 validation waves pass.
3. **Validation loop** -- A 4-wave validation protocol that must pass before committing:
   - Wave 1: Schema verification, diff review, security scan
   - Wave 2: Test synthesis, regression checks, spec audits
   - Wave 3: Consistency checks, code simplification review
   - Wave 4: Self-critic review

## Linting

[Ruff](https://docs.astral.sh/ruff/) 0.11.13 is used for Python linting and formatting. It runs automatically via a PostToolUse hook on every edit to `.py` files:

```bash
ruff check --fix <file>
```
