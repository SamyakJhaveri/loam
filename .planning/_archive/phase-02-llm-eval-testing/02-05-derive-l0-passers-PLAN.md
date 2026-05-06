---
phase: 02-llm-eval-testing
plan: 05
type: execute
wave: 2
depends_on: []
files_modified:
  - scripts/evaluation/derive_l0_passers.py
  - tests/test_derive_l0_passers.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "`scripts/evaluation/derive_l0_passers.py` exists and is invokable as `python3 -m scripts.evaluation.derive_l0_passers --help`"
    - "Filter semantics: pass@1-of-any — cell (source, target) is a passer iff ≥1 sample for that cell has overall_status==PASS and augment_level==0"
    - "Output schema = flat list of {source_spec, target_spec, augment_level:0} objects"
    - "Default output path = `.planning/eval-selections/l0_passers_{model}.json`"
    - "Permissive on incomplete samples: ≥1 PASS included with stderr warning; missing samples treated as non-passes"
    - "Per-file read robustness via the `_load_complexity_lookup` try/except-and-warn-continue pattern"
    - "`pass_at_k` is NOT reimplemented — existing `scripts/analysis/statistical_analysis.py:706` remains the single source"
    - "Tests cover 5 cases from D-22 with synthetic fixtures"
  artifacts:
    - path: "scripts/evaluation/derive_l0_passers.py"
      provides: "CLI that emits l0_passers_{model}.json from a canonical result directory"
      min_lines: 60
      exports: ["main", "derive_passers"]
    - path: "tests/test_derive_l0_passers.py"
      provides: "5 D-22 test cases with synthetic fixtures"
      min_lines: 80
  key_links:
    - from: "derive_l0_passers.py --canonical-dir"
      to: "results/evaluation/{model}/*.json (per-task result files)"
      via: "glob + per-file JSON parse"
      pattern: "augment_level.*0"
    - from: "derive_l0_passers.py output"
      to: "run_eval_batch.py --task-list (plan 02-06)"
      via: "Flat JSON list of task tuples"
      pattern: "source_spec.*target_spec"
---

<objective>
Create `scripts/evaluation/derive_l0_passers.py`: a new CLI that ingests a directory of canonical (pass@3, L0) result JSONs for a given model and emits a flat list of (source_spec, target_spec, augment_level=0) tuples where ≥1 of the 3 samples passed. Output is consumed by plan 02-06's `--task-list` flag in `run_eval_batch.py`.

Purpose: Phase 3 ablation (L1-L4) runs only against L0-passers per the Gal-approved design. Without this script, selecting the L0-passer set is a manual process that (a) drifts from the filter definition and (b) cannot be re-run after a canonical re-eval. This script makes the filter reproducible + testable.

Implements D-16, D-17, D-18, D-19, D-20, D-21, D-22.

**Single source of truth:** `pass_at_k` already exists at `scripts/analysis/statistical_analysis.py:706`. Do NOT reimplement. This script does not need `pass_at_k` anyway — the filter is pass@1-of-any (≥1 PASS), which is a simple `any()` aggregation.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@scripts/analysis/analyze_eval.py
@scripts/analysis/statistical_analysis.py
@tests/conftest.py
@.claude/rules/evaluation.md
@./CLAUDE.md
</context>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Implement scripts/evaluation/derive_l0_passers.py</name>
  <files>scripts/evaluation/derive_l0_passers.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-16 through D-22)
    - scripts/analysis/analyze_eval.py (specifically `_load_complexity_lookup` — the try/except-and-warn-continue idiom to mirror)
    - scripts/analysis/statistical_analysis.py (lines near 706 — to confirm `pass_at_k` exists and we are NOT reimplementing it)
    - .claude/rules/evaluation.md (result JSON schema)
  </read_first>
  <behavior>
    - `python3 -m scripts.evaluation.derive_l0_passers --help` prints args: `--canonical-dir`, `--model`, `--out` (optional).
    - For `--canonical-dir <dir>`: globs `<dir>/**/*.json` (recursive — accommodates both flat and model-subdir layouts).
    - Filters each loaded JSON: keep iff `obj.get("model") == args.model` AND `obj.get("augment_level") == 0`.
    - Groups by cell key `(source_spec, target_spec)`.
    - Cell is a PASSER iff ≥1 result in the group has `overall_status == "PASS"`.
    - Emits JSON list: `[{"source_spec": ..., "target_spec": ..., "augment_level": 0}, ...]` in deterministic order (sorted by `(source_spec, target_spec)`).
    - Default `--out` = `.planning/eval-selections/l0_passers_{args.model}.json`. Parent dir created with `mkdir(parents=True, exist_ok=True)`.
    - Warns to stderr when: (a) a JSON file fails to parse, (b) a cell has <3 samples, (c) a cell has 0 samples (vacuous — excluded).
    - Exit code 0 on success, 1 on fatal error (bad args, input dir does not exist).
  </behavior>
  <action>
Create `scripts/evaluation/derive_l0_passers.py`:

```python
"""Derive L0 passer-set for a given model from a canonical eval directory.

Phase 2 / Plan 02-05. Implements D-16 through D-21.

Filter: pass@1-of-any — cell (source_spec, target_spec) is a passer iff
the set of samples for that cell at augment_level=0 contains at least one
result with overall_status == "PASS". Samples with missing / unparseable
JSONs are treated as non-passes (permissive, matches D-21 exactly).

Output schema (D-19): flat list of {"source_spec": str, "target_spec": str,
"augment_level": 0} dicts. `augment_level: 0` is a placeholder — the consuming
`run_eval_batch.py --task-list` invocation overrides via `--augment-levels 1 2 3 4`.

Usage:
    python3 -m scripts.evaluation.derive_l0_passers \\
        --canonical-dir results/evaluation/qwen_canonical \\
        --model together-qwen-3.5-397b-a17b \\
        --out .planning/eval-selections/l0_passers_qwen.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def _load_result(path: Path) -> dict[str, Any] | None:
    """Load a result JSON, mirroring analyze_eval.py:_load_complexity_lookup's
    try/except-and-warn-continue idiom. Returns None on any parse error."""
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"warning: failed to load {path}: {e}", file=sys.stderr)
        return None


def derive_passers(canonical_dir: Path, model: str) -> list[dict[str, Any]]:
    """Return sorted passer list. Pure function — no filesystem writes.

    Per D-18: cell is a passer iff ≥1 of its (augment_level=0, model==model) samples
    has overall_status == "PASS".
    Per D-21: cells with <3 samples emit a stderr warning but are still included if
    they have ≥1 PASS. Cells with 0 samples emit a warning and are excluded.
    """
    if not canonical_dir.is_dir():
        raise FileNotFoundError(f"canonical dir not found: {canonical_dir}")

    # Group samples per cell.
    cell_samples: dict[tuple[str, str], list[str]] = defaultdict(list)
    # Discover cells even if 0 samples pass the filter (so we can warn on them).
    all_cells_seen: set[tuple[str, str]] = set()

    for path in sorted(canonical_dir.rglob("*.json")):
        obj = _load_result(path)
        if obj is None:
            continue
        if obj.get("model") != model:
            continue
        if obj.get("augment_level") != 0:
            continue
        src = obj.get("source_spec")
        tgt = obj.get("target_spec")
        status = obj.get("overall_status")
        if not src or not tgt:
            print(f"warning: {path} missing source_spec/target_spec", file=sys.stderr)
            continue
        cell = (src, tgt)
        all_cells_seen.add(cell)
        cell_samples[cell].append(status)

    passers: list[dict[str, Any]] = []
    for cell in sorted(all_cells_seen):
        samples = cell_samples[cell]
        n = len(samples)
        if n == 0:
            print(f"warning: cell {cell} has 0 samples; excluded", file=sys.stderr)
            continue
        if n < 3:
            print(f"warning: cell {cell} has {n}/3 samples (incomplete)", file=sys.stderr)
        if any(s == "PASS" for s in samples):
            passers.append({
                "source_spec": cell[0],
                "target_spec": cell[1],
                "augment_level": 0,
            })

    return passers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Derive L0-passer set (pass@1-of-any) for a model from a canonical eval directory.",
    )
    parser.add_argument("--canonical-dir", type=Path, required=True,
                        help="Directory of canonical (L0) result JSONs (recursively scanned).")
    parser.add_argument("--model", type=str, required=True,
                        help="Model id to filter on (e.g. together-qwen-3.5-397b-a17b).")
    parser.add_argument("--out", type=Path, default=None,
                        help="Output path (default: .planning/eval-selections/l0_passers_{model}.json).")
    args = parser.parse_args(argv)

    try:
        passers = derive_passers(args.canonical_dir, args.model)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out_path = args.out
    if out_path is None:
        # Slugify model for filename safety.
        slug = args.model.replace("/", "_")
        out_path = Path(".planning/eval-selections") / f"l0_passers_{slug}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(passers, indent=2) + "\\n")
    print(f"wrote {len(passers)} passers to {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Important constraints:**
- Do NOT import `pass_at_k`. Do NOT reimplement it. This script's semantics (`any()` aggregation) is deliberately simpler.
- Do NOT add a `--filter` flag for the Gal pass@2-of-3 fallback (CONTEXT §Claude's Discretion: defer until requested).
- Do NOT hardcode `results/evaluation/<model>/` — the `--canonical-dir` must accept any path.
- Do NOT exit with a non-zero code if the passer list is empty — an empty list is valid output (the canonical dir may have 0 passers; caller decides what to do).
- Keep the module self-contained: no imports from `harness/` or `c_augmentation/`. Only stdlib + `pathlib`.
  </action>
  <verify>
    <automated>python3 -m scripts.evaluation.derive_l0_passers --help 2>&1 | grep -E "^\\s*--(canonical-dir|model|out)\\s"</automated>
  </verify>
  <acceptance_criteria>
    - `python3 -m scripts.evaluation.derive_l0_passers --help` prints usage with `--canonical-dir`, `--model`, `--out`.
    - `grep -n 'pass_at_k' scripts/evaluation/derive_l0_passers.py` returns no matches (not reimplemented).
    - `grep -n 'from scripts.analysis' scripts/evaluation/derive_l0_passers.py` returns no matches (no dependency on analysis package).
    - `grep -n 'augment_level' scripts/evaluation/derive_l0_passers.py` returns matches (filter uses the field).
    - `grep -n 'overall_status' scripts/evaluation/derive_l0_passers.py` returns matches.
    - `grep -n 'mkdir(parents=True' scripts/evaluation/derive_l0_passers.py` returns a match (output dir is created).
    - `grep -n '`.planning/eval-selections`' scripts/evaluation/derive_l0_passers.py` or equivalent string literal returns a match (default out path).
    - `grep -n 'any(s == "PASS"' scripts/evaluation/derive_l0_passers.py` returns a match (the pass@1-of-any implementation).
  </acceptance_criteria>
  <done>Script exists, CLI functional, pure `derive_passers()` function available for tests, filter semantics match D-18/D-21.</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Add tests/test_derive_l0_passers.py with 5 synthetic-fixture cases</name>
  <files>tests/test_derive_l0_passers.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-22 — 5 cases)
    - scripts/evaluation/derive_l0_passers.py (just created)
    - tests/conftest.py (fixture patterns, but NOT using integration marker)
  </read_first>
  <behavior>
    Cases per D-22 (synthetic fixtures — temp dir + `json.dump` of fake result JSONs, no real eval data):
    1. 3/3 PASS → cell included, no warning
    2. 1/3 PASS → cell included, no warning
    3. 0/3 PASS → cell excluded, no warning
    4. 2 samples (1 PASS, 1 FAIL) → cell included + `incomplete sample count` warning
    5. 0 samples for a discovered cell → never included, 0-samples warning (this requires either (a) observing a cell through another mechanism or (b) verifying the pure function yields `[]` when the dir is empty)

    Plus:
    6. `--out` default path is `.planning/eval-selections/l0_passers_{model}.json`.
    7. Filter is per-model: a file with a different `model` id is ignored.
    8. Filter is per-augment-level: a file with `augment_level != 0` is ignored.
    9. Unparseable JSON file is skipped with warning, does not abort.
  </behavior>
  <action>
Create `tests/test_derive_l0_passers.py`:

```python
"""Phase 2 / Plan 02-05 tests: derive_l0_passers filter semantics (D-22)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.evaluation.derive_l0_passers import derive_passers, main


MODEL = "together-qwen-3.5-397b-a17b"


def _write_result(tmp_path: Path, filename: str, *, model: str = MODEL, augment_level: int = 0,
                  source_spec: str = "rodinia-bfs-cuda", target_spec: str = "rodinia-bfs-omp",
                  overall_status: str = "PASS") -> Path:
    obj = {
        "model": model,
        "augment_level": augment_level,
        "source_spec": source_spec,
        "target_spec": target_spec,
        "overall_status": overall_status,
    }
    p = tmp_path / filename
    p.write_text(json.dumps(obj))
    return p


def test_three_of_three_pass_included(tmp_path, capsys):
    """D-22 case 1: 3/3 PASS → included, no warning."""
    for i in range(3):
        _write_result(tmp_path, f"cell-s{i}.json", overall_status="PASS")
    passers = derive_passers(tmp_path, MODEL)
    assert len(passers) == 1
    assert passers[0] == {"source_spec": "rodinia-bfs-cuda", "target_spec": "rodinia-bfs-omp", "augment_level": 0}
    err = capsys.readouterr().err
    assert "incomplete" not in err
    assert "0 samples" not in err


def test_one_of_three_pass_included(tmp_path, capsys):
    """D-22 case 2: 1/3 PASS → included, no warning."""
    _write_result(tmp_path, "cell-s0.json", overall_status="PASS")
    _write_result(tmp_path, "cell-s1.json", overall_status="BUILD_FAIL")
    _write_result(tmp_path, "cell-s2.json", overall_status="VERIFY_FAIL")
    passers = derive_passers(tmp_path, MODEL)
    assert len(passers) == 1
    err = capsys.readouterr().err
    assert "incomplete" not in err


def test_zero_of_three_pass_excluded(tmp_path, capsys):
    """D-22 case 3: 0/3 PASS → excluded, no warning (samples complete)."""
    for i in range(3):
        _write_result(tmp_path, f"cell-s{i}.json", overall_status="BUILD_FAIL")
    passers = derive_passers(tmp_path, MODEL)
    assert passers == []
    err = capsys.readouterr().err
    assert "incomplete" not in err


def test_two_samples_one_pass_included_with_warning(tmp_path, capsys):
    """D-22 case 4: 2 samples, 1 PASS → included + incomplete-sample warning."""
    _write_result(tmp_path, "cell-s0.json", overall_status="PASS")
    _write_result(tmp_path, "cell-s1.json", overall_status="BUILD_FAIL")
    passers = derive_passers(tmp_path, MODEL)
    assert len(passers) == 1
    err = capsys.readouterr().err
    assert "2/3" in err or "incomplete" in err


def test_zero_samples_vacuous(tmp_path, capsys):
    """D-22 case 5: no matching files → empty passer list (0 samples means no cell discovered)."""
    # Put a file that does NOT match the model filter — should be ignored.
    _write_result(tmp_path, "other-model.json", model="azure-gpt-5.4", overall_status="PASS")
    passers = derive_passers(tmp_path, MODEL)
    assert passers == []


def test_model_filter_excludes_other_models(tmp_path):
    """Only files with the target model id count."""
    _write_result(tmp_path, "wrong-model-pass.json", model="gpt-4o", overall_status="PASS")
    _write_result(tmp_path, "right-model-fail.json", model=MODEL, overall_status="BUILD_FAIL")
    passers = derive_passers(tmp_path, MODEL)
    assert passers == []


def test_augment_level_filter_excludes_non_L0(tmp_path):
    """Only augment_level==0 results count."""
    for lvl in (1, 2, 3, 4):
        _write_result(tmp_path, f"L{lvl}.json", augment_level=lvl, overall_status="PASS")
    passers = derive_passers(tmp_path, MODEL)
    assert passers == []


def test_unparseable_json_is_skipped(tmp_path, capsys):
    """Unparseable JSON → stderr warning, not a crash. Good file still processed."""
    (tmp_path / "broken.json").write_text("{not json")
    _write_result(tmp_path, "good.json", overall_status="PASS")
    passers = derive_passers(tmp_path, MODEL)
    assert len(passers) == 1
    err = capsys.readouterr().err
    assert "failed to load" in err and "broken.json" in err


def test_main_writes_default_out_path(tmp_path, monkeypatch, capsys):
    """Default --out path = .planning/eval-selections/l0_passers_{model}.json."""
    monkeypatch.chdir(tmp_path)
    canonical = tmp_path / "canonical"
    canonical.mkdir()
    _write_result(canonical, "good.json", overall_status="PASS")
    rc = main(["--canonical-dir", str(canonical), "--model", MODEL])
    assert rc == 0
    out = tmp_path / ".planning" / "eval-selections" / f"l0_passers_{MODEL}.json"
    assert out.exists()
    data = json.loads(out.read_text())
    assert len(data) == 1
    assert data[0]["augment_level"] == 0


def test_missing_canonical_dir_returns_1(tmp_path, capsys):
    """Non-existent dir → exit code 1 with stderr error."""
    rc = main(["--canonical-dir", str(tmp_path / "nope"), "--model", MODEL])
    assert rc == 1
    err = capsys.readouterr().err
    assert "not found" in err
```

Do NOT mark with `@pytest.mark.integration` or `@pytest.mark.llm` — these are pure-function tests over synthetic fixtures. Always run in default `pytest tests/`.
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_derive_l0_passers.py -v</automated>
  </verify>
  <acceptance_criteria>
    - `pytest tests/test_derive_l0_passers.py -v` exits 0; all 10 tests pass.
    - `grep -c 'def test_' tests/test_derive_l0_passers.py` returns at least 10 (D-22's 5 cases + 5 supporting invariants).
    - `grep -n '@pytest.mark.integration' tests/test_derive_l0_passers.py` returns no matches.
    - `grep -n '@pytest.mark.llm' tests/test_derive_l0_passers.py` returns no matches.
  </acceptance_criteria>
  <done>Test file covers all 5 D-22 cases + 5 robustness invariants; all green.</done>
</task>

</tasks>

<verification>
- `pytest tests/test_derive_l0_passers.py -v` passes 10/10.
- `python3 -m scripts.evaluation.derive_l0_passers --help` exits 0 and shows three flags.
- `git diff --stat` shows only the two files in `files_modified`.
</verification>

<success_criteria>
`derive_l0_passers.py` exists, implements pass@1-of-any per D-18, writes the D-19 schema to the D-20 default path, handles D-21 edge cases with warnings, and all D-22 cases are tested.
</success_criteria>

<output>
After completion, create `.planning/phases/02-llm-eval-testing/02-05-SUMMARY.md` documenting: (a) the exact CLI help output, (b) the pure `derive_passers()` function signature, (c) confirmation that `pass_at_k` was NOT reimplemented.
</output>
