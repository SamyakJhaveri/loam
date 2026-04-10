# Phase 01: Pipeline Testing & Uniformity - Research

**Researched:** 2026-04-10
**Domain:** Python testing (pytest), harness pipeline (build/run/verify), code deduplication
**Confidence:** HIGH

## Summary

Phase 1 is a testing and cleanup phase operating entirely within the existing ParBench Python codebase. No new external libraries are needed -- the work uses pytest (already installed, 9.0.2), the existing harness Python API (`build_spec`, `run_spec`, `verify_run`), and standard library modules (`argparse`, `json`, `pathlib`). The codebase is well-understood: 185 tests already pass, the harness API is stable with consistent `(spec: dict, project_root: Path)` signatures, and the 5 sample specs per suite are already defined in `tests/test_spec_loader_integration.py`.

The main risks are: (1) integration tests that depend on real GPU compilation taking too long or flaking due to environment issues, (2) the `analyze_rodinia_batch.py` replacement needing to match the existing output format exactly while becoming suite-agnostic, and (3) the `quantitative_findings.py` Rodinia-specific counter generalization touching a large file (~3085 lines) where a wrong edit could break paper data generation.

**Primary recommendation:** Implement in order: `harness/constants.py` first (unblocks everything else), then integration tests, then batch analyzer replacement, then analysis script cleanup, then TDD campaign tests last.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Test scope is sampling -- 1 representative spec per suite. Use the same 5 specs already chosen in `tests/test_spec_loader_integration.py`: `rodinia-bfs-cuda`, `xsbench-xsbench-cuda`, `rsbench-rsbench-cuda`, `mixbench-mixbench-cuda`, `hecbench-bezier-surface-cuda`.
- **D-02:** Tests live in a new file `tests/test_harness_integration.py`. Do not extend `test_spec_loader_integration.py`.
- **D-03:** Each test runs the full pipeline: `build -> run -> verify`. If build fails, mark test as failed (not just skipped). Test corresponds to `python3 -m harness verify <spec>` end-to-end.
- **D-04:** KNOWN_FAIL specs are skipped via `pytest.mark.skip` using the `EXCLUDED_SPECS` constant (once centralized). Skip message should name the spec and link to KNOWN_FAIL reason.
- **D-05:** Project root is auto-detected from `conftest.py` (existing `PROJECT_ROOT` constant). No new env var or CLI flag required.
- **D-06:** Tests are `@pytest.mark.integration` to allow skipping on machines without GPU/compilers (matches existing conftest skip mechanism).
- **D-07:** Single source of truth lives in `harness/constants.py` (new file). This is the authoritative enforcement point for the 8 KNOWN_FAIL specs.
- **D-08:** All 4 current duplicate definitions are replaced with imports from `harness.constants`: `scripts/evaluation/analyze_eval.py`, `scripts/analysis/quantitative_findings.py`, `scripts/analysis/generate_paper_data.py`, `scripts/analysis/token_analysis.py`.
- **D-09:** `harness/constants.py` is the single source of truth for the KNOWN_FAIL list. `known-issues.md` documents WHY each spec fails; the code enforces. Both must stay in sync.
- **D-10:** Write `scripts/analysis/analyze_harness_batch.py` -- suite-agnostic, accepts `--suite` flag. Delete `analyze_rodinia_batch.py` immediately once the replacement exists. No wrapper, no deprecated stub.
- **D-11:** Output directory: `results/harness/{suite}/` (new namespace). Old Rodinia results in `results/rodinia/logs/` are left untouched.
- **D-12:** Output files per run: `results/harness/{suite}/{suite}_results.json` and `results/harness/{suite}/results_matrix_{suite}.md`.
- **D-13:** `scripts/analysis/quantitative_findings.py` -- replace `rodinia_c1_total`/`rodinia_c1_pass` counters with a per-suite dict.
- **D-14:** `scripts/analysis/classify_translation_pairs.py` -- replace hardcoded Rodinia-only direction breakdown with a `--suite` filter flag.
- **D-15:** Evaluation pipeline files (`harness/`, `scripts/evaluation/`) -- already have no suite-specific hardcoding. Verify, do not change.
- **D-16:** Write `tests/test_campaign_classification.py` with locked interface contract for `campaign_for()`. Mark all tests `@pytest.mark.skip(reason="campaign_for() not yet implemented -- Phase 2")`.
- **D-17:** Interface contract (locked): `campaign_for(record: dict) -> str` where `record` is a result JSON dict. Returns `'c1'` or `'c2'`.
- **D-18:** C2 classification logic: `temperature != 0.0 OR sample_id is not None`. Either signal -> C2.
- **D-19:** Minimum test cases to cover: `{temperature: 0.0, sample_id: None}` -> `'c1'`; `{temperature: 0.7, sample_id: 's1'}` -> `'c2'`.
- **D-20:** `campaign_for()` will ultimately live in `scripts/evaluation/campaign_utils.py` (Phase 2 creates this file).

### Claude's Discretion
- Test fixture structure in `test_harness_integration.py` (parameterization approach, fixture names)
- Exact content/docstring of `harness/constants.py` beyond `EXCLUDED_SPECS`
- Whether `analyze_harness_batch.py` uses `argparse` or `click`
- Internal structure of per-suite dict in `quantitative_findings.py` cleanup

### Deferred Ideas (OUT OF SCOPE)
- Full portability (compiler path templating via `config/paths.json`) -- deferred post-NeurIPS per PROJECT.md
- Migrating existing `results/rodinia/logs/` to `results/harness/rodinia/` -- not worth the risk; old data stays in place
- Campaign edge case tests (temp=0.0 + sample_id present; temp=0.7 + no sample_id) -- user chose minimal test set; Phase 2 can extend
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| pytest | 9.0.2 | Test framework | Already installed and configured in `pyproject.toml` with `integration` marker [VERIFIED: pyproject.toml] |
| harness (internal) | N/A | build_spec, run_spec, verify_run | Existing pipeline API -- no new dependencies [VERIFIED: harness/*.py] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| argparse (stdlib) | N/A | CLI for analyze_harness_batch.py | Suite-agnostic batch analyzer [ASSUMED: follows existing pattern in analyze_rodinia_batch.py] |
| json (stdlib) | N/A | Result JSON read/write | All result I/O |
| pathlib (stdlib) | N/A | Path handling | All file operations |

**No new packages to install.** All work uses existing dependencies.

## Architecture Patterns

### New Files to Create
```
harness/
  constants.py          # EXCLUDED_SPECS frozenset (D-07)
scripts/analysis/
  analyze_harness_batch.py  # Replaces analyze_rodinia_batch.py (D-10)
tests/
  test_harness_integration.py      # Build/run/verify per suite (D-02)
  test_campaign_classification.py  # TDD stubs for Phase 2 (D-16)
results/harness/
  {suite}/              # Created on first run by analyze_harness_batch.py (D-11)
```

### Files to Modify
```
scripts/evaluation/analyze_eval.py        # Replace EXCLUDED_SPECS with import (lines ~49-58)
scripts/analysis/quantitative_findings.py # Replace EXCLUDED_SPECS (lines ~51-60), generalize rodinia counters (lines ~3064-3068)
scripts/analysis/generate_paper_data.py   # Replace EXCLUDED_SPECS (lines ~43-52)
scripts/analysis/token_analysis.py        # Replace EXCLUDED_SPECS (lines ~45-52) -- NOTE: currently missing 2 HeCBench specs!
scripts/analysis/classify_translation_pairs.py  # Add --suite filter (lines ~165-184)
```

### Files to Delete
```
scripts/analysis/analyze_rodinia_batch.py  # Replaced by analyze_harness_batch.py (D-10)
```

### Pattern 1: Integration Test via Python API (not subprocess)
**What:** Call `build_spec()`, `run_spec()`, `verify_run()` directly from pytest, mirroring what `cmd_verify()` in `harness/cli.py` does. [VERIFIED: harness/cli.py lines 116-160]
**When to use:** All `test_harness_integration.py` tests.
**Example:**
```python
# Source: harness/cli.py cmd_verify() pattern
from harness.builder import build_spec
from harness.runner import run_spec
from harness.verifier import verify_run
from harness.models import Status
from harness.spec_loader import load_spec

def test_full_pipeline(suite_spec_path, project_root):
    spec = load_spec(suite_spec_path)
    build_result = build_spec(spec, project_root, verbose=True)
    assert build_result.status == Status.PASS, f"Build failed: {build_result.stderr[:500]}"
    
    run_result = run_spec(spec, project_root, configuration="correctness", verbose=True)
    assert run_result.status == Status.PASS, f"Run failed (exit={run_result.exit_code}): {run_result.stderr[:500]}"
    
    ver_result = verify_run(spec, run_result)
    assert ver_result.status == Status.PASS, f"Verify failed: {ver_result.details}"
```

### Pattern 2: Parametrized Fixture with Suite Specs
**What:** Reuse the `SUITE_SPECS` dict from `test_spec_loader_integration.py` via a parametrized fixture.
**When to use:** Both integration test files should reference the same 5 specs. [VERIFIED: test_spec_loader_integration.py lines 34-39]
**Example:**
```python
# Source: tests/test_spec_loader_integration.py existing pattern
PROJECT_ROOT = Path("/home/samyak/Desktop/parbench_sam")
SPECS_DIR = PROJECT_ROOT / "specs"

SUITE_SPECS = {
    "rodinia": SPECS_DIR / "rodinia-bfs-cuda.json",
    "xsbench": SPECS_DIR / "xsbench-xsbench-cuda.json",
    "rsbench": SPECS_DIR / "rsbench-rsbench-cuda.json",
    "mixbench": SPECS_DIR / "mixbench-mixbench-cuda.json",
    "hecbench": SPECS_DIR / "hecbench-bezier-surface-cuda.json",
}

@pytest.fixture(params=list(SUITE_SPECS.keys()), ids=list(SUITE_SPECS.keys()))
def suite_spec(request):
    suite = request.param
    spec_path = SUITE_SPECS[suite]
    spec = load_spec(spec_path)
    return suite, spec
```

### Pattern 3: EXCLUDED_SPECS as Importable Constant
**What:** Single `frozenset[str]` in `harness/constants.py`, imported everywhere else. [VERIFIED: all 4 copies currently identical except token_analysis.py which is missing 2 HeCBench entries]
**Example:**
```python
# harness/constants.py
"""Shared constants for the ParBench harness and analysis scripts.

EXCLUDED_SPECS: The 8 KNOWN_FAIL specs excluded from evaluation batches
and statistics. See .claude/rules/known-issues.md for WHY each spec fails.
"""
from __future__ import annotations

EXCLUDED_SPECS: frozenset[str] = frozenset({
    "rodinia-kmeans-cuda",
    "rodinia-mummergpu-cuda",
    "rodinia-mummergpu-omp",
    "rodinia-hybridsort-cuda",
    "rodinia-nn-opencl",
    "rodinia-kmeans-opencl",
    "hecbench-stencil1d-omp_target",
    "hecbench-scan-omp_target",
})
```

### Pattern 4: Suite-Agnostic Batch Analyzer
**What:** Replace hardcoded `"rodinia-"` prefix parsing with spec_id split logic that works for any `{suite}-{slug}-{api}` format. [VERIFIED: analyze_rodinia_batch.py lines 28-35]
**Example:**
```python
# Source: analyze_rodinia_batch.py get_all_slugs() — generalized
def get_all_slugs(log_dir: Path, suite: str, apis: list[str]) -> list[str]:
    slugs = set()
    for f in log_dir.glob(f"{suite}-*.json"):
        parts = f.stem.split("-")
        if len(parts) >= 3 and parts[-1] in apis:
            slug = "-".join(parts[1:-1])
            slugs.add(slug)
    return sorted(slugs)
```

### Anti-Patterns to Avoid
- **Subprocess-based integration tests:** Do not shell out to `python3 -m harness verify`. Call the Python API directly -- faster, better error messages, no subprocess overhead. [VERIFIED: harness API is cleanly callable from Python]
- **Hardcoded PROJECT_ROOT in new test files:** Use the same `Path("/home/samyak/Desktop/parbench_sam")` pattern as `test_spec_loader_integration.py` for consistency. The portability issue is deferred post-NeurIPS.
- **Duplicating SUITE_SPECS:** Both test files should define or import the same 5 specs. Do not create a second divergent list.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Test parametrization | Manual test-per-suite functions | `pytest.fixture(params=...)` | DRY, automatic test IDs, consistent with existing pattern [VERIFIED: test_spec_loader_integration.py] |
| Integration skip logic | Custom `if not GPU` guards | `@pytest.mark.integration` + conftest auto-skip | Already implemented in `conftest.py`, handles missing benchmark dirs [VERIFIED: tests/conftest.py] |
| Spec ID parsing | Custom regex per suite | Split on `-`, suite is `parts[0]`, api is `parts[-1]`, slug is middle | Consistent with existing `analyze_rodinia_batch.py` pattern [VERIFIED] |

## Common Pitfalls

### Pitfall 1: token_analysis.py Has Only 6 EXCLUDED_SPECS (Missing HeCBench)
**What goes wrong:** The `EXCLUDED_SPECS` in `scripts/analysis/token_analysis.py` (lines 45-52) only has 6 Rodinia entries, missing the 2 HeCBench KNOWN_FAIL specs (`hecbench-stencil1d-omp_target`, `hecbench-scan-omp_target`). The other 3 copies have all 8. [VERIFIED: read the actual file]
**Why it happens:** The file was written before HeCBench KNOWN_FAIL specs were identified.
**How to avoid:** Centralization (D-07/D-08) fixes this automatically -- just replace with import.
**Warning signs:** After centralization, `token_analysis.py` will exclude 2 more specs than before.

### Pitfall 2: Integration Tests Are Slow (GPU Compilation)
**What goes wrong:** Each `build_spec()` call compiles real CUDA/OpenMP code. CUDA builds take 10-30 seconds. 5 specs x (build + run + verify) could take 2-3 minutes total.
**Why it happens:** Real compilation is the point of integration tests, but it's slow.
**How to avoid:** Mark as `@pytest.mark.integration`, document expected run time. The conftest auto-skip protects CI. Consider adding `@pytest.mark.timeout(120)` per test. [ASSUMED: based on XSBench build times from known-issues-archive.md]
**Warning signs:** Tests timing out on first run -- increase timeout if needed.

### Pitfall 3: analyze_harness_batch.py Must Create Output Directories
**What goes wrong:** `results/harness/{suite}/` does not exist yet. Writing JSON/MD there will fail with `FileNotFoundError`.
**Why it happens:** New output namespace (D-11).
**How to avoid:** `output_dir.mkdir(parents=True, exist_ok=True)` before writing.
**Warning signs:** First run of the new script fails immediately.

### Pitfall 4: quantitative_findings.py Is ~3085 Lines -- Surgical Edits Only
**What goes wrong:** The file is very large. The Rodinia-specific counter is at lines ~3064-3068 (spot-check 5, lines ~3085-3089). Changing the wrong counter variable or misidentifying the scope causes paper data generation to break.
**Why it happens:** Tight coupling between counter variables and spot-check assertions downstream.
**How to avoid:** Read the full spot-check block (lines ~3050-3090) before editing. The `rodinia_c1_total` and `rodinia_c1_pass` variables feed into spot-check 5 (`rodinia_c1_pass_count`). Replace with a `suite_c1_counts` dict and update the spot-check to use the dict. [VERIFIED: quantitative_findings.py lines 3064-3089]
**Warning signs:** `python3 scripts/analysis/quantitative_findings.py` crashes or spot-checks fail after edit.

### Pitfall 5: classify_translation_pairs.py Rodinia Filter Is Print-Only
**What goes wrong:** The Rodinia-only section (lines ~165-184) is purely a print/display block, not a data filter. Adding `--suite` needs to affect the filter on line 167 (`r["suite"] == "rodinia"`), not just add a new CLI flag. [VERIFIED: classify_translation_pairs.py lines 165-184]
**Why it happens:** The section header says "By Direction (Rodinia)" but it's just a filter in the display loop.
**How to avoid:** Make the `--suite` flag filter the `rows` list before the "By Direction" section. Default: all suites combined.

### Pitfall 6: Campaign Test Import Will Fail Until Phase 2
**What goes wrong:** `from scripts.evaluation.campaign_utils import campaign_for` will raise `ModuleNotFoundError` because `campaign_utils.py` doesn't exist yet.
**Why it happens:** TDD pattern -- tests written before implementation.
**How to avoid:** The `@pytest.mark.skip` decorator (D-16) prevents the test from running. However, the import at module top-level will still fail during test collection. Use `importlib` or put the import inside the test function body, guarded by the skip. [VERIFIED: this is a real issue -- pytest collects test files by importing them]
**Warning signs:** `pytest tests/test_campaign_classification.py` fails with ImportError even though tests are skipped.

## Code Examples

### Full Pipeline Test (verified pattern from harness/cli.py)
```python
# Source: harness/cli.py cmd_verify() lines 116-160
from harness.builder import build_spec
from harness.runner import run_spec
from harness.verifier import verify_run
from harness.models import Status
from harness.spec_loader import load_spec

spec = load_spec(Path("specs/rodinia-bfs-cuda.json"))
project_root = Path("/home/samyak/Desktop/parbench_sam")

build_result = build_spec(spec, project_root, verbose=True)
# build_result.status: Status.PASS/FAIL/ERROR/TIMEOUT
# build_result.stderr: str (error details)

run_result = run_spec(spec, project_root, configuration="correctness", verbose=True)
# run_result.status: Status.PASS/FAIL/ERROR/TIMEOUT
# run_result.exit_code: int
# run_result.stdout: str

ver_result = verify_run(spec, run_result)
# ver_result.status: Status.PASS/FAIL/SKIP
# ver_result.details: str
```

### Campaign Classification TDD (from D-16 through D-20)
```python
# Source: CONTEXT.md decisions D-16 through D-20
import pytest

# Must handle ImportError gracefully during collection
try:
    from scripts.evaluation.campaign_utils import campaign_for
except ImportError:
    campaign_for = None

@pytest.mark.skip(reason="campaign_for() not yet implemented -- Phase 2")
def test_c1_classification():
    result = campaign_for({"temperature": 0.0, "sample_id": None})
    assert result == "c1"

@pytest.mark.skip(reason="campaign_for() not yet implemented -- Phase 2")
def test_c2_classification():
    result = campaign_for({"temperature": 0.7, "sample_id": "s1"})
    assert result == "c2"
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 4 duplicate EXCLUDED_SPECS frozensets | Single import from harness.constants | Phase 1 (now) | token_analysis.py gains 2 missing HeCBench entries |
| Rodinia-only batch analyzer | Suite-agnostic analyze_harness_batch.py | Phase 1 (now) | All 5 suites can be analyzed identically |
| Manual smoke tests (known-issues-archive.md) | pytest integration tests | Phase 1 (now) | Reproducible, automated verification |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` [tool.pytest.ini_options] |
| Quick run command | `python3 -m pytest tests/ -m "not integration" -x -q` |
| Full suite command | `python3 -m pytest tests/ -v` |

### Phase Requirements to Test Map
| Behavior | Test Type | Automated Command | File Exists? |
|----------|-----------|-------------------|-------------|
| Spec loading all 5 suites | integration | `pytest tests/test_spec_loader_integration.py -v` | Yes (185 tests) |
| Build/run/verify per suite | integration | `pytest tests/test_harness_integration.py -v -m integration` | No -- Wave 0 |
| EXCLUDED_SPECS centralized | unit | `pytest tests/test_harness_integration.py -k excluded` | No -- Wave 0 |
| Campaign classification TDD | unit (skipped) | `pytest tests/test_campaign_classification.py -v` | No -- Wave 0 |
| analyze_harness_batch works | manual/smoke | `python3 scripts/analysis/analyze_harness_batch.py --suite rodinia` | No -- Wave 0 |
| quantitative_findings generalized | manual | `python3 scripts/analysis/quantitative_findings.py --help` | Existing file |

### Wave 0 Gaps
- [ ] `tests/test_harness_integration.py` -- build/run/verify integration tests
- [ ] `tests/test_campaign_classification.py` -- TDD stubs for Phase 2
- [ ] `harness/constants.py` -- EXCLUDED_SPECS constant (unblocks test imports)

## Assumptions Log

> List all claims tagged [ASSUMED] in this research.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | argparse is the right CLI framework for analyze_harness_batch.py (follows existing pattern) | Standard Stack | LOW -- click would also work, user left this to discretion |
| A2 | Integration tests will take 2-3 minutes total for 5 suite specs | Common Pitfalls | LOW -- if slower, increase timeout; if faster, no action needed |

**If this table is empty:** N/A -- 2 assumptions listed above.

## Open Questions

1. **Import strategy for campaign_for TDD tests**
   - What we know: `campaign_utils.py` won't exist until Phase 2. The import will fail at collection time.
   - What's unclear: Whether `pytest.importorskip` or a try/except at module level is the cleaner pattern.
   - Recommendation: Use try/except with `campaign_for = None` fallback (shown in Code Examples). The `@pytest.mark.skip` prevents actual execution. This is standard pytest TDD practice.

2. **EXCLUDED_SPECS sync test**
   - What we know: D-09 says `harness/constants.py` and `known-issues.md` must stay in sync.
   - What's unclear: Whether to write an automated test that parses `known-issues.md` and compares to the frozenset.
   - Recommendation: Add a comment in `constants.py` pointing to `known-issues.md`. An automated sync test is overkill for 8 items -- the planner can decide.

## Sources

### Primary (HIGH confidence)
- `harness/cli.py` lines 116-160 -- cmd_verify() pattern for full pipeline [VERIFIED: Read tool]
- `harness/builder.py` lines 50-79 -- build_spec() signature [VERIFIED: Read tool]
- `harness/runner.py` lines 54-84 -- run_spec() signature [VERIFIED: Read tool]
- `harness/verifier.py` lines 14-50 -- verify_run() signature [VERIFIED: Read tool]
- `harness/models.py` -- Status enum, BuildResult, RunResult, VerificationResult [VERIFIED: Read tool]
- `tests/conftest.py` -- integration mark auto-skip mechanism [VERIFIED: Read tool]
- `tests/test_spec_loader_integration.py` lines 34-53 -- SUITE_SPECS dict and fixture pattern [VERIFIED: Read tool]
- `scripts/evaluation/analyze_eval.py` lines 49-58 -- EXCLUDED_SPECS copy 1 (8 entries) [VERIFIED: Read tool]
- `scripts/analysis/quantitative_findings.py` lines 51-60 -- EXCLUDED_SPECS copy 2 (8 entries) [VERIFIED: Read tool]
- `scripts/analysis/generate_paper_data.py` lines 43-52 -- EXCLUDED_SPECS copy 3 (8 entries) [VERIFIED: Read tool]
- `scripts/analysis/token_analysis.py` lines 45-52 -- EXCLUDED_SPECS copy 4 (ONLY 6 entries -- missing HeCBench!) [VERIFIED: Read tool]
- `scripts/analysis/classify_translation_pairs.py` lines 165-184 -- Rodinia-only direction breakdown [VERIFIED: Read tool]
- `scripts/analysis/quantitative_findings.py` lines 3064-3089 -- Rodinia-specific counters [VERIFIED: Read tool]
- `scripts/analysis/analyze_rodinia_batch.py` -- Full file, suite-specific batch analyzer to replace [VERIFIED: Read tool]
- `pyproject.toml` -- pytest markers, package config [VERIFIED: Read tool]

### Secondary (MEDIUM confidence)
- `.planning/phases/01-pipeline-testing-uniformity/01-CONTEXT.md` -- All D-01 through D-20 decisions [VERIFIED: Read tool]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- no new libraries, all existing code verified via Read tool
- Architecture: HIGH -- all patterns derived from existing codebase, not assumed
- Pitfalls: HIGH -- each pitfall verified against actual file contents with line numbers

**Research date:** 2026-04-10
**Valid until:** 2026-05-10 (stable internal codebase, no external dependency churn)
