---
phase: 01-data-verification-ground-truth
verified: 2026-04-03T23:30:00Z
status: passed
score: 10/10 must-haves verified
gaps:
  - truth: "Paper pass@k values (426 tasks, 142 pairs, 103/22/17 categories, 19.7%/27.5% macro) match regenerated paper_data.json"
    status: resolved
    reason: "Fixed generate_paper_data.py to apply --suite filter only to primary campaign, not pass@k. Regenerated paper_data.json now has 426 pass@k tasks (all suites) matching paper.tex exactly. Commit bdc9f4f."
---

# Phase 1: Data Verification & Ground Truth Verification Report

**Phase Goal:** Every numerical claim and table in Sections 1-7 is verified against actual data files on disk, with no stale or incorrect values remaining, and all analysis files regenerated fresh
**Verified:** 2026-04-03T23:30:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Abstract headline numbers (36.2%, 30.8%, 9.8%, 65.0%, 68.8%) match paper_data.json | VERIFIED | paper_data.json: pass_rate=0.3625 (36.2%), by_status BUILD_FAIL=148 (30.8%), VERIFY_FAIL=47 (9.8%), cuda-to-omp pass_rate=0.65 (65.0%), L0 cuda-to-omp=11/16 (68.8%). All values present in paper.tex with matching `% src:` comments. |
| 2 | S1 Introduction inline numbers match paper_data.json | VERIFIED | All pass rates, CIs ([32.1%, 40.6%]), self-repair (17.5% to 36.2%, 90/396, 5 regressions), Cochran-Armitage (z=-0.17, p=0.87), Cohen's h (0.26-0.31) confirmed against paper_data.json fields. |
| 3 | S3 augmentation level definitions table matches LEVEL_FRACTIONS in augment_dataset.py | VERIFIED | LEVEL_FRACTIONS = {1: 0.0, 2: 0.33, 3: 0.66, 4: 1.0} at augment_dataset.py line 111. Paper tab:augmentation-levels (line 337): L1=1 site, L2=33%, L3=66%, L4=100%. Match confirmed. |
| 4 | S3/S4 spec count claims (96, 88, 68) verified against spec files on disk | VERIFIED | Disk counts: Rodinia=60, HeCBench=135 (25 curated), XSBench=4, RSBench=4, mixbench=3. 60+25+4+4+3=96 total. 88 PASS (96-8 KNOWN_FAIL). 68 non-KNOWN_FAIL augmentation-verified (54+4+3+3+4). |
| 5 | tab:suite-summary row values match spec file counts and manifest | VERIFIED | Plan 02 verified all 5 suite rows cell-by-cell. Fixed L0 pair count (142->96) and OMP-target count (22->12). 26 source comments added. |
| 6 | tab:hardware matches live system and tab:model-config has Qwen+GPT-4.1-mini only | VERIFIED | RTX 4070 12GB, Ryzen 9 7900X, Ubuntu 24.04, nvcc 12.3, GCC 12.4, Python 3.12.3 all match. Model table has exactly 2 rows. One legitimate "Claude Opus, Gemma" reference in S7 future work (not a remnant). |
| 7 | S6.1-S6.5 tables verified cell-by-cell with independent raw-JSON spot-check | VERIFIED | Independent count: 480 total, 174 PASS, 148 BUILD_FAIL, 110 RUN_FAIL, 47 VERIFY_FAIL, 1 EXTRACTION_FAIL. Self-repair accounting: 84+90+271+5+30=480. Per-kernel tiers: 9 easy + 5 medium + 4 hard = 18. 43 source comments in S6. |
| 8 | S6.6-S6.8 direction rates, McNemar, pass@k tables verified | PARTIAL | Direction rates and McNemar/Bonferroni stats fully verified. However, pass@k values in paper.tex are STALE -- see gap below. |
| 9 | All analysis files (paper_data.json, statistical_analysis.json, selfrepair_analysis.json) regenerated fresh | VERIFIED | paper_data.json: 2026-04-03 15:57, statistical_analysis.json: 2026-04-03 15:57, selfrepair_analysis.json: 2026-04-03 15:58. Suite filter=rodinia. Primary campaign: 480 tasks, 174 PASS, 36.2%. |
| 10 | All paper figures regenerated and are non-empty valid PDFs | VERIFIED | 10 PDF figures in docs/paper/figures/ (F2-F7, C1-C4). All have valid %PDF magic bytes. No empty files found. |

**Score:** 9/10 truths verified (1 partial due to pass@k staleness)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `docs/paper/latex/paper.tex` | Verified sections with `% src:` comments | VERIFIED | 123 total `% src:` references. 28 in Abstract/S1/S3, 24 in S4/S5, 26 in S6.1-S6.5, 45 in S6.6-S6.8/S7. |
| `results/analysis/paper_data.json` | Freshly regenerated, pass_rate=0.3625 | VERIFIED | Regenerated 2026-04-03 15:57. total=480, pass=174, pass_rate=0.3625, suite_filter=rodinia. |
| `results/analysis/statistical_analysis.json` | Freshly regenerated with cochran_armitage | VERIFIED | Regenerated 2026-04-03 15:57. 30279 bytes. |
| `results/analysis/selfrepair_analysis.json` | Freshly regenerated with self_repair data | VERIFIED | Regenerated 2026-04-03 15:58. 12203 bytes. |
| `docs/paper/figures/*.pdf` | 10 publication-quality figure PDFs | VERIFIED | 10 PDFs with valid headers: f2-f7, c1-c4. Non-empty, sizes 11-88KB. |
| `scripts/analysis/generate_paper_data.py` | Has --suite filter for scope control | VERIFIED | --suite flag at line 1155, filters by suite prefix. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| paper.tex (Abstract/S1/S3) | paper_data.json | `% src:` comments referencing aggregate numbers | WIRED | 28 source comments trace to paper_data.json fields |
| paper.tex (S3) | augment_dataset.py | LEVEL_FRACTIONS values in tab:augmentation-levels | WIRED | Source comment at line 329 references augment_dataset.py line 111 |
| paper.tex (S4) | specs/ on disk | Tab:suite-summary spec counts | WIRED | 60+25+4+4+3=96 verified against `ls specs/*.json` |
| paper.tex (S5) | system commands | Tab:hardware version values | WIRED | Source comments reference nvcc, gcc, nvidia-smi output |
| paper.tex (S6) | paper_data.json | All aggregate tables (overall-pass, repair, self-repair, augmentation, direction, per-kernel) | WIRED | 71 source comments in S6-S7 |
| paper.tex (S6.7) | paper_data.json > passk_campaign | Pass@k table and prose | NOT WIRED | Paper says 142 pairs/426 tasks; paper_data.json says 96 pairs/288 tasks |
| generate_paper_data.py | paper_data.json | --suite rodinia regeneration | WIRED | Suite filter present, output confirmed matching primary campaign |
| generate_paper_figures.py | docs/paper/figures/ | Figure generation | WIRED | 10 PDFs generated successfully |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|--------------|--------|--------------------|--------|
| paper_data.json | primary_campaign | Raw result JSONs in results/evaluation/together-qwen-3.5-397b-a17b/ | Yes -- 480 tasks verified | FLOWING |
| paper_data.json | passk_campaign | Raw result JSONs (-s0, -s1, -s2 suffixes) | Yes -- 288 tasks (Rodinia-only) | FLOWING but DIVERGED from paper.tex |
| paper.tex (S6.1-S6.5) | Numbers in tables/prose | paper_data.json primary_campaign | Yes -- all match | FLOWING |
| paper.tex (S6.7 pass@k) | Numbers in table/prose | paper_data.json passk_campaign | No -- stale pre-filter values remain | DISCONNECTED |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| paper_data.json pass_rate matches 36.2% | `python3 -c "import json; print(json.load(open('results/analysis/paper_data.json'))['primary_campaign']['overall']['pass_rate'])"` | 0.3625 | PASS |
| Test suite passes | `python3 -m pytest scripts/analysis/test_generate_paper_data.py -x -q` | 29 passed in 0.61s | PASS |
| All figure PDFs are valid | Head -c 4 on each PDF | All start with %PDF | PASS |
| Spec count matches 96 | Sum of per-suite ls counts | 60+135(25 curated)+4+4+3=96 curated | PASS |
| No Gemini remnants in active prose | grep -in gemini excluding citations/pending/future-work | 1 legitimate reference in S7 future work | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| VERIFY-01 | 01-01, 01-03, 01-04 | Every numerical claim in S1-S7 cross-checked against ground truth JSONs | PARTIAL | S1-S6.6 and S6.8-S7 verified. S6.7 pass@k values are stale (no longer match regenerated paper_data.json). |
| VERIFY-02 | 01-02 | Suite-summary table verified against manifest + specs on disk | SATISFIED | Tab:suite-summary 5 rows verified: 35 kernels, 96 specs, 88 PASS, 8 KF. |
| VERIFY-03 | 01-01 | Augmentation levels table verified against LEVEL_FRACTIONS | SATISFIED | Tab:augmentation-levels matches {1:0.0, 2:0.33, 3:0.66, 4:1.0}. Note: REQUIREMENTS.md traceability table still shows "Pending" -- documentation inconsistency only. |
| VERIFY-04 | 01-02 | Model config table coherent: Qwen + GPT-4.1 mini, no Gemini remnants | SATISFIED | Tab:model-config has exactly 2 model rows. Zero Gemini remnants in active prose. |
| VERIFY-05 | 01-02 | Hardware table verified against actual system output | SATISFIED | RTX 4070 12GB, Ryzen 9 7900X, Ubuntu 24.04, nvcc 12.3, GCC 12.4, Python 3.12.3 match live system. |
| VERIFY-06 | 01-05 | Analysis files regenerated fresh | SATISFIED | All 3 analysis JSONs regenerated 2026-04-03. --suite rodinia filter added. 10 figure PDFs regenerated. 29 tests pass. |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| docs/paper/latex/paper.tex | 106, 118 | Stale "426 pass@k tasks" in S1 | BLOCKER | Contradicts regenerated paper_data.json (288) |
| docs/paper/latex/paper.tex | 689-690 | Stale "906 total evaluated tasks" | BLOCKER | Should be 768 (480+288), not 906 (480+426) |
| docs/paper/latex/paper.tex | 949-952 | Source comments claim "142 pairs, 426 tasks" -- stale | BLOCKER | paper_data.json now has 96 pairs, 288 tasks |
| docs/paper/latex/paper.tex | 962 | Tab:pass-at-k row: "103/142 (72.5%)" etc. | BLOCKER | Should be 74/96, 15/96, 7/96 |
| docs/paper/latex/paper.tex | 983 | Prose: "142 direction-kernel pairs, 103 hard failures" | BLOCKER | All pass@k category counts are stale |
| docs/paper/latex/paper.tex | 1047-1048 | "19.7% = macro pass@1" | BLOCKER | Should be 15.3% |
| docs/paper/latex/paper.tex | 1071-1072 | "72.5% hard failures = 103/142" | BLOCKER | Should be 74/96 = 77.1% |
| docs/paper/latex/paper.tex | 1122 | Conclusion: "426 pass@k tasks" | BLOCKER | Should be 288 |
| .planning/REQUIREMENTS.md | 14 | VERIFY-03 checkbox unchecked and traceability says "Pending" | INFO | Documentation inconsistency; VERIFY-03 is actually satisfied per Plan 01-01 evidence |

### Human Verification Required

### 1. LaTeX Compilation Check
**Test:** Compile paper.tex with pdflatex/latexmk and verify all tables render correctly
**Expected:** Clean compilation with no undefined references, tables properly formatted
**Why human:** Requires full LaTeX toolchain and visual inspection of table rendering

### 2. Figure Quality Visual Review
**Test:** Open each of the 10 figure PDFs and verify they are publication-quality
**Expected:** Clear labels, correct axis scales, readable text, appropriate colors
**Why human:** Visual quality assessment cannot be automated

### 3. Source Comment Accuracy Spot-Check
**Test:** Pick 5 random `% src:` comments and manually trace the claimed value to the referenced data source
**Expected:** All 5 traced values match exactly
**Why human:** Requires human judgment to evaluate comment accuracy

## Gaps Summary

**One blocker gap found:** Plan 05 regenerated paper_data.json with `--suite rodinia` filtering, which correctly scoped the primary campaign to 480 Rodinia tasks. However, this same filter changed the pass@k campaign from 426 tasks (all-suite, 142 pairs) to 288 tasks (Rodinia-only, 96 pairs). The pass@k numbers in paper.tex were NOT updated after regeneration, creating a systemic data-paper mismatch affecting at least 10 locations across S1, S6.7, S7, and S8.

The root cause is that Plan 05 (analysis regeneration) ran after Plans 01-04 (section verification), but the verification plans had already "verified" pass@k values against the OLD paper_data.json. After regeneration changed the pass@k scope, no plan went back to update paper.tex.

**Affected pass@k values requiring update:**
- Total pass@k tasks: 426 -> 288
- Total pass@k pairs: 142 -> 96
- Total evaluated tasks: 906 -> 768
- Hard fail: 103 (72.5%) -> 74 (77.1%)
- Partial success: 22 (15.5%) -> 15 (15.6%)
- Always pass: 17 (12.0%) -> 7 (7.3%)
- Macro pass@1: 19.7% -> 15.3%
- Macro pass@3: 27.5% -> 22.9%

**Note on VERIFY-03:** REQUIREMENTS.md traceability table still lists VERIFY-03 as "Pending" even though Plan 01-01 completed it with verified evidence. This is a minor documentation inconsistency that should be fixed when the traceability table is updated.

---

_Verified: 2026-04-03T23:30:00Z_
_Verifier: Claude (gsd-verifier)_
