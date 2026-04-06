---
phase: 13
slug: paper-figure-table-wiring
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-06
---

# Phase 13 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | grep-based verification (no LaTeX compiler on system) |
| **Config file** | none — no test framework needed |
| **Quick run command** | `grep -n 'fig:xsbench\|Triple-panel\|TODO.*drawio\|fbox.*placeholder\|fbox.*Missing' docs/paper/latex/paper.tex docs/paper/latex/appendices.tex` |
| **Full suite command** | `grep -rn 'fig:xsbench\|fig:api-network\|fig:bipartite\|fig:quality-tiers\|f6_xsbench\|Triple-panel\|TODO.*drawio\|fbox.*placeholder\|fbox.*Missing\|quality_tiers' docs/paper/latex/*.tex` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command (grep for stale references)
- **After every plan wave:** Run full suite command (all stale patterns)
- **Before `/gsd-verify-work`:** Full suite must return zero matches
- **Max feedback latency:** 2 seconds

---

## Per-Task Verification Map

### Plan 01 (paper.tex edits)

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-01-01 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -cP '^\s*\\\\includegraphics.*parbench_architecture' docs/paper/latex/paper.tex` (expect 1; must NOT match commented `% \includegraphics`) | ✅ | ⬜ pending |
| 13-01-02 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'Triple-panel' docs/paper/latex/paper.tex` (expect 0) | ✅ | ⬜ pending |
| 13-01-03 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:aug-heatmap' docs/paper/latex/paper.tex` (expect 1) | ✅ | ⬜ pending |
| 13-01-04 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:cross-suite' docs/paper/latex/paper.tex` (expect 1) | ✅ | ⬜ pending |
| 13-01-05 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'TODO.*drawio' docs/paper/latex/paper.tex` (expect 0) | ✅ | ⬜ pending |
| 13-01-06 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fbox.*placeholder' docs/paper/latex/paper.tex` (expect 0) | ✅ | ⬜ pending |
| 13-01-07 | 01 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:xsbench' docs/paper/latex/paper.tex` (expect 0) | ✅ | ⬜ pending |

### Plan 02 (appendices.tex edits + file deletions)

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 13-02-01 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'f6_cross_suite_comparison' docs/paper/latex/appendices.tex` (expect 1) | ✅ | ⬜ pending |
| 13-02-02 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:cross-suite' docs/paper/latex/appendices.tex` (expect 1) | ✅ | ⬜ pending |
| 13-02-03 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'aug_heatmap' docs/paper/latex/appendices.tex` (expect >= 1) | ✅ | ⬜ pending |
| 13-02-04 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:aug-heatmap' docs/paper/latex/appendices.tex` (expect 1) | ✅ | ⬜ pending |
| 13-02-05 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:xsbench' docs/paper/latex/appendices.tex` (expect 0) | ✅ | ⬜ pending |
| 13-02-06 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:api-network' docs/paper/latex/appendices.tex` (expect 0) | ✅ | ⬜ pending |
| 13-02-07 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:bipartite' docs/paper/latex/appendices.tex` (expect 0) | ✅ | ⬜ pending |
| 13-02-08 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fig:quality-tiers' docs/paper/latex/appendices.tex` (expect 0) | ✅ | ⬜ pending |
| 13-02-09 | 02 | 1 | AUG-04 | — | N/A | grep | `grep -c 'fbox.*Missing' docs/paper/latex/appendices.tex` (expect 0) | ✅ | ⬜ pending |
| 13-02-10 | 02 | 1 | AUG-04 | — | N/A | file | `test ! -f docs/paper/latex/figures/f6_xsbench_comparison.pdf` | ✅ | ⬜ pending |
| 13-02-11 | 02 | 1 | AUG-04 | — | N/A | file | `test ! -f docs/paper/latex/figures/f6_xsbench_comparison.png` | ✅ | ⬜ pending |
| 13-02-12 | 02 | 1 | AUG-04 | — | N/A | file | `test ! -f docs/paper/figures/t2_model_comparison.tex` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

### Anti-False-Positive Notes

- **13-01-01**: Uses `-P '^\s*\\\\includegraphics'` (PCRE) to match only uncommented lines. Plain `grep 'includegraphics.*parbench_architecture'` would false-positive on the commented-out `% \includegraphics` that exists pre-edit.
- **13-02-09**: Pattern `fbox.*Missing` catches all 3 appendices.tex placeholder blocks. The paper.tex placeholder uses `fbox.*placeholder` (different pattern, covered by 13-01-06).

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No test framework needed — all verifications use grep and file existence checks.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Architecture PDF export | AUG-04 | Requires draw.io desktop (not available via CLI) | User exports `parbench_architecture.drawio` → `docs/paper/latex/figures/parbench_architecture.pdf` before execution |
| LaTeX compilation success | AUG-04 | No pdflatex installed on this machine | Compile paper.tex on a system with LaTeX and verify no warnings |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 2s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
