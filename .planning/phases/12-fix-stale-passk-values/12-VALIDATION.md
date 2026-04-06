---
phase: 12
slug: fix-stale-passk-values
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-05
validated: 2026-04-05
revalidated: 2026-04-05
validator: adversarial-validator + nyquist-auditor
verdict: PASS
---

# Phase 12 Adversarial Validation Report

**Validator:** adversarial-validator
**Date:** 2026-04-05
**Scope:** 5 commits (b47119d, c7de043, 473276d, 1adaf32, f086461) updating paper.tex from 480-task to 710-task scope

---

## Wave 1: Fast Checks (Diff Review + Security Scan)

### Diff Review: PASS
- All 5 commits touch only expected files: `docs/paper/latex/paper.tex` and `.planning/` directory
- One additional commit (dd681ca) updates 7 canonical docs -- unrelated to Phase 12 but clean
- LaTeX structure verified balanced: 17 table environments, 17 tabular environments, 17 toprule/bottomrule pairs
- No accidentally deleted content; all changes are numerical updates or table expansions

### Security Scan: PASS
- No API keys, secrets, passwords, or credentials in any `.planning/` files
- No sensitive paths or tokens leaked

**Wave 1 Overall: PASS**

---

## Wave 2: Medium Checks (Regression + Git History)

### Planning Infrastructure: PASS (with fixes applied)
- STATE.md: Phase 12 marked complete, VERIFY-01 satisfied
- STATE.md frontmatter: `percent: 100`, `completed_plans: 24`, `total_plans: 24` -- correct
- **FIX APPLIED:** STATE.md progress bar showed `[..........] 0%` despite `percent: 100` -- fixed to `[######....] 64%`
- **FIX APPLIED:** ROADMAP.md dependency graph had `Phase 12` without `(DONE)` marker -- fixed to `Phase 12 (DONE)`
- REQUIREMENTS.md: VERIFY-01 correctly marked `[x]` Complete
- Both SUMMARY files well-formed with frontmatter and Self-Check sections

### Git History Audit: PASS
- All 5 commits exist and are well-structured
- Commit messages accurately describe changes
- No unrelated changes mixed into Phase 12 commits

**Wave 2 Overall: PASS (after fixes)**

---

## Wave 3: Deep Consistency Checks

### Per-Kernel Table (31 rows): PASS
- All 31 kernel rows verified against `paper_data.json > primary_campaign > by_kernel`
- Total/PASS/Fail/Rate all match for every row
- Sum verification: 272 total PASS, 710 total tasks confirmed
- Tier membership: 17 easy + 7 medium + 7 hard = 31 (provenance comment correct)

### Direction Rates Table: PASS
- All 6 standard directions verified against paper_data.json
- L0 rates verified for all directions
- Task sum: 120+120+90+90+100+100=620 (standard) + 40+50=90 (case study) = 710

### McNemar Tests: PASS
- cuda-omp: n=24, p=0.6875, h=-0.1724
- cuda-opencl: n=20, p=0.6875, h=0.2838
- omp-opencl: n=18, p=1.0, h=0.1157

### Augmentation (Cochran-Armitage): PASS
- z=0.0, p=1.0, n_kernels=24, pass_counts=[16,14,17,14,16]

### Overall Status Distribution: PASS
- 272+241+144+51+1+1=710
- BUILD_FAIL 55.0%, RUN_FAIL 20.3%, VERIFY_FAIL 7.2% of total

### Self-Repair: PASS
- 160 first-attempt, 112 repaired, 7 regressions, 392 persistent, 550 initially-failing
- 20.4% repair rate, 70.0% relative improvement
- BUILD_FAIL repair: 72/346=20.8%

### Direction Asymmetry Gaps: PASS
- 11.7pp, 11.1pp, 14.0pp, 58.2pp all correct

### OpenCL-to-CUDA BUILD_FAIL: PASS
- Verified from raw result files: 81/100=81.0% (after excluding 3 KNOWN_FAIL kernels)

### Stale Value Sweep: PASS
- All 14 stale patterns return 0 hits

**Wave 3 Overall: PASS**

---

## Wave 4: Adversarial Review

### Wilson CI Rounding: FLAG (minor)

8 Wilson CI values in the per-kernel table have borderline rounding discrepancies:

| Kernel(s) | Paper CI | Computed CI | Exact value | Issue |
|-----------|----------|-------------|-------------|-------|
| lud, nw, pathfinder (15/30) | [33.1%, 66.8%] | [33.2%, 66.8%] | 33.1539% | Rounds to 33.2 at 1dp |
| heartwall, myocyte, rsbench, xsbench (0/30) | [0.0%, 11.3%] | [0.0%, 11.4%] | 11.3517% | Rounds to 11.4 at 1dp |
| mixbench (8/30) | [14.2%, 44.5%] | [14.2%, 44.4%] | 44.4417% | Rounds to 44.4 at 1dp |

**Severity: FLAG.** These are regressions from the old paper's correct values.

### Tier Counts: PASS
- 17 easy + 7 medium + 7 hard = 31 confirmed against data
- Text correctly says "Seven" for both medium and hard tiers
- Note: intermediate commit had "Six"/"Eight" but final commit corrected

### Statistical Claims: PASS
- All p-values, z-scores, effect sizes mathematically valid
- Cochran-Armitage z=0.0 correct for symmetric pass counts

**Wave 4 Overall: FLAG (CI rounding only)**

---

## Summary

| Wave | Result | Details |
|------|--------|---------|
| Wave 1 | **PASS** | Clean diff, no security issues |
| Wave 2 | **PASS** (fixes applied) | STATE.md + ROADMAP.md fixed |
| Wave 3 | **PASS** | All numbers verified against paper_data.json |
| Wave 4 | **PASS** (FLAG resolved) | 8 Wilson CI values corrected in commit d1b1bc5 |
| **Overall** | **PASS** | All waves pass; Nyquist-compliant |

## Fixes Applied by Validator

1. STATE.md line 33: Progress bar 0% -> 64%
2. ROADMAP.md line 125: Phase 12 marked (DONE)

## Issues for Reviewer Teammate (paper.tex)

1. ~~**FLAG:** 8 Wilson CI cells regressed from correct rounding~~ — **RESOLVED** by commit `d1b1bc5` (all 8 values corrected to match paper_data.json exact Wilson CI bounds)

---

## Nyquist Validation Audit 2026-04-05

### Requirement-to-Verification Map

| Requirement | Task | Verification Method | Status |
|---|---|---|---|
| VERIFY-01: Abstract numbers | Plan 01, Task 1 | grep sweep + adversarial Wave 3 | COVERED |
| VERIFY-01: S1/S5 numbers | Plan 01, Task 1 | grep sweep + 77 provenance comments | COVERED |
| VERIFY-01: S6.1-6.2 | Plan 01, Task 2 | grep sweep + adversarial Wave 3 | COVERED |
| VERIFY-01: S6.4-6.5 | Plan 01, Task 3 | grep sweep + adversarial Wave 3 | COVERED |
| VERIFY-01: S6.3 per-kernel (31 rows) | Plan 02, Task 1 | adversarial Wave 3 (all 31 rows vs paper_data.json) | COVERED |
| VERIFY-01: S6.6-6.8 direction/stats | Plan 02, Task 1 | grep sweep + adversarial Wave 3 | COVERED |
| VERIFY-01: S7-S8 consistency | Plan 02, Task 2 | grep sweep + 14-pattern stale-value sweep | COVERED |
| Wilson CI rounding (8 cells) | FLAG → commit d1b1bc5 | Verified values match paper_data.json exact bounds | COVERED |
| Cross-section consistency | Plan 02, Task 2 | 5 key values verified across all sections | COVERED |

### Test Infrastructure

| Type | Tool | Scope |
|---|---|---|
| Stale-value sweep | grep (14 patterns) | All sections of paper.tex |
| Per-cell verification | adversarial validator | 31 kernel rows, direction tables, statistical claims |
| Provenance tracing | grep "src: paper_data.json" | 77 provenance comments linking numbers to JSON field paths |
| Cross-section consistency | grep (5 key values) | Abstract, S1, S6, S7, S8 |

### Audit Metrics

| Metric | Count |
|---|---|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |
| FLAG items resolved | 1 (Wilson CI rounding — commit d1b1bc5) |

### Sign-Off

Phase 12 is **Nyquist-compliant**. All requirements (VERIFY-01) have automated verification.
No code was changed — only `docs/paper/latex/paper.tex` was modified. Verification is
grep-based (14 stale patterns + 5 consistency values + 77 provenance comments) rather than
pytest/jest, which is appropriate for a paper-editing phase.
