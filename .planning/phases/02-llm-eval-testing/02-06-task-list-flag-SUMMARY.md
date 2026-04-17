---
phase: 02-llm-eval-testing
plan: 02-06
subsystem: evaluation
tags: [task-list, run-eval-batch, mutex-group, ablation-launcher, d-23, d-24, d-25, d-26]
requires:
  - 02-03  # --thinking flag must coexist on the same parser
  - 02-05  # produces the passer-JSON consumed by --task-list
provides:
  - "scripts/evaluation/run_eval_batch.py --task-list <json> — bypasses manifest enumeration"
  - "argparse-native mutex group: --suite ⊥ --kernels ⊥ --task-list (D-23 LOCK)"
  - "_build_tasks_from_task_list(...) — pure fn for tests + downstream import"
  - "_build_parser() helper extracted from main() for testability"
  - "tests/test_run_eval_batch_task_list.py — 13 tests covering D-26 cases 1-4 + matrix expansion + JSON validation"
affects:
  - 02-07  # smoke test will exercise the new parser shape
  - 02-08  # ablation slice will use --task-list end-to-end
tech-stack:
  added: []
  patterns:
    - "argparse `add_mutually_exclusive_group(required=False)` for CLI-native mutex (D-23 LOCK — no parser.error fallback)"
    - "argparse parser construction extracted from main() into _build_parser() for unit-testable mutex"
    - "Manifest indexed by `unique_id` (suite-kernel-api) for O(1) skip-on-missing lookup"
key-files:
  created:
    - tests/test_run_eval_batch_task_list.py
  modified:
    - scripts/evaluation/run_eval_batch.py
decisions:
  - "Extracted `_build_parser()` from `main()`. Plan called this 'preferred for crisper test feedback' and the alternative was clean test-skip; chose extraction so all 13 tests run as real assertions, not skips. Pure refactor: zero behavior change in main()."
  - "`--task-list` uses `dest='task_list'` (snake_case) so `args.task_list` reads naturally; argparse default would be `args.task_list` anyway but spelled it out for clarity."
  - "`_build_tasks_from_task_list()` validates structure (FileNotFound → FileNotFoundError, malformed JSON → ValueError, non-list root → ValueError, missing source/target_spec keys → stderr-warn + skip). Per-entry malformed dicts skip with warning rather than abort the whole batch — same robustness pattern as `derive_l0_passers.py:_load_result()`."
  - "Added a direction-mismatch skip: if the passer JSON's source_spec parallel_api ≠ `--direction` source api (or target ≠ target), the entry is skipped with a warning. Defensive against feeding a Qwen-canonical passer file to an OpenCL ablation invocation by accident. Tested in test_task_list_skips_direction_mismatch."
  - "Added top-level `task_list` field to batch summary JSON (alongside existing `suite`/`kernels`) so downstream analysis can identify which passer file produced the batch. Set to `null` when --task-list was not used; otherwise the path string."
  - "Did NOT touch `_build_tasks()` (manifest enumeration). The new path is a sibling function called from `main()`; all 12 existing call sites of `_build_tasks` are unchanged. Surgical."
  - "Did NOT alter `--direction`'s `required=True` (D-24 preserved). Did NOT touch MODEL_REGISTRY or derive_l0_passers.py (out of scope)."
metrics:
  duration_minutes: 14
  tasks_total: 2
  tasks_complete: 2
  files_created: 1
  files_modified: 1
  commits: 0
  completed_date: 2026-04-17
---

# Phase 2 Plan 02-06: Task-List Flag Summary

Added `--task-list <json>` to `scripts/evaluation/run_eval_batch.py` so the Phase 3 ablation launcher (L1-L4 against pre-derived L0 passers) is a one-liner. Mutex with `--suite` and `--kernels` enforced via argparse-native `add_mutually_exclusive_group()` per the D-23 LOCK — no runtime `parser.error()` fallback. 13/13 tests pass.

## Objective Met

> Add a `--task-list <json>` argument to `run_eval_batch.py` that consumes the passer-JSON list produced by `derive_l0_passers.py` (plan 02-05) and runs only the listed cells, bypassing manifest enumeration.

Implements D-23, D-24, D-25, D-26.

## Mutex Group Contents

```
[--suite SUITE | --kernels KERNEL [...] | --task-list TASK_LIST]
```

Verified via `python3 scripts/evaluation/run_eval_batch.py --help` (exit 0):

```
usage: run_eval_batch.py [-h] [--suite SUITE | --kernels KERNEL [KERNEL ...] |
                         --task-list TASK_LIST] --direction SRC-to-TGT
                         --models MODEL [MODEL ...] ...
```

End-to-end CLI rejection (cuda-to-opencl direction, hook-friendly):
```
$ python3 scripts/evaluation/run_eval_batch.py \
    --task-list /tmp/fake_passers.json --suite rodinia \
    --direction cuda-to-opencl --models gpt-4o
run_eval_batch.py: error: argument --suite: not allowed with argument --task-list
$ echo $?
2
```

`--direction`, `--models` remain `required=True` outside the mutex group — they are mandatory for all three task-selection modes.

## `_build_parser` Extraction

**Yes** — extracted from `main()`. Behavior of `main()` is byte-equivalent (it now calls `parser = _build_parser()` then `parser.parse_args()`). The extraction enables 13 real test assertions instead of `pytest.skip` fallbacks. Zero downstream importers of this module's parser exist (verified via grep), so the API change is internal-only.

## Test Pass/Skip Count

`pytest tests/test_run_eval_batch_task_list.py -v` → **13 passed, 0 skipped, 0 failed** (0.03 s).

| # | Test | D-26 case | Asserts |
|---|------|-----------|---------|
| 1 | `test_parser_advertises_task_list_flag` | — | `--task-list` in `--help` |
| 2 | `test_task_list_mutex_with_kernels` | 3 | SystemExit code == 2 |
| 3 | `test_task_list_mutex_with_suite` | 3-ext | SystemExit code == 2 |
| 4 | `test_task_list_without_direction_fails` | 4 | SystemExit |
| 5 | `test_task_list_expands_by_augment_levels` | 1 | 2 passers × 4 levels = 8 tasks; task-dict shape matches `_build_tasks` contract |
| 6 | `test_task_list_expands_by_num_samples` | 1-ext | 2 × 4 × 3 = 24 tasks; sample_id ∈ {0,1,2} |
| 7 | `test_task_list_expands_by_models` | 1-ext | 2 × 1 × 1 × 2 models = 4 tasks |
| 8 | `test_task_list_skips_unknown_specs` | 2 | unknown specs skipped + stderr warning |
| 9 | `test_task_list_skips_direction_mismatch` | (added) | direction-API mismatch skipped + warning |
| 10 | `test_task_list_malformed_json_raises` | (robustness) | ValueError("not valid JSON") |
| 11 | `test_task_list_non_list_json_raises` | (robustness) | ValueError("must contain a JSON list") |
| 12 | `test_task_list_empty_list_returns_empty` | (robustness) | empty list → no tasks, no error |
| 13 | `test_task_list_missing_file_raises` | (robustness) | FileNotFoundError with path |

## Artifacts

| Path | Kind | Lines added |
|------|------|------|
| `scripts/evaluation/run_eval_batch.py` | modified | +130 (mostly `_build_tasks_from_task_list`) |
| `tests/test_run_eval_batch_task_list.py` | created | 268 |

## Verification

```
$ python3 -m pytest tests/test_run_eval_batch_task_list.py -v   # 13 passed
$ python3 -m pytest tests/test_derive_l0_passers.py tests/test_thinking_flag.py tests/test_model_registry.py -q   # 26 passed
$ python3 -m pytest tests/ -q --ignore=tests/test_harness_integration.py --ignore=tests/test_spec_loader_integration.py   # 152 passed, 3 skipped
$ grep -n 'add_mutually_exclusive_group' scripts/evaluation/run_eval_batch.py   # match @ line 473
$ grep -n 'parser.error' scripts/evaluation/run_eval_batch.py | grep -iE 'task.list|kernels.*task'   # no match (D-23 lock holds)
$ grep -n '_build_tasks_from_task_list' scripts/evaluation/run_eval_batch.py   # 2 matches (defn + call)
$ grep -n 'required=True' scripts/evaluation/run_eval_batch.py | grep -i direction   # match @ line 499
```

## Deviations from Plan

None of substance. Two minor additive choices documented as decisions above:
- Direction-API mismatch warning + skip (added robustness; covered by test #9).
- Top-level `task_list` field in batch summary JSON (alongside existing `suite`/`kernels`).

## Self-Check: PASSED

- [x] `scripts/evaluation/run_eval_batch.py` exists and contains `--task-list` (verified via grep).
- [x] `tests/test_run_eval_batch_task_list.py` exists and 13 tests pass.
- [x] No new commits yet (BATCHED-COMMIT mode — Phase A only). Will be committed in Phase B on user signal.

## Threat Flags

None. The flag is a CLI-only enumeration shortcut — no new network surface, no auth path, no schema change at trust boundaries. The passer JSON is a local file produced by the user's own canonical-eval directory.
