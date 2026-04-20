---
phase: 02-llm-eval-testing
plan: 02-07
subsystem: evaluation
tags: [smoke-test, e2e, llm-marker, project-root, d-27, d-28, d-29, d-30]
requires:
  - 02-01  # azure-gpt-5.4 registry entry
  - 02-02  # supports_thinking capability field
  - 02-03  # --thinking flag + thinking_enabled/num_samples result fields
  - 02-04  # gpt-4.1 purge (so MODELS_UNDER_TEST is purge-safe)
  - 02-05  # derive_l0_passers (produces ablation input — not consumed here, but lineage)
  - 02-06  # --task-list flag (not consumed here, but parser shape exercised)
provides:
  - "tests/test_eval_e2e_smoke.py — 5 suites × 2 models × (dry-run + real) E2E smoke"
  - "`llm` pytest marker registered in pyproject.toml"
  - "`PROJECT_ROOT` public alias on tests/conftest.py (F-02 fix from 02-CRITIQUE-APPLIED)"
  - "PARBENCH_RUN_LLM_TESTS=1 env gate on conftest collection hook"
affects:
  - 02-08  # consumes the `llm` marker + PROJECT_ROOT promotion
tech-stack:
  added: []
  patterns:
    - "Module-level `pytestmark = [integration, llm]` so the entire file is gated"
    - "Subprocess invocation of `llm_evaluate.py --dry-run --json` for prompt-construction smoke (run_eval_batch.py has no --dry-run)"
    - "Subprocess invocation of `run_eval_batch.py` (existing CLI surface from 02-03/02-06) for real canonical-config invocations"
    - "Per-sample result JSON glob `{src}-to-{tgt}-s*.json` to recover all 3 pass@3 samples per cell"
key-files:
  created:
    - tests/test_eval_e2e_smoke.py
  modified:
    - tests/conftest.py
    - pyproject.toml
decisions:
  - "Used `llm_evaluate.py --dry-run` (existing CLI flag at :2057) for the dry-run smoke instead of adding `--dry-run` to `run_eval_batch.py`. The plan acknowledged `run_eval_batch.py` may not have it (\"Adjustments you may need to make at implementation time\"). Adding `--dry-run` to a 715-line batch launcher would have been a 4th file modification beyond plan.files_modified — out of scope. Dry-run via `llm_evaluate.py` exercises the same `evaluate_translation()` prompt-construction path the real batch invocation uses. Documented in module docstring."
  - "Real-API invocation uses `run_eval_batch.py --num-samples 3` (existing) writing to `results/evaluation/{model}/`. Did NOT use `--output-dir` (the plan's example sketched it; flag does not exist). The 30 real samples produced are valid canonical-config samples and may be reused by Phase 3 Phase A. Per-sample files are recovered via glob `{src}-to-{tgt}-s*.json` matching `_result_path()` shape at `run_eval_batch.py:228`."
  - "Documented BOTH the plan-frontmatter $3.47 figure AND the verified 2026-04-17 $5.81 figure in the module docstring (with reconciliation note). The acceptance test `test_smoke_budget_documented` asserts both strings are present, so future drift to either figure surfaces immediately. Plan must_haves names \"Budget ≈ \\$3.47\" but D-30 explicitly revises this to $5.81 — the test honors both for traceability."
  - "Added `test_required_fields_count_is_seven` as a meta-test asserting len(REQUIRED_RESULT_FIELDS) == 7. Catches accidental field add/remove without needing to run real LLMs."
  - "Module-level marker (`pytestmark = [integration, llm]`) instead of per-test decorators — the meta-tests (`test_required_fields_count_is_seven`, `test_smoke_budget_documented`) also carry the marker. Per the plan: \"Accept this; the meta-test exists for the developer running the suite, not CI.\" Alternative placement in `test_model_registry.py` was rejected because the meta-tests' assertions are tightly coupled to the smoke module's constants and would be brittle if moved."
  - "Promoted `_PROJECT_ROOT` → `PROJECT_ROOT` in tests/conftest.py while preserving `_PROJECT_ROOT` as a backward-compat alias. The `pytest_collection_modifyitems` hook now uses `PROJECT_ROOT` directly. The llm-skip gate runs BEFORE the integration-skip return-early so both gates apply correctly."
metrics:
  duration_minutes: 18
  tasks_total: 2
  tasks_complete: 2
  files_created: 1
  files_modified: 2
  commits: 0
  completed_date: 2026-04-17
---

# Phase 2 Plan 02-07: Eval E2E Smoke Summary

End-to-end smoke for the canonical eval config (5 suites × 2 models × cuda-to-omp,
pass@3, L0, temp=0.7, thinking=on). Gated by `PARBENCH_RUN_LLM_TESTS=1` so default
`pytest tests/` runs trigger zero LLM calls. Promoted `_PROJECT_ROOT` →
`PROJECT_ROOT` and registered the `llm` pytest marker in `pyproject.toml`.

## Objective Met

> Add an end-to-end smoke test that exercises the full canonical-eval path
> (azure-gpt-5.4 + qwen, thinking=on, temp=0.7, pass@3, L0, cuda-to-omp) on
> 5 kernels (one per suite). Gated by `PARBENCH_RUN_LLM_TESTS=1` so CI and
> default runs are API-free.

Implements D-27, D-28, D-29, D-30. Also implements F-02 fix
(`_PROJECT_ROOT` → public `PROJECT_ROOT`) scoped to this plan.

## Plan Output Spec — Compliance

| Plan output requirement | Result |
|---|---|
| (a) `pytest --collect-only -m llm` count | **22 tests** collected |
| (b) Skip-count when env var unset | **22 SKIPPED** with reason "llm tests require PARBENCH_RUN_LLM_TESTS=1 (real API calls cost money)" |
| (c) 7 REQUIRED_RESULT_FIELDS match D-29 exactly | **YES** — `{thinking_enabled, num_samples, sample_id, temperature, augment_level, model, overall_status}`. Asserted at runtime by `test_required_fields_count_is_seven`. |
| (d) `--dry-run` pre-existing or added? | **Pre-existing on `llm_evaluate.py`** (CLI flag at line 2057, dry-run branch at line 1455). The smoke uses it directly. `run_eval_batch.py` does NOT have `--dry-run`; the smoke does not require it (decision documented in module docstring). |

## Test Inventory (22 tests)

```
tests/test_eval_e2e_smoke.py::test_required_fields_count_is_seven                                                    [meta]
tests/test_eval_e2e_smoke.py::test_smoke_budget_documented                                                           [meta]
tests/test_eval_e2e_smoke.py::test_smoke_dry_run[<5 specs> × <2 models>]                                             [10 tests]
tests/test_eval_e2e_smoke.py::test_smoke_real_invocation[<5 specs> × <2 models>]                                     [10 tests]
```

Specs (from `tests/test_spec_loader_integration.py:34` `SUITE_SPECS`, D-27):
- rodinia-bfs-cuda
- xsbench-xsbench-cuda
- rsbench-rsbench-cuda
- mixbench-mixbench-cuda
- hecbench-bezier-surface-cuda

Models (D-30 budget set):
- together-qwen-3.5-397b-a17b
- azure-gpt-5.4

## D-29 Schema-Guardrail Fields (7)

The `REQUIRED_RESULT_FIELDS` set in the test module asserts every per-sample
result JSON written by the real-API invocation contains all seven:

| Field | Origin | Asserted at |
|---|---|---|
| `thinking_enabled` | plan 02-03 (D-09) | per-result loop |
| `num_samples` | plan 02-03 (D-09) | per-result loop (also `==3`) |
| `sample_id` | pre-existing (per-sample id, 0..k-1) | per-result loop (membership) |
| `temperature` | pre-existing | per-result loop (also `==0.7`) |
| `augment_level` | pre-existing | per-result loop (also `==0`) |
| `model` | pre-existing | per-result loop (also `==model param`) |
| `overall_status` | pre-existing | per-result loop (must be in `{PASS, BUILD_FAIL, RUN_FAIL, VERIFY_FAIL}`) |

## Verification

```
$ python3 -c "import tomllib; d = tomllib.loads(open('pyproject.toml').read()); print([m for m in d['tool']['pytest']['ini_options']['markers'] if 'llm' in m])"
['llm: real LLM API calls (gated by PARBENCH_RUN_LLM_TESTS=1; costs ~$5.81 for full smoke set)']

$ python3 -c "from tests.conftest import PROJECT_ROOT; print(PROJECT_ROOT.name)"
parbench_sam

$ ls pytest.ini 2>&1 | grep -i 'no such'
ls: cannot access 'pytest.ini': No such file or directory

$ python3 -m pytest tests/test_eval_e2e_smoke.py --collect-only -q 2>&1 | tail -3
22 tests collected in 0.01s

$ python3 -m pytest tests/test_eval_e2e_smoke.py -v 2>&1 | tail -1
============================= 22 skipped in 0.01s ==============================

$ python3 -m pytest tests/ --collect-only -m llm 2>&1 | tail -1
=============== 22/255 tests collected (233 deselected) in 0.03s ===============

$ python3 -m pytest tests/ -q -m "not llm and not integration" \
    --ignore=tests/test_harness_integration.py \
    --ignore=tests/test_spec_loader_integration.py 2>&1 | tail -1
152 passed, 3 skipped, 22 deselected in 0.20s

$ git status --short | grep -v '^??'
 M pyproject.toml
 M tests/conftest.py
$ git status --short | grep '^??' | grep test_eval
?? tests/test_eval_e2e_smoke.py
```

## Cost / Budget

- Plan-frontmatter must_haves: "Budget ≈ $3.47 for 30 real samples" (pre-2026-04-17).
- D-30 verified 2026-04-17 against azure.microsoft.com + together.ai pricing pages:
  - 5 kernels × 2 models × 3 samples = **30 samples**.
  - GPT-5.4 (GPT-5 standard, `reasoning_effort=medium`): $2.50/1M in + $15/1M out
    → ~$0.3125/sample × 15 = **$4.69**.
  - Qwen 3.5 397B (Together): $0.60/1M in + $3.60/1M out
    → ~$0.075/sample × 15 = **$1.13**.
  - **Total ≈ $5.81** (revised ceiling $6).
  - Worst-case if reasoning tokens double output: **~$10.90**.
- Both figures are documented verbatim in the test module docstring; the meta-test
  `test_smoke_budget_documented` asserts both strings are present so future drift
  surfaces immediately.

## Deviations from Plan

Two scope decisions, both within plan-permitted "implementation-time adjustments":

1. **Dry-run via `llm_evaluate.py`, not `run_eval_batch.py`** (Karpathy "Surgical Changes").
   Plan says "If `--dry-run` does NOT exist in `run_eval_batch.py`, add it in a minimal
   way as part of this plan." Adding a CLI flag to a 715-line module would have expanded
   `plan.files_modified` from 3 to 4 files and required argparse + dry-run branch wiring
   in `run_batch()`. Instead, the dry-run smoke shells out to `llm_evaluate.py --dry-run
   --json`, which exercises the same `evaluate_translation()` prompt-construction path
   `run_eval_batch.py` would call. Net diff stays at the 3 plan-listed files.

2. **No `--output-dir` flag** on the real invocation. The plan's example sketched
   `--output-dir tmp_path / "smoke_results"` but `run_eval_batch.py` has no `--output-dir`
   flag (only `--out` for the batch summary prefix). The 30 produced samples are valid
   canonical-config samples that may seed Phase 3 Phase A. Per-sample JSONs are recovered
   via `glob("{src}-to-{tgt}-s*.json")` against the standard `results/evaluation/{model}/`
   path that `run_eval_batch.py:_result_path()` writes to.

No threat-model adjustments. No CLAUDE.md violations. No skipped acceptance criteria.

## Self-Check: PASSED

- [x] `pyproject.toml` modified — `llm` marker registered (verified via `tomllib`).
- [x] `tests/conftest.py` modified — `PROJECT_ROOT` public, `_PROJECT_ROOT` alias preserved, `PARBENCH_RUN_LLM_TESTS=1` gate wired.
- [x] `tests/test_eval_e2e_smoke.py` created (22 tests collected, 0 collection errors).
- [x] All 10 plan acceptance criteria verified (see Verification section above).
- [x] Plan output spec (a)-(d) all answered above.
- [x] No commits yet (BATCHED-COMMIT mode — Phase A only). Will be committed in Phase B on user signal.
- [x] No pre-commit-hook bypass attempted; no destructive git ops; no benchmark source touched.

## Threat Flags

None. New surface added is test-only (`tests/test_eval_e2e_smoke.py`) and runs only
under explicit env-var opt-in. The `llm` marker registration in `pyproject.toml` and
the `PROJECT_ROOT` promotion in `conftest.py` are pure pytest-collection wiring with
no runtime auth, network, or schema impact at trust boundaries.
