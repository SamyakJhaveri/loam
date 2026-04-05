---
phase: 8
slug: figure-regeneration
status: validated
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-04
updated: 2026-04-04
---

# Phase 8 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual visual inspection + script exit code |
| **Config file** | None (script uses argparse) |
| **Quick run command** | `python3 scripts/generate_paper_figures.py --project-root . --figure F2 -v` |
| **Full suite command** | `python3 scripts/generate_paper_figures.py --project-root . --figure all -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `--figure <specific>` for the modified figure
- **After every plan wave:** Run `--figure all -v` and verify all outputs exist
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | FIG-05 | — | N/A | smoke | `python3 scripts/generate_paper_figures.py --project-root . --figure F3 -v` | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | FIG-06 | — | N/A | smoke | `python3 scripts/generate_paper_figures.py --project-root . --figure F4 -v` | ✅ | ✅ green |
| 08-01-03 | 01 | 1 | FIG-01 | — | N/A | smoke | `python3 scripts/generate_paper_figures.py --project-root . --figure F6 -v` | ✅ | ✅ green |
| 08-01-04 | 01 | 1 | FIG-01 | — | N/A | smoke | `python3 scripts/generate_paper_figures.py --project-root . --figure F7 -v` | ✅ | ✅ green |
| 08-02-01 | 02 | 1 | FIG-01 | — | N/A | smoke | `ls docs/paper/figures/{f2,f3,f4,f5,f6,f7}_*.pdf` | ✅ | ✅ green |
| 08-02-02 | 02 | 1 | FIG-02 | — | N/A | smoke | `ls docs/paper/figures/{c1,c2,c3,c4}_*.pdf` | ✅ | ✅ green |
| 08-02-03 | 02 | 1 | FIG-03 | — | N/A | smoke | `cat docs/paper/figures/t2_model_comparison.tex` | ✅ | ✅ green |
| 08-02-04 | 02 | 1 | FIG-04 | — | N/A | smoke | `ls docs/paper/figures/*.png \| wc -l` | ✅ | ✅ green |
| 08-02-05 | 02 | 1 | FIG-07 | — | N/A | smoke | `python3 scripts/generate_paper_figures.py --project-root . 2>&1 \| grep -i warn` | ✅ | ✅ green |
| G1 | 01 | 1 | FIG-01 | — | N/A | unit | `python3 -m pytest scripts/evaluation/test_generate_paper_figures.py::test_model_constants_reflect_two_model_layout -v` | ✅ | ✅ green |
| G2 | 01 | 1 | FIG-05 | — | N/A | integration | `python3 -m pytest scripts/evaluation/test_generate_paper_figures.py::test_f3_heatmap_kernel_count -v` | ✅ | ✅ green |
| G3 | 01 | 1 | FIG-06 | — | N/A | unit | `python3 -m pytest scripts/evaluation/test_generate_paper_figures.py::test_suite_order_contains_all_five_suites -v` | ✅ | ✅ green |
| G4 | 02 | 1 | FIG-03 | — | N/A | integration | `python3 -m pytest scripts/evaluation/test_generate_paper_figures.py::test_t2_table_has_two_model_layout -v` | ✅ | ✅ green |
| G5 | 02 | 1 | FIG-04 | — | N/A | unit | `python3 -m pytest scripts/evaluation/test_generate_paper_figures.py::test_pdf_png_parity -v` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| F3 heatmap shows all suite kernels grouped correctly | FIG-05 | Visual layout verification | Open f3_kernel_model_heatmap.pdf and verify suite grouping labels and divider lines |
| F6 shows cross-suite bar chart (not XSBench-specific) | FIG-01, FIG-06 | Visual design verification | Open f6 PDF and verify 5 suite bars with CIs |
| GPT-4.1 mini cells show gray/hatched N/A | FIG-01 | Visual rendering check | Verify gray hatched cells in F3, F7 |
| No empty subplots or missing data placeholders | FIG-07 | Visual completeness | Scroll through all PDFs checking for blank areas |

---

## Validation Audit 2026-04-04

| Metric | Count |
|--------|-------|
| Gaps found | 5 |
| Resolved | 5 |
| Escalated | 0 |

**Tests added:** 5 pytest tests in `scripts/evaluation/test_generate_paper_figures.py` (G1-G5).
**Total tests:** 9 (4 pre-existing + 5 new). All passing.
