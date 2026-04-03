# Testing Patterns

**Analysis Date:** 2026-04-03

## Test Framework

**Runner:**
- pytest `>=8.0` (declared in `pyproject.toml` dev dependencies)
- No `pytest.ini` or `setup.cfg` [tool:pytest] section — runs with defaults
- No `conftest.py` files in the project

**Assertion Library:**
- pytest built-in `assert` statements
- `pytest.approx()` for floating-point comparisons (e.g., `assert rate == pytest.approx(0.3625, abs=0.0001)`)
- `pytest.mark.parametrize` for parameterized tests
- `pytest.fixture` for shared setup
- `pytest.skip()` for conditionally skipping when data not yet available

**Run Commands:**
```bash
# Activate venv first
source env_parbench/bin/activate

# Primary test suite — MUST all pass before commit
python3 -m pytest c_augmentation/test_transforms.py -v

# Campaign results validation (requires Qwen result files on disk)
python3 -m pytest tests/test_campaign_results.py -v

# Statistical analysis tests (requires results data)
python3 -m pytest scripts/analysis/test_statistical_analysis.py -v

# Build error taxonomy tests
python3 -m pytest scripts/analysis/test_build_error_taxonomy.py -v

# Paper data generation tests (requires paper_data.json)
python3 -m pytest scripts/analysis/test_generate_paper_data.py -v

# Token analysis tests
python3 -m pytest scripts/analysis/test_token_analysis.py -v

# Paper figures tests
python3 -m pytest scripts/evaluation/test_generate_paper_figures.py -v

# Run all non-data-dependent tests
python3 -m pytest c_augmentation/test_transforms.py scripts/analysis/test_build_error_taxonomy.py scripts/evaluation/test_generate_paper_figures.py -v
```

## Test File Organization

**Location:**
- Co-located with the module under test: `c_augmentation/test_transforms.py` tests `c_augmentation/augment_dataset.py`
- Separate `tests/` directory for integration-level tests: `tests/test_campaign_results.py`
- Nested alongside scripts: `scripts/analysis/test_*.py`, `scripts/evaluation/test_generate_paper_figures.py`

**Naming:**
- All test files: `test_{module_or_subject}.py`
- All test functions: `test_{behavior_being_verified}`
- Test classes: `Test{Component}` (used for logical grouping, not for shared setup)

**Structure:**
```
parbench_sam/
├── c_augmentation/
│   └── test_transforms.py       # 15 tests — AST transform unit tests
├── tests/
│   └── test_campaign_results.py # 12 tests (3 classes) — eval result schema validation
├── scripts/
│   ├── analysis/
│   │   ├── test_statistical_analysis.py   # 13 tests — pass@k and Cochran-Armitage
│   │   ├── test_build_error_taxonomy.py   # 17 tests — VERIFY_FAIL classification
│   │   ├── test_generate_paper_data.py    # 29 tests — paper_data.json correctness
│   │   └── test_token_analysis.py         # 14 tests — EXCLUDED_SPECS filtering
│   └── evaluation/
│       └── test_generate_paper_figures.py # 4 tests — figure utility functions
```

## Test Structure

**Suite Organization:**
```python
class TestPassAtKStochasticFilter:
    """pass@k must use only stochastic (temp > 0) samples, not deterministic."""

    def test_pass_at_k_excludes_deterministic(self):
        """Given 1 deterministic + 3 stochastic records for same task,
        n must be 3 (stochastic only), not 4."""
        records = [...]
        table = compute_pass_at_k_table(records, k_values=[1, 2, 3])
        assert len(table) == 1
        entry = list(table.values())[0]
        assert entry["n"] == 3, f"Expected n=3 (stochastic only), got n={entry['n']}"
```

**Patterns:**
- Test classes group related tests by behavioral category (not by fixture)
- Descriptive docstrings on every test class and function — explain the invariant being tested
- Failure messages in assert statements: `assert x == y, f"Expected y, got {x}"` — never bare asserts on computed values
- Parametrize for multi-suite repetition: `@pytest.mark.parametrize("suite", SUITES)`
- `pytest.fixture(scope="module")` for expensive one-time setup (e.g., loading `paper_data.json`)

## Mocking

**Framework:** No external mocking library (no `unittest.mock`, no `pytest-mock`)

**Patterns:**
- Monkey-patching via context manager for deterministic behavior in augmentation tests:
```python
@contextmanager
def deterministic_random():
    orig_random = random.random
    orig_choice = random.choice
    random.random = always_zero  # type: ignore[assignment]
    random.choice = first        # type: ignore[assignment]
    try:
        yield
    finally:
        random.random = orig_random  # type: ignore[assignment]
        random.choice = orig_choice  # type: ignore[assignment]
```

- `tempfile.TemporaryDirectory()` as context manager for filesystem isolation in token analysis tests
- `subprocess.run()` for end-to-end script tests (e.g., `test_script_runs_and_produces_json` in `test_generate_paper_data.py`)

**What to Mock:**
- `random.random` and `random.choice` in augmentation tests (for deterministic transform selection)
- Filesystem structure (temp directories with written result JSON files) in analysis tests

**What NOT to Mock:**
- The libclang AST parser — tests use real parsing with `ci.Index.create()`
- File I/O in paper_data tests — tests load real `paper_data.json` from `results/analysis/`
- The harness pipeline — integration tests build and run real binaries

## Fixtures and Factories

**Test Data:**
- Inline factory functions (`_make_record`, `_make_result`, `_make_verify_fail_record`) at module scope:
```python
def _make_record(
    kernel: str = "bfs",
    model: str = "test-model",
    direction: str = "cuda-to-omp",
    level: int = 0,
    status: str = "PASS",
    temperature: float = 0.0,
    sample_id: int | str | None = 0,
) -> dict:
    """Build a minimal eval record for testing."""
    return {
        "source_spec": f"rodinia-{kernel}-cuda",
        "model": model,
        "direction": direction,
        "augment_level": level,
        "overall_status": status,
        "temperature": temperature,
        "sample_id": sample_id,
    }
```

- Module-level constants for test data defaults: `DEFAULT_TEST_PROMPT_TOKENS = 1000`
- `pytest.fixture(scope="module")` for loading real output files:
```python
@pytest.fixture(scope="module")
def paper_data() -> dict:
    assert PAPER_DATA_PATH.exists(), f"paper_data.json not found at {PAPER_DATA_PATH}"
    with open(PAPER_DATA_PATH) as f:
        return json.load(f)
```

**Location:**
- No dedicated `fixtures/` directory — all test data is generated inline or loaded from `results/`
- Temporary directories created inline using `tempfile.TemporaryDirectory()`

## Coverage

**Requirements:** None enforced — no coverage config, no minimum threshold

**View Coverage:**
```bash
# Run with coverage (manual)
python3 -m pytest c_augmentation/test_transforms.py --cov=c_augmentation --cov-report=term-missing
```

## Test Types

**Unit Tests (`c_augmentation/test_transforms.py` — 15 tests):**
- Each transform tested in isolation: `test_arithmetic_transform`, `test_swap_condition_positive`, etc.
- Both positive (transform applies) and negative (transform is not applicable) cases per transform
- Bug regression tests named explicitly: `test_pointer_arithmetic_overlapping_nested` (Bug A), `test_swap_condition_skip_assignment_in_operand` (Bug C)
- Parsed output must always be syntactically valid C++: `assert_parseable(result.code)`

**Integration Tests (`c_augmentation/test_transforms.py` — 1 test):**
- `test_real_kernel_pipeline`: runs full augmentation pipeline (all transforms, real libclang AST) on a realistic kernel body

**Schema/Contract Tests (`tests/test_campaign_results.py` — 12 tests across 3 classes):**
- `TestPrimaryCampaignExists`: verifies expected number of result JSON files exist per suite
- `TestResultSchema`: validates required fields, temperature, attempts count in each result JSON
- `TestAugmentationEffect`: validates `overall_status` is from known set across all levels

**Statistical Correctness Tests (`scripts/analysis/test_statistical_analysis.py` — 13 tests):**
- Tests that analysis functions correctly filter stochastic vs deterministic records
- Tests that balanced group constraint is enforced in Cochran-Armitage trend test
- Tests for helper predicates (`is_deterministic`, `is_stochastic`) and module constants

**Taxonomy Tests (`scripts/analysis/test_build_error_taxonomy.py` — 17 tests):**
- Unit tests for `classify_verify_fail()` covering all VERIFY_FAIL subcategories
- Integration tests for `build_taxonomy()` covering mixed status inputs and per-kernel/per-model tracking

**Regression Tests (`scripts/analysis/test_generate_paper_data.py` — 29 tests):**
- Loads real `results/analysis/paper_data.json` and validates specific numeric values
- Tests are assertions against known-correct numbers: `assert by_status["PASS"] == 174`
- Tests mathematical invariants: direction totals sum to campaign total, CI bounds in [0,1]
- Includes subprocess end-to-end test that regenerates paper data and validates JSON structure

**E2E Tests:**
- `test_script_runs_and_produces_json` in `test_generate_paper_data.py` runs the full `generate_paper_data.py` script via `subprocess.run()` with `timeout=120`
- No browser/UI end-to-end tests

## Common Patterns

**Parsing correctness (augmentation tests):**
```python
def assert_parseable(code: str) -> None:
    index = ci.Index.create()
    tu = index.parse(
        path="snippet.cpp",
        args=["-xc++", "-std=c++17"],
        unsaved_files=[("snippet.cpp", code)],
        options=ci.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD,
    )
    fatals = [diag for diag in tu.diagnostics if diag.severity >= ci.Diagnostic.Fatal]
    assert not fatals, f"fatal parse diagnostics: {[str(diag) for diag in fatals]}"
```

**Deterministic transform application:**
```python
def apply_deterministically(transform, code: str) -> str:
    index = ci.Index.create()
    with deterministic_random():
        result = transform.apply(code, index)
    assert result.applied, f"{transform.name} did not apply"
    assert_parseable(result.code)
    return result.code
```

**Floating-point assertions:**
```python
assert overall["pass_rate"] == pytest.approx(0.3625, abs=0.0001)
assert ca["z"] == pytest.approx(-0.17, abs=0.05)
```

**Schema skip when data absent:**
```python
@pytest.fixture(params=SUITES)
def suite_results(self, request) -> tuple[str, list[dict]]:
    suite = request.param
    results = _load_primary_results(suite)
    if not results:
        pytest.skip(f"No primary results for {suite} yet")
    return suite, results
```

## Post-Edit Automated Testing

The `post-edit-test.sh` hook runs automatically after every Edit/Write tool call:

| File edited | Automatic check triggered |
|-------------|--------------------------|
| `c_augmentation/*.py` | `python3 -m pytest c_augmentation/test_transforms.py -x -q --tb=line` (30s timeout) |
| `harness/*.py` | `python3 -m harness --help` (smoke test import) |
| `scripts/evaluation/*.py` | `importlib.import_module('scripts.evaluation.llm_evaluate')` (import smoke test) |
| `specs/*.json` | `python3 scripts/validate_schema.py --spec <file>` |

This runs in advisory mode (always exits 0, never blocks) but surfaces test failures immediately.

## Schema Validation (Non-pytest)

`scripts/validate_schema.py` validates spec JSON files and manifest.jsonl against JSON Schema (Draft-07). Invoked as:

```bash
# Validate a single spec
python3 scripts/validate_schema.py --spec specs/rodinia-bfs-cuda.json

# Validate entire manifest
python3 scripts/validate_schema.py --manifest manifest.jsonl

# Full audit (manifest + all specs + cross-checks)
python3 scripts/validate_schema.py --all
```

Checks performed by `--all`:
1. JSON Schema validation for each manifest entry and spec file
2. Cross-field consistency (unique_id matches filename, api fields agree)
3. File path resolution (prompt_payload files exist on disk)
4. Translation_targets subset of prompt_payload
5. Build working directory existence
6. Manifest-spec cross-consistency (kernel_name, parallel_api match)
7. Cross-kernel pairing (warns if kernel has only 1 API — not useful for translation)

**Expected errors:** ~135 errors are pre-existing and must NOT be fixed:
- ~120 HeCBench `source_dir` disk-not-found (HeCBench not cloned)
- 15 from 5 deleted phantom Rodinia specs still in append-only manifest

## Augmentation Verification (Non-pytest)

`c_augmentation/validate_augmentation.py` runs the full augment → build → run → verify pipeline on specs (separate from unit tests). Invoked via `scripts/augmentation/augment_verify.py`:

```bash
python3 scripts/augmentation/augment_verify.py specs/<name>.json \
  --augment_level 2 --seed 42 -v \
  --project-root /home/samyak/Desktop/parbench_sam
```

## Test Coverage Gaps

**Harness pipeline (no unit tests):**
- `harness/builder.py`, `harness/runner.py`, `harness/verifier.py`, `harness/spec_loader.py`, `harness/reporter.py` — zero pytest tests
- Only covered by integration-level harness runs against real benchmark specs
- Files: `harness/builder.py`, `harness/runner.py`, `harness/spec_loader.py`

**LLM evaluation pipeline (no unit tests):**
- `scripts/evaluation/llm_evaluate.py` (2083 lines) — no unit tests
- `scripts/evaluation/run_eval_batch.py` (567 lines) — no unit tests
- `scripts/evaluation/analyze_eval.py` (563 lines) — no unit tests
- Only validated by running actual LLM eval batches

**Analysis scripts (partial):**
- `scripts/generate_paper_figures.py` — only 4 smoke tests for utility functions; figure generation not tested
- `scripts/analysis/generate_paper_data.py` — tested via subprocess end-to-end + 28 structural tests, but only for Qwen model data

**Validation scripts:**
- `scripts/validate_schema.py` — no pytest tests; tested manually

**Shell hooks (`c.claude/hooks/`):**
- All bash hooks are untested — no shell test framework

---

*Testing analysis: 2026-04-03*
