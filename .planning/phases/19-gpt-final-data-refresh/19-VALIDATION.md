---
phase: 19
slug: gpt-final-data-refresh
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-08
---

# Phase 19 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (in venv) |
| **Config file** | none (pytest auto-discovers) |
| **Quick run command** | `python3 -m pytest scripts/analysis/ -q` |
| **Full suite command** | `/validate` (4-wave validation loop) |
| **Estimated runtime** | ~120 seconds (analysis scripts) + ~180s (validate) |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m pytest scripts/analysis/ -q` (note: these tests validate Qwen augmentation data only — they will pass regardless of GPT changes; they are a sanity check, not a substitute for /validate)
- **After every plan wave:** Run `/validate` (4-wave loop — this is the only command that writes the `.validation_passed` sentinel required for commit)
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | D-01 | T-19-01 | Files staged correctly | smoke | `git diff --cached --stat results/evaluation/azure-gpt-4.1-mini/ \| tail -1` | N/A (git) | ⬜ pending |
| 19-01-02 | 01 | 1 | D-01 | T-19-03 | Analysis files regenerated with today's date | smoke | `python3 -c "import json; d=json.load(open('results/analysis/paper_data_gpt41mini.json')); print(d['generated_at'])"` | N/A | ⬜ pending |
| 19-01-03 | 01 | 1 | D-02 | T-19-02 | All figures have recent mtime | smoke | `stat -c '%Y' docs/paper/figures/f*_*.pdf \| sort -n \| head -1` | N/A | ⬜ pending |
| 19-01-04 | 01 | 1 | D-03 | — | 19-STRUCTURAL-CHANGES.md produced | smoke | `test -f .planning/phases/19-gpt-final-data-refresh/19-STRUCTURAL-CHANGES.md` | Wave 0 | ⬜ pending |
| 19-01-05 | 01 | 1 | D-04 | — | Validation passes AND sentinel written | e2e | `/validate` then `test -f .validation_passed && echo OK` | N/A | ⬜ pending |
| 19-01-06 | 01 | 1 | D-01 | T-19-01 | Direction set change: omp_target-to-cuda present, cuda-to-omp_target absent | smoke | `python3 -c "import json; d=json.load(open('results/analysis/paper_data_gpt41mini.json')); dirs=d['primary_campaign']['by_direction']; print('omp_target-to-cuda' in dirs, 'cuda-to-omp_target' not in dirs)"` must print `True True` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements.* No new test files needed — analysis scripts and figure generation are tested by their own execution (exit code 0 = pass).

**Important:** `python3 -m pytest scripts/analysis/ -q` runs tests that validate Qwen augmentation data only (augmentation_per_kernel_matrix.json, etc.). These tests are unaffected by GPT eval changes and will pass either way. They are a sanity check for the test infrastructure, not a gate on Phase 19 correctness. The real gate is `/validate`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 19-STRUCTURAL-CHANGES.md content accuracy | D-03 | Requires human review of paper.tex locations | Verify each listed section/line reference matches actual paper.tex content |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 120s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
