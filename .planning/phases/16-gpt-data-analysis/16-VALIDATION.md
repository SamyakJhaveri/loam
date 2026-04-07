---
phase: 16
slug: gpt-data-analysis
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-07
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (installed in venv) + inline smoke tests |
| **Config file** | None specific to analysis scripts |
| **Quick run command** | `python3 -c "import json; d=json.load(open('results/evaluation/eval_summary.json')); assert len(d['by_model'])==2"` |
| **Full suite command** | `python3 -m pytest scripts/analysis/ -x` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run inline smoke test for that task's output
- **After every plan wave:** Run `python3 -m pytest scripts/analysis/ -x`
- **Before `/gsd-verify-work`:** Full suite must be green + all 7 artifacts verified
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | T1 eval_summary | — | N/A | smoke | `python3 -c "import json; d=json.load(open('results/evaluation/eval_summary.json')); assert len(d['by_model'])==2"` | N/A (inline) | ⬜ pending |
| 16-01-02 | 01 | 1 | T2 paper_data GPT | — | N/A | smoke | `python3 -c "import json; d=json.load(open('results/analysis/paper_data_gpt41mini.json')); assert 'pass_rate' in d['primary_campaign']['overall']"` | N/A (inline) | ⬜ pending |
| 16-01-03 | 01 | 1 | T3 error_taxonomy GPT | — | N/A | smoke | `python3 -c "import json; d=json.load(open('results/analysis/error_taxonomy.json')); assert 'azure-gpt-4.1-mini' in d['per_model']"` | N/A (inline) | ⬜ pending |
| 16-01-04 | 01 | 2 | T3b schema gate | — | N/A | smoke | `python3 -c "import json; d=json.load(open('results/analysis/paper_data_gpt41mini.json')); assert 'by_direction' in d['primary_campaign']"` | N/A (inline) | ⬜ pending |
| 16-01-05 | 01 | 3 | T4 cross_model_comparison | — | N/A | smoke | `python3 -c "import json; d=json.load(open('results/analysis/cross_model_comparison.json')); assert 'chi_squared' in d.get('overall',{})"` | N/A (inline) | ⬜ pending |
| 16-01-06 | 01 | 3 | T5 figures regenerated | — | N/A | visual | Manual check of f3, f4, f7 PDFs for dual-model data | Manual | ⬜ pending |
| 16-01-07 | 01 | 4 | T6 coverage gaps | — | N/A | file | `test -f results/analysis/coverage_gaps.md` | N/A (inline) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- Existing infrastructure covers all phase requirements — no new test files needed
- Inline smoke tests are sufficient for pipeline verification
- Existing tests: `test_generate_paper_data.py`, `test_build_error_taxonomy.py` already exist

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Figures show dual-model data | T5 | Visual verification of PDF charts | Open f3_kernel_model_heatmap.pdf, f4_failure_taxonomy.pdf, f7_augmentation_robustness.pdf — confirm GPT data appears in sky blue (#56B4E9), not grey or "pending" |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
