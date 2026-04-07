---
phase: 15-paper-review-tools
reviewed: 2026-04-06T18:30:00Z
depth: standard
files_reviewed: 2
files_reviewed_list:
  - docs/paper/latex/paper.tex
  - docs/paper/latex/appendices.tex
findings:
  critical: 3
  warning: 4
  info: 3
  total: 10
status: issues_found
---

# Phase 15: Code Review Report

**Reviewed:** 2026-04-06T18:30:00Z
**Depth:** standard
**Files Reviewed:** 2
**Status:** issues_found

## Summary

Reviewed `paper.tex` (1122 lines) and `appendices.tex` (1401 lines) -- the SC26 ParBench paper LaTeX source. The review focused on LaTeX compilation correctness, internal data consistency, and cross-reference integrity.

Three critical issues were found: two duplicate `\newcommand` definitions that will cause LaTeX compilation errors, and a Fisher exact test paragraph with internally inconsistent sample sizes that contradict numbers reported elsewhere in the paper. Four warnings identify data inconsistencies between different sections of the paper and appendices that would be caught by reviewers.

Cross-references between `paper.tex` and `appendices.tex` are complete -- all `\ref{}` targets have corresponding `\label{}` definitions and no dangling references were found.

## Critical Issues

### CR-01: Duplicate `\newcommand{\pending}` -- LaTeX compilation error

**File:** `docs/paper/latex/paper.tex:36-37`
**Issue:** `\pending` is defined twice on consecutive lines. LaTeX will error on `\newcommand` for an already-defined command. The first definition (`[PENDING: #1]`) is immediately overwritten by the second (`[PENDING-GPT: #1]`), but standard LaTeX will refuse to compile.
**Fix:**
```latex
% Remove line 36 entirely; keep only the intended definition:
\newcommand{\pending}[1]{\textcolor{red}{\textbf{[PENDING-GPT: #1]}}}
```

### CR-02: Duplicate `\newcommand{\parbench}` -- LaTeX compilation error

**File:** `docs/paper/latex/paper.tex:28,53`
**Issue:** `\parbench` is defined on line 28 as `\textsc{ParBench}` and again on line 53 as plain `ParBench`. LaTeX will error on the second `\newcommand`. Additionally, the macro appears to never actually be used in the paper body (all instances use literal `ParBench` or `\textbf{ParBench}`). Line 27 also has a commented-out third definition.
**Fix:**
```latex
% Remove line 53 entirely. Keep line 28 (\textsc version) as the canonical definition.
% Delete: \newcommand{\parbench}{ParBench}
```

### CR-03: Fisher exact test sample sizes are internally inconsistent

**File:** `docs/paper/latex/paper.tex:921`
**Issue:** The Fisher exact test paragraph states "$n = 192$: 96 L0 tasks, 96 pooled augmented tasks" for the "CUDA-to-OpenMP direction." However, Table `tab:direction-rates` (line 939) shows CUDA-to-OMP has 24 kernels at L0 and 120 total tasks (24 * 5 levels). Therefore L0 = 24 tasks and L1-L4 = 96 tasks, giving n = 120, not 192. The paragraph also states "L0 achieves a 41.7% pass rate" but Table `tab:augmentation-rates` (appendices line 1141) shows CUDA-to-OMP L0 = 66.7% (16/24). The 41.7% figure does not match any reported data. Similarly, the "63.5% for pooled L1-L4" does not match the augmented levels (58.3%, 70.8%, 58.3%, 66.7% from the same table). These numbers appear to come from a different analysis scope than described.
**Fix:** Re-run the Fisher exact test using the correct CUDA-to-OMP data: L0 = 16/24 (66.7%), pooled L1-L4 = 61/96 (63.5%), n = 120. Alternatively, clarify that the test uses a different scope (e.g., all directions) and update the prose accordingly. All derived statistics (odds ratio, p-value, Bonferroni correction) must be recomputed from the corrected data.

## Warnings

### WR-01: HeCBench kernel count inconsistency (513 vs 516)

**File:** `docs/paper/latex/appendices.tex:395,413,424` vs `docs/paper/latex/appendices.tex:741,750,786` and `docs/paper/latex/paper.tex:453`
**Issue:** The HeCBench total kernel count is reported as 516 in Appendix B (bubble chart caption line 395, top candidates caption line 413, funnel text line 424) but as 513 in Appendix C4 (funnel figure caption line 741, text line 750, percentage line 786) and the main paper Section 4 (line 453). This 3-kernel discrepancy would be noticed by reviewers cross-checking the paper.
**Fix:** Determine the correct count and make it consistent across all six occurrences. If 513 is correct, update lines 395, 413, 424 in appendices.tex. If 516 is correct, update lines 741, 750, 786 in appendices.tex and line 453 in paper.tex.

### WR-02: HeCBench funnel Stage 1 numbers conflict between Appendix B3 and C4

**File:** `docs/paper/latex/appendices.tex:428-432` vs `docs/paper/latex/appendices.tex:754-758`
**Issue:** Appendix B3 (line 428) states the API filter yields 272 kernels from 516 total, while Appendix C4 (line 755) states the same filter yields 327 kernels from 513 total. These are different descriptions of the same funnel but with contradictory numbers at every stage. Appendix B3 also conflates the API filter with build system and self-checking filters into a single "Stage 1" (272 = all three conditions), while C4 and the main paper separate them into three stages (327 -> 325 -> 242). This creates confusion about the actual funnel.
**Fix:** Reconcile the two appendix descriptions. They should report identical numbers for the same filtering process. Consider making Appendix B3 reference the detailed funnel in C4 rather than presenting its own version with different numbers.

### WR-03: Per-kernel table Fail column does not include breakdown

**File:** `docs/paper/latex/paper.tex:806-827`
**Issue:** Table `tab:per-kernel` has a "Fail" column that simply shows `Total - PASS`, but the surrounding text discusses failure mode breakdowns (BUILD_FAIL, VERIFY_FAIL) for specific kernels without those numbers appearing in the table. For example, the text states "Backprop's failures concentrate in BUILD_FAIL (16/30)" (line 847) and "cfd...VERIFY_FAIL counts (10 each)" (line 844), but these breakdowns are not in the table. Readers may find it difficult to verify claims against the table. This is a minor presentation issue -- the full table is in the appendix.
**Fix:** Consider adding a "Dominant Failure" column to `tab:per-kernel`, or ensure the full appendix table (`tab:per-kernel-full`) includes failure mode columns.

### WR-04: Augmentation robustness Fisher test scope description vs statistics mismatch

**File:** `docs/paper/latex/paper.tex:921`
**Issue:** Beyond the sample size issue (CR-03), the Fisher test describes "Bonferroni-corrected p = 0.0075, family size = 2" but does not explain what the two tests in the family are. The only other augmentation test is the Cochran-Armitage trend test, but a Fisher test and a Cochran-Armitage test address different hypotheses on the same data -- it is unusual to Bonferroni-correct across tests that are not multiple comparisons of the same type. The rationale for family size = 2 should be stated.
**Fix:** Add a parenthetical explaining the family: e.g., "(family: Fisher L0-vs-augmented and Cochran-Armitage trend, both testing augmentation effects on the same dataset)." Alternatively, if the family of 2 refers to two Fisher tests (one per model), state that explicitly.

## Info

### IN-01: Commented-out `\parbench` definition adds confusion

**File:** `docs/paper/latex/paper.tex:27`
**Issue:** Line 27 has `% \newcommand{\parbench}{ParBench}` commented out, immediately before the active definition on line 28. Combined with the duplicate on line 53, this creates three definitions (one commented, two active) for the same macro, making authorial intent unclear.
**Fix:** Remove line 27 (the commented-out version) and line 53 (the duplicate). Keep only line 28.

### IN-02: Related work table footnote says "1,136 tasks" but body text says "710 primary campaign tasks"

**File:** `docs/paper/latex/paper.tex:221`
**Issue:** The footnote under Table `tab:related-work` states "Initial campaign: 1,136 tasks" while the body consistently describes the primary campaign as 710 tasks plus 426 pass@k tasks. The 1,136 total is correct (710 + 426 = 1,136), but calling it "Initial campaign" is ambiguous -- it conflates the primary campaign with the separate pass@k sweep. A reviewer might expect the "Initial campaign" to refer to 710 tasks only.
**Fix:** Change to "Total evaluation: 1,136 tasks (710 primary + 426 pass@$k$) with Qwen~3.5 397B-A17B; GPT-4.1~mini campaign in progress."

### IN-03: `\parbench` macro defined but never used in body text

**File:** `docs/paper/latex/paper.tex:28,53`
**Issue:** The `\parbench` macro is defined (twice) but the paper body uses literal `ParBench` or `\textbf{ParBench}` or `\textsc{ParBench}` throughout. The macro provides no value if unused and contributes to the duplicate-definition error.
**Fix:** Either use `\parbench` consistently throughout the paper body, or remove the macro definition entirely and use literal text.

---

_Reviewed: 2026-04-06T18:30:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
