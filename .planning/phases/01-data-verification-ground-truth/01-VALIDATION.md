---
phase: 1
slug: data-verification-ground-truth
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
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
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `source env_parbench/bin/activate && python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q`
- **After every plan wave:** Run full analysis test suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-xx | 01 | 1 | VERIFY-01 | manual + smoke | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x` | YES (20 tests) | ⬜ pending |
| 01-02-xx | 02 | 1 | VERIFY-02 | manual | `python3 -c "..."` (inline count check) | Manual only | ⬜ pending |
| 01-03-xx | 03 | 1 | VERIFY-03 | manual | `grep LEVEL_FRACTIONS c_augmentation/augment_dataset.py` | Manual only | ⬜ pending |
| 01-04-xx | 04 | 1 | VERIFY-04 | manual | `grep -in gemini docs/paper/latex/paper.tex` | Manual only | ⬜ pending |
| 01-05-xx | 05 | 1 | VERIFY-05 | manual | `nvcc --version && gcc --version && nvidia-smi` | Manual only | ⬜ pending |
| 01-06-xx | 06 | 2 | VERIFY-06 | smoke | Run all 4 scripts, then re-run test suite | YES | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files needed for this phase. Manual verification is the primary method for VERIFY-02 through VERIFY-05.

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

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
