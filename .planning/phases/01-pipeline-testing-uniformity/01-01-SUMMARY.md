---
phase: 01-pipeline-testing-uniformity
plan: 01
subsystem: harness-constants
tags: [deduplication, constants, known-fail]
dependency_graph:
  requires: []
  provides: [EXCLUDED_SPECS-centralized]
  affects: [analyze_eval, quantitative_findings, generate_paper_data, token_analysis]
tech_stack:
  added: []
  patterns: [single-source-of-truth-constant]
key_files:
  created:
    - harness/constants.py
  modified:
    - scripts/evaluation/analyze_eval.py
    - scripts/analysis/quantitative_findings.py
    - scripts/analysis/generate_paper_data.py
    - scripts/analysis/token_analysis.py
decisions:
  - "EXCLUDED_SPECS placed in harness/constants.py (not harness/__init__.py) to keep __init__.py minimal"
  - "Used frozenset for immutability"
metrics:
  duration_seconds: 74
  completed: "2026-04-10T17:15:49Z"
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 4
---

# Phase 01 Plan 01: Centralize EXCLUDED_SPECS Summary

Centralized the 8 KNOWN_FAIL spec IDs into a single `harness/constants.py` module, replacing 4 duplicate frozenset definitions across analysis and evaluation scripts. Fixed a latent bug where `token_analysis.py` only excluded 6 specs (missing 2 HeCBench entries).

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Create harness/constants.py | 00ea129 | harness/constants.py |
| 2 | Replace 4 EXCLUDED_SPECS duplicates | 00ea129 | analyze_eval.py, quantitative_findings.py, generate_paper_data.py, token_analysis.py |

## Verification Results

- `from harness.constants import EXCLUDED_SPECS` -- OK, 8 entries
- All 4 files: import present, no local frozenset definition
- `python3 -m pytest tests/ -x -q` -- 184 passed, 1 skipped

## Deviations from Plan

None -- plan executed exactly as written.

## Bug Fixed

`scripts/analysis/token_analysis.py` had only 6 EXCLUDED_SPECS (missing `hecbench-stencil1d-omp_target` and `hecbench-scan-omp_target`). The import from `harness.constants` automatically fixes this, ensuring all 8 KNOWN_FAIL specs are excluded from token analysis.

## Known Stubs

None.

## Self-Check: PASSED

- [x] harness/constants.py exists
- [x] Commit 00ea129 exists in git log
- [x] All 4 modified files contain the import
- [x] No local EXCLUDED_SPECS definitions remain
- [x] 184 tests pass
