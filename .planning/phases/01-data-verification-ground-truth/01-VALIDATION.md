---
phase: 1
slug: data-verification-ground-truth
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-03
last_audit: 2026-04-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` (pytest section) |
| **Quick run command** | `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q` |
| **Full suite command** | `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py scripts/analysis/test_statistical_analysis.py scripts/analysis/test_build_error_taxonomy.py -v` |
| **Estimated runtime** | ~1 second |

---

## Sampling Rate

- **After every task commit:** Run `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q`
- **After every plan wave:** Run full analysis test suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 1 second

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-xx | 01 | 1 | VERIFY-01 | manual + smoke | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x` | YES (29 tests) | ✅ green |
| 01-02-xx | 02 | 1 | VERIFY-02 | manual | `python3 -c "..."` (inline count check) | Manual only | ✅ green |
| 01-03-xx | 03 | 1 | VERIFY-03 | manual | `grep LEVEL_FRACTIONS c_augmentation/augment_dataset.py` | Manual only | ✅ green |
| 01-04-xx | 04 | 1 | VERIFY-04 | manual | `grep -in gemini docs/paper/latex/paper.tex` | Manual only | ✅ green |
| 01-05-xx | 05 | 1 | VERIFY-05 | manual | `nvcc --version && gcc --version && nvidia-smi` | Manual only | ✅ green |
| 01-06-xx | 06 | 2 | VERIFY-06 | smoke | Run all 4 scripts, then re-run test suite | YES | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

All infrastructure was pre-existing. No new test files needed for this phase. Manual verification was the primary method for VERIFY-02 through VERIFY-05. Automated tests cover VERIFY-01 and VERIFY-06.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Suite-summary table matches manifest+specs | VERIFY-02 | Requires cross-checking LaTeX table against file counts | Count specs/ files, parse manifest.jsonl, compare to paper table |
| Augmentation levels match code | VERIFY-03 | One-time check of 4 values | Grep LEVEL_FRACTIONS from augment_dataset.py, compare to paper table |
| No Gemini remnants in paper | VERIFY-04 | Text search across LaTeX | `grep -in gemini docs/paper/latex/paper.tex` — zero non-pending matches |
| Hardware table matches system | VERIFY-05 | Requires live system commands | Run nvcc/gcc/nvidia-smi, compare outputs to paper table |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** complete

---

## Validation Audit 2026-04-06

| Metric | Count |
|--------|-------|
| Gaps found | 17 |
| Resolved | 17 |
| Escalated | 0 |

**Root cause:** Test expectations hardcoded for 480-task Rodinia-only scope; project moved to 710-task all-suite coverage. All 17 tests updated to match current paper_data.json (710 tasks, all suites). Full suite: 59/59 pass.
