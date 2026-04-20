---
phase: 01
slug: pipeline-testing-uniformity
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-10
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` (pytest section) |
| **Quick run command** | `python3 -m pytest tests/ -x -q --ignore=tests/test_harness_integration.py` |
| **Full suite command** | `python3 -m pytest tests/ -v` |
| **Estimated runtime** | ~30 seconds (unit), ~120 seconds (with integration) |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest tests/ -x -q --ignore=tests/test_harness_integration.py`
- **After every plan wave:** Run `python3 -m pytest tests/ -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | EXCLUDED_SPECS constant created | unit | `python3 -c "from harness.constants import EXCLUDED_SPECS; assert len(EXCLUDED_SPECS) == 8"` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | 4 duplicate definitions replaced | unit | `python3 -m pytest tests/ -x -q` | ✅ | ⬜ pending |
| 01-02-01 | 02 | 2 | Harness integration tests | integration | `python3 -m pytest tests/test_harness_integration.py -v` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | Campaign TDD tests (skipped) | unit | `python3 -m pytest tests/test_campaign_classification.py -v` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | analyze_harness_batch.py created | unit | `python3 scripts/analysis/analyze_harness_batch.py --help` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 1 | analyze_rodinia_batch.py deleted | unit | `python3 -c "from pathlib import Path; assert not Path('scripts/analysis/analyze_rodinia_batch.py').exists()"` | ✅ | ⬜ pending |
| 01-04-01 | 04 | 2 | Per-suite counters in quantitative_findings.py | unit | `python3 -m pytest tests/ -x -q` | ✅ | ⬜ pending |
| 01-04-02 | 04 | 2 | --suite flag in classify_translation_pairs.py | unit | `python3 scripts/analysis/classify_translation_pairs.py --help 2>&1 \| grep -q "\-\-suite"` | ✅ | ⬜ pending |
| 01-04-03 | 04 | 2 | No suite-specific hardcoding verified | unit | `grep -rn "if suite ==" harness/ scripts/evaluation/ \| wc -l` | ✅ | ⬜ pending |
| 01-05-01 | 05 | 2 | Portability audit documented | manual | `python3 -c "from pathlib import Path; assert Path('.planning/phases/01-pipeline-testing-uniformity/portability-audit.md').exists()"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `harness/constants.py` — new file with EXCLUDED_SPECS frozenset
- [ ] `tests/test_harness_integration.py` — integration test stubs
- [ ] `tests/test_campaign_classification.py` — TDD test stubs (skipped)

*Existing pytest infrastructure (conftest.py, pyproject.toml) covers framework needs.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Portability audit | Hardcoded paths documented | Requires human judgment on path categorization | Review `config/paths.json` usage, document findings |
| Old Rodinia results untouched | Historical data preserved | File existence check, not behavioral | `ls results/rodinia/logs/` confirms no changes |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
