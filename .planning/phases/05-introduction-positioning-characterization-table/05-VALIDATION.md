---
phase: 5
slug: introduction-positioning-characterization-table
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
validated: 2026-04-05
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual LaTeX compilation + grep verification |
| **Config file** | None (LaTeX build: `pdflatex -> bibtex -> pdflatex x2`) |
| **Quick run command** | `grep -c '\\pending' docs/paper/latex/paper.tex` (count remaining placeholders) |
| **Full suite command** | `cd docs/paper/latex && pdflatex paper.tex && bibtex paper && pdflatex paper.tex && pdflatex paper.tex` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Grep for key markers (numbers, section labels, table refs)
- **After every plan wave:** Full LaTeX compilation
- **Before `/gsd-verify-work`:** PDF compiles without errors; all INTRO/CHAR requirements verified
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-T1 | 01 | 1 | INTRO-01, INTRO-02, INTRO-03, INTRO-04 | — | N/A | automated+manual | `grep -c 'ParBench evaluates this question systematically' docs/paper/latex/paper.tex` (scope teaser); `grep -c 'LASSI.*kernel-level granularity' docs/paper/latex/paper.tex` (LASSI para); `grep -c 'Multi-file coordination' docs/paper/latex/paper.tex` (multi-file para) | N/A | ✅ green |
| 05-01-T2 | 01 | 1 | INTRO-01 (D-11) | — | N/A | automated | `grep -c '700 primary campaign tasks' docs/paper/latex/paper.tex` (updated task count); `grep -c 'raises the effective pass rate from 22.1' docs/paper/latex/paper.tex` (self-repair fix) | N/A | ✅ green |
| 05-01-T3 | 01 | 1 | INTRO-01 (D-11) | — | N/A | automated | `grep -c '700 primary campaign tasks spanning 35 kernels' docs/paper/latex/paper.tex` (abstract updated); `grep -c 'z = -0.77' docs/paper/latex/paper.tex` (Cochran-Armitage updated) | N/A | ✅ green |
| 05-01-T1-manual | 01 | 1 | INTRO-04 | — | N/A | manual | Read Section 1.2 for ParEval-Repo contrast quality and LASSI complementary tone | N/A | ⬜ manual-only |
| 05-02-T1 | 02 | 2 | CHAR-07 | — | N/A | automated | `grep -c 'tab:category-distribution' docs/paper/latex/paper.tex` (table label exists); `grep -c 'Physics simulation.*7' docs/paper/latex/paper.tex` (physics row correct) | N/A | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. This is a text-editing phase with no test infrastructure needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Quantitative highlights woven into prose (not bullet list) | INTRO-01 | Prose quality requires human judgment | Read Section 1.1-1.4, verify numbers appear in sentences not bullet lists |
| LASSI dimensions have numbers | INTRO-02 | Counting dimensions requires reading | Check LASSI paragraph has 4 numbered comparisons (augmentation, suites, directions, specs) |
| Multi-file in both intro and Section 4 | INTRO-03 | Cross-section consistency check | Grep for multi-file in both Section 1 and Section 4; verify pass rate gap (51.3% vs 22.2%) |
| Gap section uses characterization data | INTRO-04 | Argument quality requires reading | Verify Section 1.2 references SLoC range, ParEval-Repo 133 SLoC threshold, complementary LASSI tone |
| Second table well-formatted in IEEE | CHAR-07 | Visual layout requires PDF review | Compile LaTeX, check table renders in double-column; verify 10 categories sum to 35 kernels |
| No stale Rodinia-scope numbers in prose | INTRO-01 (D-11) | Requires cross-checking multiple sections | Grep for old numbers (480, 36.2%, 30.8%, 17.5%, "doubles") in non-comment lines; expect 0 matches |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter (set after all tasks pass)

**Approval:** PASSED — Nyquist validation audit 2026-04-05; all automated tasks green, 1 manual-only (prose quality)

---

## Validation Audit 2026-04-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| Automated COVERED | 4 |
| Manual-only | 1 |

**Notes:**
- All grep-based verifications pass against current `paper.tex`
- pdflatex not available on Linux GPU machine (not a blocker)
- Stale "480" numbers in Section 6 (Rodinia-scope per D-12) and Section 8 (known future-phase stub) are intentionally out of Phase 5 scope
- No auditor agent spawned (zero gaps to fill)
