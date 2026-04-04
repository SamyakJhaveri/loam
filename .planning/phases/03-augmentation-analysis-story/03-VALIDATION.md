---
phase: 3
slug: augmentation-analysis-story
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-03
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml (pytest section) |
| **Quick run command** | `python3 -m pytest scripts/analysis/test_augmentation_analysis.py -x -v` |
| **Full suite command** | `python3 -m pytest scripts/analysis/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest scripts/analysis/test_augmentation_analysis.py -x -v`
- **After every plan wave:** Run `python3 -m pytest scripts/analysis/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | AUG-01 | unit | `pytest scripts/analysis/test_augmentation_analysis.py::test_matrix_structure -x` | Wave 0 | pending |
| 03-01-02 | 01 | 1 | AUG-01 | integration | `pytest scripts/analysis/test_augmentation_analysis.py::test_kernel_count_matches_disk -x` | Wave 0 | pending |
| 03-01-03 | 01 | 1 | AUG-01 | integration | `pytest scripts/analysis/test_augmentation_analysis.py::test_status_values_match_raw -x` | Wave 0 | pending |
| 03-01-04 | 01 | 1 | AUG-02 | unit | `pytest scripts/analysis/test_augmentation_analysis.py::test_pattern_classification -x` | Wave 0 | pending |
| 03-02-01 | 02 | 1 | AUG-04 | smoke | `pytest scripts/analysis/test_augmentation_analysis.py::test_figures_exist -x` | Wave 0 | pending |
| 03-02-02 | 02 | 1 | AUG-04 | unit | `pytest scripts/analysis/test_augmentation_analysis.py::test_okabe_ito_palette -x` | Wave 0 | pending |
| 03-03-01 | 03 | 2 | AUG-03 | manual | Manual: verify LASSI paragraphs in paper.tex | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `scripts/analysis/test_augmentation_analysis.py` — stubs for AUG-01 through AUG-04
- [ ] Framework install: None needed — pytest 9.0.2 already available

*Existing infrastructure covers framework requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| LASSI positioning paragraphs in paper.tex | AUG-03 | LaTeX prose content — no automated check for quality/framing | Verify paper.tex Section 7.4 contains complementary positioning paragraphs |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
