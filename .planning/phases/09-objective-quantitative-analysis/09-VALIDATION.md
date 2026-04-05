---
phase: 9
slug: objective-quantitative-analysis
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-04
---

# Phase 9 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | pyproject.toml |
| **Quick run command** | `python3 -m pytest scripts/analysis/test_quantitative_findings.py -x` |
| **Full suite command** | `python3 -m pytest scripts/analysis/test_quantitative_findings.py -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest scripts/analysis/test_quantitative_findings.py -x`
- **After every plan wave:** Run `python3 -m pytest scripts/analysis/test_quantitative_findings.py -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 09-01-01 | 01 | 1 | QUANT-01 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_aggregate_pass_rates -x` | Yes | ✅ green |
| 09-01-02 | 01 | 1 | QUANT-02 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_direction_pass_rates -x` | Yes | ✅ green |
| 09-01-03 | 01 | 1 | QUANT-03 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_direction_asymmetry_pairs_on_suite_kernel -x` | Yes | ✅ green |
| 09-01-04 | 01 | 1 | QUANT-04 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_augmentation_trends_per_direction_and_aggregate -x` | Yes | ✅ green |
| 09-01-05 | 01 | 1 | QUANT-05 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_failure_taxonomy_classification -x` | Yes | ✅ green |
| 09-02-01 | 02 | 2 | QUANT-06 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_self_repair -x` | Yes | ✅ green |
| 09-02-02 | 02 | 2 | QUANT-07 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_pass_at_k -x` | Yes | ✅ green |
| 09-02-03 | 02 | 2 | QUANT-08 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_per_kernel_tiers -x` | Yes | ✅ green |
| 09-02-04 | 02 | 2 | QUANT-09 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_complexity_correlation -x` | Yes | ✅ green |
| 09-02-05 | 02 | 2 | QUANT-10 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_cross_suite -x` | Yes | ✅ green |
| 09-02-06 | 02 | 2 | QUANT-11 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_token_cost -x` | Yes | ✅ green |
| 09-02-07 | 02 | 2 | QUANT-12 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_sloc_correlation -x` | Yes | ✅ green |
| 09-02-08 | 02 | 2 | QUANT-13 | — | N/A | unit | `python3 -m pytest scripts/analysis/test_quantitative_findings.py::test_opencl_kernel_only_effect -x` | Yes | ✅ green |
| 09-03-01 | 03 | 2 | QUANT-14 | — | N/A | integration | `python3 scripts/analysis/quantitative_findings.py --project-root /home/samyak/Desktop/parbench_sam --validate` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `scripts/analysis/test_quantitative_findings.py` — tests for QUANT-01 through QUANT-13 (23 tests, all green)
- [ ] End-to-end run: script produces `results/analysis/quantitative_findings.json` with all sections
- [ ] Validation run: `--validate` flag checks 10+ numbers against raw file counts

*Existing infrastructure covers pytest framework. Wave 0 tests added 2026-04-04.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Markdown tables copy-paste correctly into LaTeX | QUANT-14 | Visual formatting check | Copy a table from `.md` into paper.tex, verify alignment |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
