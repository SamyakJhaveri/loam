---
status: complete
phase: 12-fix-stale-passk-values
source: [12-01-SUMMARY.md, 12-02-SUMMARY.md]
started: 2026-04-05T23:10:00Z
updated: 2026-04-05T23:26:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Abstract Scope Values Correct
expected: Abstract contains 710 tasks, 38.3% [34.8%, 41.9%] overall pass rate, z=0.0/p=1.0 Cochran-Armitage, 7.2% VERIFY_FAIL. No stale 480/700/38.0%/z=-0.77 values.
result: pass

### 2. Per-Kernel Table Expanded to 31 All-Suite Rows
expected: The `tab:per-kernel` table in S6.3 has 31 data rows spanning 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench). Includes Suite column and midrule tier separators between Easy (>=50%), Medium (1-49%), Hard (0%) tiers.
result: issue
reported: "that table should have information on what happened to the 4 kernels (from the 35) that were also included in the eval, but why they are not present in this table."
severity: major

### 3. Overall Pass Table Has ERROR Column
expected: The `tab:overall-pass` table in S6.1 includes an ERROR column. Row values: 272 PASS / 241 BUILD_FAIL / 144 RUN_FAIL / 51 VERIFY_FAIL / 1 EXTRACTION_FAIL / 1 ERROR / 710 total / 38.3%.
result: pass

### 4. No Stale Rodinia-Only Values Remain
expected: Searching paper.tex for any of these 14 stale patterns returns 0 hits: "480" (task count), "906" (total), "36.2%", "65.0%" (CUDA-to-OMP direction), "17.5%", "z=-0.17", "z=-0.77", "p=0.87", "p=0.44", "doubles", "107.1", "30.8%", "48.4%", "15.4%".
result: pass

### 5. Provenance Comments Trace to paper_data.json
expected: Numerical claims throughout paper.tex have LaTeX comments of the form `% src: paper_data.json/...` tracing each value to its source field path. At least 70+ such comments should exist across all sections.
result: pass

### 6. Section 7 Discussion Updated to All-Suite Scope
expected: S7 Discussion (S7.1-S7.5, S7.7) references 710-task scope, 31 kernels, 38.3% pass rate, 64.2% CUDA-to-OMP direction rate, and 55.0% BUILD_FAIL failure share. No stale Rodinia-only references remain.
result: issue
reported: "make sure to mention and justify why 31 kernels and not 35 kernels, what happened to the other 4 kernels."
severity: major

### 7. Section 8 Conclusion Updated
expected: S8 Conclusion references the 710-task all-suite scope with correct key findings (38.3% pass rate, 70% relative improvement from self-repair, z=0.0/p=1.0 augmentation result). No stale values.
result: pass

## Summary

total: 7
passed: 5
issues: 2
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "Per-kernel table explains why 4 of the 35 eval kernels are absent from the 31-row table"
  status: failed
  reason: "User reported: that table should have information on what happened to the 4 kernels (from the 35) that were also included in the eval, but why they are not present in this table."
  severity: major
  test: 2
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""

- truth: "S7 Discussion explains why 31 kernels appear in the per-kernel table instead of 35 eval kernels"
  status: failed
  reason: "User reported: make sure to mention and justify why 31 kernels and not 35 kernels, what happened to the other 4 kernels."
  severity: major
  test: 6
  root_cause: ""
  artifacts: []
  missing: []
  debug_session: ""
