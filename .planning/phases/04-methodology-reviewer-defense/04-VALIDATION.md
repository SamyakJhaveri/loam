---
phase: 4
slug: methodology-reviewer-defense
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
validated: 2026-04-05
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Manual LaTeX compilation + grep verification |
| **Config file** | None (paper.tex is the target) |
| **Quick run command** | `grep -cin "Fisher" docs/paper/latex/paper.tex` (should return 0 after edit) |
| **Full suite command** | See per-requirement checks below |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Grep verification of each METHOD edit
- **After every plan wave:** Full grep sweep for Fisher remnants, Bonferroni consistency, provenance comments
- **Before `/gsd-verify-work`:** All 8 requirement greps pass + no regression in existing paper text
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | METHOD-01 | — | N/A | grep | `grep -c "orthogonal competencies" docs/paper/latex/paper.tex` (expect 1+) | N/A | ✅ green (1) |
| 04-01-02 | 01 | 1 | METHOD-01 | — | N/A | grep | `grep -c "64.2" docs/paper/latex/paper.tex` (expect 1+) | N/A | ✅ green (2) |
| 04-02-01 | 02 | 1 | METHOD-02 | — | N/A | grep | `grep -c "Fisher" docs/paper/latex/paper.tex` (expect 0) | N/A | ✅ green (0) |
| 04-02-02 | 02 | 1 | METHOD-02 | — | N/A | grep | `grep -c "McNemar" docs/paper/latex/paper.tex` (expect 5+) | N/A | ✅ green (11) |
| 04-02-03 | 02 | 1 | METHOD-02/D-07b | — | N/A | grep | `grep -c "0.0125" docs/paper/latex/paper.tex` (expect 3+) | N/A | ✅ green (7) |
| 04-03-01 | 02 | 1 | METHOD-03 | — | N/A | grep | `grep -c "9c10d3ea" docs/paper/latex/paper.tex` (expect 1+) | N/A | ✅ green (2) |
| 04-04-01 | 01 | 1 | METHOD-04 | — | N/A | grep | `grep -ci "compilation-only" docs/paper/latex/paper.tex` (expect 1+) | N/A | ✅ green (1) |
| 04-04-02 | 01 | 1 | METHOD-04 | — | N/A | grep | `grep -c "7.3" docs/paper/latex/paper.tex` (expect 1+) | N/A | ✅ green (12) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. Phase 4 edits existing paper.tex — no test infrastructure needed.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Paragraph reads well in context | All METHOD reqs | Prose quality requires human judgment | Read the inserted paragraphs in the compiled PDF |
| LaTeX compiles without errors | All METHOD reqs | Full LaTeX build is not automated in CI | `cd docs/paper/latex && pdflatex paper.tex` |
| No regression in surrounding text | All METHOD reqs | Semantic coherence of edits | Visually inspect sections around each edit point |

---

## Validation Audit 2026-04-05

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

**Notes:**
- All 8 automated checks pass against current `paper.tex` (commit 5823fed)
- Fixed `04-04-01` check: changed `grep -c` to `grep -ci` (case-insensitive) because paper uses `Compilation-only` (capital C) at sentence start
- `04-04-02` count (12) includes false positives from other numbers containing "7.3" (e.g., 37.3%, 17.3%); the actual VERIFY_FAIL 7.3% rate is confirmed present at lines 312-314
- All METHOD requirements verified complete: METHOD-01 (Plan 01), METHOD-02 (Plan 02), METHOD-03 (Plan 02), METHOD-04 (Plan 01)

### Requirement Completion Cross-Reference

| Requirement | Plan | Tasks | Commits | Verified |
|-------------|------|-------|---------|----------|
| METHOD-01 | 01 | 04-01-01, 04-01-02 | 945268a | ✅ |
| METHOD-02 | 02 | 04-02-01, 04-02-02, 04-02-03 | c1d8c7b | ✅ |
| METHOD-03 | 02 | 04-03-01 | 379bee0 | ✅ |
| METHOD-04 | 01 | 04-04-01, 04-04-02 | f89b5da | ✅ |
