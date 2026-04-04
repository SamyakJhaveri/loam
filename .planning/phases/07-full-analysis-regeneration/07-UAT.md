---
status: complete
phase: 07-full-analysis-regeneration
source: [07-01-SUMMARY.md, 07-02-SUMMARY.md]
started: 2026-04-04T20:52:24Z
updated: 2026-04-04T21:12:00Z
---

## Current Test

[testing complete]

## Tests

### 1. eval_summary.json Task Count and Pass Rate
expected: eval_summary.json shows 1,136 post-exclusion tasks with 31.3% overall pass rate (356 PASS). Previously was 907 tasks.
result: pass

### 2. Dual Paper Data Scopes
expected: Two separate paper_data files exist — paper_data_rodinia.json with 480 primary tasks (Rodinia-only, 36.2% pass rate) and paper_data.json with 710 primary tasks across all 5 suites (38.3% pass rate). The Rodinia file preserves backward compatibility for Sections 6.1-6.5.
result: pass

### 3. Error Taxonomy Completeness
expected: error_taxonomy.json covers all 1,248 result files with 892 failures classified into subcategories (12 BUILD_FAIL, 7 RUN_FAIL, 2 EXTRACTION_FAIL, 3 VERIFY_FAIL subcategories). The .md companion is also updated.
result: pass

### 4. Statistical Analysis with Wilson CIs
expected: statistical_analysis.json includes Wilson confidence intervals for 1,136 post-exclusion results, including non-Rodinia kernels (xsbench, rsbench, mixbench, convolution1d, floydwarshall, scan). Overall CI should be approximately [28.7%, 34.1%].
result: pass

### 5. Token Analysis Updated
expected: token_analysis.json shows 1,136 results (up from 906), with total tokens ~55.2M and total cost ~$39.03 for Qwen 3.5 397B via Together AI.
result: issue
reported: "User provided actual Together AI billing CSV showing $0.60/$3.60 per M token rates (not $0.50/$1.50 in script). Billing totals: 96.2M input + 24.3M output = 120.6M tokens, $145.37 total cost. Result JSONs capture only ~54% of billed tokens."
severity: major

### 6. Translation Complexity Coverage
expected: translation_complexity.csv contains 290 translation pairs across 5 suites (hecbench=150, rodinia=110, xsbench=12, rsbench=12, mixbench=6). Previously was Rodinia-only.
result: pass

### 7. Cross-Suite Kernel Presence in Analysis Outputs
expected: Non-Rodinia kernels (at minimum xsbench, rsbench, mixbench) appear in error_taxonomy.json, statistical_analysis.json, and token_analysis.json — confirming all analysis scripts processed the full 5-suite dataset, not just Rodinia.
result: pass

## Summary

total: 7
passed: 6
issues: 1
pending: 0
skipped: 0
blocked: 0

## Gaps

- truth: "token_analysis.json should reflect actual API costs and token usage"
  status: fixed
  reason: "User reported: actual Together AI billing shows $0.60/$3.60 per M pricing (not $0.50/$1.50), and 120.6M total tokens ($145.37) vs 55.2M reported. Three-layer discrepancy: wrong pricing, KNOWN_FAIL exclusion, and result JSON token under-reporting."
  severity: major
  test: 5
  root_cause: "MODEL_PRICING in token_analysis.py had stale $0.50/$1.50 rates; result JSONs structurally undercount vs provider billing"
  artifacts:
    - path: "scripts/analysis/token_analysis.py"
      issue: "Wrong pricing, no billing ground truth"
  missing: []
  fix_applied: "Updated pricing to $0.60/$3.60, added actual_billing section with CSV ground truth, re-ran analysis. New result-JSON cost: $67.38, actual billing: $145.37"
