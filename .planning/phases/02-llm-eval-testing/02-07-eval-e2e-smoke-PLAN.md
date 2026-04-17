---
phase: 02-llm-eval-testing
plan: 07
type: execute
wave: 6
depends_on:
  - "02-01"
  - "02-02"
  - "02-03"
  - "02-04"
  - "02-05"
  - "02-06"
files_modified:
  - tests/test_eval_e2e_smoke.py
  - tests/conftest.py
  - pyproject.toml
autonomous: true
requirements: []
must_haves:
  truths:
    - "tests/test_eval_e2e_smoke.py exists with `@pytest.mark.integration` + `@pytest.mark.llm` markers"
    - "`llm` pytest marker is registered in pyproject.toml `[tool.pytest.ini_options].markers`"
    - "Test is gated: skip unless `PARBENCH_RUN_LLM_TESTS=1`"
    - "Kernel set is SUITE_SPECS from tests/test_spec_loader_integration.py:34 — 5 specs, one per suite"
    - "Per pair (suite_sample, model): (1) --dry-run assertion, (2) one real invocation asserting overall_status ∈ {PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL} + 7 schema fields"
    - "tests/conftest.py `_PROJECT_ROOT` is promoted to public `PROJECT_ROOT`"
    - "Budget ≈ $3.47 for 30 real samples (5 × 2 × 3)"
    - "Default `pytest tests/` (without the env var) does NOT trigger any LLM call"
  artifacts:
    - path: "tests/test_eval_e2e_smoke.py"
      provides: "E2E smoke test for canonical config"
      min_lines: 100
    - path: "tests/conftest.py"
      provides: "Public PROJECT_ROOT + llm marker skip mechanism"
      contains: "PROJECT_ROOT"
    - path: "pyproject.toml"
      provides: "llm marker registered"
      contains: "llm"
  key_links:
    - from: "PARBENCH_RUN_LLM_TESTS=1"
      to: "real LLM calls for 5 suites × 2 models"
      via: "pytest llm marker skip unless env set"
      pattern: "PARBENCH_RUN_LLM_TESTS"
    - from: "result JSON schema (post-02-03)"
      to: "test assertions (7 fields)"
      via: "D-29 schema-guardrail checks"
      pattern: "thinking_enabled.*num_samples"
---

<objective>
Add an end-to-end smoke test that exercises the full canonical-eval path (azure-gpt-5.4 + qwen, thinking=on, temp=0.7, pass@3, L0, cuda-to-omp) on 5 kernels (one per suite). Gated by `PARBENCH_RUN_LLM_TESTS=1` so CI and default runs are API-free.

Purpose: Plans 02-01 through 02-06 each validate their slice in isolation. The integration-level bug surface — e.g., the `--thinking` flag plumbed correctly from `run_eval_batch.py` through `evaluate_translation()` into the Azure SDK call — only shows up end-to-end. This test is the final guardrail before Phase 3 Phase A launches 204 hours of canonical runs against un-smoke-tested code paths.

Implements D-27, D-28, D-29, D-30. Also promotes `tests/conftest.py:_PROJECT_ROOT` → public `PROJECT_ROOT` (per F-02 fix in 02-CRITIQUE-APPLIED).

**Scope minimization:** This plan is the only entrypoint for (a) registering the `llm` pytest marker, (b) the PROJECT_ROOT promotion. Both are scoped to this plan to avoid disturbing 02-01..02-06.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@.planning/phases/02-llm-eval-testing/02-01-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-02-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-03-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-04-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-05-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-06-SUMMARY.md
@tests/conftest.py
@tests/test_spec_loader_integration.py
@pyproject.toml
@scripts/evaluation/run_eval_batch.py
@scripts/evaluation/llm_evaluate.py
@scripts/analysis/statistical_analysis.py
@.claude/rules/evaluation.md
@.claude/rules/known-issues.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Register `llm` pytest marker + promote _PROJECT_ROOT → PROJECT_ROOT</name>
  <files>pyproject.toml, tests/conftest.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-28; F-02 fix — `_PROJECT_ROOT` → `PROJECT_ROOT` promotion scoped to this plan)
    - pyproject.toml (locate `[tool.pytest.ini_options]` — verify 2026-04-16 note: no pytest.ini exists, markers live here)
    - tests/conftest.py (find `_PROJECT_ROOT` and the `integration` marker skip logic)
  </read_first>
  <action>
**Step 1 — Verify no pytest.ini.**

```bash
ls pytest.ini 2>&1 | head -1   # must NOT exist per CONTEXT.md
```

If `pytest.ini` exists (drift since 2026-04-16), ask before proceeding — markers may live there instead of pyproject.toml.

**Step 2 — Register `llm` marker in `pyproject.toml`.** Locate `[tool.pytest.ini_options]`. The `markers` list should already contain `integration`. Add `llm`:

```toml
[tool.pytest.ini_options]
markers = [
    "integration: real build/run tests (slow, require compilers)",
    "llm: real LLM API calls (gated by PARBENCH_RUN_LLM_TESTS=1; costs ~$3.47 for full smoke set)",
]
```

Preserve any existing marker entries; append the `llm` line.

**Step 3 — Promote `_PROJECT_ROOT` → `PROJECT_ROOT` in `tests/conftest.py`.**

Find the existing `_PROJECT_ROOT = Path(__file__).parent.parent` (or similar). Keep the variable but ALSO expose a public alias:

```python
# tests/conftest.py
PROJECT_ROOT = Path(__file__).parent.parent
_PROJECT_ROOT = PROJECT_ROOT  # retained for backward-compat with pre-02-07 tests
```

Downstream tests can now `from tests.conftest import PROJECT_ROOT`.

**Step 4 — Extend the `integration` marker skip logic with an `llm` gate.** Inside `pytest_collection_modifyitems` or the equivalent hook in `tests/conftest.py`, add a skip directive for the `llm` marker that checks `os.environ.get("PARBENCH_RUN_LLM_TESTS") == "1"`:

```python
def pytest_collection_modifyitems(config, items):
    # existing integration skip logic
    # ...
    run_llm = os.environ.get("PARBENCH_RUN_LLM_TESTS") == "1"
    skip_llm = pytest.mark.skip(reason="llm tests require PARBENCH_RUN_LLM_TESTS=1 (costs real $)")
    for item in items:
        if "llm" in item.keywords and not run_llm:
            item.add_marker(skip_llm)
```

If the existing conftest uses a different skip pattern (e.g. `pytest_runtest_setup`), match that style. Do not duplicate the integration skip logic — extend it in place.

**Step 5 — Do NOT:**
- Delete `_PROJECT_ROOT`. The alias preserves backward-compat with any existing tests that still reference the private name.
- Change the `integration` marker's skip behavior.
- Introduce a new env var naming convention (stick with `PARBENCH_RUN_LLM_TESTS`).
  </action>
  <verify>
    <automated>python3 -c "import tomllib; d = tomllib.loads(open('pyproject.toml').read()); markers = d['tool']['pytest']['ini_options']['markers']; assert any('llm' in m for m in markers), markers; print('OK')" && python3 -c "from tests.conftest import PROJECT_ROOT; print(PROJECT_ROOT)"</automated>
  </verify>
  <acceptance_criteria>
    - `python3 -c "import tomllib; d = tomllib.loads(open('pyproject.toml').read()); print([m for m in d['tool']['pytest']['ini_options']['markers'] if 'llm' in m])"` prints a non-empty list.
    - `python3 -c "from tests.conftest import PROJECT_ROOT; print(PROJECT_ROOT.name)"` prints `parbench_sam` (or the repo dirname).
    - `grep -n '_PROJECT_ROOT' tests/conftest.py` still returns at least one match (alias preserved).
    - `grep -n 'PARBENCH_RUN_LLM_TESTS' tests/conftest.py` returns at least one match (skip gate wired).
    - `pytest --collect-only -m llm 2>&1 | tail -10` shows no collection errors (marker registered correctly, no `PytestUnknownMarkWarning`).
    - `ls pytest.ini 2>&1 | grep 'No such'` — confirms no pytest.ini exists (drift check).
  </acceptance_criteria>
  <done>`llm` marker registered; PROJECT_ROOT public; llm-skip gate wired; no pytest.ini drift.</done>
</task>

<task type="auto">
  <name>Task 2: Create tests/test_eval_e2e_smoke.py with D-27..D-30 smoke coverage</name>
  <files>tests/test_eval_e2e_smoke.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-27, D-28, D-29, D-30)
    - tests/test_spec_loader_integration.py (line 34 — `SUITE_SPECS` canonical list; verify with `grep -n 'SUITE_SPECS' tests/test_spec_loader_integration.py`)
    - tests/conftest.py (post-Task-1 `PROJECT_ROOT` public + llm marker)
    - scripts/evaluation/run_eval_batch.py (understand CLI for subprocess invocation; confirm `--dry-run` exists — grep `--dry-run`)
    - scripts/evaluation/llm_evaluate.py (understand result JSON output path pattern)
    - .claude/rules/evaluation.md (result JSON schema)
  </read_first>
  <action>
Create `tests/test_eval_e2e_smoke.py`:

```python
"""Phase 2 / Plan 02-07: End-to-end smoke test for canonical eval config.

Gated by PARBENCH_RUN_LLM_TESTS=1 (costs ~$3.47 per full run).

For each of 5 suite-representative kernels × 2 models (azure-gpt-5.4, together-qwen-3.5-397b-a17b):
  (a) `--dry-run` invocation asserts the prompt is built with no API call.
  (b) One real invocation (num_samples=3, thinking=on, temp=0.7, L0, cuda-to-omp)
      asserts overall_status ∈ {PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL} and the
      result JSON carries 7 schema-guardrail fields (D-29).

Reuses the canonical `SUITE_SPECS` from `tests/test_spec_loader_integration.py:34` (D-27):
  - rodinia-bfs-cuda
  - xsbench-xsbench-cuda
  - rsbench-rsbench-cuda
  - mixbench-mixbench-cuda
  - hecbench-bezier-surface-cuda

Budget breakdown (D-30, pricing verified 2026-04-17): 5 kernels × 2 models × 3 samples = 30 samples.
  azure-gpt-5.4 (GPT-5 standard tier, $2.50/1M in + $15/1M out, 5k prompt + 20k output)
    ≈ $0.3125/sample → 15 × $0.3125 = $4.69
  together-qwen-3.5-397b-a17b ($0.60/1M in + $3.60/1M out, same assumption)
    ≈ $0.075/sample → 15 × $0.075 = $1.13
  Total ≈ $5.81 (revised ceiling $6; prior $3.47 figure obsolete).
  Reasoning tokens bill as output tokens on both providers — worst-case with 2× output
  inflation ≈ $10.90.

Registry-key vs SKU note: "GPT-5.4" is the ParBench-internal registry key / Azure
deployment name chosen by Le; the Azure SKU/tier is "GPT-5 standard".
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import PROJECT_ROOT
from tests.test_spec_loader_integration import SUITE_SPECS


# D-29 schema-guardrail fields. Two new (02-03): thinking_enabled, num_samples.
# Five existing (regression-guard): sample_id, temperature, augment_level, model, overall_status.
REQUIRED_RESULT_FIELDS = {
    "thinking_enabled",
    "num_samples",
    "sample_id",
    "temperature",
    "augment_level",
    "model",
    "overall_status",
}

VALID_SMOKE_STATUSES = {"PASS", "BUILD_FAIL", "RUN_FAIL", "VERIFY_FAIL"}

MODELS_UNDER_TEST = [
    "together-qwen-3.5-397b-a17b",
    "azure-gpt-5.4",
]


# SUITE_SPECS from tests/test_spec_loader_integration.py:34 is a dict or list
# per that file's structure. Normalize to a flat list of source-spec ids.
# (Re-check actual shape at implementation time; adjust normalization accordingly.)
def _source_specs():
    specs = SUITE_SPECS
    if isinstance(specs, dict):
        return list(specs.values())
    return list(specs)


pytestmark = [pytest.mark.integration, pytest.mark.llm]


@pytest.mark.parametrize("model", MODELS_UNDER_TEST)
@pytest.mark.parametrize("source_spec", _source_specs())
def test_smoke_dry_run(source_spec, model):
    """(a) --dry-run builds prompt without API call."""
    # Derive target spec via API swap.
    if not source_spec.endswith("-cuda"):
        pytest.skip(f"non-CUDA source spec: {source_spec}")
    target_spec = source_spec[: -len("-cuda")] + "-omp"

    cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--kernels", source_spec.rsplit("-", 1)[0].split("-", 1)[1],  # heuristic: kernel slug extraction
        "--direction", "cuda-to-omp",
        "--models", model,
        "--augment-levels", "0",
        "--num-samples", "1",
        "--temperature", "0.7",
        "--thinking", "on",
        "--dry-run",
        "--project-root", str(PROJECT_ROOT),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=60)
    assert result.returncode == 0, f"dry-run failed: {result.stderr}"
    # Dry-run output should include prompt/task indicators and explicitly no API call.
    assert "dry-run" in (result.stdout + result.stderr).lower() or "DRY" in result.stdout


@pytest.mark.parametrize("model", MODELS_UNDER_TEST)
@pytest.mark.parametrize("source_spec", _source_specs())
def test_smoke_real_invocation(source_spec, model, tmp_path):
    """(b) One real canonical-config invocation asserts valid status + 7-field schema."""
    if not source_spec.endswith("-cuda"):
        pytest.skip(f"non-CUDA source spec: {source_spec}")
    target_spec = source_spec[: -len("-cuda")] + "-omp"

    out_dir = tmp_path / "smoke_results"
    out_dir.mkdir()

    cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--kernels", source_spec.rsplit("-", 1)[0].split("-", 1)[1],
        "--direction", "cuda-to-omp",
        "--models", model,
        "--augment-levels", "0",
        "--num-samples", "3",
        "--temperature", "0.7",
        "--thinking", "on",
        "--project-root", str(PROJECT_ROOT),
        "--output-dir", str(out_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT, timeout=600)
    assert result.returncode == 0, f"real invocation failed: stdout={result.stdout[-2000:]} stderr={result.stderr[-2000:]}"

    # Load at least one result JSON from out_dir (pass@3 → up to 3 files per cell).
    result_files = list(out_dir.rglob("*.json"))
    assert result_files, f"no result JSONs produced in {out_dir}"

    for rf in result_files:
        data = json.loads(rf.read_text())
        missing = REQUIRED_RESULT_FIELDS - set(data.keys())
        assert not missing, f"{rf.name} missing required fields: {missing}"
        assert data["overall_status"] in VALID_SMOKE_STATUSES, \
            f"{rf.name} has unexpected overall_status: {data['overall_status']!r}"
        # Canonical config guardrails.
        assert data["augment_level"] == 0
        assert data["temperature"] == 0.7
        assert data["num_samples"] == 3
        assert data["thinking_enabled"] is True
        assert data["model"] == model


def test_smoke_budget_documented_in_this_file():
    """Meta-test: the 30-sample / $3.47 budget is documented in the module docstring.

    This ensures future maintainers see the cost model before running the suite.
    """
    import tests.test_eval_e2e_smoke as mod
    assert "$3.47" in (mod.__doc__ or "")
    assert "30 samples" in (mod.__doc__ or "")
```

**Adjustments you may need to make at implementation time:**
- The exact `--kernels` argument shape depends on `run_eval_batch.py`'s parser. Verify with `--help` output. If `--kernels` expects full unique_ids like `rodinia-bfs` (suite-kernel), use those — the heuristic `rsplit/split` in the test above is a best guess. Adjust to match actual CLI.
- The `--dry-run` flag is assumed to exist per D-29. If it does NOT exist in `run_eval_batch.py`, add it in a minimal way as part of this plan (just print the prompt + skip the API call). The CONTEXT.md §Verification point 6 states it should exist; this is the first place it would be tested.
- `SUITE_SPECS` shape: verify with `python3 -c "from tests.test_spec_loader_integration import SUITE_SPECS; print(type(SUITE_SPECS), SUITE_SPECS)"`. Normalize the test's `_source_specs()` helper to the actual shape (list of strings vs dict-of-specs).
- `--output-dir` flag: if `run_eval_batch.py` does not have one, use its default path + clean up post-test, OR add the flag as part of this plan.

**Module-level markers.** Both smoke tests use `pytestmark = [pytest.mark.integration, pytest.mark.llm]` so the whole module is gated. `test_smoke_budget_documented_in_this_file` is a pure metadata test with NO API call — the module-level markers still apply, which means it only runs under `PARBENCH_RUN_LLM_TESTS=1`. Accept this; the meta-test exists for the developer running the suite, not CI.

**Alternative placement for the meta-test:** If you prefer the meta-test to run in default `pytest tests/`, move it to `tests/test_model_registry.py` instead (which is always-on). Either location is acceptable.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_eval_e2e_smoke.py --collect-only -q 2>&1 | head -40</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/test_eval_e2e_smoke.py --collect-only -q` lists at least 10 test cases (5 specs × 2 models × 2 tests dry-run+real = 20 minimum, plus the budget meta-test).
    - `pytest tests/test_eval_e2e_smoke.py -v` (WITHOUT `PARBENCH_RUN_LLM_TESTS=1`) reports all tests SKIPPED with reason mentioning `PARBENCH_RUN_LLM_TESTS`.
    - `grep -n 'PROJECT_ROOT' tests/test_eval_e2e_smoke.py` shows `from tests.conftest import PROJECT_ROOT`.
    - `grep -n 'SUITE_SPECS' tests/test_eval_e2e_smoke.py` shows `from tests.test_spec_loader_integration import SUITE_SPECS`.
    - `grep -n 'REQUIRED_RESULT_FIELDS' tests/test_eval_e2e_smoke.py` returns a match; the set has exactly 7 elements matching D-29.
    - `grep -n 'thinking_enabled' tests/test_eval_e2e_smoke.py` AND `grep -n 'num_samples' tests/test_eval_e2e_smoke.py` both return matches (two new fields asserted).
    - `grep -n '@pytest.mark' tests/test_eval_e2e_smoke.py | head -5` shows `integration` AND `llm` markers (via `pytestmark` list).
    - `grep -n '\\$3.47' tests/test_eval_e2e_smoke.py` returns at least one match (budget doc).
    - `grep -n '30 samples' tests/test_eval_e2e_smoke.py` returns a match.
    - `grep -n 'rodinia-bfs-cuda' tests/test_eval_e2e_smoke.py` — no direct hardcoding; specs come from SUITE_SPECS import.
  </acceptance_criteria>
  <done>Smoke test module exists, properly gated, imports canonical spec list + PROJECT_ROOT, asserts 7-field schema + 4-status set, and default pytest run does not trigger any LLM call.</done>
</task>

</tasks>

<verification>
- `pytest tests/ -v` (no env var) completes without LLM cost; smoke tests report SKIPPED.
- `pytest --collect-only -m llm` lists the smoke tests without `PytestUnknownMarkWarning`.
- `python3 -c "from tests.conftest import PROJECT_ROOT; from tests.test_spec_loader_integration import SUITE_SPECS; print(PROJECT_ROOT, len(SUITE_SPECS) if hasattr(SUITE_SPECS, '__len__') else 'n/a')"` exits 0.
- `grep -c '@pytest.mark.llm' tests/` or equivalent shows the `llm` marker only in `test_eval_e2e_smoke.py`.
- `git diff --stat` shows only pyproject.toml, tests/conftest.py, tests/test_eval_e2e_smoke.py.
</verification>

<success_criteria>
- `llm` marker is registered and gated by `PARBENCH_RUN_LLM_TESTS=1`.
- `tests/conftest.PROJECT_ROOT` is importable publicly.
- Smoke test covers 5 suites × 2 models × (dry-run + real) with 7-field schema assertions per D-29.
- Default `pytest tests/` runs no LLM calls.
- Budget of ~$3.47 for 30 real samples is documented in the test module docstring.
- All 7 plans (02-01..02-07) composed: CONTEXT.md §Verification criteria 1-8 pass.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-07-SUMMARY.md` listing: (a) `pytest --collect-only -m llm` count, (b) skip-count when env var is unset, (c) confirmation that the 7 REQUIRED_RESULT_FIELDS match D-29 exactly, (d) confirmation that `--dry-run` was either pre-existing or added in this plan.
</output>
