# Testing Patterns

**Analysis Date:** 2026-04-09

## Test Framework

**Runner:**
- pytest >= 8.0
- Config: `pyproject.toml` (no separate `pytest.ini` or `conftest.py`)
- No pytest plugins configured

**Assertion Library:**
- Built-in `assert` statements (pytest rewrites)
- `pytest.approx()` for floating-point comparison
- `pytest.skip()` for conditional skipping when data files are not generated yet
- `pytest.mark.parametrize` for parameterized tests

**Run Commands:**
```bash
source env_parbench/bin/activate

# Augmentation transform tests (primary test suite)
python3 -m pytest c_augmentation/test_transforms.py -v

# Campaign result validation
python3 -m pytest tests/test_campaign_results.py -v

# Analysis module tests (run from project root)
python3 -m pytest scripts/analysis/test_build_error_taxonomy.py -v
python3 -m pytest scripts/analysis/test_statistical_analysis.py -v
python3 -m pytest scripts/analysis/test_token_analysis.py -v
python3 -m pytest scripts/analysis/test_benchmark_characterization.py -v
python3 -m pytest scripts/analysis/test_augmentation_analysis.py -v
python3 -m pytest scripts/analysis/test_quantitative_findings.py -v
python3 -m pytest scripts/analysis/test_cross_consistency_audit.py -v
python3 -m pytest scripts/analysis/test_generate_paper_data.py -v
python3 -m pytest scripts/analysis/test_cross_model_comparison.py -v

# Figure generation tests
python3 -m pytest scripts/evaluation/test_generate_paper_figures.py -v

# All tests
python3 -m pytest -v
```

## Test File Organization

**Location:** Co-located with source in two patterns:

1. **Same directory as source:** `c_augmentation/test_transforms.py` tests `c_augmentation/augment_dataset.py`
2. **Same directory as analysis scripts:** `scripts/analysis/test_*.py` test `scripts/analysis/*.py`
3. **Dedicated tests directory:** `tests/test_campaign_results.py` for integration-level campaign validation

**Naming:**
- `test_<module_name>.py` for analysis scripts: `test_build_error_taxonomy.py`, `test_statistical_analysis.py`
- `test_transforms.py` for the augmentation module (tests all transform classes)
- `test_campaign_results.py` for result validation tests

**Structure:**
```
parbench_sam/
├── c_augmentation/
│   ├── augment_dataset.py
│   └── test_transforms.py          # 15 tests, augmentation AST transforms
├── tests/
│   └── test_campaign_results.py     # Campaign result schema/count validation
├── scripts/
│   ├── analysis/
│   │   ├── build_error_taxonomy.py
│   │   ├── test_build_error_taxonomy.py    # 15 tests
│   │   ├── statistical_analysis.py
│   │   ├── test_statistical_analysis.py    # 9 tests
│   │   ├── token_analysis.py
│   │   ├── test_token_analysis.py          # 10 tests
│   │   ├── benchmark_characterization.py
│   │   ├── test_benchmark_characterization.py  # 21 tests
│   │   ├── augmentation_analysis.py
│   │   ├── test_augmentation_analysis.py   # 10 tests
│   │   ├── quantitative_findings.py
│   │   ├── test_quantitative_findings.py   # 10 tests
│   │   ├── cross_consistency_audit.py
│   │   ├── test_cross_consistency_audit.py
│   │   ├── generate_paper_data.py
│   │   ├── test_generate_paper_data.py
│   │   ├── cross_model_comparison.py
│   │   └── test_cross_model_comparison.py
│   └── evaluation/
│       └── test_generate_paper_figures.py
└── scripts/
    └── validate_schema.py           # Not pytest -- standalone CLI validator
```

## Test Structure

**Suite organization -- two patterns:**

### Pattern 1: Flat function tests (augmentation, smaller modules)
```python
# c_augmentation/test_transforms.py
def test_arithmetic_transform() -> None:
    code = """
void foo() {
    int x = 0;
    x += 1;
}
"""
    rewritten = apply_deterministically(ArithmeticTransform(), code)
    assert "x = x + (1)" in rewritten
```
Also has a `main()` function that runs all tests manually (standalone mode without pytest):
```python
def main() -> int:
    tests = [test_arithmetic_transform, test_swap_condition_positive, ...]
    for test in tests:
        test()
        print(f"[OK] {test.__name__}")
    return 0
```

### Pattern 2: Class-based test groups (analysis modules)
```python
# tests/test_campaign_results.py
class TestPrimaryCampaignExists:
    """Verify that the expected number of primary result files exist per suite."""

    @pytest.mark.parametrize("suite", SUITES)
    def test_suite_has_primary_results(self, suite: str):
        results = _load_primary_results(suite)
        expected = EXPECTED_L0_PAIRS[suite] * len(AUGMENT_LEVELS)
        assert len(results) == expected, (
            f"{suite}: expected {expected} primary results, got {len(results)}"
        )

class TestResultSchema:
    """Validate the schema/content of each primary result JSON."""

    @pytest.fixture(params=SUITES)
    def suite_results(self, request) -> tuple[str, list[dict]]:
        suite = request.param
        results = _load_primary_results(suite)
        if not results:
            pytest.skip(f"No primary results for {suite} yet")
        return suite, results
```

## Test Helpers

**Synthetic record factories:** Test files use `_make_record()` helper functions to create minimal test data:
```python
# scripts/analysis/test_statistical_analysis.py
def _make_record(
    kernel: str = "bfs",
    model: str = "test-model",
    direction: str = "cuda-to-omp",
    level: int = 0,
    status: str = "PASS",
    temperature: float = 0.0,
    sample_id: int | str | None = 0,
) -> dict:
    return {
        "source_spec": f"rodinia-{kernel}-cuda",
        "model": model,
        ...
    }
```

**Deterministic randomness context manager:**
```python
# c_augmentation/test_transforms.py
@contextmanager
def deterministic_random():
    orig_random = random.random
    orig_choice = random.choice
    random.random = lambda: 0.0
    random.choice = lambda seq: seq[0]
    try:
        yield
    finally:
        random.random = orig_random
        random.choice = orig_choice
```

**Parse validation helper:**
```python
def assert_parseable(code: str) -> None:
    index = ci.Index.create()
    tu = index.parse(path="snippet.cpp", args=["-xc++", "-std=c++17"],
                     unsaved_files=[("snippet.cpp", code)],
                     options=ci.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
    fatals = [d for d in tu.diagnostics if d.severity >= ci.Diagnostic.Fatal]
    assert not fatals
```

## Mocking

**Framework:** `unittest.mock` (standard library)

**Pattern:** Used sparingly. Mainly `unittest.mock.patch` in `test_cross_consistency_audit.py` for mocking file reads.

**What to mock:** External file system state when testing pure logic (rare in this codebase).

**What NOT to mock:** Most tests use real data files or synthetic in-memory dicts. The codebase favors integration-style testing over mocking.

## Fixtures and Factories

**Test data approaches:**

1. **Inline code strings** for augmentation tests:
```python
code = """
void foo(int a, int b) {
    if (a < b) { }
}
"""
```

2. **Synthetic dict factories** for analysis tests (see `_make_record()` above)

3. **Real data file loading** with graceful skip for benchmark characterization and campaign tests:
```python
@pytest.fixture(scope="module")
def char_data() -> dict:
    if not OUTPUT_JSON.exists():
        pytest.skip("benchmark_characterization.json not yet generated")
    return json.loads(OUTPUT_JSON.read_text())
```

4. **Temp directory fixtures** for file I/O tests:
```python
def test_excludes_source_spec(self):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        results = [_make_result("rodinia-bfs-cuda", "rodinia-bfs-omp"), ...]
        _write_results(tmpdir, "test-model", results)
        loaded = load_all_results(tmpdir)
        assert len(loaded) == 2
```

5. **pytest tmp_path** for subprocess end-to-end tests:
```python
def test_script_runs_successfully(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--output-dir", str(tmp_path)],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0
```

**Location:** Fixtures defined in the same test file. No shared `conftest.py` files in the project.

## Coverage

**Requirements:** No coverage targets enforced. No coverage configuration in `pyproject.toml`.

**Coverage tooling:** Not configured. No `pytest-cov` in dependencies.

## Test Types

**Unit tests:**
- Augmentation transform tests (`c_augmentation/test_transforms.py`): 15 tests covering positive/negative cases for each AST transform (ArithmeticTransform, SwapCondition, PointerArithmeticToArrayIndex, TypedefExpansion, ChangeNames, ChangeFunctionNames), plus regression tests for Bugs A, B, C
- Statistical analysis tests: pure function tests for `is_deterministic()`, `is_stochastic()`, `compute_pass_at_k_table()`, `compute_augmentation_trends()`
- Error taxonomy tests: classification function tests with synthetic result dicts
- Token analysis tests: EXCLUDED_SPECS validation, filtering logic, utility extraction

**Integration tests:**
- `test_campaign_results.py`: Validates actual result JSON files on disk (counts, schema, augmentation levels)
- `test_benchmark_characterization.py`: Runs script via subprocess, validates output against independently computed ground truth from raw manifest/spec files
- `test_generate_paper_data.py`: End-to-end subprocess test producing JSON output

**Ground truth validation tests:**
Several test files independently compute expected values from raw data files (manifest.jsonl, spec JSONs, result directories) and compare against script output:
```python
# test_benchmark_characterization.py
def test_category_counts_match_manifest(char_data):
    valid = _load_valid_manifest_entries()
    cat_kernels: dict[str, set[str]] = defaultdict(set)
    for e in valid:
        cat_kernels[e["category"]].add(e["kernel_name"])
    expected_counts = {cat: len(kernels) for cat, kernels in cat_kernels.items()}
    for cat_name, cat_data in char_data["categories"].items():
        assert cat_data["kernel_count"] == expected_counts.get(cat_name, 0)
```

**E2E tests:** Subprocess-based script execution tests that run analysis scripts end-to-end and validate JSON output structure.

## CI/CD Gates

**No CI pipeline configured.** No GitHub Actions, no Jenkins, no GitLab CI files present.

**Pre-commit validation loop (Claude Code specific):**
The project uses a Claude Code hook system in `.claude/settings.json` instead of traditional CI:

1. **PostToolUse auto-test hook** (`post-edit-test.sh`): Runs lightweight tests immediately after every file edit:
   - Edits to `c_augmentation/` trigger `pytest c_augmentation/test_transforms.py -x -q`
   - Edits to `harness/` trigger `python3 -m harness --help` smoke test
   - Edits to `scripts/evaluation/` trigger import smoke test
   - Edits to `specs/` trigger `validate_schema.py --spec`

2. **PostToolUse ruff auto-fix** (inline in `.claude/settings.json`): Runs `ruff check --fix` on every edited `.py` file.

3. **Full validation loop** (`/validate` command): 4-wave validation with 10+ parallel agents:
   - Wave 1: schema validation, diff review, security scan (~30s)
   - Wave 2: test synthesis, regression check, spec audit (~60s)
   - Wave 3: consistency check, code simplification (~45s)
   - Wave 4: self-critic (Opus), plan-reviewer (~30s) — optional for commits
   On failure: fix loop (max 3 iterations). Pre-commit gate (`pre-commit-gate.sh`) requires waves 1-3 to pass via `.validation_passed` sentinel. Wave 4 is available but not required for commits.

## Validation Scripts

**`scripts/validate_schema.py`** -- Standalone schema validator (not a pytest test):
```bash
python3 scripts/validate_schema.py --all              # Full validation
python3 scripts/validate_schema.py --spec specs/X.json # Single spec
python3 scripts/validate_schema.py --manifest manifest.jsonl
```

Validates against JSON Schemas in `schema/`:
- `schema/manifest_schema.json` for manifest entries
- `schema/spec_schema.json` for Level 2 spec files

Cross-cutting checks performed:
- `unique_id` matches filename
- `unique_id` matches `{source_suite}-{kernel_name}-{parallel_api}`
- `implementation.api` matches `identity.parallel_api`
- All classified files exist on disk
- File classification integrity (no overlap between `prompt_payload` and `verification_only`)
- `translation_targets` is a subset of `prompt_payload`
- Build working directory exists
- Manifest-spec field consistency (kernel_name, parallel_api, source_dir)
- Cross-kernel pairing checks (each kernel has >= 2 APIs for translation)
- Build command variable references resolved

**Expected errors:** ~15 errors from 5 deleted phantom Rodinia specs (still referenced in append-only `manifest.jsonl`). Documented in `.claude/rules/known-issues.md`. Do NOT attempt to fix these.

## Protection Hooks

**PreToolUse hooks** (`.claude/settings.json`) that prevent destructive operations:
- `protect-benchmark-sources.sh`: Blocks edits to benchmark source directories (`rodinia/`, `HeCBench-master/`)
- `result-immutability.sh`: Blocks edits to existing result JSON files
- `protect-cuda-omp-results.sh`: Blocks deletion of CUDA-to-OMP evaluation results

## Common Patterns

**Async testing:** Not used. All tests are synchronous.

**Parameterized testing:**
```python
@pytest.mark.parametrize("suite", SUITES)
def test_suite_has_primary_results(self, suite: str):
    results = _load_primary_results(suite)
    assert len(results) == expected
```

**Error testing (negative cases):**
```python
def test_swap_condition_negative_template_and_preprocessor() -> None:
    code = """
#if A < B
#endif
template <typename T> struct Box { T value; };
"""
    index = ci.Index.create()
    transform = SwapCondition()
    assert not transform.is_applicable(code, index)
    result = transform.apply(code, index)
    assert not result.applied
    assert result.code == code
```

**Regression tests (named after bugs):**
```python
def test_pointer_arithmetic_overlapping_nested() -> None:
    """Bug A: nested subscripts like J[iS[i]*cols+j] must not produce overlapping edits."""

def test_pointer_arithmetic_struct_member() -> None:
    """Fix B: *(ptr+i).member form must produce parseable output..."""

def test_swap_condition_skip_assignment_in_operand() -> None:
    """Bug C: comparisons where an operand contains an assignment must be skipped."""
```

**TDD pattern:** Several test files explicitly note "TDD RED phase" in their docstrings, indicating tests were written before implementation:
```python
"""Tests for quantitative_findings.py -- TDD RED phase."""
"""Tests for cross_model_comparison.py -- TDD RED phase: these tests define expected behavior before implementation."""
```

**Graceful skip for missing data:**
```python
if not OUTPUT_JSON.exists():
    pytest.skip("benchmark_characterization.json not yet generated -- run script first")
```

**Assertion messages:** Multi-line f-string messages are standard for clear failure diagnosis:
```python
assert len(results) == expected, (
    f"{suite}: expected {expected} primary results "
    f"({EXPECTED_L0_PAIRS[suite]} L0 pairs x {len(AUGMENT_LEVELS)} levels), "
    f"got {len(results)}"
)
```

---

*Testing analysis: 2026-04-09*
