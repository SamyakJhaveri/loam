---
phase: 17
slug: paper-integration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-07
---

# Phase 17 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep-based + LaTeX syntax checks (no pdflatex on Linux) |
| **Config file** | none |
| **Quick run command** | `grep -c '\\\\pending{' docs/paper/latex/paper.tex && grep -c '\\\\tbd' docs/paper/latex/paper.tex` |
| **Full suite command** | `grep -n '\\\\pending{' docs/paper/latex/paper.tex; grep -n '\\\\tbd' docs/paper/latex/paper.tex; grep -c '\\\\begin{' docs/paper/latex/paper.tex; grep -c '\\\\end{' docs/paper/latex/paper.tex` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command (pending/tbd counts)
- **After every plan wave:** Run full suite command (syntax balance check)
- **Before `/gsd-verify-work`:** Full suite must show 0 or 1 pending (line 631 exemption), 0 tbd
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 17-01-01 | 01 | 1 | D-03, D-07 | — | N/A | grep | `grep -c '\\\\pending{' docs/paper/latex/paper.tex` (expect 1) | ✅ | ⬜ pending |
| 17-01-02 | 01 | 1 | D-04 | — | N/A | grep | `grep -c '\\\\tbd' docs/paper/latex/paper.tex` (expect 0) | ✅ | ⬜ pending |
| 17-02-01 | 02 | 2 | D-08 | — | N/A | grep | `grep -c 'Cross-Model Comparison' docs/paper/latex/paper.tex` (expect ≥1) | ✅ | ⬜ pending |
| 17-02-02 | 02 | 2 | D-08 | — | No placeholder stats | grep | `grep -c 'p.*=.*0\\.' docs/paper/latex/paper.tex` (chi-squared present) | ✅ | ⬜ pending |
| 17-03-01 | 03 | 2 | — | — | N/A | grep | `grep -c 'augmentation' docs/paper/latex/paper.tex` | ✅ | ⬜ pending |
| 17-04-01 | 04 | 2 | — | — | N/A | grep | `grep -c 'anonymi' docs/paper/latex/paper.tex` | ✅ | ⬜ pending |
| 17-05-01 | 05 | 3 | D-09 | — | N/A | grep | `grep -c '_qwen.pdf' docs/paper/latex/paper.tex` (expect ≥4) | ✅ | ⬜ pending |
| 17-05-02 | 05 | 3 | D-09 | — | N/A | grep | `grep -c '_gpt.pdf' docs/paper/latex/appendices.tex` (expect ≥4) | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements — grep-based validation needs no setup.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Figure captions include model name | D-09-captions | Caption text varies | Grep for "(Qwen 3.5 397B)" in paper.tex figure environments |
| Aggregate row is sum not average | D-04-aggregate | Arithmetic correctness | Read tab:overall-pass, verify Aggregate = Qwen count + GPT count |
| Section 6.9 framing is benchmark-focused | D-08-framing | Prose judgment | Read Section 6.9, verify no model ranking language |

*All other phase behaviors have automated grep verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
