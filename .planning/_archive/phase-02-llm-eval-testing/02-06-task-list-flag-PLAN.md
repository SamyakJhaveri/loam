---
phase: 02-llm-eval-testing
plan: 06
type: execute
wave: 5
depends_on:
  - "02-03"
  - "02-05"
files_modified:
  - scripts/evaluation/run_eval_batch.py
  - tests/test_run_eval_batch_task_list.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "`run_eval_batch.py --task-list <json>` loads a flat passer-JSON list and runs only the listed cells"
    - "`--task-list` is mutually exclusive with `--suite` and `--kernels` via `parser.add_mutually_exclusive_group()` (argparse-native)"
    - "`--task-list` is compatible with `--models`, `--direction` (still required), `--augment-levels`, `--num-samples`, `--temperature`, `--thinking`, `--max-retries`, `--resume`"
    - "Passer entries whose source/target specs are not in manifest are skipped with stderr warning, not crash"
    - "Task list shape (dict per task) matches the existing `_build_tasks()` contract"
    - "Argparse-native error shape is asserted in tests via `pytest.raises(SystemExit)` with exit code 2 (NOT exact error-message text)"
  artifacts:
    - path: "scripts/evaluation/run_eval_batch.py"
      provides: "--task-list flag + mutex group + task-list consumption branch in _build_tasks"
      contains: "--task-list"
    - path: "tests/test_run_eval_batch_task_list.py"
      provides: "D-26 4 cases with synthetic passer JSON + mocked evaluate_translation"
      min_lines: 80
  key_links:
    - from: "`--task-list` argparse"
      to: "`_build_tasks()` branch"
      via: "args.task_list: Path passed through to task builder"
      pattern: "task_list"
    - from: "derive_l0_passers.py output (02-05)"
      to: "run_eval_batch.py --task-list (this plan)"
      via: "Flat JSON list consumed verbatim"
      pattern: "source_spec.*target_spec"
---

<objective>
Add a `--task-list <json>` argument to `run_eval_batch.py` that consumes the passer-JSON list produced by `derive_l0_passers.py` (plan 02-05) and runs only the listed cells, bypassing manifest enumeration.

Purpose: Phase 3 ablation (L1-L4) only runs against L0-passers. Without this flag, the batch runner has to enumerate all cells + filter — error-prone and slow. With the flag, ablation launches are a one-liner: `run_eval_batch.py --task-list l0_passers_qwen.json --augment-levels 1 2 3 4 --models together-qwen-3.5-397b-a17b --direction cuda-to-omp`.

Implements D-23, D-24, D-25, D-26.

**LOCK (D-23):** The mutex enforcement MUST use `parser.add_mutually_exclusive_group()` (argparse-native). Runtime `if args.task_list and args.kernels: parser.error(...)` fallback is NOT PERMITTED. Test case D-26 #3 asserts argparse's standard `SystemExit(2)` without asserting the exact stderr text (robust to argparse-wording drift across Python versions).
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@.planning/phases/02-llm-eval-testing/02-03-SUMMARY.md
@.planning/phases/02-llm-eval-testing/02-05-SUMMARY.md
@scripts/evaluation/run_eval_batch.py
@scripts/evaluation/derive_l0_passers.py
@tests/conftest.py
@.claude/rules/evaluation.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Add --task-list flag to run_eval_batch.py with argparse mutex group</name>
  <files>scripts/evaluation/run_eval_batch.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-23, D-24, D-25)
    - scripts/evaluation/run_eval_batch.py (argparse block inside `main()`, lines 362-473 — re-verify with `grep -n 'argparse.ArgumentParser' scripts/evaluation/run_eval_batch.py`)
    - scripts/evaluation/run_eval_batch.py (`_build_tasks()` function — find with `grep -n 'def _build_tasks' scripts/evaluation/run_eval_batch.py`)
  </read_first>
  <behavior>
    - `run_eval_batch.py --help` shows `--task-list PATH`.
    - `--task-list` and `--suite` cannot both be passed → argparse SystemExit(2).
    - `--task-list` and `--kernels` cannot both be passed → argparse SystemExit(2).
    - `--task-list` without `--direction` → SystemExit (existing `required=True` preserved).
    - When `--task-list` is passed, `_build_tasks()` loads the JSON and builds tasks from the entries × `--augment-levels` × `--num-samples` (matrix expansion, matching the existing manifest-enumeration path's task shape).
    - Entries whose source or target spec is absent from the manifest emit a stderr warning and are skipped (not crash).
  </behavior>
  <action>
**Step 1 — Re-verify line ranges.** Run:

```bash
grep -n 'argparse.ArgumentParser' scripts/evaluation/run_eval_batch.py
grep -n 'def _build_tasks' scripts/evaluation/run_eval_batch.py
grep -n 'args.suite' scripts/evaluation/run_eval_batch.py
grep -n 'args.kernels' scripts/evaluation/run_eval_batch.py
```

Use grep output as ground truth; update line references in the SUMMARY if drifted.

**Step 2 — argparse mutex group (D-23 LOCK).** Locate the existing `--suite` and `--kernels` argument definitions. Refactor them into a mutually exclusive group that also contains the new `--task-list`:

```python
    # D-23: --task-list is mutex with --suite and --kernels (argparse-native).
    # Runtime-check fallback is NOT permitted (D-23 lock); use add_mutually_exclusive_group.
    task_selection = parser.add_mutually_exclusive_group(required=False)
    task_selection.add_argument(
        "--suite",
        type=str,
        default=None,
        choices=["rodinia", "xsbench", "rsbench", "mixbench", "hecbench"],
        help="Benchmark suite to enumerate tasks from (mutex with --task-list, --kernels).",
    )
    task_selection.add_argument(
        "--kernels",
        type=str,
        nargs="+",
        default=None,
        help="Explicit list of kernel ids to run (mutex with --task-list, --suite).",
    )
    task_selection.add_argument(
        "--task-list",
        type=Path,
        default=None,
        dest="task_list",
        help=(
            "Path to a passer-JSON list (e.g. from derive_l0_passers.py) — "
            "runs only the listed cells, bypassing manifest enumeration. "
            "Mutex with --suite and --kernels."
        ),
    )
```

**Important:** Preserve the `required=True` on `--direction` if it currently has it (D-24). Do NOT move `--direction` into the mutex group. `--direction` remains mandatory for all three branches.

**Alternative allowed:** If `--suite` and `--kernels` are currently defined with `required=True` each (they cannot both be required in a mutex group), remove `required=True` from the mutex group members and handle the "at least one of suite/kernels/task-list" requirement via a post-parse check. This is acceptable if it preserves behavior. Prefer keeping the existing validation if it was already permissive (one-of-three).

**Step 3 — Branch in `_build_tasks()`.** Locate `_build_tasks(...)`. Add the task-list branch BEFORE the existing manifest-enumeration branch:

```python
def _build_tasks(args, manifest_entries, ...):
    # [existing code]

    if getattr(args, "task_list", None) is not None:
        return _build_tasks_from_task_list(args, manifest_entries)

    # [existing manifest-enumeration branch, unchanged]
```

Implement `_build_tasks_from_task_list()` in the same file:

```python
def _build_tasks_from_task_list(args, manifest_entries) -> list[dict]:
    """Build task dict list from a passer-JSON file (D-25).

    Each entry in the passer JSON looks like:
        {"source_spec": "...", "target_spec": "...", "augment_level": 0}
    `augment_level` in the passer file is a placeholder — we override with
    `args.augment_levels` (list of ints). Cross-product with `--num-samples`.

    Entries whose source_spec or target_spec are absent from the manifest
    are skipped with a stderr warning (D-26 case 2).
    """
    import sys
    import json as _json
    data = _json.loads(args.task_list.read_text())
    manifest_ids = {e.get("unique_id") for e in manifest_entries}
    tasks: list[dict] = []
    for entry in data:
        src = entry["source_spec"]
        tgt = entry["target_spec"]
        if src not in manifest_ids or tgt not in manifest_ids:
            print(
                f"warning: passer entry skipped — not in manifest: "
                f"source_spec={src!r} target_spec={tgt!r}",
                file=sys.stderr,
            )
            continue
        for augment_level in args.augment_levels:
            for sample_id in range(args.num_samples):
                # Shape must match the existing manifest-enumeration branch's
                # task dict contract. Use the existing helper if one exists;
                # otherwise construct manually mirroring the shape.
                tasks.append({
                    "source_spec": src,
                    "target_spec": tgt,
                    "augment_level": augment_level,
                    "sample_id": sample_id,
                })
    return tasks
```

**Verify dict shape matches existing contract.** Before finalizing, READ the existing `_build_tasks()` manifest-enumeration branch to confirm task-dict keys. If additional keys are required (e.g. `direction`, `model`), add them identically to the new branch. Do not invent new keys.

**Step 4 — Do NOT:**
- Add a runtime mutex check (`if args.task_list and args.kernels: parser.error(...)`) — D-23 lock forbids this in favor of argparse-native mutex.
- Change `--direction`'s required status.
- Break the existing `--suite`/`--kernels` code paths.
- Touch MODEL_REGISTRY.
- Touch `derive_l0_passers.py` (02-05 scope).
  </action>
  <verify>
    <automated>python3 scripts/evaluation/run_eval_batch.py --help 2>&1 | grep -E "^\\s*--task-list\\s"</automated>
  </verify>
  <acceptance_criteria>
    - `python3 scripts/evaluation/run_eval_batch.py --help` output includes `--task-list TASK_LIST`.
    - `grep -n 'add_mutually_exclusive_group' scripts/evaluation/run_eval_batch.py` returns at least one match (D-23 LOCK).
    - `grep -n 'parser.error' scripts/evaluation/run_eval_batch.py | grep -i 'task.list\\|kernels.*task'` returns NO matches (runtime-check fallback forbidden by D-23).
    - `grep -n '_build_tasks_from_task_list' scripts/evaluation/run_eval_batch.py` returns at least 2 matches (definition + call).
    - `grep -n 'required=True' scripts/evaluation/run_eval_batch.py | grep -i direction` returns at least one match (direction is still required, D-24).
    - `python3 scripts/evaluation/run_eval_batch.py --task-list /tmp/nope.json --kernels foo --direction cuda-to-omp --models gpt-4o 2>&1 | head -10` exits nonzero and stderr mentions "not allowed" or "mutually exclusive" (argparse native wording) — BUT the test only asserts exit code 2, not the text.
  </acceptance_criteria>
  <done>`--task-list` flag live, argparse-native mutex with --suite/--kernels, task-list branch in _build_tasks constructs tasks + skips unknown specs.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add tests/test_run_eval_batch_task_list.py covering D-26 4 cases</name>
  <files>tests/test_run_eval_batch_task_list.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-23, D-24, D-25, D-26)
    - scripts/evaluation/run_eval_batch.py (post-edit from Task 1)
    - tests/conftest.py (test pattern reference; NOT using integration marker)
  </read_first>
  <behavior>
    D-26 cases:
    1. Valid passer JSON + `--augment-levels 1 2 3 4` + N passers → task list has `4 × N` entries.
    2. Passer entry whose source/target not in manifest → skipped + stderr warning.
    3. `--task-list` + `--kernels` → `pytest.raises(SystemExit)` + exit code 2 (do NOT assert error text, per F-12).
    4. `--task-list` without `--direction` → `pytest.raises(SystemExit)` (existing required=True preserved).

    Plus:
    5. `--task-list` + `--suite` → SystemExit(2) (same mutex group).
    6. Valid passer with `--num-samples 3` → task list has `4 × N × 3` entries.
  </behavior>
  <action>
Create `tests/test_run_eval_batch_task_list.py`:

```python
"""Phase 2 / Plan 02-06 tests: --task-list flag (D-26).

Uses synthetic passer JSON + mocked evaluate_translation. Validates:
- argparse-native mutex (D-23)
- task matrix expansion (D-25)
- skip-on-missing-manifest behavior (D-26 case 2)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.evaluation import run_eval_batch


@pytest.fixture
def passer_json(tmp_path):
    passers = [
        {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "augment_level": 0},
        {"source_spec": "xsbench-xsbench-cuda", "target_spec": "xsbench-xsbench-omp", "augment_level": 0},
    ]
    p = tmp_path / "passers.json"
    p.write_text(json.dumps(passers))
    return p


@pytest.fixture
def fake_manifest_entries():
    """Mock manifest entries matching the passer JSON."""
    return [
        {"unique_id": "rodinia-bfs-cuda", "parallel_api": "cuda"},
        {"unique_id": "rodinia-bfs-omp", "parallel_api": "omp"},
        {"unique_id": "xsbench-xsbench-cuda", "parallel_api": "cuda"},
        {"unique_id": "xsbench-xsbench-omp", "parallel_api": "omp"},
    ]


def test_task_list_expands_by_augment_levels(tmp_path, passer_json, fake_manifest_entries):
    """D-26 case 1: N passers × 4 levels → 4N tasks (with --num-samples 1)."""
    # Build args via argparse so we test the full parse path.
    argv = [
        "--task-list", str(passer_json),
        "--direction", "cuda-to-omp",
        "--models", "gpt-4o",
        "--augment-levels", "1", "2", "3", "4",
        "--num-samples", "1",
    ]
    with patch.object(run_eval_batch, "load_manifest", return_value=fake_manifest_entries, create=True):
        # Parse args only; do not run eval.
        parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
        if parser is None:
            # Fallback: invoke main() with all deps mocked so it returns before running.
            pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
        args = parser.parse_args(argv)
        tasks = run_eval_batch._build_tasks_from_task_list(args, fake_manifest_entries)
    # 2 passers × 4 levels × 1 sample = 8 tasks
    assert len(tasks) == 8
    assert {t["augment_level"] for t in tasks} == {1, 2, 3, 4}


def test_task_list_expands_by_num_samples(tmp_path, passer_json, fake_manifest_entries):
    """2 passers × 4 levels × 3 samples = 24 tasks."""
    argv = [
        "--task-list", str(passer_json),
        "--direction", "cuda-to-omp",
        "--models", "gpt-4o",
        "--augment-levels", "1", "2", "3", "4",
        "--num-samples", "3",
    ]
    parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
    if parser is None:
        pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
    args = parser.parse_args(argv)
    tasks = run_eval_batch._build_tasks_from_task_list(args, fake_manifest_entries)
    assert len(tasks) == 24


def test_task_list_skips_unknown_specs(tmp_path, fake_manifest_entries, capsys):
    """D-26 case 2: passer entry with spec not in manifest → skip + warning."""
    passers = [
        {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "augment_level": 0},
        {"source_spec": "nonexistent-kernel-cuda", "target_spec": "nonexistent-kernel-omp", "augment_level": 0},
    ]
    p = tmp_path / "passers.json"
    p.write_text(json.dumps(passers))
    argv = [
        "--task-list", str(p),
        "--direction", "cuda-to-omp",
        "--models", "gpt-4o",
        "--augment-levels", "1",
        "--num-samples", "1",
    ]
    parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
    if parser is None:
        pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
    args = parser.parse_args(argv)
    tasks = run_eval_batch._build_tasks_from_task_list(args, fake_manifest_entries)
    # Only the known-manifest passer yields a task.
    assert len(tasks) == 1
    err = capsys.readouterr().err
    assert "nonexistent-kernel" in err


def test_task_list_mutex_with_kernels(tmp_path, passer_json):
    """D-26 case 3: --task-list + --kernels → SystemExit(2).
    Per F-12: assert exit code only, NOT error text (argparse wording drifts across Python)."""
    argv = [
        "--task-list", str(passer_json),
        "--kernels", "rodinia-bfs",
        "--direction", "cuda-to-omp",
        "--models", "gpt-4o",
    ]
    parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
    if parser is None:
        pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)
    assert exc_info.value.code == 2  # argparse's standard error exit code


def test_task_list_mutex_with_suite(tmp_path, passer_json):
    """D-26 case 3 (extended): --task-list + --suite → SystemExit(2)."""
    argv = [
        "--task-list", str(passer_json),
        "--suite", "rodinia",
        "--direction", "cuda-to-omp",
        "--models", "gpt-4o",
    ]
    parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
    if parser is None:
        pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(argv)
    assert exc_info.value.code == 2


def test_task_list_without_direction_fails(tmp_path, passer_json):
    """D-26 case 4: --task-list without --direction → SystemExit (existing required=True)."""
    argv = [
        "--task-list", str(passer_json),
        "--models", "gpt-4o",
    ]
    parser = run_eval_batch._build_parser() if hasattr(run_eval_batch, "_build_parser") else None
    if parser is None:
        pytest.skip("no _build_parser helper; covered by 02-07 integration smoke")
    with pytest.raises(SystemExit):
        parser.parse_args(argv)
```

**Note on `_build_parser` helper:** If `run_eval_batch.py` currently builds its parser inline in `main()`, Task 1 SHOULD extract the parser construction into a `_build_parser()` helper to enable this test. Extracting the parser is a minor refactor (move lines, no behavior change) — acceptable within this plan's scope since it is directly test-enabling. If you prefer NOT to extract, the tests will cleanly `pytest.skip` and the integration smoke in 02-07 covers mutex enforcement. Prefer extraction for crisper test feedback.

Do NOT mark these tests `@pytest.mark.integration` or `@pytest.mark.llm` — they are pure unit tests over argparse + pure functions.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_run_eval_batch_task_list.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/test_run_eval_batch_task_list.py -v` exits 0; tests pass or skip cleanly (skip means `_build_parser` not extracted — acceptable).
    - Among the non-skip tests, at least the two mutex tests (`test_task_list_mutex_with_kernels`, `test_task_list_mutex_with_suite`) pass and assert `exc_info.value.code == 2` (NOT message text).
    - `grep -n '@pytest.mark.integration' tests/test_run_eval_batch_task_list.py` returns no matches.
    - `grep -n 'exc_info.value.code == 2' tests/test_run_eval_batch_task_list.py` returns at least 2 matches (D-26 case 3 + extension).
    - `grep -n 'not allowed\\|mutually exclusive' tests/test_run_eval_batch_task_list.py` returns NO matches (F-12: don't assert error text).
  </acceptance_criteria>
  <done>Test file covers D-26 cases 1-4 + 2 supporting invariants; mutex tests assert exit code only.</done>
</task>

</tasks>

<verification>
- `pytest tests/test_run_eval_batch_task_list.py -v` passes (or cleanly skips with `_build_parser` extraction deferred).
- `python3 scripts/evaluation/run_eval_batch.py --help | grep -- '--task-list'` succeeds.
- `grep -n 'add_mutually_exclusive_group' scripts/evaluation/run_eval_batch.py` shows the mutex group.
- `grep -n 'parser.error' scripts/evaluation/run_eval_batch.py | grep -iE 'task.list|kernels.*task'` returns no runtime-check fallback.
</verification>

<success_criteria>
`--task-list` exists, is argparse-mutex with `--suite` and `--kernels`, consumes the 02-05 passer-JSON format, expands by `--augment-levels` × `--num-samples`, skips specs missing from manifest with warning, and all D-26 test cases green.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-06-SUMMARY.md` documenting: (a) mutex group contents (`--suite`, `--kernels`, `--task-list`), (b) whether `_build_parser` was extracted (yes/no), (c) test pass/skip count.
</output>
