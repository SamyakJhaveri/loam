---
phase: 7
slug: full-analysis-regeneration
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-04
audited: 2026-04-06
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 + inline python3 -c assertions |
| **Config file** | pyproject.toml |
| **Quick run command** | `python3 -c "import json; d=json.load(open('results/evaluation/eval_summary.json')); print(d['by_model']['together-qwen-3.5-397b-a17b']['total'])"` |
| **Full suite command** | `python3 scripts/analysis/validate_characterization.py --project-root .` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run inline verification for the script just executed
- **After every plan wave:** Run all REGEN verification commands
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 1 | REGEN-01 | — | eval_summary total_tasks > 1000 | smoke | `python3 -c "import json; assert json.load(open('results/evaluation/eval_summary.json'))['by_model']['together-qwen-3.5-397b-a17b']['total'] > 1000"` | N/A (inline) | ✅ green |
| 07-01-02 | 01 | 1 | REGEN-02 | — | Two paper_data files, different scopes | smoke | `python3 -c "import json; r=json.load(open('results/analysis/paper_data_rodinia.json')); f=json.load(open('results/analysis/paper_data.json')); assert r['suite_filter']=='rodinia'; assert f['suite_filter'] is None"` | N/A (inline) | ✅ green |
| 07-01-03 | 01 | 1 | REGEN-03 | — | error_taxonomy has non-Rodinia kernels | smoke | `python3 -c "import json; d=json.load(open('results/analysis/error_taxonomy.json')); assert any(k in d.get('per_kernel',{}) for k in ['floydwarshall','xsbench','rsbench','mixbench'])"` | N/A (inline) | ✅ green |
| 07-01-04 | 01 | 1 | REGEN-04 | — | selfrepair has non-Rodinia kernels | smoke | `python3 -c "import json; d=json.load(open('results/analysis/selfrepair_analysis.json')); assert any(k in d.get('by_kernel',{}) for k in ['floydwarshall','xsbench','rsbench','mixbench'])"` | N/A (inline) | ✅ green |
| 07-01-05 | 01 | 1 | REGEN-05 | — | statistical has non-Rodinia kernels | smoke | `python3 -c "import json; d=json.load(open('results/analysis/statistical_analysis.json')); assert any(k in d.get('wilson_cis',{}).get('by_kernel',{}) for k in ['floydwarshall','xsbench','rsbench','mixbench'])"` | N/A (inline) | ✅ green |
| 07-02-01 | 02 | 1 | REGEN-06 | — | sloc_analysis unchanged | smoke | `md5sum results/analysis/sloc_analysis.json` (compare before/after) | N/A | ✅ green |
| 07-02-02 | 02 | 1 | REGEN-07 | — | token_analysis covers 1000+ tasks | smoke | `python3 -c "import json; assert json.load(open('results/analysis/token_analysis.json'))['total_results'] > 1000"` | N/A (inline) | ✅ green |
| 07-02-03 | 02 | 1 | REGEN-08 | — | characterization validation passes | smoke | `python3 scripts/analysis/validate_characterization.py --project-root .` | Exists | ✅ green |
| 07-02-04 | 02 | 1 | REGEN-09 | — | translation_complexity 5 suites | smoke | `python3 -c "import csv; from collections import Counter; r=csv.DictReader(open('results/evaluation/translation_complexity.csv')); assert len(Counter(row['suite'] for row in r)) == 5"` | N/A (inline) | ✅ green |
| 07-02-05 | 02 | 1 | REGEN-10 | — | augmentation matrix (conditional) | manual-only | Check Phase 3 status; validate existing file | N/A | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. No new test files needed — all verification is inline python3 assertions against output JSON files.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Augmentation matrix regeneration | REGEN-10 | Conditional on Phase 3 completion; no standalone script | Check Phase 3 status in STATE.md; if complete, verify `augmentation_per_kernel_matrix.json` exists and is recent |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** 2026-04-06

---

## Validation Audit 2026-04-06

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated to manual-only | 0 |
| Tasks verified green | 9 automated + 1 manual |
| Notes | REGEN-10 manual: augmentation_per_kernel_matrix.json exists, 26 kernels in per_kernel (primary_matrix.kernel_count=26). REGEN-01 through REGEN-09 all pass inline assertions. |
