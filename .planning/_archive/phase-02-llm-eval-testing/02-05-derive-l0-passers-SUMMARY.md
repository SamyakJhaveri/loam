---
phase: 02-llm-eval-testing
plan: 02-05
subsystem: evaluation
tags: [derive-l0-passers, pass-at-1-of-any, d-16, d-17, d-18, d-19, d-20, d-21, d-22]
requires: []
provides:
  - "scripts/evaluation/derive_l0_passers.py — CLI emitting l0_passers_{model}.json (pass@1-of-any)"
  - "derive_passers(canonical_dir, model) -> list[dict] — pure fn for tests + downstream import"
  - "tests/test_derive_l0_passers.py — 10 synthetic-fixture tests covering D-22 + robustness invariants"
affects:
  - 02-06  # run_eval_batch.py --task-list consumes the JSON this script emits
tech-stack:
  added: []
  patterns:
    - "try/except-and-warn-continue per-file robustness (mirrors analyze_eval.py:_load_complexity_lookup)"
    - "argparse CLI + pure core function split (main() thin, derive_passers() testable)"
key-files:
  created:
    - scripts/evaluation/derive_l0_passers.py
    - tests/test_derive_l0_passers.py
  modified: []
decisions:
  - "Removed `all_cells_seen: set[...]` tracker and the unreachable `n == 0` branch per wave-3 code-simplifier advisory. Every cell added to the set was also added to `cell_samples`, so the set was redundant and the zero-samples branch was dead code. Iteration now goes through `sorted(cell_samples)` directly. Behavior-preserving."
  - "Did NOT reimplement `pass_at_k` — the pass@1-of-any semantics reduces to `any(s == 'PASS' for s in samples)`, not a k-choose-c probability. The existing pass_at_k at scripts/analysis/statistical_analysis.py:706 remains the single source."
  - "Did NOT add a `--filter` flag for the Gal pass@2-of-3 fallback (CONTEXT §Claude's Discretion: defer until requested)."
  - "Module kept stdlib-only per the plan's constraint list; no imports from harness/, c_augmentation/, or scripts/analysis/."
metrics:
  duration_minutes: 12
  tasks_total: 2
  tasks_complete: 2
  files_created: 2
  files_modified: 0
  commits: 3
  completed_date: 2026-04-17
---

# Phase 2 Plan 02-05: Derive L0 Passers Summary

New `scripts/evaluation/derive_l0_passers.py` CLI emits a flat list of (source_spec, target_spec, augment_level=0) tuples for cells where ≥1 of the canonical L0 samples passed — the input artifact that `run_eval_batch.py --task-list` (plan 02-06) will consume for the L1–L4 ablation stream.

## Objective Met

> Create a new CLI that ingests a directory of canonical (pass@3, L0) result JSONs for a given model and emits a flat list of (source_spec, target_spec, augment_level=0) tuples where ≥1 of the 3 samples passed.

Implemented per D-16 through D-22. Filter is pass@1-of-any (`any(s == "PASS" for s in samples)`), not pass@k reconstruction. 10/10 tests pass.

## Artifacts

| Path | Kind | Lines |
|------|------|-------|
| `scripts/evaluation/derive_l0_passers.py` | created | 119 |
| `tests/test_derive_l0_passers.py` | created | 127 |

## CLI Help Output

```
usage: derive_l0_passers.py [-h] --canonical-dir CANONICAL_DIR --model MODEL
                            [--out OUT]

Derive L0-passer set (pass@1-of-any) for a model from a canonical eval
directory.

options:
  -h, --help            show this help message and exit
  --canonical-dir CANONICAL_DIR
                        Directory of canonical (L0) result JSONs (recursively
                        scanned).
  --model MODEL         Model id to filter on (e.g. together-
                        qwen-3.5-397b-a17b).
  --out OUT             Output path (default: .planning/eval-
                        selections/l0_passers_{model}.json).
```

## Pure Function Signature

```python
def derive_passers(canonical_dir: Path, model: str) -> list[dict[str, Any]]:
    """Return sorted passer list. Pure function — no filesystem writes."""
```

Returns a list of `{"source_spec": str, "target_spec": str, "augment_level": 0}` dicts in deterministic sort order. Raises `FileNotFoundError` if `canonical_dir` doesn't exist; emits stderr warnings for unparseable JSONs and incomplete (<3) sample counts; otherwise never raises.

`main(argv: list[str] | None = None) -> int` wraps the pure function with argparse and the default output-path contract (`.planning/eval-selections/l0_passers_{model}.json`); returns `0` on success, `1` if the input dir is missing.

## pass_at_k Confirmation

`grep -n 'pass_at_k' scripts/evaluation/derive_l0_passers.py` → no matches. The single source of truth at `scripts/analysis/statistical_analysis.py:706` is unchanged. The filter in this script reduces to `any()` aggregation and does not need the k-choose-c estimator.

## Test Cases (D-22 + supporting invariants)

| # | Test | D-22 case | Asserts |
|---|------|-----------|---------|
| 1 | `test_three_of_three_pass_included` | case 1 (3/3 PASS) | included, no warning |
| 2 | `test_one_of_three_pass_included` | case 2 (1/3 PASS) | included, no warning |
| 3 | `test_zero_of_three_pass_excluded` | case 3 (0/3 PASS) | excluded, no warning |
| 4 | `test_two_samples_one_pass_included_with_warning` | case 4 (2 samples, 1 PASS) | included + "incomplete" / "2/3" warning |
| 5 | `test_zero_samples_vacuous` | case 5 (0 samples) | empty list (cell never discovered) |
| 6 | `test_model_filter_excludes_other_models` | — | only matching model counts |
| 7 | `test_augment_level_filter_excludes_non_L0` | — | only `augment_level==0` counts |
| 8 | `test_unparseable_json_is_skipped` | — | warn + continue |
| 9 | `test_main_writes_default_out_path` | — | default path honored, `augment_level=0` in output |
| 10 | `test_missing_canonical_dir_returns_1` | — | exit 1 + stderr |

`pytest tests/test_derive_l0_passers.py -v` → **10/10 PASS** in 0.02s.

## Commits

| Task | Hash | Message |
|------|------|---------|
| 1 | _pending_ | `feat(02-05): add derive_l0_passers.py for L0 passer derivation` |
| 2 | _pending_ | `test(02-05): add tests for derive_l0_passers` |
| 3 | _pending_ | `docs(02-05): complete derive-l0-passers plan` |

Commit hashes will be filled in after the batched commit pass in the parent session (sentinel-lifecycle batching).

## Verification (from PLAN.md §verification)

- ✅ `pytest tests/test_derive_l0_passers.py -v` → 10/10 pass.
- ✅ `python3 -m scripts.evaluation.derive_l0_passers --help` → exits 0, shows `--canonical-dir`, `--model`, `--out`.
- ✅ `git diff --stat` over the plan's commits → only `scripts/evaluation/derive_l0_passers.py`, `tests/test_derive_l0_passers.py`, and the metadata files (`.planning/phases/02-llm-eval-testing/02-05-derive-l0-passers-SUMMARY.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`) touched.

## Acceptance Criteria (from Task 1)

- ✅ `--help` prints the three flags.
- ✅ `grep 'pass_at_k' derive_l0_passers.py` → no matches.
- ✅ `grep 'from scripts.analysis' derive_l0_passers.py` → no matches.
- ✅ `grep 'augment_level' derive_l0_passers.py` → matches.
- ✅ `grep 'overall_status' derive_l0_passers.py` → matches.
- ✅ `grep 'mkdir(parents=True' derive_l0_passers.py` → matches.
- ✅ `.planning/eval-selections` literal present.
- ✅ `any(s == "PASS"` present — the pass@1-of-any implementation.

## Acceptance Criteria (from Task 2)

- ✅ `pytest tests/test_derive_l0_passers.py -v` exits 0; 10/10 pass.
- ✅ 10 `def test_` functions (D-22's 5 cases + 5 supporting invariants).
- ✅ No `@pytest.mark.integration` or `@pytest.mark.llm` markers.

## Deviations from Plan

**One behavior-preserving simplification.**

### 1. [Advisory cleanup] Removed dead code in `derive_passers()`

- **Found during:** Wave-3 `/validate` advisory from parent session.
- **Issue:** The `all_cells_seen: set[tuple[str, str]]` tracker duplicated `cell_samples`'s keyset. Every cell added to the set was also added to `cell_samples` in the same loop iteration. Iterating `sorted(all_cells_seen)` and then branching on `n == 0` made the zero-samples branch unreachable.
- **Fix:** Removed the set; changed the second loop to `for cell in sorted(cell_samples):`; removed the `n == 0` branch.
- **Files modified:** `scripts/evaluation/derive_l0_passers.py` (lines 54–83 region).
- **Tests:** All 10 still pass unchanged — the D-22 "case 5 (0 samples)" test verifies the vacuous case at the directory level (no matching files → empty list), which the simplified code handles correctly via the empty `cell_samples` defaultdict.
- **Commit:** bundled into Task 1's `feat(02-05): add derive_l0_passers.py …` commit.

No Rule 1/2/3 auto-fixes were needed. No Rule 4 architectural questions arose.

## Auth Gates

None.

## Known Stubs

None. The script does not emit any UI-bound placeholder; output is a flat JSON list consumed programmatically by plan 02-06.

## Self-Check

Filesystem + commit verification will run after the batched commit pass completes.

- ✅ FOUND: `scripts/evaluation/derive_l0_passers.py` (created, 119 lines, `--help` works)
- ✅ FOUND: `tests/test_derive_l0_passers.py` (created, 127 lines, 10/10 pass)
- ⏳ PENDING: commit hashes (filled after batched commit pass)
